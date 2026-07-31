"""LangGraph runtime for the single-agent orchestration workflow."""

from __future__ import annotations

from dataclasses import replace
from operator import add
from typing import Annotated, TypedDict
from uuid import uuid4

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from . import self_improve, world_model
from .agent_definition import AgentDefinition, load_agent_definition
from .capabilities import act, planning, reviewing
from .checkpoint_store import DEFAULT_CHECKPOINT_PATH, open_sqlite_checkpointer
from .memory import Memory
from .runtime import CheckpointInfo, RunEvent, RunResult, validate_recovery_state_patch
from .trace_store import TraceStore

MAX_STEPS = 10

class AgentState(TypedDict):
    task: str
    memory_context: str
    steps: list[str]
    results: Annotated[list[str], add]
    has_lesson: bool
    should_stop: bool
    outcome: str
    execution_session: dict
    pending_interruption: dict
    action_events: list[dict]
    failure: str


class LangGraphRuntime:
    """Maps the existing agent policies onto a LangGraph StateGraph."""

    def __init__(
        self,
        memory: Memory,
        trace_store: TraceStore | None = None,
        definition: AgentDefinition | None = None,
        checkpointer: BaseCheckpointSaver | None = None,
        checkpoint_path: str | None = None,
    ):
        self.memory = memory
        self.trace_store = trace_store or TraceStore()
        self.definition = definition or load_agent_definition()
        self._checkpoint_connection = None
        if checkpointer is None:
            self.checkpointer, self._checkpoint_connection = open_sqlite_checkpointer(
                checkpoint_path or DEFAULT_CHECKPOINT_PATH,
            )
        else:
            self.checkpointer = checkpointer
        self.graph = self._build_graph()

    def close(self) -> None:
        """Close the SQLite connection owned by this runtime, if any."""
        if self._checkpoint_connection is not None:
            self._checkpoint_connection.close()
            self._checkpoint_connection = None

    def run(self, task: str) -> RunResult:
        thread_id = uuid4().hex
        run_id = uuid4().hex
        events = [RunEvent(1, run_id, "run", "started", {
            "task": task,
            "agent_id": self.definition.id,
            "thread_id": thread_id,
        })]
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": MAX_STEPS * 2 + 10,
        }
        initial_state: AgentState = {
            "task": task,
            "memory_context": "",
            "steps": [],
            "results": [],
            "has_lesson": False,
            "should_stop": False,
            "outcome": "",
            "execution_session": {},
            "pending_interruption": {},
            "action_events": [],
            "failure": "",
        }

        return self._execute_graph(task, run_id, thread_id, initial_state, config, events)

    def resume(self, thread_id: str, decision: object, parent_run_id: str | None = None) -> RunResult:
        """Resume the latest checkpoint with a decision, such as tool approval."""
        run_id = uuid4().hex
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": MAX_STEPS * 2 + 10}
        snapshot = self.graph.get_state(config)
        checkpoint_id = snapshot.config.get("configurable", {}).get("checkpoint_id")
        task = snapshot.values.get("task")
        if not checkpoint_id or not task:
            raise ValueError(f"unknown or expired thread: {thread_id}")
        events = [RunEvent(1, run_id, "run", "resumed", {
            "thread_id": thread_id,
            "parent_run_id": parent_run_id,
            "recovered_from_checkpoint_id": checkpoint_id,
            "recovery_mode": "replay",
        })]
        return self._execute_graph(
            task,
            run_id,
            thread_id,
            Command(resume=decision),
            config,
            events,
            parent_run_id,
            checkpoint_id,
            "replay",
        )

    def checkpoint_history(self, thread_id: str) -> tuple[CheckpointInfo, ...]:
        """List selectable checkpoints, newest first, for one state thread."""
        config = {"configurable": {"thread_id": thread_id}}
        history = []
        for snapshot in self.graph.get_state_history(config):
            checkpoint_id = snapshot.config.get("configurable", {}).get("checkpoint_id")
            if checkpoint_id:
                history.append(CheckpointInfo(checkpoint_id, tuple(snapshot.next)))
        return tuple(history)

    def recover(
        self,
        thread_id: str,
        checkpoint_id: str,
        state_patch: dict | None = None,
        parent_run_id: str | None = None,
    ) -> RunResult:
        """Replay a checkpoint, or fork from it when an explicit state patch is supplied."""
        validate_recovery_state_patch(state_patch)
        config = self._checkpoint_config(thread_id, checkpoint_id)
        recovery_mode = "fork" if state_patch else "replay"
        if state_patch:
            # Treat an operator's changed steps as a revised plan, so prediction runs again.
            config = self.graph.update_state(config, values=state_patch, as_node="plan")
        config = {**config, "recursion_limit": MAX_STEPS * 2 + 10}
        state = self.graph.get_state(config).values
        task = state.get("task")
        if not task:
            raise ValueError(f"checkpoint does not contain a runnable task: {checkpoint_id}")
        run_id = uuid4().hex
        events = [RunEvent(1, run_id, "run", "recovered", {
            "thread_id": thread_id,
            "parent_run_id": parent_run_id,
            "recovered_from_checkpoint_id": checkpoint_id,
            "recovery_mode": recovery_mode,
            "patched_fields": sorted(state_patch) if state_patch else [],
        })]
        return self._execute_graph(
            task,
            run_id,
            thread_id,
            None,
            config,
            events,
            parent_run_id,
            checkpoint_id,
            recovery_mode,
        )

    def _checkpoint_config(self, thread_id: str, checkpoint_id: str) -> dict:
        for snapshot in self.graph.get_state_history({"configurable": {"thread_id": thread_id}}):
            config = snapshot.config
            if config.get("configurable", {}).get("checkpoint_id") == checkpoint_id:
                return config
        raise ValueError(f"unknown checkpoint {checkpoint_id} for thread {thread_id}")

    def _execute_graph(
        self,
        task: str,
        run_id: str,
        thread_id: str,
        graph_input: object,
        config: dict,
        events: list[RunEvent],
        parent_run_id: str | None = None,
        recovered_from_checkpoint_id: str | None = None,
        recovery_mode: str | None = None,
    ) -> RunResult:
        interrupts: list[dict] = []
        try:
            for chunk in self.graph.stream(
                graph_input,
                config,
                stream_mode="updates",
                version="v2",
            ):
                if chunk["type"] != "updates":
                    continue
                for node_name, update in chunk["data"].items():
                    if node_name == "__interrupt__":
                        payload = self._interrupt_payload(update)
                        interrupts.extend(payload)
                        kinds = {item["value"].get("kind") for item in payload}
                        phase = "unknown" if "unknown" in kinds else "input" if "input" in kinds else "approval"
                        events.append(RunEvent(len(events) + 1, run_id, phase, "paused", {"interrupts": payload}))
                        continue
                    payload = dict(update) if update else {}
                    events.append(RunEvent(
                        len(events) + 1,
                        run_id,
                        node_name,
                        "completed",
                        payload,
                    ))

            if interrupts:
                return self._persist_trace(RunResult(
                    run_id, task, None, tuple(events), interrupts=tuple(interrupts),
                    thread_id=thread_id, parent_run_id=parent_run_id,
                    recovered_from_checkpoint_id=recovered_from_checkpoint_id,
                    recovery_mode=recovery_mode,
                ))
            state = self.graph.get_state({"configurable": {"thread_id": thread_id}}).values
            failure = state.get("failure")
            if failure:
                events.append(RunEvent(len(events) + 1, run_id, "run", "failed", {"error": failure}))
                return self._persist_trace(RunResult(
                    run_id, task, None, tuple(events), failure,
                    thread_id=thread_id, parent_run_id=parent_run_id,
                    recovered_from_checkpoint_id=recovered_from_checkpoint_id,
                    recovery_mode=recovery_mode,
                ))
            outcome = state.get("outcome") or "(未执行)"
        except Exception as error:
            message = str(error) or error.__class__.__name__
            events.append(RunEvent(len(events) + 1, run_id, "run", "failed", {"error": message}))
            return self._persist_trace(RunResult(
                run_id, task, None, tuple(events), message,
                thread_id=thread_id, parent_run_id=parent_run_id,
                recovered_from_checkpoint_id=recovered_from_checkpoint_id,
                recovery_mode=recovery_mode,
            ))

        events.append(RunEvent(len(events) + 1, run_id, "run", "completed", {"outcome": outcome}))
        return self._persist_trace(RunResult(
            run_id, task, outcome, tuple(events), thread_id=thread_id,
            parent_run_id=parent_run_id,
            recovered_from_checkpoint_id=recovered_from_checkpoint_id,
            recovery_mode=recovery_mode,
        ))

    @staticmethod
    def _interrupt_payload(update: object) -> list[dict]:
        return [{"id": item.id, "value": item.value} for item in update]

    def _persist_trace(self, result: RunResult) -> RunResult:
        try:
            self.trace_store.save(result)
        except Exception as error:
            message = str(error) or error.__class__.__name__
            return replace(result, warnings=result.warnings + (f"trace_persist_failed: {message}",))
        return result

    def checkpoint_count(self, thread_id: str) -> int:
        """Return the number of framework checkpoints saved for one thread."""
        config = {"configurable": {"thread_id": thread_id}}
        return sum(1 for _ in self.checkpointer.list(config))

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("load_memory", self._load_memory)
        builder.add_node("plan", self._plan)
        builder.add_node("predict", self._predict)
        builder.add_node("prepare_action", self._prepare_action)
        builder.add_node("interrupt_for_human", self._interrupt_for_human)
        builder.add_node("reflect", self._reflect)
        builder.add_node("save_memory", self._save_memory)

        builder.add_edge(START, "load_memory")
        builder.add_edge("load_memory", "plan")
        builder.add_edge("plan", "predict")
        builder.add_edge("predict", "prepare_action")
        builder.add_conditional_edges("prepare_action", self._after_prepare, {
            "interrupt_for_human": "interrupt_for_human",
            "reflect": "reflect",
            "save_memory": "save_memory",
            "end": END,
        })
        builder.add_conditional_edges("interrupt_for_human", self._after_interruption, {
            "interrupt_for_human": "interrupt_for_human",
            "prepare_action": "prepare_action",
            "end": END,
        })
        builder.add_conditional_edges("reflect", self._after_reflect, {
            "prepare_action": "prepare_action",
            "save_memory": "save_memory",
        })
        builder.add_edge("save_memory", END)
        return builder.compile(checkpointer=self.checkpointer)

    def _load_memory(self, state: AgentState) -> dict:
        memory_context = self.memory.to_context()
        if memory_context != "(无记忆)":
            print("\n📚 [记忆] 已加载记忆上下文")
        return {"memory_context": memory_context}

    def _plan(self, state: AgentState) -> dict:
        print("\n🧭 [规划] 正在生成计划...")
        steps = planning.make_plan(state["task"], state["memory_context"], self.definition)
        for index, step in enumerate(steps, 1):
            print(f"   📋 步骤 {index}: {step}")
        return {"steps": steps}

    def _predict(self, state: AgentState) -> dict:
        print("\n🔮 [预测] 正在评估计划风险...")
        predictions = world_model.predict(state["steps"], state["memory_context"])
        risky = world_model.has_high_risk(predictions)
        if not risky:
            print("   ✅ 未发现高风险，计划无需调整")
            return {}

        for prediction in risky:
            print(f"   ⚠️  {prediction['step']}: {prediction['risk']}")
        print("\n🧭 [规划] 正在根据风险调整计划...")
        steps = planning.adjust_plan(
            state["steps"],
            risky,
            execution_tools=self.definition.tools,
        )
        for index, step in enumerate(steps, 1):
            print(f"   📋 调整后步骤 {index}: {step}")
        return {"steps": steps}

    def _prepare_action(self, state: AgentState) -> dict:
        index = len(state["results"])
        step = state["steps"][index]
        session = state["execution_session"]
        if not session:
            print(f"\n⚡ [执行] 步骤 {index + 1}/{len(state['steps'])}: {step}")
            context = "\n".join(f"[步骤{i + 1}结果] {result}" for i, result in enumerate(state["results"]))
            session = act.start_step(
                step,
                context or "(第一步，暂无上下文)",
                self.definition,
            )
        progress = act.advance(session, self.definition)
        if progress["status"] == "interrupted":
            return {
                "execution_session": progress["session"],
                "pending_interruption": progress["interruption"],
                "action_events": progress.get("actions", []),
            }
        if progress["status"] == "contract_error":
            return {"failure": progress["error"], "action_events": progress["actions"]}

        result = progress["result"]
        self.memory.working_add({"step": step, "result": result, "summary": result[:100]})
        return {
            "results": [result],
            "execution_session": {},
            "pending_interruption": {},
            "action_events": progress.get("actions", []),
        }

    def _interrupt_for_human(self, state: AgentState) -> dict:
        """Pause once, then pass the resolution to the action layer."""
        interruption = state["pending_interruption"]
        resolution = act.resolve_interruption(
            state["execution_session"],
            interruption,
            interrupt(interruption),
            self.definition,
        )
        if resolution["status"] == "interrupted":
            return {
                "execution_session": resolution["session"],
                "pending_interruption": resolution["interruption"],
                "action_events": resolution["actions"],
            }
        if resolution["status"] in {"failed", "contract_error"}:
            return {
                "pending_interruption": {},
                "failure": resolution["error"],
                "action_events": resolution["actions"],
            }
        return {
            "execution_session": resolution["session"],
            "pending_interruption": {},
            "action_events": resolution["actions"],
        }

    def _after_prepare(self, state: AgentState) -> str:
        if state["failure"]:
            return "end"
        if state["pending_interruption"]:
            return "interrupt_for_human"
        return self._after_execute(state)

    def _after_interruption(self, state: AgentState) -> str:
        if state["failure"]:
            return "end"
        if state["pending_interruption"]:
            return "interrupt_for_human"
        return "prepare_action"

    def _after_execute(self, state: AgentState) -> str:
        if len(state["results"]) >= len(state["steps"]) or len(state["results"]) >= MAX_STEPS:
            return "save_memory"
        return "reflect"

    def _reflect(self, state: AgentState) -> dict:
        print("\n🔎 [反思] 正在评估进展...")
        done_index = len(state["results"])
        decision = reviewing.reflect(
            state["task"],
            state["steps"],
            done_index,
            state["results"],
            self.definition.acceptance,
        )
        has_lesson = state["has_lesson"] or decision.get("has_lesson", False)

        if decision["action"] == "done":
            print(f"   ✅ 提前完成: {decision.get('summary', '')}")
            return {"has_lesson": has_lesson, "should_stop": True}
        if decision["action"] == "replan":
            steps = state["steps"][:done_index] + decision["new_steps"]
            print(f"   🔄 调整计划: {decision['new_steps']}")
            return {"steps": steps, "has_lesson": True, "should_stop": False}

        print("   ➡️  继续执行")
        return {"has_lesson": has_lesson, "should_stop": False}

    def _after_reflect(self, state: AgentState) -> str:
        if state["should_stop"] or len(state["results"]) >= len(state["steps"]) or len(state["results"]) >= MAX_STEPS:
            return "save_memory"
        return "prepare_action"

    def _save_memory(self, state: AgentState) -> dict:
        results = state["results"]
        outcome = results[-1] if results else "(未执行)"
        self.memory.episodic_add(state["task"], state["steps"][:len(results)], results, outcome)
        self.memory.working_clear()

        if not state["has_lesson"]:
            print("\n   [记忆] 执行顺利，无需提炼")
            return {"outcome": outcome}

        print("\n🧪 [记忆] 正在提炼经验...")
        try:
            insights = self_improve.distill(state["task"], state["steps"][:len(results)], results)
            for fact in insights.get("facts", []):
                self.memory.semantic_add(fact, source=state["task"])
                print(f"   💡 知识: {fact}")
            for pattern in insights.get("patterns", []):
                self.memory.procedural_add(pattern["trigger"], pattern["steps"])
                print(f"   📐 模式: 当{pattern['trigger']}时 → {' → '.join(pattern['steps'])}")
            for correction in insights.get("corrections", []):
                self.memory.corrections_add(
                    correction.get("mistake", ""),
                    correction.get("lesson", str(correction)),
                    source=state["task"],
                )
                print(f"   🔧 教训: {correction.get('mistake', '')} → {correction.get('lesson', '')}")
        except Exception as error:
            print(f"   ⚠️  提炼失败: {error}")

        removed = self_improve.consolidate(self.memory)
        if removed > 0:
            print(f"   🧹 语义记忆合并去重，精简了 {removed} 条")
        return {"outcome": outcome}
