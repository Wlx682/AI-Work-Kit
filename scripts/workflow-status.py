#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent

STATE_LABELS = {
    "requirement": "需求分析",
    "architecture": "技术方案",
    "test-first": "验收测试先行",
    "development": "功能开发",
    "verify": "非功能验证",
    "review": "Code Review",
    "deploy": "部署",
    "retro": "团队回顾",
    "done": "全部完成",
}

SKILL_ACTIONS = {
    "template-generator": "创建 Epic 和首个子 plan",
    "event-storming-assistant": "补需求分析 plan",
    "spec-by-example-assistant": "补实例化需求与验收标准",
    "requirement-analyst": "闭环需求 P0",
    "architecture-design-assistant": "补技术方案并评审采纳",
    "test-generator": "补自动化测试 plan 的用例映射",
    "task-splitter": "拆功能开发任务并补覆盖 AC",
    "feature-dev-assistant": "继续功能开发实现",
    "figma-ui": "继续 Figma/UI 子任务",
    "nfr-assistant": "补非功能验证",
    "review-assistant": "补 Review 结论",
    "deployment-assistant": "补部署检查和冒烟计划",
    "retro-assistant": "补团队回顾",
    "material-prep-assistant": "补轻量清单",
}


def run_gate(args: argparse.Namespace) -> dict[str, Any]:
    cmd = ["bash", "scripts/workflow-gate.sh"]
    if args.workflow:
        cmd.extend(["--workflow", args.workflow])
    if args.epic:
        cmd.extend(["--epic", args.epic])
    if args.project:
        cmd.extend(["--project", args.project])
    cmd.append("--json")
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "workflow-gate 执行失败")
    return json.loads(proc.stdout)


def label_state(state: str) -> str:
    return STATE_LABELS.get(state, state or "未知")


def simplify_blocker(blocker: str) -> str:
    text = re.sub(r"\b(?:BLOCKED|WARN):traceability:", "", blocker.strip())
    ac_ids = sorted(set(re.findall(r"AC[0-9A-Za-z_]+(?:-反)?", text)))
    if "无 Epic plan" in text:
        return "还没有 Epic，需要先创建项目总 plan"
    if "testTraceability" in text:
        acs = "、".join(ac_ids)
        suffix = f"：{acs}" if acs else ""
        return f"验收标准缺测试覆盖{suffix}"
    if "无测试覆盖" in text:
        acs = "、".join(ac_ids)
        suffix = f"：{acs}" if acs else ""
        return f"验收标准缺测试覆盖{suffix}"
    if "devTraceability" in text:
        acs = "、".join(ac_ids)
        suffix = f"：{acs}" if acs else ""
        return f"P0 验收标准缺功能开发任务覆盖{suffix}"
    if "无开发任务覆盖" in text:
        acs = "、".join(ac_ids)
        suffix = f"：{acs}" if acs else ""
        return f"P0 验收标准缺功能开发任务覆盖{suffix}"
    if "skill_run" in text:
        return "任务完成反馈缺失或格式不合法"
    if "WBS 切片" in text:
        m = re.search(r"缺:\s*([^)）]+)", text)
        return f"WBS 还有未完成切片：{m.group(1)}" if m else "WBS 切片未完成"
    if "子 Plan 未创建" in text:
        m = re.search(r"（([^）]+)）", text)
        return f"还没有创建子 plan：{m.group(1)}" if m else "还没有创建当前阶段子 plan"
    if "status 须为" in text:
        return "当前阶段 plan 还没评审到目标状态"
    if "p0_open" in text:
        return "仍有 P0 问题未闭环"
    if "plan-gate-check" in text:
        return "开发开工门禁未通过，需要先补齐文档或前置证据"
    return text


def merge_blockers(blockers: list[str]) -> list[str]:
    grouped: dict[str, set[str]] = {
        "验收标准缺测试覆盖": set(),
        "P0 验收标准缺功能开发任务覆盖": set(),
    }
    other: list[str] = []
    for blocker in blockers:
        matched = False
        for prefix in grouped:
            if blocker == prefix or blocker.startswith(prefix + "："):
                matched = True
                if "：" in blocker:
                    grouped[prefix].update(item for item in blocker.split("：", 1)[1].split("、") if item)
                break
        if not matched:
            other.append(blocker)
    merged = []
    for prefix, acs in grouped.items():
        if acs:
            merged.append(f"{prefix}：{'、'.join(sorted(acs))}")
    return merged + other


def current_plan(gate: dict[str, Any]) -> str | None:
    state = gate.get("current_state")
    for item in gate.get("plans_found", []) or []:
        if not isinstance(item, str) or ":" not in item:
            continue
        key, path = item.split(":", 1)
        if key == state and path:
            return path
    if gate.get("epic"):
        return gate["epic"]
    return None


def next_step(gate: dict[str, Any]) -> str:
    if gate.get("current_state") == "done":
        return "归档或蒸馏可复用结论"
    skill = gate.get("recommended_skill") or ""
    return SKILL_ACTIONS.get(skill, f"调用 {skill}" if skill else "查看 blocker 后补齐当前阶段")


def resume_hint(gate: dict[str, Any]) -> str:
    plan = current_plan(gate)
    if plan:
        return f"/resume plan={plan} 进度={label_state(gate.get('current_state', ''))}"
    if gate.get("recommended_skill") == "template-generator":
        return "/start 或 template-generator 创建 Epic"
    return "/status 查看最新状态"


def summarize(gate: dict[str, Any]) -> dict[str, Any]:
    blockers = merge_blockers([simplify_blocker(item) for item in gate.get("blockers", []) or []])
    return {
        "workflow": gate.get("workflow"),
        "current": label_state(gate.get("current_state", "")),
        "current_state": gate.get("current_state"),
        "blocked": bool(blockers),
        "blockers": blockers,
        "next": next_step(gate),
        "recommended_skill": gate.get("recommended_skill"),
        "resume": resume_hint(gate),
        "constitution": gate.get("constitution", {}).get("status"),
        "details": {
            "epic": gate.get("epic"),
            "raw_state": gate.get("current_state"),
            "raw_next": gate.get("next_state"),
        },
    }


def print_human(summary: dict[str, Any]) -> None:
    print(f"当前：{summary['current']}")
    if summary["blocked"]:
        print("卡点：")
        for blocker in summary["blockers"]:
            print(f"- {blocker}")
    else:
        print("卡点：无")
    print(f"下一步：{summary['next']}")
    print(f"继续：{summary['resume']}")
    if summary.get("constitution"):
        print(f"规则：constitution {summary['constitution']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Human-friendly workflow status wrapper.")
    parser.add_argument("--workflow", help="Workflow name, e.g. client-dev or computer-mgmt")
    parser.add_argument("--epic", help="Epic plan path")
    parser.add_argument("--project", help="Project name for workflow-gate lookup")
    parser.add_argument("--json", action="store_true", help="Output simplified JSON")
    args = parser.parse_args()

    try:
        gate = run_gate(args)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"BLOCKED:workflow-status:{exc}", file=sys.stderr)
        return 1
    summary = summarize(gate)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
