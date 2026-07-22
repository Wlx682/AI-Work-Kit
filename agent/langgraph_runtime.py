"""LangGraph runtime for the single-agent orchestration workflow."""

from __future__ import annotations

from dataclasses import replace
from operator import add
from typing import Annotated, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from . import self_improve, world_model
from .capabilities import act, planning, reviewing
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


class LangGraphRuntime:
    """Maps the existing agent policies onto a LangGraph StateGraph."""

    def __init__(self, memory: Memory, trace_store: TraceStore | None = None):
        self.memory = memory
        self.trace_store = trace_store or TraceStore()
        self.checkpointer = InMemorySaver()
        self.graph = self._build_graph()

    def run(self, task: str) -> RunResult:
        run_id = uuid4().hex
        events = [RunEvent(1, run_id, "run", "started", {"task": task})]
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
        }

        try:
            for chunk in self.graph.stream(
                initial_state,
                config,
                stream_mode="updates",
                version="v2",
            ):
                if chunk["type"] != "updates":
                    continue
                for node_name, update in chunk["data"].items():
                    payload = dict(update) if update else {}
                    events.append(RunEvent(
                        len(events) + 1,
                        run_id,
                        node_name,
                        "completed",
                        payload,
                    ))

            state = self.graph.get_state(config).values
            outcome = state.get("outcome") or "(未执行)"
        except Exception as error:
            message = str(error) or error.__class__.__name__
            events.append(RunEvent(len(events) + 1, run_id, "run", "failed", {"error": message}))
            return self._persist_trace(RunResult(run_id, task, None, tuple(events), message))

        events.append(RunEvent(len(events) + 1, run_id, "run", "completed", {"outcome": outcome}))
        return self._persist_trace(RunResult(run_id, task, outcome, tuple(events)))

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
        builder.add_node("execute_step", self._execute_step)
        builder.add_node("reflect", self._reflect)
        builder.add_node("save_memory", self._save_memory)

        builder.add_edge(START, "load_memory")
        builder.add_edge("load_memory", "plan")
        builder.add_edge("plan", "predict")
        builder.add_edge("predict", "execute_step")
        builder.add_conditional_edges("execute_step", self._after_execute, {
            "reflect": "reflect",
            "save_memory": "save_memory",
        })
        builder.add_conditional_edges("reflect", self._after_reflect, {
            "execute_step": "execute_step",
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
        steps = planning.make_plan(state["task"], state["memory_context"])
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

    def _execute_step(self, state: AgentState) -> dict:
        index = len(state["results"])
        step = state["steps"][index]
        print(f"\n⚡ [执行] 步骤 {index + 1}/{len(state['steps'])}: {step}")
        context = "\n".join(
            f"[步骤{result_index + 1}结果] {result}"
            for result_index, result in enumerate(state["results"])
        )
        result = act.run_step(step, context or "(第一步，暂无上下文)")
        self.memory.working_add({"step": step, "result": result, "summary": result[:100]})
        return {"results": [result]}

    def _after_execute(self, state: AgentState) -> str:
        if len(state["results"]) >= len(state["steps"]) or len(state["results"]) >= MAX_STEPS:
            return "save_memory"
        return "reflect"

    def _reflect(self, state: AgentState) -> dict:
        print("\n🔎 [反思] 正在评估进展...")
        done_index = len(state["results"])
        decision = reviewing.reflect(state["task"], state["steps"], done_index, state["results"])
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
        return "execute_step"

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
