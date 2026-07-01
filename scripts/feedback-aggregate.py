#!/usr/bin/env python3
"""
feedback-aggregate.py — 月度聚合 skill_run 反馈块

扫描：
  - Plans/**/*.meta.yaml（人类卷/AI卷分离后的 AI 卷，优先）
  - Plans/**/*.md 末尾的 skill_run 块（取 last per file；已有同名 .meta.yaml 则跳过去重）
  - Contexts/决策/孤立反馈记录.md 所有 skill_run yaml 块

输出：Contexts/决策/反馈聚合-YYYY-MM.md（或 --dry-run 输出到 stdout）

聚合规则（per Contexts/决策/Skill反馈协议.md §五）：
  - 本月热点 Contexts: utility=high 累计 ≥ 3 次
  - 冷却候选: 近 90 天无任何 utility=high 引用
  - 漂移告警: contexts_stale 同 path 累计 ≥ 2 次
  - 补全候选: contexts_missing 同字符串去重后累计 ≥ 2 次
"""
import argparse
import pathlib
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ===== 内嵌解析器（与 validate-skill-run.py 同步保持） =====

def _strip_inline_comment(line: str) -> str:
    in_q = None
    for i, c in enumerate(line):
        if in_q:
            if c == in_q:
                in_q = None
            continue
        if c in ('"', "'"):
            in_q = c
            continue
        if c == "#" and (i == 0 or line[i - 1] in (" ", "\t")):
            return line[:i].rstrip()
    return line.rstrip()


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def parse_skill_run(body: str) -> dict | None:
    raw_lines = body.splitlines()
    lines = []
    for ln in raw_lines:
        stripped = _strip_inline_comment(ln)
        if stripped.strip():
            lines.append(stripped)
    if not lines or lines[0].strip() != "skill_run:":
        return None

    sr: dict = {}
    i, n = 1, len(lines)
    while i < n:
        line = lines[i]
        m = re.match(r"^  ([A-Za-z_]+)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val:
            sr[key] = _unquote(val)
            i += 1
            continue
        i += 1
        items = []
        while i < n:
            child = lines[i]
            if child.startswith("    - "):
                first = child[6:].strip()
                kv = re.match(r"^([A-Za-z_]+)\s*:\s*(.*)$", first)
                if kv:
                    item: dict = {kv.group(1): _unquote(kv.group(2).strip())}
                    i += 1
                    while i < n and re.match(r"^      ([A-Za-z_]+)\s*:\s*(.*)$", lines[i]):
                        sub = re.match(r"^      ([A-Za-z_]+)\s*:\s*(.*)$", lines[i])
                        item[sub.group(1)] = _unquote(sub.group(2).strip())
                        i += 1
                    items.append(item)
                else:
                    items.append(_unquote(first))
                    i += 1
            elif child.startswith("  ") and not child.startswith("    "):
                break
            else:
                i += 1
        sr[key] = items
    return {"skill_run": sr}


def find_all_skill_run_blocks(content: str) -> list[str]:
    pattern = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)
    out = []
    for m in pattern.finditer(content):
        body = m.group(1)
        if re.match(r"^\s*skill_run\s*:", body):
            out.append(body)
    return out


# ===== 扫描与聚合 =====

def scan_all_skill_runs() -> list[dict]:
    runs = []
    seen_plans = set()  # 已由 .meta.yaml 覆盖的 plan 路径，避免与报告内 skill_run 块重复计数
    # 1) 优先：Plans/**/*.meta.yaml（人类卷/AI卷分离后的 AI 卷）
    for p in (ROOT / "Plans").rglob("*.meta.yaml"):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        parsed = parse_skill_run(text)
        if parsed and "skill_run" in parsed:
            sr = parsed["skill_run"]
            sr["_source_file"] = str(p.relative_to(ROOT))
            runs.append(sr)
            if sr.get("plan"):
                seen_plans.add(str(sr["plan"]).strip())
    # 2) 回退：Plans/**/*.md 末尾的 skill_run 块（兼容未拆分的旧案例）
    for p in (ROOT / "Plans").rglob("*.md"):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for body in find_all_skill_run_blocks(text):
            parsed = parse_skill_run(body)
            if parsed and "skill_run" in parsed:
                sr = parsed["skill_run"]
                if str(p.relative_to(ROOT)) in seen_plans:
                    continue  # 已有对应 .meta.yaml，跳过报告内块避免重复
                sr["_source_file"] = str(p.relative_to(ROOT))
                runs.append(sr)
    orphan = ROOT / "Contexts" / "决策" / "孤立反馈记录.md"
    if orphan.exists():
        text = orphan.read_text(encoding="utf-8")
        for body in find_all_skill_run_blocks(text):
            parsed = parse_skill_run(body)
            if parsed:
                sr = parsed["skill_run"]
                sr["_source_file"] = str(orphan.relative_to(ROOT))
                runs.append(sr)
    return runs


