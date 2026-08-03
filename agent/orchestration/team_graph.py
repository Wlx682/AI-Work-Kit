"""LangGraph runtime for the four-role Team workflow."""

from __future__ import annotations

from dataclasses import replace
from operator import add
from typing import Annotated, TypedDict
from uuid import uuid4

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from ..cognition import self_improve
from ..cognition.memory import Memory
from ..core.models import CheckpointInfo, RunEvent, RunResult, validate_recovery_state_patch
from ..infrastructure.checkpoints import DEFAULT_CHECKPOINT_PATH, open_sqlite_checkpointer
from ..infrastructure.traces import TraceStore
from ..roles import Executor, Planner, Predictor, Reviewer

MAX_RETRIES = 3


class TeamState(TypedDict):
    """Shared state passed between Team Graph nodes."""

    task: str
    max_retries: int
    memory_context: str
    steps: list[str]
    risky: list[dict]
    results: list[str]
    verdict: dict
    attempt: int
    has_review_rejection: bool
    outcome: str
    handoffs: Annotated[list[dict[str, object]], add]
    execution_session: dict
    pending_interruption: dict
    action_events: list[dict]
    failure: str


class TeamGraphRuntime:
    """Runs Planner -> Predictor -> Executor -> Reviewer as a LangGraph."""

    def __init__(
        self,
        memory: Memory,
        trace_store: TraceStore | None = None,
        checkpointer: BaseCheckpointSaver | None = None,
        checkpoint_path: str | None = None,
    ):
        self.memory = memory
        self.trace_store = trace_store or TraceStore()
        self.planner = Planner()
        self.predictor = Predictor()
        self.executor = Executor()
        self.reviewer = Reviewer()
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

    def run(self, task: str, max_retries: int = MAX_RETRIES) -> RunResult:
        """Run the team graph and persist a normalized execution trace."""
        thread_id = uuid4().hex
        run_id = uuid4().hex
        events = [RunEvent(1, run_id, "run", "started", {
            "task": task,
            "thread_id": thread_id,
            "team": [
                self.planner.definition.id,
                self.predictor.definition.id,
                self.executor.definition.id,
                self.reviewer.definition.id,
            ],
        })]
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": max_retries * 3 + 20,
        }
        initial_state: TeamState = {
            "task": task,
            "max_retries": max_retries,
            "memory_context": "",
            "steps": [],
            "risky": [],
            "results": [],
            "verdict": {},
            "attempt": 0,
            "has_review_rejection": False,
            "outcome": "",
            "handoffs": [],
            "execution_session": {},
            "pending_interruption": {},
            "action_events": [],
            "failure": "",
        }

        return self._execute_graph(task, run_id, thread_id, initial_state, config, events)

    def resume(self, thread_id: str, decision: object, parent_run_id: str | None = None) -> RunResult:
        """Resume the latest Team checkpoint with a decision."""
        run_id = uuid4().hex
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": MAX_RETRIES * 3 + 20}
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
        """List selectable checkpoints, newest first, for one Team state thread."""
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
        """Replay a Team checkpoint, or fork from it with an explicit state patch."""
        validate_recovery_state_patch(state_patch)
        config = self._checkpoint_config(thread_id, checkpoint_id)
        recovery_mode = "fork" if state_patch else "replay"
        if state_patch:
            # Treat an operator's changed steps as a revised plan, so prediction runs again.
            config = self.graph.update_state(config, values=state_patch, as_node="plan")
        config = {**config, "recursion_limit": MAX_RETRIES * 3 + 20}
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
                    events.append(RunEvent(
                        len(events) + 1,
                        run_id,
                        node_name,
                        "completed",
                        dict(update) if update else {},
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

    def checkpoint_count(self, thread_id: str) -> int:
        """Return the number of framework checkpoints saved for one team thread."""
        return sum(1 for _ in self.checkpointer.list({"configurable": {"thread_id": thread_id}}))

    def _persist_trace(self, result: RunResult) -> RunResult:
        try:
            self.trace_store.save(result)
        except Exception as error:
            message = str(error) or error.__class__.__name__
            return replace(result, warnings=result.warnings + (f"trace_persist_failed: {message}",))
        return result

    def _build_graph(self):
        builder = StateGraph(TeamState)
        builder.add_node("load_memory", self._load_memory)
        builder.add_node("plan", self._plan)
        builder.add_node("predict", self._predict)
        builder.add_node("adjust_plan", self._adjust_plan)
        builder.add_node("prepare_action", self._prepare_action)
        builder.add_node("interrupt_for_human", self._interrupt_for_human)
        builder.add_node("review", self._review)
        builder.add_node("revise_plan", self._revise_plan)
        builder.add_node("save_memory", self._save_memory)

        builder.add_edge(START, "load_memory")
        builder.add_edge("load_memory", "plan")
        builder.add_edge("plan", "predict")
        builder.add_conditional_edges("predict", self._after_predict, {
            "adjust_plan": "adjust_plan",
            "prepare_action": "prepare_action",
        })
        builder.add_edge("adjust_plan", "prepare_action")
        builder.add_conditional_edges("prepare_action", self._after_prepare, {
            "prepare_action": "prepare_action",
            "interrupt_for_human": "interrupt_for_human",
            "review": "review",
            "end": END,
        })
        builder.add_conditional_edges("interrupt_for_human", self._after_interruption, {
            "interrupt_for_human": "interrupt_for_human",
            "prepare_action": "prepare_action",
            "end": END,
        })
        builder.add_conditional_edges("review", self._after_review, {
            "save_memory": "save_memory",
            "revise_plan": "revise_plan",
        })
        builder.add_edge("revise_plan", "prepare_action")
        builder.add_edge("save_memory", END)
        return builder.compile(checkpointer=self.checkpointer)

    def _load_memory(self, state: TeamState) -> dict:
        memory_context = self.memory.to_context()
        if memory_context != "(无记忆)":
            print("\n📚 [记忆] 已加载记忆上下文")
        return {"memory_context": memory_context}

    def _plan(self, state: TeamState) -> dict:
        print("\n🧭 [Planner] 正在生成计划...")
        steps = self.planner.make_plan(
            state["task"],
            state["memory_context"],
            self.executor.definition.tools,
        )
        for index, step in enumerate(steps, 1):
            print(f"   📋 步骤 {index}: {step}")
        return {
            "steps": steps,
            "handoffs": [self._handoff("Planner", "Predictor", "plan", steps)],
        }

    def _predict(self, state: TeamState) -> dict:
        print("\n🔮 [Predictor] 正在评估计划风险...")
        risky = self.predictor.evaluate(state["steps"], state["memory_context"])
        if risky:
            handoff = self._handoff("Predictor", "Planner", "risk", risky)
        else:
            handoff = self._handoff("Predictor", "Executor", "plan_approved", state["steps"])
        return {"risky": risky, "handoffs": [handoff]}

    def _after_predict(self, state: TeamState) -> str:
        return "adjust_plan" if state["risky"] else "prepare_action"

    def _adjust_plan(self, state: TeamState) -> dict:
        print("\n🧭 [Planner] 正在根据风险调整计划...")
        steps = self.planner.adjust_plan(
            state["steps"],
            state["risky"],
            self.executor.definition.tools,
        )
        for index, step in enumerate(steps, 1):
            print(f"   📋 调整后步骤 {index}: {step}")
        return {
            "steps": steps,
            "handoffs": [self._handoff("Planner", "Executor", "adjusted_plan", steps)],
        }

    def _prepare_action(self, state: TeamState) -> dict:
        index = len(state["results"])
        step = state["steps"][index]
        session = state["execution_session"]
        update = {}
        if not session:
            if index == 0:
                attempt = state["attempt"] + 1
                print(f"\n⚡ [Executor] 第 {attempt} 轮执行...")
                update["attempt"] = attempt
            print(f"   步骤 {index + 1}/{len(state['steps'])}: {step}")
            context = "\n".join(f"[步骤{i + 1}结果] {result}" for i, result in enumerate(state["results"]))
            session = self.executor.start_step(step, context or "(第一步)")
        progress = self.executor.advance_step(session)
        if progress["status"] == "interrupted":
            return {
                **update,
                "execution_session": progress["session"],
                "pending_interruption": progress["interruption"],
                "action_events": progress.get("actions", []),
            }
        if progress["status"] == "contract_error":
            return {**update, "failure": progress["error"], "action_events": progress["actions"]}

        results = state["results"] + [progress["result"]]
        update = {
            **update,
            "results": results,
            "execution_session": {},
            "pending_interruption": {},
            "action_events": progress.get("actions", []),
        }
        if len(results) == len(state["steps"]):
            update["handoffs"] = [self._handoff("Executor", "Reviewer", "result", {
                "steps": state["steps"],
                "results": results,
            })]
        return update

    def _interrupt_for_human(self, state: TeamState) -> dict:
        """Pause once, then pass the resolution to the Executor."""
        interruption = state["pending_interruption"]
        resolution = self.executor.resolve_interruption(
            state["execution_session"],
            interruption,
            interrupt(interruption),
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

    def _after_prepare(self, state: TeamState) -> str:
        if state["failure"]:
            return "end"
        if state["pending_interruption"]:
            return "interrupt_for_human"
        if len(state["results"]) < len(state["steps"]):
            return "prepare_action"
        return "review"

    def _after_interruption(self, state: TeamState) -> str:
        if state["failure"]:
            return "end"
        if state["pending_interruption"]:
            return "interrupt_for_human"
        return "prepare_action"

    def _review(self, state: TeamState) -> dict:
        print("\n🔎 [Reviewer] 正在评审结果...")
        verdict = self.reviewer.review(state["task"], state["steps"], state["results"])
        if verdict.get("verdict") == "accept":
            print(f"   ✅ 通过（第 {state['attempt']} 轮）：{verdict.get('reason', '')}")
            handoff = self._handoff("Reviewer", "Team", "accept", verdict)
            has_review_rejection = state["has_review_rejection"]
        else:
            print(f"   🔴 打回（第 {state['attempt']} 轮）：{verdict.get('reason', '')}")
            handoff = self._handoff("Reviewer", "Planner", "revise", verdict)
            # A rejected review is an experience signal even if retry is exhausted.
            has_review_rejection = True
        return {
            "verdict": verdict,
            "has_review_rejection": has_review_rejection,
            "handoffs": [handoff],
        }

    def _after_review(self, state: TeamState) -> str:
        if state["verdict"].get("verdict") == "accept":
            return "save_memory"
        if state["attempt"] > state["max_retries"]:
            print(f"   ⛔ 已达最大重试 {state['max_retries']} 次，终止")
            return "save_memory"
        return "revise_plan"

    def _revise_plan(self, state: TeamState) -> dict:
        print("\n🧭 [Planner] 正在根据评审意见修订计划...")
        steps = self.planner.revise_plan(
            state["task"],
            state["steps"],
            state["verdict"].get("suggestion", ""),
        )
        return {
            "steps": steps,
            "results": [],
            "execution_session": {},
            "pending_interruption": {},
            "handoffs": [self._handoff("Planner", "Executor", "revised_plan", steps)],
        }

    def _save_memory(self, state: TeamState) -> dict:
        results = state["results"]
        outcome = results[-1] if results else "(未执行)"
        self.memory.episodic_add(state["task"], state["steps"][:len(results)], results, outcome)

        if not state["has_review_rejection"]:
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

    @staticmethod
    def _handoff(sender: str, recipient: str, intent: str, content: object) -> dict[str, object]:
        """Record a role handoff as runtime evidence, not a routing command."""
        preview = str(content)
        if len(preview) > 80:
            preview = preview[:80] + "..."
        print(f"   ✉️  {sender} → {recipient} [{intent}]: {preview}")
        return {
            "sender": sender,
            "recipient": recipient,
            "intent": intent,
            "content": content,
        }
