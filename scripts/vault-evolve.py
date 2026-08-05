#!/usr/bin/env python3
"""
vault-evolve.py — Vault 月度进化中央调度脚本

聚合 6 个进化子任务的输出为一份统一月度报告：
  §1 反馈聚合（调用 feedback-aggregate.py）
  §2 业务仓漂移（调用 drift-scan.py）
  §3 关系图谱（调用 relations-check.py）
  §4 Contexts 老化扫描（本脚本实现）
  §5 死链巡逻（本脚本实现）
  §6 文档脚本引用一致性（调用 doc-script-refs-check.py）

用法：
  scripts/vault-evolve.py                       # 跑全套 + 写月度报告
  scripts/vault-evolve.py --dry-run             # 输出到 stdout
  scripts/vault-evolve.py --month 2026-06       # 指定月份
  scripts/vault-evolve.py --only aging          # 单跑一项（调试）
  scripts/vault-evolve.py --skip drift          # 跳过某项
  scripts/vault-evolve.py --aging-days 180      # 老化阈值（默认 90）

零依赖。月度 launchd: scripts/com.aiworkkit.vault-evolve.plist
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

SUBTASKS = ["feedback", "drift", "relations", "aging", "links", "docrefs"]

# 老化扫描排除目录（与 relations-check.py 的 IGNORE_PATTERNS 一致）
AGING_IGNORE = [
    "Contexts/日报/",
    "Contexts/周报/",
    "Contexts/复盘/",
    "Contexts/分享/",
]

# 死链扫描排除模式（占位符 / 目录引用 / 示例符号）
LINK_SKIP_PATTERNS = [
    re.compile(r"\{\{.*\}\}"),       # Templater {{date}}
    re.compile(r"^【.*】$"),          # 模板占位 【xxx】
    re.compile(r"^[A-Za-z]+/$"),     # 目录引用 Plans/ Templates/
    re.compile(r"xxx"),              # 模板示例占位 xxx-子任务...
    re.compile(r"[…]"),              # 中文省略号示例
    re.compile(r"\.\.\."),           # 英文省略号示例
]


# ===== 子进程辅助 =====

def run_subprocess(args: list[str]) -> tuple[bool, str]:
    """Run a subcommand, return (success, stdout+stderr)."""
    try:
        r = subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode == 0, out
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        return False, f"[exec error] {e}"


def strip_frontmatter(text: str) -> str:
    """Drop leading --- ... --- block so embedded outputs don't double-frontmatter."""
    m = re.match(r"^---\s*\n.*?\n---\s*\n", text, re.DOTALL)
    return text[m.end():] if m else text


# ===== §1 反馈聚合（嵌入） =====

def run_feedback(month: str) -> str:
    ok, out = run_subprocess(["python3", str(SCRIPTS / "feedback-aggregate.py"), "--dry-run", "--month", month])
    if not ok:
        return f"⚠️ feedback-aggregate 执行失败\n\n```\n{out}\n```"
    return strip_frontmatter(out)


# ===== §2 业务仓漂移（嵌入） =====

def run_drift() -> str:
    ok, out = run_subprocess(["python3", str(SCRIPTS / "drift-scan.py"), "--dry-run"])
    if not ok:
        return f"⚠️ drift-scan 执行失败\n\n```\n{out}\n```"
    return strip_frontmatter(out)


# ===== §3 关系图谱（嵌入） =====

def run_relations() -> str:
    ok, out = run_subprocess(["python3", str(SCRIPTS / "relations-check.py")])
    status = "✓ 一致" if ok else "✗ 不一致"
    return f"**结果**：{status}\n\n```\n{out.strip()}\n```\n"


# ===== §6 文档脚本引用一致性 =====

def run_docrefs() -> str:
    ok, out = run_subprocess(["python3", str(SCRIPTS / "doc-script-refs-check.py")])
    status = "✓ 一致" if ok else "✗ 有死引用"
    return f"**结果**：{status}\n\n```\n{out.strip()}\n```\n"


# ===== §4 Contexts 老化扫描 =====

def is_aging_ignored(rel_path: str) -> bool:
    return any(rel_path.startswith(p) for p in AGING_IGNORE)


