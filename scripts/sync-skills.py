#!/usr/bin/env python3
"""Synchronize canonical Skills into project or explicitly requested user locations."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Skills"
PROJECT_TARGETS = (
    ROOT / ".cursor" / "skills",
    ROOT / ".claude" / "skills",
    ROOT / ".codex" / "skills",
)
RESERVED = {".system"}


def skill_names(base: Path) -> set[str]:
    if not base.is_dir():
        return set()
    return {
        item.name
        for item in base.iterdir()
        if item.is_dir() and (item / "SKILL.md").is_file()
    }


def equal_trees(left: Path, right: Path) -> bool:
    if not left.is_dir() or not right.is_dir():
        return False
    comparison = filecmp.dircmp(left, right, ignore=[".DS_Store", "__pycache__"])
    if (
        comparison.left_only
        or comparison.right_only
        or comparison.diff_files
        or comparison.funny_files
    ):
        return False
    return all(equal_trees(left / name, right / name) for name in comparison.common_dirs)


def sync_target(target: Path, names: set[str], *, prune: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)
    if prune:
        for item in target.iterdir():
            if item.is_dir() and item.name not in names and item.name not in RESERVED:
                shutil.rmtree(item)
    for name in sorted(names):
        destination = target / name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(SOURCE / name, destination)


def check_target(target: Path, names: set[str], *, allow_extra: bool) -> list[str]:
    errors: list[str] = []
    present = skill_names(target)
    missing = sorted(names - present)
    extra = sorted(present - names - RESERVED) if not allow_extra else []
    if missing:
        errors.append(f"{target}: missing {', '.join(missing)}")
    if extra:
        errors.append(f"{target}: extra {', '.join(extra)}")
    for name in sorted(names & present):
        if not equal_trees(SOURCE / name, target / name):
            errors.append(f"{target / name}: differs from canonical source")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--sync", action="store_true")
    parser.add_argument(
        "--global",
        dest="global_targets",
        action="store_true",
        help="also change user-level Cursor, Claude and Codex skill directories",
    )
    args = parser.parse_args()

    names = skill_names(SOURCE)
    if not names:
        print("ERROR: no canonical Skills found")
        return 1

    targets = [(target, True) for target in PROJECT_TARGETS]
    if args.global_targets:
        user_root = Path.home()
        targets.extend(
            (
                (user_root / ".cursor" / "skills", False),
                (user_root / ".claude" / "skills", False),
                (user_root / ".codex" / "skills", False),
            )
        )

    if args.sync:
        for target, prune in targets:
            sync_target(target, names, prune=prune)
            print(f"synced {len(names)} skills -> {target}")

    errors: list[str] = []
    for target, prune in targets:
        errors.extend(check_target(target, names, allow_extra=not prune))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(names)} canonical skills match {len(targets)} target directories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
