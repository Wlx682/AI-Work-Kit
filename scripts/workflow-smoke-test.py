#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKFLOWS = [
    "merge-code",
    "ui-change",
    "bugfix",
    "story-split-only",
    "computer-mgmt",
    "learning-loop",
    "client-dev",
]
ROUTE_PHRASES = {
    "merge-code": "帮我把 feature/search 分支合进 main",
    "ui-change": "帮我改一下 UI",
    "bugfix": "线上报错帮我修bug",
    "story-split-only": "这个技术方案只拆 Story",
    "computer-mgmt": "帮我清理电脑缓存",
    "learning-loop": "我要学习 agent 开发",
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
    # 路由检查会校验全部蓝图，因此 smoke 隔离库要提前建立全部阶段目录。
    for blueprint in (tmp / ".workflows/blueprints").glob("*.json"):
        try:
            data = json.loads(blueprint.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        ensure_plan_folders(tmp, data)


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


def skill_run(skill: str, plan: str, stage: str | None = None) -> str:
    stage_line = f"  workflow_stage: {stage}\n" if stage else ""
    return f"""## 反馈（skill_run）

```yaml
skill_run:
  skill: {skill}
{stage_line}  plan: {plan}
  date: 2026-07-03
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "workflow smoke fixture 校验反馈块格式。"
  contexts_missing: []
  contexts_stale: []
```
"""


def wbs_table(rows: list[int | str]) -> str:
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


def merge_analysis_fixture() -> str:
    return textwrap.dedent(
        """
        ## 双边代码意图

        | 意图ID | 分支侧 | 文件/模块 | 代码变化 | 业务目标 | 行为/规则变化 | 证据 | 置信度 |
        |--------|--------|-----------|----------|----------|---------------|------|--------|
        | SI-001 | 源分支 | payment/risk.py | 增加自动风险校验 | 降低异常支付 | 提交前增加校验 | commit abc；test_risk.py | 高 |
        | TI-001 | 目标分支 | payment/review.py | 保留人工审核入口 | 控制高风险订单 | 高风险订单人工审核 | commit def；test_review.py | 高 |

        ## 业务冲突矩阵

        | 冲突ID | 关联意图 | 冲突类型 | 业务影响 | AI结论 | 需开发者决策 | 决策ID |
        |--------|----------|----------|----------|--------|----------------|--------|
        | MC-001 | SI-001, TI-001 | 业务规则 | 自动校验可能绕过人工审核 | 需开发者决策：证据不能确定审核优先级 | 是 | D-001 |

        ## 开发者决策清单

        | 决策ID | 待决策问题 | 可选方案及影响 | 开发者结论 | 决策人 | 确认记录 | 状态 |
        |--------|------------|----------------|------------|--------|----------|------|
        | D-001 | 自动校验后是否人工审核 | A 保留审核更安全；B 自动放行吞吐更高 | 保留人工审核并增加自动校验 | 支付模块开发负责人 | 2026-07-03 合并评审记录 #42 | 已决策 |

        ## 合并策略与验证映射

        | 冲突ID | 处理策略 | 影响范围 | 验证场景 | 状态 |
        |--------|----------|----------|----------|------|
        | MC-001 | 自动校验后高风险订单仍人工审核 | 支付提交与审核队列 | 高风险订单校验通过后仍生成审核任务 | 已规划 |
        """
    ).strip()


def merge_implementation_fixture() -> str:
    return textwrap.dedent(
        """
        ## 决策落实记录

        | 追踪ID | 影响文件 | 落实方式 | 验证用例 | 状态 |
        |--------|----------|----------|----------|------|
        | MC-001 | payment/risk.py | 自动校验不改变人工审核状态 | test_risk_then_review | 已落实 |
        | D-001 | payment/review.py | 高风险订单进入人工审核队列 | test_high_risk_review_queue | 已落实 |

        ## 验证记录

        | 命令/检查 | 覆盖意图/冲突 | 结果 | 备注 |
        |-----------|---------------|------|------|
        | pytest payment | SI-001, TI-001, MC-001, D-001 | pass | 组合场景通过 |

        ## 合并结果

        - 合并后 SHA：abc123
        - 两边业务意图：均已保留
        - 开发者决策：已全部落实
        """
    ).strip()


def inject_merge_fixtures(tmp: Path, bp: dict) -> None:
    if bp.get("name") != "merge-code":
        return
    for stage in bp.get("stages", []):
        stage_key = stage.get("key", "")
        if stage_key not in {"intent-analysis", "merge"}:
            continue
        folder = tmp / stage.get("planFolder", "")
        for plan in folder.glob("*.md"):
            text = plan.read_text(encoding="utf-8")
            if f"workflow_stage: {stage_key}" not in text:
                continue
            rel = plan.relative_to(tmp).as_posix()
            extra_fm = "p0_open: 0\n" if stage_key == "intent-analysis" else ""
            body = merge_analysis_fixture() if stage_key == "intent-analysis" else merge_implementation_fixture()
            write_fixture(
                plan,
                f"""---
status: 已采纳
{extra_fm}workflow: merge-code
workflow_stage: {stage_key}
skill: merge-code-assistant
---

# {stage.get('label')}：smoke

{body}

{skill_run('merge-code-assistant', rel)}
""",
            )


def inject_story_split_fixtures(tmp: Path, bp: dict, stage_key: str) -> None:
    if bp.get("name") != "story-split-only" or stage_key != "story-split":
        return
    folder = tmp / "Plans/功能开发"
    for plan in folder.glob("*Story拆分*.md"):
        text = plan.read_text(encoding="utf-8")
        if "workflow_stage: story-split" not in text:
            continue
        rel = plan.relative_to(tmp).as_posix()
        index_rel = rel[:-3] + ".stories.json"
        story_rel = "Plans/功能开发/smoke-us-001.md"
        if "story_index:" not in text:
            lines = text.splitlines()
            if lines and lines[0].strip() == "---":
                lines.insert(1, f"story_index: {index_rel}")
                plan.write_text("\n".join(lines) + "\n", encoding="utf-8")
        (tmp / index_rel).write_text(json.dumps({
            "scope_confirmed": True,
            "stories": [{
                "id": "US-001", "title": "用户可以完成 smoke 能力", "path": story_rel,
                "story_points": 3, "estimate_confirmed": True, "priority": "P0",
                "sprint_scope": True, "dependencies": [], "acceptance_criteria": ["AC1"],
                "architecture_refs": ["ADR-001"], "vertical_slice": True,
            }],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_fixture(
            tmp / story_rel,
            """
            ---
            story_id: US-001
            status: 待开发
            ---

            # US-001
            """,
        )


def inject_implementation_design_fixtures(tmp: Path, bp: dict, stage_key: str) -> None:
    if stage_key != "implementation-design":
        return
    for stage in bp.get("stages", []):
        if stage.get("key") != "implementation-design":
            continue
        folder = tmp / stage.get("planFolder", "")
        for plan in folder.glob("*.md"):
            text = plan.read_text(encoding="utf-8")
            if "workflow_stage: implementation-design" not in text:
                continue
            source_rel = "src/bugfix/smoke.ts"
            impl_rel = plan.relative_to(tmp).as_posix().replace(".md", ".impl.json")
            write_fixture(tmp / source_rel, "export const smokeBugfix = true")
            (tmp / impl_rel).write_text(json.dumps({
                "codebase_available": True,
                "codebase_read": [{"path": source_rel, "reason": "bugfix smoke 既有实现参考"}],
                "target_files": {
                    "modify": [{"path": source_rel, "purpose": "修复 smoke 缺陷", "layer": "Domain"}],
                    "create": []
                },
                "module_boundary": {"layer": "Domain", "dependency_rule": "Domain 不依赖 UI"},
                "tests": {"red": [{"path": "tests/smoke_bugfix.test.ts", "command": "pytest tests/smoke_bugfix.test.ts"}]},
                "risks": [],
                "blocked_questions": [],
                "confirmed": True,
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if "implementation_design:" not in text:
                lines = text.splitlines()
                if lines and lines[0].strip() == "---":
                    lines.insert(1, f"implementation_design: {impl_rel}")
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
  prioritization: Plans/需求排序/smoke.md
  architecture: Plans/技术方案/smoke.md
  development: Plans/功能开发/smoke.md
  integration_plan: Plans/自动化测试/smoke-plan.md
  integration: Plans/自动化测试/smoke.md
---

# Smoke Epic

## 三、动态用户故事看板

故事真理源：`Plans/功能开发/smoke.stories.json`。
""",
    )
    return epic_rel


LEARNING_STAGE_FIXTURES = [
    (
        "topic-intake",
        "Plans/学习循环/smoke-topic.md",
        "workflow-router",
        ["一、学习主题", "二、完成门槛"],
        1,
    ),
    (
        "material-prepare",
        "Plans/学习循环/smoke-material.md",
        "material-prep-assistant",
        ["三、资料准备", "四、最小概念树"],
        2,
    ),
    (
        "study",
        "Plans/学习循环/smoke-study.md",
        "material-prep-assistant",
        ["五、学习过程", "六、问题与澄清"],
        3,
    ),
    (
        "design",
        "Plans/学习循环/smoke-design.md",
        "feature-dev-assistant",
        ["七、设计决策"],
        "4a",
    ),
    (
        "code",
        "Plans/学习循环/smoke-code.md",
        "feature-dev-assistant",
        ["八、编码实现", "九、代码产物"],
        "4b",
    ),
    (
        "verify",
        "Plans/学习循环/smoke-verify.md",
        "test-generator",
        ["十、验证清单", "十一、验证结论"],
        5,
    ),
    (
        "retro",
        "Plans/学习循环/smoke-retro.md",
        "report-assistant",
        ["十二、复盘", "十三、下一步建议"],
        6,
    ),
    (
        "record",
        "Plans/学习循环/smoke-record.md",
        "material-prep-assistant",
        ["十四、学习记录", "十五、知识图谱增量", "十六、用户确认"],
        7,
    ),
]


def create_learning_epic(tmp: Path) -> str:
    epic_rel = "Plans/Epic/smoke-learning.md"
    plan_lines = "\n".join(f"  {stage}: {rel}" for stage, rel, *_ in LEARNING_STAGE_FIXTURES)
    write_fixture(
        tmp / epic_rel,
        f"""
---
project: smoke-learning
workflow: learning-loop
p0_open: 0
plans:
{plan_lines}
---

# Smoke Learning Epic

## 三、WBS

```
[ ] 1. 确认学习主题与完成门槛
[ ] 2. AI 准备资料与最小概念树
[ ] 3. 用户学习与答疑
[ ] 4a. 设计决策
[ ] 4b. 编码实现
[ ] 5. AI 验证
[ ] 6. 学习复盘
[ ] 7. 学习记录与知识图谱增量
```
""",
    )
    return epic_rel


def create_learning_stage_plan(tmp: Path, epic_rel: str, rel: str, stage: str, skill: str, sections: list[str], slice_n: int | str) -> None:
    section_blocks = "\n\n".join(f"## {title}\n\nsmoke {title}" for title in sections)
    write_fixture(
        tmp / rel,
        f"""
---
status: 已采纳
workflow: learning-loop
workflow_stage: {stage}
epic: {epic_rel}
---

# 学习阶段 smoke：{stage}

{section_blocks}

{wbs_table([slice_n])}

{skill_run(skill, rel)}
""",
    )


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

{skill_run("requirement-analyst", "Plans/需求分析/smoke.md", "requirement")}
""",
    )


def create_client_prioritization(tmp: Path, epic_rel: str) -> None:
    plan_rel = "Plans/需求排序/smoke.md"
    index_rel = "Plans/需求排序/smoke.backlog.json"
    write_fixture(
        tmp / plan_rel,
        f"""
---
status: 已采纳
epic: {epic_rel}
backlog_index: {index_rel}
---

# 需求排序 smoke

## 排序原则

业务价值、紧迫度与依赖分开评估。

## 需求排序

REQ-001 为 P0。

## 团队确认

已确认本迭代顺序。

{skill_run("backlog-prioritization-assistant", plan_rel, "prioritization")}
""",
    )
    (tmp / index_rel).write_text(json.dumps({
        "confirmed": True,
        "requirements": [{
            "id": "REQ-001", "title": "完成支付", "business_value": "high",
            "urgency": "high", "dependencies": [], "priority": "P0",
            "reason": "核心收银路径", "confirmed": True,
        }],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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

## 五、非功能约束

门禁判定必须可重复、无状态。

## 六、ADR

ADR-001：选择文件系统事实作为唯一权威源。

## 七、需求影响矩阵

| 需求 | 模块 | ADR |
|------|------|-----|
| REQ-001 | Gate | ADR-001 |

{wbs_table([3])}

{skill_run("architecture-design-assistant", "Plans/技术方案/smoke.md", "architecture")}
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


def create_client_story_scope(tmp: Path, epic_rel: str) -> None:
    dev_rel = "Plans/功能开发/smoke.md"
    index_rel = "Plans/功能开发/smoke.stories.json"
    story_rel = "Plans/功能开发/smoke-us-001.md"
    write_fixture(
        tmp / dev_rel,
        f"""
---
epic: {epic_rel}
story_index: {index_rel}
---

# 用户故事拆分 smoke

## 迭代 Scope

US-001 将端到端交付“用户完成支付”能力。

{skill_run("task-splitter", dev_rel, "story-split")}
""",
    )
    (tmp / index_rel).write_text(json.dumps({
        "scope_confirmed": True,
        "stories": [{
            "id": "US-001", "title": "用户可以完成支付", "path": story_rel,
            "story_points": 5, "estimate_confirmed": True, "priority": "P0",
            "sprint_scope": True, "dependencies": [], "acceptance_criteria": ["AC1"],
            "architecture_refs": ["ADR-001"], "vertical_slice": True,
        }],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_fixture(
        tmp / story_rel,
        f"""
---
story_id: US-001
status: 待开发
implementation_design: Plans/功能开发/smoke-us-001.impl.json
tdd_evidence: Plans/功能开发/smoke-us-001.tdd.json
---

# US-001
""",
    )


def create_client_implementation_design(tmp: Path) -> None:
    source_rel = "src/features/payment/view.ts"
    impl_rel = "Plans/功能开发/smoke-us-001.impl.json"
    write_fixture(tmp / source_rel, "export const existingPaymentView = true")
    (tmp / impl_rel).write_text(json.dumps({
        "story_id": "US-001",
        "codebase_available": True,
        "codebase_read": [{"path": source_rel, "reason": "同模块命名与分层参考"}],
        "target_files": {
            "modify": [{"path": source_rel, "purpose": "接入支付入口", "layer": "Presentation"}],
            "create": [{"path": "src/features/payment/use-case.ts", "reason": "现有模块没有支付用例", "naming_basis": "沿用 use-case 命名", "layer": "Domain"}],
        },
        "module_boundary": {"layer": "Presentation/Domain", "dependency_rule": "Presentation 只依赖 Domain"},
        "tests": {"red": [{"path": "tests/payment.test.ts", "command": "pytest tests/payment.test.ts"}]},
        "risks": [],
        "blocked_questions": [],
        "confirmed": True,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dev = tmp / "Plans/功能开发/smoke.md"
    dev.write_text(dev.read_text(encoding="utf-8") + "\n## 实现落点设计\nUS-001 已完成代码落点设计。\n" + skill_run(
        "implementation-design-assistant", "Plans/功能开发/smoke.md", "implementation-design"
    ), encoding="utf-8")

def complete_client_story_tdd(tmp: Path) -> None:
    story_rel = "Plans/功能开发/smoke-us-001.md"
    evidence_rel = "Plans/功能开发/smoke-us-001.tdd.json"
    write_fixture(
        tmp / story_rel,
        f"""
---
story_id: US-001
status: 已完成
implementation_design: Plans/功能开发/smoke-us-001.impl.json
tdd_evidence: {evidence_rel}
---

# US-001
""",
    )
    (tmp / evidence_rel).write_text(json.dumps({
        "story_id": "US-001", "commit": "smoke123",
        "red": {"command": "pytest story", "exit_code": 1, "reason": "功能尚未实现", "at": "t1"},
        "green": {"command": "pytest story", "exit_code": 0, "at": "t2"},
        "refactor": {"command": "pytest story", "exit_code": 0, "at": "t3"},
        "integration_smoke": {"command": "pytest smoke", "exit_code": 0, "at": "t4"},
        "acceptance": [{"ac_id": "AC1", "pass": True}],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dev = tmp / "Plans/功能开发/smoke.md"
    dev.write_text(dev.read_text(encoding="utf-8") + "\n" + skill_run(
        "feature-dev-assistant", "Plans/功能开发/smoke.md", "story-development"
    ), encoding="utf-8")


def create_client_integration(tmp: Path, epic_rel: str) -> None:
    plan_rel = "Plans/自动化测试/smoke.md"
    report_rel = "Plans/自动化测试/smoke.integration.json"
    write_fixture(
        tmp / plan_rel,
        f"""
---
epic: {epic_rel}
story_index: Plans/功能开发/smoke.stories.json
approved_test_plan: Plans/自动化测试/smoke-plan.md
target_commit: smoke123
integration_report: {report_rel}
---

# 全量集成测试 smoke

{skill_run("test-generator", plan_rel, "integration-test")}
""",
    )
    (tmp / report_rel).write_text(json.dumps({
        "commit": "smoke123", "all_scope_stories_completed": True,
        "suites": [{"name": "cross-story", "command": "pytest integration", "exit_code": 0}],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_client_integration_plan(tmp: Path, epic_rel: str) -> None:
    plan_rel = "Plans/自动化测试/smoke-plan.md"
    case_rel = "Plans/自动化测试/smoke.cases.json"
    review_rel = "Plans/自动化测试/smoke.review.json"
    case_path = tmp / case_rel
    case_path.write_text(json.dumps({
        "target_commit": "smoke123",
        "cases": [{
            "id": "IT-001", "title": "完整蓝图", "priority": "P0", "type": "cross-story",
            "preconditions": ["Smoke fixture 已就绪"], "test_data": ["有效 fixture"],
            "steps": ["执行完整流程"], "expected_results": ["流程完成"],
            "automation": "automated", "suite": "cross-story",
            "ac_refs": [{"story_id": "US-001", "ac_id": "AC1"}],
        }],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (tmp / review_rel).write_text(json.dumps({
        "approved": True, "reviewer": "Smoke QA", "reviewed_at": "2026-08-07T10:00:00+08:00",
        "target_commit": "smoke123", "case_index_sha256": hashlib.sha256(case_path.read_bytes()).hexdigest(),
        "unresolved_comments": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_fixture(
        tmp / plan_rel,
        f"""
---
status: 已采纳
epic: {epic_rel}
story_index: Plans/功能开发/smoke.stories.json
target_commit: smoke123
test_case_index: {case_rel}
test_review: {review_rel}
---

# 集成测试计划 smoke

## 测试策略
覆盖完整流程、异常和恢复。

## 测试用例
IT-001 覆盖完整流程。

## 需求与用例覆盖
US-001/AC1 → IT-001。

## 测试审核
Smoke QA 已审核。

{skill_run("test-generator", plan_rel, "integration-test-plan")}
""",
    )


def smoke_learning_workflow(tmp: Path, workflow: str, bp: dict) -> None:
    bootstrap = run_json(
        tmp,
        ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--project", "不存在的学习", "--json"],
    )
    if bootstrap.get("next_state") != "bootstrap-epic" or not bootstrap.get("blockers"):
        raise SmokeError(f"{workflow} 无 Epic 时应要求 bootstrap: {bootstrap}")

    epic_rel = create_learning_epic(tmp)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "topic-intake")
    if not any(("子 Plan 未创建" in item or "子 Plan 不存在" in item) for item in gate.get("blockers", [])):
        raise SmokeError(f"{workflow} 新 Epic 应阻塞在学习主题子 Plan: {gate}")

    stages = [stage.get("key") for stage in bp.get("stages", [])]
    for index, (stage, rel, skill, sections, slice_n) in enumerate(LEARNING_STAGE_FIXTURES):
        create_learning_stage_plan(tmp, epic_rel, rel, stage, skill, sections, slice_n)
        gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
        expected = stages[index + 1] if index + 1 < len(stages) else "done"
        assert_gate_state(gate, workflow, expected)

    if gate.get("blockers"):
        raise SmokeError(f"{workflow} 完整真实推进后仍有 blockers: {gate}")

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


def smoke_epic_workflow(tmp: Path, workflow: str, bp: dict) -> None:
    if workflow == "learning-loop":
        smoke_learning_workflow(tmp, workflow, bp)
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
    assert_gate_state(gate, workflow, "prioritization")

    create_client_prioritization(tmp, epic_rel)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "architecture")

    create_client_architecture(tmp, epic_rel)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "story-split")

    create_client_story_scope(tmp, epic_rel)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "implementation-design")

    create_client_implementation_design(tmp)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "story-development")

    complete_client_story_tdd(tmp)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "integration-test-plan")

    create_client_integration_plan(tmp, epic_rel)
    gate = run_json(tmp, ["bash", "scripts/workflow-gate.sh", "--workflow", workflow, "--epic", epic_rel, "--json"])
    assert_gate_state(gate, workflow, "integration-test")

    create_client_integration(tmp, epic_rel)
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
        inject_merge_fixtures(tmp, bp)
        inject_story_split_fixtures(tmp, bp, str(current))
        inject_implementation_design_fixtures(tmp, bp, str(current))
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
