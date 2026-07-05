#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDERS = {"", "【】", "-", "—", "待补", "TODO", "todo"}


def clean_cell(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1].strip()
    return value


def split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    return [clean_cell(cell) for cell in stripped.strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def is_placeholder(value: str) -> bool:
    stripped = clean_cell(value)
    if stripped in PLACEHOLDERS:
        return True
    return bool(re.fullmatch(r"【[^】]*】", stripped))


def strip_inline_comment(line: str) -> str:
    in_quote: str | None = None
    for i, char in enumerate(line):
        if in_quote:
            if char == in_quote:
                in_quote = None
            continue
        if char in {"'", '"'}:
            in_quote = char
            continue
        if char == "#" and (i == 0 or line[i - 1] in {" ", "\t"}):
            return line[:i].rstrip()
    return line.rstrip()


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def read_frontmatter(path: str | Path) -> dict[str, str]:
    p = Path(path)
    frontmatter: dict[str, str] = {}
    in_fm = False
    seen_open = False
    for raw in p.read_text(encoding="utf-8").splitlines():
        if raw.strip() == "---":
            if not seen_open:
                seen_open = True
                in_fm = True
                continue
            if in_fm:
                break
        if not in_fm:
            continue
        if raw.startswith((" ", "\t")):
            continue
        m = re.match(r"^([^:\s][^:]*):\s*(.*?)\s*$", raw)
        if not m:
            continue
        key, value = m.groups()
        value = unquote(strip_inline_comment(value))
        frontmatter[key] = value
    return frontmatter


def read_plan_index(path: str | Path) -> dict[str, str]:
    p = Path(path)
    plans: dict[str, str] = {}
    in_plans = False
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.strip() == "---" and not in_plans:
            continue
        if re.match(r"^plans:\s*$", line):
            in_plans = True
            continue
        if in_plans and line and not line.startswith((" ", "\t")):
            break
        if not in_plans:
            continue
        m = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if not m:
            continue
        key, value = m.groups()
        value = value.split("#", 1)[0].strip().strip('"').strip("'")
        if value and value != "null":
            plans[key] = value
    return plans


def parse_ac_table(path: str | Path) -> dict[str, dict[str, str]]:
    p = Path(path)
    result: dict[str, dict[str, str]] = {}
    for line_no, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        cells = split_table_row(line)
        if len(cells) < 2 or is_separator_row(cells):
            continue
        ac_id = cells[0]
        if not re.match(r"^AC\S*$", ac_id):
            continue
        priority = ""
        for cell in reversed(cells):
            if re.fullmatch(r"P[0-9]+", cell.strip(), flags=re.IGNORECASE):
                priority = cell.strip().upper()
                break
        result[ac_id] = {"id": ac_id, "priority": priority or "P2", "line": str(line_no)}
    return result


def parse_test_map(path: str | Path) -> dict[str, list[dict[str, str]]]:
    p = Path(path)
    result: dict[str, list[dict[str, str]]] = {}
    for line_no, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        cells = split_table_row(line)
        if len(cells) < 4 or is_separator_row(cells):
            continue
        ac_id = cells[0]
        if not re.match(r"^AC\S*$", ac_id):
            continue
        case_id = cells[1]
        description = cells[3]
        if is_placeholder(case_id) or is_placeholder(description):
            continue
        result.setdefault(ac_id, []).append(
            {
                "ac": ac_id,
                "case_id": case_id,
                "type": cells[2] if len(cells) > 2 else "",
                "description": description,
                "status": cells[4] if len(cells) > 4 else "",
                "line": str(line_no),
            }
        )
    return result


def parse_dev_ac_coverage(path: str | Path) -> dict[str, list[dict[str, str]]]:
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines()
    in_section = False
    header: list[str] | None = None
    ac_index = -1
    result: dict[str, list[dict[str, str]]] = {}
    for line_no, line in enumerate(lines, 1):
        if re.match(r"^##\s+五、实施切片", line):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        cells = split_table_row(line)
        if not cells or is_separator_row(cells):
            continue
        if header is None:
            if "覆盖 AC" in cells:
                header = cells
                ac_index = cells.index("覆盖 AC")
            continue
        if ac_index < 0 or ac_index >= len(cells):
            continue
        raw_acs = cells[ac_index]
        if is_placeholder(raw_acs):
            continue
        task_id = cells[0] if cells else ""
        task_desc = " / ".join(cells[1:4]).strip(" /")
        for ac_id in re.findall(r"AC[^\s,，、;；|/]+", raw_acs):
            result.setdefault(ac_id, []).append(
                {"ac": ac_id, "task": task_id, "description": task_desc, "line": str(line_no)}
            )
    return result


def wbs_slice_status(path: str | Path, n: str | int) -> str | None:
    """WBS 切片状态的唯一权威源 = fenced `[x] N.` checklist（模板约定形态）。
    只认 fenced 内 `[标记] N. 描述` 行，不再匹配任何表格——表格首列同为数字，
    既有同一 plan 多张表的歧义（输入输出表 vs 状态表），也有跨子 Plan 同号误匹配，
    均由「切片号无法可靠定位唯一正确行」引起。统一到 fenced checklist 根治。
    返回 'x' / '~' / ' '，无匹配返回 None。"""
    p = Path(path)
    target = str(n)
    lines = p.read_text(encoding="utf-8").splitlines()

    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        m = re.match(r"^\[([ xX~])\]\s*" + re.escape(target) + r"\.\s+", line)
        if m:
            mark = m.group(1)
            return "x" if mark in {"x", "X"} else mark
    return None


def check_sections(path: str | Path, sections: list[str]) -> dict[str, list[str]]:
    """对每个 section 名判定：标题是否存在 + 标题下是否有实质内容。
    返回 {"missing": [...标题缺失], "empty": [...有标题但内容空/纯占位]}。
    标题匹配容忍序号前缀（如 '## 三、模块边界' 命中 '模块边界'）。"""
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines()

    heads: list[tuple[int, int, str]] = []  # (行号, 级别, 标题文本)
    in_fence = False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2).strip()))

    def body_has_content(start_line: int, level: int) -> bool:
        end = len(lines)
        for hl, lv, _ in heads:
            if hl > start_line and lv <= level:
                end = hl
                break
        for raw in lines[start_line + 1:end]:
            s = raw.strip()
            if not s:
                continue
            # 去掉勾选框/列表符号后判占位
            stripped = re.sub(r"^[-*]\s*\[[ xX~]\]\s*", "", s)
            stripped = re.sub(r"^[-*]\s*", "", stripped)
            if is_placeholder(stripped):
                continue
            return True
        return False

    missing: list[str] = []
    empty: list[str] = []
    for want in sections:
        hit = None
        for hl, lv, text in heads:
            if want in text:
                hit = (hl, lv)
                break
        if hit is None:
            missing.append(want)
        elif not body_has_content(hit[0], hit[1]):
            empty.append(want)
    return {"missing": missing, "empty": empty}