def parse_date(s: str) -> date | None:
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def aggregate(runs: list[dict], month: str) -> dict:
    month_start = datetime.strptime(month + "-01", "%Y-%m-%d").date()
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)

    month_runs = [r for r in runs if (d := parse_date(r.get("date", ""))) and month_start <= d < next_month]

    hot_counter: Counter = Counter()
    hot_reasons: dict = defaultdict(list)
    for r in month_runs:
        for cu in r.get("contexts_used", []) or []:
            if isinstance(cu, dict) and cu.get("utility") == "high":
                p = cu.get("path")
                if p:
                    hot_counter[p] += 1
                    if cu.get("reason"):
                        hot_reasons[p].append(cu["reason"])
    hot = [(path, n, hot_reasons[path][:3]) for path, n in hot_counter.most_common() if n >= 3]

    today = date.today()
    ninety = today - timedelta(days=90)
    recent_high = set()
    for r in runs:
        d = parse_date(r.get("date", ""))
        if not d or d < ninety:
            continue
        for cu in r.get("contexts_used", []) or []:
            if isinstance(cu, dict) and cu.get("utility") == "high":
                p = cu.get("path")
                if p:
                    recent_high.add(p)
    all_ctx = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "Contexts").rglob("*.md"))
    cold = [p for p in all_ctx if p not in recent_high]

    stale_counter: Counter = Counter()
    stale_reasons: dict = defaultdict(list)
    for r in runs:
        for cs in r.get("contexts_stale", []) or []:
            if isinstance(cs, dict) and cs.get("path"):
                stale_counter[cs["path"]] += 1
                if cs.get("reason"):
                    stale_reasons[cs["path"]].append(cs["reason"])
    drift = [(path, n, stale_reasons[path][:3]) for path, n in stale_counter.most_common() if n >= 2]

    missing_counter: Counter = Counter()
    for r in runs:
        for cm in r.get("contexts_missing", []) or []:
            if isinstance(cm, str):
                missing_counter[cm.strip()] += 1
    missing = [(s, n) for s, n in missing_counter.most_common() if n >= 2]

    return {
        "month": month,
        "n_runs_month": len(month_runs),
        "n_runs_total": len(runs),
        "hot": hot,
        "cold": cold,
        "drift": drift,
        "missing": missing,
    }


def render(agg: dict) -> str:
    L = [f"---", "tags: [复盘, 反馈聚合, 自动生成]", f"date: {agg['month']}-01", "status: 待 review", "---", ""]
    L += [f"# Skill 反馈聚合报告 — {agg['month']}", ""]
    L += [f"> 由 `scripts/feedback-aggregate.py` 自动生成。本月 skill_run 执行 **{agg['n_runs_month']}** 次（全库累计 **{agg['n_runs_total']}**）。"]
    L += [f"> 协议：[[Contexts/决策/Skill反馈协议]] · 消费：月度复盘"]
    L += [""]

    L += ["## 一、本月热点 Contexts（utility=high 累计 ≥ 3 次）", ""]
    if agg["hot"]:
        L += ["| 路径 | 次数 | 主要用途（样本）|", "|------|------|------------------|"]
        for path, n, reasons in agg["hot"]:
            sample = " · ".join(reasons) if reasons else "—"
            L += [f"| `{path}` | {n} | {sample} |"]
    else:
        L += ["（无）"]
    L += [""]

    L += ["## 二、冷却候选（近 90 天无任何 high 引用）", ""]
    L += ["> 决策：**删除** / **合并** / **标 deprecated** / **保留为长期参考**", ""]
    if agg["cold"]:
        for p in agg["cold"][:50]:
            L += [f"- [ ] `{p}`"]
        if len(agg["cold"]) > 50:
            L += [f"- … 还有 {len(agg['cold']) - 50} 条未列出（见下方 dataview）"]
    else:
        L += ["（无 — 所有 Contexts 均在 90 天内被高利用引用过）"]
    L += [""]

    L += ["## 三、漂移告警（contexts_stale 累计 ≥ 2 次）", ""]
    L += ["> 决策：**必须 review** 并修复 / 归档。", ""]
    if agg["drift"]:
        L += ["| 路径 | 标记次数 | 脱钩原因（样本）|", "|------|---------|-----------------|"]
        for path, n, reasons in agg["drift"]:
            sample = " · ".join(reasons) if reasons else "—"
            L += [f"| `{path}` | {n} | {sample} |"]
    else:
        L += ["（无）"]
    L += [""]

    L += ["## 四、补全候选（contexts_missing 累计 ≥ 2 次）", ""]
    L += ["> 决策：**新建** Contexts / **合并到现有** / **改 Skill 默认列表**", ""]
    if agg["missing"]:
        L += ["| 主题 | 提及次数 |", "|------|---------|"]
        for s, n in agg["missing"]:
            L += [f"| {s} | {n} |"]
    else:
        L += ["（无）"]
    L += [""]

    L += ["---", "", "## 五、Review 决策记录", "", "> review 完毕后在此追加日期 + 每项的处置结果（删 / 合并 / 修 / 保留 / 新建），便于后续追溯。", ""]

    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--month", default=date.today().strftime("%Y-%m"), help="YYYY-MM，默认本月")
    ap.add_argument("--dry-run", action="store_true", help="输出到 stdout，不写文件")
    args = ap.parse_args()

    runs = scan_all_skill_runs()
    agg = aggregate(runs, args.month)
    text = render(agg)

    if args.dry_run:
        sys.stdout.write(text)
        return

    out_path = ROOT / "Contexts" / "决策" / f"反馈聚合-{args.month}.md"
    out_path.write_text(text, encoding="utf-8")
    print(f"✓ 已生成 {out_path.relative_to(ROOT)}")
    print(f"  本月 runs: {agg['n_runs_month']} / 全库累计: {agg['n_runs_total']}")
    print(f"  热点: {len(agg['hot'])} / 冷却: {len(agg['cold'])} / 漂移: {len(agg['drift'])} / 补全: {len(agg['missing'])}")


if __name__ == "__main__":
    main()
