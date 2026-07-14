"""目标循环编排器。对应架构图「单智能体操作系统」的核心调度。

串联所有子系统：
  System 2 规划 → 世界模型预测 → System 2 调整
  → System 1 执行（经安全层）→ System 2 反思
  → 记忆沉淀
"""

from .capabilities import planning, act, reviewing
from . import world_model
from . import self_improve
from .memory import Memory

MAX_STEPS = 10


class Orchestrator:
    """单智能体操作系统的编排器。"""

    def __init__(self, memory: Memory):
        self.memory = memory

    def run(self, task: str) -> str:
        """运行完整的目标循环，返回最终结果。"""

        print(f"\n🎯 任务: {task}")
        print("─" * 60)

        mem_context = self._load_memory()
        steps = self._plan(task, mem_context)
        steps = self._predict_and_adjust(steps, mem_context)
        results = self._execute_loop(task, steps)
        self._save_memory(task, steps, results)

        total = len(results)
        print("\n" + "─" * 60)
        print(f"✅ 任务完成（共执行 {total} 步）")

        return results[-1] if results else "(未执行)"

    # --- 内部阶段 ---

    def _load_memory(self) -> str:
        mem_context = self.memory.to_context()
        if mem_context != "(无记忆)":
            print(f"\n📚 记忆上下文已加载")
        return mem_context

    def _plan(self, task: str, mem_context: str) -> list[str]:
        print("\n🧠 System 2 正在规划...")
        steps = planning.make_plan(task, mem_context)
        for i, step in enumerate(steps, 1):
            print(f"   📋 步骤 {i}: {step}")
        return steps

    def _predict_and_adjust(self, steps: list[str], mem_context: str) -> list[str]:
        print("\n🔮 世界模型正在预测...")
        predictions = world_model.predict(steps, mem_context)
        risky = world_model.has_high_risk(predictions)

        if not risky:
            print("   ✅ 未发现高风险，计划无需调整")
            return steps

        for p in risky:
            print(f"   ⚠️  {p['step']}: {p['risk']}")

        print("\n🧠 System 2 根据风险调整计划...")
        steps = planning.adjust_plan(steps, risky)
        for i, step in enumerate(steps, 1):
            print(f"   📋 调整后步骤 {i}: {step}")
        return steps

    def _execute_loop(self, task: str, steps: list[str]) -> list[str]:
        results = []
        step_index = 0
        self._has_lesson = False

        while step_index < len(steps) and len(results) < MAX_STEPS:
            step = steps[step_index]

            print(f"\n⚡ 执行步骤 {step_index + 1}/{len(steps)}: {step}")

            context = "\n".join(f"[步骤{i+1}结果] {r}" for i, r in enumerate(results))
            result = act.run_step(step, context or "(第一步，暂无上下文)")
            results.append(result)

            self.memory.working_add({"step": step, "result": result, "summary": result[:100]})
            step_index += 1

            if step_index < len(steps):
                steps, should_stop = self._reflect(task, steps, step_index, results)
                if should_stop:
                    break

        return results

    def _reflect(self, task: str, steps: list[str], done_index: int, results: list[str]) -> tuple[list[str], bool]:
        """System 2 反思。返回 (可能调整后的 steps, 是否结束)。"""
        print("\n🧠 System 2 正在反思...")
        decision = reviewing.reflect(task, steps, done_index, results)

        if decision.get("has_lesson"):
            self._has_lesson = True

        if decision["action"] == "done":
            print(f"   ✅ 提前完成: {decision.get('summary', '')}")
            return steps, True
        elif decision["action"] == "replan":
            # 硬信号兜底：计划被改过就是走了弯路，无条件算有教训（不依赖 LLM 判断）
            self._has_lesson = True
            new_steps = decision["new_steps"]
            print(f"   🔄 调整计划: {new_steps}")
            return steps[:done_index] + new_steps, False
        else:
            print("   ➡️  继续执行")
            return steps, False

    def _save_memory(self, task: str, steps: list[str], results: list[str]):
        outcome = results[-1] if results else "(未执行)"
        self.memory.episodic_add(task, steps[:len(results)], results, outcome)
        self.memory.working_clear()

        # L7: 只在反思判定有教训时才蒸馏（决策 C1）
        if not self._has_lesson:
            print("\n   (执行顺利，无需提炼)")
            return

        print("\n🧪 正在提炼经验...")
        try:
            insights = self_improve.distill(task, steps[:len(results)], results)

            for fact in insights.get("facts", []):
                self.memory.semantic_add(fact, source=task)
                print(f"   💡 知识: {fact}")

            for pat in insights.get("patterns", []):
                self.memory.procedural_add(pat["trigger"], pat["steps"])
                print(f"   📐 模式: 当{pat['trigger']}时 → {' → '.join(pat['steps'])}")

            # 决策 C3: corrections 存入独立的纠正记忆
            for corr in insights.get("corrections", []):
                self.memory.corrections_add(
                    corr.get("mistake", ""),
                    corr.get("lesson", str(corr)),
                    source=task,
                )
                print(f"   🔧 教训: {corr.get('mistake', '')} → {corr.get('lesson', '')}")

            if not any(insights.get(k) for k in ("facts", "patterns", "corrections")):
                print("   (无新经验)")
        except Exception as e:
            print(f"   ⚠️  提炼失败: {e}")

        # 决策 C2: 语义记忆攒够阈值后批量去重合并
        removed = self_improve.consolidate(self.memory)
        if removed > 0:
            print(f"   🧹 语义记忆合并去重，精简了 {removed} 条")
