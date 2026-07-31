"""工具注册表：统一行动空间的入口。

对应架构图「统一行动空间」——所有工具在此注册和发现。
"""

import json
from typing import Callable, Optional

from jsonschema import Draft202012Validator, ValidationError

_functions: dict[str, Callable] = {}
_schemas: list[dict] = []
_output_schemas: dict[str, dict] = {}


def register(
    name: str,
    description: str,
    parameters: dict,
    output_schema: dict,
    func: Callable,
):
    """注册一个工具。

    Args:
        name: 工具名称（唯一标识）。
        description: 工具描述（给 LLM 看的）。
        parameters: JSON Schema 格式的参数定义。
        output_schema: MCP outputSchema，约束成功时的 structuredContent。
        func: 实际执行函数，接受 **kwargs，返回 MCP 风格结果。
    """
    _functions[name] = func
    _output_schemas[name] = output_schema
    _schemas.append({
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    })


def get_function(name: str) -> Optional[Callable]:
    return _functions.get(name)


def get_all_schemas() -> list[dict]:
    return list(_schemas)


def get_output_schema(name: str) -> Optional[dict]:
    """Return the MCP outputSchema declared for one local tool."""
    return _output_schemas.get(name)


def success(structured_content: dict, text: str | None = None) -> dict:
    """Build a successful MCP CallToolResult for a local tool."""
    return {
        "content": [{"type": "text", "text": text or json.dumps(structured_content, ensure_ascii=False)}],
        "structuredContent": structured_content,
        "isError": False,
    }


def error(message: str) -> dict:
    """Build an MCP tool execution error without inventing successful output."""
    return {
        "content": [{"type": "text", "text": message}],
        "isError": True,
    }


def validate_tool_result(name: str, result: object) -> dict:
    """Validate a local MCP-style result before it enters the agent context."""
    if not isinstance(result, dict):
        raise ValidationError("tool result must be an object")
    content = result.get("content")
    if not isinstance(content, list) or not all(
        isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str)
        for item in content
    ):
        raise ValidationError("tool result content must be text content blocks")

    is_error = result.get("isError", False)
    if not isinstance(is_error, bool):
        raise ValidationError("tool result isError must be a boolean")
    if is_error:
        return result

    structured_content = result.get("structuredContent")
    if not isinstance(structured_content, dict):
        raise ValidationError("successful tool result requires structuredContent")
    output_schema = get_output_schema(name)
    if output_schema is None:
        raise ValidationError(f"tool {name} has no outputSchema")
    Draft202012Validator(output_schema).validate(structured_content)
    return result


def list_tools() -> list[str]:
    return list(_functions.keys())
