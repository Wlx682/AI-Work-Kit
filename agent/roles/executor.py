"""Executor：执行者 Agent。只按计划干活，看不到全局意图。"""

from ..capabilities import act
from .base import BaseAgent


class Executor(BaseAgent):
    name = "Executor"
    definition_id = "executor"

    def run(self, steps: list[str]) -> list[str]:
        """按顺序执行所有步骤，返回每步结果。"""
        results: list[str] = []
        for i, step in enumerate(steps, 1):
            print(f"\n   ⚡ Executor 执行 {i}/{len(steps)}: {step}")
            context = "\n".join(f"[步骤{j+1}结果] {r}" for j, r in enumerate(results))
            results.append(act.run_step(step, context or "(第一步)", self.definition))

        return results
