#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import gate_parse


ROOT = Path(__file__).resolve().parent.parent


def resolve_path(raw: str | None) -> Path | None:
    if not raw:
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = ROOT / p
    if p.suffix != ".md":
        p = p.with_suffix(".md")
    return p


def fail(message: str) -> None:
    print(f"BLOCKED:traceability:{message}", file=sys.stderr)


def warn(message: str) -> None:
    print(f"WARN:traceability:{message}", file=sys.stderr)


def require_file(label: str, path: Path | None) -> Path:
    if path is None:
        raise FileNotFoundError(f"缺少 {label} plan 路径")
    if not path.exists():
        raise FileNotFoundError(f"{label} plan 不存在: {path}")
    return path


def missing_test_coverage(req: Path, test: Path) -> tuple[list[str], list[str]]:
    acs = gate_parse.parse_ac_table(req)
    tests = gate_parse.parse_test_map(test)
    blockers: list[str] = []
    warnings: list[str] = []
    for ac_id, meta in sorted(acs.items()):
        if tests.get(ac_id):
            continue
        priority = meta.get("priority", "P2")
        message = f"{ac_id}({priority}) 无测试覆盖"
        if priority == "P0":
            blockers.append(message)
        else:
            warnings.append(message)
    return blockers, warnings


def missing_dev_coverage(req: Path, dev: Path) -> tuple[list[str], list[str]]:
    acs = gate_parse.parse_ac_table(req)
    coverage = gate_parse.parse_dev_ac_coverage(dev)
    blockers: list[str] = []
    warnings: list[str] = []
    for ac_id, meta in sorted(acs.items()):
        priority = meta.get("priority", "P2")
        if priority != "P0" or coverage.get(ac_id):
            continue
        blockers.append(f"{ac_id}({priority}) 无开发任务覆盖")
    return blockers, warnings


def paths_from_epic(epic: Path) -> dict[str, Path | None]:
    plans = gate_parse.read_plan_index(epic)
    return {
        "req": resolve_path(plans.get("requirement")),
        "test": resolve_path(plans.get("test")),
        "dev": resolve_path(plans.get("development")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check AC traceability across requirement, test, and development plans.")
    parser.add_argument("--epic", help="Epic plan path; reads plans.requirement/test/development")
    parser.add_argument("--req", help="Requirement plan path")
    parser.add_argument("--test", help="Test plan path")
    parser.add_argument("--dev", help="Development plan path")
    parser.add_argument("--check", choices=["test", "dev", "all"], default="all")
    args = parser.parse_args()

    req = resolve_path(args.req)
    test = resolve_path(args.test)
    dev = resolve_path(args.dev)
    if args.epic:
        epic = require_file("Epic", resolve_path(args.epic))
        from_epic = paths_from_epic(epic)
        req = req or from_epic["req"]
        test = test or from_epic["test"]
        dev = dev or from_epic["dev"]

    blockers: list[str] = []
    warnings: list[str] = []
    try:
        if args.check in {"test", "all"}:
            b, w = missing_test_coverage(require_file("需求", req), require_file("测试", test))
            blockers.extend(b)
            warnings.extend(w)
        if args.check in {"dev", "all"} and (args.check == "dev" or dev is not None):
            b, w = missing_dev_coverage(require_file("需求", req), require_file("功能开发", dev))
            blockers.extend(b)
            warnings.extend(w)
    except FileNotFoundError as exc:
        fail(str(exc))
        return 1

    for item in warnings:
        warn(item)
    for item in blockers:
        fail(item)
    if blockers:
        return 1
    print("OK:traceability")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
