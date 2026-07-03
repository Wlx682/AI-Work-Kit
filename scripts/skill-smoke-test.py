#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class SmokeError(Exception):
    pass


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def expected_path(input_path: Path) -> Path:
    name = input_path.name
    if name.endswith(".input.md"):
        return input_path.with_name(name.removesuffix(".input.md") + ".expected.md")
    return input_path.with_suffix(input_path.suffix + ".expected.md")


def bullet_values(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    values: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped == heading
            continue
        if not in_section:
            continue
        if stripped.startswith("- "):
            value = stripped[2:].strip()
            if value:
                values.append(value.strip("`"))
    return values


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeError(message)


def validate_fixture(skill: str, input_path: Path, expected: Path) -> tuple[list[str], list[str]]:
    require(input_path.exists(), f"输入 fixture 不存在: {rel(input_path)}")
    require(expected.exists(), f"期望 fixture 不存在: {rel(expected)}")

    input_text = input_path.read_text(encoding="utf-8")
    expected_text = expected.read_text(encoding="utf-8")

    require(f"skill: {skill}" in input_text, f"{rel(input_path)} 缺少 skill: {skill}")
    require("## 输入" in input_text, f"{rel(input_path)} 缺少 ## 输入")
    require("## 期望断言" in expected_text, f"{rel(expected)} 缺少 ## 期望断言")

    must = bullet_values(expected_text, "## 必须包含")
    forbid = bullet_values(expected_text, "## 禁止包含")
    require(must or forbid, f"{rel(expected)} 必须至少声明一个包含或禁止断言")
    return must, forbid


def validate_output(output_path: Path, must: list[str], forbid: list[str]) -> None:
    require(output_path.exists(), f"输出文件不存在: {rel(output_path)}")
    text = output_path.read_text(encoding="utf-8")
    missing = [item for item in must if item not in text]
    forbidden = [item for item in forbid if item in text]
    if missing:
        raise SmokeError("输出缺少必须片段: " + ", ".join(missing))
    if forbidden:
        raise SmokeError("输出包含禁止片段: " + ", ".join(forbidden))


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill fixture/产物 smoke test。")
    parser.add_argument("skill", help="Skill 名称，如 figma-ui")
    parser.add_argument("input", help="*.input.md fixture 路径")
    parser.add_argument("--output", help="可选：真实产物路径；提供后执行包含/禁止断言")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    expected = expected_path(input_path)

    try:
        must, forbid = validate_fixture(args.skill, input_path, expected)
        if args.output:
            output_path = Path(args.output)
            if not output_path.is_absolute():
                output_path = ROOT / output_path
            validate_output(output_path, must, forbid)
            print(f"OK:skill-smoke-test:{args.skill}:output assertions passed")
        else:
            print(
                f"OK:skill-smoke-test:{args.skill}:fixture ready "
                f"(must={len(must)}, forbid={len(forbid)})"
            )
        return 0
    except SmokeError as exc:
        print(f"BLOCKED:skill-smoke-test:{args.skill}:{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
