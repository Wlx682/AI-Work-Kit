"""Planner：规划者 Agent。只出计划，不碰工具。

薄壳：自身只负责"身份 + A2A 通信"，真正的规划本事调用能力层 planning。
决策 3-C：收到评审建议时，由 planning.revise_plan 判断微调还是重规划。
首次规划发给 Predictor 审风险；修订计划直接发 Executor（基于真实反馈，不需二次预测）。
"""

from ..capabilities import planning
from .base import BaseAgent


class Planner(BaseAgent):
    name = "Planner"

    def make_plan(self, task: str) -> list[str]:
        """首次规划：拆解任务，把计划发给 Predictor 审风险。"""
        steps = planning.make_plan(task)
        self.send("Predictor", "plan", steps)
        return steps

    def adjust_plan(self, steps: list[str], risky: list[dict]) -> list[str]:
        """收到 Predictor 的风险预测后，调整计划，发给 Executor。"""
        steps = planning.adjust_plan(steps, risky)
        print(f"   🧭 Planner 根据风险调整了计划")
        self.send("Executor", "plan", steps)
        return steps

    def revise_plan(self, task: str, prev_steps: list[str], suggestion: str) -> list[str]:
        """收到评审建议后，自主决定微调还是重规划，直接发给 Executor。"""
        result = planning.revise_plan(task, prev_steps, suggestion)
        decision, steps = result["decision"], result["steps"]
        print(f"   🧭 Planner 决定：{'微调' if decision == 'tweak' else '重新规划'}")
        self.send("Executor", "plan", steps)
        return steps
