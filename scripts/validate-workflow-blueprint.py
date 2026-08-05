#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = ROOT / ".workflows" / "blueprints"


class ValidationError(Exception):
    pass


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: JSON 解析失败: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: 顶层必须是 object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_blueprint(path: Path) -> list[str]:
    bp = load_json(path)
    warnings: list[str] = []

    if bp.get("kind") == "engine-index":
        require(isinstance(bp.get("triggerPhrases", []), list), f"{path}: engine-index.triggerPhrases 必须是数组")
        return warnings

    for key in ["name", "label", "version", "usesEpic", "stages"]:
        require(key in bp, f"{path}: 缺少必填字段 {key}")

    name = bp["name"]
    require(isinstance(name, str) and name, f"{path}: name 必须是非空字符串")
    require(path.stem == name, f"{path}: 文件名必须与 name 一致（当前 name={name}）")
    require(isinstance(bp["usesEpic"], bool), f"{path}: usesEpic 必须是 boolean")
    require(isinstance(bp["stages"], list) and bp["stages"], f"{path}: stages 必须是非空数组")

    if bp["usesEpic"]:
        require(bp.get("epicTemplate"), f"{path}: usesEpic=true 时必须声明 epicTemplate")
        require((ROOT / bp["epicTemplate"]).exists(), f"{path}: epicTemplate 不存在: {bp['epicTemplate']}")

    for script_key in ["bootScript", "gateScript"]:
        if bp.get(script_key):
            require((ROOT / bp[script_key]).exists(), f"{path}: {script_key} 不存在: {bp[script_key]}")

    stage_keys: list[str] = []
    for index, stage in enumerate(bp["stages"], start=1):
        require(isinstance(stage, dict), f"{path}: stages[{index}] 必须是 object")
        for key in ["key", "label", "planFolder", "skills", "exitCriteria", "next"]:
            require(key in stage, f"{path}: stage #{index} 缺少字段 {key}")

        stage_key = stage["key"]
        require(isinstance(stage_key, str) and stage_key, f"{path}: stage #{index} key 必须是非空字符串")
        require(stage_key not in stage_keys, f"{path}: stage key 重复: {stage_key}")
        stage_keys.append(stage_key)

        folder = stage["planFolder"]
        require(isinstance(folder, str) and folder, f"{path}: stage {stage_key}.planFolder 必须是非空字符串")
        candidate_folders = [folder, *[str(item) for item in as_list(stage.get("planFolderAlt"))]]
        if not any((ROOT / candidate).is_dir() for candidate in candidate_folders):
            raise ValidationError(f"{path}: stage {stage_key} 的 planFolder/planFolderAlt 均不存在: {candidate_folders}")

        skills = stage["skills"]
        require(isinstance(skills, list) and all(isinstance(item, str) and item for item in skills), f"{path}: stage {stage_key}.skills 必须是非空字符串数组")

        exit_criteria = stage["exitCriteria"]
        require(isinstance(exit_criteria, dict) and exit_criteria, f"{path}: stage {stage_key}.exitCriteria 必须是非空 object")

        if bp["usesEpic"]:
            require(stage.get("epicField"), f"{path}: usesEpic=true 时 stage {stage_key} 必须声明 epicField")
        elif stage.get("epicField"):
            warnings.append(f"{path}: usesEpic=false 时 stage {stage_key}.epicField 会被忽略")

        template = stage.get("template")
        if template and not (ROOT / template).exists():
            warnings.append(f"{path}: stage {stage_key}.template 不存在: {template}")

    valid_next = set(stage_keys) | {"done"}
    stage_positions = {key: index for index, key in enumerate(stage_keys)}
    for stage in bp["stages"]:
        next_key = stage["next"]
        require(next_key in valid_next, f"{path}: stage {stage['key']}.next 指向未知阶段: {next_key}")
        exit_criteria = stage["exitCriteria"]
        if "mergeAnalysis" in exit_criteria:
            require(
                isinstance(exit_criteria["mergeAnalysis"], bool),
                f"{path}: stage {stage['key']}.exitCriteria.mergeAnalysis 必须是 boolean",
            )
        if "mergeDecisionTraceability" in exit_criteria:
            analysis_stage = exit_criteria["mergeDecisionTraceability"]
            require(
                isinstance(analysis_stage, str) and analysis_stage in stage_positions,
                f"{path}: stage {stage['key']}.exitCriteria.mergeDecisionTraceability 须引用已声明阶段",
            )
            require(
                stage_positions[analysis_stage] < stage_positions[stage["key"]],
                f"{path}: stage {stage['key']}.mergeDecisionTraceability 只能引用前序阶段",
            )

    trigger_hints = bp.get("triggerHints", [])
    if trigger_hints:
        require(isinstance(trigger_hints, list) and all(isinstance(item, str) and item.strip() for item in trigger_hints), f"{path}: triggerHints 必须是非空字符串数组")

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 .workflows/blueprints 工作流蓝图。")
    parser.add_argument("paths", nargs="*", help="要校验的蓝图文件；不传则校验 .workflows/blueprints/*.json")
    parser.add_argument("--quiet", action="store_true", help="只输出错误")
    args = parser.parse_args()

    paths = [Path(item) for item in args.paths]
    if not paths:
        paths = sorted(BLUEPRINT_DIR.glob("*.json"))

    if not paths:
        print("BLOCKED:workflow-blueprint: 未找到蓝图文件", file=sys.stderr)
        return 1

    ok = True
    for raw in paths:
        path = raw if raw.is_absolute() else ROOT / raw
        try:
            warnings = validate_blueprint(path)
        except ValidationError as exc:
            ok = False
            print(f"BLOCKED:workflow-blueprint: {exc}", file=sys.stderr)
            continue
        if not args.quiet:
            print(f"OK:workflow-blueprint:{path.relative_to(ROOT)}")
            for warning in warnings:
                print(f"WARN:workflow-blueprint:{warning}", file=sys.stderr)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