def main() -> int:
    parser = argparse.ArgumentParser(description="Shared parsers for workflow gate facts.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["read-frontmatter", "read-plan-index", "parse-ac-table", "parse-test-map", "parse-dev-ac-coverage"]:
        child = sub.add_parser(name)
        child.add_argument("path")
    key_cmd = sub.add_parser("read-frontmatter-key")
    key_cmd.add_argument("path")
    key_cmd.add_argument("key")
    plan_key_cmd = sub.add_parser("read-plan-key")
    plan_key_cmd.add_argument("path")
    plan_key_cmd.add_argument("key")
    wbs_cmd = sub.add_parser("wbs-slice-status")
    wbs_cmd.add_argument("path")
    wbs_cmd.add_argument("slice")
    sections_cmd = sub.add_parser("check-sections")
    sections_cmd.add_argument("path")
    sections_cmd.add_argument("sections", nargs="+")
    sections_cmd.add_argument("--msg", action="store_true", help="输出人类可读 blocker 串（缺/空章节），全通过则空")
    args = parser.parse_args()

    if args.command == "read-frontmatter":
        payload = read_frontmatter(args.path)
    elif args.command == "read-plan-index":
        payload = read_plan_index(args.path)
    elif args.command == "parse-ac-table":
        payload = parse_ac_table(args.path)
    elif args.command == "parse-test-map":
        payload = parse_test_map(args.path)
    elif args.command == "parse-dev-ac-coverage":
        payload = parse_dev_ac_coverage(args.path)
    elif args.command == "read-frontmatter-key":
        print(read_frontmatter(args.path).get(args.key, ""))
        return 0
    elif args.command == "read-plan-key":
        print(read_plan_index(args.path).get(args.key, ""))
        return 0
    elif args.command == "wbs-slice-status":
        status = wbs_slice_status(args.path, args.slice)
        if status is None:
            return 1
        print(status)
        return 0
    elif args.command == "check-sections":
        secs = args.sections
        # 容忍单个 JSON 数组参数（gate 直接透传 requiredSections，免在 bash 里拆数组）
        if len(secs) == 1 and secs[0].lstrip().startswith("["):
            try:
                secs = json.loads(secs[0])
            except Exception:
                pass
        result = check_sections(args.path, secs)
        if args.msg:
            parts = []
            if result["missing"]:
                parts.append("缺章节: " + "/".join(result["missing"]))
            if result["empty"]:
                parts.append("空章节: " + "/".join(result["empty"]))
            print(" ; ".join(parts))
        else:
            print(json.dumps(result, ensure_ascii=False))
        return 0
    else:
        raise AssertionError(args.command)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
