"""多智能体协调者。对应架构图「多智能体协作层」。

协调者本身不干活，只调度四个纯独立 Agent，
让它们靠 A2A 消息总线沟通，跑「规划 → 预测 → (调整?) → 执行 → 评审 → (通过?收工:打回)」循环。

与单智能体 Orchestrator 的区别：
- Orchestrator 是一个全能选手，内部各能力是自己的函数。
- Team 是一个团队，Planner/Predictor/Executor/Reviewer 是四个独立成员，
  Predictor 和 Reviewer 分别是事前和事后的第三方视角。
"""

from .a2a import MessageBus
from .roles import Planner, Predictor, Executor, Reviewer
from . import self_improve
from .memory import Memory

MAX_RETRIES = 3


class Team:
    """四角色多智能体团队的协调者。"""

    def __init__(self):
        self.bus = MessageBus()
        self.planner = Planner(self.bus)
        self.predictor = Predictor(self.bus)
        self.executor = Executor(self.bus)
        self.reviewer = Reviewer(self.bus)
        self.memory = Memory()

    def run(self, task: str, max_retries: int = MAX_RETRIES) -> str:
        """跑完整的多智能体协作循环，返回最终结果。"""
        print(f"\n🎯 任务: {task}")
        print("─" * 60)

        steps = self.planner.make_plan(task)

        risky = self.predictor.evaluate(steps)
        if risky:
            steps = self.planner.adjust_plan(steps, risky)

        results: list[str] = []
        was_revised = False

        for attempt in range(1, max_retries + 2):
            results = self.executor.run(steps)
            verdict = self.reviewer.review(task, steps, results)

            if verdict.get("verdict") == "accept":
                print(f"\n✅ Reviewer 通过（第 {attempt} 轮）：{verdict.get('reason', '')}")
                break

            print(f"\n🔴 Reviewer 打回（第 {attempt} 轮）：{verdict.get('reason', '')}")
            was_revised = True
            if attempt > max_retries:
                print(f"   ⛔ 已达最大重试 {max_retries} 次，终止")
                break

            steps = self.planner.revise_plan(task, steps, verdict.get("suggestion", ""))

        self._save_memory(task, steps, results, was_revised)

        print("\n" + "─" * 60)
        print(f"📜 A2A 消息共 {len(self.bus.transcript())} 条")
        return results[-1] if results else "(未执行)"

    def _save_memory(self, task: str, steps: list[str], results: list[str], was_revised: bool):
        """记忆沉淀 + 经验蒸馏。硬信号：Reviewer 打回过就算有教训。"""
        outcome = results[-1] if results else "(未执行)"
        self.memory.episodic_add(task, steps[:len(results)], results, outcome)

        if not was_revised:
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

        removed = self_improve.consolidate(self.memory)
        if removed > 0:
            print(f"   🧹 语义记忆合并去重，精简了 {removed} 条")
