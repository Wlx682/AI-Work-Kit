#!/usr/bin/env python3
"""
drift-scan.py — 扫描 Contexts/ 中 frontmatter 的 verified_against 字段，
与业务仓 HEAD commit 对比，输出漂移报告。

用法：
  scripts/drift-scan.py                       # 写到 Contexts/决策/漂移报告-YYYY-WW.md
  scripts/drift-scan.py --dry-run             # 输出到 stdout
  scripts/drift-scan.py --projects PATH       # 自定义 projects.list 路径

零依赖。schema：见 Contexts/决策/Contexts漂移检测协议.md
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_PROJECTS = pathlib.Path.home() / ".config" / "aiworkkit" / "projects.list"


def load_projects(path: pathlib.Path) -> dict[str, str]:
    """读 projects.list → {identifier: abs_path}"""
    if not path.exists():
        return {}
    projects: dict[str, str] = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.split("#", 1)[0].strip()
        if not ln or "=" not in ln:
            continue
        ident, _, p = ln.partition("=")
        projects[ident.strip()] = p.strip()
    return projects


def repo_head(repo_path: str) -> str | None:
    """git rev-parse HEAD"""
    if not (pathlib.Path(repo_path) / ".git").exists():
        return None
    try:
        out = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def extract_verified_against(content: str) -> list[dict]:
    """从 md 文件 frontmatter 中提取 verified_against 字段，归一为 list[dict]。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not m:
        return []
    fm_lines = m.group(1).splitlines()
    n = len(fm_lines)

    start = None
    for i, ln in enumerate(fm_lines):
        if re.match(r"^verified_against\s*:\s*$", ln):
            start = i + 1
            break
    if start is None:
        return []

    items: list[dict] = []
    current: dict | None = None

    for j in range(start, n):
        line = fm_lines[j]
        if not line.strip():
            continue
        if not line.startswith(" "):
            break

        m = re.match(r"^  -\s+(\w+)\s*:\s*(.*)$", line)
        if m:
            if current:
                items.append(current)
            current = {m.group(1): _unquote(m.group(2))}
            continue

        m = re.match(r"^    (\w+)\s*:\s*(.*)$", line)
        if m and current is not None:
            current[m.group(1)] = _unquote(m.group(2))
            continue

        m = re.match(r"^  (\w+)\s*:\s*(.*)$", line)
        if m:
            if current is None:
                current = {}
            current[m.group(1)] = _unquote(m.group(2))
            continue

    if current:
        items.append(current)
    return items


def commits_match(recorded: str, current: str) -> bool:
    if not recorded or not current:
        return False
    n = min(len(recorded), len(current))
    return recorded[:n].lower() == current[:n].lower()


def scan() -> dict:
    """返回 {scanned, with_field, drifts, missing_repo, head_failed, projects}"""
    projects_path = pathlib.Path(os.environ.get("AIWORKKIT_PROJECTS", DEFAULT_PROJECTS))
    projects = load_projects(projects_path)

    project_heads: dict[str, str] = {}
    head_failed: list[str] = []
    for ident, p in projects.items():
        h = repo_head(p)
        if h:
            project_heads[ident] = h
        else:
            head_failed.append(ident)

    scanned = 0
    with_field = 0
    drifts: list[dict] = []
    missing_repo: list[dict] = []

    for f in (ROOT / "Contexts").rglob("*.md"):
        scanned += 1
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        items = extract_verified_against(text)
        if not items:
            continue
        with_field += 1
        rel = str(f.relative_to(ROOT))
        for item in items:
            repo = item.get("repo")
            commit = str(item.get("commit", ""))
            if not repo or not commit:
                continue
            if repo not in project_heads:
                missing_repo.append({"file": rel, "repo": repo, "recorded": commit})
                continue
            current = project_heads[repo]
            if not commits_match(commit, current):
                drifts.append({
                    "file": rel,
                    "repo": repo,
                    "recorded": commit,
                    "current": current[:8],
                    "date": item.get("date", "—"),
                    "note": item.get("note", ""),
                })

    return {
        "scanned": scanned,
        "with_field": with_field,
        "drifts": drifts,
        "missing_repo": missing_repo,
        "head_failed": head_failed,
        "projects": project_heads,
        "projects_path": str(projects_path),
    }


