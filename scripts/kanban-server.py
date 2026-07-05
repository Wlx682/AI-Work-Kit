#!/usr/bin/env python3
"""Local Epic kanban server — 127.0.0.1:7777 only. Stdlib only."""
from __future__ import annotations

import json
import re
import sys
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
except Exception:  # pragma: no cover - gate_parse 不可用时降级读 Epic 字面量
    _wbs_slice_status = None

RUN_DIR = ROOT / ".workflows" / "runs"
EVENT_DIR = ROOT / ".workflows" / "events"


def gate_history_for(epic_rel: str) -> dict[str, Any] | None:
    """回放该 Epic 最新 run 的门禁事件流，供看板卡片展示时间账本摘要。
    返回 {last_gate: {result, stage, at, reason}, consecutive_fails}；无事件流返回 None。"""
    if not RUN_DIR.is_dir():
        return None
    epic_stem = Path(epic_rel).stem
    runs = sorted((f for f in RUN_DIR.glob("*.run.yaml") if epic_stem in f.name), key=lambda f: f.name)
    if not runs:
        return None
    run_id = runs[-1].name[: -len(".run.yaml")]
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
        return None
    last = gate_events[-1]
    last_stage = last.get("stage")
    consecutive_fails = 0
    for ev in reversed(gate_events):
        if ev.get("stage") != last_stage or ev.get("type") != "gate_fail":
            break
        consecutive_fails += 1
    return {
        "last_gate": {
            "result": "pass" if last.get("type") == "gate_pass" else "fail",
            "stage": last_stage,
            "at": (last.get("created_at") or "")[:10],
            "reason": (last.get("reason") or "").split(";")[0].strip(),
        },
        "consecutive_fails": consecutive_fails,
    }


PLAN_STATUSES = {"草稿", "进行中", "评审中", "已采纳", "搁置", "done", "pending-change"}
SLICE_RE = re.compile(r"^(\[[ xX~]\])\s*(\d+)([a-zA-Z]?)\.?\s+(.+)$")
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

SLICE_PLAN_STAGE: dict[int, str] = {
    1: "requirement",
    2: "architecture",
    3: "development",
    4: "development",
    5: "development",
    6: "development",
    7: "development",
    8: "development",
    9: "development",
    10: "development",
    11: "test",
    12: "development",
    13: "deploy",
    14: "deploy",
    15: "development",
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
    lines = fm_raw.splitlines()
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
    }
    in_plans = False
    for line in text.splitlines():
        if line.strip() == "plans:":
            in_plans = True
            continue
        if in_plans:
            if line and not line.startswith(" ") and not line.startswith("\t"):
                break
            m = re.match(r"^\s+(\w+):\s*(.+)$", line)
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
        done = all(m == "[x]" for m in marks)
        if len(items) == 1:
            label = items[0]["label"]
        else:
            label = " · ".join(
                (f"{it['suffix']}: {it['label']}" if it['suffix'] else it['label'])
                for it in items
            )
        slices.append({"n": n, "done": done, "label": label, "line": items[0]["line"]})
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


def _derive_slice_done(
    epic_literal_done: bool, preferred_child: str | None, n: int, stage_key: str
) -> tuple[bool, str]:
    """切片完成态派生策略（防撒谎优先）：
    只有当该切片映射到 development 阶段（功能开发主 plan 按约定沿用 Epic 全局切片号）、
    且功能开发子 Plan 明确查到该号状态时，才从子 Plan 派生；
    其余阶段（需求/方案/测试/部署等，子 Plan 用局部编号，与 Epic 切片号无对应关系）
    以及查无该号时，一律回退 Epic 字面量——避免把「恰好同号但语义无关」的行误当切片状态。
    返回 (done, derived_from)，derived_from ∈ {"child-plan", "epic-literal"}。"""
    if stage_key == "development":
        status = _slice_status_in(preferred_child, n)
        if status is not None:
            return status == "x", "child-plan"
    return epic_literal_done, "epic-literal"


