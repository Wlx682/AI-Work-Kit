#!/usr/bin/env python3
from __future__ import annotations
"""
validate-skill-run.py — 校验 plan 文件末尾的 skill_run YAML 块

用法：
  python3 scripts/validate-skill-run.py <plan.md>             # 块缺失视为 OK（非强制路径）
  python3 scripts/validate-skill-run.py --require <plan.md>   # 块缺失即失败

退出码：
  0 — 块缺失（无 --require）或块存在且合法
  1 — 块缺失（有 --require）或块存在但非法

说明：使用零依赖手写解析器，仅支持本协议的固定 schema。
协议：Contexts/决策/Skill反馈协议.md
"""
import argparse
import pathlib
import re
import sys

ALLOWED_UTILITY = {"high", "not-needed"}
ALLOWED_OUTCOME = {"pass", "blocked", "partial"}
ROOT = pathlib.Path(__file__).resolve().parent.parent


def find_skill_run_blocks(content: str) -> list[str]:
    pattern = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)
    blocks = []
    for m in pattern.finditer(content):
        body = m.group(1)
        if re.match(r"^\s*skill_run\s*:", body):
            blocks.append(body)
    return blocks


def strip_inline_comment(line: str) -> str:
    """去 ` # ` 之后的行尾注释（不在引号内）。"""
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


def unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def parse_inline_value(s: str):
    s = unquote(s.strip())
    if s == "[]":
        return []
    if s.startswith("[") and s.endswith("]"):
        body = s[1:-1].strip()
        if not body:
            return []
        return [unquote(item.strip()) for item in body.split(",") if item.strip()]
    return s