def parse_frontmatter_dependents(text: str) -> int:
    """Count items under relations.dependents in frontmatter. Returns -1 if no relations field."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return -1
    fm = m.group(1)
    rel_m = re.search(r"^relations:\s*\n((?:[ \t]+.*\n?)*)", fm, re.M)
    if not rel_m:
        return -1
    block = rel_m.group(1)
    deps_m = re.search(r"^  dependents:\s*(.*)\n((?:    .*\n?)*)", block, re.M)
    if not deps_m:
        return 0
    inline = deps_m.group(1).strip()
    if inline in ("[]", "") and not deps_m.group(2).strip():
        return 0
    items = re.findall(r"^    -\s+\S", deps_m.group(2), re.M)
    return len(items)


def count_skill_run_refs() -> Counter:
    """Count how many times each Contexts path appears in any skill_run.contexts_used as utility=high."""
    counter: Counter = Counter()
    for p in (ROOT / "Plans").rglob("*.md"):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for block in re.finditer(r"```yaml\s*\n(.*?)\n```", text, re.DOTALL):
            body = block.group(1)
            if not re.match(r"^\s*skill_run\s*:", body):
                continue
            for path_match in re.finditer(r"^      path:\s*(.+?)\s*$", body, re.M):
                # only count when nearby utility line is high
                pass
            current_path = None
            for line in body.splitlines():
                pm = re.match(r"^      path:\s*(.+?)\s*$", line)
                if pm:
                    current_path = pm.group(1).strip().strip('"').strip("'")
                    continue
                um = re.match(r"^      utility:\s*(.+?)\s*$", line)
                if um and current_path:
                    if um.group(1).strip() == "high":
                        counter[current_path] += 1
                    current_path = None
    orphan = ROOT / "进化" / "孤立反馈记录.md"
    if orphan.exists():
        text = orphan.read_text(encoding="utf-8")
        current_path = None
        for line in text.splitlines():
            pm = re.match(r"^      path:\s*(.+?)\s*$", line)
            if pm:
                current_path = pm.group(1).strip().strip('"').strip("'")
                continue
            um = re.match(r"^      utility:\s*(.+?)\s*$", line)
            if um and current_path:
                if um.group(1).strip() == "high":
                    counter[current_path] += 1
                current_path = None
    return counter


def run_aging(threshold_days: int) -> str:
    refs = count_skill_run_refs()
    today = datetime.now()
    cutoff_yellow = today - timedelta(days=threshold_days)
    cutoff_red = today - timedelta(days=threshold_days * 2)

    red, yellow = [], []
    for f in (ROOT / "Contexts").rglob("*.md"):
        rel = str(f.relative_to(ROOT))
        if is_aging_ignored(rel):
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        deps = parse_frontmatter_dependents(text)
        ref_count = refs.get(rel, 0)

        if mtime < cutoff_red and ref_count == 0 and deps <= 0:
            red.append((rel, mtime, ref_count, deps))
        elif mtime < cutoff_yellow and ref_count == 0:
            yellow.append((rel, mtime, ref_count, deps))

    L = [
        f"**老化阈值**：mtime > {threshold_days} 天（红：> {threshold_days * 2} 天 + 引用 0 + dependents 0）",
        f"**统计**：🔴 {len(red)} 条 · 🟡 {len(yellow)} 条",
        "",
    ]
    if red:
        L += ["### 🔴 强候选删除/合并", "", "| 路径 | mtime | high 引用 (90d) | dependents |", "|------|-------|----------------|------------|"]
        for rel, mt, rc, dp in sorted(red, key=lambda x: x[1]):
            L.append(f"| `{rel}` | {mt.strftime('%Y-%m-%d')} | {rc} | {dp if dp >= 0 else '—'} |")
        L.append("")
    if yellow:
        L += ["### 🟡 弱候选 review", "", "| 路径 | mtime | high 引用 (90d) | dependents |", "|------|-------|----------------|------------|"]
        for rel, mt, rc, dp in sorted(yellow, key=lambda x: x[1]):
            L.append(f"| `{rel}` | {mt.strftime('%Y-%m-%d')} | {rc} | {dp if dp >= 0 else '—'} |")
        L.append("")
    if not red and not yellow:
        L.append("（无候选 — 所有 Contexts 仍活跃或有依赖）")
    return "\n".join(L) + "\n"


# ===== §5 死链巡逻 =====

WIKILINK_RE = re.compile(r"(?<!\!)\[\[([^\]]+)\]\]")
EMBED_RE = re.compile(r"!\[\[([^\]]+)\]\]")


def should_skip_link(target: str) -> bool:
    return any(p.search(target) for p in LINK_SKIP_PATTERNS)


def build_file_index() -> tuple[set[str], dict[str, list[str]]]:
    """Return (all_relpaths_without_ext, basename → list[relpaths])."""
    paths = set()
    by_name: dict[str, list[str]] = defaultdict(list)
    for f in ROOT.rglob("*.md"):
        rel = str(f.relative_to(ROOT))
        if rel.startswith(".") or rel.startswith("Plans/.archive"):
            continue
        paths.add(rel[:-3])  # strip .md
        paths.add(rel)
        by_name[f.stem].append(rel)
    return paths, by_name


def normalize_link_target(raw: str) -> str:
    """Strip alias (Note|alias), section (Note#Heading), block (Note^id), strip .md."""
    s = raw.split("|", 1)[0]
    s = s.split("#", 1)[0]
    s = s.split("^", 1)[0]
    s = s.strip()
    if s.endswith(".md"):
        s = s[:-3]
    return s


def strip_code_regions(text: str) -> str:
    """Replace fenced code blocks and inline backticks with spaces (preserve newlines/offsets)."""
    text = re.sub(
        r"(```|~~~)[\s\S]*?\1",
        lambda m: re.sub(r"[^\n]", " ", m.group(0)),
        text,
    )
    text = re.sub(
        r"`[^`\n]*`",
        lambda m: " " * len(m.group(0)),
        text,
    )
    return text


def run_links() -> str:
    paths, by_name = build_file_index()
    broken: list[dict] = []
    for f in ROOT.rglob("*.md"):
        rel = str(f.relative_to(ROOT))
        if rel.startswith(".") or rel.startswith("Plans/.archive"):
            continue
        try:
            raw_text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        text = strip_code_regions(raw_text)
        for m in WIKILINK_RE.finditer(text):
            raw = m.group(1).strip()
            if should_skip_link(raw):
                continue
            target = normalize_link_target(raw)
            if not target:
                continue
            if target in paths or f"{target}.md" in paths:
                continue
            base = target.split("/")[-1]
            if base in by_name and len(by_name[base]) >= 1:
                continue
            # broken
            line_no = text[: m.start()].count("\n") + 1
            broken.append({"from": rel, "line": line_no, "target": raw})

    if not broken:
        return "✓ 无死链。\n"

    by_source: dict[str, list[dict]] = defaultdict(list)
    for b in broken:
        by_source[b["from"]].append(b)

    L = [f"**统计**：{len(broken)} 条死链，分布在 {len(by_source)} 个文件", ""]
    L += ["| 来源 | 行 | 目标 |", "|------|-----|------|"]
    for src in sorted(by_source.keys()):
        for b in by_source[src]:
            L.append(f"| `{src}` | {b['line']} | `[[{b['target']}]]` |")
    return "\n".join(L) + "\n"


# ===== 报告渲染 =====

def render(month: str, sections: dict[str, str]) -> str:
    L = [
        "---",
        "tags: [复盘, Vault进化, 自动生成]",
        f"date: {month}-01",
        "status: 待 review",
        "---",
        "",
        f"# Vault 进化报告 — {month}",
        "",
        f"> 由 `scripts/vault-evolve.py` 自动生成 · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "> 月度复盘消费此报告。每节末有「Review 决策」位置，处置后追加日期 + 决定。",
        "",
    ]
    titles = {
        "feedback": "一、反馈聚合（utility=high / 冷却 / 漂移 / 补全候选）",
        "drift": "二、业务仓漂移检测",
        "relations": "三、关系图谱一致性",
        "aging": "四、Contexts 老化扫描",
        "links": "五、死链巡逻",
        "docrefs": "六、文档脚本引用一致性",
    }
    for key in SUBTASKS:
        if key not in sections:
            continue
        L += [f"## {titles[key]}", "", sections[key], ""]

    L += [
        "---",
        "",
        "## 六、本月 Review 决策",
        "",
        "> review 后在此追加：日期 + 每节处置摘要（删 / 合并 / 修 / 新建 / 保留）。",
        "",
    ]
    return "\n".join(L) + "\n"


# ===== 主入口 =====

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--month", default=date.today().strftime("%Y-%m"), help="YYYY-MM（默认本月）")
    ap.add_argument("--dry-run", action="store_true", help="输出到 stdout 不写文件")
    ap.add_argument("--only", choices=SUBTASKS, help="只跑指定子任务")
    ap.add_argument("--skip", choices=SUBTASKS, action="append", default=[], help="跳过指定子任务（可多次）")
    ap.add_argument("--aging-days", type=int, default=90, help="老化阈值天数（默认 90）")
    args = ap.parse_args()

    to_run = [args.only] if args.only else [k for k in SUBTASKS if k not in args.skip]

    sections: dict[str, str] = {}
    print(f"→ vault-evolve · 月份={args.month} · 子任务={','.join(to_run)}", file=sys.stderr)
    for key in to_run:
        print(f"  跑 {key} ...", file=sys.stderr)
        if key == "feedback":
            sections[key] = run_feedback(args.month)
        elif key == "drift":
            sections[key] = run_drift()
        elif key == "relations":
            sections[key] = run_relations()
        elif key == "aging":
            sections[key] = run_aging(args.aging_days)
        elif key == "links":
            sections[key] = run_links()
        elif key == "docrefs":
            sections[key] = run_docrefs()

    text = render(args.month, sections)

    if args.dry_run:
        sys.stdout.write(text)
        return

    out_path = ROOT / "Contexts" / "决策" / f"Vault进化报告-{args.month}.md"
    out_path.write_text(text, encoding="utf-8")
    print(f"✓ 已生成 {out_path.relative_to(ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
