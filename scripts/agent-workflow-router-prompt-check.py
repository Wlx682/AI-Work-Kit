#!/usr/bin/env python3
"""Check the first workflow-router prompt fixture, optionally against DeepSeek."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


PROMPT = """你是 AI-Work-Kit 的只读 workflow 路由建议器。

背景：
- 你只负责把用户自然语言请求映射到 workflow 蓝图和下一步命令。
- 你不写需求、方案、代码、测试、部署内容。
- 你不修改 Plan、Contexts、Epic，也不跳过 workflow-gate。

可选 workflow：
- client-dev：客户端功能、做个功能、全流程开发、启动项目。
- computer-mgmt：电脑空间、电脑管理、清理电脑、磁盘满了、释放空间、备份电脑、系统加固。
- unknown：显式 workflow 不存在，或请求不属于工作流入口。
- needs_clarification：信息不足，无法安全选择。

判断规则：
1. 如果用户显式给出 workflow=xxx，优先使用该 workflow；若不在可选 workflow 中，返回 unknown。
2. 如果是单阶段任务，如 PRD 评审、日报、学习审计、Figma 对稿、测试计划、部署清单、代码 review，不要路由到完整开发工作流，返回 needs_clarification。
3. 如果是普通代码任务、修 bug、开发环境报错、普通资料整理，不要默认路由到 client-dev。
4. 只有明确是客户端功能/全流程开发，才选择 client-dev。
5. 只有明确是电脑管理/清理/备份/加固，才选择 computer-mgmt。

输出必须是 JSON，不要输出多余文字：
{
  "workflow": "client-dev | computer-mgmt | unknown | needs_clarification",
  "reason": "一句话说明命中或不命中的依据",
  "next_command": "建议用户执行的下一步命令；不能安全建议时填空字符串",
  "allowed_actions": ["只读建议"],
  "blocked_actions": ["不写文件", "不跳门禁", "不替代阶段 Skill"]
}

用户请求：
{user_request}
"""


CASES = [
    {
        "name": "client-dev positive",
        "input": "全流程开发一下支付收银台",
        "workflow": "client-dev",
        "command_contains": ["template-generator", "workflow=client-dev"],
    },
    {
        "name": "computer-mgmt positive",
        "input": "帮我清理电脑缓存",
        "workflow": "computer-mgmt",
        "command_contains": ["workflow-status.py", "computer-mgmt"],
    },
    {
        "name": "single code task negative",
        "input": "实现这个函数",
        "workflow": "needs_clarification",
        "command_contains": [],
    },
    {
        "name": "unknown explicit workflow",
        "input": "workflow=unknown 做一下",
        "workflow": "unknown",
        "command_contains": [],
    },
]


REQUIRED_BLOCKED = {"不写文件", "不跳门禁", "不替代阶段 Skill"}


def extract_json(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return json.loads(stripped)


def validate_result(case: dict, result: dict) -> list[str]:
    errors: list[str] = []
    if result.get("workflow") != case["workflow"]:
        errors.append(f"workflow expected {case['workflow']!r}, got {result.get('workflow')!r}")

    command = result.get("next_command", "")
    if not isinstance(command, str):
        errors.append("next_command must be a string")
    elif case["command_contains"]:
        for needle in case["command_contains"]:
            if needle not in command:
                errors.append(f"next_command missing {needle!r}: {command!r}")
    elif command.strip():
        errors.append(f"next_command should be empty for blocked case, got {command!r}")

    blocked = result.get("blocked_actions", [])
    if not isinstance(blocked, list):
        errors.append("blocked_actions must be a list")
    else:
        missing = REQUIRED_BLOCKED.difference(str(item) for item in blocked)
        if missing:
            errors.append(f"blocked_actions missing {sorted(missing)!r}")

    allowed = result.get("allowed_actions", [])
    if "只读建议" not in [str(item) for item in allowed]:
        errors.append("allowed_actions must include '只读建议'")

    return errors


def call_deepseek(api_key: str, model: str, user_request: str, timeout: int) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": PROMPT.format(user_request=user_request)},
        ],
        "response_format": {"type": "json_object"},
        "stream": False,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    content = body["choices"][0]["message"]["content"]
    return extract_json(content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="call DeepSeek API instead of only checking fixtures")
    parser.add_argument("--model", default=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash"))
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    if not args.live:
        print("DRY-RUN: prompt fixture has 4 cases")
        for case in CASES:
            print(f"- {case['name']}: {case['input']} -> {case['workflow']}")
        print("Run with --live after exporting DEEPSEEK_API_KEY.")
        return 0

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY is not set", file=sys.stderr)
        return 2

    failures = 0
    for case in CASES:
        try:
            result = call_deepseek(api_key, args.model, case["input"], args.timeout)
        except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
            failures += 1
            print(f"FAIL {case['name']}: {exc}", file=sys.stderr)
            continue

        errors = validate_result(case, result)
        if errors:
            failures += 1
            print(f"FAIL {case['name']}: {errors}; result={json.dumps(result, ensure_ascii=False)}")
        else:
            print(f"PASS {case['name']}: {json.dumps(result, ensure_ascii=False)}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
