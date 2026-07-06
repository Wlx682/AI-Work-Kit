#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKFLOWS = ["ui-change", "bugfix", "task-split-only", "computer-mgmt", "learning-agent-dev", "client-dev"]
ROUTE_PHRASES = {
    "ui-change": "帮我改一下 UI",
    "bugfix": "线上报错帮我修bug",
    "task-split-only": "这个技术方案只拆任务",
    "computer-mgmt": "帮我清理电脑缓存",
    "learning-agent-dev": "继续创建学习工作流",
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
    (tmp / "Contexts/决策/AI-Work-Kit工作流总览.md").write_text("# AI-Work-Kit工作流总览\n", encoding="utf-8")
    (tmp / "Contexts/决策/Kit核心原则.md").write_text("# Kit核心原则\n", encoding="utf-8")
    (tmp / "Contexts/决策/母子plan投影规则.md").write_text("# 母子plan投影规则\n", encoding="utf-8")


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


def write_fixture(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def skill_run(skill: str, plan: str) -> str:
    return f"""## 反馈（skill_run）

```yaml
skill_run:
  skill: {skill}
  plan: {plan}
  date: 2026-07-03
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "workflow smoke fixture 校验反馈块格式。"
  contexts_missing: []
  contexts_stale: []
```
"""


def wbs_table(rows: list[int]) -> str:
    lines = "\n".join(f"[x] {n}. smoke fixture" for n in rows)
    return "## 三、WBS\n\n```\n" + lines + "\n```\n"


def assert_gate_state(data: dict, workflow: str, expected: str) -> None:
    if data.get("current_state") != expected:
        raise SmokeError(f"{workflow} 期望阶段 {expected}，实际 gate={data}")


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


def workflow_from_utterance(utterance: str) -> str:
    with tempfile.TemporaryDirectory(prefix="aiwk-utterance-route-") as raw:
        tmp = Path(raw)
        copy_runtime(tmp)
        data = run_json(tmp, ["python3", "scripts/workflow-router-check.py", "--json", utterance])
    if not data.get("matched") or not data.get("workflow"):
        raise SmokeError(f"需求未命中 workflow: {data}")
    return str(data["workflow"])


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


def create_client_dev_epic(tmp: Path) -> str:
    epic_rel = "Plans/Epic/smoke.md"
    write_fixture(
        tmp / epic_rel,
        """
---
project: smoke
workflow: client-dev
含业务逻辑: 是
p0_open: 0
plans:
  requirement: Plans/需求分析/smoke.md
  architecture: Plans/技术方案/smoke.md
  test: Plans/自动化测试/smoke.md
  development: Plans/功能开发/smoke.md
---

# Smoke Epic

## 三、WBS

```
[ ] 1. 事件风暴完成
[ ] 2. 实例化需求完成
[ ] 3. 技术方案完成
[ ] 4. 验收测试先行完成
[ ] 5. Domain 完成
[ ] 6. Data 完成
[ ] 7. UI 完成
[ ] 8. 交互完成
[ ] 9. 单测完成
[ ] 10. 联调完成
[ ] 11. 非功能验证完成
```
""",
    )
    return epic_rel


def create_client_requirement(tmp: Path, epic_rel: str) -> None:
    req_body = "需求背景：" + ("这是用于 workflow smoke 的需求说明。" * 45)
    write_fixture(
        tmp / "Plans/需求分析/smoke.md",
        f"""
---
status: 已采纳
p0_open: 0
epic: {epic_rel}
---

# 需求分析 smoke

{req_body}

## 七、边界情况清单

- 完整子 Plan 存在时，client-dev gate 应进入 done。
- 指定 Epic 时，不应串到其他 plan。

## 八、异常流程矩阵

| 异常 | 触发条件 | 预期处理 |
|------|----------|----------|
| 缺少 skill_run | 阶段完成未追加反馈 | gate 阻塞 |

## 九、验收标准

| # | 验收项 | 锚定事件 | Given | When | Then | 优先级 |
|---|--------|----------|-------|------|------|--------|
| AC1 | 完整蓝图进入 done | 已创建完整子 Plan | 运行 gate | 查看 JSON | current_state=done | P0 |
| AC1-反 | 指定 Epic 不串 plan | 指定 Epic | 运行 gate | 查看 JSON | 只扫描 smoke plan | P0 |
| AC2 | run gate 记录通过事件 | 已启动 run | 执行 gate | 查看事件 | 存在 gate_pass | P1 |

{wbs_table([1, 2])}

{skill_run("requirement-analyst", "Plans/需求分析/smoke.md")}
""",
    )


def create_client_architecture(tmp: Path, epic_rel: str) -> None:
    write_fixture(
        tmp / "Plans/技术方案/smoke.md",
        f"""
---
status: 已采纳
epic: {epic_rel}
---

# 技术方案 smoke

## 二、模块边界

- Gate 引擎：读蓝图和子 Plan 文件系统事实，产出阶段判定。
- Run 引擎：记录工作流运行态与 gate 事件。

## 三、数据模型

| 实体 | 字段 | 说明 |
|------|------|------|
| Epic | plans, workflow | 工作流数据上下文 |
| Stage | key, exitCriteria | 蓝图阶段定义 |

## 四、API Schema

- `workflow-gate.sh --workflow client-dev --epic <path> --json`
- `workflow-run.py gate --run <path>`

{wbs_table([3])}

{skill_run("architecture-design-assistant", "Plans/技术方案/smoke.md")}
""",
    )


def create_client_test_plan(tmp: Path, epic_rel: str) -> None:
    write_fixture(
        tmp / "Plans/自动化测试/smoke.md",
        f"""
---
epic: {epic_rel}
---

# 自动化测试 smoke

## 二、用例映射（链需求验收标准）

| 验收项 # | 测试用例 ID | 类型 | 描述 | 状态 |
|----------|-------------|------|------|------|
| AC1 | IT-001 | 集成 | 覆盖完整蓝图 done 判断 | 已实现 |
| AC1-反 | IT-002 | 集成 | 覆盖指定 Epic 不串 plan | 已实现 |
| AC2 | IT-003 | 集成 | 覆盖 run gate 事件记录 | 已实现 |

{wbs_table([4])}

{skill_run("test-generator", "Plans/自动化测试/smoke.md")}
""",
    )


def write_client_development(tmp: Path, epic_rel: str, rows: list[int], skill: str) -> None:
    write_fixture(
        tmp / "Plans/功能开发/smoke.md",
        f"""
---
epic: {epic_rel}
requirement_plan: Plans/需求分析/smoke.md
p0_open: 0
含业务逻辑: 是
---

# 功能开发 smoke

## 一、需求分析

- [[Plans/需求分析/smoke.md]]

## 二、技术方案

- [[Plans/技术方案/smoke.md]]

{wbs_table(rows)}

## 五、实施切片

| # | 输入 | 输出 | 覆盖 AC | 验收 | 预估 | 阻塞 |
|---|------|------|---------|------|------|------|
| 5 | 需求 | Domain | AC1, AC1-反 | gate done | 0.5d | - |
| 6 | 运行态 | Run gate | AC2 | gate_pass event | 0.5d | - |

{skill_run(skill, "Plans/功能开发/smoke.md")}
""",
    )


def create_learning_epic(tmp: Path) -> str:
    epic_rel = "Plans/Epic/learning-smoke.md"
    write_fixture(
        tmp / epic_rel,
        """
---
project: learning-smoke
workflow: learning-agent-dev
topic: 智能体路由MVP
repo: /Users/wanglongxiang/git/agent-workflow-dev
branch: main
含业务逻辑: 否
p0_open: 0
plans:
  topic: Plans/学习/learning-topic.md
  theory: Plans/学习/learning-theory.md
  test: Plans/学习/learning-test.md
  project_setup: Plans/学习/learning-project.md
  tool_build: Plans/学习/learning-tool.md
  integration_run: Plans/学习/learning-integration.md
  retro: Plans/学习/learning-retro.md
---

# Learning Smoke

## 三、WBS

```
[ ] 1. 选题与边界
[ ] 2. 理论输入
[ ] 3. 测试先行
[ ] 4. 工程与技术选型
[ ] 5. 工具实现
[ ] 6. 接入试跑
[ ] 7. 效果复盘
```
""",
    )
    return epic_rel


def write_learning_stage(tmp: Path, rel: str, stage: str, wbs: int) -> None:
    write_fixture(
        tmp / rel,
        f"""
---
status: 已采纳
workflow: learning-agent-dev
workflow_stage: {stage}
epic: Plans/Epic/learning-smoke.md
---

# {stage} smoke

## 三、WBS

```
[x] {wbs}. smoke
```

{skill_run("learn-assistant", rel)}
""",
    )


def smoke_epic_workflow(tmp: Path, workflow: str, bp: dict) -> None:
    if workflow == "learning-agent-dev":
        bootstrap = run_json(
            tmp,
            ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--project", "不存在的项目", "--json"],
        )
        if bootstrap.get("next_state") != "bootstrap-epic" or not bootstrap.get("blockers"):
            raise SmokeError(f"{workflow} 无 Epic 时应要求 bootstrap: {bootstrap}")

        epic_rel = create_learning_epic(tmp)
        gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
        assert_gate_state(gate, workflow, "topic")

        stage_specs = [
            ("Plans/学习/learning-topic.md", "topic", 1, "theory"),
            ("Plans/学习/learning-theory.md", "theory", 2, "test-first"),
            ("Plans/学习/learning-test.md", "test-first", 3, "project-setup"),
            ("Plans/学习/learning-project.md", "project-setup", 4, "tool-build"),
            ("Plans/学习/learning-tool.md", "tool-build", 5, "integration-run"),
            ("Plans/学习/learning-integration.md", "integration-run", 6, "retro"),
            ("Plans/学习/learning-retro.md", "retro", 7, "done"),
        ]
        for rel, stage, wbs, expected_next in stage_specs:
            write_learning_stage(tmp, rel, stage, wbs)
            gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
            assert_gate_state(gate, workflow, expected_next)
        if gate.get("blockers"):
            raise SmokeError(f"{workflow} 完整推进后仍有 blockers: {gate}")
        return

    if workflow != "client-dev":
        raise SmokeError(f"暂未定义 Epic 型 smoke fixture: {workflow}")

    bootstrap = run_json(
        tmp,
        ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--project", "不存在的项目", "--json"],
    )
    if bootstrap.get("next_state") != "bootstrap-epic" or not bootstrap.get("blockers"):
        raise SmokeError(f"{workflow} 无 Epic 时应要求 bootstrap: {bootstrap}")

    epic_rel = create_client_dev_epic(tmp)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "requirement")
    if not any(("子 Plan 未创建" in item or "子 Plan 不存在" in item) for item in gate.get("blockers", [])):
        raise SmokeError(f"{workflow} 新 Epic 应阻塞在需求子 Plan: {gate}")

    create_client_requirement(tmp, epic_rel)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "architecture")

    create_client_architecture(tmp, epic_rel)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "test-first")

    create_client_test_plan(tmp, epic_rel)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "split")

    write_client_development(tmp, epic_rel, [5], "task-splitter")
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "development")
    if not any("WBS 切片" in item for item in gate.get("blockers", [])):
        raise SmokeError(f"{workflow} 拆分后应阻塞在开发 WBS: {gate}")

    write_client_development(tmp, epic_rel, [5, 6, 7, 8, 9, 10, 11], "feature-dev-assistant")
    done = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(done, workflow, "done")
    if done.get("blockers"):
        raise SmokeError(f"{workflow} 完整真实推进后仍有 blockers: {done}")

    run_rel = run_text(
        tmp,
        ["python3", "scripts/workflow-run.py", "start", "--workflow", workflow, "--epic", epic_rel],
    ).strip()
    run_text(tmp, ["python3", "scripts/workflow-run.py", "gate", "--run", run_rel])
    run_file = tmp / run_rel
    run_text_body = run_file.read_text(encoding="utf-8")
    if 'result: "pass"' not in run_text_body:
        raise SmokeError(f"{workflow} run gate 未记录 pass: {run_rel}")
    event_rel = run_text_body.split('events: "')[1].split('"')[0]
    event_types = [
        json.loads(line)["type"]
        for line in (tmp / event_rel).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if "gate_pass" not in event_types:
        raise SmokeError(f"{workflow} run 事件缺 gate_pass: {event_types}")


def smoke_lightweight_workflow(tmp: Path, workflow: str, bp: dict) -> None:
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--json"])
    if gate.get("current_state") == "done" or not gate.get("blockers"):
        raise SmokeError(f"{workflow} 空仓库应阻塞在首阶段: {gate}")

    for _ in bp.get("stages", []):
        current = gate.get("current_state")
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
                "--include-feedback",
            ],
        )
        inject_verdicts(tmp, bp)
        next_gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--json"])
        if next_gate.get("current_state") == current and next_gate.get("blockers"):
            raise SmokeError(f"{workflow} 创建 {current} 阶段 plan 后没有推进: {next_gate}")
        gate = next_gate
        if gate.get("current_state") == "done":
            return

    if gate.get("current_state") != "done" or gate.get("blockers"):
        raise SmokeError(f"{workflow} 逐阶段推进后未 done: {gate}")


