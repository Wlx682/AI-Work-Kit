"""LangGraph runtime for the four-role Team workflow."""

from __future__ import annotations

from dataclasses import replace
from operator import add
from typing import Annotated, TypedDict
from uuid import uuid4

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from . import self_improve
from .checkpoint_store import DEFAULT_CHECKPOINT_PATH, open_sqlite_checkpointer
from .memory import Memory
from .roles import Executor, Planner, Predictor, Reviewer
from .runtime import RunEvent, RunResult
from .trace_store import TraceStore

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
    pending_approval: dict


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
        run_id = uuid4().hex
        events = [RunEvent(1, run_id, "run", "started", {
            "task": task,
            "team": [
                self.planner.definition.id,
                self.predictor.definition.id,
                self.executor.definition.id,
                self.reviewer.definition.id,
            ],
        })]
        config = {
            "configurable": {"thread_id": run_id},
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
            "pending_approval": {},
        }

        return self._execute_graph(task, run_id, initial_state, config, events)

    def resume(self, run_id: str, decision: object) -> RunResult:
        """Resume a paused Team Graph run with an approval decision."""
        config = {"configurable": {"thread_id": run_id}, "recursion_limit": MAX_RETRIES * 3 + 20}
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
                    events.append(RunEvent(
                        len(events) + 1,
                        run_id,
                        node_name,
                        "completed",
                        dict(update) if update else {},
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

    def checkpoint_count(self, run_id: str) -> int:
        """Return the number of framework checkpoints saved for one team run."""
        return sum(1 for _ in self.checkpointer.list({"configurable": {"thread_id": run_id}}))

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
        builder.add_node("approve_tool", self._approve_tool)
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
            "approve_tool": "approve_tool",
            "review": "review",
        })
        builder.add_edge("approve_tool", "prepare_action")
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
        steps = self.planner.make_plan(state["task"], state["memory_context"])
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
        steps = self.planner.adjust_plan(state["steps"], state["risky"])
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
        if progress["status"] == "approval_required":
            return {
                **update,
                "execution_session": progress["session"],
                "pending_approval": progress["proposal"],
            }

        results = state["results"] + [progress["result"]]
        update = {
            **update,
            "results": results,
            "execution_session": {},
            "pending_approval": {},
        }
        if len(results) == len(state["steps"]):
            update["handoffs"] = [self._handoff("Executor", "Reviewer", "result", {
                "steps": state["steps"],
                "results": results,
            })]
        return update

    def _approve_tool(self, state: TeamState) -> dict:
        decision = interrupt(state["pending_approval"])
        session = self.executor.resolve_approval(state["execution_session"], decision)
        return {"execution_session": session, "pending_approval": {}}

    def _after_prepare(self, state: TeamState) -> str:
        if state["pending_approval"]:
            return "approve_tool"
        if len(state["results"]) < len(state["steps"]):
            return "prepare_action"
        return "review"

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
            "pending_approval": {},
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
