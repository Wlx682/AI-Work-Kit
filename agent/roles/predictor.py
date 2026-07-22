"""Predictor：预测者 Agent。独立第三方视角预测计划风险。

薄壳：自身只负责"身份 + A2A 通信"，真正的预测本事调用 world_model。
和 Reviewer 同理——Planner 不能预测自己的计划，就像不能审自己的代码。
"""

from .. import world_model
from .base import BaseAgent


class Predictor(BaseAgent):
    name = "Predictor"
    definition_id = "predictor"

    def evaluate(self, steps: list[str], context: str = "") -> list[dict]:
        """对计划做行动前预测，返回高风险项（空列表=安全）。"""
        print(f"\n   🔮 Predictor 正在预测 {len(steps)} 个步骤...")
        predictions = world_model.predict(steps, context, self.definition)
        risky = world_model.has_high_risk(predictions)

        if risky:
            for p in risky:
                print(f"      ⚠️  {p['step']}: {p['risk']}")
            self.send("Planner", "risk", risky)
        else:
            print("      ✅ 未发现高风险")
            self.send("Coordinator", "safe", {"steps": len(steps)})

        return risky
