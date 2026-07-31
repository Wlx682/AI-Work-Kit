"""Planner：规划者 Agent。只出计划，不碰工具。"""

from ..capabilities import planning
from .base import BaseAgent


class Planner(BaseAgent):
    name = "Planner"
    definition_id = "planner"

    def make_plan(
        self,
        task: str,
        memory_context: str = "",
        execution_tools: tuple[str, ...] | None = None,
    ) -> list[str]:
        """首次规划：把任务拆解成可执行步骤。"""
        if execution_tools is not None:
            return planning.make_plan(
                task,
                memory_context,
                self.definition,
                execution_tools=execution_tools,
            )
        return planning.make_plan(task, memory_context, self.definition)

    def adjust_plan(
        self,
        steps: list[str],
        risky: list[dict],
        execution_tools: tuple[str, ...] = (),
    ) -> list[str]:
        """根据 Predictor 的风险预测调整计划。"""
        steps = planning.adjust_plan(steps, risky, execution_tools=execution_tools)
        print(f"   🧭 Planner 根据风险调整了计划")
        return steps

    def revise_plan(self, task: str, prev_steps: list[str], suggestion: str) -> list[str]:
        """根据评审建议决定微调还是重规划。"""
        result = planning.revise_plan(task, prev_steps, suggestion)
        decision, steps = result["decision"], result["steps"]
        print(f"   🧭 Planner 决定：{'微调' if decision == 'tweak' else '重新规划'}")
        return steps
