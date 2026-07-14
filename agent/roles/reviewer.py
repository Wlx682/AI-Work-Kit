"""Reviewer：评审者 Agent。第三方视角审执行结果，可打回。

薄壳：自身只负责"身份 + A2A 通信"，真正的评审本事调用能力层 reviewing。
它没参与规划和执行，因此不会被过程中的思路带偏——这正是独立评审的价值。
决策 3-C：Reviewer 只给建议，不替 Planner 决定怎么改。
"""

from ..capabilities import reviewing
from .base import BaseAgent


class Reviewer(BaseAgent):
    name = "Reviewer"

    def review(self, task: str, steps: list[str], results: list[str]) -> dict:
        """审查执行结果，accept 则通知协调者收工，revise 则打回给 Planner。"""
        verdict = reviewing.review(task, steps, results)

        if verdict.get("verdict") == "accept":
            self.send("Coordinator", "review", {"verdict": "accept", "reason": verdict.get("reason", "")})
        else:
            self.send("Planner", "revise", verdict.get("suggestion", ""))
        return verdict
