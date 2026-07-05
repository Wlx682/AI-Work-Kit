#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = ROOT / ".workflows" / "blueprints"
RUN_DIR = ROOT / ".workflows" / "runs"
EVENT_DIR = ROOT / ".workflows" / "events"


def slugify(value: str) -> str:
    value = re.sub(r"\s+", "-", value.strip())
    value = re.sub(r"[^0-9A-Za-z._\-\u4e00-\u9fff]+", "-", value)
    return value.strip("-") or "run"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def yaml_value(value: str) -> Any:
    value = value.strip()
    if value == "null":
        return None
    if value == "[]":
        return []
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def write_run_file(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        f"run_id: {yaml_scalar(payload['run_id'])}",
        f"workflow_id: {yaml_scalar(payload['workflow_id'])}",
        f"workflow_version: {yaml_scalar(payload['workflow_version'])}",
        f"epic: {yaml_scalar(payload.get('epic'))}",
        f"project: {yaml_scalar(payload.get('project'))}",
        f"status: {yaml_scalar(payload['status'])}",
        f"current_stage: {yaml_scalar(payload['current_stage'])}",
        f"started_at: {yaml_scalar(payload['started_at'])}",
        f"updated_at: {yaml_scalar(payload['updated_at'])}",
        f"events: {yaml_scalar(payload['events'])}",
    ]
    for key in ("stage_history", "decisions", "gate_checks"):
        items = payload.get(key) or []
        if not items:
            lines.append(f"{key}: []")
            continue
        lines.append(f"{key}:")
        for item in items:
            lines.append("  -")
            for item_key, item_value in item.items():
                lines.append(f"    {item_key}: {yaml_scalar(item_value)}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def load_run_file(path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    current_list: str | None = None
    current_item: dict[str, Any] | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        top = re.match(r"^([A-Za-z_]+):\s*(.*)$", raw)
        if top:
            current_list = None
            current_item = None
            key, value = top.group(1), top.group(2)
            if value:
                payload[key] = yaml_value(value)
            else:
                payload[key] = []
                current_list = key
            continue
        if raw.startswith("  -") and current_list:
            current_item = {}
            payload[current_list].append(current_item)
            first = raw[3:].strip()
            if first:
                kv = re.match(r"^([A-Za-z_]+):\s*(.*)$", first)
                if kv:
                    current_item[kv.group(1)] = yaml_value(kv.group(2))
            continue
        nested = re.match(r"^    ([A-Za-z_]+):\s*(.*)$", raw)
        if nested and current_item is not None:
            current_item[nested.group(1)] = yaml_value(nested.group(2))

    for key in ("stage_history", "decisions"):
        if not isinstance(payload.get(key), list):
            payload[key] = []
    return payload


def load_blueprint(workflow: str) -> dict[str, Any]:
    path = BLUEPRINT_DIR / f"{workflow}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("kind") == "engine-index":
        raise SystemExit(f"BLOCKED:workflow-run: {workflow} 是 engine index，不是可运行蓝图")
    return data


def resolve_run_path(run: str) -> Path:
    path = Path(run)
    if not path.is_absolute():
        path = ROOT / path
    if path.exists():
        return path
    candidate = RUN_DIR / run
    if candidate.exists():
        return candidate
    candidate = RUN_DIR / f"{run}.run.yaml"
    if candidate.exists():
        return candidate
    raise SystemExit(f"BLOCKED:workflow-run: run 不存在: {run}")


def append_event(payload: dict[str, Any], event_type: str, **extra: Any) -> None:
    event_path = ROOT / str(payload["events"])
    event_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "type": event_type,
        "run_id": payload["run_id"],
        "workflow_id": payload["workflow_id"],
        "current_stage": payload["current_stage"],
        "status": payload["status"],
        "created_at": payload["updated_at"],
        **extra,
    }
    with event_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def next_stage(blueprint: dict[str, Any], stage: str) -> str:
    for item in blueprint.get("stages", []):
        if item.get("key") == stage:
            return item.get("next") or "done"
    raise SystemExit(f"BLOCKED:workflow-run: 当前阶段不在蓝图中: {stage}")


def validate_stage(blueprint: dict[str, Any], stage: str) -> None:
    valid = {item.get("key") for item in blueprint.get("stages", [])} | {"done"}
    if stage not in valid:
        raise SystemExit(f"BLOCKED:workflow-run: 阶段不在蓝图中: {stage}")


