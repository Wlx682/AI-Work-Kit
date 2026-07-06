#!/usr/bin/env python3
"""
relations-check.py — 校验 Vault 中 frontmatter 的 relations 字段双向一致性。

用法：
  scripts/relations-check.py              校验
  scripts/relations-check.py --write-dependents  反推 dependents

零依赖。仅认 fenced frontmatter:
---
relations:
  depends_on:
    - path/to/file.md
  supersedes: []
  conflicts: []
---

规则：
- A.depends_on 含 B  ⇔  B.dependents 含 A
- A.supersedes 含 B  ⇔  B.superseded_by 含 A
- A.conflicts 含 B  ⇔  B.conflicts 含 A
- 路径必须存在
- 空数组与字段缺失等价
"""
from __future__ import annotations
import re, sys, argparse, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RELATION_KEYS = ("depends_on", "dependents", "supersedes", "superseded_by", "conflicts")

# 关系图谱只连长期文件；Plans/ 是任务临时产物（做完删），不上图谱。
# 见 关系图谱协议.md §四「不上」。指向这些前缀的 relations 目标一律报错。
NON_GRAPH_PREFIXES = ("Plans/",)


def is_non_graph_target(p: str) -> bool:
    return any(p.startswith(prefix) for prefix in NON_GRAPH_PREFIXES)


# 校验范围：仅扫这些目录的 .md
SCAN_DIRS = ["Contexts", "Templates", "Skills"]

# 忽略文件（不参与关系校验）
IGNORE_PATTERNS = [
    "Contexts/日报/",
    "Contexts/周报/",
    "Contexts/复盘/",
]

FRONTMATTER_RE = re.compile(r'\A﻿?---\s*\n(.*?)\n---\s*\n', re.S)


def strip_bom(text: str) -> str:
    return text.lstrip('﻿​')


def is_ignored(rel_path: str) -> bool:
    return any(rel_path.startswith(p) for p in IGNORE_PATTERNS)


def collect_files() -> list[Path]:
    files = []
    for d in SCAN_DIRS:
        for md in (ROOT / d).rglob("*.md"):
            rel = str(md.relative_to(ROOT))
            if is_ignored(rel):
                continue
            files.append(md)
    return files


def parse_relations(text: str) -> dict | None:
    """Returns dict of {depends_on: [...], dependents: [...], ...} or None if no relations field."""
    text = strip_bom(text)
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm = m.group(1)
    # find `relations:` block (top-level, not indented)
    rel_match = re.search(r'^relations:\s*\n((?:[ \t]+.*\n?)*)', fm, re.M)
    if not rel_match:
        return None
    block = rel_match.group(1)
    # parse keys at 2-space indent under relations:
    result = {k: [] for k in RELATION_KEYS}
    cur_key = None
    for line in block.splitlines():
        # 2-space indented key like "  depends_on:"
        km = re.match(r'^ {2}([a-z_]+):\s*(.*)$', line)
        if km:
            key, inline = km.group(1), km.group(2).strip()
            if key not in RELATION_KEYS:
                cur_key = None
                continue
            cur_key = key
            # inline `[]` empty
            if inline in ("", "[]"):
                result[key] = []
            else:
                # not supporting other inline forms; warn
                pass
            continue
        # 4+ space indent list item under current key
        lm = re.match(r'^ {4,}-\s*(.+?)\s*$', line)
        if lm and cur_key:
            val = lm.group(1).strip().strip('"').strip("'")
            if val and val != "[]":
                result[cur_key].append(val)
    return result


def write_dependents(files: list[Path], data: dict[str, dict]) -> int:
    """Rebuild dependents field for each file based on others' depends_on. Returns # files updated."""
    # Build inverted index: target -> [sources that depend_on target]
    rev_depends = {}
    rev_supersedes = {}
    for src_rel, rel in data.items():
        for tgt in rel["depends_on"]:
            rev_depends.setdefault(tgt, set()).add(src_rel)
        for tgt in rel["supersedes"]:
            rev_supersedes.setdefault(tgt, set()).add(src_rel)

    updated = 0
    for f in files:
        rel_path = str(f.relative_to(ROOT))
        if rel_path not in data:
            continue
        cur = data[rel_path]
        new_dependents = sorted(rev_depends.get(rel_path, set()))
        new_superseded_by = sorted(rev_supersedes.get(rel_path, set()))
        if cur["dependents"] == new_dependents and cur["superseded_by"] == new_superseded_by:
            continue
        # rewrite file
        text = f.read_text(encoding="utf-8")
        text_clean = strip_bom(text)
        m = FRONTMATTER_RE.match(text_clean)
        if not m:
            continue
        fm = m.group(1)
        rel_match = re.search(r'^relations:\s*\n((?:[ \t]+.*\n?)*)', fm, re.M)
        if not rel_match:
            continue
        new_fm = rebuild_relations_block(fm, new_dependents, new_superseded_by)
        new_text = "---\n" + new_fm + "\n---\n" + text_clean[m.end():]
        f.write_text(new_text, encoding="utf-8")
        updated += 1
    return updated


