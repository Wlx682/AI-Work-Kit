#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib.util
import os
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
    # WBS 状态权威源 = fenced `[x] N.` checklist（与 gate_parse.wbs_slice_status 一致）。
    lines = "\n".join(f"[x] {n}. fixture" for n in rows)
    return "## 三、WBS\n\n```\n" + lines + "\n```\n\n## 四、记录"


def merge_analysis_sections(*, resolved: bool = True) -> str:
    decision_conclusion = "采用兼容并集，保留人工审核并新增自动校验" if resolved else "待确认"
    decision_owner = "支付模块开发负责人" if resolved else "待确认"
    decision_record = "2026-07-03 合并评审记录 #42" if resolved else "待确认"
    decision_status = "已决策" if resolved else "待决策"
    return textwrap.dedent(
        f"""
        ## 双边代码意图

        | 意图ID | 分支侧 | 文件/模块 | 代码变化 | 业务目标 | 行为/规则变化 | 证据 | 置信度 |
        |--------|--------|-----------|----------|----------|---------------|------|--------|
        | SI-001 | 源分支 | payment/risk.py | 增加自动风险校验 | 降低异常支付 | 支付提交前增加自动校验 | commit abc；test_risk.py | 高 |
        | TI-001 | 目标分支 | payment/review.py | 保留人工审核入口 | 控制高风险订单 | 高风险订单必须人工审核 | commit def；test_review.py | 高 |

        ## 业务冲突矩阵

        | 冲突ID | 关联意图 | 冲突类型 | 业务影响 | AI结论 | 需开发者决策 | 决策ID |
        |--------|----------|----------|----------|--------|----------------|--------|
        | MC-001 | SI-001, TI-001 | 业务规则 | 自动校验可能绕过人工审核 | 需开发者决策：代码证据不能确定审核优先级 | 是 | D-001 |

        ## 开发者决策清单

        | 决策ID | 待决策问题 | 可选方案及影响 | 开发者结论 | 决策人 | 确认记录 | 状态 |
        |--------|------------|----------------|------------|--------|----------|------|
        | D-001 | 自动校验后是否仍需人工审核 | A 保留审核更安全；B 自动放行吞吐更高 | {decision_conclusion} | {decision_owner} | {decision_record} | {decision_status} |

        ## 合并策略与验证映射

        | 冲突ID | 处理策略 | 影响范围 | 验证场景 | 状态 |
        |--------|----------|----------|----------|------|
        | MC-001 | 自动校验通过后高风险订单仍进入人工审核 | 支付提交与审核队列 | 高风险订单校验通过后仍生成审核任务 | 已规划 |
        """
    ).strip()


