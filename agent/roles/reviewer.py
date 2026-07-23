"""Reviewer：评审者 Agent。第三方视角审执行结果，可打回。"""

from ..capabilities import reviewing
from .base import BaseAgent


class Reviewer(BaseAgent):
    name = "Reviewer"
    definition_id = "reviewer"

    def review(self, task: str, steps: list[str], results: list[str]) -> dict:
        """审查执行结果，返回 accept/revise 结论。"""
        return reviewing.review(task, steps, results, self.definition.acceptance)
