#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from gate_parse import is_placeholder, read_frontmatter, split_table_row


PLACEHOLDER_WORDS = {
    "",
    "-",
    "—",
    "todo",
    "待补",
    "待补充",
    "待确认",
    "待决策",
    "未知",
    "未分析",
}
NO_VALUE_WORDS = {"无", "无需", "n/a", "na", "不适用"}
YES_WORDS = {"是", "需要", "需决策", "yes", "true"}
NO_WORDS = {"否", "不需要", "无需", "no", "false"}
AI_OWNER_PATTERN = re.compile(
    r"^(?:ai|codex|claude|chatgpt|模型|大模型|助手|ai助手|自动化助手|机器人)$",
    re.IGNORECASE,
)


class MergeAnalysisError(Exception):
    pass


@dataclass(frozen=True)
class Table:
    headers: list[str]
    rows: list[dict[str, str]]


def normalized(value: str) -> str:
    return re.sub(r"\s+", "", value.strip()).lower()


def blank_or_placeholder(value: str) -> bool:
    clean = value.strip()
    return (
        is_placeholder(clean)
        or normalized(clean) in PLACEHOLDER_WORDS
        or bool(re.search(r"【[^】]*】", clean))
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MergeAnalysisError(message)


def section_lines(path: Path, wanted: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    headings: list[tuple[int, int, str]] = []
    in_fence = False
    for index, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            headings.append((index, len(match.group(1)), match.group(2).strip()))

    for index, (line_no, level, title) in enumerate(headings):
        if wanted not in title:
            continue
        end = len(lines)
        for next_line, next_level, _ in headings[index + 1 :]:
            if next_level <= level:
                end = next_line
                break
        return lines[line_no + 1 : end]
    raise MergeAnalysisError(f"缺少章节「{wanted}」")


def parse_table(path: Path, section: str, required_headers: list[str]) -> Table:
    raw_rows = [split_table_row(line) for line in section_lines(path, section)]
    rows = [row for row in raw_rows if row]
    require(rows, f"「{section}」缺少 Markdown 表格")

    header_index = -1
    for index, row in enumerate(rows):
        if all(header in row for header in required_headers):
            header_index = index
            break
    require(header_index >= 0, f"「{section}」表头须包含：{'、'.join(required_headers)}")

    headers = rows[header_index]
    data_rows: list[dict[str, str]] = []
    for row in rows[header_index + 1 :]:
        if len(row) == len(headers) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in row):
            continue
        if len(row) != len(headers):
            continue
        data_rows.append(dict(zip(headers, row)))
    require(data_rows, f"「{section}」至少需要一条数据")
    return Table(headers=headers, rows=data_rows)


def require_fields(row: dict[str, str], fields: list[str], context: str) -> None:
    for field in fields:
        require(not blank_or_placeholder(row.get(field, "")), f"{context} 的「{field}」未填写或仍是占位")


def unique_ids(rows: list[dict[str, str]], field: str, context: str) -> set[str]:
    values: list[str] = []
    for row in rows:
        value = row.get(field, "").strip()
        require(not blank_or_placeholder(value), f"{context} 的「{field}」未填写")
        values.append(value)
    require(len(values) == len(set(values)), f"{context} 的「{field}」存在重复")
    return set(values)


def validate_analysis(path: Path) -> tuple[set[str], set[str]]:
    require(path.is_file(), f"分析 plan 不存在：{path}")
    frontmatter = read_frontmatter(path)
    require(frontmatter.get("status") == "已采纳", "分析 plan 的 status 须为「已采纳」")
    require(frontmatter.get("p0_open") == "0", "分析 plan 的 p0_open 须为 0")

    intent = parse_table(
        path,
        "双边代码意图",
        ["意图ID", "分支侧", "文件/模块", "代码变化", "业务目标", "行为/规则变化", "证据", "置信度"],
    )
    intent_ids = unique_ids(intent.rows, "意图ID", "双边代码意图")
    sides: set[str] = set()
    low_confidence_intents: set[str] = set()
    for row in intent.rows:
        require_fields(
            row,
            ["意图ID", "分支侧", "文件/模块", "代码变化", "业务目标", "行为/规则变化", "证据", "置信度"],
            f"意图 {row.get('意图ID', '')}",
        )
        side = normalized(row["分支侧"])
        if "源" in side or side in {"source", "ours"}:
            sides.add("source")
        if "目标" in side or side in {"target", "theirs"}:
            sides.add("target")
        confidence = row["置信度"].strip()
        require(confidence in {"高", "中", "低"}, f"意图 {row['意图ID']} 的置信度只能填高/中/低")
        if confidence == "低":
            low_confidence_intents.add(row["意图ID"].strip())
    require({"source", "target"} <= sides, "双边代码意图必须同时覆盖源分支和目标分支")

    conflicts = parse_table(
        path,
        "业务冲突矩阵",
        ["冲突ID", "关联意图", "冲突类型", "业务影响", "AI结论", "需开发者决策", "决策ID"],
    )
    conflict_ids = unique_ids(conflicts.rows, "冲突ID", "业务冲突矩阵")
    required_decision_ids: set[str] = set()
    covered_intent_ids: set[str] = set()
    decision_intent_ids: set[str] = set()
    for row in conflicts.rows:
        conflict_id = row["冲突ID"].strip()
        require_fields(
            row,
            ["冲突ID", "关联意图", "冲突类型", "业务影响", "AI结论", "需开发者决策"],
            f"冲突 {conflict_id}",
        )
        linked_intents = {
            item.strip()
            for item in re.split(r"[,，/、;\s]+", row["关联意图"])
            if item.strip()
        }
        require(linked_intents <= intent_ids, f"冲突 {conflict_id} 引用了不存在的意图：{sorted(linked_intents - intent_ids)}")
        covered_intent_ids.update(linked_intents)
        decision_flag = normalized(row["需开发者决策"])
        require(decision_flag in YES_WORDS | NO_WORDS, f"冲突 {conflict_id} 的「需开发者决策」只能填是/否")
        conclusion = row["AI结论"]
        if decision_flag in YES_WORDS:
            require("需开发者决策" in conclusion, f"冲突 {conflict_id} 需要开发者决策，AI结论须明确写「需开发者决策」")
            decision_id = row.get("决策ID", "").strip()
            require(not blank_or_placeholder(decision_id) and normalized(decision_id) not in NO_VALUE_WORDS, f"冲突 {conflict_id} 缺少决策ID")
            required_decision_ids.add(decision_id)
            decision_intent_ids.update(linked_intents)
        else:
            require("需开发者决策" not in conclusion, f"冲突 {conflict_id} 标记无需决策，但 AI结论仍写了「需开发者决策」")
            require(
                normalized(row.get("决策ID", "")) in NO_VALUE_WORDS,
                f"冲突 {conflict_id} 无需开发者决策时，决策ID须明确填「无」",
            )
    uncovered_intents = intent_ids - covered_intent_ids
    require(not uncovered_intents, f"以下双边意图未进入业务冲突评估：{sorted(uncovered_intents)}")
    unreviewed_low_confidence = low_confidence_intents - decision_intent_ids
    require(
        not unreviewed_low_confidence,
        f"以下低置信度意图未交由开发者决策：{sorted(unreviewed_low_confidence)}",
    )

    decisions = parse_table(
        path,
        "开发者决策清单",
        ["决策ID", "待决策问题", "可选方案及影响", "开发者结论", "决策人", "确认记录", "状态"],
    )
    decision_rows: dict[str, dict[str, str]] = {}
    for row in decisions.rows:
        decision_id = row["决策ID"].strip()
        if normalized(decision_id) in NO_VALUE_WORDS:
            require(not required_decision_ids, "存在待决策冲突时，开发者决策清单不能写「无需决策」")
            require(normalized(row.get("状态", "")) in {"无需决策", "不适用"}, "无决策行的状态须为「无需决策」")
            require(
                normalized(row.get("开发者结论", "")) in {"无需决策", "不适用"},
                "无决策行的开发者结论须为「无需决策」",
            )
            continue
        require(not blank_or_placeholder(decision_id), "开发者决策清单存在空决策ID")
        require(decision_id not in decision_rows, f"开发者决策清单的决策ID重复：{decision_id}")
        require_fields(
            row,
            ["待决策问题", "可选方案及影响", "开发者结论", "决策人", "确认记录", "状态"],
            f"决策 {decision_id}",
        )
        require(row["状态"].strip() == "已决策", f"决策 {decision_id} 尚未由开发者确认")
        require(not AI_OWNER_PATTERN.search(row["决策人"]), f"决策 {decision_id} 的决策人不能是 AI 或自动化助手")
        decision_rows[decision_id] = row
    missing_decisions = required_decision_ids - set(decision_rows)
    require(not missing_decisions, f"缺少已确认的开发者决策：{sorted(missing_decisions)}")

    strategy = parse_table(
        path,
        "合并策略与验证映射",
        ["冲突ID", "处理策略", "影响范围", "验证场景", "状态"],
    )
    strategy_rows: dict[str, dict[str, str]] = {}
    for row in strategy.rows:
        conflict_id = row["冲突ID"].strip()
        require(conflict_id not in strategy_rows, f"合并策略与验证映射的冲突ID重复：{conflict_id}")
        require_fields(row, ["冲突ID", "处理策略", "影响范围", "验证场景", "状态"], f"策略 {conflict_id}")
        require(row["状态"].strip() == "已规划", f"冲突 {conflict_id} 的合并策略状态须为「已规划」")
        strategy_rows[conflict_id] = row
    missing_strategy = conflict_ids - set(strategy_rows)
    require(not missing_strategy, f"业务冲突缺少合并策略或验证场景：{sorted(missing_strategy)}")
    return conflict_ids, required_decision_ids


def validate_implementation(path: Path, conflict_ids: set[str], decision_ids: set[str]) -> None:
    require(path.is_file(), f"合并执行 plan 不存在：{path}")
    implementation = parse_table(
        path,
        "决策落实记录",
        ["追踪ID", "影响文件", "落实方式", "验证用例", "状态"],
    )
    rows: dict[str, dict[str, str]] = {}
    for row in implementation.rows:
        trace_id = row["追踪ID"].strip()
        require(not blank_or_placeholder(trace_id), "决策落实记录存在空追踪ID")
        require(trace_id not in rows, f"决策落实记录的追踪ID重复：{trace_id}")
        require_fields(row, ["影响文件", "落实方式", "验证用例", "状态"], f"落实项 {trace_id}")
        require(row["状态"].strip() == "已落实", f"落实项 {trace_id} 的状态须为「已落实」")
        rows[trace_id] = row

    required_trace_ids = conflict_ids | decision_ids
    missing = required_trace_ids - set(rows)
    require(not missing, f"以下冲突/决策未落实到文件与验证用例：{sorted(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 merge-code 的双边业务意图、开发者决策与落实追踪。")
    parser.add_argument("--analysis", required=True, type=Path, help="intent-analysis 阶段 plan")
    parser.add_argument("--implementation", type=Path, help="merge 阶段 plan；提供时校验追踪闭环")
    args = parser.parse_args()

    try:
        conflict_ids, decision_ids = validate_analysis(args.analysis)
        if args.implementation:
            validate_implementation(args.implementation, conflict_ids, decision_ids)
    except (MergeAnalysisError, OSError) as exc:
        print(f"BLOCKED:merge-analysis:{exc}")
        return 1

    suffix = "analysis+implementation" if args.implementation else "analysis"
    print(f"OK:merge-analysis:{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
