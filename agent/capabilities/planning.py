"""能力·规划（planning）：拆解任务 / 按风险或反馈调整计划。

以前单智能体和角色规划者各写一份规划逻辑；现在统一到这里。
"""

import json
from typing import TYPE_CHECKING

from jsonschema import Draft202012Validator, ValidationError

from ..infrastructure import llm

if TYPE_CHECKING:
    from ..core.definition import AgentDefinition

PLAN_PROMPT = """\
你的职责是把用户的任务拆解成具体的执行步骤。

规则：
- 你只负责规划，不负责执行。
- 输出一个 JSON 数组，每个元素是一个步骤描述（字符串）。
- 步骤要具体到可以直接用工具执行。
- 步骤数量控制在 1~6 步。
- 如果提供了记忆上下文，参考历史经验优化计划。
- 只能围绕已注册的执行工具规划；未注册的外部服务、网站、API 或凭据不能假定存在。
- 通用的本地文件和 shell 工具不等同于某个外部服务的适配器，不能借此假设能够获得该服务的数据。
- 已注册工具清单是穷尽集合，不要规划“检测是否存在工具”、扫描本地缓存或配置来寻找未注册的外部服务。
- 若完成任务所需的数据服务未注册，用户输入后应如实说明缺少相应适配器；不要为此创建报告文件或编造替代数据。
- 用户任务缺少业务参数时，先规划为通过 request_user_input 询问完成任务所需的最少非敏感信息。
- API 密钥、密码、令牌等秘密不能作为计划步骤或向用户索取的信息；它们只能由已配置的工具适配器从受控环境取得。
- 只输出 JSON 数组，不要其他内容。
"""

ADJUST_PROMPT = """\
世界模型对你的计划做了风险预测，有以下风险：

{risks}

原始计划：
{plan}

请根据风险预测调整计划。输出调整后的完整步骤列表（JSON 数组）。
如果风险可以接受，保持原计划不变。只输出 JSON 数组。

调整规则：
- 保持原任务边界，不要把通用的网络、密钥、重试、备用数据源或格式化建议扩写成新的执行工作。
- 不得为未注册的外部服务、网站、API 或凭据设计步骤，也不得要求用户提供秘密。
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

PLAN_OUTPUT_SCHEMA = {
    "type": "array",
    "minItems": 1,
    "maxItems": 6,
    "items": {"type": "string", "minLength": 1},
}


def make_plan(
    task: str,
    memory_context: str = "",
    definition: "AgentDefinition | None" = None,
    *,
    execution_tools: tuple[str, ...] | None = None,
) -> list[str]:
    """把任务拆解成步骤列表。"""
    user_content = task
    if memory_context and memory_context != "(无记忆)":
        user_content = f"参考信息：\n{memory_context}\n\n任务：{task}"

    available_tools = execution_tools
    if available_tools is None:
        available_tools = definition.tools if definition is not None else ()

    prompt = f"{PLAN_PROMPT}\n\n{_execution_capability_context(available_tools)}"
    if definition is not None:
        prompt = f"{prompt}\n\n{definition.prompt_context()}"

    result = llm.chat_json([
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_content},
    ])
    return _validate_steps(result)


def adjust_plan(
    steps: list[str],
    risky_predictions: list[dict],
    *,
    execution_tools: tuple[str, ...] = (),
) -> list[str]:
    """根据世界模型的风险预测调整计划。"""
    risks_text = "\n".join(
        f"- 步骤「{p['step']}」：风险={p['risk']}，建议={p.get('suggestion', '无')}"
        for p in risky_predictions
    )
    plan_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))

    prompt = (
        f"{ADJUST_PROMPT.format(risks=risks_text, plan=plan_text)}\n\n"
        f"{_execution_capability_context(execution_tools)}"
    )
    result = llm.chat_json([
        {"role": "system", "content": prompt},
        {"role": "user", "content": "请输出调整后的计划。"},
    ])
    return _validate_steps(result)


def _execution_capability_context(execution_tools: tuple[str, ...]) -> str:
    """State execution capability separately from the Planner's own empty tool list."""
    names = ", ".join(execution_tools) if execution_tools else "（无）"
    return f"已注册的执行工具：{names}"


def _validate_steps(value: object) -> list[str]:
    """Reject malformed model output before it becomes executable graph state."""
    try:
        Draft202012Validator(PLAN_OUTPUT_SCHEMA).validate(value)
    except ValidationError as error:
        raise ValueError(f"plan output does not match schema: {error.message}") from error
    steps = [step.strip() for step in value]
    if any(not step for step in steps):
        raise ValueError("plan output does not match schema: steps must not be blank")
    return steps


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
