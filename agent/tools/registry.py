"""工具注册表：统一行动空间的入口。

对应架构图「统一行动空间」——所有工具在此注册和发现。
"""

from typing import Callable, Optional

_functions: dict[str, Callable] = {}
_schemas: list[dict] = []


def register(name: str, description: str, parameters: dict, func: Callable):
    """注册一个工具。

    Args:
        name: 工具名称（唯一标识）。
        description: 工具描述（给 LLM 看的）。
        parameters: JSON Schema 格式的参数定义。
        func: 实际执行函数，接受 **kwargs，返回 str。
    """
    _functions[name] = func
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


def list_tools() -> list[str]:
    return list(_functions.keys())
