"""能力·规划（planning）：拆解任务 / 按风险或反馈调整计划。对应架构图 System 2 慢思考。

以前 system2.plan 和 roles/planner 各写一份规划逻辑；现在统一到这里。
"""

import json

from .. import llm

PLAN_PROMPT = """\
你的职责是把用户的任务拆解成具体的执行步骤。

规则：
- 你只负责规划，不负责执行。
- 输出一个 JSON 数组，每个元素是一个步骤描述（字符串）。
- 步骤要具体到可以直接用工具执行。
- 步骤数量控制在 1~6 步。
- 如果提供了记忆上下文，参考历史经验优化计划。
- 只输出 JSON 数组，不要其他内容。
"""

ADJUST_PROMPT = """\
世界模型对你的计划做了风险预测，有以下风险：

{risks}

原始计划：
{plan}

请根据风险预测调整计划。输出调整后的完整步骤列表（JSON 数组）。
如果风险可以接受，保持原计划不变。只输出 JSON 数组。
"""

REVISE_PROMPT = """\
上一版计划被评审打回了，附带了修改建议。

请你判断该怎么改，然后输出 JSON：
{
  "decision": "tweak" 或 "replan",
  "steps": ["步骤1", "步骤2", ...]
}

规则：
- "tweak"：上一版大方向没错，只是局部要改，你在原计划基础上小改。
- "replan"：上一版思路本身有问题，你推翻重来。
- steps 是你最终决定的完整新计划（JSON 数组）。
- 只输出 JSON。
"""


def make_plan(task: str, memory_context: str = "") -> list[str]:
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


def revise_plan(task: str, prev_steps: list[str], suggestion: str) -> dict:
    """根据评审建议决定微调还是重规划，返回 {"decision", "steps"}。"""
    payload = (
        f"任务：{task}\n\n"
        f"上一版计划：{json.dumps(prev_steps, ensure_ascii=False)}\n\n"
        f"评审的修改建议：{suggestion}"
    )
    result = llm.chat_json([
        {"role": "system", "content": REVISE_PROMPT},
        {"role": "user", "content": payload},
    ])
    return {
        "decision": result.get("decision", "tweak"),
        "steps": result.get("steps", prev_steps),
    }
