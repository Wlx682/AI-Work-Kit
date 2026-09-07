#!/usr/bin/env python3
"""Verify the small set of invariants that define active AI-Work-Kit behavior."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTROL_FILES = (
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / ".cursorrules",
    ROOT / ".obsidian" / "community-plugins.json",
    ROOT / "README.md",
    ROOT / "索引.md",
    ROOT / "Knowledge" / "决策" / "Kit核心原则.md",
)
FORBIDDEN_ACTIVE_PATHS = (
    "Plans",
    "Contexts",
    "Templates",
    ".workflows",
    "_Archive_v1",
)
FORBIDDEN_CONTROL_TERMS = (
    "workflow-router",
    "workflow-gate.sh",
    "workflow-status.py",
    "plan-gate-check.sh",
    "skill_run",
    ".workflows/blueprints",
    "Plans/",
    "Templates/",
    "_Archive_v1/",
    '"templater-obsidian"',
)
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def frontmatter_name(text: str) -> str | None:
    match = re.search(r"(?m)^name:\s*([^\s]+)\s*$", text)
    return match.group(1) if match else None


def main() -> int:
    errors: list[str] = []

    for path in CONTROL_FILES:
        if not path.is_file():
            errors.append(f"missing control file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in FORBIDDEN_CONTROL_TERMS:
            if term in text:
                errors.append(f"{path.relative_to(ROOT)} still references {term}")

    for name in FORBIDDEN_ACTIVE_PATHS:
        if (ROOT / name).exists():
            errors.append(f"legacy active path still exists: {name}")

    skills_root = ROOT / "Skills"
    if not skills_root.is_dir():
        errors.append("missing canonical Skills directory")
    else:
        for item in sorted(skills_root.iterdir()):
            if not item.is_dir():
                continue
            if not NAME_PATTERN.fullmatch(item.name):
                errors.append(f"invalid skill directory name: {item.name}")
                continue
            entry = item / "SKILL.md"
            if not entry.is_file():
                errors.append(f"missing SKILL.md: {item.name}")
                continue
            text = entry.read_text(encoding="utf-8")
            if frontmatter_name(text) != item.name:
                errors.append(f"frontmatter name mismatch: {item.name}")
            for term in FORBIDDEN_CONTROL_TERMS:
                if term in text:
                    errors.append(f"Skills/{item.name}/SKILL.md still references {term}")

    core = ROOT / "Knowledge" / "决策" / "Kit核心原则.md"
    if core.is_file():
        core_text = core.read_text(encoding="utf-8")
        for expected in (
            "人拥有方向",
            "AI 帮助人协作，不代表人承诺",
            "证据决定完成",
            "把边界写具体，把路径留动态",
        ):
            if expected not in core_text:
                errors.append(f"core principle missing invariant: {expected}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    skill_count = len([item for item in skills_root.iterdir() if item.is_dir()])
    print(f"OK: active Kit has no fixed workflow runtime; verified {skill_count} capabilities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