def smoke_workflow(workflow: str) -> str:
    with tempfile.TemporaryDirectory(prefix=f"aiwk-{workflow}-smoke-") as raw:
        tmp = Path(raw)
        copy_runtime(tmp)
        bp = load_blueprint(tmp, workflow)
        ensure_plan_folders(tmp, bp)

        run_text(tmp, ["python3", "scripts/validate-workflow-blueprint.py", f".workflows/blueprints/{workflow}.json"])
        assert_route(tmp, workflow)

        if bp.get("usesEpic"):
            smoke_epic_workflow(tmp, workflow, bp)
            return f"OK:workflow-smoke-test:{workflow}"

        smoke_lightweight_workflow(tmp, workflow, bp)

    return f"OK:workflow-smoke-test:{workflow}"


def main() -> int:
    parser = argparse.ArgumentParser(description="对 workflow 蓝图做隔离 smoke test。")
    parser.add_argument("--utterance", help="从一条自然语言需求入口开始，先路由再跑完整 workflow")
    parser.add_argument("workflows", nargs="*", default=DEFAULT_WORKFLOWS)
    args = parser.parse_args()

    if args.utterance:
        try:
            workflow = workflow_from_utterance(args.utterance)
            print(smoke_workflow(workflow))
            return 0
        except SmokeError as exc:
            print(f"BLOCKED:workflow-smoke-test:{args.utterance}:{exc}")
            return 1

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
