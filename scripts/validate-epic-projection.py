#!/usr/bin/env python3
"""
validate-epic-projection.py — 校验 Epic 看板 与 子 plan WBS 表 的状态/备注一致性

用法：
  python3 scripts/validate-epic-projection.py <plan.md>
  python3 scripts/validate-epic-projection.py --require <plan.md>

路由：
  - Plans/Epic/*.md           → 以自身为 Epic，扫 frontmatter plans.* 列出的所有子 plan
  - 其它带 epic: 字段的 plan → 解析 epic 路径，回扫所有子 plan
  - 其它 plan                → 跳过（输出 OK）

校验规则（详见 Contexts/决策/母子plan投影规则.md）：
  A. Epic 行 `[x]` 但子 plan 聚合非 done
  B. Epic 行 `[ ]` 但子 plan 聚合非 todo（已有完成项）
  C. Epic 行 `[~]` 但子 plan 聚合 == done 或 == todo
  D. Epic 备注含 ✅/完成/done 字眼但子 plan 未全完成（半完成压扁）
  E. 子 plan 拆出 a/b/c 分项但 Epic 既未拆行也无『分项见 [[子 plan]] §X』指针

退出码：
  0 — 校验通过 / 本路径非强制且无 epic 链接
  1 — 任一规则违反 或 强制路径下结构缺失
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

EPIC_LINE_RE = re.compile(r"^\s*\[([ x~])\]\s+(\d+)([a-z]?)\s*[\.\)、\s]+\s*(.*)$")
SUBPLAN_ROW_RE = re.compile(r"^\|\s*(\d+)([a-z]?)\s*\|")
DONE_KEYWORDS_RE = re.compile(r"(✅|✓|完成|done|DONE)")
POINTER_RE = re.compile(r"分项见|参见\s*\[\[|\[\[[^\]]+\]\]\s*§")
SECTION_THREE_RE = re.compile(r"^##\s*三、.*?(?=^##\s)", re.DOTALL | re.MULTILINE)


def classify_substate(text: str) -> str:
    t = text.strip().replace("**", "")
    if t in {"", "—", "-"}:
        return "todo"
    if t in {"✅", "✓", "完成", "已完成", "done", "Done", "DONE", "OK"}:
        return "done"
    if t in {"⬜", "未开始", "待办", "TODO", "todo"}:
        return "todo"
    partial_markers = ("部分", "进行中", "骨架", "待截图", "待走查", "待联调", "WIP", "/")
    if any(k in t for k in partial_markers):
        return "partial"
    if "✅" in t:
        return "done"
    return "partial"


def aggregate(sub_rows: list[tuple[str, str]]) -> str:
    states = [s for _, s in sub_rows]
    if not states:
        return "unknown"
    if all(s == "done" for s in states):
        return "done"
    if all(s == "todo" for s in states):
        return "todo"
    return "partial"


def read_fm(content: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not m:
        return {}
    fm: dict = {}
    plans: dict = {}
    cur_subtree: str | None = None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        top = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if top:
            key, val = top.group(1), top.group(2).strip()
            if key == "plans" and not val:
                cur_subtree = "plans"
                fm["plans"] = plans
            else:
                cur_subtree = None
                fm[key] = val
            continue
        if cur_subtree == "plans":
            sub = re.match(r"^  ([A-Za-z_]+):\s*(.*)$", line)
            if sub:
                v = sub.group(2).strip()
                if v and v != "null":
                    plans[sub.group(1)] = v
    return fm


def resolve(path_str: str) -> pathlib.Path:
    p = pathlib.Path(path_str)
    if not p.is_absolute():
        p = ROOT / p
    if p.suffix != ".md":
        p = p.with_suffix(".md")
    return p


def section_three(content: str) -> str:
    m = SECTION_THREE_RE.search(content)
    return m.group(0) if m else ""


def parse_epic_board(content: str) -> list[tuple[str, str, str, str]]:
    sec = section_three(content)
    if not sec:
        return []
    rows: list[tuple[str, str, str, str]] = []
    in_code = False
    for line in sec.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            continue
        m = EPIC_LINE_RE.match(line)
        if not m:
            continue
        state = {"x": "done", " ": "todo", "~": "partial"}.get(m.group(1), "unknown")
        rows.append((m.group(2), m.group(3), state, m.group(4).strip()))
    return rows


def parse_subplan_wbs(content: str) -> dict[str, list[tuple[str, str]]]:
    sec = section_three(content)
    if not sec:
        return {}
    agg: dict[str, list[tuple[str, str]]] = {}
    for line in sec.splitlines():
        if not line.startswith("|"):
            continue
        m = SUBPLAN_ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 2:
            continue
        substate = classify_substate(cells[-1])
        agg.setdefault(m.group(1), []).append((m.group(2), substate))
    return agg


def fail(msg: str) -> None:
    print(f"BLOCKED:epic-projection:{msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"WARN:epic-projection:{msg}", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("plan", help="plan 文件路径")
    ap.add_argument("--require", action="store_true", help="本路径强制要求校验通过")
    args = ap.parse_args()

    plan_path = pathlib.Path(args.plan).resolve()
    if not plan_path.exists():
        fail(f"plan 文件不存在: {args.plan}")
    content = plan_path.read_text(encoding="utf-8")
    fm = read_fm(content)

    epic_path: pathlib.Path | None = None
    if "/Plans/Epic/" in str(plan_path):
        epic_path = plan_path
    elif fm.get("epic"):
        epic_path = resolve(fm["epic"])
        if not epic_path.exists():
            fail(f"epic plan 不存在: {fm['epic']}")

    if epic_path is None:
        if args.require:
            fail("本路径强制要求 epic 链接，但 plan 不在 Plans/Epic/ 也无 epic: 字段")
        print("OK:epic-projection 跳过（非 Epic / 无 epic: 字段）")
        sys.exit(0)

    epic_content = epic_path.read_text(encoding="utf-8")
    epic_fm = read_fm(epic_content)
    epic_rows = parse_epic_board(epic_content)
    if not epic_rows:
        fail(
            f"Epic 看板未识别到任何 `[ ]/[x]/[~]` 勾选行（§三 是否含代码块？）：{epic_path.name}"
        )

    plans_map = epic_fm.get("plans") or {}
    if not plans_map:
        fail(
            f"Epic frontmatter 缺 plans: 子字段映射（requirement/architecture/development/test/deploy）：{epic_path.name}"
        )

    sub_wbs_all: dict[str, list[tuple[str, str]]] = {}
    for kind, sub_link in plans_map.items():
        sub_p = resolve(sub_link)
        if not sub_p.exists():
            warn(f"plans.{kind} 子 plan 不存在: {sub_link}")
            continue
        sub_content = sub_p.read_text(encoding="utf-8")
        for num, items in parse_subplan_wbs(sub_content).items():
            sub_wbs_all.setdefault(num, []).extend(items)

    epic_has_subitem: dict[str, set[str]] = {}
    for num, suffix, _, _ in epic_rows:
        if suffix:
            epic_has_subitem.setdefault(num, set()).add(suffix)

    errors: list[str] = []

    for num, suffix, e_state, notes in epic_rows:
        sub = sub_wbs_all.get(num, [])
        if not sub:
            continue

        if suffix:
            target = [(sf, st) for sf, st in sub if sf == suffix]
            if not target:
                errors.append(
                    f"#{num}{suffix} Epic 拆出此分项但子 plan 同编号同后缀缺失"
                )
                continue
            sub_state = target[0][1]
            if e_state == "done" and sub_state != "done":
                errors.append(f"#{num}{suffix} Epic=[x] 但子 plan 状态={sub_state}")
            elif e_state == "todo" and sub_state == "done":
                errors.append(f"#{num}{suffix} Epic=[ ] 但子 plan 状态=done")
            elif e_state == "partial" and sub_state in ("done", "todo"):
                errors.append(
                    f"#{num}{suffix} Epic=[~] 但子 plan 状态={sub_state}（应使用 [x] 或 [ ]）"
                )
            if DONE_KEYWORDS_RE.search(notes) and sub_state != "done":
                errors.append(
                    f"#{num}{suffix} Epic 备注含完成态字眼但子 plan 未完成；备注={notes!r}"
                )
            continue

        agg_state = aggregate(sub)
        sub_suffixes = sorted({sf for sf, _ in sub if sf})
        epic_subs = epic_has_subitem.get(num, set())

        if e_state == "done" and agg_state != "done":
            errors.append(
                f"#{num} Epic=[x] 但子 plan 聚合={agg_state}（未全部完成）"
            )
        if e_state == "todo" and agg_state != "todo":
            errors.append(
                f"#{num} Epic=[ ] 但子 plan 聚合={agg_state}（已有完成或进行中项，应升级为 [~] 或 [x]）"
            )
        if e_state == "partial" and agg_state in ("done", "todo"):
            errors.append(
                f"#{num} Epic=[~] 但子 plan 聚合={agg_state}（应使用 [x] 或 [ ]）"
            )
        if DONE_KEYWORDS_RE.search(notes) and agg_state != "done":
            errors.append(
                f"#{num} Epic 备注含完成态字眼但子 plan 未完成；备注={notes!r}"
            )
        if sub_suffixes and not epic_subs and not POINTER_RE.search(notes):
            errors.append(
                f"#{num} 子 plan 拆出分项 {sub_suffixes} 但 Epic 既无 #{num}a/b/... 行也无『分项见 [[子 plan]] §X』指针"
            )

    if errors:
        for e in errors:
            print(f"BLOCKED:epic-projection:{e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"OK:epic-projection 通过 (epic={epic_path.name}, sub_plans={len(plans_map)}, epic_rows={len(epic_rows)})"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
