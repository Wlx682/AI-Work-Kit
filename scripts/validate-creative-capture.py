#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import gate_parse


STAGES = ["radar", "insight", "synthesis", "reality-test", "retro"]
PLACEHOLDERS = {"", "-", "—", "待补", "TODO", "todo", "待确认"}


class ValidationError(Exception):
    pass


def is_placeholder(value: str) -> bool:
    value = value.strip().strip("`")
    if value in PLACEHOLDERS:
        return True
    if re.fullmatch(r"【[^】]*】", value):
        return True
    return "【" in value or "】" in value


def table_rows(content: str, prefix: str, width: int) -> list[list[str]]:
    pattern = re.compile(rf"^{re.escape(prefix)}-\d{{2,}}$")
    rows: list[list[str]] = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < width or not pattern.fullmatch(cells[0]):
            continue
        cells = cells[:width]
        if any(is_placeholder(cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_radar(content: str, _: dict[str, str]) -> str:
    rows = table_rows(content, "S", 8)
    require(len(rows) >= 12, f"至少需要 12 条完整信号（当前 {len(rows)}）")
    domains = {row[1] for row in rows}
    require(len(domains) >= 4, f"至少需要 4 个不同领域（当前 {len(domains)}）")
    outside = [row for row in rows if row[6] == "是"]
    require(len(outside) >= 2, f"至少需要 2 条同温层外信号（当前 {len(outside)}）")
    random_walks = [row for row in rows if row[2] == "随机漫步"]
    require(len(random_walks) >= 1, "至少需要 1 条来源类型为“随机漫步”的信号")
    return f"signals={len(rows)}, domains={len(domains)}, outside={len(outside)}, random_walk={len(random_walks)}"


def validate_insight(content: str, _: dict[str, str]) -> str:
    insights = table_rows(content, "I", 7)
    problems = table_rows(content, "Q", 4)
    require(len(insights) >= 5, f"至少需要 5 张完整洞察卡（当前 {len(insights)}）")
    require(len(problems) >= 3, f"至少需要 3 张深层问题卡（当前 {len(problems)}）")
    return f"insights={len(insights)}, problems={len(problems)}"


def validate_synthesis(content: str, fm: dict[str, str]) -> str:
    ideas = table_rows(content, "C", 8)
    require(len(ideas) >= 3, f"至少需要 3 个完整创意候选（当前 {len(ideas)}）")
    selected = fm.get("selected_idea", "").strip()
    require(not is_placeholder(selected), "frontmatter.selected_idea 未选择")
    ids = {row[0] for row in ideas}
    require(selected in ids, f"selected_idea={selected!r} 不在完整创意候选中")
    return f"ideas={len(ideas)}, selected={selected}"


def validate_reality_test(content: str, fm: dict[str, str]) -> str:
    experiments = table_rows(content, "E", 7)
    evidence = table_rows(content, "EV", 5)
    require(len(experiments) >= 1, "至少需要 1 个完整现实实验")
    require(len(evidence) >= 1, "至少需要 1 条真实行为证据")
    result = fm.get("experiment_result", "").strip()
    allowed = {"继续验证", "转向", "停止"}
    require(result in allowed, f"experiment_result 必须是 {sorted(allowed)} 之一（当前 {result or '空'}）")
    experiment_ids = {row[0] for row in experiments}
    dangling = [row[0] for row in evidence if row[1] not in experiment_ids]
    require(not dangling, f"证据引用了不存在的实验: {', '.join(dangling)}")
    return f"experiments={len(experiments)}, evidence={len(evidence)}, result={result}"


def validate_retro(content: str, fm: dict[str, str]) -> str:
    seeds = table_rows(content, "N", 4)
    require(len(seeds) >= 3, f"至少需要 3 个下轮种子（当前 {len(seeds)}）")
    cycle = fm.get("cycle_decision", "").strip()
    require(cycle in {"继续", "转向", "停止"}, "cycle_decision 必须是“继续 / 转向 / 停止”之一")
    archive = fm.get("archive_decision", "").strip()
    require(
        archive in {"已归档", "不沉淀（用户确认）"},
        "archive_decision 仍待用户确认；只能填写“已归档”或“不沉淀（用户确认）”",
    )
    return f"seeds={len(seeds)}, cycle={cycle}, archive={archive}"


VALIDATORS = {
    "radar": validate_radar,
    "insight": validate_insight,
    "synthesis": validate_synthesis,
    "reality-test": validate_reality_test,
    "retro": validate_retro,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 creative-capture 周循环的定量配额与人类决定事实。")
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("plan")
    args = parser.parse_args()

    plan = Path(args.plan)
    if not plan.is_file():
        print(f"BLOCKED:creative-capture:{args.stage}: plan 不存在: {plan}", file=sys.stderr)
        return 1
    content = plan.read_text(encoding="utf-8")
    frontmatter = gate_parse.read_frontmatter(plan)
    try:
        details = VALIDATORS[args.stage](content, frontmatter)
    except ValidationError as exc:
        print(f"BLOCKED:creative-capture:{args.stage}: {exc}", file=sys.stderr)
        return 1
    print(f"OK:creative-capture:{args.stage}: {details}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