def update_run(path: Path, payload: dict[str, Any], event_type: str, **event_extra: Any) -> int:
    payload["updated_at"] = now_iso()
    append_event(payload, event_type, **event_extra)
    write_run_file(path, payload)
    print(str(path.relative_to(ROOT)))
    return 0


def start_run(args: argparse.Namespace) -> int:
    blueprint = load_blueprint(args.workflow)
    first_stage = blueprint["stages"][0]["key"]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    label = args.project or (Path(args.epic).stem if args.epic else blueprint["name"])
    run_id = f"{timestamp}-{blueprint['name']}-{slugify(label)}"
    run_rel = f".workflows/runs/{run_id}.run.yaml"
    event_rel = f".workflows/events/{run_id}.events.jsonl"

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    EVENT_DIR.mkdir(parents=True, exist_ok=True)

    now = now_iso()
    payload = {
        "run_id": run_id,
        "workflow_id": blueprint["name"],
        "workflow_version": blueprint["version"],
        "epic": args.epic,
        "project": args.project,
        "status": "running",
        "current_stage": first_stage,
        "started_at": now,
        "updated_at": now,
        "events": event_rel,
        "stage_history": [],
        "decisions": [],
        "gate_checks": [],
    }
    write_run_file(ROOT / run_rel, payload)

    event = {
        "type": "workflow_run_started",
        "run_id": run_id,
        "workflow_id": blueprint["name"],
        "workflow_version": blueprint["version"],
        "current_stage": first_stage,
        "epic": args.epic,
        "project": args.project,
        "created_at": now,
    }
    (ROOT / event_rel).write_text(json.dumps(event, ensure_ascii=False) + "\n", encoding="utf-8")
    print(run_rel)
    return 0


def advance_run(args: argparse.Namespace) -> int:
    path = resolve_run_path(args.run)
    payload = load_run_file(path)
    if payload.get("status") in {"blocked", "paused"}:
        raise SystemExit(f"BLOCKED:workflow-run: 当前 status={payload.get('status')}，请先 resume")
    if payload.get("status") == "done":
        raise SystemExit("BLOCKED:workflow-run: run 已完成")

    blueprint = load_blueprint(str(payload["workflow_id"]))
    from_stage = str(payload["current_stage"])
    to_stage = args.stage or next_stage(blueprint, from_stage)
    validate_stage(blueprint, to_stage)

    payload["current_stage"] = to_stage
    payload["status"] = "done" if to_stage == "done" else "running"
    payload["stage_history"].append(
        {"at": now_iso(), "from": from_stage, "to": to_stage, "reason": args.reason}
    )
    return update_run(
        path,
        payload,
        "workflow_run_advanced",
        from_stage=from_stage,
        to_stage=to_stage,
        reason=args.reason,
    )


def block_run(args: argparse.Namespace) -> int:
    path = resolve_run_path(args.run)
    payload = load_run_file(path)
    if payload.get("status") == "done":
        raise SystemExit("BLOCKED:workflow-run: run 已完成，不能标记阻塞")
    payload["status"] = "blocked"
    payload["decisions"].append(
        {"at": now_iso(), "type": "blocked", "stage": payload["current_stage"], "reason": args.reason}
    )
    return update_run(path, payload, "workflow_run_blocked", reason=args.reason)


def pause_run(args: argparse.Namespace) -> int:
    path = resolve_run_path(args.run)
    payload = load_run_file(path)
    if payload.get("status") == "done":
        raise SystemExit("BLOCKED:workflow-run: run 已完成，不能暂停")
    payload["status"] = "paused"
    payload["decisions"].append(
        {"at": now_iso(), "type": "paused", "stage": payload["current_stage"], "reason": args.reason}
    )
    return update_run(path, payload, "workflow_run_paused", reason=args.reason)


def resume_run(args: argparse.Namespace) -> int:
    path = resolve_run_path(args.run)
    payload = load_run_file(path)
    if payload.get("status") == "done":
        raise SystemExit("BLOCKED:workflow-run: run 已完成，不能恢复")
    previous_status = payload.get("status")
    payload["status"] = "running"
    payload["decisions"].append(
        {"at": now_iso(), "type": "resumed", "stage": payload["current_stage"], "reason": args.reason}
    )
    return update_run(
        path,
        payload,
        "workflow_run_resumed",
        previous_status=previous_status,
        reason=args.reason,
    )


