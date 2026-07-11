"""LLM 客户端封装。统一所有模块对 DeepSeek API 的调用。"""

import os
import json
from openai import OpenAI


_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
        )
    return _client


def chat(messages: list[dict], tools: list[dict] | None = None, max_tokens: int = 8192) -> dict:
    """调用 LLM，返回标准化结果。

    Returns:
        {
            "content": str | None,       # 文本回复
            "tool_calls": list | None,    # 工具调用列表
            "finish_reason": str,         # "stop" / "tool_calls"
            "raw": message object,        # 原始 message，用于拼接 messages
        }
    """
    kwargs = dict(
        model="deepseek-chat",
        max_tokens=max_tokens,
        messages=messages,
    )
    if tools:
        kwargs["tools"] = tools

    response = get_client().chat.completions.create(**kwargs)
    choice = response.choices[0]
    msg = choice.message

    return {
        "content": msg.content,
        "tool_calls": msg.tool_calls,
        "finish_reason": choice.finish_reason,
        "raw": msg,
    }


def chat_json(messages: list[dict]) -> dict | list:
    """调用 LLM 并解析返回的 JSON。"""
    result = chat(messages)
    raw = result["content"] or ""
    # 兼容 LLM 用 ```json 包裹的情况
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
