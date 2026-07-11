"""世界模型。对应架构图「世界模型：行动后果预测 · 内在试错」。

在 System 2 规划之后、System 1 执行之前，对计划进行后果预测。
预测结果反馈给 System 2 以调整计划。
"""

from . import llm

PREDICT_PROMPT = """\
你是世界模型（World Model）。你的职责是在行动前预测后果。

你会收到一个即将执行的计划（步骤列表）和当前的环境上下文。
请为每个步骤预测：
1. 预期结果：正常情况下会发生什么
2. 风险：可能出错的地方
3. 建议：是否需要调整（可选）

输出 JSON 数组，每个元素对应一个步骤：
[
  {"step": "步骤描述", "expected": "预期结果", "risk": "可能的风险", "suggestion": "调整建议或null"}
]

只输出 JSON，不要其他内容。
"""


def predict(steps: list[str], context: str = "") -> list[dict]:
    """对计划的每个步骤做行动前预测。"""
    prompt = f"环境上下文：\n{context or '(无)'}\n\n计划步骤：\n"
    for i, s in enumerate(steps, 1):
        prompt += f"{i}. {s}\n"

    predictions = llm.chat_json([
        {"role": "system", "content": PREDICT_PROMPT},
        {"role": "user", "content": prompt},
    ])

    return predictions


def has_high_risk(predictions: list[dict]) -> list[dict]:
    """筛选出有风险提示的步骤。"""
    risky = []
    for p in predictions:
        risk = p.get("risk", "")
        if risk and risk.lower() not in ("无", "none", "null", "没有", "无风险"):
            risky.append(p)
    return risky