def done_run(args: argparse.Namespace) -> int:
    path = resolve_run_path(args.run)
    payload = load_run_file(path)
    from_stage = str(payload["current_stage"])
    if from_stage != "done":
        payload["stage_history"].append(
            {"at": now_iso(), "from": from_stage, "to": "done", "reason": args.reason}
        )
    payload["current_stage"] = "done"
    payload["status"] = "done"
    return update_run(path, payload, "workflow_run_done", from_stage=from_stage, reason=args.reason)


def gate_run(args: argparse.Namespace) -> int:
    """对指定 run 跑一次门禁判定，把 pass/fail + reason 追加成事件与 gate_checks 轨迹。
    只读门禁（调 workflow-gate.sh --json），不改门禁逻辑；给『现看现判』的判定留痕，
    使『某阶段门禁历史上判过几次、为何不过』可回放。"""
    path = resolve_run_path(args.run)
    payload = load_run_file(path)
    stage = str(payload["current_stage"])

    gate_cmd = ["bash", str(ROOT / "scripts" / "workflow-gate.sh"),
                "--workflow", str(payload["workflow_id"]), "--json"]
    epic = payload.get("epic")
    if epic:
        gate_cmd += ["--epic", str(epic)]
    proc = subprocess.run(gate_cmd, capture_output=True, text=True)
    try:
        gate = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise SystemExit(f"BLOCKED:workflow-run: 门禁无有效 JSON 输出：{proc.stderr.strip() or proc.stdout.strip()}")

    blockers = gate.get("blockers") or []
    passed = not blockers
    gate_stage = gate.get("current_state", stage)
    payload.setdefault("gate_checks", []).append(
        {"at": now_iso(), "stage": gate_stage, "result": "pass" if passed else "fail",
         "blocker_count": len(blockers)}
    )
    if passed:
        return update_run(path, payload, "gate_pass", stage=gate_stage)
    return update_run(path, payload, "gate_fail", stage=gate_stage,
                      reason="; ".join(str(b) for b in blockers))


def main() -> int:
    parser = argparse.ArgumentParser(description="创建或维护 AI-Work-Kit workflow run 实例。")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="创建一次 workflow run")
    start.add_argument("--workflow", required=True, help="蓝图 name，例如 client-dev")
    start.add_argument("--epic", help="关联 Epic 路径")
    start.add_argument("--project", help="无 Epic 或新需求时的项目名")
    start.set_defaults(func=start_run)

    advance = sub.add_parser("advance", help="推进到下一阶段或指定阶段")
    advance.add_argument("--run", required=True, help="run 文件路径或 run_id")
    advance.add_argument("--stage", help="目标阶段；默认读取蓝图 next")
    advance.add_argument("--reason", default="", help="推进原因")
    advance.set_defaults(func=advance_run)

    block = sub.add_parser("block", help="标记 run 阻塞")
    block.add_argument("--run", required=True, help="run 文件路径或 run_id")
    block.add_argument("--reason", required=True, help="阻塞原因")
    block.set_defaults(func=block_run)

    pause = sub.add_parser("pause", help="暂停 run")
    pause.add_argument("--run", required=True, help="run 文件路径或 run_id")
    pause.add_argument("--reason", default="", help="暂停原因")
    pause.set_defaults(func=pause_run)

    resume = sub.add_parser("resume", help="恢复 blocked/paused run")
    resume.add_argument("--run", required=True, help="run 文件路径或 run_id")
    resume.add_argument("--reason", default="", help="恢复原因")
    resume.set_defaults(func=resume_run)

    done = sub.add_parser("done", help="标记 run 完成")
    done.add_argument("--run", required=True, help="run 文件路径或 run_id")
    done.add_argument("--reason", default="", help="完成原因")
    done.set_defaults(func=done_run)

    gate = sub.add_parser("gate", help="对 run 跑一次门禁判定并留痕（gate_pass/gate_fail 事件）")
    gate.add_argument("--run", required=True, help="run 文件路径或 run_id")
    gate.set_defaults(func=gate_run)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