def rebuild_relations_block(fm: str, new_dependents: list[str], new_superseded_by: list[str]) -> str:
    """Rewrite dependents and superseded_by inside relations: block."""
    # split fm into pre-relations + relations block + post
    rel_match = re.search(r'^relations:\s*\n((?:[ \t]+.*\n?)*)', fm, re.M)
    if not rel_match:
        return fm
    block = rel_match.group(1)
    pre = fm[:rel_match.start()]
    post = fm[rel_match.end():]

    # parse the existing block as ordered key-value pairs (preserving original keys order)
    parsed = parse_block_ordered(block)
    parsed["dependents"] = new_dependents
    parsed["superseded_by"] = new_superseded_by

    # serialize
    lines = ["relations:"]
    keys_order = ["depends_on", "dependents", "supersedes", "superseded_by", "conflicts"]
    for k in keys_order:
        v = parsed.get(k, [])
        if v:
            lines.append(f"  {k}:")
            for item in v:
                lines.append(f"    - {item}")
        else:
            lines.append(f"  {k}: []")
    new_block = "\n".join(lines) + "\n"
    return pre + new_block + post


def parse_block_ordered(block: str) -> dict:
    """Parse a relations: block content into {key: [values]}."""
    result = {}
    cur_key = None
    for line in block.splitlines():
        km = re.match(r'^ {2}([a-z_]+):\s*(.*)$', line)
        if km:
            cur_key = km.group(1)
            inline = km.group(2).strip()
            if inline in ("", "[]"):
                result[cur_key] = []
            else:
                result[cur_key] = []
            continue
        lm = re.match(r'^ {4,}-\s*(.+?)\s*$', line)
        if lm and cur_key:
            val = lm.group(1).strip().strip('"').strip("'")
            if val and val != "[]":
                result.setdefault(cur_key, []).append(val)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-dependents", action="store_true", help="反推并写入 dependents / superseded_by")
    args = ap.parse_args()

    files = collect_files()
    data: dict[str, dict] = {}
    for f in files:
        rel_path = str(f.relative_to(ROOT))
        try:
            text = f.read_text(encoding="utf-8")
        except Exception as e:
            print(f"WARN: 读不了 {rel_path}: {e}", file=sys.stderr)
            continue
        rels = parse_relations(text)
        if rels is None:
            continue
        data[rel_path] = rels

    if args.write_dependents:
        updated = write_dependents(files, data)
        # re-collect after write
        data = {}
        for f in files:
            rel_path = str(f.relative_to(ROOT))
            text = f.read_text(encoding="utf-8")
            rels = parse_relations(text)
            if rels is not None:
                data[rel_path] = rels
        print(f"反推完成：{updated} 个文件更新")

    # Validate
    errors = []

    def check_path_exists(p: str, ctx: str):
        if not (ROOT / p).exists():
            errors.append(f"{ctx}: 引用文件不存在: {p}")

    def check_not_plan(p: str, ctx: str):
        if is_non_graph_target(p):
            errors.append(f"{ctx}: relations 目标是 Plans/ 临时产物，不上图谱（见 关系图谱协议 §四）: {p}")

    for src, rel in data.items():
        for key in RELATION_KEYS:
            for tgt in rel[key]:
                check_not_plan(tgt, f"{src}.{key}")
        for tgt in rel["depends_on"]:
            check_path_exists(tgt, f"{src}.depends_on")
            if tgt in data:
                if src not in data[tgt]["dependents"]:
                    errors.append(f"{src}.depends_on={tgt} 但 {tgt}.dependents 不含 {src}（跑 --write-dependents 修）")
        for tgt in rel["supersedes"]:
            check_path_exists(tgt, f"{src}.supersedes")
            if tgt in data:
                if src not in data[tgt]["superseded_by"]:
                    errors.append(f"{src}.supersedes={tgt} 但 {tgt}.superseded_by 不含 {src}")
        for tgt in rel["conflicts"]:
            check_path_exists(tgt, f"{src}.conflicts")
            if tgt in data:
                if src not in data[tgt]["conflicts"]:
                    errors.append(f"{src}.conflicts={tgt} 但 {tgt}.conflicts 不含 {src}（应对称）")

    if errors:
        print("✗ 关系图谱不一致：", file=sys.stderr)
        for e in errors:
            print(f"  · {e}", file=sys.stderr)
        sys.exit(1)
    print(f"✓ 关系图谱一致（{len(data)} 个文件参与）")


if __name__ == "__main__":
    main()
