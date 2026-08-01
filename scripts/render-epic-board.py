#!/usr/bin/env python3
"""
render-epic-board.py — 从「文件系统事实」派生并写回 Epic §三 WBS 看板的勾选标记。

三层架构下 Epic 是**被动数据聚合根**：§三 看板的 `[ ]/[~]/[-]/[x]` 不再手写，
而是单向从子 Plan 事实派生。每个切片的标记来源（防第三份真理源）：
  - 该切片「归属 stage」的子 Plan 若有 fenced `[N.]` checklist 行 → 直接采其状态
    （复用 gate_parse.wbs_slice_status，与 workflow-gate / kanban-server 同一读法）。
  - 否则回退到 stage 级完成度：由 workflow-gate.sh --probe 判定的 current_state
    决定该 stage 是否已过（已过=[x]，当前/未来=[ ]）。
本脚本只改每行的 `[标记]` 方括号，描述/缩进/编号一律保留。带后缀切片（6a/6b）
不自动改写（与 kanban-server.toggle_slice 拒绝子项一致），交人工维护。

用法：
  render-epic-board.py <epic.md>            # 打印派生后的 §三（dry-run，不写）
  render-epic-board.py <epic.md> --write    # 写回 Epic §三
  render-epic-board.py <epic.md> --check    # 校验：§三 与派生不一致则退出 1（供 pre-commit）

退出码：
  0 — 一致 / 写入成功 / dry-run
  1 — --check 下发现漂移（stderr 列出差异）
  2 — 基础设施失败（gate 无输出、blueprint 缺失等），不阻断（pre-commit 视为放行）
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from gate_parse import wbs_slice_status  # noqa: E402  同一权威读法

SECTION_THREE_RE = re.compile(r"(^##\s*三、.*?)(?=^##\s|\Z)", re.DOTALL | re.MULTILINE)
FENCED_LINE_RE = re.compile(r"^(\[)([ xX~-])(\]\s*)(\d+)([a-zA-Z]?)(\.\s+.*)$")


def read_fm_key(path: pathlib.Path, key: str) -> str:
    out = subprocess.run(
        ["python3", str(ROOT / "scripts" / "gate_parse.py"), "read-frontmatter-key", str(path), key],
        capture_output=True, text=True,
    )
    return out.stdout.strip()


def read_plan_key(path: pathlib.Path, key: str) -> str:
    out = subprocess.run(
        ["python3", str(ROOT / "scripts" / "gate_parse.py"), "read-plan-key", str(path), key],
        capture_output=True, text=True,
    )
    return out.stdout.strip()


def load_blueprint(workflow: str) -> dict | None:
    bp = ROOT / ".workflows" / "blueprints" / f"{workflow}.json"
    if not bp.is_file():
        return None
    return json.loads(bp.read_text(encoding="utf-8"))


def run_gate(epic: pathlib.Path, workflow: str) -> dict | None:
    out = subprocess.run(
        ["bash", str(ROOT / "scripts" / "workflow-gate.sh"),
         "--workflow", workflow, "--epic", str(epic), "--probe", "--json"],
        capture_output=True, text=True,
    )
    if out.returncode != 0 or not out.stdout.strip():
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


def resolve(path_str: str) -> pathlib.Path:
    p = pathlib.Path(path_str)
    if not p.is_absolute():
        p = ROOT / p
    if p.suffix != ".md":
        p = p.with_suffix(".md")
    return p


def build_derivation(epic: pathlib.Path):
    """返回 (slice_mark: dict[int,str], warn: str|None)。mark ∈ {'x','~',' ','-'}。"""
    workflow = read_fm_key(epic, "workflow") or "client-dev"
    bp = load_blueprint(workflow)
    if not bp:
        return None, f"blueprint 缺失: .workflows/blueprints/{workflow}.json"
    gate = run_gate(epic, workflow)
    if not gate:
        return None, f"workflow-gate.sh 无有效输出（workflow={workflow}）"

    stages = bp.get("stages", [])
    stage_order = [s.get("key") for s in stages]
    slice_stage: dict[int, str] = {}
    stage_child: dict[str, pathlib.Path] = {}
    for s in stages:
        key = s.get("key")
        for n in s.get("wbsSlices", []) or []:
            raw = str(n)
            if raw.isdigit():
                slice_stage[int(raw)] = key
        # 子 Plan 直接从 Epic frontmatter 的 plans.<epicField> 解析——不依赖 gate
        # 的 plans_found（后者在首个受阻 stage 处 break、会截断后续 stage 的子 Plan）。
        epic_field = s.get("epicField", "")
        if epic_field:
            raw = read_plan_key(epic, epic_field)
            if raw and raw != "null":
                stage_child[key] = resolve(raw)

    current_state = gate.get("current_state", "done")
    current_idx = stage_order.index(current_state) if current_state in stage_order else len(stage_order)

    marks: dict[int, str] = {}
    for n, stage_key in slice_stage.items():
        child = stage_child.get(stage_key)
        status = None
        if child and child.is_file():
            try:
                status = wbs_slice_status(child, n)
            except Exception:
                status = None
        if status is not None:
            marks[n] = "x" if status in ("x", "X") else status
        else:
            stage_done = stage_key in stage_order and stage_order.index(stage_key) < current_idx
            marks[n] = "x" if stage_done else " "
    return marks, None


def render_section(section: str, marks: dict[int, str]) -> tuple[str, list[str]]:
    """按 marks 重写 §三 fenced 行的方括号；返回 (新 section, 变更描述列表)。"""
    changes: list[str] = []
    out_lines: list[str] = []
    in_fence = False
    for line in section.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        m = FENCED_LINE_RE.match(line) if in_fence else None
        if not m:
            out_lines.append(line)
            continue
        suffix = m.group(5)
        n = int(m.group(4))
        if suffix or n not in marks:
            out_lines.append(line)  # 子项/未知切片：不动
            continue
        old_mark = m.group(2).lower()
        old_mark = " " if old_mark == " " else ("x" if old_mark == "x" else old_mark)
        new_mark = marks[n]
        if old_mark != new_mark:
            changes.append(f"#{n}: [{m.group(2)}] → [{new_mark}]")
        out_lines.append(f"{m.group(1)}{new_mark}{m.group(3)}{m.group(4)}{m.group(6)}")
    return "\n".join(out_lines), changes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("epic", help="Plans/Epic/xxx.md")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="写回 Epic §三")
    mode.add_argument("--check", action="store_true", help="校验一致性（漂移退出 1，供 pre-commit）")
    args = ap.parse_args()

    epic = pathlib.Path(args.epic).resolve()
    if not epic.is_file():
        print(f"WARN:render-epic-board: Epic 不存在: {args.epic}", file=sys.stderr)
        return 2

    content = epic.read_text(encoding="utf-8")
    sec_m = SECTION_THREE_RE.search(content)
    if not sec_m:
        print(f"WARN:render-epic-board: 未找到 §三 章节: {epic.name}", file=sys.stderr)
        return 2

    marks, warn = build_derivation(epic)
    if warn:
        print(f"WARN:render-epic-board: {warn}（跳过，不阻断）", file=sys.stderr)
        return 2

    section = sec_m.group(1)
    new_section, changes = render_section(section, marks)

    if args.check:
        if changes:
            print(f"BLOCKED:render-epic-board: {epic.name} §三 看板与子 Plan 事实漂移，需刷新：", file=sys.stderr)
            for c in changes:
                print(f"  {c}", file=sys.stderr)
            print(f"  修复：python3 scripts/render-epic-board.py {args.epic} --write", file=sys.stderr)
            return 1
        print(f"OK:render-epic-board: {epic.name} §三 与子 Plan 一致")
        return 0

    if args.write:
        if not changes:
            print(f"OK:render-epic-board: {epic.name} §三 已是最新，无需改写")
            return 0
        epic.write_text(content[:sec_m.start(1)] + new_section + content[sec_m.end(1):], encoding="utf-8")
        print(f"OK:render-epic-board: 已写回 {epic.name} §三（{len(changes)} 处）：")
        for c in changes:
            print(f"  {c}")
        return 0

    # dry-run
    print(new_section)
    if changes:
        print(f"\n# 将改写 {len(changes)} 处（--write 落盘）：", file=sys.stderr)
        for c in changes:
            print(f"#   {c}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
