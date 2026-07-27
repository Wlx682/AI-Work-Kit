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
from .runtime import RunEvent, RunResult
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
    pending_approval: dict


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
        run_id = uuid4().hex
        events = [RunEvent(1, run_id, "run", "started", {
            "task": task,
            "agent_id": self.definition.id,
        })]
        config = {
            "configurable": {"thread_id": run_id},
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
            "pending_approval": {},
        }

        return self._execute_graph(task, run_id, initial_state, config, events)

    def resume(self, run_id: str, decision: object) -> RunResult:
        """Resume a paused run with an explicit approval decision."""
        config = {"configurable": {"thread_id": run_id}, "recursion_limit": MAX_STEPS * 2 + 10}
        state = self.graph.get_state(config).values
        task = state.get("task")
        if not task:
            raise ValueError(f"unknown or expired run: {run_id}")
        events = self._previous_events(run_id)
        events.append(RunEvent(len(events) + 1, run_id, "run", "resumed", {"decision": decision}))
        return self._execute_graph(task, run_id, Command(resume=decision), config, events)

    def _execute_graph(self, task: str, run_id: str, graph_input: object, config: dict, events: list[RunEvent]) -> RunResult:
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
                        events.append(RunEvent(len(events) + 1, run_id, "approval", "paused", {"interrupts": payload}))
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
                return self._persist_trace(RunResult(run_id, task, None, tuple(events), interrupts=tuple(interrupts)))
            state = self.graph.get_state(config).values
            outcome = state.get("outcome") or "(未执行)"
        except Exception as error:
            message = str(error) or error.__class__.__name__
            events.append(RunEvent(len(events) + 1, run_id, "run", "failed", {"error": message}))
            return self._persist_trace(RunResult(run_id, task, None, tuple(events), message))

        events.append(RunEvent(len(events) + 1, run_id, "run", "completed", {"outcome": outcome}))
        return self._persist_trace(RunResult(run_id, task, outcome, tuple(events)))

    def _previous_events(self, run_id: str) -> list[RunEvent]:
        try:
            return list(self.trace_store.load(run_id).events)
        except FileNotFoundError:
            return []

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

    def checkpoint_count(self, run_id: str) -> int:
        """Return the number of framework checkpoints saved for one run."""
        config = {"configurable": {"thread_id": run_id}}
        return sum(1 for _ in self.checkpointer.list(config))

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("load_memory", self._load_memory)
        builder.add_node("plan", self._plan)
        builder.add_node("predict", self._predict)
        builder.add_node("prepare_action", self._prepare_action)
        builder.add_node("approve_tool", self._approve_tool)
        builder.add_node("reflect", self._reflect)
        builder.add_node("save_memory", self._save_memory)

        builder.add_edge(START, "load_memory")
        builder.add_edge("load_memory", "plan")
        builder.add_edge("plan", "predict")
        builder.add_edge("predict", "prepare_action")
        builder.add_conditional_edges("prepare_action", self._after_prepare, {
            "approve_tool": "approve_tool",
            "reflect": "reflect",
            "save_memory": "save_memory",
        })
        builder.add_edge("approve_tool", "prepare_action")
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
        steps = planning.adjust_plan(state["steps"], risky)
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
            session = act.start_step(step, context or "(第一步，暂无上下文)")
        progress = act.advance(session, self.definition)
        if progress["status"] == "approval_required":
            return {"execution_session": progress["session"], "pending_approval": progress["proposal"]}

        result = progress["result"]
        self.memory.working_add({"step": step, "result": result, "summary": result[:100]})
        return {"results": [result], "execution_session": {}, "pending_approval": {}}

    def _approve_tool(self, state: AgentState) -> dict:
        decision = interrupt(state["pending_approval"])
        session = act.resolve_approval(state["execution_session"], decision, self.definition)
        return {"execution_session": session, "pending_approval": {}}

    def _after_prepare(self, state: AgentState) -> str:
        if state["pending_approval"]:
            return "approve_tool"
        return self._after_execute(state)

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
