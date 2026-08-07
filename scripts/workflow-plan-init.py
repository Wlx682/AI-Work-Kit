#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import gate_parse


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
    return data


def run_gate(workflow: str, epic: str | None = None, project: str | None = None) -> dict[str, Any]:
    command = ["bash", "scripts/workflow-gate.sh", "--workflow", workflow]
    if epic:
        command.extend(["--epic", epic])
    if project:
        command.extend(["--project", project])
    command.append("--json")
    proc = subprocess.run(
        command,
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


def skill_run(skill: str, plan: str, stage: str | None = None) -> str:
    stage_line = f"  workflow_stage: {stage}\n" if stage else ""
    return f"""## 反馈（skill_run）

```yaml
skill_run:
  skill: {skill}
{stage_line}  plan: {plan}
  date: {date.today().isoformat()}
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "workflow fixture 校验反馈块格式。"
  contexts_missing: []
  contexts_stale: []
```
"""


def render_plan(
    workflow: str,
    stage: dict[str, Any],
    title: str,
    day: str,
    rel_path: str,
    include_feedback: bool,
) -> str:
    skill = stage["skills"][0]
    required_sections = stage.get("requiredSections") or []
    gates = stage.get("exitCriteria") or {}
    sections = "\n".join(f"- [ ] {item}" for item in required_sections) or "- [ ] 按当前阶段补齐必要内容"
    section_blocks = "\n\n".join(
        f"## {item}\n\n本阶段输出将在执行时补齐。"
        for item in required_sections
    )
    gate_lines = "\n".join(f"- `{key}`: {value}" for key, value in gates.items())
    extra_frontmatter = ""
    if gates.get("storyScopeReady"):
        story_index = f"{rel_path[:-3]}.stories.json" if rel_path.endswith(".md") else f"{rel_path}.stories.json"
        extra_frontmatter = f"story_index: {story_index}\n"
    feedback = "\n\n" + skill_run(skill, rel_path, stage["key"]) if include_feedback else ""

    required_section_text = f"\n\n{section_blocks}" if section_blocks else ""
    return f"""---
tags: [工作流, {workflow}]
type: plan
category: {stage['planFolder'].split('/')[-1]}
status: 进行中
date: {day}
workflow: {workflow}
workflow_stage: {stage['key']}
task_id: {workflow}-{day}-{slugify(title)}
task_title: {title}
skill: {skill}
{extra_frontmatter}---

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


def render_stage_template(
    workflow: str,
    stage: dict[str, Any],
    title: str,
    day: str,
    rel_path: str,
    include_feedback: bool,
    epic: Path | None = None,
) -> str:
    template_raw = str(stage.get("template") or "").strip()
    if not template_raw:
        return render_plan(workflow, stage, title, day, rel_path, include_feedback)
    template = ROOT / template_raw
    if not template.is_file():
        raise InitError(f"阶段模板不存在: {template_raw}")
    content = template.read_text(encoding="utf-8")
    replacements = {
        "{{date}}": day,
        "{{title}}": title,
        "{{title-kebab}}": slugify(title),
        "{{plan-path}}": rel_path,
        "{{plan-stem}}": str(Path(rel_path).with_suffix("")),
        "{{epic-path}}": str(epic.relative_to(ROOT)) if epic else "",
    }
    if epic:
        for field, value in gate_parse.read_plan_index(epic).items():
            replacements[f"{{{{plan:{field}}}}}"] = value
    for source, value in replacements.items():
        content = content.replace(source, value)
    if include_feedback:
        content = content.rstrip() + "\n\n" + skill_run(stage["skills"][0], rel_path, stage["key"])
    return content.rstrip() + "\n"


def plan_path_for(stage: dict[str, Any], title: str, day: str) -> tuple[Path, str]:
    folder = stage["planFolder"]
    prefix = stage.get("planPrefix") or stage["key"]
    filename = f"{day}-{prefix}-{slugify(title)}.md"
    rel = f"{folder}/{filename}"
    return ROOT / rel, rel


def resolve_epic(raw: str) -> tuple[Path, str]:
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    try:
        rel = str(path.relative_to(ROOT.resolve()))
    except ValueError as exc:
        raise InitError(f"Epic 超出工作区: {raw}") from exc
    if not path.is_file():
        raise InitError(f"Epic 不存在: {rel}")
    return path, rel


def insert_epic_plan_path(epic: Path, field: str, rel_path: str) -> None:
    lines = epic.read_text(encoding="utf-8").splitlines()
    plans_index = next((i for i, line in enumerate(lines) if line.strip() == "plans:"), None)
    if plans_index is None:
        raise InitError(f"Epic 缺少 plans: 索引: {epic.relative_to(ROOT)}")
    insert_at = plans_index + 1
    while insert_at < len(lines):
        line = lines[insert_at]
        if line and not line.startswith((" ", "\t")):
            break
        insert_at += 1
    lines.insert(insert_at, f"  {field}: {rel_path}")
    epic.write_text("\n".join(lines) + "\n", encoding="utf-8")


def epic_plan_path(stage: dict[str, Any], epic: Path) -> tuple[Path, str]:
    field = str(stage.get("epicField") or "").strip()
    if not field:
        raise InitError(f"Epic 阶段 {stage.get('key')} 缺少 epicField")
    plans = gate_parse.read_plan_index(epic)
    rel = plans.get(field, "").strip()
    if not rel:
        suffix = str(stage.get("planSuffix") or stage.get("label") or stage.get("key")).strip()
        rel = f"{stage['planFolder']}/{epic.stem}-{slugify(suffix)}.md"
        insert_epic_plan_path(epic, field, rel)
    path = (ROOT / rel).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise InitError(f"Epic plans.{field} 超出工作区: {rel}") from exc
    return path, rel


def target_stages(bp: dict[str, Any], current: str, all_stages: bool) -> list[dict[str, Any]]:
    if all_stages:
        return list(bp.get("stages", []))
    stage = stage_by_key(bp, current)
    if not stage or current == "done":
        raise InitError(f"当前阶段不可创建 plan: {current}")
    return [stage]


def create_plans(args: argparse.Namespace) -> list[str]:
    bp = load_blueprint(args.workflow)
    if bp.get("usesEpic") and not args.epic:
        raise InitError(f"{args.workflow} 使用 Epic，须传 --epic Plans/Epic/xxx.md")
    if not bp.get("usesEpic") and args.epic:
        raise InitError(f"{args.workflow} 是无 Epic 轻流程，不接受 --epic")
    epic: Path | None = None
    epic_rel: str | None = None
    if args.epic:
        epic, epic_rel = resolve_epic(args.epic)
    # 轻流程必须按具体任务判定当前阶段，否则会与同工作流的历史 plan 串单。
    gate = run_gate(args.workflow, epic_rel, None if epic else args.title)
    stages = target_stages(bp, gate.get("current_state", ""), args.all)
    epic_fm = gate_parse.read_frontmatter(epic) if epic else {}
    epic_day = epic.stem[:10] if epic and re.match(r"^\d{4}-\d{2}-\d{2}", epic.stem) else ""
    day = str(epic_fm.get("date") or epic_day or args.date)
    title = args.title
    if not title and epic:
        title = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", epic.stem)
    if not title:
        raise InitError("缺少任务标题：轻流程须传 --title；Epic 流程可从 --epic 文件名派生")
    created: list[str] = []
    skipped: list[str] = []
    for stage in stages:
        path, rel = epic_plan_path(stage, epic) if epic else plan_path_for(stage, title, day)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not args.force:
            skipped.append(rel)
            continue
        path.write_text(
            (
                render_stage_template(args.workflow, stage, title, day, rel, args.include_feedback, epic)
                if epic
                else render_plan(args.workflow, stage, title, day, rel, args.include_feedback)
            ),
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
    parser = argparse.ArgumentParser(description="按蓝图为当前阶段创建 plan；Epic 工作流严格写入 Epic plans.* 声明路径。")
    parser.add_argument("--workflow", required=True, help="工作流名，如 client-dev / ui-change / bugfix")
    parser.add_argument("--epic", help="Epic plan 路径；usesEpic=true 的工作流必填")
    parser.add_argument("--title", help="任务标题；Epic 工作流默认从 Epic 文件名派生")
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
