#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKFLOWS = ["ui-change", "bugfix", "task-split-only"]
ROUTE_PHRASES = {
    "ui-change": "帮我改一下 UI",
    "bugfix": "线上报错帮我修bug",
    "task-split-only": "这个技术方案只拆任务",
    "computer-mgmt": "帮我清理电脑缓存",
    "client-dev": "全流程开发一下支付收银台",
}


class SmokeError(Exception):
    pass


def copy_runtime(tmp: Path) -> None:
    shutil.copytree(ROOT / "scripts", tmp / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / ".workflows", tmp / ".workflows")
    shutil.copytree(ROOT / "Templates", tmp / "Templates")
    (tmp / "Contexts/决策").mkdir(parents=True, exist_ok=True)
    (tmp / "Contexts/决策/Skill反馈协议.md").write_text("# Skill反馈协议\n", encoding="utf-8")


def run_json(tmp: Path, cmd: list[str]) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=tmp,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise SmokeError(f"{' '.join(cmd)} failed:\n{proc.stderr or proc.stdout}")
    return json.loads(proc.stdout)


def run_text(tmp: Path, cmd: list[str]) -> str:
    proc = subprocess.run(
        cmd,
        cwd=tmp,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise SmokeError(f"{' '.join(cmd)} failed:\n{proc.stderr or proc.stdout}")
    return proc.stdout


def load_blueprint(tmp: Path, workflow: str) -> dict:
    path = tmp / ".workflows" / "blueprints" / f"{workflow}.json"
    if not path.exists():
        raise SmokeError(f"蓝图不存在: {path.relative_to(tmp)}")
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_plan_folders(tmp: Path, bp: dict) -> None:
    for stage in bp.get("stages", []):
        folder = stage.get("planFolder")
        if folder:
            (tmp / folder).mkdir(parents=True, exist_ok=True)


def assert_route(tmp: Path, workflow: str) -> None:
    phrase = ROUTE_PHRASES.get(workflow)
    if not phrase:
        return
    data = run_json(tmp, ["python3", "scripts/workflow-router-check.py", "--json", phrase])
    if not data.get("matched") or data.get("workflow") != workflow:
        raise SmokeError(f"路由未命中 {workflow}: {data}")


def inject_verdicts(tmp: Path, bp: dict) -> None:
    """为含 verdictPass 的阶段注入一个通过裁决 + 子 Plan verdict: 字段，
    使 smoke-test 覆盖 verdictPass 通过路径（模拟 figma-ui 报完成前落盘的复核裁决）。"""
    for stage in bp.get("stages", []):
        if "verdictPass" not in stage.get("exitCriteria", {}):
            continue
        stage_key = stage.get("key", "")
        folder = tmp / stage.get("planFolder", "")
        if not folder.is_dir():
            continue
        for plan in folder.glob("*.md"):
            text = plan.read_text(encoding="utf-8")
            if f"workflow_stage: {stage_key}" not in text:
                continue
            verdict_path = f"{stage.get('planFolder')}/{plan.stem}.verdict.json"
            (tmp / verdict_path).write_text(
                json.dumps(
                    {"pass": True, "score": 9.5, "summary": "smoke",
                     "deviations": [], "verified_ok": ["smoke"], "reviewed": True},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            # 在 frontmatter 首个 --- 后注入 verdict: 字段
            lines = text.splitlines()
            if lines and lines[0].strip() == "---":
                lines.insert(1, f"verdict: {verdict_path}")
                plan.write_text("\n".join(lines) + "\n", encoding="utf-8")


def smoke_workflow(workflow: str) -> str:
    with tempfile.TemporaryDirectory(prefix=f"aiwk-{workflow}-smoke-") as raw:
        tmp = Path(raw)
        copy_runtime(tmp)
        bp = load_blueprint(tmp, workflow)
        ensure_plan_folders(tmp, bp)

        run_text(tmp, ["python3", "scripts/validate-workflow-blueprint.py", f".workflows/blueprints/{workflow}.json"])
        assert_route(tmp, workflow)

        empty = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--json"])
        if empty.get("current_state") == "done" or not empty.get("blockers"):
            raise SmokeError(f"{workflow} 空仓库应阻塞在首阶段: {empty}")

        run_text(
            tmp,
            [
                "python3",
                "scripts/workflow-plan-init.py",
                "--workflow",
                workflow,
                "--title",
                "smoke",
                "--date",
                "2026-07-03",
                "--all",
                "--include-feedback",
            ],
        )
        inject_verdicts(tmp, bp)
        done = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--json"])
        if done.get("current_state") != "done" or done.get("blockers"):
            raise SmokeError(f"{workflow} 补齐阶段 plan 后未 done: {done}")

    return f"OK:workflow-smoke-test:{workflow}"


def main() -> int:
    parser = argparse.ArgumentParser(description="对 workflow 蓝图做隔离 smoke test。")
    parser.add_argument("workflows", nargs="*", default=DEFAULT_WORKFLOWS)
    args = parser.parse_args()

    ok = True
    for workflow in args.workflows:
        try:
            print(smoke_workflow(workflow))
        except SmokeError as exc:
            ok = False
            print(f"BLOCKED:workflow-smoke-test:{workflow}:{exc}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