def merge_implementation_sections() -> str:
    return textwrap.dedent(
        """
        ## 决策落实记录

        | 追踪ID | 影响文件 | 落实方式 | 验证用例 | 状态 |
        |--------|----------|----------|----------|------|
        | MC-001 | payment/risk.py | 自动校验不直接改变人工审核状态 | test_risk_then_review | 已落实 |
        | D-001 | payment/review.py | 高风险订单始终进入人工审核队列 | test_high_risk_review_queue | 已落实 |

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


class WorkflowRefactorTests(unittest.TestCase):
    maxDiff = None

    def test_router_skill_is_synced(self) -> None:
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

    def test_client_dev_blueprint_has_manifest_driven_full_workflow(self) -> None:
        bp = json.loads((ROOT / ".workflows/blueprints/client-dev.json").read_text(encoding="utf-8"))
        self.assertTrue(bp["usesEpic"])
        self.assertEqual(bp["gateScript"], "scripts/workflow-gate.sh")
        self.assertEqual(bp["bootScript"], "scripts/workflow-board-boot.sh")
        self.assertEqual(bp["epicTemplate"], "Templates/Epic模板-client-dev.md")
        self.assertTrue(bp["epicRequired"])
        self.assertTrue(bp["startup"]["createBoard"])
        self.assertEqual(bp["startup"]["boardSource"], "Epic")
        self.assertTrue(bp["startup"]["requireEpicBeforeBoot"])
        self.assertEqual(bp["startup"]["createEpicSkill"], "template-generator")

        stages = {stage["key"]: stage for stage in bp["stages"]}
        self.assertEqual(
            list(stages),
            ["requirement", "architecture", "test-first", "split", "development"],
        )
        self.assertEqual(stages["test-first"]["epicField"], "test")
        self.assertEqual(stages["split"]["epicField"], "development")
        self.assertEqual(stages["development"]["epicField"], "development")
        self.assertEqual(stages["architecture"]["planFolder"], "Plans/技术方案")
        self.assertEqual(stages["development"]["skills"], ["feature-dev-assistant", "figma-ui"])
        self.assertIn("workflow-router", (ROOT / "Skills/README.md").read_text(encoding="utf-8"))
        epic_template = (ROOT / "Templates/Epic模板-client-dev.md").read_text(encoding="utf-8")
        for mark in ["[ ]", "[~]", "[-]", "[x]"]:
            self.assertIn(mark, epic_template)
        self.assertIn("optionalWbsSlices", epic_template)

    def test_feedback_aggregate_reads_open_candidates_from_pending_section(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            orphan = tmp / "Contexts/决策/孤立反馈记录.md"
            write_file(
                orphan,
                """
                # 孤立反馈记录

                ## 待整理

                ### 进化候选：候选 A

                - 证据：A

                ### 待整理：普通条目

                - 证据：不应进入进化候选清单

                ### 进化候选：候选 B

                - 证据：B

                ## 已归位

                - **2026-07-06** 进化候选：已完成，不应重复出现
                """,
            )
            spec = importlib.util.spec_from_file_location("feedback_aggregate", ROOT / "scripts/feedback-aggregate.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp

            titles = mod.scan_open_evolution_candidates()

        self.assertEqual(titles, ["进化候选：候选 A", "进化候选：候选 B"])

    def test_kanban_reads_evolution_candidates_from_pending_section(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            orphan = tmp / "Contexts/决策/孤立反馈记录.md"
            write_file(
                orphan,
                """
                # 孤立反馈记录

                ## 待整理

                ### 进化候选：候选 A

                - 证据：A 的摘要

                ### 待整理：普通条目

                - 证据：不应进入进化候选清单

                ## 已归位

                - **2026-07-06** 候选 B 已归位：验证通过
                """,
            )
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ORPHAN_FEEDBACK = orphan

            data = mod.read_evolution_candidates()

        self.assertEqual(data["pending"], [{"title": "候选 A", "summary": "证据：A 的摘要"}])
        self.assertEqual(data["resolved"], [{"date": "2026-07-06", "summary": "候选 B 已归位：验证通过"}])

    def test_kanban_revision_tracks_content_not_file_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            epic = tmp / "Plans/Epic/fixture.md"
            write_file(epic, "# fixture")
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            initial = mod.board_revision()
            content = epic.read_bytes()
            original_stat = epic.stat()
            epic.write_bytes(content)
            os.utime(epic, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns + 1_000_000_000))
            self.assertNotEqual(original_stat.st_mtime_ns, epic.stat().st_mtime_ns)
            timestamp_only = mod.board_revision()
            epic.write_text("# fixture changed\n", encoding="utf-8")
            content_changed = mod.board_revision()

        self.assertEqual(initial, timestamp_only)
        self.assertNotEqual(initial, content_changed)

    def test_kanban_poll_refresh_skips_unchanged_payload_and_entry_animation(self) -> None:
        html = (ROOT / "scripts/kanban/index.html").read_text(encoding="utf-8")

        self.assertIn("function boardContentSignature(data)", html)
        self.assertIn("skipUnchanged && envelope && boardContentSignature(nextEnvelope) === boardContentSignature(envelope)", html)
        self.assertIn("await loadBoard({ animate: false, skipUnchanged: true })", html)
        self.assertIn("function observeFades(animate = true)", html)
        self.assertIn("if (!animate) {", html)

    def test_kanban_derives_wbs_stage_from_blueprint(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            epic = tmp / "Plans/Epic/fixture.md"
            epic.write_text(
                epic.read_text(encoding="utf-8").replace("[x] 11. 非功能验证完成", "[ ] 11. 非功能验证完成"),
                encoding="utf-8",
            )
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.RUN_DIR = tmp / ".workflows/runs"
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            data = mod.scan_epic(epic)
            by_n = {item["n"]: item for item in data["slices"]}
        self.assertEqual(by_n[11]["stage_key"], "development")
        self.assertEqual(by_n[11]["plan_stage_key"], "development")
        self.assertEqual(by_n[11]["related_plan"], "Plans/功能开发/fixture.md")
        self.assertTrue(by_n[11]["done"])
        self.assertEqual(by_n[11]["derived_from"], "child-plan")

    def test_kanban_wbs_slices_follow_blueprint_and_child_plan_facts(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            epic = tmp / "Plans/Epic/fixture.md"
            development = tmp / "Plans/功能开发/fixture.md"
            development.write_text(
                development.read_text(encoding="utf-8").replace("[x] 9. fixture", "[ ] 9. fixture"),
                encoding="utf-8",
            )
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.RUN_DIR = tmp / ".workflows/runs"
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            data = mod.scan_epic(epic)
            by_n = {item["n"]: item for item in data["slices"]}

        expected = {
            1: ("requirement", "requirement", "Plans/需求分析/fixture.md"),
            2: ("requirement", "requirement", "Plans/需求分析/fixture.md"),
            3: ("architecture", "architecture", "Plans/技术方案/fixture.md"),
            4: ("test-first", "test", "Plans/自动化测试/fixture.md"),
            5: ("split", "development", "Plans/功能开发/fixture.md"),
            6: ("development", "development", "Plans/功能开发/fixture.md"),
            7: ("development", "development", "Plans/功能开发/fixture.md"),
            8: ("development", "development", "Plans/功能开发/fixture.md"),
            9: ("development", "development", "Plans/功能开发/fixture.md"),
            10: ("development", "development", "Plans/功能开发/fixture.md"),
            11: ("development", "development", "Plans/功能开发/fixture.md"),
        }
        for n, (stage_key, plan_stage_key, related_plan) in expected.items():
            self.assertEqual(by_n[n]["stage_key"], stage_key, f"WBS {n} stage")
            self.assertEqual(by_n[n]["plan_stage_key"], plan_stage_key, f"WBS {n} plan stage")
            self.assertEqual(by_n[n]["related_plan"], related_plan, f"WBS {n} related plan")
            self.assertEqual(by_n[n]["derived_from"], "child-plan", f"WBS {n} fact source")

        # 子 Plan 是事实源：即使 Epic 字面量仍是 [x]，功能开发子 Plan 的 WBS9 未完成也应让看板卡住。
        self.assertFalse(by_n[9]["done"])
        self.assertEqual(data["next_slice"], 9)
        self.assertEqual(data["current_stage"], "development")
        self.assertEqual(data["slices_done"], 14)
        self.assertEqual(data["slices_total"], 15)
        # 蓝图未声明的历史切片保留 Epic 字面量回退，不强行推断。
        self.assertEqual(by_n[12]["derived_from"], "epic-literal")

    def test_kanban_slice_action_writes_child_plan_and_enforces_optional_skip(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            bp_file = tmp / ".workflows/blueprints/client-dev.json"
            bp = json.loads(bp_file.read_text(encoding="utf-8"))
            for stage in bp["stages"]:
                if stage["key"] == "development":
                    stage["optionalWbsSlices"] = [11]
            bp_file.write_text(json.dumps(bp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.RUN_DIR = tmp / ".workflows/runs"
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            epic = tmp / "Plans/Epic/fixture.md"
            result = mod.update_slice_from_epic(epic, 11, "skipped", "test")
            data = mod.scan_epic(epic)
            by_n = {item["n"]: item for item in data["slices"]}
            event_file = tmp / ".workflows/events/fixture.events.jsonl"
            events = [json.loads(l) for l in event_file.read_text(encoding="utf-8").splitlines() if l.strip()]
            progress = data.get("progress_history") or {}

            with self.assertRaisesRegex(ValueError, "not optional"):
                mod.update_slice_from_epic(epic, 10, "skipped", "test")

            self.assertEqual(result["target"], "Plans/功能开发/fixture.md")
            self.assertIn("[-] 11.  fixture", (tmp / "Plans/功能开发/fixture.md").read_text(encoding="utf-8"))
            self.assertIn("[x] 11. 非功能验证完成", (tmp / "Plans/Epic/fixture.md").read_text(encoding="utf-8"))
            self.assertTrue(by_n[11]["done"])
            self.assertTrue(by_n[11]["skipped"])
            self.assertTrue(by_n[11]["optional"])
            self.assertEqual(by_n[11]["derived_from"], "child-plan")
            self.assertEqual(events[-1]["type"], "wbs_progress")
            self.assertEqual(events[-1]["slice"], 11)
            self.assertEqual(events[-1]["state"], "skipped")
            self.assertEqual(events[-1]["previous_state"], "done")
            self.assertEqual(events[-1]["target_plan"], "Plans/功能开发/fixture.md")
            self.assertEqual((data.get("gate_history") or {}).get("total", 0), 0)
            self.assertEqual(progress["total"], 1)
            self.assertEqual(progress["recent"][0]["slice"], 11)
            self.assertFalse(any(ev.get("epic") == "fixture" for ev in mod.all_gate_events()))

    def test_kanban_sync_script_uses_slice_state_api_for_skip(self) -> None:
        script = (ROOT / "scripts/kanban-sync.sh").read_text(encoding="utf-8")
        self.assertIn("--skip|--skipped", script)
        self.assertIn("--slices-skipped|--slices-skip", script)
        self.assertIn('"state":"%s"', script)
        self.assertNotIn('"done":true', script)
        self.assertNotIn('"done":%s', script)
        subprocess.run(
            ["bash", "-n", "scripts/kanban-sync.sh"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def test_render_epic_board_preserves_skipped_slice_status(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            bp_file = tmp / ".workflows/blueprints/client-dev.json"
            bp = json.loads(bp_file.read_text(encoding="utf-8"))
            for stage in bp["stages"]:
                if stage["key"] == "development":
                    stage["optionalWbsSlices"] = [11]
            bp_file.write_text(json.dumps(bp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            development = tmp / "Plans/功能开发/fixture.md"
            development.write_text(
                development.read_text(encoding="utf-8").replace("[x] 11. fixture", "[-] 11. fixture"),
                encoding="utf-8",
            )
            epic = tmp / "Plans/Epic/fixture.md"
            epic.write_text(
                epic.read_text(encoding="utf-8").replace("[x] 11. 非功能验证完成", "[ ] 11. 非功能验证完成"),
                encoding="utf-8",
            )

            proc = subprocess.run(
                ["python3", "scripts/render-epic-board.py", "Plans/Epic/fixture.md"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        self.assertIn("[-] 11. 非功能验证完成", proc.stdout)

    def test_kanban_exposes_test_coverage_health(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.RUN_DIR = tmp / ".workflows/runs"
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            data = mod.scan_epic(tmp / "Plans/Epic/fixture.md")
            th = data["test_health"]

        self.assertEqual(th["health"], "green")
        self.assertEqual(th["ac_total"], 3)
        self.assertEqual(th["ac_covered"], 3)
        self.assertEqual(th["p0_total"], 2)
        self.assertEqual(th["p0_covered"], 2)
        self.assertEqual(th["case_count"], 3)
        self.assertEqual(th["blockers"], [])

    def test_kanban_test_coverage_flags_missing_p0_tests(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_traceability_fixture(tmp, cover_tests=False, include_dev=True)
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.RUN_DIR = tmp / ".workflows/runs"
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            data = mod.scan_epic(tmp / "Plans/Epic/trace.md")
            th = data["test_health"]

        self.assertEqual(th["health"], "red")
        self.assertIn("AC1", th["missing_p0_tests"])
        self.assertIn("AC1-反", th["missing_p0_tests"])
        self.assertTrue(any("P0 AC 缺测试覆盖" in item for item in th["blockers"]))

    def test_kanban_tests_envelope_groups_workflow_and_task_tests(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.RUN_DIR = tmp / ".workflows/runs"
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            data = mod.tests_envelope()

        suite_groups = {item["group"] for item in data["suites"]}
        suite_levels = {item["level"] for item in data["suites"]}
        object_levels = {
            item["id"]: {level["id"] for level in item["levels"]}
            for item in data["objects"]
        }
        taxonomy_groups = {item["group"] for item in data["taxonomy"]}
        self.assertIn("workflow-engine", suite_groups)
        self.assertIn("skill-fixtures", suite_groups)
        self.assertIn("unit", suite_levels)
        self.assertIn("contract", suite_levels)
        self.assertIn("integration", suite_levels)
        self.assertIn("e2e", suite_levels)
        self.assertIn("regression", suite_levels)
        self.assertIn("unit", object_levels["workflow-engine"])
        self.assertIn("unit", object_levels["workflow-task"])
        self.assertIn("acceptance", object_levels["workflow-task"])
        self.assertIn("workflow-task", taxonomy_groups)
        self.assertEqual(data["kpi"]["task_epic_count"], 1)
        self.assertEqual(data["task_tests"][0]["coverage_pct"], 100)
        self.assertEqual(data["task_tests"][0]["object_type"], "workflow-task")
        self.assertTrue(any(level["id"] == "unit" for level in data["task_tests"][0]["levels"]))
        self.assertTrue(any(level["id"] == "acceptance" and level["runnable"] for level in data["task_tests"][0]["levels"]))
        self.assertEqual(len(data["cases"]), 3)
        self.assertEqual({case["level"] for case in data["cases"]}, {"unit"})

    def test_kanban_can_start_whitelisted_tests_from_board(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.RUN_DIR = tmp / ".workflows/runs"
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            suite = mod.run_test_from_board("suite", "blueprint-schema")
            task = mod.run_test_from_board("task", "Plans/Epic/fixture.md")

        self.assertTrue(suite["ok"], suite["output"])
        self.assertIn("validate-workflow-blueprint.py", suite["command"])
        self.assertTrue(task["ok"], task["output"])
        self.assertIn("traceability-check.py", task["command"])

    def test_merge_code_scenario_suite_is_p0_and_first_in_catalog(self) -> None:
        spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
        self.assertIsNotNone(spec)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        suite = mod.TEST_SUITE_CATALOG[0]
        self.assertEqual(suite["id"], "merge-code-p0-scenarios")
        self.assertEqual(suite["priority"], "P0")
        self.assertEqual(suite["argv"], ["python3", "scripts/test-merge-code-workflow.py"])
        for scenario in ["权限位", "文本冲突", "删除/修改", "重命名", "二进制", "文件/目录", "脏工作树", "无文本业务冲突"]:
            self.assertIn(scenario, suite["scope"])

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
        self.assertIn("OK:workflow-blueprint:.workflows/blueprints/merge-code.json", proc.stdout)
        self.assertIn("OK:workflow-blueprint:.workflows/blueprints/computer-mgmt.json", proc.stdout)

    def test_merge_code_blueprint_requires_business_intent_and_decision_traceability(self) -> None:
        bp = json.loads((ROOT / ".workflows/blueprints/merge-code.json").read_text(encoding="utf-8"))
        stages = {stage["key"]: stage for stage in bp["stages"]}
        self.assertEqual(list(stages), ["preflight", "intent-analysis", "merge", "review"])
        self.assertTrue(stages["intent-analysis"]["exitCriteria"]["mergeAnalysis"])
        self.assertEqual(
            stages["merge"]["exitCriteria"]["mergeDecisionTraceability"],
            "intent-analysis",
        )
        self.assertIn("开发者决策清单", stages["intent-analysis"]["requiredSections"])
        self.assertIn("决策落实记录", stages["merge"]["requiredSections"])

    def test_merge_analysis_validator_blocks_unresolved_decisions_and_missing_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            valid_analysis = tmp / "valid-analysis.md"
            no_conflict_analysis = tmp / "no-conflict-analysis.md"
            unresolved_analysis = tmp / "unresolved-analysis.md"
            valid_implementation = tmp / "valid-implementation.md"
            incomplete_implementation = tmp / "incomplete-implementation.md"
            frontmatter = """
                ---
                status: 已采纳
                p0_open: 0
                ---
            """
            write_file(valid_analysis, frontmatter + "\n" + merge_analysis_sections())
            write_file(
                no_conflict_analysis,
                frontmatter
                + "\n"
                + merge_analysis_sections()
                .replace(
                    "| MC-001 | SI-001, TI-001 | 业务规则 | 自动校验可能绕过人工审核 | 需开发者决策：代码证据不能确定审核优先级 | 是 | D-001 |",
                    "| MC-000 | SI-001, TI-001 | 无冲突 | 两边规则可按顺序同时生效 | 可证明兼容：调用链与测试均保留 | 否 | 无 |",
                )
                .replace(
                    "| D-001 | 自动校验后是否仍需人工审核 | A 保留审核更安全；B 自动放行吞吐更高 | 采用兼容并集，保留人工审核并新增自动校验 | 支付模块开发负责人 | 2026-07-03 合并评审记录 #42 | 已决策 |",
                    "| 无 | 当前未发现需开发者决策项 | 不适用 | 无需决策 | 不适用 | 不适用 | 无需决策 |",
                )
                .replace(
                    "| MC-001 | 自动校验通过后高风险订单仍进入人工审核 | 支付提交与审核队列 | 高风险订单校验通过后仍生成审核任务 | 已规划 |",
                    "| MC-000 | 顺序保留自动校验与人工审核 | 支付提交与审核队列 | 自动校验与人工审核组合回归 | 已规划 |",
                ),
            )
            write_file(unresolved_analysis, frontmatter + "\n" + merge_analysis_sections(resolved=False))
            write_file(valid_implementation, merge_implementation_sections())
            write_file(
                incomplete_implementation,
                merge_implementation_sections().replace(
                    "| D-001 | payment/review.py | 高风险订单始终进入人工审核队列 | test_high_risk_review_queue | 已落实 |\n",
                    "",
                ),
            )

            valid = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/validate-merge-analysis.py"),
                    "--analysis",
                    str(valid_analysis),
                    "--implementation",
                    str(valid_implementation),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            unresolved = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/validate-merge-analysis.py"),
                    "--analysis",
                    str(unresolved_analysis),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            no_conflict = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/validate-merge-analysis.py"),
                    "--analysis",
                    str(no_conflict_analysis),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            incomplete = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/validate-merge-analysis.py"),
                    "--analysis",
                    str(valid_analysis),
                    "--implementation",
                    str(incomplete_implementation),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        self.assertIn("OK:merge-analysis:analysis+implementation", valid.stdout)
        self.assertEqual(no_conflict.returncode, 0, no_conflict.stdout + no_conflict.stderr)
        self.assertNotEqual(unresolved.returncode, 0)
        self.assertIn("BLOCKED:merge-analysis:", unresolved.stdout)
        self.assertNotEqual(incomplete.returncode, 0)
        self.assertIn("D-001", incomplete.stdout)

    def test_kanban_shows_only_created_lightweight_workflows(self) -> None:
        with self.fixture_repo() as tmp:
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.RUN_DIR = tmp / ".workflows/runs"
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            data = mod.board_envelope()
            write_file(
                tmp / "Plans/界面开发/2026-07-03-UI范围-卡片.md",
                f"""
                ---
                status: 进行中
                ---
                # UI范围

                {skill_run("figma-ui", "Plans/界面开发/2026-07-03-UI范围-卡片.md")}
                """,
            )
            data_with_plan = mod.board_envelope()

        lightweight_names = {item["name"] for item in data["lightweight"]}
        self.assertEqual(lightweight_names, set())
        lightweight_names = {item["name"] for item in data_with_plan["lightweight"]}
        self.assertIn("ui-change", lightweight_names)
        self.assertNotIn("bugfix", lightweight_names)

    def test_kanban_reads_hyphenated_learning_plan_keys(self) -> None:
        with self.fixture_repo() as tmp:
            spec = importlib.util.spec_from_file_location("kanban_server", ROOT / "scripts/kanban-server.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            mod.ROOT = tmp
            mod.RUN_DIR = tmp / ".workflows/runs"
            mod.EVENT_DIR = tmp / ".workflows/events"
            mod.BLUEPRINT_DIR = tmp / ".workflows/blueprints"
            mod.CONSTITUTION_FILE = tmp / ".workflows/constitution.json"
            mod.ORPHAN_FEEDBACK = tmp / "Contexts/决策/孤立反馈记录.md"

            write_file(
                tmp / "Plans/Epic/learning.md",
                """
                ---
                workflow: learning-loop
                p0_open: 0
                plans:
                  topic-intake: Plans/学习循环/topic.md
                  material-prepare: Plans/学习循环/material.md
                  study: Plans/学习循环/study.md
                ---

                # Learning Epic

                ## 三、WBS

                ```
                [x] 1. topic
                [x] 2. material
                [ ] 3. study
                ```
                """,
            )
            for rel in ["topic.md", "material.md", "study.md"]:
                write_file(
                    tmp / f"Plans/学习循环/{rel}",
                    """
                    ---
                    status: 进行中
                    ---
                    # learning child
                    """,
                )

            epic = next(item for item in mod.board_payload() if item["file"] == "Plans/Epic/learning.md")

        plan_by_stage = {item["stage_key"]: item["path"] for item in epic["plans"]}
        self.assertEqual(plan_by_stage["topic-intake"], "Plans/学习循环/topic.md")
        self.assertEqual(plan_by_stage["material-prepare"], "Plans/学习循环/material.md")
        slice_by_n = {item["n"]: item for item in epic["slices"]}
        self.assertEqual(slice_by_n[1]["related_plan"], "Plans/学习循环/topic.md")
        self.assertEqual(slice_by_n[2]["related_plan"], "Plans/学习循环/material.md")

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
            "全流程闭环做一下搜索页": "client-dev",
            "从0到1做个客户端功能": "client-dev",
            "新需求：客户端弹窗改版": "client-dev",
            "开发功能：批量导出": "client-dev",
            "做一个会员积分功能": "client-dev",
            "客户端项目：会员权益页": "client-dev",
            "走完整流程做搜索筛选": "client-dev",
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
            "电脑太卡了帮我处理一下": "computer-mgmt",
            "清一下电脑缓存": "computer-mgmt",
            "空间不足，先盘点一下": "computer-mgmt",
            "workflow=computer-mgmt 帮我跑一下": "computer-mgmt",
            "工作流:computer-mgmt 帮我清理": "computer-mgmt",
            "/workflow computer-mgmt 先盘点": "computer-mgmt",
            "workflow=client-dev 启动这个项目": "client-dev",
            "工作流：client-dev 做订单模块": "client-dev",
            "帮我改一下 UI": "ui-change",
            "Figma还原这个卡片": "ui-change",
            "做界面，对一下 Figma 稿": "ui-change",
            "页面视觉不对齐，走轻流程": "ui-change",
            "样式问题和间距对齐检查一下": "ui-change",
            "线上报错帮我修bug": "bugfix",
            "这个崩溃走 bugfix": "bugfix",
            "修一下这个 bug": "bugfix",
            "按钮点不动，帮我排查": "bugfix",
            "这个异常不生效": "bugfix",
            "这个技术方案只拆任务": "task-split-only",
            "帮我把方案拆成开发任务": "task-split-only",
            "这个功能拆成几步做": "task-split-only",
            "WBS修订一下": "task-split-only",
            "帮我合代码": "merge-code",
            "把 feature/search 分支合进 main": "merge-code",
            "合一下分支": "merge-code",
            "merge 分支到 release": "merge-code",
            "解决合并冲突": "merge-code",
            "workflow=merge-code 合并 feature/pay": "merge-code",
            "我要学习 agent 开发": "learning-loop",
            "开始学习智能体开发": "learning-loop",
            "帮我准备资料学习 MCP": "learning-loop",
            "学完之后开始实践": "learning-loop",
            "实践完了帮我验证复盘": "learning-loop",
            "总结知识图谱": "learning-loop",
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
            "生成技术方案模板",
            "写测试计划",
            "实现这个函数",
            "帮我写个脚本",
            "开发环境启动失败，帮我看看",
            "备份这份文档",
            "整理需求列表",
            "清理一下这篇文档",
            "帮我做代码 review",
            "部署检查清单生成一下",
            "复盘一下这个项目",
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

    def test_lightweight_workflow_gates_reach_done_with_prefixed_plans(self) -> None:
        cases = [
            (
                "ui-change",
                [
                    ("Plans/界面开发/2026-07-03-UI范围-卡片.md", "figma-ui"),
                    ("Plans/界面开发/2026-07-03-UI实现-卡片.md", "figma-ui"),
                    ("Plans/界面开发/2026-07-03-UI复核-卡片.md", "review-assistant"),
                ],
            ),
            (
                "bugfix",
                [
                    ("Plans/Bug排查/2026-07-03-复现-价格错误.md", "feature-dev-assistant"),
                    ("Plans/Bug排查/2026-07-03-定位-价格错误.md", "feature-dev-assistant"),
                    ("Plans/Bug排查/2026-07-03-修复-价格错误.md", "feature-dev-assistant"),
                    ("Plans/Bug排查/2026-07-03-回归-价格错误.md", "review-assistant"),
                ],
            ),
            (
                "task-split-only",
                [
                    ("Plans/功能开发/2026-07-03-任务拆分-优惠券.md", "task-splitter"),
                    ("Plans/功能开发/2026-07-03-任务拆分复核-优惠券.md", "task-splitter"),
                ],
            ),
            (
                "merge-code",
                [
                    ("Plans/代码重构/2026-07-03-合并预检-功能分支.md", "merge-code-assistant"),
                    ("Plans/代码重构/2026-07-03-合并意图分析-功能分支.md", "merge-code-assistant"),
                    ("Plans/代码重构/2026-07-03-代码合并-功能分支.md", "merge-code-assistant"),
                    ("Plans/代码重构/2026-07-03-合并复核-功能分支.md", "code-review"),
                ],
            ),
        ]
        with self.fixture_repo() as tmp:
            for workflow, _plans in cases:
                with self.subTest(workflow=workflow, state="empty"):
                    blocked = self.run_gate(tmp, "--workflow", workflow, "--json")
                    self.assertNotEqual(blocked["current_state"], "done")
                    self.assertTrue(blocked["blockers"])

            for workflow, plans in cases:
                for rel, skill in plans:
                    # verdictPass=required 阶段（ui-change 的 UI 实现）须带经复核的通过裁决，
                    # 模拟 figma-ui 报完成前落盘 verdict json，否则门禁阻塞在该阶段。
                    verdict_fm = ""
                    if "UI实现" in rel:
                        verdict_rel = rel.replace(".md", ".verdict.json")
                        write_file(
                            tmp / verdict_rel,
                            json.dumps(
                                {"pass": True, "reviewed": True, "score": 9.5,
                                 "summary": "fixture", "deviations": []},
                                ensure_ascii=False,
                            ),
                        )
                        verdict_fm = f"verdict: {verdict_rel}\n"
                    merge_fm = ""
                    merge_body = ""
                    if "合并意图分析" in rel:
                        merge_fm = "p0_open: 0\n"
                        merge_body = merge_analysis_sections()
                    elif "代码合并" in rel:
                        merge_body = merge_implementation_sections()
                    write_file(
                        tmp / rel,
                        f"""
                        ---
                        status: 已采纳
                        {verdict_fm}{merge_fm}---

                        # {rel}

                        轻流程 fixture。

                        {merge_body}

                        {skill_run(skill, rel)}
                        """,
                    )
                with self.subTest(workflow=workflow, state="done"):
                    data = self.run_gate(tmp, "--workflow", workflow, "--json")
                    self.assertEqual(data["current_state"], "done", data)
                    self.assertEqual(data["blockers"], [])
                    self.assertTrue(data["plans_found"], data)

    def test_merge_code_gate_stops_before_merge_when_developer_decision_is_unresolved(self) -> None:
        with self.fixture_repo() as tmp:
            preflight_rel = "Plans/代码重构/2026-07-03-合并预检-功能分支.md"
            analysis_rel = "Plans/代码重构/2026-07-03-合并意图分析-功能分支.md"
            write_file(
                tmp / preflight_rel,
                f"""
                ---
                status: 已采纳
                ---

                # 合并预检

                已确认源分支、目标分支和 merge-base。

                {skill_run("merge-code-assistant", preflight_rel)}
                """,
            )
            write_file(
                tmp / analysis_rel,
                f"""
                ---
                status: 已采纳
                p0_open: 0
                ---

                # 合并意图分析

                {merge_analysis_sections(resolved=False)}

                {skill_run("merge-code-assistant", analysis_rel)}
                """,
            )

            data = self.run_gate(tmp, "--workflow", "merge-code", "--json")

        self.assertEqual(data["current_state"], "intent-analysis", data)
        self.assertTrue(any("mergeAnalysis" in item and "D-001" in item for item in data["blockers"]), data)

    def test_workflow_smoke_script_covers_core_workflows(self) -> None:
        proc = subprocess.run(
            [
                "python3",
                "scripts/workflow-smoke-test.py",
                "merge-code",
                "ui-change",
                "bugfix",
                "task-split-only",
                "learning-loop",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("OK:workflow-smoke-test:merge-code", proc.stdout)
        self.assertIn("OK:workflow-smoke-test:ui-change", proc.stdout)
        self.assertIn("OK:workflow-smoke-test:bugfix", proc.stdout)
        self.assertIn("OK:workflow-smoke-test:task-split-only", proc.stdout)
        self.assertIn("OK:workflow-smoke-test:learning-loop", proc.stdout)

    def test_merge_code_real_git_scenario_suite_passes(self) -> None:
        proc = subprocess.run(
            ["python3", "scripts/test-merge-code-workflow.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("OK:merge-code-workflow-scenarios:16", proc.stdout)

    def test_workflow_smoke_script_can_start_from_utterance(self) -> None:
        proc = subprocess.run(
            ["python3", "scripts/workflow-smoke-test.py", "--utterance", "全流程开发一下支付收银台"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("OK:workflow-smoke-test:client-dev", proc.stdout)

    def test_skill_smoke_all_fixtures_valid_and_product_skills_covered(self) -> None:
        proc = subprocess.run(
            ["python3", "scripts/skill-smoke-all.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        combined = proc.stdout + proc.stderr
        # 所有 fixture 结构必须合法（退出码 0）。
        self.assertEqual(proc.returncode, 0, combined)
        self.assertIn("fixture 结构合法", proc.stdout)
        # 产物类 Skill 全覆盖：不允许出现「尚缺 fixture」缺口。
        # 新增产物类 Skill 时必须同时补 fixture，否则此断言把缺口挡在回归里。
        self.assertNotIn("尚缺 fixture", proc.stdout, combined)
        # 覆盖关键 Skill，防 fixture 目录被误删后静默漏测。
        for skill in ("requirement-analyst", "architecture-design-assistant", "test-generator"):
            self.assertIn(f"OK:skill-smoke-test:{skill}", proc.stdout, combined)

    def test_workflow_plan_init_creates_lightweight_stage_plan(self) -> None:
        with self.fixture_repo() as tmp:
            proc = subprocess.run(
                [
                    "python3",
                    "scripts/workflow-plan-init.py",
                    "--workflow",
                    "ui-change",
                    "--title",
                    "卡片",
                    "--date",
                    "2026-07-03",
                ],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            rel = "Plans/界面开发/2026-07-03-UI范围-卡片.md"
            self.assertIn(f"created: {rel}", proc.stdout)
            plan = tmp / rel
            self.assertTrue(plan.exists())
            text = plan.read_text(encoding="utf-8")
            self.assertIn("workflow: ui-change", text)
            self.assertIn("workflow_stage: ui-scope", text)
            self.assertIn("skill: figma-ui", text)

            gate = self.run_gate(tmp, "--workflow", "ui-change", "--json")
            self.assertEqual(gate["current_state"], "ui-scope")
            self.assertTrue(any("skill_run" in item for item in gate["blockers"]), gate)

    def test_workflow_plan_init_all_with_feedback_can_reach_done(self) -> None:
        with self.fixture_repo() as tmp:
            subprocess.run(
                [
                    "python3",
                    "scripts/workflow-plan-init.py",
                    "--workflow",
                    "task-split-only",
                    "--title",
                    "优惠券",
                    "--date",
                    "2026-07-03",
                    "--all",
                    "--include-feedback",
                ],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            gate = self.run_gate(tmp, "--workflow", "task-split-only", "--json")
            self.assertEqual(gate["current_state"], "done", gate)

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

    def test_workflow_gate_accepts_skipped_optional_wbs_slice(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            bp_file = tmp / ".workflows/blueprints/client-dev.json"
            bp = json.loads(bp_file.read_text(encoding="utf-8"))
            for stage in bp["stages"]:
                if stage["key"] == "development":
                    stage["optionalWbsSlices"] = [11]
            bp_file.write_text(json.dumps(bp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            development = tmp / "Plans/功能开发/fixture.md"
            development.write_text(
                development.read_text(encoding="utf-8").replace("[x] 11. fixture", "[-] 11. fixture"),
                encoding="utf-8",
            )

            data = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md", "--json")
        self.assertEqual(data["current_state"], "done", data)
        self.assertEqual(data["blockers"], [])

    def test_workflow_gate_blocks_skipped_required_wbs_slice(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            development = tmp / "Plans/功能开发/fixture.md"
            development.write_text(
                development.read_text(encoding="utf-8").replace("[x] 11. fixture", "[-] 11. fixture"),
                encoding="utf-8",
            )

            data = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md", "--json")
        self.assertEqual(data["current_state"], "development", data)
        self.assertTrue(any("缺: 11" in blocker for blocker in data["blockers"]), data["blockers"])

    def test_workflow_gate_aggregates_optional_wbs_sub_slices(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            bp_file = tmp / ".workflows/blueprints/client-dev.json"
            bp = json.loads(bp_file.read_text(encoding="utf-8"))
            for stage in bp["stages"]:
                if stage["key"] == "development":
                    stage["optionalWbsSlices"] = [7]
            bp_file.write_text(json.dumps(bp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            development = tmp / "Plans/功能开发/fixture.md"
            development.write_text(
                development.read_text(encoding="utf-8").replace(
                    "[x] 7. fixture",
                    "[x] 7a. mock fixture\n[-] 7b. backend integration skipped",
                ),
                encoding="utf-8",
            )

            data = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md", "--json")
        self.assertEqual(data["current_state"], "done", data)

    def test_workflow_gate_blocks_required_wbs_sub_slice_skip(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            development = tmp / "Plans/功能开发/fixture.md"
            development.write_text(
                development.read_text(encoding="utf-8").replace(
                    "[x] 7. fixture",
                    "[x] 7a. mock fixture\n[-] 7b. backend integration skipped",
                ),
                encoding="utf-8",
            )

            data = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md", "--json")
        self.assertEqual(data["current_state"], "development", data)
        self.assertTrue(any("缺: 7" in blocker for blocker in data["blockers"]), data["blockers"])

    def test_workflow_run_gate_records_pass_event_and_check_trail(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            proc = subprocess.run(
                ["python3", "scripts/workflow-run.py", "start",
                 "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md"],
                cwd=tmp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
            )
            run_rel = proc.stdout.strip()
            run_file = tmp / run_rel
            subprocess.run(
                ["python3", "scripts/workflow-run.py", "gate", "--run", run_rel],
                cwd=tmp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
            )
            run_text = run_file.read_text(encoding="utf-8")
            self.assertIn("gate_checks:", run_text)
            self.assertIn('result: "pass"', run_text)
            event_rel = run_text.split('events: "')[1].split('"')[0]
            events = [json.loads(l) for l in (tmp / event_rel).read_text(encoding="utf-8").splitlines() if l.strip()]
            types = [e["type"] for e in events]
            self.assertIn("gate_pass", types)
            self.assertNotIn("gate_fail", types)

    def test_workflow_gate_records_pass_when_previous_blocker_is_resolved(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            req = tmp / "Plans/需求分析/fixture.md"
            req.write_text(req.read_text(encoding="utf-8").replace("status: 已采纳", "status: 评审中"), encoding="utf-8")

            first = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md", "--json")
            self.assertEqual(first["current_state"], "requirement")

            req.write_text(req.read_text(encoding="utf-8").replace("status: 评审中", "status: 已采纳"), encoding="utf-8")
            (tmp / "Plans/自动化测试/fixture.md").unlink()
            second = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md", "--json")
            self.assertEqual(second["current_state"], "test-first")

            event_file = tmp / ".workflows/events/fixture.events.jsonl"
            events = [json.loads(l) for l in event_file.read_text(encoding="utf-8").splitlines() if l.strip()]
            stage_types = [(e["stage"], e["type"]) for e in events if e["type"] in {"gate_pass", "gate_fail"}]

        self.assertEqual(stage_types[-4:], [
            ("requirement", "gate_fail"),
            ("requirement", "gate_pass"),
            ("architecture", "gate_pass"),
            ("test-first", "gate_fail"),
        ])
        self.assertIn("历史阻塞已解除", events[-3]["reason"])

    def test_workflow_gate_json_output_handles_multiline_gate_result(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            data = self.run_gate(tmp, "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md", "--json")
        self.assertIsInstance(data["gate_development"], str)
        self.assertIn("OK:skill_run", data["gate_development"])
        self.assertIn("\n", data["gate_development"])

    def test_plan_gate_requires_skill_run_for_all_plan_categories(self) -> None:
        with self.fixture_repo() as tmp:
            plan = tmp / "Plans/技术方案/no-feedback.md"
            write_file(
                plan,
                """
                ---
                status: 已采纳
                ---

                # 技术方案 no feedback
                """,
            )
            missing = subprocess.run(
                ["bash", "scripts/plan-gate-check.sh", "Plans/技术方案/no-feedback.md"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("skill_run", missing.stderr + missing.stdout)

            write_file(
                plan,
                plan.read_text(encoding="utf-8")
                + "\n"
                + skill_run("architecture-design-assistant", "Plans/技术方案/no-feedback.md"),
            )
            ok = subprocess.run(
                ["bash", "scripts/plan-gate-check.sh", "Plans/技术方案/no-feedback.md"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(ok.returncode, 0, ok.stderr + ok.stdout)

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
                [-] 4. skipped
                [x] 7a. mock
                [-] 7b. backend integration skipped
                [ ] 8a. open
                [x] 8b. done
                [~] 9a. doing
                [x] 9b. done
                ```

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
            self.assertEqual(mod.wbs_slice_status(plan, 4), "-")
            self.assertEqual(mod.wbs_slice_status(plan, 7), "-")
            self.assertEqual(mod.wbs_slice_status(plan, 8), " ")
            self.assertEqual(mod.wbs_slice_status(plan, 9), "~")
            # WBS 状态只认 fenced checklist；表格行（5）不再被识别，避免多表/同号歧义。
            self.assertIsNone(mod.wbs_slice_status(plan, 5))
            self.assertIsNone(mod.wbs_slice_status(plan, 6))

    def test_gate_parse_section_check_strips_skipped_checkboxes(self) -> None:
        with self.fixture_repo() as tmp:
            empty = tmp / "Plans/需求分析/empty.md"
            write_file(
                empty,
                """
                # Section fixture

                ## 验收标准

                - [-] 【】
                """,
            )
            filled = tmp / "Plans/需求分析/filled.md"
            write_file(
                filled,
                """
                # Section fixture

                ## 验收标准

                - [-] 本需求无空态，已由产品确认不适用
                """,
            )
            spec = importlib.util.spec_from_file_location("gate_parse", ROOT / "scripts/gate_parse.py")
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)

            self.assertEqual(mod.check_sections(empty, ["验收标准"])["empty"], ["验收标准"])
            self.assertEqual(mod.check_sections(filled, ["验收标准"])["empty"], [])

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

    def test_workflow_status_replays_gate_history_from_events(self) -> None:
        with self.fixture_repo() as tmp:
            self.create_complete_client_dev_fixture(tmp)
            proc = subprocess.run(
                ["python3", "scripts/workflow-run.py", "start",
                 "--workflow", "client-dev", "--epic", "Plans/Epic/fixture.md"],
                cwd=tmp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
            )
            run_rel = proc.stdout.strip()
            subprocess.run(
                ["python3", "scripts/workflow-run.py", "gate", "--run", run_rel],
                cwd=tmp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
            )
            run_text = (tmp / run_rel).read_text(encoding="utf-8")
            event_rel = run_text.split('events: "')[1].split('"')[0]
            event_file = tmp / event_rel
            before_events = event_file.read_text(encoding="utf-8")
            proc = subprocess.run(
                ["python3", "scripts/workflow-status.py", "--workflow", "client-dev",
                 "--epic", "Plans/Epic/fixture.md", "--run", run_rel, "--json"],
                cwd=tmp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
            )
            after_events = event_file.read_text(encoding="utf-8")
            direct_event_file = tmp / ".workflows/events/fixture.events.jsonl"
            data = json.loads(proc.stdout)
        self.assertIn("history", data)
        self.assertIsNotNone(data["history"]["last_gate"])
        self.assertEqual(data["history"]["last_gate"]["result"], "pass")
        self.assertEqual(after_events, before_events)
        self.assertFalse(direct_event_file.exists())

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
                    "Plans/界面开发",
                    "Plans/学习循环",
                    "Plans/Bug排查",
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

        ## 七、边界情况清单

        - 空仓库无任何子 Plan：门禁应阻塞在首阶段并给出建链提示。
        - 指定不存在的 Epic 项目：应触发 bootstrap 流程。

        ## 八、异常流程矩阵

        | 异常 | 触发条件 | 预期处理 |
        |------|----------|----------|
        | 子 Plan 缺 skill_run | 阶段收尾未追加反馈块 | 门禁阻塞并提示补 skill_run |
        | WBS 切片未全勾 | 存在未完成切片 | 阻塞并列出缺失切片 |

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
            (
                "Plans/技术方案/fixture.md",
                "architecture-design-assistant",
                [3],
                "已采纳",
                """
                ## 二、模块边界

                - Gate 引擎：读蓝图 + 扫子 Plan，产出阶段判定。
                - Traceability：需求 AC → 测试/开发覆盖闭环。

                ## 三、数据模型

                | 实体 | 字段 | 说明 |
                |------|------|------|
                | Epic | plans, p0_open | 被动数据聚合根 |
                | Stage | key, exitCriteria | 蓝图阶段定义 |

                ## 四、API Schema

                - `workflow-gate.sh --workflow <name> --json` → `{current_state, blockers, plans_found}`
                """,
            ),
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

        {wbs_table([5, 6, 7, 8, 9, 10, 11])}

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

        ## 七、边界情况清单

        - 测试未覆盖 P0 反例 AC：门禁应在 test-first 阶段阻塞。
        - 开发任务未覆盖 P0 AC：门禁应在 development 阶段阻塞。

        ## 八、异常流程矩阵

        | 异常 | 触发条件 | 预期处理 |
        |------|----------|----------|
        | 用例映射缺 AC1-反 | 测试 plan 漏反例 | testTraceability 阻塞 |

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
