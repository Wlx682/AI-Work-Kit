#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib.util
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts/validate-client-dev.py"


class ClientDevWorkflowTests(unittest.TestCase):
    """client-dev 专属 P0：不得被通用 workflow smoke 替代。"""

    def run_validator(self, root: Path, command: str, plan: Path, ok: bool) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            ["python3", str(VALIDATOR), command, "--root", str(root), "--plan", str(plan)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if ok and proc.returncode != 0:
            self.fail(proc.stderr or proc.stdout)
        if not ok and proc.returncode == 0:
            self.fail(f"{command} 应失败但通过: {proc.stdout}")
        return proc

    @staticmethod
    def write(path: Path, content: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
        return path

    @staticmethod
    def dump(path: Path, payload: dict) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def test_ac01_ac03_ac12_blueprint_stage_chain_and_gates(self) -> None:
        bp = json.loads((ROOT / ".workflows/blueprints/client-dev.json").read_text(encoding="utf-8"))
        self.assertEqual(bp["name"], "client-dev")
        self.assertEqual(bp["enablement"]["preflight"], "python3 scripts/workflow-install.py check --workflow client-dev")
        for capability in ["core-tools", "skills", "tool-entrypoints", "global-instructions", "pre-commit-hook", "kanban-board"]:
            self.assertIn(capability, bp["enablement"]["requires"])
        stages = bp["stages"]
        self.assertEqual(
            [stage["key"] for stage in stages],
            ["requirement", "prioritization", "architecture", "story-split", "implementation-design", "story-development", "integration-test"],
        )
        by_key = {stage["key"]: stage for stage in stages}
        self.assertTrue(by_key["prioritization"]["exitCriteria"]["backlogPrioritized"])
        self.assertEqual(by_key["architecture"]["next"], "story-split")
        self.assertEqual(by_key["story-split"]["next"], "implementation-design")
        self.assertTrue(by_key["story-split"]["exitCriteria"]["storyScopeReady"])
        self.assertTrue(by_key["implementation-design"]["exitCriteria"]["implementationDesignReady"])
        self.assertEqual(by_key["implementation-design"]["skills"], ["implementation-design-assistant"])
        self.assertTrue(by_key["story-development"]["exitCriteria"]["storyTddComplete"])
        self.assertTrue(by_key["integration-test"]["exitCriteria"]["integrationReportPass"])
        self.assertEqual(by_key["integration-test"]["next"], "done")
        self.assertFalse({"release", "deploy"} & {stage["key"] for stage in stages})

    def test_assets_have_no_conflicting_legacy_contract(self) -> None:
        forbidden = {
            "Templates/Epic模板-client-dev.md": ["15 步", "WBS 看板（1–11"],
            "Templates/客户端功能开发模板.md": ["WBS 1–15", "发布检查", "线上冒烟"],
            "Skills/task_splitter.md": ["5–10 原子任务"],
        }
        for rel, needles in forbidden.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            for needle in needles:
                self.assertNotIn(needle, text, f"{rel} 仍保留旧版冲突口径: {needle}")

    def test_ac02_backlog_requires_confirmed_ordering_facts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="client-dev-backlog-") as raw:
            root = Path(raw)
            plan = self.write(root / "Plans/需求排序/demo.md", """
                ---
                backlog_index: Plans/需求排序/demo.backlog.json
                ---
                # 需求排序
            """)
            index = root / "Plans/需求排序/demo.backlog.json"
            self.dump(index, {"confirmed": False, "requirements": [{"id": "REQ-1"}]})
            self.run_validator(root, "backlog", plan, ok=False)
            self.dump(index, {
                "confirmed": True,
                "requirements": [{
                    "id": "REQ-1", "title": "创建草稿", "business_value": "high",
                    "urgency": "medium", "dependencies": [], "priority": "P0",
                    "reason": "核心用户路径", "confirmed": True,
                }],
            })
            self.run_validator(root, "backlog", plan, ok=True)

    def test_ac04_ac07_story_scope_requires_vertical_story_and_points(self) -> None:
        with tempfile.TemporaryDirectory(prefix="client-dev-scope-") as raw:
            root = Path(raw)
            plan = self.write(root / "Plans/功能开发/demo.md", """
                ---
                story_index: Plans/功能开发/demo.stories.json
                ---
                # 用户故事拆分
            """)
            index = root / "Plans/功能开发/demo.stories.json"
            base_story = {
                "id": "US-1", "title": "用户可以创建草稿", "path": "Plans/功能开发/us-1.md",
                "story_points": 13, "estimate_confirmed": True, "priority": "P0",
                "sprint_scope": True, "dependencies": [], "acceptance_criteria": ["AC1"],
                "architecture_refs": ["ADR-1"], "vertical_slice": True,
            }
            self.dump(index, {"scope_confirmed": True, "stories": [base_story]})
            self.run_validator(root, "story-scope", plan, ok=False)
            valid_story = dict(base_story)
            valid_story["story_points"] = 5
            self.dump(index, {"scope_confirmed": True, "stories": [valid_story]})
            self.run_validator(root, "story-scope", plan, ok=True)
            invalid_hours = dict(valid_story)
            invalid_hours["estimated_hours"] = 16
            self.dump(index, {"scope_confirmed": True, "stories": [invalid_hours]})
            self.run_validator(root, "story-scope", plan, ok=False)

    def test_implementation_design_requires_codebase_placement_facts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="client-dev-impl-design-") as raw:
            root = Path(raw)
            plan = self.write(root / "Plans/功能开发/demo.md", """
                ---
                story_index: Plans/功能开发/demo.stories.json
                ---
                # 用户故事开发
            """)
            self.write(root / "src/features/draft/view.ts", "export const existing = true")
            self.write(root / "Plans/功能开发/us-1.md", """
                ---
                story_id: US-1
                status: 待开发
                implementation_design: Plans/功能开发/us-1.impl.json
                ---
                # US-1
            """)
            self.dump(root / "Plans/功能开发/demo.stories.json", {
                "scope_confirmed": True,
                "stories": [{
                    "id": "US-1", "title": "用户可以创建草稿", "path": "Plans/功能开发/us-1.md",
                    "story_points": 5, "estimate_confirmed": True, "priority": "P0",
                    "sprint_scope": True, "dependencies": [], "acceptance_criteria": ["AC1"],
                    "architecture_refs": ["ADR-1"], "vertical_slice": True,
                }],
            })
            self.run_validator(root, "implementation-design", plan, ok=False)
            self.dump(root / "Plans/功能开发/us-1.impl.json", {
                "story_id": "US-1",
                "codebase_available": True,
                "codebase_read": [{"path": "src/features/draft/view.ts", "reason": "同模块分层和命名参考"}],
                "target_files": {
                    "modify": [{"path": "src/features/draft/view.ts", "purpose": "接入创建草稿入口", "layer": "Presentation"}],
                    "create": [{"path": "src/features/draft/use-case.ts", "reason": "现有模块没有创建用例", "naming_basis": "沿用 use-case 命名", "layer": "Domain"}],
                },
                "module_boundary": {"layer": "Presentation/Domain", "dependency_rule": "Presentation 只依赖 Domain"},
                "tests": {"red": [{"path": "tests/draft.test.ts", "command": "pytest tests/draft.test.ts"}]},
                "risks": [],
                "blocked_questions": [],
                "confirmed": True,
            })
            self.run_validator(root, "implementation-design", plan, ok=True)

    def test_ac08_ac09_ac11_development_requires_each_story_tdd_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="client-dev-tdd-") as raw:
            root = Path(raw)
            plan = self.write(root / "Plans/功能开发/demo.md", """
                ---
                story_index: Plans/功能开发/demo.stories.json
                ---
                # 用户故事开发
            """)
            story = self.write(root / "Plans/功能开发/us-1.md", """
                ---
                story_id: US-1
                status: 已完成
                implementation_design: Plans/功能开发/us-1.impl.json
                tdd_evidence: Plans/功能开发/us-1.tdd.json
                ---
                # US-1
            """)
            self.dump(root / "Plans/功能开发/demo.stories.json", {
                "scope_confirmed": True,
                "stories": [{
                    "id": "US-1", "title": "用户可以创建草稿", "path": "Plans/功能开发/us-1.md",
                    "story_points": 5, "estimate_confirmed": True, "priority": "P0",
                    "sprint_scope": True, "dependencies": [], "acceptance_criteria": ["AC1"],
                    "architecture_refs": ["ADR-1"], "vertical_slice": True,
                }],
            })
            self.run_validator(root, "story-development", plan, ok=False)
            self.dump(root / "Plans/功能开发/us-1.tdd.json", {
                "story_id": "US-1", "commit": "abc123",
                "red": {"command": "pytest test_story.py", "exit_code": 1, "reason": "功能尚未实现", "at": "2026-08-05T10:00:00+08:00"},
                "green": {"command": "pytest test_story.py", "exit_code": 0, "at": "2026-08-05T10:10:00+08:00"},
                "refactor": {"command": "pytest test_story.py", "exit_code": 0, "at": "2026-08-05T10:20:00+08:00"},
                "integration_smoke": {"command": "pytest test_smoke.py", "exit_code": 0, "at": "2026-08-05T10:25:00+08:00"},
                "acceptance": [{"ac_id": "AC1", "pass": True}],
            })
            self.run_validator(root, "story-development", plan, ok=True)
            self.assertTrue(story.exists())

    def test_ac10_integration_report_must_match_target_commit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="client-dev-integration-") as raw:
            root = Path(raw)
            plan = self.write(root / "Plans/自动化测试/integration.md", """
                ---
                target_commit: abc123
                story_index: Plans/功能开发/demo.stories.json
                integration_report: Plans/自动化测试/integration.report.json
                ---
                # 集成测试
            """)
            self.dump(root / "Plans/功能开发/demo.stories.json", {"scope_confirmed": True, "stories": []})
            report = root / "Plans/自动化测试/integration.report.json"
            self.dump(report, {
                "commit": "stale456", "all_scope_stories_completed": True,
                "suites": [{"name": "cross-story", "command": "pytest integration", "exit_code": 0}],
            })
            self.run_validator(root, "integration", plan, ok=False)
            self.dump(report, {
                "commit": "abc123", "all_scope_stories_completed": True,
                "suites": [{"name": "cross-story", "command": "pytest integration", "exit_code": 0}],
            })
            self.run_validator(root, "integration", plan, ok=True)

    def test_skill_contracts_match_client_dev(self) -> None:
        expected = {
            ".cursor/skills/backlog-prioritization-assistant/SKILL.md": ["business_value", "confirmed"],
            ".cursor/skills/architecture-design-assistant/SKILL.md": ["需求排序", "story-split"],
            ".cursor/skills/task-splitter/SKILL.md": ["用户故事", "story_points", "vertical_slice"],
            ".cursor/skills/implementation-design-assistant/SKILL.md": ["implementation_design", "代码落点", "Red"],
            ".cursor/skills/feature-dev-assistant/SKILL.md": ["Red", "Green", "implementation_design", "tdd_evidence"],
            ".cursor/skills/test-generator/SKILL.md": ["integration-test", "integration_report"],
        }
        for rel, needles in expected.items():
            path = ROOT / rel
            self.assertTrue(path.exists(), f"缺少 Skill: {rel}")
            text = path.read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, f"{rel} 缺 client-dev 契约: {needle}")

    def test_gate_advances_through_client_dev_file_facts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="client-dev-gate-") as raw:
            root = Path(raw)
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / ".workflows", root / ".workflows")
            shutil.copytree(ROOT / "Templates", root / "Templates")
            for folder in ["Plans/Epic", "Plans/需求分析", "Plans/需求排序", "Plans/技术方案", "Plans/功能开发", "Plans/自动化测试", "Contexts/决策"]:
                (root / folder).mkdir(parents=True, exist_ok=True)
            self.write(root / "Contexts/决策/Skill反馈协议.md", "# Skill反馈协议")

            def receipt(skill: str, plan: str, stage: str | None = None) -> str:
                stage_line = f"  workflow_stage: {stage}\n" if stage else ""
                return f"""## 反馈（skill_run）

```yaml
skill_run:
  skill: {skill}
{stage_line}  plan: {plan}
  date: 2026-08-05
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "client-dev gate fixture"
  contexts_missing: []
  contexts_stale: []
```
"""

            epic = self.write(root / "Plans/Epic/demo.md", """
                ---
                workflow: client-dev
                plans:
                  requirement: Plans/需求分析/demo.md
                  prioritization: Plans/需求排序/demo.md
                  architecture: Plans/技术方案/demo.md
                  development: Plans/功能开发/demo.md
                  integration: Plans/自动化测试/demo.md
                ---
                # Demo Epic
            """)
            requirement = self.write(root / "Plans/需求分析/demo.md", """
                ---
                status: 已采纳
                p0_open: 0
                ---
                # 需求
                ## 边界情况清单
                已覆盖空态。
                ## 异常流程矩阵
                已覆盖失败恢复。
                ## 验收标准
                | # | 验收项 | 优先级 |
                |---|--------|--------|
                | AC1 | 用户可创建草稿 | P0 |
            """)
            requirement.write_text(requirement.read_text(encoding="utf-8") + receipt(
                "requirement-analyst", "Plans/需求分析/demo.md"
            ), encoding="utf-8")
            gate = lambda: json.loads(subprocess.run(
                ["bash", "scripts/workflow-gate.sh", "--workflow", "client-dev", "--epic", str(epic), "--json", "--probe"],
                cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
            ).stdout)
            first_gate = gate()
            self.assertEqual(first_gate["current_state"], "prioritization", first_gate)

            prioritization = self.write(root / "Plans/需求排序/demo.md", """
                ---
                status: 已采纳
                backlog_index: Plans/需求排序/demo.backlog.json
                ---
                # 排序
                ## 排序原则
                价值与成本分开。
                ## 需求排序
                REQ-1 为 P0。
                ## 团队确认
                已确认。
            """)
            prioritization.write_text(prioritization.read_text(encoding="utf-8") + receipt(
                "backlog-prioritization-assistant", "Plans/需求排序/demo.md", "prioritization"
            ), encoding="utf-8")
            self.dump(root / "Plans/需求排序/demo.backlog.json", {"confirmed": True, "requirements": [{
                "id": "REQ-1", "title": "创建草稿", "business_value": "high", "urgency": "high",
                "dependencies": [], "priority": "P0", "reason": "核心路径", "confirmed": True,
            }]})
            self.assertEqual(gate()["current_state"], "architecture")

            architecture = self.write(root / "Plans/技术方案/demo.md", """
                ---
                status: 已采纳
                ---
                # 架构
                ## 模块边界
                草稿模块独立。
                ## 数据模型
                Draft 聚合。
                ## API Schema
                POST /drafts。
                ## 非功能约束
                幂等。
                ## ADR
                ADR-1 使用本地优先。
                ## 需求影响矩阵
                REQ-1 映射草稿模块。
            """)
            architecture.write_text(architecture.read_text(encoding="utf-8") + receipt(
                "architecture-design-assistant", "Plans/技术方案/demo.md", "architecture"
            ), encoding="utf-8")
            self.assertEqual(gate()["current_state"], "story-split")

            development = self.write(root / "Plans/功能开发/demo.md", """
                ---
                story_index: Plans/功能开发/demo.stories.json
                ---
                # 故事拆分
            """)
            development.write_text(development.read_text(encoding="utf-8") + receipt(
                "task-splitter", "Plans/功能开发/demo.md", "story-split"
            ), encoding="utf-8")
            self.dump(root / "Plans/功能开发/demo.stories.json", {"scope_confirmed": True, "stories": [{
                "id": "US-1", "title": "用户可以创建草稿", "path": "Plans/功能开发/us-1.md",
                "story_points": 5, "estimate_confirmed": True, "priority": "P0", "sprint_scope": True,
                "dependencies": [], "acceptance_criteria": ["AC1"], "architecture_refs": ["ADR-1"], "vertical_slice": True,
            }]})
            self.write(root / "Plans/功能开发/us-1.md", """
                ---
                story_id: US-1
                status: 待开发
                implementation_design: Plans/功能开发/us-1.impl.json
                tdd_evidence: Plans/功能开发/us-1.tdd.json
                ---
                # US-1
            """)
            self.assertEqual(gate()["current_state"], "implementation-design")
            self.write(root / "src/features/draft/view.ts", "export const existing = true")
            self.dump(root / "Plans/功能开发/us-1.impl.json", {
                "story_id": "US-1",
                "codebase_available": True,
                "codebase_read": [{"path": "src/features/draft/view.ts", "reason": "同模块分层和命名参考"}],
                "target_files": {
                    "modify": [{"path": "src/features/draft/view.ts", "purpose": "接入创建入口", "layer": "Presentation"}],
                    "create": [{"path": "src/features/draft/use-case.ts", "reason": "现有模块没有创建用例", "naming_basis": "沿用 use-case 命名", "layer": "Domain"}],
                },
                "module_boundary": {"layer": "Presentation/Domain", "dependency_rule": "Presentation 只依赖 Domain"},
                "tests": {"red": [{"path": "tests/draft.test.ts", "command": "pytest tests/draft.test.ts"}]},
                "risks": [],
                "blocked_questions": [],
                "confirmed": True,
            })
            development.write_text(development.read_text(encoding="utf-8") + "\n## 实现落点设计\nUS-1 已完成代码落点设计。\n" + receipt(
                "implementation-design-assistant", "Plans/功能开发/demo.md", "implementation-design"
            ), encoding="utf-8")
            self.assertEqual(gate()["current_state"], "story-development")

            self.write(root / "Plans/功能开发/us-1.md", """
                ---
                story_id: US-1
                status: 已完成
                implementation_design: Plans/功能开发/us-1.impl.json
                tdd_evidence: Plans/功能开发/us-1.tdd.json
                ---
                # US-1
            """)
            self.dump(root / "Plans/功能开发/us-1.tdd.json", {
                "story_id": "US-1", "commit": "abc123",
                "red": {"command": "pytest story", "exit_code": 1, "reason": "功能尚未实现", "at": "t1"},
                "green": {"command": "pytest story", "exit_code": 0, "at": "t2"},
                "refactor": {"command": "pytest story", "exit_code": 0, "at": "t3"},
                "integration_smoke": {"command": "pytest smoke", "exit_code": 0, "at": "t4"},
                "acceptance": [{"ac_id": "AC1", "pass": True}],
            })
            development.write_text(development.read_text(encoding="utf-8") + receipt(
                "feature-dev-assistant", "Plans/功能开发/demo.md", "story-development"
            ), encoding="utf-8")
            self.assertEqual(gate()["current_state"], "integration-test")

            integration = self.write(root / "Plans/自动化测试/demo.md", """
                ---
                story_index: Plans/功能开发/demo.stories.json
                target_commit: abc123
                integration_report: Plans/自动化测试/demo.integration.json
                ---
                # 集成测试
            """)
            integration.write_text(integration.read_text(encoding="utf-8") + receipt(
                "test-generator", "Plans/自动化测试/demo.md", "integration-test"
            ), encoding="utf-8")
            self.dump(root / "Plans/自动化测试/demo.integration.json", {
                "commit": "abc123", "all_scope_stories_completed": True,
                "suites": [{"name": "cross-story", "command": "pytest integration", "exit_code": 0}],
            })
            self.assertEqual(gate()["current_state"], "done")
            self.assertTrue(all(path.exists() for path in [requirement, prioritization, architecture, development, integration]))

    def test_epic_without_version_uses_client_dev_directly(self) -> None:
        with tempfile.TemporaryDirectory(prefix="client-dev-unversioned-") as raw:
            root = Path(raw)
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / ".workflows", root / ".workflows")
            shutil.copytree(ROOT / "Templates", root / "Templates")
            for folder in ["Plans/Epic", "Plans/需求分析", "Plans/需求排序", "Plans/技术方案", "Plans/自动化测试", "Plans/功能开发", "Contexts/决策"]:
                (root / folder).mkdir(parents=True, exist_ok=True)
            self.write(root / "Contexts/决策/Skill反馈协议.md", "# Skill反馈协议")
            epic = self.write(root / "Plans/Epic/legacy.md", """
                ---
                workflow: client-dev
                plans:
                  requirement: Plans/需求分析/legacy.md
                  architecture: null
                  test: null
                  development: null
                ---
                # Legacy
            """)
            req = self.write(root / "Plans/需求分析/legacy.md", """
                ---
                status: 已采纳
                p0_open: 0
                ---
                ## 边界情况清单
                已覆盖。
                ## 异常流程矩阵
                已覆盖。
                ## 验收标准
                AC1。

                ```yaml
                skill_run:
                  skill: requirement-analyst
                  plan: Plans/需求分析/legacy.md
                  date: 2026-08-05
                  contexts_used:
                    - path: Contexts/决策/Skill反馈协议.md
                      utility: high
                      reason: "unversioned Epic fixture"
                  contexts_missing: []
                  contexts_stale: []
                ```
            """)
            proc = subprocess.run(
                ["bash", "scripts/workflow-gate.sh", "--workflow", "client-dev", "--epic", str(epic), "--json", "--probe"],
                cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            result = json.loads(proc.stdout)
            self.assertEqual(result["current_state"], "prioritization", result)
            self.assertTrue(req.exists())

    def test_ac13_kanban_projects_dynamic_story_points_and_tdd_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="client-dev-kanban-") as raw:
            root = Path(raw)
            shutil.copytree(ROOT / ".workflows", root / ".workflows")
            epic = self.write(root / "Plans/Epic/demo.md", """
                ---
                workflow: client-dev
                plans:
                  requirement: Plans/需求分析/demo.md
                  prioritization: Plans/需求排序/demo.md
                  architecture: Plans/技术方案/demo.md
                  development: Plans/功能开发/demo.md
                  integration: Plans/自动化测试/demo.md
                ---
                # Demo
            """)
            for rel in ["Plans/需求分析/demo.md", "Plans/需求排序/demo.md", "Plans/技术方案/demo.md"]:
                self.write(root / rel, "---\nstatus: 已采纳\n---\n# done")
            self.write(root / "Plans/功能开发/demo.md", """
                ---
                story_index: Plans/功能开发/demo.stories.json
                ---
                # Stories
            """)
            self.dump(root / "Plans/功能开发/demo.stories.json", {
                "scope_confirmed": True,
                "stories": [{
                    "id": "US-1", "title": "用户可创建草稿", "path": "Plans/功能开发/us-1.md",
                    "story_points": 5, "priority": "P0", "sprint_scope": True, "dependencies": [],
                }],
            })
            self.write(root / "Plans/功能开发/us-1.md", """
                ---
                status: 已完成
                implementation_design: Plans/功能开发/us-1.impl.json
                tdd_evidence: Plans/功能开发/us-1.tdd.json
                ---
                # US-1
            """)
            self.write(root / "src/features/draft/view.ts", "export const existing = true")
            self.dump(root / "Plans/功能开发/us-1.impl.json", {
                "codebase_available": True,
                "codebase_read": [{"path": "src/features/draft/view.ts", "reason": "同模块参考"}],
                "target_files": {"modify": [{"path": "src/features/draft/view.ts", "purpose": "接入", "layer": "Presentation"}], "create": []},
                "module_boundary": {"layer": "Presentation", "dependency_rule": "不直连 Data"},
                "tests": {"red": [{"path": "tests/draft.test.ts", "command": "pytest tests/draft.test.ts"}]},
                "risks": [],
                "blocked_questions": [],
                "confirmed": True,
            })
            self.dump(root / "Plans/功能开发/us-1.tdd.json", {
                "commit": "abc", "red": {"exit_code": 1}, "green": {"exit_code": 0},
                "refactor": {"exit_code": 0}, "integration_smoke": {"exit_code": 0},
            })
            spec = importlib.util.spec_from_file_location("kanban_server_client_dev", ROOT / "scripts/kanban-server.py")
            assert spec and spec.loader
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.ROOT = root
            mod.RUN_DIR = root / ".workflows/runs"
            mod.EVENT_DIR = root / ".workflows/events"
            mod.BLUEPRINT_DIR = root / ".workflows/blueprints"
            data = mod.scan_epic(epic)
            self.assertEqual(data["effective_workflow"], "client-dev")
            self.assertEqual(data["current_stage"], "integration-test")
            self.assertEqual(data["story_points_total"], 5)
            self.assertEqual(data["story_points_done"], 5)
            self.assertEqual(data["stories"][0]["state"], "done")
            self.assertEqual(data["slices"], [])


if __name__ == "__main__":
    unittest.main()
