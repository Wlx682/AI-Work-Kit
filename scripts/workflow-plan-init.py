#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = ROOT / ".workflows" / "blueprints"


class InitError(Exception):
    pass


def slugify(value: str) -> str:
    value = re.sub(r"\s+", "-", value.strip())
    value = re.sub(r"[^0-9A-Za-z._\-\u4e00-\u9fff]+", "-", value)
    return value.strip("-") or "未命名"


def load_blueprint(workflow: str) -> dict[str, Any]:
    path = BLUEPRINT_DIR / f"{workflow}.json"
    if not path.exists():
        raise InitError(f"蓝图不存在: .workflows/blueprints/{workflow}.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("kind") == "engine-index":
        raise InitError(f"{workflow} 是 engine index，不是可创建 plan 的工作流")
    if data.get("usesEpic"):
        raise InitError(f"{workflow} 使用 Epic，请走 Epic 模板或 workflow-router 启动")
    return data


def run_gate(workflow: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise InitError(proc.stderr.strip() or proc.stdout.strip() or "workflow-gate 执行失败")
    return json.loads(proc.stdout)


def stage_by_key(bp: dict[str, Any], key: str) -> dict[str, Any] | None:
    for stage in bp.get("stages", []):
        if stage.get("key") == key:
            return stage
    return None


def skill_run(skill: str, plan: str) -> str:
    return f"""## 反馈（skill_run）

```yaml
skill_run:
  skill: {skill}
  plan: {plan}
  date: {date.today().isoformat()}
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "workflow fixture 校验反馈块格式。"
  contexts_missing: []
  contexts_stale: []
```
"""


def render_plan(workflow: str, stage: dict[str, Any], title: str, rel_path: str, include_feedback: bool) -> str:
    skill = stage["skills"][0]
    required_sections = stage.get("requiredSections") or []
    gates = stage.get("exitCriteria") or {}
    sections = "\n".join(f"- [ ] {item}" for item in required_sections) or "- [ ] 按当前阶段补齐必要内容"
    section_blocks = "\n\n".join(
        f"## {item}\n\n本阶段输出将在执行时补齐。"
        for item in required_sections
    )
    gate_lines = "\n".join(f"- `{key}`: {value}" for key, value in gates.items())
    feedback = "\n\n" + skill_run(skill, rel_path) if include_feedback else ""
    required_section_text = f"\n\n{section_blocks}" if section_blocks else ""
    return f"""---
tags: [工作流, {workflow}]
type: plan
category: {stage['planFolder'].split('/')[-1]}
status: 进行中
date: {date.today().isoformat()}
workflow: {workflow}
workflow_stage: {stage['key']}
skill: {skill}
---

# {stage['label']}：{title}

**工作流**：`{workflow}`
**阶段**：`{stage['key']}` / {stage['label']}
**推荐 Skill**：`{skill}`
**存放路径**：`{rel_path}`

---

## 一、输入

- 来源：【粘贴任务背景、链接、日志、Figma 或技术方案】
- 范围：【本阶段只处理什么】
- 非目标：【本阶段不处理什么】

## 二、阶段产出

{sections}
{required_section_text}

## 三、完成门禁

{gate_lines}

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow {workflow} --json`。

## 四、续做

```text
/resume plan={rel_path} 进度=【当前完成情况】
```{feedback}
"""


def plan_path_for(stage: dict[str, Any], title: str, day: str) -> tuple[Path, str]:
    folder = stage["planFolder"]
    prefix = stage.get("planPrefix") or stage["key"]
    filename = f"{day}-{prefix}-{slugify(title)}.md"
    rel = f"{folder}/{filename}"
    return ROOT / rel, rel


def target_stages(bp: dict[str, Any], current: str, all_stages: bool) -> list[dict[str, Any]]:
    if all_stages:
        return list(bp.get("stages", []))
    stage = stage_by_key(bp, current)
    if not stage or current == "done":
        raise InitError(f"当前阶段不可创建 plan: {current}")
    return [stage]


def create_plans(args: argparse.Namespace) -> list[str]:
    bp = load_blueprint(args.workflow)
    gate = run_gate(args.workflow)
    stages = target_stages(bp, gate.get("current_state", ""), args.all)
    day = args.date
    created: list[str] = []
    skipped: list[str] = []
    for stage in stages:
        path, rel = plan_path_for(stage, args.title, day)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not args.force:
            skipped.append(rel)
            continue
        path.write_text(
            render_plan(args.workflow, stage, args.title, rel, args.include_feedback),
            encoding="utf-8",
        )
        created.append(rel)
    for rel in created:
        print(f"created: {rel}")
    for rel in skipped:
        print(f"skipped: {rel}")
    if not created and skipped:
        print("no changes")
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="为无 Epic 轻流程创建阶段 plan 骨架。")
    parser.add_argument("--workflow", required=True, help="轻流程名，如 ui-change / bugfix / task-split-only")
    parser.add_argument("--title", required=True, help="任务标题，会进入文件名")
    parser.add_argument("--date", default=date.today().isoformat(), help="文件名前缀日期，默认今天")
    parser.add_argument("--all", action="store_true", help="创建所有阶段 plan；默认只创建当前阶段 plan")
    parser.add_argument("--force", action="store_true", help="覆盖已存在文件")
    parser.add_argument("--include-feedback", action="store_true", help="测试用：生成可通过 skill_run 门禁的 fixture plan")
    args = parser.parse_args()

    try:
        create_plans(args)
        return 0
    except InitError as exc:
        print(f"BLOCKED:workflow-plan-init:{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