def render(result: dict, week: str) -> str:
    L: list[str] = [
        "---",
        "tags: [复盘, 漂移检测, 自动生成]",
        f"date: {date.today().isoformat()}",
        f"week: {week}",
        "status: 待 review",
        "---",
        "",
        f"# Contexts 漂移检测报告 — {week}",
        "",
        f"> 由 `scripts/drift-scan.py` 自动生成。",
        f"> 协议：`Contexts/决策/Contexts漂移检测协议.md`",
        "",
        "## 一、扫描总览",
        "",
        f"- 业务仓清单：`{result['projects_path']}`（{len(result['projects'])} 个仓 HEAD 已读）",
        f"- 扫描 Contexts：{result['scanned']} 个 md 文件",
        f"- 含 `verified_against` 字段：{result['with_field']} 个",
        f"- **检测到漂移**：{len(result['drifts'])} 条",
        f"- repo 标识符不在 projects.list：{len(result['missing_repo'])} 条",
        f"- 仓库 HEAD 读取失败：{len(result['head_failed'])} 个",
        "",
    ]

    if result["head_failed"]:
        L += ["### 仓库 HEAD 读取失败", ""]
        for r in result["head_failed"]:
            L += [f"- `{r}`（projects.list 中路径不存在或非 git 仓）"]
        L += [""]

    L += ["## 二、漂移列表", ""]
    if result["drifts"]:
        L += [
            "> **每条都需人工 review**：是 Contexts 落后于代码（需更新文档），还是代码暂时性偏移（可忽略并更新 verified_against）。",
            "",
            "| 文件 | 仓 | 记录 commit | 当前 commit | 记录日期 | 备注 |",
            "|------|-----|-------------|-------------|---------|------|",
        ]
        for d in result["drifts"]:
            L += [
                f"| `{d['file']}` | `{d['repo']}` | `{d['recorded']}` | `{d['current']}` | {d['date']} | {d['note'] or '—'} |"
            ]
    else:
        L += ["（无漂移）"]
    L += [""]

    if result["missing_repo"]:
        L += ["## 三、未识别的 repo 标识符", "", "> 这些 Contexts 写了 `verified_against.repo` 但 projects.list 中没有该 identifier。", ""]
        for m in result["missing_repo"]:
            L += [f"- `{m['file']}` → repo `{m['repo']}`"]
        L += [""]

    L += [
        "## 四、Review 决策记录",
        "",
        "> 处置每条漂移后追加：日期 + 文件 + 决策（更新 Contexts / 更新 verified_against / 忽略）。",
        "",
    ]

    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="输出到 stdout，不写文件")
    ap.add_argument("--projects", help="自定义 projects.list 路径", default=None)
    args = ap.parse_args()

    if args.projects:
        os.environ["AIWORKKIT_PROJECTS"] = args.projects

    result = scan()
    today = date.today()
    iso_year, iso_week, _ = today.isocalendar()
    week_str = f"{iso_year}-W{iso_week:02d}"
    text = render(result, week_str)

    if args.dry_run:
        sys.stdout.write(text)
        return

    out_path = ROOT / "Contexts" / "决策" / f"漂移报告-{week_str}.md"
    out_path.write_text(text, encoding="utf-8")
    print(f"✓ 已生成 {out_path.relative_to(ROOT)}")
    print(f"  扫描 {result['scanned']} 个 Contexts；含字段 {result['with_field']}；漂移 {len(result['drifts'])}")
    if result["head_failed"]:
        print(f"  ⚠️ {len(result['head_failed'])} 个 repo HEAD 读取失败：{', '.join(result['head_failed'])}")


if __name__ == "__main__":
    main()
