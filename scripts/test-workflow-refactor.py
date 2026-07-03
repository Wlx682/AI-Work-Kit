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


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = textwrap.dedent(content).lstrip()
    # Fixture documents are authored inside indented Python blocks; markdown
    # gates expect frontmatter/headings at column 1.
    normalized = []
    for line in text.splitlines():
        while line.startswith("        "):
            line = line[8:]
        normalized.append(line)
    text = "\n".join(normalized)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def skill_run(skill: str, plan: str) -> str:
    return textwrap.dedent(
        f"""
        ## 反馈（skill_run）

        ```yaml
        skill_run:
          skill: {skill}
          plan: {plan}
          date: 2026-07-03
          contexts_used:
            - path: Contexts/决策/Skill反馈协议.md
              utility: high
              reason: 校验反馈块格式与必填字段。
        ```
        """
    ).strip()


def wbs_table(rows: list[int]) -> str:
    body = "\n".join(f"| {n} | fixture | ✅ |" for n in rows)
    return textwrap.dedent(
        f"""
        ## 三、WBS

        | 编号 | 任务 | 完成 |
        | --- | --- | --- |
        {body}

        ## 四、记录
        """
    ).strip()


class WorkflowRefactorTests(unittest.TestCase):
    maxDiff = None

    def test_router_skill_is_synced_and_legacy_full_cycle_assistant_removed(self) -> None:
        router_paths = [
            ROOT / ".cursor/skills/workflow-router/SKILL.md",
            ROOT / ".claude/skills/workflow-router/SKILL.md",
            ROOT / ".codex/skills/workflow-router/SKILL.md",
            ROOT / "Skills/workflow_router.md",
        ]
        for path in router_paths:
            self.assertTrue(path.exists(), f"缺少 workflow-router: {path}")
            text = path.read_text(encoding="utf-8")
            self.assertIn("workflow-router", text)
            self.assertIn("workflow-gate", text)

        legacy_paths = [
            ROOT / ".cursor/skills/full-cycle-assistant/SKILL.md",
            ROOT / ".claude/skills/full-cycle-assistant/SKILL.md",
            ROOT / ".codex/skills/full-cycle-assistant/SKILL.md",
            ROOT / "Skills/full_cycle_assistant.md",
        ]
        for path in legacy_paths:
            self.assertFalse(path.exists(), f"旧入口仍存在: {path}")

    def test_client_dev_blueprint_has_manifest_driven_full_workflow(self) -> None:
        bp = json.loads((ROOT / ".workflows/blueprints/client-dev.json").read_text(encoding="utf-8"))
        self.assertTrue(bp["usesEpic"])
        self.assertEqual(bp["gateScript"], "scripts/workflow-gate.sh")
        self.assertEqual(bp["bootScript"], "scripts/full-cycle-boot.sh")
        self.assertEqual(bp["epicTemplate"], "Templates/Epic模板-client-dev.md")
        self.assertTrue(bp["epicRequired"])
        self.assertTrue(bp["startup"]["createBoard"])
        self.assertEqual(bp["startup"]["boardSource"], "Epic")
        self.assertTrue(bp["startup"]["requireEpicBeforeBoot"])
        self.assertEqual(bp["startup"]["createEpicSkill"], "template-generator")

        stages = {stage["key"]: stage for stage in bp["stages"]}
        self.assertEqual(
            list(stages),
            ["requirement", "architecture", "test-first", "development", "verify", "review", "deploy", "retro"],
        )
        self.assertEqual(stages["verify"]["epicField"], "verify")
        self.assertEqual(stages["review"]["epicField"], "review")
        self.assertEqual(stages["retro"]["epicField"], "retro")
        self.assertEqual(stages["architecture"]["planFolder"], "Plans/技术方案")
        self.assertEqual(stages["development"]["skills"], ["task-splitter", "feature-dev-assistant", "figma-ui"])
        self.assertIn("workflow-router", (ROOT / "Skills/README.md").read_text(encoding="utf-8"))

    def test_workflow_blueprints_validate(self) -> None:
        proc = subprocess.run(
            ["python3", "scripts/validate-workflow-blueprint.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("OK:workflow-blueprint:.workflows/blueprints/client-dev.json", proc.stdout)
        self.assertIn("OK:workflow-blueprint:.workflows/blueprints/computer-mgmt.json", proc.stdout)

    def test_workflow_run_start_creates_instance_and_event(self) -> None:
        with self.fixture_repo() as tmp:
            proc = subprocess.run(
                ["python3", "scripts/workflow-run.py", "start", "--workflow", "computer-mgmt", "--project", "fixture"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            run_rel = proc.stdout.strip()
            run_file = tmp / run_rel
            self.assertTrue(run_file.exists(), proc.stdout)
            run_text = run_file.read_text(encoding="utf-8")
            self.assertIn('workflow_id: "computer-mgmt"', run_text)
            self.assertIn('current_stage: "inventory"', run_text)
            event_rel = run_text.split('events: "')[1].split('"')[0]
            event_file = tmp / event_rel
            self.assertTrue(event_file.exists(), event_rel)
            event = json.loads(event_file.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(event["type"], "workflow_run_started")
            self.assertEqual(event["workflow_id"], "computer-mgmt")

    def test_workflow_run_lifecycle_updates_state_and_events(self) -> None:
        with self.fixture_repo() as tmp:
            proc = subprocess.run(
                ["python3", "scripts/workflow-run.py", "start", "--workflow", "computer-mgmt", "--project", "fixture"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            run_rel = proc.stdout.strip()
            run_file = tmp / run_rel

            subprocess.run(
                ["python3", "scripts/workflow-run.py", "advance", "--run", run_rel, "--reason", "盘点完成"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            run_text = run_file.read_text(encoding="utf-8")
            self.assertIn('current_stage: "cleanup"', run_text)
            self.assertIn('status: "running"', run_text)
            self.assertIn('from: "inventory"', run_text)
            self.assertIn('to: "cleanup"', run_text)

            subprocess.run(
                ["python3", "scripts/workflow-run.py", "block", "--run", run_rel, "--reason", "等待用户确认删除列表"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            blocked = subprocess.run(
                ["python3", "scripts/workflow-run.py", "advance", "--run", run_rel],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("请先 resume", blocked.stderr)

            subprocess.run(
                ["python3", "scripts/workflow-run.py", "resume", "--run", run_rel, "--reason", "用户已确认"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            subprocess.run(
                ["python3", "scripts/workflow-run.py", "done", "--run", run_rel, "--reason", "复核完成"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            final_text = run_file.read_text(encoding="utf-8")
            self.assertIn('current_stage: "done"', final_text)
            self.assertIn('status: "done"', final_text)
            event_rel = final_text.split('events: "')[1].split('"')[0]
            event_lines = (tmp / event_rel).read_text(encoding="utf-8").splitlines()
            event_types = [json.loads(line)["type"] for line in event_lines]
            self.assertEqual(
                event_types,
                [
                    "workflow_run_started",
                    "workflow_run_advanced",
                    "workflow_run_blocked",
                    "workflow_run_resumed",
                    "workflow_run_done",
                ],
            )

    def test_feedback_aggregate_parses_inline_empty_arrays(self) -> None:
        spec = importlib.util.spec_from_file_location("feedback_aggregate", ROOT / "scripts/feedback-aggregate.py")
        self.assertIsNotNone(spec)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        parsed = mod.parse_skill_run(
            textwrap.dedent(
                """
                skill_run:
                  skill: workflow-router
                  plan: orphan
                  date: 2026-07-03
                  contexts_used:
                    - path: Contexts/决策/Skill反馈协议.md
                      utility: high
                      reason: 校验反馈块格式。
                  contexts_missing: []
                  contexts_stale: []
                """
            ).strip()
        )
        sr = parsed["skill_run"]
        self.assertEqual(sr["contexts_missing"], [])
        self.assertEqual(sr["contexts_stale"], [])
        agg = mod.aggregate([sr], "2026-07")
        self.assertNotIn(("[", 1), agg["missing"])
        self.assertEqual(agg["missing"], [])

    def test_workflow_router_hits_expected_workflows_from_natural_language(self) -> None:
        cases = {
            "帮我启动一个会员中心客户端功能项目": "client-dev",
            "全流程开发一下支付收银台": "client-dev",
            "客户端全流程开发prd = XXX": "client-dev",
            "这个需求一条龙走完": "client-dev",
            "做个功能：订单筛选": "client-dev",
            "实现一个客户端设置页": "client-dev",
            "开始做这个项目：会员权益": "client-dev",
            "启动项目，做订单售后模块": "client-dev",
            "启动全流程：会员中心重构": "client-dev",
            "/full-cycle 模块=订单筛选": "client-dev",
            "/full-cycle": "client-dev",
            "full-cycle 新建支付模块": "client-dev",
            "全流程闭环做一下搜索页": "client-dev",
            "从0到1做个客户端功能": "client-dev",
            "新需求：客户端弹窗改版": "client-dev",
            "开发功能：批量导出": "client-dev",
            "开发一个客户端功能，支持收银台分组": "client-dev",
            "帮我开发会员等级模块": "client-dev",
            "帮我清理电脑缓存和大文件": "computer-mgmt",
            "整理电脑，顺便做备份": "computer-mgmt",
            "磁盘清理和系统加固走一遍": "computer-mgmt",
            "电脑管理：先盘点启动项": "computer-mgmt",
            "Mac 磁盘满了，帮我释放空间": "computer-mgmt",
            "帮我看一下电脑空间": "computer-mgmt",
            "看一下电脑空间": "computer-mgmt",
            "电脑空间够不够": "computer-mgmt",
            "磁盘空间还有多少": "computer-mgmt",
            "空间不够了，帮我看看": "computer-mgmt",
            "清理一下电脑里的缓存": "computer-mgmt",
            "系统加固检查跑一遍": "computer-mgmt",
            "电脑备份走一遍": "computer-mgmt",
            "备份电脑关键配置": "computer-mgmt",
            "整理电脑启动项和大文件": "computer-mgmt",
            "/full-cycle 帮我清理电脑": "computer-mgmt",
            "workflow=computer-mgmt 帮我跑一下": "computer-mgmt",
            "工作流:computer-mgmt 帮我清理": "computer-mgmt",
            "/workflow computer-mgmt 先盘点": "computer-mgmt",
            "workflow=client-dev 启动这个项目": "client-dev",
            "工作流：client-dev 做订单模块": "client-dev",
        }
        for utterance, expected in cases.items():
            with self.subTest(utterance=utterance):
                result = self.route_utterance(utterance)
                self.assertTrue(result["matched"], result)
                self.assertEqual(result["workflow"], expected, result)
                self.assertGreater(result["score"], 0, result)
                self.assertTrue(result["hits"], result)

    def test_workflow_router_does_not_hijack_single_stage_intents(self) -> None:
        utterances = [
            "帮我看一下这个 PRD 有没有问题",
            "写一份日报",
            "审计学习进度",
            "生成技术方案模板",
            "做界面，对一下 Figma 稿",
            "写测试计划",
            "实现这个函数",
            "帮我写个脚本",
            "修一下这个 bug",
            "开发环境启动失败，帮我看看",
            "备份这份文档",
            "整理需求列表",
            "清理一下这篇文档",
            "帮我做代码 review",
            "部署检查清单生成一下",
            "复盘一下这个项目",
            "学习路线继续",
            "workflow=unknown 启动项目",
            "工作流：not-exist 帮我清理电脑",
        ]
        for utterance in utterances:
            with self.subTest(utterance=utterance):
                result = self.route_utterance(utterance)
                self.assertFalse(result["matched"], result)
                self.assertIsNone(result["workflow"], result)

    def test_workflow_gate_bootstraps_client_dev_when_project_has_no_epic(self) -> None:
        with self.fixture_repo() as tmp:
            data = self.run_gate(tmp, "--workflow", "client-dev", "--project", "不存在的项目", "--json")
        self.assertEqual(data["current_state"], "requirement")
        self.assertEqual(data["next_state"], "bootstrap-epic")
        self.assertEqual(data["recommended_skill"], "template-generator")
        self.assertTrue(any("无 Epic plan" in item for item in data["blockers"]))
        self.assertEqual(data["plans_found"], [])

    def test_workflow_gate_supports_non_epic_computer_management_blueprint(self) -> None:
        with self.fixture_repo() as tmp:
            data = self.run_gate(tmp, "--workflow", "computer-mgmt", "--json")
        self.assertFalse(data["uses_epic"])
        self.assertEqual(data["constitution"]["status"], "not-configured")
        self.assertEqual(data["current_state"], "inventory")
        self.assertEqual(data["next_state"], "cleanup")
        self.assertEqual(data["recommended_skill"], "material-prep-assistant")
        self.assertTrue(any("盘点" in item and "子 Plan 未创建" in item for item in data["blockers"]))

    def test_workflow_gate_reaches_done_for_complete_client_dev_fixture(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            data = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md", "--json")
        self.assertEqual(data["current_state"], "done")
        self.assertEqual(data["next_state"], "done")
        self.assertEqual(data["blockers"], [])
        self.assertEqual(data["constitution"]["path"], ".workflows/constitution.json")
        self.assertEqual(data["constitution"]["status"], "ok")
        self.assertIn("OK", data["gate_development"])
        self.assertTrue(any(item.startswith("development:Plans/功能开发/") for item in data["plans_found"]))

    def test_workflow_gate_json_output_handles_multiline_gate_result(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            data = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md", "--json")
        self.assertIsInstance(data["gate_development"], str)
        self.assertIn("OK:skill_run", data["gate_development"])
        self.assertIn("\n", data["gate_development"])

    def test_gate_parse_supports_negative_ac_and_filters_placeholder_tests(self) -> None:
        with self.fixture_repo() as tmp:
            req = tmp / "Plans/需求分析/ac.md"
            test = tmp / "Plans/自动化测试/ac.md"
            write_file(
                req,
                """
                # AC fixture

                ## 九、验收标准

                | # | 验收项 | 锚定事件 | Given | When | Then | 优先级 |
                |---|--------|----------|-------|------|------|--------|
                | AC1 | 正例 | 已完成 | a | b | c | P0 |
                | AC1-反 | 反例 | — | a | b | 不应发生 | P0 |
                | AC2 | 次要 | 已完成 | a | b | c | P1 |
                """,
            )
            write_file(
                test,
                """
                # Test fixture

                ## 二、用例映射（链需求验收标准）

                | 验收项 # | 测试用例 ID | 类型 | 描述 | 状态 |
                |----------|-------------|------|------|------|
                | AC1 | UT-001 | 单元 | 覆盖 AC1 | 未实现 |
                | AC1-反 | UT-002 | 单元 | 【】 | ☐ |
                | AC2 | UT-003 | 单元 | 覆盖 AC2 | 未实现 |
                """,
            )
            spec = importlib.util.spec_from_file_location("gate_parse", ROOT / "scripts/gate_parse.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            acs = mod.parse_ac_table(req)
            tests = mod.parse_test_map(test)
            self.assertIn("AC1-反", acs)
            self.assertEqual(acs["AC1-反"]["priority"], "P0")
            self.assertIn("AC1", tests)
            self.assertNotIn("AC1-反", tests)

    def test_gate_parse_reads_frontmatter_plan_index_and_wbs_status(self) -> None:
        with self.fixture_repo() as tmp:
            plan = tmp / "Plans/Epic/parse.md"
            write_file(
                plan,
                """
                ---
                workflow: "client-dev" # 展示注释
                lifecycle_state: requirement  # DEPRECATED
                含业务逻辑: 是
                plans:
                  requirement: Plans/需求分析/parse.md
                  test: "Plans/自动化测试/parse.md"
                ---

                # Parse fixture

                ```
                [x] 1. done
                [~] 2. doing
                [ ] 3. todo
                ```

                | 4 | table done | ✅ |
                | 5 | table todo | ☐ |
                """,
            )
            spec = importlib.util.spec_from_file_location("gate_parse", ROOT / "scripts/gate_parse.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            fm = mod.read_frontmatter(plan)
            self.assertEqual(fm["workflow"], "client-dev")
            self.assertEqual(fm["lifecycle_state"], "requirement")
            self.assertEqual(fm["含业务逻辑"], "是")
            plans = mod.read_plan_index(plan)
            self.assertEqual(plans["requirement"], "Plans/需求分析/parse.md")
            self.assertEqual(plans["test"], "Plans/自动化测试/parse.md")
            self.assertEqual(mod.wbs_slice_status(plan, 1), "x")
            self.assertEqual(mod.wbs_slice_status(plan, 2), "~")
            self.assertEqual(mod.wbs_slice_status(plan, 3), " ")
            self.assertEqual(mod.wbs_slice_status(plan, 4), "x")
            self.assertEqual(mod.wbs_slice_status(plan, 5), " ")
            self.assertIsNone(mod.wbs_slice_status(plan, 6))

    def test_traceability_blocks_missing_p0_and_negative_test_coverage(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_traceability_fixture(tmp, cover_tests=False, include_dev=False)
            proc = subprocess.run(
                ["python3", "scripts/traceability-check.py", "--epic", "Plans/Epic/trace.md", "--check", "test"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("AC1(P0) 无测试覆盖", proc.stderr)
        self.assertIn("AC1-反(P0) 无测试覆盖", proc.stderr)

    def test_workflow_gate_test_traceability_does_not_require_development_plan(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_traceability_fixture(tmp, cover_tests=False, include_dev=False)
            data = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/trace.md", "--json")
        self.assertEqual(data["current_state"], "test-first")
        self.assertTrue(any("testTraceability" in item for item in data["blockers"]))
        self.assertFalse(any("devTraceability" in item for item in data["blockers"]))
        rules = {item["id"]: item["status"] for item in data["constitution"]["rules"]}
        self.assertEqual(rules["traceability"], "blocked")

    def test_workflow_status_summarizes_done_state_for_humans(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            proc = subprocess.run(
                [
                    "python3",
                    "scripts/workflow-status.py",
                    "--workflow",
                    "client-dev",
                    "--epic",
                    "Plans/Epic/fixture.md",
                    "--json",
                ],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            data = json.loads(proc.stdout)
        self.assertEqual(data["current"], "全部完成")
        self.assertFalse(data["blocked"])
        self.assertEqual(data["blockers"], [])
        self.assertEqual(data["next"], "归档或蒸馏可复用结论")

    def test_workflow_status_translates_traceability_blocker(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_traceability_fixture(tmp, cover_tests=False, include_dev=False)
            proc = subprocess.run(
                [
                    "python3",
                    "scripts/workflow-status.py",
                    "--workflow",
                    "client-dev",
                    "--epic",
                    "Plans/Epic/trace.md",
                    "--json",
                ],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            data = json.loads(proc.stdout)
        self.assertEqual(data["current"], "验收测试先行")
        self.assertTrue(data["blocked"])
        self.assertTrue(any("验收标准缺测试覆盖" in item for item in data["blockers"]))
        self.assertTrue(any("AC1-反" in item for item in data["blockers"]))
        self.assertFalse(any("BLOCKED:" in item for item in data["blockers"]))
        self.assertEqual(data["next"], "补自动化测试 plan 的用例映射")
        self.assertIn("/resume plan=Plans/自动化测试/trace.md", data["resume"])

    def test_traceability_blocks_missing_development_p0_coverage(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_traceability_fixture(tmp, cover_tests=True, include_dev=True, cover_dev=False)
            proc = subprocess.run(
                ["python3", "scripts/traceability-check.py", "--epic", "Plans/Epic/trace.md", "--check", "dev"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("AC1(P0) 无开发任务覆盖", proc.stderr)
        self.assertIn("AC1-反(P0) 无开发任务覆盖", proc.stderr)

    def test_constitution_check_aggregates_client_dev_gate_results(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            proc = subprocess.run(
                ["python3", "scripts/constitution-check.py", "--epic", "Plans/Epic/fixture.md", "--json"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["constitution"], ".workflows/constitution.json")
        rules = {item["id"]: item["status"] for item in data["rules"]}
        self.assertEqual(rules["traceability"], "ok")
        self.assertEqual(rules["figma_forced"], "indexed")

    def test_constitution_check_reports_traceability_blocker_without_rejudging(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_traceability_fixture(tmp, cover_tests=False, include_dev=False)
            proc = subprocess.run(
                ["python3", "scripts/constitution-check.py", "--epic", "Plans/Epic/trace.md", "--json"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            data = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(data["status"], "blocked")
        rules = {item["id"]: item["status"] for item in data["rules"]}
        self.assertEqual(rules["traceability"], "blocked")
        self.assertTrue(any("testTraceability" in item for item in data["blockers"]))

    def test_constitution_check_is_blueprint_opt_in_not_global(self) -> None:
        proc = subprocess.run(
            ["python3", "scripts/constitution-check.py", "--workflow", "computer-mgmt", "--json"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "not-configured")
        self.assertIsNone(data["constitution"])

    @staticmethod
    def run_gate(tmp: Path, *args: str) -> dict:
        proc = subprocess.run(
            ["bash", "scripts/workflow-gate.sh", *args],
            cwd=tmp,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return json.loads(proc.stdout)

    @staticmethod
    def route_utterance(utterance: str) -> dict:
        proc = subprocess.run(
            ["python3", "scripts/workflow-router-check.py", "--json", utterance],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return json.loads(proc.stdout)

    @staticmethod
    def fixture_repo():
        class Fixture:
            def __enter__(self) -> Path:
                self.tmpdir = tempfile.TemporaryDirectory(prefix="aiwk-workflow-test-")
                self.root = Path(self.tmpdir.name)
                shutil.copytree(ROOT / "scripts", self.root / "scripts")
                shutil.copytree(ROOT / ".workflows", self.root / ".workflows")
                shutil.copytree(ROOT / "Templates", self.root / "Templates")
                for plan_dir in [
                    "Plans/Epic",
                    "Plans/需求分析",
                    "Plans/技术方案",
                    "Plans/自动化测试",
                    "Plans/功能开发",
                    "Plans/非功能验证",
                    "Plans/代码重构",
                    "Plans/部署",
                    "Plans/最佳实践",
                    "Plans/电脑管理",
                ]:
                    (self.root / plan_dir).mkdir(parents=True, exist_ok=True)
                write_file(self.root / "Contexts/决策/Skill反馈协议.md", "# Skill反馈协议\n")
                write_file(self.root / "Contexts/决策/母子plan投影规则.md", "# 母子plan投影规则\n")
                write_file(self.root / "Contexts/需求分析/需求分析规范.md", "# 需求分析规范\n")
                return self.root

            def __exit__(self, exc_type, exc, tb) -> None:
                self.tmpdir.cleanup()

        return Fixture()

    @staticmethod
    def create_complete_client_dev_fixture(root: Path) -> None:
        epic = """
        ---
        project: fixture
        workflow: client-dev
        lifecycle_state: obsolete-hint
        含业务逻辑: 是
        p0_open: 0
        plans:
          requirement: Plans/需求分析/fixture.md
          architecture: Plans/技术方案/fixture.md
          test: Plans/自动化测试/fixture.md
          development: Plans/功能开发/fixture.md
          verify: Plans/非功能验证/fixture.md
          review: Plans/代码重构/fixture.md
          deploy: Plans/部署/fixture.md
          retro: Plans/最佳实践/fixture.md
        ---

        # Fixture Epic

        ## 三、WBS

        ```
        [x] 1. 事件风暴完成
        [x] 2. 实例化需求完成
        [x] 3. 技术方案完成
        [x] 4. 验收测试先行完成
        [x] 5. Domain 完成
        [x] 6. Data 完成
        [x] 7. UI 完成
        [x] 8. 交互完成
        [x] 9. 单测完成
        [x] 10. 联调完成
        [x] 11. 非功能验证完成
        [x] 12. Review 完成
        [x] 13. 发布检查完成
        [x] 14. 监控完成
        [x] 15. 回顾完成
        ```

        ## 四、记录
        """
        write_file(root / "Plans/Epic/fixture.md", epic)

        requirement_body = "需求背景：" + ("这是用于自动化测试的需求说明。" * 45)
        requirement = f"""
        ---
        status: 已采纳
        p0_open: 0
        epic: Plans/Epic/fixture.md
        ---

        # 需求分析 fixture

        {requirement_body}

        ## 九、验收标准

        | # | 验收项 | 锚定事件 | Given | When | Then | 优先级 |
        |---|--------|----------|-------|------|------|--------|
        | AC1 | 完整蓝图进入 done | 已创建完整子 Plan | 运行 gate | 查看 JSON | current_state=done | P0 |
        | AC1-反 | 不串其它 Epic | — | 指定 Epic | 运行 gate | 不扫描其它 plan | P0 |
        | AC2 | 不存在项目要求 bootstrap | — | 指定不存在项目 | 运行 gate | 提示 bootstrap | P1 |

        {wbs_table([1, 2])}

        {skill_run("requirement-analyst", "Plans/需求分析/fixture.md")}
        """
        write_file(root / "Plans/需求分析/fixture.md", requirement)

        stage_specs = [
            ("Plans/技术方案/fixture.md", "architecture-design-assistant", [3], "已采纳", ""),
            (
                "Plans/自动化测试/fixture.md",
                "test-generator",
                [4],
                "",
                """
                ## 二、用例映射（链需求验收标准）

                | 验收项 # | 测试用例 ID | 类型 | 描述 | 状态 |
                |----------|-------------|------|------|------|
                | AC1 | UT-001 | 单元 | 覆盖完整蓝图 done 判断 | 未实现 |
                | AC1-反 | UT-002 | 单元 | 覆盖指定 Epic 不串 plan | 未实现 |
                | AC2 | UT-003 | 单元 | 覆盖 bootstrap 提示 | 未实现 |
                """,
            ),
            ("Plans/非功能验证/fixture.md", "nfr-assistant", [11], "", ""),
            ("Plans/代码重构/fixture.md", "review-assistant", [12], "", ""),
            ("Plans/部署/fixture.md", "deployment-assistant", [13, 14], "", ""),
            ("Plans/最佳实践/fixture.md", "retro-assistant", [15], "", ""),
        ]
        for rel, skill, rows, status, extra_body in stage_specs:
            frontmatter = f"status: {status}\n" if status else ""
            write_file(
                root / rel,
                f"""
                ---
                {frontmatter}epic: Plans/Epic/fixture.md
                ---

                # {rel}

                {extra_body}

                {wbs_table(rows)}

                {skill_run(skill, rel)}
                """,
            )

        development = f"""
        ---
        epic: Plans/Epic/fixture.md
        requirement_plan: Plans/需求分析/fixture.md
        p0_open: 0
        含业务逻辑: 是
        ---

        # 功能开发 fixture

        ## 一、需求分析

        - [[Plans/需求分析/fixture.md]]

        ## 二、技术方案

        - [[Plans/技术方案/fixture.md]]

        {wbs_table([5, 6, 7, 8, 9, 10])}

        ## 五、实施切片

        | # | 输入 | 输出 | 覆盖 AC | 验收 | 预估 | 阻塞 |
        |---|------|------|---------|------|------|------|
        | 5 | 需求 | Domain | AC1, AC1-反 | 业务规则完成 | 1d | — |
        | 6 | 需求 | Data | AC2 | 数据接入完成 | 1d | — |

        {skill_run("feature-dev-assistant", "Plans/功能开发/fixture.md")}
        """
        write_file(root / "Plans/功能开发/fixture.md", development)

    @staticmethod
    def create_traceability_fixture(
        root: Path,
        *,
        cover_tests: bool,
        include_dev: bool,
        cover_dev: bool = True,
    ) -> None:
        dev_plan_line = "  development: Plans/功能开发/trace.md" if include_dev else ""
        if include_dev:
            dev_plan_line = "  development: Plans/功能开发/trace.md"
        write_file(
            root / "Plans/Epic/trace.md",
            f"""
        ---
        project: trace
        workflow: client-dev
        含业务逻辑: 否
        p0_open: 0
        plans:
          requirement: Plans/需求分析/trace.md
          test: Plans/自动化测试/trace.md
        {dev_plan_line}
        ---

        # Trace Epic
        """,
        )
        requirement_body = "需求背景：" + ("这是 traceability fixture。" * 45)
        write_file(
            root / "Plans/需求分析/trace.md",
            f"""
        ---
        status: 已采纳
        p0_open: 0
        epic: Plans/Epic/trace.md
        ---

        # Trace Requirement

        {requirement_body}

        ## 九、验收标准

        | # | 验收项 | 锚定事件 | Given | When | Then | 优先级 |
        |---|--------|----------|-------|------|------|--------|
        | AC1 | 正例 | 已完成 | a | b | c | P0 |
        | AC1-反 | 反例 | — | a | b | 不应发生 | P0 |
        | AC2 | 次要 | 已完成 | a | b | c | P1 |

        {wbs_table([1, 2])}

        {skill_run("requirement-analyst", "Plans/需求分析/trace.md")}
        """,
        )
        if cover_tests:
            test_rows = """
            | AC1 | UT-001 | 单元 | 覆盖 AC1 | 未实现 |
            | AC1-反 | UT-002 | 单元 | 覆盖 AC1-反 | 未实现 |
            | AC2 | UT-003 | 单元 | 覆盖 AC2 | 未实现 |
            """
        else:
            test_rows = """
            | AC1 | UT-001 | 单元 | 【】 | ☐ |
            | AC2 | UT-003 | 单元 | 覆盖 AC2 | 未实现 |
            """
        write_file(
            root / "Plans/自动化测试/trace.md",
            f"""
        ---
        epic: Plans/Epic/trace.md
        ---

        # Trace Test

        ## 二、用例映射（链需求验收标准）

        | 验收项 # | 测试用例 ID | 类型 | 描述 | 状态 |
        |----------|-------------|------|------|------|
        {test_rows}

        {wbs_table([4])}

        {skill_run("test-generator", "Plans/自动化测试/trace.md")}
        """,
        )
        if include_dev:
            dev_coverage = "AC1, AC1-反" if cover_dev else "—"
            write_file(
                root / "Plans/功能开发/trace.md",
                f"""
        ---
        epic: Plans/Epic/trace.md
        requirement_plan: Plans/需求分析/trace.md
        p0_open: 0
        含业务逻辑: 否
        ---

        # Trace Development

        ## 一、需求分析

        - [[Plans/需求分析/trace.md]]

        {wbs_table([5, 6, 7, 8, 9, 10])}

        ## 五、实施切片

        | # | 输入 | 输出 | 覆盖 AC | 验收 | 预估 | 阻塞 |
        |---|------|------|---------|------|------|------|
        | 5 | 需求 | Domain | {dev_coverage} | 完成 | 1d | — |

        {skill_run("feature-dev-assistant", "Plans/功能开发/trace.md")}
        """,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