def scan_epic(path: Path) -> dict[str, Any]:
    fm, _, _ = read_frontmatter(path)
    rel = str(path.relative_to(ROOT))
    slices = parse_wbs_slices(path)
    wbs_table = parse_wbs_table(path)
    plans = parse_plans_block(path)
    plan_by_stage = {p["stage_key"]: p.get("path") for p in plans if p.get("path")}
    enriched: list[dict[str, Any]] = []
    for s in slices:
        n = s["n"]
        tbl = wbs_table.get(n, {})
        stage_key = SLICE_PLAN_STAGE.get(n, "development")
        child = plan_by_stage.get(stage_key)
        done, derived_from = _derive_slice_done(s["done"], child, n, stage_key)
        enriched.append(
            {
                "n": n,
                "done": done,
                "derived_from": derived_from,
                "label": s["label"],
                "title": tbl.get("title") or s["label"],
                "summary": SLICE_SUMMARY.get(n, ""),
                "skill": tbl.get("skill", ""),
                "input": tbl.get("input", ""),
                "output": tbl.get("output", ""),
                "acceptance": tbl.get("acceptance", ""),
                "related_plan": plan_by_stage.get(stage_key),
                "stage_key": stage_key,
            }
        )
    first_open = next((e["n"] for e in enriched if not e["done"]), None)
    return {
        "file": rel,
        "name": path.stem,
        "epic_id": fm.get("epic_id", ""),
        "status": fm.get("status", ""),
        "lifecycle_state": fm.get("lifecycle_state", ""),
        "p0_open": int(fm.get("p0_open", "0") or "0"),
        "repo": fm.get("repo", ""),
        "branch": fm.get("branch", ""),
        "slices": enriched,
        "plans": plans,
        "next_slice": first_open,
        "gate_history": gate_history_for(rel),
    }


def board_revision() -> str:
    epic_dir = ROOT / "Plans" / "Epic"
    if not epic_dir.is_dir():
        return "0"
    parts: list[str] = []
    for f in sorted(epic_dir.glob("*.md")):
        if f.name.startswith("."):
            continue
        st = f.stat()
        parts.append(f"{f.name}:{st.st_mtime_ns}:{st.st_size}")
    # 看板切片状态派生自子 Plan（事实源），故子 Plan 变更也须触发前端刷新。
    child_seen: set[str] = set()
    for f in sorted(epic_dir.glob("*.md")):
        if f.name.startswith("."):
            continue
        for p in parse_plans_block(f):
            rel = p.get("path")
            if not rel or rel in child_seen:
                continue
            child_seen.add(rel)
            pf = ROOT / rel if not Path(rel).is_absolute() else Path(rel)
            if pf.is_file():
                st = pf.stat()
                parts.append(f"{rel}:{st.st_mtime_ns}:{st.st_size}")
    return str(hash(tuple(parts)))


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


def board_envelope() -> dict[str, Any]:
    return {
        "revision": board_revision(),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "epics": board_payload(),
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


def toggle_slice(epic: Path, slice_n: int, done: bool, operator: str = "web") -> None:
    text = epic.read_text(encoding="utf-8")
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
    if not matches:
        raise ValueError(f"slice {slice_n} not found")
    if len(matches) > 1 or matches[0][1].group(3):
        raise ValueError(
            f"slice {slice_n} has sub-items (e.g. {slice_n}a/{slice_n}b); edit the Epic file directly"
        )
    i, m = matches[0]
    mark = "[x]" if done else "[ ]"
    lines[i] = f"{mark} {slice_n}.  {m.group(4).strip()}"
    epic.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    action = "勾选切片" if done else "取消切片"
    append_change_log(epic, action, "development", str(slice_n), operator, f"WBS {slice_n} → {'done' if done else 'open'}")


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
            idx = KANBAN_DIR / "index.html"
            if not idx.is_file():
                self._json(404, {"error": "index.html missing"})
                return
            data = idx.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/api/board":
            env = board_envelope()
            self._json(200, env)
            return
        if path == "/api/revision":
            self._json(
                200,
                {"revision": board_revision(), "updated_at": datetime.now().isoformat(timespec="seconds")},
            )
            return
        self._json(404, {"error": "not found"})

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
            if path == "/api/slice":
                rel = body.get("file", "")
                slice_n = int(body.get("slice", 0))
                done = bool(body.get("done", True))
                operator = body.get("operator", "web")
                epic = resolve_plan(rel)
                toggle_slice(epic, slice_n, done, operator)
                self._json(200, {"ok": True, "file": rel, "slice": slice_n, "done": done})
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
