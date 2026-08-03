"""Predictor：预测者 Agent。独立第三方视角预测计划风险。"""

from ..cognition import world_model
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
        else:
            print("      ✅ 未发现高风险")

        return risky
