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
        if ev.get("stage") != last_stage or ev.get("type") != "gate_fail":
            break
        consecutive_fails += 1
    # recent：最近若干条完整事件（时间倒序），供前端渲染门禁时间线。
    recent = [
        {
            "result": "pass" if e.get("type") == "gate_pass" else "fail",
            "stage": e.get("stage"),
            "at": (e.get("created_at") or "")[:19].replace("T", " "),
            "reason": (e.get("reason") or "").split(";")[0].strip(),
            "git_commit": (e.get("git_commit") or "")[:7],
            "inferred": bool(e.get("inferred")),
            "passed_stages": e.get("passed_stages") or [],
        }
        for e in reversed(gate_events)
    ][:12]
    passes = sum(1 for e in gate_events if e.get("type") == "gate_pass")
    return {
        "last_gate": {
            "result": "pass" if last.get("type") == "gate_pass" else "fail",
            "stage": last_stage,
            "at": (last.get("created_at") or "")[:10],
            "reason": (last.get("reason") or "").split(";")[0].strip(),
        },
        "consecutive_fails": consecutive_fails,
        "recent": recent,
        "total": len(gate_events),
        "passes": passes,
    }


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
        "architecture": "技术方案",
        "development": "功能开发",
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
                    fm, _, _ = read_frontmatter(sp)
                    sub["status"] = fm.get("status")
                    sub["lifecycle_state"] = fm.get("lifecycle_state", stage_key)
                else:
                    sub["status"] = None
            except ValueError:
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
    path = ROOT / ".workflows" / "blueprints" / f"{name}.json"
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
    raw: list[dict[str, Any]] = []
    for line in text.splitlines():
        if line.strip() == "```":
            in_fence = not in_fence
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


def _test_health(plan_by_stage: dict[str, str], plans: list[dict[str, Any]]) -> dict[str, Any]:
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


