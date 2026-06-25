#!/usr/bin/env python3
"""
doc-script-refs-check.py — 校验 *.md 中提到的 scripts/xxx.{sh,py,js} 都真实存在。

防止「文档说 feedback-aggregate.sh，实际脚本是 .py」这类扩展名漂移。

用法：
  scripts/doc-script-refs-check.py                   # 全 vault 扫，有漂移则 exit 1
  scripts/doc-script-refs-check.py PATH [PATH ...]   # 只检查指定 md 文件（pre-gate 用）
  scripts/doc-script-refs-check.py --quiet           # 仅在有问题时输出

零依赖。代码块/反引号内外都扫（因为漂移在 bash 命令里同样常见）。
"""
from __future__ import annotations
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent

# 仅匹配文件名段（不含路径分隔符），避免误抓 scripts/kanban/ 这类目录引用
SCRIPT_REF_RE = re.compile(r'scripts/([A-Za-z0-9_\-\.]+\.(?:sh|py|js))')

SKIP_PARTS = {".git", "node_modules", "__pycache__", ".obsidian"}
SKIP_PREFIXES = ("Plans/.archive/",)


def iter_md(targets: list[Path] | None) -> list[Path]:
    if targets:
        return [t for t in targets if t.suffix == ".md" and t.exists()]
    files = []
    for p in ROOT.rglob("*.md"):
        rel = p.relative_to(ROOT)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if str(rel).startswith(SKIP_PREFIXES):
            continue
        files.append(p)
    return files


def real_scripts() -> set[str]:
    s = set()
    sdir = ROOT / "scripts"
    if not sdir.exists():
        return s
    for f in sdir.iterdir():
        if f.is_file() and f.suffix in (".sh", ".py", ".js"):
            s.add(f.name)
    return s


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("paths", nargs="*", help="只检查这些 md 文件；不传则全 vault 扫")
    ap.add_argument("--quiet", action="store_true", help="仅在有问题时输出")
    args = ap.parse_args()

    targets = [Path(p) if Path(p).is_absolute() else (ROOT / p) for p in args.paths] if args.paths else None

    real = real_scripts()
    broken: dict[str, list[tuple[int, str]]] = defaultdict(list)
    n_refs = 0

    for f in iter_md(targets):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in SCRIPT_REF_RE.finditer(line):
                n_refs += 1
                name = m.group(1)
                if name not in real:
                    try:
                        rel = str(f.relative_to(ROOT))
                    except ValueError:
                        rel = str(f)
                    broken[rel].append((i, name))

    n_broken = sum(len(v) for v in broken.values())
    if not broken:
        if not args.quiet:
            scope = "指定文件" if targets else f"vault（{len(real)} 个脚本被引用 {n_refs} 次）"
            print(f"✓ 文档脚本引用一致（{scope}）")
        return 0

    print(f"✗ 文档引用了 {n_broken} 处不存在的 scripts/* 路径，分布 {len(broken)} 个文件：", file=sys.stderr)
    for src in sorted(broken):
        for line_no, name in broken[src]:
            print(f"  · {src}:{line_no}  scripts/{name}", file=sys.stderr)
    print("\n修法：要么 mv 脚本到引用名，要么改文档与实际扩展名一致。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
