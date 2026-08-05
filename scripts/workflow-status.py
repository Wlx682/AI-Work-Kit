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
RUN_DIR = ROOT / ".workflows" / "runs"
EVENT_DIR = ROOT / ".workflows" / "events"

STATE_LABELS = {
    "requirement": "需求分析",
    "prioritization": "需求排序",
    "architecture": "技术方案",
    "story-split": "纵向 Story 拆分/故事点",
    "story-check": "Story Scope 自检",
    "story-development": "逐 Story TDD 开发",
    "integration-test": "全量集成测试",
    "test-first": "验收测试先行",
    "development": "功能开发",
    "verify": "非功能验证",
    "review": "Code Review",
    "deploy": "部署",
    "retro": "复盘",
    "topic-intake": "学习主题确认",
    "material-prepare": "AI 准备资料",
    "study": "用户学习与答疑",
    "practice": "实践任务",
    "record": "学习记录",
    "done": "全部完成",
}

SKILL_ACTIONS = {
    "template-generator": "创建 Epic 和首个子 plan",
    "event-storming-assistant": "补需求分析 plan",
    "spec-by-example-assistant": "补实例化需求与验收标准",
    "requirement-analyst": "闭环需求 P0",
    "backlog-prioritization-assistant": "按价值/紧迫度/依赖排序并确认 Backlog",
    "architecture-design-assistant": "补技术方案并评审采纳",
    "test-generator": "执行全量集成测试并写回归报告",
    "task-splitter": "拆纵向 Story、估故事点并确认 Scope",
    "feature-dev-assistant": "继续当前 Story 的 Red→Green→Refactor",
    "figma-ui": "继续 Figma/UI 子任务",
    "nfr-assistant": "补非功能验证",
    "review-assistant": "补 Review 结论",
    "deployment-assistant": "补部署检查和冒烟计划",
    "retro-assistant": "补团队回顾",
    "material-prep-assistant": "准备资料或沉淀记录",
}


def run_gate(args: argparse.Namespace) -> dict[str, Any]:
    cmd = ["bash", "scripts/workflow-gate.sh"]
    if args.workflow:
        cmd.extend(["--workflow", args.workflow])
    if args.epic:
        cmd.extend(["--epic", args.epic])
    if args.project:
        cmd.extend(["--project", args.project])
    cmd.extend(["--probe", "--json"])
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
    text = blocker.strip()
    if "无 Epic plan" in text:
        return "还没有 Epic，需要先创建项目总 plan"
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
    seen: set[str] = set()
    unique: list[str] = []
    for blocker in blockers:
        if blocker in seen:
            continue
        seen.add(blocker)
        unique.append(blocker)
    return unique


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


def _find_run_id(explicit_run: str | None, epic: str | None) -> str | None:
    """定位要回放的 run：显式 --run 优先；否则按 Epic stem 匹配最新 run 文件名。"""
    if explicit_run:
        stem = Path(explicit_run).name
        for suffix in (".run.yaml", ""):
            if stem.endswith(suffix) and suffix:
                stem = stem[: -len(suffix)]
        return stem
    if not epic or not RUN_DIR.is_dir():
        return None
    epic_stem = Path(epic).stem
    candidates = sorted(
        (f for f in RUN_DIR.glob("*.run.yaml") if epic_stem in f.name),
        key=lambda f: f.name,
    )
    if not candidates:
        return None
    return candidates[-1].name[: -len(".run.yaml")]


def replay_events(run_id: str | None) -> dict[str, Any] | None:
    """回放某 run 的事件流，提取门禁历史信号（会话层）：最近一次门禁 pass/fail + 原因，
    以及当前阶段连续 fail 次数（供『同一阶段反复判不过』告警）。事件流缺失返回 None。"""
    if not run_id:
        return None
    event_file = EVENT_DIR / f"{run_id}.events.jsonl"
    if not event_file.is_file():
        return None
    gate_events: list[dict[str, Any]] = []
    for line in event_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") in ("gate_pass", "gate_fail"):
            gate_events.append(ev)
    if not gate_events:
        return {"run_id": run_id, "last_gate": None, "consecutive_fails": 0}
    last = gate_events[-1]
    last_stage = last.get("stage")
    consecutive_fails = 0
    for ev in reversed(gate_events):
        if ev.get("stage") != last_stage:
            break
        if ev.get("type") == "gate_fail":
            consecutive_fails += 1
        else:
            break
    return {
        "run_id": run_id,
        "last_gate": {
            "result": "pass" if last.get("type") == "gate_pass" else "fail",
            "stage": last_stage,
            "at": last.get("created_at"),
            "reason": last.get("reason", ""),
        },
        "consecutive_fails": consecutive_fails,
    }


def summarize(gate: dict[str, Any], replay: dict[str, Any] | None = None) -> dict[str, Any]:
    blockers = merge_blockers([simplify_blocker(item) for item in gate.get("blockers", []) or []])
    summary = {
        "workflow": gate.get("workflow"),
        "current": label_state(gate.get("current_state", "")),
        "current_state": gate.get("current_state"),
        "blocked": bool(blockers),
        "blockers": blockers,
        "next": next_step(gate),
        "recommended_skill": gate.get("recommended_skill"),
        "resume": resume_hint(gate),
        "details": {
            "epic": gate.get("epic"),
            "raw_state": gate.get("current_state"),
            "raw_next": gate.get("next_state"),
        },
    }
    if replay:
        summary["history"] = replay
    return summary


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
    hist = summary.get("history")
    if hist and hist.get("last_gate"):
        lg = hist["last_gate"]
        day = (lg.get("at") or "")[:10]
        if lg["result"] == "pass":
            print(f"最近门禁：{day} 通过（{label_state(lg.get('stage',''))}）")
        else:
            reason = (lg.get("reason") or "").split(";")[0].strip()
            print(f"最近门禁：{day} 未过（{label_state(lg.get('stage',''))}）— {reason}")
        if hist.get("consecutive_fails", 0) >= 2:
            print(f"⚠️ 告警：当前阶段门禁已连续 {hist['consecutive_fails']} 次判不过，建议排查根因或调整方案")


def main() -> int:
    parser = argparse.ArgumentParser(description="Human-friendly workflow status wrapper.")
    parser.add_argument("--workflow", help="Workflow name, e.g. client-dev or computer-mgmt")
    parser.add_argument("--epic", help="Epic plan path")
    parser.add_argument("--project", help="Project name for workflow-gate lookup")
    parser.add_argument("--run", help="Run id or run file path for event-stream replay (会话层历史)")
    parser.add_argument("--json", action="store_true", help="Output simplified JSON")
    args = parser.parse_args()

    try:
        gate = run_gate(args)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"BLOCKED:workflow-status:{exc}", file=sys.stderr)
        return 1
    replay = replay_events(_find_run_id(args.run, args.epic))
    summary = summarize(gate, replay)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
