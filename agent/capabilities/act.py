"""能力·执行（act）：调工具完成一个步骤。

全系统唯一的执行器。以前单智能体执行器和 Executor 各写一份、
几乎逐行重复；现在两边都调这一个 run_step，重复被消除。
"""

import json
from typing import TYPE_CHECKING
from uuid import uuid4

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


def start_step(step: str, context: str = "") -> dict:
    """Create a serializable tool-use session for one execution step."""
    return {
        "messages": [
            {"role": "system", "content": ACT_PROMPT},
            {"role": "user", "content": f"背景信息：\n{context}\n\n当前步骤：{step}"},
        ],
        "pending_calls": [],
        "tool_rounds": 0,
    }


def advance(session: dict, definition: "AgentDefinition | None" = None) -> dict:
    """Advance a session until it finishes or needs an approval decision.

    The returned session and proposal are JSON-serializable so a graph checkpoint
    can preserve the exact tool call that a human is asked to approve.
    """
    messages = list(session["messages"])
    pending_calls = list(session["pending_calls"])
    tool_rounds = session["tool_rounds"]
    actions: list[dict] = []

    while True:
        if pending_calls:
            call = pending_calls[0]
            verdict = _tool_verdict(call["name"], call["args"], definition)
            if verdict.get("needs_approval"):
                return {
                    "status": "approval_required",
                    "session": _session(messages, pending_calls, tool_rounds),
                    "proposal": {
                        "action_id": call["action_id"],
                        "tool_call_id": call["id"],
                        "tool": call["name"],
                        "args": call["args"],
                        "reason": verdict["reason"],
                    },
                    "actions": actions,
                }

            tool_result = _execute_with_verdict(
                call["name"], call["args"], verdict, call["action_id"],
            )
            actions.append(_action_event(call, verdict))
            messages.append(_tool_message(call["id"], tool_result))
            pending_calls.pop(0)
            continue

        if tool_rounds >= MAX_TOOL_ROUNDS:
            return {"status": "done", "result": "(达到工具调用上限)", "actions": actions}

        result = llm.chat(messages, tools=_tool_schemas(definition))
        if result["content"]:
            print(f"   💬 {result['content']}")

        if result["finish_reason"] == "stop" or not result["tool_calls"]:
            return {
                "status": "done",
                "result": result["content"] or "(无输出)",
                "actions": actions,
            }

        calls = _normalize_tool_calls(result["tool_calls"])
        messages.append(_assistant_message(result["content"], calls))
        pending_calls = calls
        tool_rounds += 1


def resolve_approval(
    session: dict,
    decision: object,
    definition: "AgentDefinition | None" = None,
) -> dict:
    """Apply a human decision to the exact first pending tool call."""
    pending_calls = list(session["pending_calls"])
    if not pending_calls:
        raise ValueError("approval requested without a pending tool call")

    call = pending_calls.pop(0)
    approved = decision is True or (
        isinstance(decision, dict) and decision.get("approved") is True
    )
    if not approved:
        safety.log(call["name"], call["args"], "rejected_by_user", call["action_id"])
        tool_result = "用户拒绝执行该操作"
        # Later proposals came from the same model turn and may depend on it.
        pending_calls = []
    else:
        verdict = _tool_verdict(call["name"], call["args"], definition)
        tool_result = _execute_with_verdict(
            call["name"], call["args"], verdict, call["action_id"],
        )

    messages = list(session["messages"])
    messages.append(_tool_message(call["id"], tool_result))
    return _session(messages, pending_calls, session["tool_rounds"])


def _session(messages: list[dict], pending_calls: list[dict], tool_rounds: int) -> dict:
    return {
        "messages": messages,
        "pending_calls": pending_calls,
        "tool_rounds": tool_rounds,
    }


def _normalize_tool_calls(tool_calls: list) -> list[dict]:
    calls = []
    for tool_call in tool_calls:
        calls.append({
            "action_id": uuid4().hex,
            "id": tool_call.id,
            "name": tool_call.function.name,
            "args": json.loads(tool_call.function.arguments),
        })
    return calls


def _assistant_message(content: str | None, calls: list[dict]) -> dict:
    return {
        "role": "assistant",
        "content": content,
        "tool_calls": [
            {
                "id": call["id"],
                "type": "function",
                "function": {
                    "name": call["name"],
                    "arguments": json.dumps(call["args"], ensure_ascii=False),
                },
            }
            for call in calls
        ],
    }


def _tool_message(tool_call_id: str, result: str) -> dict:
    preview = result[:150] + "..." if len(result) > 150 else result
    print(f"      ← {preview}")
    return {"role": "tool", "tool_call_id": tool_call_id, "content": result}


def _tool_verdict(name: str, args: dict, definition: "AgentDefinition | None") -> dict:
    if definition is not None and name not in definition.tools:
        return {"allowed": False, "reason": f"Agent 定义未授权工具: {name}"}
    return safety.check(name, args)


def _action_event(call: dict, verdict: dict) -> dict:
    return {
        "action_id": call["action_id"],
        "tool": call["name"],
        "args": call["args"],
        "status": "called" if verdict.get("allowed", True) else "blocked",
    }


def _execute_with_verdict(name: str, args: dict, verdict: dict, action_id: str) -> str:
    if not verdict.get("allowed", True):
        safety.log(name, args, "blocked", action_id)
        return f"安全层拒绝: {verdict['reason']}"
    fn = get_function(name)
    if fn is None:
        return f"Error: unknown tool '{name}'"
    try:
        print(f"   🔧 {name}({args})")
        out = fn(**args)
        safety.log(name, args, "executed", action_id)
        return out
    except Exception as error:
        return f"Error executing {name}: {error}"

def _tool_schemas(definition: "AgentDefinition | None") -> list[dict]:
    schemas = get_all_schemas()
    if definition is None:
        return schemas
    return [schema for schema in schemas if schema["function"]["name"] in definition.tools]
