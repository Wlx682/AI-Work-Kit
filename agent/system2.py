"""System 2：慢思考。对应架构图「系统2（慢思考）规划 · 反思 · 世界模型模拟」。

职责：
1. 读取上下文（记忆 + 用户输入）
2. 生成可执行计划（步骤列表）
3. 调用世界模型做行动前预测，根据预测调整计划
4. 每步执行后反思，决定继续/调整/完成
"""

from . import llm

PLAN_PROMPT = """\
你是 System 2（规划者）。你的职责是把用户的任务拆解成具体的执行步骤。

规则：
- 你只负责规划，不负责执行。
- 输出一个 JSON 数组，每个元素是一个步骤描述（字符串）。
- 步骤要具体到可以直接用工具执行。
- 步骤数量控制在 1~6 步。
- 如果提供了记忆上下文，参考历史经验优化计划。
- 只输出 JSON 数组，不要其他内容。
"""

REFLECT_PROMPT = """\
你是 System 2（反思者）。你会看到已完成步骤的执行结果和剩余步骤。

请判断：
- 如果剩余步骤仍然合理，输出：{"action": "continue"}
- 如果需要调整剩余步骤，输出：{"action": "replan", "new_steps": ["新步骤1", ...]}
- 如果任务已经完成，输出：{"action": "done", "summary": "一句话总结"}

只输出 JSON。
"""

ADJUST_PROMPT = """\
你是 System 2（规划调整者）。世界模型对你的计划做了风险预测，有以下风险：

{risks}

原始计划：
{plan}

请根据风险预测调整计划。输出调整后的完整步骤列表（JSON 数组）。
如果风险可以接受，保持原计划不变。只输出 JSON 数组。
"""


def plan(task: str, memory_context: str = "") -> list[str]:
    """把任务拆解成步骤列表。"""
    user_content = task
    if memory_context and memory_context != "(无记忆)":
        user_content = f"参考信息：\n{memory_context}\n\n任务：{task}"

    return llm.chat_json([
        {"role": "system", "content": PLAN_PROMPT},
        {"role": "user", "content": user_content},
    ])


def adjust_plan(steps: list[str], risky_predictions: list[dict]) -> list[str]:
    """根据世界模型的风险预测调整计划。"""
    risks_text = "\n".join(
        f"- 步骤「{p['step']}」：风险={p['risk']}，建议={p.get('suggestion', '无')}"
        for p in risky_predictions
    )
    plan_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))

    prompt = ADJUST_PROMPT.format(risks=risks_text, plan=plan_text)
    return llm.chat_json([
        {"role": "system", "content": prompt},
        {"role": "user", "content": "请输出调整后的计划。"},
    ])


def reflect(task: str, steps: list[str], done_index: int, results: list[str]) -> dict:
    """反思已完成的结果，决定下一步。"""
    completed = "\n".join(f"步骤 {i+1} [{steps[i]}]: {r}" for i, r in enumerate(results))
    remaining = "\n".join(
        f"步骤 {i+1}: {s}"
        for i, s in enumerate(steps[done_index:], done_index)
    )

    return llm.chat_json([
        {"role": "system", "content": REFLECT_PROMPT},
        {"role": "user", "content": (
            f"原始任务：{task}\n\n已完成：\n{completed}\n\n剩余步骤：\n{remaining or '(无)'}"
        )},
    ])
