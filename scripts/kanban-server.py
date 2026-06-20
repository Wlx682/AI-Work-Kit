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

PLAN_STATUSES = {"草稿", "进行中", "评审中", "已采纳", "搁置", "done", "pending-change"}
SLICE_RE = re.compile(r"^(\[[ xX]\])\s*(\d+)\.\s*(.+)$")


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
    slices: list[dict[str, Any]] = []
    for line in text.splitlines():
        if line.strip() == "```":
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        m = SLICE_RE.match(line)
        if not m:
            continue
        mark, num, label = m.group(1), int(m.group(2)), m.group(3).strip()
        slices.append({"n": num, "done": mark.lower() == "[x]", "label": label, "line": line})
    return slices


def scan_epic(path: Path) -> dict[str, Any]:
    fm, _, _ = read_frontmatter(path)
    rel = str(path.relative_to(ROOT))
    slices = parse_wbs_slices(path)
    plans = parse_plans_block(path)
    first_open = next((s["n"] for s in slices if not s["done"]), None)
    return {
        "file": rel,
        "name": path.stem,
        "epic_id": fm.get("epic_id", ""),
        "status": fm.get("status", ""),
        "lifecycle_state": fm.get("lifecycle_state", ""),
        "p0_open": int(fm.get("p0_open", "0") or "0"),
        "repo": fm.get("repo", ""),
        "branch": fm.get("branch", ""),
        "slices": [{"n": s["n"], "done": s["done"], "label": s["label"]} for s in slices],
        "plans": plans,
        "next_slice": first_open,
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
    changed = False
    for i, line in enumerate(lines):
        if line.strip() == "```":
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        m = SLICE_RE.match(line)
        if not m or int(m.group(2)) != slice_n:
            continue
        mark = "[x]" if done else "[ ]"
        lines[i] = f"{mark} {slice_n}.  {m.group(3).strip()}"
        changed = True
        break
    if not changed:
        raise ValueError(f"slice {slice_n} not found")
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
