"""Executor：执行者 Agent。只按计划干活，看不到全局意图。

薄壳：自身只负责"身份 + A2A 通信"，真正的执行本事调用能力层 act。
和单智能体共用同一个 act.run_step，不再自己写一份工具循环。
"""

from ..capabilities import act
from .base import BaseAgent


class Executor(BaseAgent):
    name = "Executor"

    def run(self, steps: list[str]) -> list[str]:
        """按顺序执行所有步骤，返回每步结果，并把汇总发给 Reviewer。"""
        results: list[str] = []
        for i, step in enumerate(steps, 1):
            print(f"\n   ⚡ Executor 执行 {i}/{len(steps)}: {step}")
            context = "\n".join(f"[步骤{j+1}结果] {r}" for j, r in enumerate(results))
            results.append(act.run_step(step, context or "(第一步)"))

        self.send("Reviewer", "result", {"steps": steps, "results": results})
        return results
