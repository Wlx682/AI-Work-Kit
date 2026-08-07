#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import gate_parse


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def fm(path: Path) -> dict[str, str]:
    require(path.exists(), f"plan 不存在: {path}")
    return gate_parse.read_frontmatter(path)


def resolve_path(base: Path, raw: str, label: str, *, must_exist: bool = True) -> Path:
    require(bool(str(raw).strip()), f"缺少 {label} 路径")
    path = Path(str(raw).strip())
    if not path.is_absolute():
        path = base / path
    path = path.resolve()
    if must_exist:
        require(path.exists(), f"{label} 不存在: {raw}")
    return path


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{label} JSON 非法: {exc}") from exc
    require(isinstance(payload, dict), f"{label} 顶层必须是 object")
    return payload


def require_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    require(bool(text), f"{label} 为空")
    return text


def require_list(value: Any, label: str) -> list[Any]:
    require(isinstance(value, list), f"{label} 必须是数组")
    return value


def validate_path_items(items: list[Any], label: str, codebase_root: Path, *, require_existing: bool, fields: list[str]) -> None:
    for pos, raw in enumerate(items, 1):
        require(isinstance(raw, dict), f"{label}[{pos}] 必须是 object")
        item = raw
        raw_path = require_text(item.get("path"), f"{label}[{pos}].path")
        if require_existing:
            resolve_path(codebase_root, raw_path, f"{label}[{pos}].path", must_exist=True)
        for field in fields:
            require_text(item.get(field), f"{label}[{pos}].{field}")


def validate_design_payload(root: Path, payload: dict[str, Any], label: str, *, expected_story_id: str | None = None) -> None:
    if expected_story_id:
        require(payload.get("story_id") == expected_story_id, f"{label}.story_id 与 Story Plan 不一致")

    codebase_available = payload.get("codebase_available")
    require(isinstance(codebase_available, bool), f"{label}.codebase_available 必须是 boolean")

    codebase_root_raw = str(payload.get("codebase_root") or ".").strip()
    codebase_root = resolve_path(root, codebase_root_raw, f"{label}.codebase_root", must_exist=codebase_available)

    codebase_read = require_list(payload.get("codebase_read"), f"{label}.codebase_read")
    if codebase_available:
        require(codebase_read, f"{label}.codebase_read 不能为空")
        validate_path_items(codebase_read, f"{label}.codebase_read", codebase_root, require_existing=True, fields=["reason"])
    else:
        require_text(payload.get("codebase_unavailable_reason"), f"{label}.codebase_unavailable_reason")

    target_files = payload.get("target_files")
    require(isinstance(target_files, dict), f"{label}.target_files 必须是 object")
    modify = require_list(target_files.get("modify"), f"{label}.target_files.modify")
    create = require_list(target_files.get("create"), f"{label}.target_files.create")
    require(modify or create, f"{label}.target_files 至少需要一个 modify 或 create")
    validate_path_items(modify, f"{label}.target_files.modify", codebase_root, require_existing=codebase_available, fields=["purpose", "layer"])
    validate_path_items(create, f"{label}.target_files.create", codebase_root, require_existing=False, fields=["reason", "naming_basis", "layer"])

    module_boundary = payload.get("module_boundary")
    require(isinstance(module_boundary, dict), f"{label}.module_boundary 必须是 object")
    require_text(module_boundary.get("layer"), f"{label}.module_boundary.layer")
    require_text(module_boundary.get("dependency_rule"), f"{label}.module_boundary.dependency_rule")

    tests = payload.get("tests")
    require(isinstance(tests, dict), f"{label}.tests 必须是 object")
    red = require_list(tests.get("red"), f"{label}.tests.red")
    require(red, f"{label}.tests.red 不能为空")
    for pos, item in enumerate(red, 1):
        require(isinstance(item, dict), f"{label}.tests.red[{pos}] 必须是 object")
        require_text(item.get("path"), f"{label}.tests.red[{pos}].path")
        require_text(item.get("command"), f"{label}.tests.red[{pos}].command")

    require_list(payload.get("risks"), f"{label}.risks")
    blocked = require_list(payload.get("blocked_questions"), f"{label}.blocked_questions")
    require(payload.get("confirmed") is True, f"{label}.confirmed 必须为 true")
    require(not blocked, f"{label}.blocked_questions 非空，不能放行开发")


def validate_plan(root: Path, plan: Path) -> None:
    frontmatter = fm(plan)
    story_index = str(frontmatter.get("story_index") or "").strip()
    if story_index:
        index_path = resolve_path(root, story_index, "story_index")
        index = load_json(index_path, "Story index")
        require(index.get("scope_confirmed") is True, "Story Scope 尚未确认")
        stories = require_list(index.get("stories"), "Story index.stories")
        scoped = [story for story in stories if isinstance(story, dict) and story.get("sprint_scope") is True]
        require(scoped, "Scope 内至少需要一个用户故事")
        for story in scoped:
            sid = require_text(story.get("id"), "story.id")
            story_plan = resolve_path(root, require_text(story.get("path"), f"{sid}.path"), f"{sid} 子 Plan")
            validate_plan(root, story_plan)
        return

    design_raw = str(frontmatter.get("implementation_design") or "").strip()
    design_path = resolve_path(root, design_raw, "implementation_design")
    payload = load_json(design_path, "Implementation design")
    expected_story_id = str(frontmatter.get("story_id") or "").strip() or None
    validate_design_payload(root, payload, "implementation_design", expected_story_id=expected_story_id)


def main() -> int:
    parser = argparse.ArgumentParser(description="校验写代码前实现落点设计文件事实。")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--plan", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    plan = Path(args.plan)
    if not plan.is_absolute():
        plan = root / plan
    try:
        validate_plan(root, plan.resolve())
    except (ValidationError, OSError) as exc:
        print(f"BLOCKED:implementation-design:{exc}", file=sys.stderr)
        return 1
    print("OK:implementation-design")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
