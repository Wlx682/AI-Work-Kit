"""能力·执行（act）：调工具完成一个步骤。

全系统唯一的执行器。以前单智能体执行器和 Executor 各写一份、
几乎逐行重复；现在两边都调这一个 run_step，重复被消除。
"""

import json
from typing import TYPE_CHECKING

from .. import llm
from .. import safety
from ..tools import get_function, get_all_schemas

if TYPE_CHECKING:
    from ..agent_definition import AgentDefinition

ACT_PROMPT = """\
你会收到一个具体的执行步骤，请调用工具完成它。

规则：
- 只执行当前步骤，不要做额外的事。
- 执行完后用 1~3 句话报告结果。
- 如果步骤不需要工具，直接给出结果。
"""

MAX_TOOL_ROUNDS = 5


def run_step(
    step: str,
    context: str = "",
    definition: "AgentDefinition | None" = None,
) -> str:
    """执行单个步骤（工具调用循环 + 安全层），返回结果文本。"""
    messages = [
        {"role": "system", "content": ACT_PROMPT},
        {"role": "user", "content": f"背景信息：\n{context}\n\n当前步骤：{step}"},
    ]
    schemas = _tool_schemas(definition)

    for _ in range(MAX_TOOL_ROUNDS):
        result = llm.chat(messages, tools=schemas)

        if result["content"]:
            print(f"   💬 {result['content']}")

        if result["finish_reason"] == "stop" or not result["tool_calls"]:
            return result["content"] or "(无输出)"

        messages.append(result["raw"])

        for tool_call in result["tool_calls"]:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            print(f"   🔧 {fn_name}({fn_args})")

            tool_result = _safe_run(fn_name, fn_args, definition)

            preview = tool_result[:150] + "..." if len(tool_result) > 150 else tool_result
            print(f"      ← {preview}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            })

    return "(达到工具调用上限)"


def _tool_schemas(definition: "AgentDefinition | None") -> list[dict]:
    schemas = get_all_schemas()
    if definition is None:
        return schemas
    return [schema for schema in schemas if schema["function"]["name"] in definition.tools]


def _safe_run(name: str, args: dict, definition: "AgentDefinition | None" = None) -> str:
    """经安全层审核后执行工具。"""
    if definition is not None and name not in definition.tools:
        return f"Agent 定义未授权工具: {name}"
    verdict = safety.check(name, args)
    if not verdict.get("allowed", True):
        safety.log(name, args, "blocked")
        return f"安全层拒绝: {verdict['reason']}"
    if verdict.get("needs_approval"):
        if not safety.request_approval(name, args, verdict["reason"]):
            return "用户拒绝执行该操作"

    fn = get_function(name)
    if fn is None:
        return f"Error: unknown tool '{name}'"
    try:
        out = fn(**args)
        safety.log(name, args, "executed")
        return out
    except Exception as e:
        return f"Error executing {name}: {e}"
