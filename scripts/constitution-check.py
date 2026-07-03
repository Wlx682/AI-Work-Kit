#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import gate_parse


ROOT = Path(__file__).resolve().parent.parent


def resolve_path(raw: str | None, *, markdown: bool = False) -> Path | None:
    if not raw:
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = ROOT / p
    if markdown and p.suffix != ".md":
        p = p.with_suffix(".md")
    return p


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def workflow_from_epic(epic: Path) -> str:
    return gate_parse.read_frontmatter(epic).get("workflow") or "client-dev"


def load_blueprint(workflow: str) -> dict[str, Any]:
    path = ROOT / ".workflows" / "blueprints" / f"{workflow}.json"
    if not path.exists():
        raise FileNotFoundError(f"蓝图不存在: {path.relative_to(ROOT)}")
    return load_json(path)


def load_constitution(blueprint: dict[str, Any]) -> tuple[Path | None, dict[str, Any] | None]:
    raw = blueprint.get("constitution")
    if not raw:
        return None, None
    path = resolve_path(str(raw))
    if path is None or not path.exists():
        raise FileNotFoundError(f"constitution 文件不存在: {raw}")
    return path, load_json(path)


def run_workflow_gate(workflow: str, epic: Path | None) -> dict[str, Any]:
    cmd = ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--json"]
    if epic is not None:
        cmd.extend(["--epic", str(epic)])
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "workflow-gate 执行失败")
    return json.loads(proc.stdout)


def rule_status(rule: dict[str, Any], gate: dict[str, Any]) -> str:
    checked_by = str(rule.get("checkedBy", ""))
    blockers = gate.get("blockers", []) or []
    if checked_by.startswith("deferred:"):
        return "indexed"
    if not blockers:
        return "ok"
    rule_id = str(rule.get("id", ""))
    needles = {
        "tdd_first": ["验收测试先行", "WBS 切片 4"],
        "skill_run_required": ["skill_run"],
        "epic_required": ["无 Epic"],
        "traceability": ["testTraceability", "devTraceability", "traceability"],
        "wbs_single_truth": ["母子 plan 投影", "epic-projection"],
    }.get(rule_id, [rule_id])
    return "blocked" if any(any(needle in item for needle in needles) for item in blockers) else "delegated"


def build_report(workflow: str, epic: Path | None) -> dict[str, Any]:
    blueprint = load_blueprint(workflow)
    constitution_path, constitution = load_constitution(blueprint)
    if constitution is None:
        return {
            "workflow": workflow,
            "constitution": None,
            "status": "not-configured",
            "rules": [],
            "gate": None,
        }
    gate = run_workflow_gate(workflow, epic)
    rules = []
    for rule in constitution.get("rules", []):
        item = dict(rule)
        item["status"] = rule_status(rule, gate)
        rules.append(item)
    return {
        "workflow": workflow,
        "constitution": str(constitution_path.relative_to(ROOT)) if constitution_path else None,
        "status": "blocked" if gate.get("blockers") else "ok",
        "current_state": gate.get("current_state"),
        "next_state": gate.get("next_state"),
        "blockers": gate.get("blockers", []),
        "rules": rules,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate client-dev constitution rules from existing gate results.")
    parser.add_argument("--epic", help="Epic plan path")
    parser.add_argument("--workflow", help="Workflow name; defaults to Epic frontmatter workflow or client-dev")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    epic = resolve_path(args.epic, markdown=True)
    if epic is not None and not epic.exists():
        print(f"BLOCKED:constitution:Epic 不存在: {epic}", file=sys.stderr)
        return 1
    workflow = args.workflow or (workflow_from_epic(epic) if epic else "client-dev")
    try:
        report = build_report(workflow, epic)
    except (FileNotFoundError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"BLOCKED:constitution:{exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"# constitution-check: {report['workflow']}")
        print(f"constitution: {report['constitution'] or 'not-configured'}")
        print(f"status: {report['status']}")
        for blocker in report.get("blockers", []):
            print(f"- BLOCKED: {blocker}")
        for rule in report.get("rules", []):
            print(f"- {rule['id']}: {rule['status']} ({rule['checkedBy']})")
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
