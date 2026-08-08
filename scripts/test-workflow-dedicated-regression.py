#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = ROOT / ".workflows" / "blueprints"


class RegressionError(AssertionError):
    pass


def load_blueprint(name: str) -> dict[str, Any]:
    path = BLUEPRINT_DIR / f"{name}.json"
    if not path.exists():
        raise RegressionError(f"缺少蓝图: {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RegressionError(f"蓝图顶层必须是 object: {path.relative_to(ROOT)}")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RegressionError(message)


def require_enablement(bp: dict[str, Any]) -> None:
    enablement = bp.get("enablement")
    require(isinstance(enablement, dict), f"{bp['name']}: 缺少 enablement 安装声明")
    require(enablement.get("preflight") == f"python3 scripts/workflow-install.py check --workflow {bp['name']}", f"{bp['name']}: preflight 命令不正确")
    for capability in ["core-tools", "skills", "tool-entrypoints", "global-instructions", "pre-commit-hook", "kanban-board"]:
        require(capability in enablement.get("requires", []), f"{bp['name']}: enablement.requires 缺 {capability}")


def stage_keys(bp: dict[str, Any]) -> list[str]:
    return [stage["key"] for stage in bp["stages"]]


def stage_map(bp: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {stage["key"]: stage for stage in bp["stages"]}


def require_no_epic_lightweight(bp: dict[str, Any], plan_root: str) -> None:
    require(bp["usesEpic"] is False, f"{bp['name']}: 轻量流程不得要求 Epic")
    require(bp["planRoot"] == plan_root, f"{bp['name']}: planRoot 应为 {plan_root}")
    require(bp["gateScript"] == "scripts/workflow-gate.sh", f"{bp['name']}: gateScript 必须走统一无状态门禁")


def assert_bugfix() -> None:
    bp = load_blueprint("bugfix")
    require_enablement(bp)
    require_no_epic_lightweight(bp, "Plans/Bug排查")
    require(stage_keys(bp) == ["reproduce", "diagnose", "implementation-design", "fix", "regression"], "bugfix: 阶段必须保持复现→定位→落点设计→修复→回归")
    stages = stage_map(bp)
    for key in ["reproduce", "diagnose", "fix"]:
        require(stages[key]["skills"] == ["feature-dev-assistant"], f"bugfix:{key}: 必须由 feature-dev-assistant 执行")
        require(stages[key]["exitCriteria"]["skillRun"] is True, f"bugfix:{key}: 必须留下 skill_run")
    require(stages["implementation-design"]["skills"] == ["implementation-design-assistant"], "bugfix: 修复前必须由 implementation-design-assistant 做代码落点设计")
    require(stages["implementation-design"]["exitCriteria"]["implementationDesignReady"] is True, "bugfix: 落点设计必须校验 implementationDesignReady")
    require(stages["regression"]["skills"] == ["code-review"], "bugfix: 回归复核必须由 code-review 执行")
    require("修bug" in bp["triggerHints"] and "需求变更" in bp["description"], "bugfix: 必须保留 bug 入口与需求变更升级提示")


def assert_ui_change() -> None:
    bp = load_blueprint("ui-change")
    require_enablement(bp)
    require_no_epic_lightweight(bp, "Plans/界面开发")
    require(stage_keys(bp) == ["ui-scope", "ui-implement", "ui-review"], "ui-change: 阶段必须保持范围→实现→复核")
    stages = stage_map(bp)
    require(stages["ui-scope"]["skills"] == ["figma-ui"], "ui-change: 范围确认必须走 figma-ui")
    require(stages["ui-implement"]["skills"] == ["figma-ui"], "ui-change: UI 实现必须走 figma-ui")
    require(stages["ui-implement"]["exitCriteria"].get("verdictPass") == "required", "ui-change: UI 实现必须要求 verdictPass")
    require(stages["ui-review"]["skills"] == ["code-review"], "ui-change: UI 复核必须走 code-review")
    for hint in ["Figma还原", "对稿", "只改界面"]:
        require(hint in bp["triggerHints"], f"ui-change: 缺少触发词 {hint}")


def assert_story_split_only() -> None:
    bp = load_blueprint("story-split-only")
    require_enablement(bp)
    require_no_epic_lightweight(bp, "Plans/功能开发")
    require(stage_keys(bp) == ["story-split", "story-check"], "story-split-only: 阶段必须只包含 Story 拆分与 Scope 自检")
    stages = stage_map(bp)
    split = stages["story-split"]
    require(split["skills"] == ["task-splitter"], "story-split-only: Story 拆分必须只走 task-splitter")
    require(split["template"] == "Templates/用户故事拆分模板.md", "story-split-only: 必须使用用户故事拆分模板")
    require(split["exitCriteria"]["childPlanExists"] is True, "story-split-only: 必须产出拆分 Plan")
    require(split["exitCriteria"]["storyScopeReady"] is True, "story-split-only: 必须校验 .stories.json 与 Scope")
    require(split["exitCriteria"]["skillRun"] is True, "story-split-only: 必须留下 skill_run")
    check = stages["story-check"]
    require(check["skills"] == ["task-splitter"], "story-split-only: Scope 自检必须只走 task-splitter")
    require(check["exitCriteria"]["childPlanExists"] is True, "story-split-only: 必须产出复核 Plan")
    require(check["exitCriteria"]["skillRun"] is True, "story-split-only: 复核必须留下 skill_run")
    for hint in ["用户故事拆分", "故事点", "确认Scope"]:
        require(hint in bp["triggerHints"], f"story-split-only: 缺少 Story 触发词 {hint}")
    for hint in ["只拆任务", "拆任务", "任务拆分", "拆成任务", "拆成开发任务", "拆一下任务"]:
        require(hint not in bp["triggerHints"], f"story-split-only: 不得保留旧任务拆分入口 {hint}")
    require("WBS修订" not in bp["triggerHints"] and "改WBS" not in bp["triggerHints"], "story-split-only: 不得保留 WBS 修订开发入口")


def assert_computer_mgmt() -> None:
    bp = load_blueprint("computer-mgmt")
    require_enablement(bp)
    require_no_epic_lightweight(bp, "Plans/电脑管理")
    require(stage_keys(bp) == ["inventory", "cleanup", "backup", "harden", "review"], "computer-mgmt: 阶段必须保持盘点→清理→备份→加固→复核")
    stages = stage_map(bp)
    expected_slices = {"inventory": [1], "cleanup": [2], "backup": [3], "harden": [4], "review": [5]}
    for key, slices in expected_slices.items():
        require(stages[key]["wbsSlices"] == slices, f"computer-mgmt:{key}: wbsSlices 应为 {slices}")
        require(stages[key]["exitCriteria"]["skillRun"] is True, f"computer-mgmt:{key}: 必须留下 skill_run")
    for key in ["inventory", "cleanup", "backup", "harden"]:
        require(stages[key]["skills"] == ["material-prep-assistant"], f"computer-mgmt:{key}: 必须走 material-prep-assistant")
    require(stages["review"]["skills"] == ["code-review"], "computer-mgmt: 复核必须走 code-review")


def assert_learning_loop() -> None:
    bp = load_blueprint("learning-loop")
    require_enablement(bp)
    require(bp["usesEpic"] is True and bp["epicRequired"] is True, "learning-loop: 必须先创建学习 Epic")
    require(bp["epicTemplate"] == "Templates/Epic模板-learning-loop.md", "learning-loop: 必须使用学习 Epic 模板")
    require(bp["startup"]["requireEpicBeforeBoot"] is True, "learning-loop: 启动看板前必须有 Epic")
    expected = ["topic-intake", "material-prepare", "study", "design", "code", "verify", "retro", "record"]
    require(stage_keys(bp) == expected, "learning-loop: 阶段链必须保持主题→资料→学习→设计→编码→验证→复盘→记录")
    stages = stage_map(bp)
    expected_slices = {
        "topic-intake": [1],
        "material-prepare": [2],
        "study": [3],
        "design": ["4a"],
        "code": ["4b"],
        "verify": [5],
        "retro": [6],
        "record": [7],
    }
    for key, slices in expected_slices.items():
        require(stages[key]["wbsSlices"] == slices, f"learning-loop:{key}: wbsSlices 应为 {slices}")
        require(stages[key]["epicField"] == key, f"learning-loop:{key}: epicField 必须支持 hyphenated key")
        require(stages[key]["exitCriteria"]["sectionsPresent"] is True, f"learning-loop:{key}: 必须校验章节事实")
        require(stages[key]["exitCriteria"]["skillRun"] is True, f"learning-loop:{key}: 必须留下 skill_run")
    require(stages["record"]["requiredSections"] == ["十四、学习记录", "十五、知识图谱增量", "十六、用户确认"], "learning-loop: record 必须沉淀学习记录、图谱增量和用户确认")


def assert_creative_incubation() -> None:
    bp = load_blueprint("creative-incubation")
    require_enablement(bp)
    require(bp["usesEpic"] is True and bp["epicRequired"] is True, "creative-incubation: 必须先创建单轮孵化 Epic")
    require(bp["epicTemplate"] == "Templates/Epic模板-创意捕获与孵化.md", "creative-incubation: 必须使用专用 Epic 模板")
    require(bp["startup"]["requireEpicBeforeBoot"] is True, "creative-incubation: 启动看板前必须有 Epic")
    expected = ["perception", "cognition", "generation", "validation"]
    require(stage_keys(bp) == expected, "creative-incubation: 阶段链必须保持感知→认知→生成→验证")
    stages = stage_map(bp)
    for index, key in enumerate(expected, start=1):
        stage = stages[key]
        require(stage["wbsSlices"] == [index], f"creative-incubation:{key}: wbsSlices 应为 {[index]}")
        require(stage["epicField"] == key, f"creative-incubation:{key}: epicField 必须与 stage key 一致")
        require(stage["skills"] == ["creative-incubation-assistant"], f"creative-incubation:{key}: 必须走专用阶段 Skill")
        require(stage["exitCriteria"]["status"] == ["已采纳"], f"creative-incubation:{key}: 必须经用户确认后采纳")
        require(stage["exitCriteria"]["sectionsPresent"] is True, f"creative-incubation:{key}: 必须校验阶段章节事实")
        require(stage["exitCriteria"]["skillRun"] is True, f"creative-incubation:{key}: 必须留下 skill_run")

    epic = (ROOT / bp["epicTemplate"]).read_text(encoding="utf-8")
    plan = (ROOT / "Templates/创意捕获与孵化模板.md").read_text(encoding="utf-8")
    skill = (ROOT / ".cursor/skills/creative-incubation-assistant/SKILL.md").read_text(encoding="utf-8")
    for needle in ["≥2 个觅食域", "生活体验为推荐增强项，不是硬门禁", "≥3 个洞察晶体", "≥10 个创意", "≥3 个 AI 高自动化方向", "2 个候选", "≥1 个真实世界实验"]:
        require(needle in epic or needle in plan or needle in skill, f"creative-incubation: 缺少核心数量契约 {needle}")
    require("下一轮" in epic and "反馈" in epic, "creative-incubation: Epic 必须声明跨轮反馈回流")
    require("原始来源" in plan and "反例/适用边界" in plan and "停止/转向阈值" in plan, "creative-incubation: 阶段模板必须保留来源、反例和可证伪阈值")


REGRESSIONS = {
    "bugfix": assert_bugfix,
    "ui-change": assert_ui_change,
    "story-split-only": assert_story_split_only,
    "computer-mgmt": assert_computer_mgmt,
    "learning-loop": assert_learning_loop,
    "creative-incubation": assert_creative_incubation,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="运行指定 workflow 的 P0 专属行为回归。")
    parser.add_argument("workflows", nargs="+", choices=sorted(REGRESSIONS), help="要验证的 workflow 名称")
    args = parser.parse_args()

    ok = True
    for name in args.workflows:
        try:
            REGRESSIONS[name]()
        except RegressionError as exc:
            ok = False
            print(f"BLOCKED:workflow-dedicated-regression:{name}: {exc}", file=sys.stderr)
        else:
            print(f"OK:workflow-dedicated-regression:{name}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