def parse_skill_run(body: str) -> dict | None:
    """解析固定 schema 的 YAML 块。仅支持本协议要求的层级结构。"""
    raw_lines = body.splitlines()
    # 去注释、去空行
    lines = []
    for ln in raw_lines:
        stripped = strip_inline_comment(ln)
        if stripped.strip():
            lines.append(stripped)
    if not lines:
        return None
    if lines[0].strip() != "skill_run:":
        return None

    sr: dict = {}
    i = 1
    n = len(lines)

    while i < n:
        line = lines[i]
        # level-1: 2-space indent, simple key
        m = re.match(r"^  ([A-Za-z_]+)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key = m.group(1)
        val = m.group(2).strip()
        if val:
            sr[key] = parse_inline_value(val)
            i += 1
            continue

        # collection — read child lines at indent ≥ 4
        i += 1
        items = []
        while i < n:
            child = lines[i]
            # 子项以 4-空格 "- " 开头
            if child.startswith("    - "):
                first = child[6:].strip()
                # 是否是 "k: v" 形态？
                kv = re.match(r"^([A-Za-z_]+)\s*:\s*(.*)$", first)
                if kv:
                    item: dict = {kv.group(1): parse_inline_value(kv.group(2).strip())}
                    i += 1
                    # 6-空格缩进的同 item 字段
                    while i < n and re.match(r"^      ([A-Za-z_]+)\s*:\s*(.*)$", lines[i]):
                        sub = re.match(r"^      ([A-Za-z_]+)\s*:\s*(.*)$", lines[i])
                        item[sub.group(1)] = parse_inline_value(sub.group(2).strip())
                        i += 1
                    items.append(item)
                else:
                    items.append(parse_inline_value(first))
                    i += 1
            elif child.startswith("  ") and not child.startswith("    "):
                # 回到 level-1，跳出 collection
                break
            else:
                # 未知缩进，跳过
                i += 1
        sr[key] = items

    return {"skill_run": sr}


def fail(msg: str) -> None:
    print(f"BLOCKED:skill_run:{msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan", help="plan 文件路径")
    ap.add_argument("--require", action="store_true", help="缺失 skill_run 块时视为失败")
    ap.add_argument("--stage", help="要求最后一个 skill_run.workflow_stage 与当前 workflow stage 一致")
    args = ap.parse_args()

    plan_path = pathlib.Path(args.plan).resolve()
    if not plan_path.exists():
        fail(f"plan 文件不存在: {args.plan}")

    content = plan_path.read_text(encoding="utf-8")
    blocks = find_skill_run_blocks(content)
    body = blocks[-1] if blocks else None

    # 同一 Plan 可承载多个 workflow stage（如 story-split / story-development）。
    # 指定 --stage 时选择最后一个匹配该 stage 的反馈，而不是要求它恰好是整份文件最后一块。
    if args.stage:
        body = None
        for candidate in reversed(blocks):
            parsed_candidate = parse_skill_run(candidate)
            if parsed_candidate and parsed_candidate.get("skill_run", {}).get("workflow_stage") == args.stage:
                body = candidate
                break

    if body is None:
        if args.require:
            fail("缺少 `## 反馈（skill_run）` 节及 ```yaml skill_run: ... ``` 代码块")
        print("OK:skill_run 块不存在（本路径非强制）")
        sys.exit(0)

    parsed = parse_skill_run(body)
    if not parsed or "skill_run" not in parsed:
        fail("YAML 块顶层缺 skill_run 键，或缩进不符合协议（必须 2-空格 / 4-空格 / 6-空格）")

    sr = parsed["skill_run"]

    if args.stage and sr.get("workflow_stage") != args.stage:
        fail(f"找不到 workflow_stage={args.stage!r} 的合法 skill_run")

    for k in ("skill", "plan", "date", "contexts_used"):
        if k not in sr:
            fail(f"缺必填字段: {k}")

    if not sr["skill"] or not isinstance(sr["skill"], str):
        fail("skill 必须是非空字符串")

    if not isinstance(sr["contexts_used"], list) or not sr["contexts_used"]:
        fail("contexts_used 必须是非空列表")

    for i, entry in enumerate(sr["contexts_used"]):
        if not isinstance(entry, dict):
            fail(f"contexts_used[{i}] 必须是 mapping")
        for k in ("path", "utility"):
            if k not in entry:
                fail(f"contexts_used[{i}] 缺 {k}")
        util = entry["utility"]
        if util not in ALLOWED_UTILITY:
            fail(f"contexts_used[{i}].utility 非法 ({util!r})，必须 ∈ {sorted(ALLOWED_UTILITY)}")
        path = entry["path"]
        if not (ROOT / path).exists():
            fail(f"contexts_used[{i}].path 不存在: {path}")
        if util == "high":
            reason = (entry.get("reason") or "").strip()
            if not reason:
                fail(f"contexts_used[{i}] utility=high 但 reason 为空")

    stale = sr.get("contexts_stale") or []
    if not isinstance(stale, list):
        fail("contexts_stale 必须是列表或省略")
    for i, entry in enumerate(stale):
        if not isinstance(entry, dict):
            fail(f"contexts_stale[{i}] 必须是 mapping")
        for k in ("path", "reason"):
            val = entry.get(k)
            if not val or not str(val).strip():
                fail(f"contexts_stale[{i}] 缺 {k} 或为空")
        if not (ROOT / entry["path"]).exists():
            fail(f"contexts_stale[{i}].path 不存在: {entry['path']}")

    # 执行质量字段（全部可选；填了才校验取值域）
    if "outcome_status" in sr:
        if sr["outcome_status"] not in ALLOWED_OUTCOME:
            fail(f"outcome_status 非法 ({sr['outcome_status']!r})，必须 ∈ {sorted(ALLOWED_OUTCOME)}")
    if "verdict_score" in sr:
        try:
            score = float(sr["verdict_score"])
        except (TypeError, ValueError):
            fail(f"verdict_score 必须是 0-10 数字（当前 {sr['verdict_score']!r}）")
        if not (0 <= score <= 10):
            fail(f"verdict_score 须在 0-10（当前 {score}）")
    if "revisit_needed" in sr:
        if str(sr["revisit_needed"]).lower() not in ("true", "false"):
            fail(f"revisit_needed 必须是布尔 true/false（当前 {sr['revisit_needed']!r}）")

    n_used = len(sr["contexts_used"])
    n_missing = len(sr.get("contexts_missing") or [])
    n_stale = len(stale)
    print(f"OK:skill_run 通过 (skill={sr['skill']}, used={n_used}, missing={n_missing}, stale={n_stale})")
    sys.exit(0)


if __name__ == "__main__":
    main()