def scan_epic(path: Path) -> dict[str, Any]:
    fm, _, _ = read_frontmatter(path)
    rel = str(path.relative_to(ROOT))
    workflow = fm.get("workflow")
    slices = parse_wbs_slices(path)
    wbs_table = parse_wbs_table(path)
    plans = parse_plans_block(path)
    plan_by_stage = {p["stage_key"]: p.get("path") for p in plans if p.get("path")}
    test_health = _test_health(plan_by_stage, plans)
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
    # 当前阶段：第一个未完成切片所属 stage_key；全完成则 done。
    cur_stage = next((e["stage_key"] for e in enriched if not e["done"]), "done")
    consec = (gh or {}).get("consecutive_fails", 0)
    p0 = int(fm.get("p0_open", "0") or "0")
    # 健康等级（指挥官排序依据）：archived 已归档（置灰，排最后）；
    # red 连续fail≥2 或 P0未闭环；amber 有未完成或最近fail；green 全通过。
    if fm.get("status") == "已归档":
        health = "archived"
    elif consec >= 2 or p0 > 0:
        health = "red"
    elif cur_stage == "done":
        health = "green"
    elif (gh and gh["last_gate"]["result"] == "fail") or total_cnt > done_cnt:
        health = "amber"
    else:
        health = "blue"
    blocker = ""
    if first_open is not None:
        blocker = next((e["title"] for e in enriched if e["n"] == first_open), f"WBS {first_open}")
    return {
        "file": rel,
        "name": path.stem,
        "epic_id": fm.get("epic_id", ""),
        "workflow": workflow,
        "status": fm.get("status", ""),
        "lifecycle_state": fm.get("lifecycle_state", ""),
        "p0_open": p0,
        "repo": fm.get("repo", ""),
        "branch": fm.get("branch", ""),
        "slices": enriched,
        "plans": plans,
        "test_health": test_health,
        "next_slice": first_open,
        "gate_history": gh,
        "progress_history": ph,
        "health": health,
        "current_stage": cur_stage,
        "slices_done": done_cnt,
        "slices_total": total_cnt,
        "blocker_hint": blocker,
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
        [CONSTITUTION_FILE, ORPHAN_FEEDBACK],
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


def _latest_stage_plan(stage: dict[str, Any]) -> dict[str, Any] | None:
    folder = ROOT / str(stage.get("plan_folder") or "")
    if not folder.is_dir():
        return None
    prefix = str(stage.get("plan_prefix") or stage.get("key") or "")
    candidates = [f for f in folder.glob("*.md") if not prefix or prefix in f.name]
    if not candidates:
        return None
    latest = max(candidates, key=lambda f: f.stat().st_mtime_ns)
    rel = str(latest.relative_to(ROOT))
    fm, _, _ = read_frontmatter(latest)
    return {"path": rel, "status": fm.get("status", ""), "updated_ns": latest.stat().st_mtime_ns}


def lightweight_payload() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for bp in read_blueprints():
        if bp.get("uses_epic") or bp.get("kind") == "engine-index":
            continue
        stages = []
        current = "done"
        blocked = False
        for stage in bp.get("stages", []):
            plan = _latest_stage_plan(stage)
            done = bool(plan)
            if not done and current == "done":
                current = str(stage.get("key") or "")
                blocked = True
            stages.append(
                {
                    "key": stage.get("key", ""),
                    "label": stage.get("label", stage.get("key", "")),
                    "skill": stage.get("skill", ""),
                    "plan": plan,
                    "done": done,
                }
            )
        total = len(stages)
        done_count = sum(1 for s in stages if s.get("done"))
        if done_count == 0:
            continue
        items.append(
            {
                "name": bp.get("name", ""),
                "description": bp.get("description", ""),
                "current_stage": current,
                "blocked": blocked,
                "stages_done": done_count,
                "stages_total": total,
                "stages": stages,
            }
        )
    return items


def aggregate_kpi(epics: list[dict[str, Any]]) -> dict[str, Any]:
    """全局 KPI —— 全部真实数据驱动，数据不足处带 sample 计数供前端标注。
    语义映射：任务管道指标 → Epic 工作流指标（详见交互设计对齐表）。"""
    total_events = 0
    passes = 0
    stage_fail = Counter()
    for e in epics:
        gh = e.get("gate_history") or {}
        total_events += gh.get("total", 0)
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
    blocked = sum(1 for e in epics if e.get("health") in ("red", "amber"))
    healthy = sum(1 for e in epics if e.get("health") == "green")
    running = sum(1 for e in epics if e.get("health") == "blue")
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
CONSTITUTION_FILE = ROOT / ".workflows" / "constitution.json"
ORPHAN_FEEDBACK = ROOT / "Contexts" / "决策" / "孤立反馈记录.md"

_RULE_ZH = {
    "tdd_first": "验收测试先行（外层 TDD 先红）",
    "skill_run_required": "阶段完成须输出 skill_run 反馈",
    "epic_required": "功能开发须先有 Epic",
    "traceability": "需求 AC → 测试/开发任务可追溯",
    "figma_forced": "含界面/对稿 → 强制 figma-ui skill",
    "wbs_single_truth": "WBS 单一权威源（子 Plan fenced checklist）",
}


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


def read_constitution() -> list[dict[str, Any]]:
    """读工作流宪法规则 + 判定其执行形态（enforced 硬门禁 / indexed 延迟索引）。"""
    if not CONSTITUTION_FILE.is_file():
        return []
    try:
        d = json.loads(CONSTITUTION_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    rules = []
    for r in d.get("rules", []):
        rid = str(r.get("id", ""))
        checked_by = str(r.get("checkedBy", ""))
        status = "indexed" if checked_by.startswith("deferred:") else "enforced"
        rules.append(
            {
                "id": rid,
                "title": _RULE_ZH.get(rid, rid),
                "checked_by": checked_by,
                "status": status,
                "severity": r.get("severity", ""),
            }
        )
    return rules


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
        "constitution": read_constitution(),
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
        "scope": "merge-code / ui-change / bugfix / task-split-only / computer-mgmt / client-dev",
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
            "summary": f"AC 覆盖 {coverage_pct if coverage_pct is not None else '—'}%，P0 {p0_covered}/{p0_total}",
            "count": p0_covered,
            "total": p0_total,
            "coverage_pct": coverage_pct,
            "runnable": True,
        },
        {
            "id": "integration",
            "title": "集成测试",
            "status": "not-connected",
            "summary": "尚未接入任务级集成测试命令",
            "count": 0,
            "runnable": False,
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
            "status": "ready" if p0_dev_covered else "not-connected",
            "summary": f"P0 开发覆盖 {p0_dev_covered}/{p0_total}" if p0_total else "暂无 P0 开发覆盖数据",
            "count": p0_dev_covered,
            "total": p0_total,
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
    marker = "## 四、变更日志" if "## 四、变更日志" in text else "## 变更日志"
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
    lc = data.get("lifecycle_state", "development")
    skill_map = {
        "requirement": "requirement-analyst",
        "architecture": "architecture-design-assistant",
        "development": "feature-dev-assistant",
        "test": "test-generator",
        "deploy": "deployment-assistant",
    }
    dev_plan = next((p["path"] for p in data.get("plans", []) if p.get("stage_key") == "development" and p.get("path")), None)
    if lc == "development" and dev_plan and ns:
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
