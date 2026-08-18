#!/usr/bin/env python3
"""Local Epic kanban server — 127.0.0.1:7777 only. Stdlib only."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
KANBAN_DIR = ROOT / "scripts" / "kanban"
HOST = "127.0.0.1"
PORT = 7777

sys.path.insert(0, str(ROOT / "scripts"))
try:
    from gate_parse import wbs_slice_status as _wbs_slice_status  # 子 Plan = 事实源
    from gate_parse import parse_ac_table as _parse_ac_table
    from gate_parse import parse_dev_ac_coverage as _parse_dev_ac_coverage
    from gate_parse import parse_test_map as _parse_test_map
except Exception:  # pragma: no cover - gate_parse 不可用时降级读 Epic 字面量
    _wbs_slice_status = None
    _parse_ac_table = None
    _parse_dev_ac_coverage = None
    _parse_test_map = None

RUN_DIR = ROOT / ".workflows" / "runs"
EVENT_DIR = ROOT / ".workflows" / "events"


def _event_file_for(epic_rel: str) -> Path | None:
    """定位该 Epic 的事件流文件。两条路径，任一命中即用：
    1. 显式 run（workflow-run.py start 建的）：.workflows/runs/*.run.yaml → <run_id>.events.jsonl
    2. 审计旁路（workflow-gate.sh 被动落盘，无需 run）：.workflows/events/<epic-stem>.events.jsonl
    路径 2 对应 auditd 哲学——事件是门禁执行的副作用，不依赖有状态的 run。"""
    epic_stem = Path(epic_rel).stem
    if RUN_DIR.is_dir():
        runs = sorted((f for f in RUN_DIR.glob("*.run.yaml") if epic_stem in f.name), key=lambda f: f.name)
        if runs:
            run_id = runs[-1].name[: -len(".run.yaml")]
            candidate = EVENT_DIR / f"{run_id}.events.jsonl"
            if candidate.is_file():
                return candidate
    direct = EVENT_DIR / f"{epic_stem}.events.jsonl"
    return direct if direct.is_file() else None


_PENDING_EVENT_REASON_MARKERS = (
    "skillRunStage:",
    "implementationDesignReady:",
    "storyTddComplete:",
    "storyScopeReady:",
    "testPlanApproved:",
    "integrationReportPass:",
    "子 Plan 未创建",
    "子 Plan 不存在",
)


def _gate_event_result(event: dict[str, Any]) -> str:
    explicit = str(event.get("display_state") or "").strip()
    if explicit in {"pass", "pending", "fail"}:
        return explicit
    if event.get("type") == "gate_pass":
        return "pass"
    reason = str(event.get("reason") or "")
    if any(marker in reason for marker in _PENDING_EVENT_REASON_MARKERS):
        return "pending"
    return "fail"


def gate_history_for(epic_rel: str) -> dict[str, Any] | None:
    """回放该 Epic 的门禁事件流，供看板卡片展示时间账本摘要。
    返回 {last_gate: {result, stage, at, reason}, consecutive_fails}；无事件流返回 None。"""
    event_file = _event_file_for(epic_rel)
    if event_file is None:
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
        return None
    last = gate_events[-1]
    last_stage = last.get("stage")
    consecutive_fails = 0
    for ev in reversed(gate_events):
        if ev.get("stage") != last_stage or _gate_event_result(ev) != "fail":
            break
        consecutive_fails += 1
    # recent：详情页使用的完整事件流（时间倒序）。
    # 纵览页由前端自行 slice；这里不截断审计记录、不截断 reason。
    recent = [
        {
            "result": _gate_event_result(e),
            "event_id": e.get("event_id"),
            "evaluation_id": e.get("evaluation_id"),
            "event_version": e.get("event_version"),
            "stage": e.get("stage"),
            "workflow": e.get("workflow"),
            "project": e.get("project"),
            "epic": e.get("epic"),
            "at": (e.get("created_at") or "")[:19].replace("T", " "),
            "reason": str(e.get("reason") or "").strip(),
            "git_commit": (e.get("git_commit") or "")[:7],
            "inferred": bool(e.get("inferred")),
            "passed_stages": e.get("passed_stages") or [],
            "child_plan": e.get("child_plan"),
            "child_plan_exists": _workspace_file_exists(e.get("child_plan")),
            "plan_snapshot": e.get("plan_snapshot"),
            "story_id": e.get("story_id"),
            "scope_story_ids": e.get("scope_story_ids") or [],
            "scope_snapshot": e.get("scope_snapshot"),
            "legacy": not bool(e.get("event_id")),
        }
        for e in reversed(gate_events)
    ]
    passes = sum(1 for e in gate_events if _gate_event_result(e) == "pass")
    failures = sum(1 for e in gate_events if _gate_event_result(e) == "fail")
    pending = sum(1 for e in gate_events if _gate_event_result(e) == "pending")
    return {
        "last_gate": {
            "result": _gate_event_result(last),
            "event_id": last.get("event_id"),
            "evaluation_id": last.get("evaluation_id"),
            "stage": last_stage,
            "workflow": last.get("workflow"),
            "project": last.get("project"),
            "epic": last.get("epic"),
            "at": (last.get("created_at") or "")[:10],
            "reason": str(last.get("reason") or "").strip(),
            "child_plan": last.get("child_plan"),
            "child_plan_exists": _workspace_file_exists(last.get("child_plan")),
            "plan_snapshot": last.get("plan_snapshot"),
            "story_id": last.get("story_id"),
            "scope_story_ids": last.get("scope_story_ids") or [],
            "scope_snapshot": last.get("scope_snapshot"),
            "legacy": not bool(last.get("event_id")),
        },
        "consecutive_fails": consecutive_fails,
        "recent": recent,
        "total": len(gate_events),
        "decisions": passes + failures,
        "passes": passes,
        "failures": failures,
        "pending": pending,
    }


def _gate_matches_current_plan(event: dict[str, Any] | None, plan_rel: str | None) -> bool:
    """Only project a gate result while it still proves the current plan bytes.

    Gate events are an audit trail, not mutable state.  An event without a plan
    snapshot cannot prove that a later edit still satisfies the gate, so it is
    intentionally excluded from the current-state projection.
    """
    if not event or not plan_rel:
        return False
    child_plan = str(event.get("child_plan") or "").strip()
    if child_plan and child_plan != str(plan_rel).strip():
        return False
    expected = str(event.get("plan_snapshot") or "").strip()
    if not expected:
        return False
    try:
        plan = resolve_plan(str(plan_rel))
        actual = hashlib.sha256(plan.read_bytes()).hexdigest()
    except (OSError, ValueError):
        return False
    return actual == expected


_ACTIVE_PLAN_STATUSES = {"草稿", "进行中", "评审中", "待开发", "待确认", "draft", "in_progress", "review"}
_EXPECTED_PROGRESS_MARKERS = {
    "requirement": ("status 须为",),
    "prioritization": ("status 须为", "backlogPrioritized:"),
    "architecture": ("status 须为",),
    "story-split": ("status 须为", "storyScopeReady:", "skillRunStage:"),
    "implementation-design": ("implementationDesignReady:", "skillRunStage:"),
    "story-development": ("storyTddComplete:", "skillRunStage:"),
    "integration-test-plan": ("testPlanApproved:", "skillRunStage:"),
    "integration-test": ("integrationReportPass:", "skillRunStage:"),
}


def _gate_failure_is_expected_progress(stage: str, plan_status: str, reason: str) -> bool:
    """Treat an unmet exit criterion as progress while its Plan is explicitly active.

    The gate still prevents stage advancement.  This only separates normal
    work-in-progress from a contradiction where a Plan claims completion but
    its exit gate fails.
    """
    if str(plan_status).strip() not in _ACTIVE_PLAN_STATUSES:
        return False
    return any(marker in str(reason) for marker in _EXPECTED_PROGRESS_MARKERS.get(stage, ()))


def _display_gate_history(
    history: dict[str, Any] | None,
    current_gate: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Project current expected gate failures as pending without rewriting audit events."""
    if not history or not current_gate or current_gate.get("result") != "pending":
        return history
    projected = json.loads(json.dumps(history, ensure_ascii=False))
    stage = current_gate.get("stage")
    snapshot = current_gate.get("plan_snapshot")
    for event in projected.get("recent", []):
        if (
            event.get("stage") == stage
            and event.get("result") == "fail"
            and event.get("plan_snapshot") == snapshot
        ):
            event["result"] = "pending"
    last = projected.get("last_gate") or {}
    if (
        last.get("stage") == stage
        and last.get("result") == "fail"
        and last.get("plan_snapshot") == snapshot
    ):
        last["result"] = "pending"
    projected["consecutive_fails"] = 0
    return projected


def _event_file_for_write(epic_rel: str) -> Path:
    """Write workflow-adjacent events to the active stream when one exists.

    Gate events remain the only inputs to gate history/pass rate. WBS events use
    the same append-only file as a process ledger, but are filtered separately.
    """
    event_file = _event_file_for(epic_rel)
    if event_file is not None:
        return event_file
    EVENT_DIR.mkdir(parents=True, exist_ok=True)
    return EVENT_DIR / f"{Path(epic_rel).stem}.events.jsonl"


def append_wbs_progress_event(
    epic_rel: str,
    workflow: str | None,
    slice_n: int,
    stage: str,
    state: str,
    previous_state: str,
    target: str,
    operator: str,
    label: str,
    optional: bool,
) -> None:
    event_file = _event_file_for_write(epic_rel)
    event = {
        "type": "wbs_progress",
        "workflow": workflow or None,
        "epic": epic_rel,
        "stage": stage,
        "slice": slice_n,
        "state": state,
        "previous_state": previous_state,
        "target_plan": target,
        "operator": operator,
        "label": label,
        "optional": optional,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    with event_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def progress_history_for(epic_rel: str) -> dict[str, Any] | None:
    event_file = _event_file_for(epic_rel)
    if event_file is None:
        return None
    progress_events: list[dict[str, Any]] = []
    for line in event_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "wbs_progress":
            progress_events.append(ev)
    if not progress_events:
        return None
    recent = [
        {
            "stage": e.get("stage"),
            "slice": e.get("slice"),
            "state": e.get("state"),
            "previous_state": e.get("previous_state"),
            "target_plan": e.get("target_plan"),
            "operator": e.get("operator"),
            "label": e.get("label"),
            "optional": bool(e.get("optional")),
            "at": (e.get("created_at") or "")[:19].replace("T", " "),
        }
        for e in reversed(progress_events)
    ][:12]
    return {"recent": recent, "total": len(progress_events)}


PLAN_STATUSES = {"草稿", "进行中", "评审中", "已采纳", "搁置", "done", "pending-change", "已归档"}
SLICE_RE = re.compile(r"^(\[[ xX~-]\])\s*(\d+)([a-zA-Z]?)\.?\s+(.+)$")
WBS_TABLE_ROW = re.compile(r"^\|\s*(\d+)\s*\|")


def clean_md_cell(s: str) -> str:
    return re.sub(r"[*`]+", "", s).strip()


def parse_wbs_table(path: Path) -> dict[int, dict[str, str]]:
    """Parse §三 WBS markdown table → detail by slice number."""
    text = path.read_text(encoding="utf-8")
    in_section = False
    details: dict[int, dict[str, str]] = {}
    for line in text.splitlines():
        if re.search(r"##\s*三、WBS", line):
            in_section = True
            continue
        if in_section and line.startswith("## ") and not re.search(r"WBS", line):
            break
        if not in_section or not line.startswith("|"):
            continue
        if "---" in line or re.match(r"^\|\s*#\s*\|", line) or "切片" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if not parts or not parts[0].isdigit():
            continue
        n = int(parts[0])
        if len(parts) >= 6:
            details[n] = {
                "title": clean_md_cell(parts[1]),
                "skill": clean_md_cell(parts[2]),
                "input": parts[3],
                "output": parts[4],
                "acceptance": parts[5],
            }
        elif len(parts) >= 5:
            details[n] = {
                "title": clean_md_cell(parts[1]),
                "skill": "",
                "input": parts[2],
                "output": parts[3],
                "acceptance": parts[4],
            }
    return details


# 看板卡片「白话一句」— 与 WBS 表 title 互补
SLICE_SUMMARY: dict[int, str] = {
    1: "把飞书 PRD、Figma、接口文档整理成可开发的需求文档",
    2: "定技术栈、模块划分、路由与 Repository 契约",
    3: "用 Figma 量每个页面的尺寸/圆角/色值，写度量表",
    4: "搭 domain 模型与目录骨架（不含 UI）",
    5: "Mock 假数据 + 日后换真 API 的 Repository",
    6: "按设计稿 1:1 画三个主页的布局（先像再动）",
    7: "页面接上假数据：Banner、灵感列表等能展示",
    8: "补交互：Tab、弹层、hover、播放器等业务态",
    9: "空数据、失败、未登录等边界页面",
    10: "接真实接口 + 和设计走查验收",
    11: "写自动化测试 plan 并跑通 CI",
    12: "Code Review，清 P0",
    13: "上线前检查清单",
    14: "发布后冒烟与监控",
    15: "沉淀通用资料、关闭 Epic",
}

def resolve_plan(rel: str) -> Path:
    p = Path(rel)
    if p.is_absolute():
        target = p.resolve()
    else:
        target = (ROOT / rel).resolve()
    if not str(target).startswith(str(ROOT.resolve())):
        raise ValueError("path outside vault")
    if "Plans" not in target.parts:
        raise ValueError("not a plan path")
    return target


def resolve_workspace_file(raw: str) -> Path:
    """Resolve an untrusted board file reference inside this workspace.

    ``Path.resolve`` closes symlink escapes; ``relative_to`` enforces a path
    boundary rather than the unsafe string-prefix check used by legacy Plan
    mutations.  Opening directories is intentionally unsupported.
    """
    value = str(raw or "").strip()
    if not value or "\x00" in value:
        raise ValueError("file path is empty or invalid")
    path = Path(value)
    target = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("file path is outside workspace") from exc
    if not target.exists():
        raise ValueError("file does not exist")
    if not target.is_file():
        raise ValueError("path is not a file")
    return target


def _workspace_file_exists(raw: Any) -> bool:
    try:
        resolve_workspace_file(str(raw or ""))
    except (OSError, ValueError):
        return False
    return True


def open_workspace_file(raw: str) -> dict[str, Any]:
    """Ask the operating system to open a validated workspace file."""
    target = resolve_workspace_file(raw)
    if sys.platform == "darwin":
        command = ["open", str(target)]
    elif sys.platform.startswith("win"):
        command = ["cmd", "/c", "start", "", str(target)]
    else:
        command = ["xdg-open", str(target)]
    try:
        subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        raise ValueError(f"system opener failed: {exc}") from exc
    return {"ok": True, "file": str(target.relative_to(ROOT.resolve()))}


def read_frontmatter(path: Path) -> tuple[dict[str, str], str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text, text
    fm_raw = text[3:end]
    body = text[end + 4 :]
    fm: dict[str, str] = {}
    for line in fm_raw.splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        key, val = line.split(":", 1)
        fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm, fm_raw, body


def write_frontmatter_field(path: Path, key: str, value: str) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("no frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("no frontmatter")
    fm_raw = text[3:end]
    body = text[end + 4 :]
    # strip 掉 frontmatter 前后空白，避免每次写入在 --- 后累积空行。
    lines = fm_raw.strip("\n").splitlines()
    pat = re.compile(rf"^{re.escape(key)}:")
    replaced = False
    out: list[str] = []
    for line in lines:
        if pat.match(line):
            out.append(f"{key}: {value}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(f"{key}: {value}")
    path.write_text("---\n" + "\n".join(out) + "\n---" + body, encoding="utf-8")


def parse_plans_block(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    plans: list[dict[str, Any]] = []
    stage_map = {
        "requirement": "需求分析",
        "prioritization": "需求排序",
        "architecture": "技术方案",
        "development": "功能开发",
        "integration_plan": "集成测试计划与审核",
        "integration": "全量集成测试",
        "test": "自动化测试",
        "deploy": "部署",
        "topic-intake": "学习主题确认",
        "material-prepare": "AI 准备资料",
        "study": "用户学习与答疑",
        "practice": "实践任务",
        "verify": "AI 验证",
        "retro": "学习复盘",
        "record": "学习记录",
    }
    in_plans = False
    for line in text.splitlines():
        if line.strip() == "plans:":
            in_plans = True
            continue
        if in_plans:
            if line and not line.startswith(" ") and not line.startswith("\t"):
                break
            m = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.+)$", line)
            if not m:
                continue
            stage_key, raw = m.group(1), m.group(2).strip()
            if raw in ("null", "~", ""):
                plans.append(
                    {
                        "stage_key": stage_key,
                        "stage": stage_map.get(stage_key, stage_key),
                        "path": None,
                        "status": None,
                        "lifecycle_state": stage_key if stage_key in stage_map else None,
                    }
                )
                continue
            rel = raw.split("#")[0].strip()
            sub = {"stage_key": stage_key, "stage": stage_map.get(stage_key, stage_key), "path": rel}
            try:
                sp = resolve_plan(rel)
                if sp.is_file():
                    sub["exists"] = True
                    fm, _, _ = read_frontmatter(sp)
                    sub["status"] = fm.get("status")
                    sub["lifecycle_state"] = fm.get("lifecycle_state", stage_key)
                else:
                    sub["exists"] = False
                    sub["status"] = None
            except ValueError:
                sub["exists"] = False
                sub["status"] = None
            plans.append(sub)
    return plans


def _clean_scalar(value: str | None, default: str = "") -> str:
    if not value:
        return default
    return str(value).split("#", 1)[0].strip().strip('"').strip("'") or default


def _load_workflow_blueprint(workflow: str | None) -> dict[str, Any]:
    name = _clean_scalar(workflow, "client-dev")
    if not re.match(r"^[A-Za-z0-9_-]+$", name):
        name = "client-dev"
    path = BLUEPRINT_DIR / f"{name}.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _slice_stage_map(workflow: str | None) -> dict[int, dict[str, str]]:
    """从工作流蓝图派生 WBS 切片归属。

    返回 n -> {stage_key, plan_stage_key, optional}：
    - stage_key：蓝图 stage key，用于看板显示当前阶段。
    - plan_stage_key：Epic plans.* 的 key，用于定位对应子 plan。
    """
    blueprint = _load_workflow_blueprint(workflow)
    epic_mapping = blueprint.get("epicMapping") or {}
    out: dict[int, dict[str, str]] = {}
    for stage in blueprint.get("stages", []) or []:
        stage_key = str(stage.get("key") or "")
        plan_stage_key = str(stage.get("epicField") or epic_mapping.get(stage_key) or stage_key)
        optional = set()
        for n in stage.get("optionalWbsSlices", []) or []:
            try:
                optional.add(int(n))
            except (TypeError, ValueError):
                continue
        for n in stage.get("wbsSlices", []) or []:
            try:
                slice_n = int(n)
            except (TypeError, ValueError):
                continue
            out[slice_n] = {
                "stage_key": stage_key,
                "plan_stage_key": plan_stage_key,
                "optional": slice_n in optional,
            }
    return out


def parse_wbs_slices(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    in_fence = False
    fence_char = ""
    fence_len = 0
    raw: list[dict[str, Any]] = []
    for line in text.splitlines():
        fence = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if fence:
            marker, suffix = fence.group(1), fence.group(2)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_len = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len and not suffix.strip():
                in_fence = False
                fence_char = ""
                fence_len = 0
            continue
        if not in_fence:
            continue
        m = SLICE_RE.match(line)
        if not m:
            continue
        mark, num, suffix, label = m.group(1).lower(), int(m.group(2)), m.group(3), m.group(4).strip()
        raw.append({"n": num, "suffix": suffix, "mark": mark, "label": label, "line": line})
    grouped: dict[int, list[dict[str, Any]]] = {}
    for r in raw:
        grouped.setdefault(r["n"], []).append(r)
    slices: list[dict[str, Any]] = []
    for n in sorted(grouped):
        items = grouped[n]
        marks = [it["mark"] for it in items]
        done = all(m in {"[x]", "[-]"} for m in marks)
        skipped = all(m == "[-]" for m in marks)
        if len(items) == 1:
            label = items[0]["label"]
        else:
            label = " · ".join(
                (f"{it['suffix']}: {it['label']}" if it['suffix'] else it['label'])
                for it in items
            )
        slices.append({"n": n, "done": done, "skipped": skipped, "label": label, "line": items[0]["line"]})
    return slices


def _slice_status_in(child: str | None, n: int) -> str | None:
    """在单个子 Plan 里查切片 n 的状态；查不到 / 不可用返回 None。"""
    if _wbs_slice_status is None or not child:
        return None
    cp = ROOT / child if not Path(child).is_absolute() else Path(child)
    if not cp.is_file():
        return None
    try:
        return _wbs_slice_status(cp, n)
    except Exception:
        return None


def _derive_slice_state(
    epic_literal_done: bool, epic_literal_skipped: bool, preferred_child: str | None, n: int
) -> tuple[bool, bool, str]:
    """切片完成态派生策略（防撒谎优先）：
    蓝图已声明切片 n 属于某 stage 时，优先到该 stage 对应子 Plan 查同号 WBS；
    查不到 / 子 Plan 不存在 / gate_parse 不可用时，回退 Epic 字面量。
    返回 (done, skipped, derived_from)，derived_from ∈ {"child-plan", "epic-literal"}。"""
    status = _slice_status_in(preferred_child, n)
    if status is not None:
        return status in {"x", "-"}, status == "-", "child-plan"
    return epic_literal_done, epic_literal_skipped, "epic-literal"


def _parse_plan_fact(rel: str | None, parser) -> Any:
    if parser is None or not rel:
        return {}
    try:
        path = resolve_plan(rel)
    except ValueError:
        return {}
    if not path.is_file():
        return {}
    try:
        return parser(path)
    except Exception:
        return {}


def _load_story_cards(dev_rel: str | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """读 client-dev 动态 Story index，并从每个故事子 Plan/TDD 证据派生状态。

    JSON 是故事范围/点数的真理源；子 Plan 是开发完成的真理源。
    看板只读投影，不在 Epic 中复制状态。
    """
    if not dev_rel:
        return [], {}
    try:
        dev = resolve_plan(dev_rel)
    except ValueError:
        return [], {"error": "development plan 路径非法"}
    if not dev.is_file():
        return [], {}
    dev_fm, _, _ = read_frontmatter(dev)
    index_raw = _clean_scalar(dev_fm.get("story_index"))
    if not index_raw:
        return [], {}
    try:
        index_path = resolve_plan(index_raw)
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        return [], {"error": f"Story index 不可用: {exc}"}

    cards: list[dict[str, Any]] = []
    done_statuses = {"已完成", "done", "completed"}
    for raw in payload.get("stories", []) if isinstance(payload, dict) else []:
        if not isinstance(raw, dict):
            continue
        path_raw = str(raw.get("path") or "").strip()
        child_status = ""
        tdd_complete = False
        implementation_design_ready = False
        path_exists = False
        implementation_design_path = ""
        implementation_design_exists = False
        tdd_evidence_path = ""
        tdd_evidence_exists = False
        if path_raw:
            try:
                child = resolve_plan(path_raw)
                if child.is_file():
                    path_exists = True
                    child_fm, _, _ = read_frontmatter(child)
                    child_status = _clean_scalar(child_fm.get("status"))
                    impl_raw = _clean_scalar(child_fm.get("implementation_design"))
                    implementation_design_path = impl_raw
                    if impl_raw:
                        impl_path = resolve_plan(impl_raw)
                        implementation_design_exists = impl_path.is_file()
                        impl = json.loads(impl_path.read_text(encoding="utf-8"))
                        implementation_design_ready = impl.get("confirmed") is True and not impl.get("blocked_questions")
                    evidence_raw = _clean_scalar(child_fm.get("tdd_evidence"))
                    tdd_evidence_path = evidence_raw
                    if evidence_raw:
                        evidence_path = resolve_plan(evidence_raw)
                        tdd_evidence_exists = evidence_path.is_file()
                        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                        phases = ["green", "refactor", "integration_smoke"]
                        tdd_complete = (
                            child_status in done_statuses
                            and evidence.get("red", {}).get("exit_code") not in (None, 0)
                            and all(evidence.get(k, {}).get("exit_code") == 0 for k in phases)
                            and bool(evidence.get("commit"))
                        )
            except (ValueError, OSError, json.JSONDecodeError):
                pass
        if tdd_complete:
            state = "done"
        elif child_status in {"进行中", "评审中", "in_progress"}:
            state = "running"
        else:
            state = "todo"
        cards.append(
            {
                "id": str(raw.get("id") or ""),
                "title": str(raw.get("title") or ""),
                "story_points": raw.get("story_points"),
                "priority": str(raw.get("priority") or ""),
                "sprint_scope": raw.get("sprint_scope") is True,
                "dependencies": raw.get("dependencies") if isinstance(raw.get("dependencies"), list) else [],
                "path": path_raw,
                "path_exists": path_exists,
                "status": child_status,
                "implementation_design_path": implementation_design_path,
                "implementation_design_exists": implementation_design_exists,
                "implementation_design_ready": implementation_design_ready,
                "tdd_evidence_path": tdd_evidence_path,
                "tdd_evidence_exists": tdd_evidence_exists,
                "tdd_complete": tdd_complete,
                "state": state,
            }
        )
    meta = {
        "index": str(index_path.relative_to(ROOT)) if index_path.is_relative_to(ROOT) else str(index_path),
        "scope_confirmed": payload.get("scope_confirmed") is True,
        "epic_scope": payload.get("epic_scope") if isinstance(payload.get("epic_scope"), list) else [],
        "current_implementation_scope": (
            payload.get("current_implementation_scope")
            if isinstance(payload.get("current_implementation_scope"), list)
            else []
        ),
    }
    return cards, meta


def _delivery_story_cards(stories: list[dict[str, Any]], story_meta: dict[str, Any]) -> list[dict[str, Any]]:
    """Whole Epic exit scope; legacy indexes fall back to rotating sprint scope."""
    epic_scope = [str(item) for item in story_meta.get("epic_scope", []) if str(item).strip()]
    if epic_scope:
        by_id = {str(story.get("id") or ""): story for story in stories}
        return [by_id[story_id] for story_id in epic_scope if story_id in by_id]
    return [story for story in stories if story.get("sprint_scope")]


def _integration_pass(plan_by_stage: dict[str, str]) -> bool:
    rel = plan_by_stage.get("integration")
    if not rel:
        return False
    try:
        plan = resolve_plan(rel)
        fm, _, _ = read_frontmatter(plan)
        report = resolve_plan(_clean_scalar(fm.get("integration_report")))
        data = json.loads(report.read_text(encoding="utf-8"))
    except (ValueError, OSError, json.JSONDecodeError):
        return False
    suites = data.get("suites")
    return (
        bool(_clean_scalar(fm.get("target_commit")))
        and data.get("commit") == _clean_scalar(fm.get("target_commit"))
        and data.get("all_scope_stories_completed") is True
        and isinstance(suites, list)
        and bool(suites)
        and all(isinstance(s, dict) and s.get("exit_code") == 0 for s in suites)
    )


def _test_plan_facts(plan_by_stage: dict[str, str]) -> dict[str, Any]:
    rel = plan_by_stage.get("integration_plan")
    facts: dict[str, Any] = {
        "path": rel,
        "approved": False,
        "case_count": 0,
        "reviewer": "",
        "reviewed_at": "",
    }
    if not rel:
        return facts
    try:
        plan = resolve_plan(rel)
        fm, _, _ = read_frontmatter(plan)
        case_index = resolve_plan(_clean_scalar(fm.get("test_case_index")))
        review_path = resolve_plan(_clean_scalar(fm.get("test_review")))
        cases = json.loads(case_index.read_text(encoding="utf-8"))
        review = json.loads(review_path.read_text(encoding="utf-8"))
        case_sha = hashlib.sha256(case_index.read_bytes()).hexdigest()
    except (ValueError, OSError, json.JSONDecodeError):
        return facts
    case_items = cases.get("cases") if isinstance(cases, dict) else None
    facts.update(
        {
            "approved": (
                _clean_scalar(fm.get("status")) == "已采纳"
                and bool(_clean_scalar(fm.get("target_commit")))
                and review.get("approved") is True
                and review.get("target_commit") == _clean_scalar(fm.get("target_commit"))
                and review.get("case_index_sha256") == case_sha
                and review.get("unresolved_comments") == 0
            ),
            "case_count": len(case_items) if isinstance(case_items, list) else 0,
            "reviewer": str(review.get("reviewer") or ""),
            "reviewed_at": str(review.get("reviewed_at") or ""),
        }
    )
    return facts


def _test_health(plan_by_stage: dict[str, str], plans: list[dict[str, Any]]) -> dict[str, Any]:
    if "integration" in plan_by_stage or "prioritization" in plan_by_stage:
        stories, story_meta = _load_story_cards(plan_by_stage.get("development"))
        scoped = _delivery_story_cards(stories, story_meta)
        done = [s for s in scoped if s.get("tdd_complete")]
        integration_ok = _integration_pass(plan_by_stage)
        test_plan = _test_plan_facts(plan_by_stage)
        pending = []
        if not scoped:
            pending.append("未确认迭代 Scope")
        if scoped and len(done) < len(scoped):
            pending.append(f"Scope Story TDD {len(done)}/{len(scoped)}")
        if scoped and len(done) == len(scoped) and not integration_ok:
            pending.append("集成测试计划待审核" if not test_plan["approved"] else "全量集成测试待完成")
        return {
            # 未完成是 client-dev 的正常进度；真实风险由当前门禁 fail/P0 投影。
            "health": "green" if integration_ok else "blue",
            "requirement_plan": plan_by_stage.get("requirement"),
            "test_plan": plan_by_stage.get("integration"),
            "planning_plan": plan_by_stage.get("integration_plan"),
            "development_plan": plan_by_stage.get("development"),
            "story_total": len(scoped),
            "story_done": len(done),
            "story_points_total": sum(int(s.get("story_points") or 0) for s in scoped),
            "story_points_done": sum(int(s.get("story_points") or 0) for s in done),
            "integration_pass": integration_ok,
            "test_plan_approved": test_plan["approved"],
            "test_case_count": test_plan["case_count"],
            "test_reviewer": test_plan["reviewer"],
            "test_reviewed_at": test_plan["reviewed_at"],
            "coverage_pct": round(len(done) / len(scoped) * 100) if scoped else None,
            "ac_total": len(scoped),
            "ac_covered": len(done),
            "pending": pending,
            "blockers": [],
        }
    req_rel = plan_by_stage.get("requirement")
    test_rel = plan_by_stage.get("test")
    dev_rel = plan_by_stage.get("development")
    acs = _parse_plan_fact(req_rel, _parse_ac_table)
    tests = _parse_plan_fact(test_rel, _parse_test_map)
    dev_cov = _parse_plan_fact(dev_rel, _parse_dev_ac_coverage)
    p0_ids = sorted(ac for ac, meta in acs.items() if str(meta.get("priority", "")).upper() == "P0")
    total_ac = len(acs)
    covered_ac = sum(1 for ac in acs if tests.get(ac))
    p0_covered = sum(1 for ac in p0_ids if tests.get(ac))
    p0_dev_covered = sum(1 for ac in p0_ids if dev_cov.get(ac))
    case_count = sum(len(items) for items in tests.values())
    missing_p0_tests = [ac for ac in p0_ids if not tests.get(ac)]
    missing_p0_dev = [ac for ac in p0_ids if not dev_cov.get(ac)]
    blockers: list[str] = []
    if req_rel and not total_ac:
        blockers.append("需求 AC 未解析到")
    if total_ac and not test_rel:
        blockers.append("测试 plan 未创建")
    if missing_p0_tests:
        blockers.append("P0 AC 缺测试覆盖: " + "、".join(missing_p0_tests[:6]))
    if missing_p0_dev:
        blockers.append("P0 AC 缺开发任务覆盖: " + "、".join(missing_p0_dev[:6]))
    if total_ac and covered_ac < total_ac:
        blockers.append(f"AC 测试覆盖 {covered_ac}/{total_ac}")

    test_plan = next((p for p in plans if p.get("stage_key") == "test"), {})
    wbs4_status = _slice_status_in(test_rel, 4)
    coverage_pct = round(covered_ac / total_ac * 100) if total_ac else None
    p0_coverage_pct = round(p0_covered / len(p0_ids) * 100) if p0_ids else None
    if not req_rel:
        health = "none"
    elif not total_ac or not test_rel or missing_p0_tests:
        health = "red"
    elif missing_p0_dev or (total_ac and covered_ac < total_ac):
        health = "amber"
    else:
        health = "green"
    return {
        "health": health,
        "requirement_plan": req_rel,
        "test_plan": test_rel,
        "development_plan": dev_rel,
        "test_status": test_plan.get("status"),
        "wbs4_done": wbs4_status in {"x", "-"} if wbs4_status is not None else None,
        "ac_total": total_ac,
        "ac_covered": covered_ac,
        "coverage_pct": coverage_pct,
        "p0_total": len(p0_ids),
        "p0_covered": p0_covered,
        "p0_coverage_pct": p0_coverage_pct,
        "p0_dev_covered": p0_dev_covered,
        "case_count": case_count,
        "missing_p0_tests": missing_p0_tests,
        "missing_p0_dev": missing_p0_dev,
        "blockers": blockers,
    }


def _build_workflow_map(
    workflow: str | None,
    current_stage: str,
    plans: list[dict[str, Any]],
    stories: list[dict[str, Any]],
    story_meta: dict[str, Any],
    test_health: dict[str, Any],
    gate_history: dict[str, Any] | None,
) -> dict[str, Any]:
    """Project blueprint stages and file facts into one navigable process map."""
    blueprint = _load_workflow_blueprint(workflow)
    stage_defs = blueprint.get("stages") or []
    plan_by_key = {p.get("stage_key"): p for p in plans}
    latest_gate_by_stage: dict[str, dict[str, Any]] = {}
    for event in (gate_history or {}).get("recent", []):
        key = str(event.get("stage") or "")
        if key and key not in latest_gate_by_stage:
            latest_gate_by_stage[key] = event

    stage_keys = [str(stage.get("key") or "") for stage in stage_defs]
    current_index = len(stage_defs) if current_stage == "done" else (
        stage_keys.index(current_stage) if current_stage in stage_keys else 0
    )
    scoped = [story for story in stories if story.get("sprint_scope")]
    delivery_stories = _delivery_story_cards(stories, story_meta)
    implementation_ready = [story for story in scoped if story.get("implementation_design_ready")]
    epic_implementation_ready = [story for story in delivery_stories if story.get("implementation_design_ready")]
    scoped_tdd_done = [story for story in scoped if story.get("tdd_complete")]
    tdd_done = [story for story in delivery_stories if story.get("tdd_complete")]
    points_total = sum(int(story.get("story_points") or 0) for story in scoped)
    delivery_points_total = sum(int(story.get("story_points") or 0) for story in delivery_stories)
    points_done = sum(int(story.get("story_points") or 0) for story in tdd_done)
    epic_mapping = blueprint.get("epicMapping") or {}
    stages: list[dict[str, Any]] = []

    for index, stage in enumerate(stage_defs):
        key = str(stage.get("key") or "")
        plan_key = str(stage.get("epicField") or epic_mapping.get(key) or key)
        plan = plan_by_key.get(plan_key) or {}
        plan_path = plan.get("path")
        plan_exists = False
        if plan_path:
            try:
                plan_exists = resolve_plan(str(plan_path)).is_file()
            except ValueError:
                plan_exists = False
        raw_gate = latest_gate_by_stage.get(key)
        gate = raw_gate if _gate_matches_current_plan(raw_gate, str(plan_path or "")) else None
        if gate and key in {"implementation-design", "story-development"} and gate.get("story_id"):
            current_story_ids = {str(story.get("id") or "") for story in scoped}
            if str(gate.get("story_id")) not in current_story_ids:
                gate = None
        if gate and gate.get("result") == "fail" and _gate_failure_is_expected_progress(
            key,
            str(plan.get("status") or ""),
            str(gate.get("reason") or ""),
        ):
            gate = {**gate, "result": "pending"}
        # A stage that is still current has not exited.  A historical pass for
        # the same stage therefore belongs to an older scope/plan revision.
        if index == current_index and gate and gate.get("result") == "pass":
            gate = None

        if current_stage == "done" or index < current_index:
            state = "completed"
        elif index > current_index:
            state = "upcoming"
        else:
            is_blocked = not plan_exists or bool(gate and gate.get("result") == "fail")
            state = "blocked" if is_blocked else "active"

        summary = str(plan.get("status") or ("子 Plan 未创建" if not plan_exists else "待推进"))
        if key == "story-split":
            scope_label = "Scope 已确认" if story_meta.get("scope_confirmed") else "Scope 未确认"
            summary = f"{len(scoped)} Story · {points_total} 点 · {scope_label}"
        elif key == "implementation-design":
            summary = (
                f"当前 Scope {len(implementation_ready)}/{len(scoped)} · "
                f"Epic 累计 {len(epic_implementation_ready)}/{len(delivery_stories)} Story"
            )
        elif key == "story-development":
            summary = f"TDD {len(tdd_done)}/{len(delivery_stories)} Story · {points_done}/{delivery_points_total} 点"
        elif key == "integration-test-plan":
            summary = (
                f"测试审核已通过 · {test_health.get('test_case_count') or 0} 用例"
                if test_health.get("test_plan_approved")
                else f"待测试审核 · {test_health.get('test_case_count') or 0} 用例"
            )
        elif key == "integration-test":
            summary = "全量集成已通过" if test_health.get("integration_pass") else "全量集成待完成"
        if state == "upcoming" and not plan_exists:
            summary = "尚未到创建阶段"

        blocker = ""
        progress_note = ""
        if index == current_index and current_stage != "done":
            if gate and gate.get("result") == "fail":
                blocker = str(gate.get("reason") or "门禁未通过")
            elif not plan_exists:
                blocker = f"{stage.get('label') or key}：子 Plan 不存在"
            elif key == "integration-test-plan" and not test_health.get("test_plan_approved"):
                progress_note = "集成测试计划正在准备或等待审核"
            elif key == "integration-test" and not test_health.get("integration_pass"):
                progress_note = "全量集成测试正在准备或执行"
            elif key == "story-split" and not story_meta.get("scope_confirmed"):
                progress_note = "Story Scope 正在拆分或等待确认"
            elif key == "implementation-design" and len(implementation_ready) < len(scoped):
                progress_note = f"还有 {len(scoped) - len(implementation_ready)} 个 Story 待完成实现落点"
            elif key == "story-development" and len(scoped_tdd_done) < len(scoped):
                progress_note = f"当前 Scope 还有 {len(scoped) - len(scoped_tdd_done)} 个 Story 正在完成 TDD"
            elif key == "story-development" and len(tdd_done) < len(delivery_stories):
                progress_note = f"当前 Story 已完成，Epic 还有 {len(delivery_stories) - len(tdd_done)} 个 Story 待激活或完成"

        stages.append(
            {
                "key": key,
                "label": stage.get("label") or key,
                "index": index + 1,
                "state": state,
                "summary": summary,
                "blocker": blocker,
                "progress_note": progress_note,
                "skills": stage.get("skills") or [],
                "template": stage.get("template") or "",
                "template_exists": _workspace_file_exists(stage.get("template")),
                "required_outputs": stage.get("requiredSections") or [],
                "exit_criteria": [name for name, required in (stage.get("exitCriteria") or {}).items() if required],
                "plan": {
                    "key": plan_key,
                    "path": plan_path,
                    "exists": plan_exists,
                    "status": plan.get("status"),
                    "lifecycle_state": plan.get("lifecycle_state"),
                },
                # 未来阶段可能残留旧蓝图/旧文件结构下的失败事件；保留审计历史，
                # 但在阶段真正成为 current 前不把旧事件投影成当前门禁结论。
                "gate": gate if index <= current_index else None,
            }
        )

    completed = sum(1 for stage in stages if stage["state"] == "completed")
    return {
        "name": blueprint.get("name") or _clean_scalar(workflow, "client-dev"),
        "label": blueprint.get("label") or _clean_scalar(workflow, "client-dev"),
        "version": blueprint.get("version") or "",
        "description": blueprint.get("description") or "",
        "current_stage": current_stage,
        "completed_stages": completed,
        "total_stages": len(stages),
        "progress_pct": round(completed / len(stages) * 100) if stages else 0,
        "stages": stages,
    }


def scan_epic(path: Path) -> dict[str, Any]:
    fm, _, _ = read_frontmatter(path)
    rel = str(path.relative_to(ROOT))
    workflow = fm.get("workflow")
    effective_workflow = _clean_scalar(workflow, "client-dev")
    is_client_dev = effective_workflow == "client-dev"
    slices = parse_wbs_slices(path)
    wbs_table = parse_wbs_table(path)
    plans = parse_plans_block(path)
    plan_by_stage = {p["stage_key"]: p.get("path") for p in plans if p.get("path")}
    test_health = _test_health(plan_by_stage, plans)
    stories, story_meta = _load_story_cards(plan_by_stage.get("development")) if is_client_dev else ([], {})
    slice_stage = _slice_stage_map(fm.get("workflow"))
    enriched: list[dict[str, Any]] = []
    for s in slices:
        n = s["n"]
        tbl = wbs_table.get(n, {})
        stage_meta = slice_stage.get(
            n, {"stage_key": "development", "plan_stage_key": "development", "optional": False}
        )
        stage_key = stage_meta["stage_key"]
        plan_stage_key = stage_meta["plan_stage_key"]
        child = plan_by_stage.get(plan_stage_key)
        done, skipped, derived_from = _derive_slice_state(s["done"], bool(s.get("skipped")), child, n)
        enriched.append(
            {
                "n": n,
                "done": done,
                "skipped": skipped,
                "optional": bool(stage_meta.get("optional")),
                "derived_from": derived_from,
                "label": s["label"],
                "title": tbl.get("title") or s["label"],
                "summary": SLICE_SUMMARY.get(n, "") if workflow in ("", "client-dev", None) else "",
                "skill": tbl.get("skill", ""),
                "input": tbl.get("input", ""),
                "output": tbl.get("output", ""),
                "acceptance": tbl.get("acceptance", ""),
                "related_plan": child,
                "stage_key": stage_key,
                "plan_stage_key": plan_stage_key,
            }
        )
    first_open = next((e["n"] for e in enriched if not e["done"]), None)
    gh = gate_history_for(rel)
    ph = progress_history_for(rel)
    done_cnt = sum(1 for e in enriched if e["done"])
    total_cnt = len(enriched)
    if is_client_dev:
        scoped = [s for s in stories if s.get("sprint_scope")]
        delivery_stories = _delivery_story_cards(stories, story_meta)
        story_done = [s for s in delivery_stories if s.get("tdd_complete")]
        status_by_stage = {p.get("stage_key"): p.get("status") for p in plans}
        adopted = {"已采纳", "已完成", "done", "completed"}
        if status_by_stage.get("requirement") not in adopted:
            cur_stage = "requirement"
        elif status_by_stage.get("prioritization") not in adopted:
            cur_stage = "prioritization"
        elif status_by_stage.get("architecture") not in adopted:
            cur_stage = "architecture"
        elif not stories or not story_meta.get("scope_confirmed"):
            cur_stage = "story-split"
        elif scoped and any(not s.get("implementation_design_ready") for s in scoped):
            cur_stage = "implementation-design"
        elif not delivery_stories or len(story_done) < len(delivery_stories):
            cur_stage = "story-development"
        elif not _test_plan_facts(plan_by_stage)["approved"]:
            cur_stage = "integration-test-plan"
        elif not _integration_pass(plan_by_stage):
            cur_stage = "integration-test"
        else:
            cur_stage = "done"
        done_cnt = len(story_done)
        total_cnt = len(delivery_stories)
    else:
        # 含 WBS 的其他工作流：第一个未完成切片所属 stage key。
        cur_stage = next((e["stage_key"] for e in enriched if not e["done"]), "done")
    p0 = int(fm.get("p0_open", "0") or "0")
    workflow_map = _build_workflow_map(
        workflow=effective_workflow,
        current_stage=cur_stage,
        plans=plans,
        stories=stories,
        story_meta=story_meta,
        test_health=test_health,
        gate_history=gh,
    )
    current_flow_stage = next(
        (stage for stage in workflow_map.get("stages", []) if stage.get("key") == cur_stage),
        {},
    )
    current_gate = current_flow_stage.get("gate") if current_flow_stage else None
    gh = _display_gate_history(gh, current_gate)
    current_failures = 0
    if current_gate and current_gate.get("result") == "fail":
        expected_snapshot = current_gate.get("plan_snapshot")
        started = False
        for event in (gh or {}).get("recent", []):
            if not started:
                if event is current_gate or (
                    event.get("stage") == cur_stage
                    and event.get("result") == "fail"
                    and event.get("plan_snapshot") == expected_snapshot
                ):
                    started = True
                else:
                    continue
            if (
                event.get("stage") != cur_stage
                or event.get("result") != "fail"
                or event.get("plan_snapshot") != expected_snapshot
            ):
                break
            current_failures += 1

    # 健康等级只消费「当前阶段 + 当前 Plan 快照」的门禁事实。
    # 正常 active 阶段是 blue，不再因「还没做完」变成 amber/red。
    if fm.get("status") == "已归档":
        health = "archived"
    elif p0 > 0 or current_failures >= 2:
        health = "red"
    elif cur_stage == "done":
        health = "green"
    elif current_flow_stage.get("state") == "blocked" or (current_gate and current_gate.get("result") == "fail"):
        health = "amber"
    else:
        health = "blue"

    blocker_hint = ""
    progress_hint = ""
    if cur_stage != "done":
        if current_flow_stage.get("state") == "blocked":
            blocker_hint = str(current_flow_stage.get("blocker") or cur_stage)
        elif is_client_dev:
            running = next((s for s in stories if s.get("state") == "running"), None)
            pending = next((s for s in stories if s.get("sprint_scope") and not s.get("tdd_complete")), None)
            progress_hint = str((running or pending or {}).get("title") or current_flow_stage.get("progress_note") or cur_stage)
        elif first_open is not None:
            progress_hint = next((e["title"] for e in enriched if e["n"] == first_open), f"WBS {first_open}")
    return {
        "file": rel,
        "name": path.stem,
        "epic_id": fm.get("epic_id", ""),
        "workflow": workflow,
        "effective_workflow": effective_workflow,
        "status": fm.get("status", ""),
        "lifecycle_state": fm.get("lifecycle_state", ""),
        "p0_open": p0,
        "repo": fm.get("repo", ""),
        "branch": fm.get("branch", ""),
        "slices": enriched,
        "stories": stories,
        "story_meta": story_meta,
        "plans": plans,
        "test_health": test_health,
        "next_slice": first_open,
        "gate_history": gh,
        "progress_history": ph,
        "health": health,
        "current_gate": current_gate,
        "current_gate_failures": current_failures,
        "current_stage": cur_stage,
        "slices_done": done_cnt,
        "slices_total": total_cnt,
        "story_points_done": sum(
            int(s.get("story_points") or 0)
            for s in (_delivery_story_cards(stories, story_meta) if is_client_dev else [])
            if s.get("tdd_complete")
        ),
        "story_points_total": sum(
            int(s.get("story_points") or 0)
            for s in (_delivery_story_cards(stories, story_meta) if is_client_dev else [])
        ),
        "blocker_hint": blocker_hint,
        "progress_hint": progress_hint,
        "workflow_map": workflow_map,
    }


def board_revision() -> str:
    epic_dir = ROOT / "Plans" / "Epic"
    files: list[Path] = []
    if epic_dir.is_dir():
        epics = [f for f in sorted(epic_dir.glob("*.md")) if not f.name.startswith(".")]
        files.extend(epics)
        child_seen: set[str] = set()
        for f in epics:
            for p in parse_plans_block(f):
                rel = p.get("path")
                if not rel or rel in child_seen:
                    continue
                child_seen.add(rel)
                pf = ROOT / rel if not Path(rel).is_absolute() else Path(rel)
                if pf.is_file():
                    files.append(pf)
    wf_globs = [
        BLUEPRINT_DIR.glob("*.json"),
        EVENT_DIR.glob("*.events.jsonl"),
        [ORPHAN_FEEDBACK],
    ]
    for group in wf_globs:
        files.extend(f for f in sorted(group, key=lambda p: p.name) if f.is_file())
    for bp in read_blueprints():
        if bp.get("uses_epic") or bp.get("kind") == "engine-index":
            continue
        for stage in bp.get("stages", []):
            folder = ROOT / str(stage.get("plan_folder") or "")
            if folder.is_dir():
                files.extend(sorted(folder.glob("*.md")))
    digest = hashlib.sha256()
    for f in files:
        digest.update(str(f.relative_to(ROOT) if f.is_relative_to(ROOT) else f).encode("utf-8"))
        digest.update(b"\0")
        digest.update(f.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def board_payload() -> list[dict[str, Any]]:
    epic_dir = ROOT / "Plans" / "Epic"
    out: list[dict[str, Any]] = []
    if not epic_dir.is_dir():
        return out
    for f in sorted(epic_dir.glob("*.md")):
        if f.name.startswith("."):
            continue
        out.append(scan_epic(f))
    return out


LIGHTWEIGHT_DONE_STATUSES = {
    "已完成",
    "已采纳",
    "已通过",
    "已复核",
    "完成",
    "done",
    "completed",
    "passed",
}


def _slugify_task(value: str) -> str:
    value = re.sub(r"\s+", "-", value.strip())
    value = re.sub(r"[^0-9A-Za-z._\-\u4e00-\u9fff]+", "-", value)
    return value.strip("-") or "未命名"


def _legacy_lightweight_title(path: Path, stage: dict[str, Any], body: str) -> str:
    """兼容旧 plan：优先从 H1 的全角/半角冒号后取任务标题，再回退到文件名。"""
    heading = re.search(r"^#\s+.+?[：:]\s*(.+?)\s*$", body, flags=re.MULTILINE)
    if heading:
        return heading.group(1).strip()
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    prefix = str(stage.get("plan_prefix") or stage.get("key") or "").strip()
    if prefix and stem.startswith(prefix + "-"):
        stem = stem[len(prefix) + 1 :]
    return stem or path.stem


def _lightweight_gate_results() -> dict[str, dict[str, Any]]:
    """返回子 Plan 的最后一次门禁事件；是否有效由当前 Plan 快照决定。"""
    results: dict[str, dict[str, Any]] = {}
    if not EVENT_DIR.is_dir():
        return results
    for event_file in sorted(EVENT_DIR.glob("*.events.jsonl")):
        for line in event_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            child = str(event.get("child_plan") or "").strip()
            if child and event.get("type") in ("gate_pass", "gate_fail"):
                results[child] = event
    return results


def lightweight_payload() -> list[dict[str, Any]]:
    gate_results = _lightweight_gate_results()
    items: list[dict[str, Any]] = []
    for bp in read_blueprints():
        if bp.get("uses_epic") or bp.get("kind") == "engine-index":
            continue
        stage_defs = {str(stage.get("key") or ""): stage for stage in bp.get("stages", [])}
        tasks: dict[str, dict[str, Any]] = {}
        seen_paths: set[str] = set()
        for stage in stage_defs.values():
            folder = ROOT / str(stage.get("plan_folder") or "")
            if not folder.is_dir():
                continue
            for path in folder.glob("*.md"):
                rel = str(path.relative_to(ROOT))
                if rel in seen_paths:
                    continue
                fm, _, body = read_frontmatter(path)
                if fm.get("workflow") != bp.get("name"):
                    continue
                stage_key = str(fm.get("workflow_stage") or "")
                matched_stage = stage_defs.get(stage_key)
                if matched_stage is None:
                    continue
                seen_paths.add(rel)
                title = str(fm.get("task_title") or "").strip() or _legacy_lightweight_title(path, matched_stage, body)
                day = str(fm.get("date") or "legacy").strip()
                task_id = str(fm.get("task_id") or "").strip() or f"{bp.get('name')}-{day}-{_slugify_task(title)}"
                task = tasks.setdefault(
                    task_id,
                    {"task_id": task_id, "title": title, "plans": {}, "updated_ns": 0},
                )
                updated_ns = path.stat().st_mtime_ns
                previous = task["plans"].get(stage_key)
                if previous is None or updated_ns > previous["updated_ns"]:
                    status = str(fm.get("status") or "").strip()
                    gate_event = gate_results.get(rel)
                    gate_result = ""
                    if _gate_matches_current_plan(gate_event, rel):
                        gate_result = "pass" if gate_event.get("type") == "gate_pass" else "fail"
                    task["plans"][stage_key] = {
                        "path": rel,
                        "status": status,
                        "gate_result": gate_result,
                        "updated_ns": updated_ns,
                    }
                task["updated_ns"] = max(task["updated_ns"], updated_ns)

        for task in tasks.values():
            stages: list[dict[str, Any]] = []
            current = "done"
            blocked = False
            for stage in bp.get("stages", []):
                key = str(stage.get("key") or "")
                plan = task["plans"].get(key)
                done = bool(
                    plan
                    and (
                        plan.get("gate_result") == "pass"
                        or str(plan.get("status") or "").lower() in LIGHTWEIGHT_DONE_STATUSES
                    )
                )
                state = "completed" if done else "upcoming"
                if not done and current == "done":
                    current = key
                    blocked = plan is None or plan.get("gate_result") == "fail"
                    state = "blocked" if blocked else "active"
                stages.append(
                    {
                        "key": key,
                        "label": stage.get("label", key),
                        "skill": stage.get("skill", ""),
                        "plan": plan,
                        "done": done,
                        "state": state,
                    }
                )
            done_count = sum(1 for stage in stages if stage["done"])
            items.append(
                {
                    "id": task["task_id"],
                    "name": task["title"],
                    "workflow": bp.get("name", ""),
                    "description": bp.get("description", ""),
                    "current_stage": current,
                    "blocked": blocked,
                    "stages_done": done_count,
                    "stages_total": len(stages),
                    "updated_ns": task["updated_ns"],
                    "stages": stages,
                }
            )
    return sorted(items, key=lambda item: int(item.get("updated_ns") or 0), reverse=True)


def aggregate_kpi(epics: list[dict[str, Any]]) -> dict[str, Any]:
    """全局 KPI —— 全部真实数据驱动，数据不足处带 sample 计数供前端标注。
    语义映射：任务管道指标 → Epic 工作流指标（详见交互设计对齐表）。"""
    total_events = 0
    pending_events = 0
    audit_events = 0
    passes = 0
    stage_fail = Counter()
    for e in epics:
        gh = e.get("gate_history") or {}
        total_events += gh.get("decisions", gh.get("total", 0))
        pending_events += gh.get("pending", 0)
        audit_events += gh.get("total", 0)
        passes += gh.get("passes", 0)
        for ev in gh.get("recent", []):
            if ev.get("result") == "fail" and ev.get("stage"):
                stage_fail[ev["stage"]] += 1
    ac_total = sum((e.get("test_health") or {}).get("ac_total", 0) for e in epics)
    ac_covered = sum((e.get("test_health") or {}).get("ac_covered", 0) for e in epics)
    p0_total = sum((e.get("test_health") or {}).get("p0_total", 0) for e in epics)
    p0_covered = sum((e.get("test_health") or {}).get("p0_covered", 0) for e in epics)
    case_count = sum((e.get("test_health") or {}).get("case_count", 0) for e in epics)
    test_risk = sum(1 for e in epics if (e.get("test_health") or {}).get("health") in ("red", "amber"))
    n_epics = len(epics)
    current_flow_stages = [
        next(
            (
                stage
                for stage in (e.get("workflow_map") or {}).get("stages", [])
                if stage.get("key") == e.get("current_stage")
            ),
            {},
        )
        for e in epics
    ]
    blocked = sum(1 for stage in current_flow_stages if stage.get("state") == "blocked")
    healthy = sum(1 for e in epics if e.get("health") == "green")
    running = sum(1 for stage in current_flow_stages if stage.get("state") == "active")
    pass_rate = round(passes / total_events * 100) if total_events else None
    top_blockers = [{"stage": s, "count": c} for s, c in stage_fail.most_common(3)]
    # 整体健康灯：任一 red→red；有 amber→amber；否则 green。
    lights = [e.get("health") for e in epics]
    overall = "red" if "red" in lights else ("amber" if "amber" in lights else "green")
    return {
        "n_epics": n_epics,
        "blocked": blocked,
        "healthy": healthy,
        "running": running,
        "pass_rate": pass_rate,
        "gate_events": total_events,
        "gate_audit_events": audit_events,
        "gate_pending_events": pending_events,
        "top_blockers": top_blockers,
        "overall_light": overall,
        "sample_low": total_events < 10,
        "test": {
            "ac_total": ac_total,
            "ac_covered": ac_covered,
            "coverage_pct": round(ac_covered / ac_total * 100) if ac_total else None,
            "p0_total": p0_total,
            "p0_covered": p0_covered,
            "p0_coverage_pct": round(p0_covered / p0_total * 100) if p0_total else None,
            "case_count": case_count,
            "risk_epics": test_risk,
        },
    }


BLUEPRINT_DIR = ROOT / ".workflows" / "blueprints"
ORPHAN_FEEDBACK = ROOT / "进化" / "孤立反馈记录.md"


def read_blueprints() -> list[dict[str, Any]]:
    """读全部工作流蓝图定义，输出阶段链（供图谱渲染）。"""
    out: list[dict[str, Any]] = []
    if not BLUEPRINT_DIR.is_dir():
        return out
    for f in sorted(BLUEPRINT_DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        stages = []
        for s in d.get("stages", []):
            crit = s.get("exitCriteria", {}) or {}
            stages.append(
                {
                    "key": s.get("key", ""),
                    "label": s.get("label", s.get("key", "")),
                    "skill": (s.get("skills") or [""])[0],
                    "plan_folder": s.get("planFolder", ""),
                    "plan_prefix": s.get("planPrefix", ""),
                    "exit": [k for k, v in crit.items() if v],
                    "onlyIf": s.get("onlyIf") or {},
                }
            )
        out.append(
            {
                "kind": d.get("kind", ""),
                "name": d.get("name", f.stem),
                "version": d.get("version", ""),
                "uses_epic": bool(d.get("usesEpic")),
                "description": d.get("description", ""),
                "stages": stages,
            }
        )
    return out


def all_gate_events() -> list[dict[str, Any]]:
    """跨全部 Epic 的门禁事件流，时间倒序，供运行态监控。"""
    events: list[dict[str, Any]] = []
    if not EVENT_DIR.is_dir():
        return events
    for f in EVENT_DIR.glob("*.events.jsonl"):
        epic_stem = f.name[: -len(".events.jsonl")]
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") not in ("gate_pass", "gate_fail"):
                continue
            events.append(
                {
                    "epic": epic_stem,
                    "result": "pass" if ev.get("type") == "gate_pass" else "fail",
                    "stage": ev.get("stage"),
                    "at": (ev.get("created_at") or "")[:19].replace("T", " "),
                    "reason": (ev.get("reason") or "").split(";")[0].strip(),
                    "git_commit": (ev.get("git_commit") or "")[:7],
                    "inferred": bool(ev.get("inferred")),
                    "passed_stages": ev.get("passed_stages") or [],
                }
            )
    events.sort(key=lambda e: e.get("at", ""), reverse=True)
    return events


def read_evolution_candidates() -> dict[str, list[dict[str, Any]]]:
    """从孤立反馈记录抽两组供看板展示：
    - pending：『待整理』区标题含「进化候选」的未归位待办。
    - resolved：『已归位』区的已落地条目摘要（保留完整演进史，不删）。"""
    empty = {"pending": [], "resolved": []}
    if not ORPHAN_FEEDBACK.is_file():
        return empty
    text = ORPHAN_FEEDBACK.read_text(encoding="utf-8")

    pending: list[dict[str, Any]] = []
    m = re.search(r"##\s*(?:待整理|待蒸馏)\s*\n(.*?)(?=\n##\s|\Z)", text, re.S)
    if m:
        for mm in re.finditer(r"###\s+(.+?)\n(.*?)(?=\n###\s|\Z)", m.group(1), re.S):
            title = mm.group(1).strip()
            if title.startswith("〔") or "进化候选" not in title:
                continue
            title = re.sub(r"^进化候选[:：]\s*", "", title)
            body = mm.group(2).strip()
            summary = ""
            for ln in body.splitlines():
                s = ln.strip().lstrip("-* ").strip()
                if s and not s.startswith("```") and not s.startswith("skill_run"):
                    summary = re.sub(r"[*`]", "", s)[:120]
                    break
            pending.append({"title": title, "summary": summary})

    resolved: list[dict[str, Any]] = []
    r = re.search(r"##\s*已归位[^\n]*\n(.*?)(?=\n##\s|\Z)", text, re.S)
    if r:
        for mm in re.finditer(r"^-\s+\*\*(.+?)\*\*\s*(.+?)(?=\n-\s+\*\*|\Z)", r.group(1), re.S | re.M):
            date = mm.group(1).strip()
            body = re.sub(r"[*`]", "", mm.group(2).strip().replace("\n", " "))
            resolved.append({"date": date, "summary": body[:140]})

    return {"pending": pending, "resolved": resolved}


def read_evolution_pending() -> list[dict[str, Any]]:
    """向后兼容：仅未归位候选（旧调用点用）。"""
    return read_evolution_candidates()["pending"]


def workflows_envelope() -> dict[str, Any]:
    events = all_gate_events()
    stage_fail = Counter(e["stage"] for e in events if e["result"] == "fail" and e.get("stage"))
    warn: list[dict[str, Any]] = []
    by_epic: dict[str, list[dict[str, Any]]] = {}
    for e in events:
        by_epic.setdefault(e["epic"], []).append(e)
    for epic, evs in by_epic.items():
        evs_sorted = sorted(evs, key=lambda x: x.get("at", ""))
        if not evs_sorted:
            continue
        last = evs_sorted[-1]
        if last["result"] != "fail":
            continue
        consec = 0
        for e in reversed(evs_sorted):
            if e["stage"] == last["stage"] and e["result"] == "fail":
                consec += 1
            else:
                break
        if consec >= 2:
            warn.append({"epic": epic, "stage": last["stage"], "consecutive": consec, "reason": last["reason"]})
    blueprints = read_blueprints()
    pass_n = sum(1 for e in events if e["result"] == "pass")
    return {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "blueprints": blueprints,
        "events": events[:40],
        "top_blockers": [{"stage": s, "count": c} for s, c in stage_fail.most_common(5)],
        "warnings": warn,
        "evolution": read_evolution_candidates(),
        "stats": {
            "blueprint_count": len(blueprints),
            "event_count": len(events),
            "pass_rate": round(pass_n / len(events) * 100) if events else None,
            "sample_low": len(events) < 10,
        },
    }


TEST_SUITE_CATALOG = [
    {
        "id": "merge-code-p0-scenarios",
        "group": "workflow-engine",
        "object_type": "workflow-engine",
        "level": "regression",
        "level_label": "P0 场景回归",
        "priority": "P0",
        "name": "代码合并工作流真实场景",
        "command": "python3 scripts/test-merge-code-workflow.py",
        "argv": ["python3", "scripts/test-merge-code-workflow.py"],
        "scope": "快进、重复合并、跨文件、同文件不同区块、权限位、文本冲突、删除/修改、重命名、二进制、同路径新增、文件/目录、脏工作树、无文本业务冲突、决策追踪",
        "signal": "AI 工作流自身",
    },
    {
        "id": "client-dev-p0-scenarios",
        "group": "workflow-engine",
        "object_type": "workflow-engine",
        "level": "regression",
        "level_label": "P0 场景回归",
        "priority": "P0",
        "name": "客户端开发工作流故事流",
        "command": "python3 scripts/test-client-dev-workflow.py",
        "argv": ["python3", "scripts/test-client-dev-workflow.py"],
        "scope": "client-dev 敏捷故事流、Story TDD 证据、集成报告和门禁派生行为",
        "signal": "AI 工作流自身",
    },
    {
        "id": "workflow-dedicated-regression",
        "group": "workflow-engine",
        "object_type": "workflow-engine",
        "level": "regression",
        "level_label": "P0 专属契约回归",
        "priority": "P0",
        "name": "工作流专属回归契约",
        "command": "python3 scripts/workflow-dedicated-regression-gate.py bugfix ui-change story-split-only computer-mgmt learning-loop",
        "argv": [
            "python3",
            "scripts/workflow-dedicated-regression-gate.py",
            "bugfix",
            "ui-change",
            "story-split-only",
            "computer-mgmt",
            "learning-loop",
        ],
        "scope": "bugfix / ui-change / story-split-only / computer-mgmt / learning-loop 的工作流特有阶段链、路由与门禁契约",
        "signal": "AI 工作流自身",
    },
    {
        "id": "workflow-core-unit",
        "group": "workflow-engine",
        "object_type": "workflow-engine",
        "level": "unit",
        "level_label": "单元测试",
        "name": "工作流核心单元测试",
        "command": (
            "python3 scripts/test-workflow-refactor.py "
            "WorkflowRefactorTests.test_gate_parse_supports_negative_ac_and_filters_placeholder_tests "
            "WorkflowRefactorTests.test_kanban_exposes_test_coverage_health "
            "WorkflowRefactorTests.test_kanban_test_coverage_flags_missing_p0_tests"
        ),
        "argv": [
            "python3",
            "scripts/test-workflow-refactor.py",
            "WorkflowRefactorTests.test_gate_parse_supports_negative_ac_and_filters_placeholder_tests",
            "WorkflowRefactorTests.test_kanban_exposes_test_coverage_health",
            "WorkflowRefactorTests.test_kanban_test_coverage_flags_missing_p0_tests",
        ],
        "scope": "AC 解析、测试覆盖健康度、P0 缺口判定",
        "signal": "AI 工作流自身",
    },
    {
        "id": "workflow-refactor",
        "group": "workflow-engine",
        "object_type": "workflow-engine",
        "level": "regression",
        "level_label": "回归测试",
        "name": "全量工作流回归",
        "command": "python3 scripts/test-workflow-refactor.py",
        "argv": ["python3", "scripts/test-workflow-refactor.py"],
        "scope": "蓝图 schema、路由、gate、run 事件、traceability、看板派生",
        "signal": "AI 工作流自身",
    },
    {
        "id": "workflow-smoke",
        "group": "workflow-engine",
        "object_type": "workflow-engine",
        "level": "integration",
        "level_label": "集成测试",
        "name": "工作流逐阶段 smoke",
        "command": "python3 scripts/workflow-smoke-test.py",
        "argv": ["python3", "scripts/workflow-smoke-test.py"],
        "scope": "merge-code / ui-change / bugfix / story-split-only / computer-mgmt / client-dev",
        "signal": "AI 工作流自身",
    },
    {
        "id": "workflow-utterance-e2e",
        "group": "workflow-engine",
        "object_type": "workflow-engine",
        "level": "e2e",
        "level_label": "端到端测试",
        "name": "自然语言入口 E2E",
        "command": 'python3 scripts/workflow-smoke-test.py --utterance "全流程开发一下支付收银台"',
        "argv": ["python3", "scripts/workflow-smoke-test.py", "--utterance", "全流程开发一下支付收银台"],
        "scope": "需求文本 → router → workflow → 逐阶段 gate → done",
        "signal": "AI 工作流自身",
    },
    {
        "id": "blueprint-schema",
        "group": "workflow-engine",
        "object_type": "workflow-engine",
        "level": "contract",
        "level_label": "契约 / Schema 测试",
        "name": "蓝图 schema 校验",
        "command": "python3 scripts/validate-workflow-blueprint.py",
        "argv": ["python3", "scripts/validate-workflow-blueprint.py"],
        "scope": ".workflows/blueprints/*.json",
        "signal": "AI 工作流自身",
    },
    {
        "id": "skill-fixtures",
        "group": "skill-fixtures",
        "object_type": "workflow-engine",
        "level": "integration",
        "level_label": "集成测试",
        "name": "Skill 产物 fixture",
        "command": "python3 scripts/skill-smoke-all.py",
        "argv": ["python3", "scripts/skill-smoke-all.py"],
        "scope": "产物型 Skill 的输入/输出 fixture 覆盖",
        "signal": "AI 工作流自身",
    },
]


TEST_OBJECTS = [
    {
        "id": "workflow-engine",
        "title": "AI 工作流自身测试",
        "description": "验证路由、蓝图、门禁、事件、Skill fixture 与全流程入口。",
        "levels": [
            {"id": "unit", "title": "单元测试"},
            {"id": "contract", "title": "契约 / Schema 测试"},
            {"id": "integration", "title": "集成测试"},
            {"id": "e2e", "title": "端到端测试"},
            {"id": "regression", "title": "回归测试"},
        ],
    },
    {
        "id": "workflow-task",
        "title": "工作流任务测试",
        "description": "验证每个 Epic 的验收标准、测试用例、开发覆盖与任务级执行结果。",
        "levels": [
            {"id": "unit", "title": "单元测试"},
            {"id": "acceptance", "title": "验收测试"},
            {"id": "integration", "title": "集成测试"},
            {"id": "e2e", "title": "端到端测试"},
            {"id": "regression", "title": "回归测试"},
        ],
    },
]


def _case_level(case_type: str) -> tuple[str, str]:
    text = (case_type or "").lower()
    if "单元" in case_type or "unit" in text or text == "ut":
        return "unit", "单元测试"
    if "契约" in case_type or "schema" in text or "contract" in text:
        return "contract", "契约 / Schema 测试"
    if "集成" in case_type or "integration" in text or text == "it":
        return "integration", "集成测试"
    if "端到端" in case_type or "e2e" in text:
        return "e2e", "端到端测试"
    if "回归" in case_type or "regression" in text:
        return "regression", "回归测试"
    return "acceptance", "验收测试"


def _test_cases_for(epic_name: str, test_rel: str | None) -> list[dict[str, Any]]:
    cases = _parse_plan_fact(test_rel, _parse_test_map)
    out: list[dict[str, Any]] = []
    for ac_id, items in sorted(cases.items()):
        for item in items:
            level, level_label = _case_level(item.get("type", ""))
            out.append(
                {
                    "object_type": "workflow-task",
                    "level": level,
                    "level_label": level_label,
                    "epic": epic_name,
                    "ac": ac_id,
                    "case_id": item.get("case_id", ""),
                    "type": item.get("type", ""),
                    "description": item.get("description", ""),
                    "status": item.get("status", ""),
                    "line": item.get("line", ""),
                    "test_plan": test_rel,
                }
            )
    return out


def _task_level_summary(th: dict[str, Any]) -> list[dict[str, Any]]:
    case_count = int(th.get("case_count") or 0)
    p0_total = int(th.get("p0_total") or 0)
    p0_covered = int(th.get("p0_covered") or 0)
    p0_dev_covered = int(th.get("p0_dev_covered") or 0)
    coverage_pct = th.get("coverage_pct")
    health = th.get("health") or "none"
    story_mode = "story_total" in th
    story_total = int(th.get("story_total") or 0)
    story_done = int(th.get("story_done") or 0)
    integration_pass = bool(th.get("integration_pass"))
    unit_status = "ready" if case_count else "not-connected"
    unit_summary = f"{case_count} 个任务级用例" if case_count else "测试 plan 暂无可识别用例"
    return [
        {
            "id": "unit",
            "title": "单元测试",
            "status": unit_status,
            "summary": unit_summary,
            "count": case_count,
            "runnable": False,
        },
        {
            "id": "acceptance",
            "title": "验收测试",
            "status": health,
            "summary": (
                f"Scope Story TDD {story_done}/{story_total}"
                if story_mode
                else f"AC 覆盖 {coverage_pct if coverage_pct is not None else '—'}%，P0 {p0_covered}/{p0_total}"
            ),
            "count": story_done if story_mode else p0_covered,
            "total": story_total if story_mode else p0_total,
            "coverage_pct": coverage_pct,
            "runnable": True,
        },
        {
            "id": "integration",
            "title": "集成测试",
            "status": "green" if integration_pass else "not-connected",
            "summary": "全量集成测试已通过" if integration_pass else "尚未通过全量集成测试",
            "count": 1 if integration_pass else 0,
            "runnable": story_mode,
        },
        {
            "id": "e2e",
            "title": "端到端测试",
            "status": "not-connected",
            "summary": "尚未接入任务级 E2E 测试命令",
            "count": 0,
            "runnable": False,
        },
        {
            "id": "regression",
            "title": "回归测试",
            "status": "ready" if (integration_pass or p0_dev_covered) else "not-connected",
            "summary": (
                "集成报告已覆盖当前目标 commit"
                if story_mode and integration_pass
                else (f"P0 开发覆盖 {p0_dev_covered}/{p0_total}" if p0_total else "暂无 P0 开发覆盖数据")
            ),
            "count": 1 if story_mode and integration_pass else p0_dev_covered,
            "total": 1 if story_mode else p0_total,
            "runnable": False,
        },
    ]


def tests_envelope() -> dict[str, Any]:
    epics = board_payload()
    test_kpi = aggregate_kpi(epics).get("test", {})
    task_rows = []
    all_cases: list[dict[str, Any]] = []
    gap_counter = Counter()
    for e in epics:
        th = e.get("test_health") or {}
        all_cases.extend(_test_cases_for(e.get("name", ""), th.get("test_plan")))
        for blocker in th.get("blockers", []) or []:
            if "P0 AC 缺测试覆盖" in blocker:
                gap_counter["P0 缺测试覆盖"] += 1
            elif "P0 AC 缺开发任务覆盖" in blocker:
                gap_counter["P0 缺开发覆盖"] += 1
            elif "测试 plan 未创建" in blocker:
                gap_counter["测试 plan 未创建"] += 1
            elif "需求 AC 未解析到" in blocker:
                gap_counter["需求 AC 未解析"] += 1
            else:
                gap_counter["其他测试缺口"] += 1
        task_rows.append(
            {
                "object_type": "workflow-task",
                "level": "acceptance",
                "level_label": "验收测试",
                "epic": e.get("name"),
                "file": e.get("file"),
                "stage": e.get("current_stage"),
                "health": th.get("health"),
                "coverage_pct": th.get("coverage_pct"),
                "p0_coverage_pct": th.get("p0_coverage_pct"),
                "p0_total": th.get("p0_total"),
                "p0_covered": th.get("p0_covered"),
                "p0_dev_covered": th.get("p0_dev_covered"),
                "case_count": th.get("case_count"),
                "test_status": th.get("test_status"),
                "test_plan": th.get("test_plan"),
                "blockers": th.get("blockers", []),
                "levels": _task_level_summary(th),
            }
        )
    task_rows.sort(key=lambda r: ({"red": 0, "amber": 1, "none": 2, "green": 3}.get(r.get("health"), 9), r.get("epic") or ""))
    return {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "kpi": {
            **test_kpi,
            "workflow_suite_count": len(TEST_SUITE_CATALOG),
            "task_epic_count": len(task_rows),
        },
        "objects": TEST_OBJECTS,
        "suites": TEST_SUITE_CATALOG,
        "task_tests": task_rows,
        "cases": all_cases,
        "gaps": [{"name": name, "count": count} for name, count in gap_counter.most_common()],
        "taxonomy": [
            {"group": "workflow-engine", "title": "AI 工作流自身", "items": ["单元测试", "契约 / Schema", "集成测试", "端到端测试", "回归测试"]},
            {"group": "workflow-task", "title": "工作流任务", "items": ["单元测试", "验收测试", "集成测试", "端到端测试", "回归测试"]},
        ],
    }


def _run_allowed_command(argv: list[str]) -> dict[str, Any]:
    started = datetime.now().isoformat(timespec="seconds")
    try:
        proc = subprocess.run(
            argv,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=240,
        )
        output = (proc.stdout + ("\n" if proc.stdout and proc.stderr else "") + proc.stderr).strip()
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "started_at": started,
            "finished_at": datetime.now().isoformat(timespec="seconds"),
            "command": " ".join(argv),
            "output": output[-16000:],
        }
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or "") + ("\n" if exc.stdout and exc.stderr else "") + (exc.stderr or "")).strip()
        return {
            "ok": False,
            "returncode": None,
            "started_at": started,
            "finished_at": datetime.now().isoformat(timespec="seconds"),
            "command": " ".join(argv),
            "output": (output + "\nTIMEOUT: 240s").strip()[-16000:],
        }


def run_test_from_board(kind: str, test_id: str) -> dict[str, Any]:
    if kind == "suite":
        suite = next((s for s in TEST_SUITE_CATALOG if s["id"] == test_id), None)
        if not suite:
            raise ValueError("unknown suite")
        return _run_allowed_command(list(suite["argv"]))
    if kind == "task":
        epic = next((e for e in board_payload() if e.get("file") == test_id), None)
        if not epic:
            raise ValueError("unknown epic")
        if epic.get("effective_workflow") == "client-dev":
            th = epic.get("test_health") or {}
            dev_plan = th.get("development_plan")
            integration_plan = th.get("test_plan")
            if not dev_plan or not integration_plan:
                return {
                    "ok": False,
                    "returncode": 1,
                    "command": "python3 scripts/validate-client-dev.py",
                    "output": "BLOCKED:client-dev: 看板缺少 Story 开发或集成测试 Plan",
                }
            dev_argv = ["python3", "scripts/validate-client-dev.py", "story-development", "--plan", dev_plan]
            integration_argv = ["python3", "scripts/validate-client-dev.py", "integration", "--plan", integration_plan]
            result = _run_allowed_command(dev_argv)
            integration_result = _run_allowed_command(integration_argv)
            result["ok"] = bool(result["ok"] and integration_result["ok"])
            result["returncode"] = 0 if result["ok"] else 1
            result["command"] += " && " + integration_result["command"]
            result["output"] = (
                result.get("output", "")
                + "\n\n--- integration ---\n"
                + integration_result.get("output", "")
            ).strip()[-16000:]
            return result
        argv = ["python3", "scripts/traceability-check.py", "--epic", test_id, "--check", "test"]
        result = _run_allowed_command(argv)
        dev_argv = ["python3", "scripts/traceability-check.py", "--epic", test_id, "--check", "dev"]
        dev_result = _run_allowed_command(dev_argv)
        result["ok"] = bool(result["ok"] and dev_result["ok"])
        result["returncode"] = 0 if result["ok"] else 1
        result["command"] = result["command"] + " && " + dev_result["command"]
        result["output"] = (result.get("output", "") + "\n\n--- dev coverage ---\n" + dev_result.get("output", "")).strip()[-16000:]
        return result
    raise ValueError("unknown test kind")


def board_envelope() -> dict[str, Any]:
    epics = board_payload()
    return {
        "revision": board_revision(),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "epics": epics,
        "lightweight": lightweight_payload(),
        "kpi": aggregate_kpi(epics),
    }


def append_change_log(epic: Path, change_type: str, stage: str, slices: str, operator: str, note: str) -> None:
    text = epic.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    row = f"| {today} | {change_type} | {stage} | {slices} | {operator} | {note} |"
    marker = next(
        (m for m in ("## 四、变更日志", "## 四、变更与迁移", "## 变更日志") if m in text),
        "## 变更日志",
    )
    if marker not in text:
        text = (
            text.rstrip()
            + f"\n\n## 四、变更日志\n\n| 日期 | 变更类型 | 影响阶段 | 重开切片 | 确认人 | 说明 |\n|------|----------|----------|----------|--------|------|\n{row}\n"
        )
        epic.write_text(text, encoding="utf-8")
        return
    lines = text.splitlines()
    insert_at = None
    for i, line in enumerate(lines):
        if line.startswith("|------") and i > 0 and "日期" in lines[i - 1]:
            insert_at = i + 1
            break
    if insert_at is None:
        lines.append(row)
    else:
        lines.insert(insert_at, row)
    epic.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")


def _slice_line_matches(path: Path, slice_n: int) -> list[tuple[int, re.Match[str]]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    in_fence = False
    matches: list[tuple[int, re.Match[str]]] = []
    for i, line in enumerate(lines):
        if line.strip() == "```":
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        m = SLICE_RE.match(line)
        if not m or int(m.group(2)) != slice_n:
            continue
        matches.append((i, m))
    return matches


def set_slice_status(plan: Path, slice_n: int, state: str) -> None:
    mark_by_state = {"done": "[x]", "open": "[ ]", "skipped": "[-]"}
    if state not in mark_by_state:
        raise ValueError(f"invalid slice state: {state}")
    text = plan.read_text(encoding="utf-8")
    lines = text.splitlines()
    matches = _slice_line_matches(plan, slice_n)
    if not matches:
        raise ValueError(f"slice {slice_n} not found")
    if len(matches) > 1 or matches[0][1].group(3):
        raise ValueError(
            f"slice {slice_n} has sub-items (e.g. {slice_n}a/{slice_n}b); edit the Epic file directly"
        )
    i, m = matches[0]
    mark = mark_by_state[state]
    lines[i] = f"{mark} {slice_n}.  {m.group(4).strip()}"
    plan.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")


def update_slice_from_epic(epic: Path, slice_n: int, state: str, operator: str = "web") -> dict[str, Any]:
    data = scan_epic(epic)
    item = next((s for s in data.get("slices", []) if s.get("n") == slice_n), None)
    if not item:
        raise ValueError(f"slice {slice_n} not found")
    if state == "skipped" and not item.get("optional"):
        raise ValueError(f"slice {slice_n} is not optional")
    previous_state = "skipped" if item.get("skipped") else ("done" if item.get("done") else "open")

    epic_rel = str(epic.relative_to(ROOT)) if epic.is_relative_to(ROOT) else str(epic)
    target_rel = item.get("related_plan") or epic_rel
    target = resolve_plan(target_rel)
    if not target.is_file() or not _slice_line_matches(target, slice_n):
        target = epic
        target_rel = epic_rel

    set_slice_status(target, slice_n, state)
    action = {"done": "勾选切片", "open": "重开切片", "skipped": "跳过切片"}[state]
    append_change_log(
        epic,
        action,
        item.get("stage_key", "development"),
        str(slice_n),
        operator,
        f"WBS {slice_n} → {state}（写入 {target_rel}）",
    )
    append_wbs_progress_event(
        epic_rel=epic_rel,
        workflow=data.get("workflow"),
        slice_n=slice_n,
        stage=item.get("stage_key", "development"),
        state=state,
        previous_state=previous_state,
        target=target_rel,
        operator=operator,
        label=item.get("title") or item.get("label") or f"WBS {slice_n}",
        optional=bool(item.get("optional")),
    )
    return {"target": target_rel, "state": state, "optional": bool(item.get("optional"))}


def toggle_slice(epic: Path, slice_n: int, done: bool, operator: str = "web") -> None:
    update_slice_from_epic(epic, slice_n, "done" if done else "open", operator)


def suggest_trigger(epic_file: str) -> dict[str, str]:
    epic = resolve_plan(epic_file)
    data = scan_epic(epic)
    ns = data.get("next_slice")
    lc = data.get("current_stage") or data.get("lifecycle_state", "development")
    skill_map = {
        "requirement": "requirement-analyst",
        "prioritization": "backlog-prioritization-assistant",
        "architecture": "architecture-design-assistant",
        "story-split": "task-splitter",
        "implementation-design": "implementation-design-assistant",
        "story-development": "feature-dev-assistant",
        "integration-test-plan": "test-generator",
        "integration-test": "test-generator",
        "development": "feature-dev-assistant",
        "test": "test-generator",
        "deploy": "deployment-assistant",
    }
    dev_plan = next((p["path"] for p in data.get("plans", []) if p.get("stage_key") == "development" and p.get("path")), None)
    pending_story = next(
        (s for s in data.get("stories", []) if s.get("sprint_scope") and not s.get("tdd_complete")),
        None,
    )
    plan_by_stage = {p.get("stage_key"): p.get("path") for p in data.get("plans", [])}
    stage_plan_key = {
        "requirement": "requirement",
        "prioritization": "prioritization",
        "architecture": "architecture",
        "story-split": "development",
        "implementation-design": "development",
        "story-development": "development",
        "integration-test-plan": "integration_plan",
        "integration-test": "integration",
    }.get(lc)
    if lc == "story-development" and pending_story and pending_story.get("path"):
        cmd = f"/resume plan={pending_story['path']} 进度={pending_story.get('id')} 待做"
    elif stage_plan_key and plan_by_stage.get(stage_plan_key):
        cmd = f"/resume plan={plan_by_stage[stage_plan_key]} 进度={lc} 待做"
    elif lc == "development" and dev_plan and ns:
        cmd = f"/resume plan={dev_plan} 进度=WBS{ns} 待做"
    elif ns:
        cmd = f"/resume plan={epic_file} 进度=WBS{ns} 待做"
    else:
        cmd = f"/resume plan={epic_file} 进度=lifecycle={lc} 待续"
    return {
        "command": cmd,
        "skill": skill_map.get(lc, "resume-assistant"),
        "next_slice": str(ns) if ns else "",
        "lifecycle_state": lc,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "EpicKanban/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _json(self, code: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send_static("index.html", "text/html; charset=utf-8")
            return
        if path == "/workflows" or path == "/workflows.html":
            self._send_static("workflows.html", "text/html; charset=utf-8")
            return
        if path == "/tests" or path == "/tests.html":
            self._send_static("tests.html", "text/html; charset=utf-8")
            return
        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if path == "/api/board":
            env = board_envelope()
            self._json(200, env)
            return
        if path == "/api/workflows":
            self._json(200, workflows_envelope())
            return
        if path == "/api/tests":
            self._json(200, tests_envelope())
            return
        if path == "/api/revision":
            self._json(
                200,
                {"revision": board_revision(), "updated_at": datetime.now().isoformat(timespec="seconds")},
            )
            return
        self._json(404, {"error": "not found"})

    def _send_static(self, name: str, content_type: str) -> None:
        f = KANBAN_DIR / name
        if not f.is_file():
            self._json(404, {"error": f"{name} missing"})
            return
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._read_json()
            if path == "/api/open-file":
                result = open_workspace_file(str(body.get("file") or ""))
                self._json(200, result)
                return
            if path == "/api/status":
                rel = body.get("file", "")
                status = body.get("status", "")
                operator = body.get("operator", "web")
                if status not in PLAN_STATUSES:
                    self._json(400, {"error": "invalid status"})
                    return
                target = resolve_plan(rel)
                write_frontmatter_field(target, "status", status)
                epic_rel = body.get("epic")
                if epic_rel:
                    append_change_log(
                        resolve_plan(epic_rel),
                        "改 status",
                        body.get("stage", "—"),
                        "—",
                        operator,
                        f"{rel} → {status}",
                    )
                self._json(200, {"ok": True, "file": rel, "status": status})
                return
            if path == "/api/test-run":
                kind = str(body.get("kind", ""))
                test_id = str(body.get("id", ""))
                result = run_test_from_board(kind, test_id)
                self._json(200, result)
                return
            if path == "/api/slice":
                rel = body.get("file", "")
                slice_n = int(body.get("slice", 0))
                state = str(body.get("state") or "")
                if not state:
                    state = "done" if bool(body.get("done", True)) else "open"
                operator = body.get("operator", "web")
                epic = resolve_plan(rel)
                result = update_slice_from_epic(epic, slice_n, state, operator)
                self._json(200, {"ok": True, "file": rel, "slice": slice_n, **result})
                return
            if path == "/api/lifecycle":
                rel = body.get("file", "")
                lc = body.get("lifecycle_state", "")
                operator = body.get("operator", "web")
                allowed = {"requirement", "architecture", "development", "test", "deploy", "done"}
                if lc not in allowed:
                    self._json(400, {"error": "invalid lifecycle_state"})
                    return
                epic = resolve_plan(rel)
                write_frontmatter_field(epic, "lifecycle_state", lc)
                append_change_log(
                    epic,
                    "改 lifecycle",
                    lc,
                    "—",
                    operator,
                    f"lifecycle_state → {lc}",
                )
                self._json(200, {"ok": True, "file": rel, "lifecycle_state": lc})
                return
            if path == "/api/trigger":
                rel = body.get("file") or body.get("epic", "")
                result = suggest_trigger(rel)
                self._json(200, result)
                return
            if path == "/api/epic-archive":
                # 手动结束/重激活：改 Epic frontmatter status（可逆，文件保留）。
                rel = body.get("file", "")
                archived = bool(body.get("archived", True))
                operator = body.get("operator", "web")
                epic = resolve_plan(rel)
                if "Epic" not in epic.parts:
                    self._json(400, {"error": "not an epic path"})
                    return
                new_status = "已归档" if archived else "进行中"
                write_frontmatter_field(epic, "status", new_status)
                append_change_log(epic, "归档" if archived else "重激活", "—", "—", operator,
                                   f"status → {new_status}")
                self._json(200, {"ok": True, "file": rel, "status": new_status})
                return
            if path == "/api/epic-delete":
                # 只删 Epic 主文件，保留子 plan。严格校验：必须 Plans/Epic/ 下的 .md。
                rel = body.get("file", "")
                epic = resolve_plan(rel)
                if "Epic" not in epic.parts or epic.suffix != ".md":
                    self._json(400, {"error": "refuse: not an Epic .md file"})
                    return
                if not epic.is_file():
                    self._json(404, {"error": "epic not found"})
                    return
                epic.unlink()
                self._json(200, {"ok": True, "deleted": rel})
                return
            self._json(404, {"error": "not found"})
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            self._json(400, {"error": str(e)})


def main() -> None:
    if not KANBAN_DIR.is_dir():
        KANBAN_DIR.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Epic kanban → http://{HOST}:{PORT}/  (Ctrl+C to stop)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)


if __name__ == "__main__":
    main()
