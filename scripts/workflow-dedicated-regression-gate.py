#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = ROOT / ".workflows" / "blueprints"


def load_blueprint(name: str) -> tuple[Path, dict[str, Any]]:
    path = BLUEPRINT_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"缺少蓝图: {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"蓝图顶层必须是 object: {path.relative_to(ROOT)}")
    return path, data


def blueprint_names() -> list[str]:
    names: list[str] = []
    for path in sorted(BLUEPRINT_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("kind") != "engine-index":
            names.append(path.stem)
    return names


def validate_blueprint(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "scripts/validate-workflow-blueprint.py", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_declared_command(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        shlex.split(command),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="先运行 workflow 蓝图声明的 P0 专属回归，失败即阻断后续通用验证。")
    parser.add_argument("workflows", nargs="*", help="要运行的 workflow；不传则运行所有蓝图声明")
    parser.add_argument("--check-only", action="store_true", help="只校验声明存在与命令格式，不执行命令")
    args = parser.parse_args()

    targets = args.workflows or blueprint_names()
    ok = True
    for name in targets:
        try:
            path, bp = load_blueprint(name)
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            ok = False
            print(f"BLOCKED:workflow-dedicated-regression-gate:{name}: {exc}", file=sys.stderr)
            continue

        validation = validate_blueprint(path)
        if validation.returncode != 0:
            ok = False
            print(f"BLOCKED:workflow-dedicated-regression-gate:{name}: 蓝图校验失败", file=sys.stderr)
            sys.stderr.write(validation.stdout)
            sys.stderr.write(validation.stderr)
            continue

        regression = bp["dedicatedRegression"]
        command = regression["command"]
        if args.check_only:
            print(f"OK:workflow-dedicated-regression-gate:{name}: {command}")
            continue

        proc = run_declared_command(command)
        if proc.returncode != 0:
            ok = False
            print(f"BLOCKED:workflow-dedicated-regression-gate:{name}: {command}", file=sys.stderr)
            sys.stderr.write(proc.stdout)
            sys.stderr.write(proc.stderr)
        else:
            print(f"OK:workflow-dedicated-regression-gate:{name}: {command}")
            sys.stdout.write(proc.stdout)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
