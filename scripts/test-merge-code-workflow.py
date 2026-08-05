#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(
    args: list[str],
    *,
    cwd: Path,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise AssertionError(
            f"command failed ({proc.returncode}): {' '.join(args)}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], cwd=repo, check=check)


def write_text(repo: Path, rel: str, content: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_bytes(repo: Path, rel: str, content: bytes) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def commit_all(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)


def unresolved_analysis_plan() -> str:
    return textwrap.dedent(
        """
        ---
        status: 已采纳
        p0_open: 0
        ---

        # 双边代码意图与业务冲突分析

        ## 双边代码意图

        | 意图ID | 分支侧 | 文件/模块 | 代码变化 | 业务目标 | 行为/规则变化 | 证据 | 置信度 |
        |--------|--------|-----------|----------|----------|---------------|------|--------|
        | SI-001 | 源分支 | checkout.py | 放宽结算折扣到 50% | 提升促销转化 | 结算允许 50% 折扣 | source commit；checkout.py | 高 |
        | TI-001 | 目标分支 | pricing.py | 收紧最大折扣到 30% | 控制毛利风险 | 全局折扣不得超过 30% | target commit；pricing.py | 高 |

        ## 业务冲突矩阵

        | 冲突ID | 关联意图 | 冲突类型 | 业务影响 | AI结论 | 需开发者决策 | 决策ID |
        |--------|----------|----------|----------|--------|----------------|--------|
        | MC-001 | SI-001, TI-001 | 业务规则 | Git 可自动合并，但最终允许折扣范围不确定 | 需开发者决策：代码证据不能确定促销与毛利规则优先级 | 是 | D-001 |

        ## 开发者决策清单

        | 决策ID | 待决策问题 | 可选方案及影响 | 开发者结论 | 决策人 | 确认记录 | 状态 |
        |--------|------------|----------------|------------|--------|----------|------|
        | D-001 | 最终最大折扣应为 30% 还是 50% | 30% 控制风险；50% 提升转化 | 待确认 | 待确认 | 待确认 | 待决策 |

        ## 合并策略与验证映射

        | 冲突ID | 处理策略 | 影响范围 | 验证场景 | 状态 |
        |--------|----------|----------|----------|------|
        | MC-001 | 根据 D-001 统一折扣上限 | 定价与结算 | 结算折扣与全局上限保持一致 | 已规划 |
        """
    ).strip() + "\n"


def resolved_analysis_plan() -> str:
    return (
        unresolved_analysis_plan()
        .replace("| 待确认 | 待确认 | 待确认 | 待决策 |", "| 统一按 30% 上限执行 | 结算模块开发负责人 | 评审记录 #42 | 已决策 |")
    )


def implementation_plan(*, include_decision: bool = True) -> str:
    decision_row = (
        "| D-001 | checkout.py | 结算层复用 pricing.MAX_DISCOUNT | test_checkout_uses_pricing_limit | 已落实 |\n"
        if include_decision
        else ""
    )
    return textwrap.dedent(
        f"""
        # 代码合并与冲突处理

        ## 决策落实记录

        | 追踪ID | 影响文件 | 落实方式 | 验证用例 | 状态 |
        |--------|----------|----------|----------|------|
        | MC-001 | pricing.py | 保留 30% 全局上限 | test_max_discount | 已落实 |
        {decision_row}
        ## 验证记录

        | 命令/检查 | 覆盖意图/冲突 | 结果 | 备注 |
        |-----------|---------------|------|------|
        | pytest | SI-001, TI-001, MC-001, D-001 | pass | 组合规则通过 |

        ## 合并结果

        - 合并后 SHA：abc123
        - 两边意图与开发者决策均已落实
        """
    ).strip() + "\n"


def skill_run(skill: str, plan: str) -> str:
    return textwrap.dedent(
        f"""
        ## 反馈（skill_run）

        ```yaml
        skill_run:
          skill: {skill}
          plan: {plan}
          date: 2026-07-28
          contexts_used:
            - path: Contexts/决策/Skill反馈协议.md
              utility: high
              reason: 验证 merge-code P0 场景门禁。
          contexts_missing: []
          contexts_stale: []
        ```
        """
    ).strip() + "\n"


class MergeCodeWorkflowScenarioTests(unittest.TestCase):
    """P0：用真实 Git 仓库覆盖 merge-code 的主要文件合并形态。"""

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="aiwk-merge-code-scenario-")
        self.tmp = Path(self._temp.name)

    def tearDown(self) -> None:
        self._temp.cleanup()

    def new_repo(self, files: dict[str, str | bytes]) -> Path:
        repo = self.tmp / "repo"
        repo.mkdir()
        git(repo, "init", "-b", "target")
        git(repo, "config", "user.email", "merge-code-test@example.com")
        git(repo, "config", "user.name", "Merge Code Test")
        for rel, content in files.items():
            if isinstance(content, bytes):
                write_bytes(repo, rel, content)
            else:
                write_text(repo, rel, content)
        commit_all(repo, "base")
        git(repo, "branch", "source")
        return repo

    def diverge(
        self,
        repo: Path,
        *,
        target_change,
        source_change,
    ) -> None:
        target_change(repo)
        commit_all(repo, "target change")
        git(repo, "checkout", "source")
        source_change(repo)
        commit_all(repo, "source change")
        git(repo, "checkout", "target")

    def merge_source(self, repo: Path) -> subprocess.CompletedProcess[str]:
        return git(repo, "merge", "--no-edit", "source", check=False)

    def unmerged_files(self, repo: Path) -> set[str]:
        output = git(repo, "diff", "--name-only", "--diff-filter=U").stdout
        return {line.strip() for line in output.splitlines() if line.strip()}

    def validate(
        self,
        analysis: str,
        implementation: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        analysis_path = self.tmp / "analysis.md"
        analysis_path.write_text(analysis, encoding="utf-8")
        args = [
            "python3",
            str(ROOT / "scripts/validate-merge-analysis.py"),
            "--analysis",
            str(analysis_path),
        ]
        if implementation is not None:
            implementation_path = self.tmp / "implementation.md"
            implementation_path.write_text(implementation, encoding="utf-8")
            args.extend(["--implementation", str(implementation_path)])
        return run(args, cwd=ROOT, check=False)

    def workflow_gate_for_analysis(self, analysis: str) -> dict:
        runtime = self.tmp / "workflow-runtime"
        shutil.copytree(ROOT / "scripts", runtime / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / ".workflows", runtime / ".workflows")
        (runtime / "Plans/代码重构").mkdir(parents=True)
        (runtime / "Contexts/决策").mkdir(parents=True)
        (runtime / "Contexts/决策/Skill反馈协议.md").write_text("# Skill反馈协议\n", encoding="utf-8")
        preflight_rel = "Plans/代码重构/2026-07-28-合并预检-语义冲突.md"
        analysis_rel = "Plans/代码重构/2026-07-28-合并意图分析-语义冲突.md"
        (runtime / preflight_rel).write_text(
            "# 合并预检\n\n源、目标分支与 merge-base 已确认。\n\n"
            + skill_run("merge-code-assistant", preflight_rel),
            encoding="utf-8",
        )
        (runtime / analysis_rel).write_text(
            analysis + "\n" + skill_run("merge-code-assistant", analysis_rel),
            encoding="utf-8",
        )
        gate = run(
            ["bash", "scripts/workflow-gate.sh", "--workflow", "merge-code", "--json"],
            cwd=runtime,
        )
        return json.loads(gate.stdout)

    def test_00_blueprint_and_isolated_workflow_smoke(self) -> None:
        blueprint = json.loads((ROOT / ".workflows/blueprints/merge-code.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [stage["key"] for stage in blueprint["stages"]],
            ["preflight", "intent-analysis", "merge", "review"],
        )
        self.assertTrue(blueprint["stages"][1]["exitCriteria"]["mergeAnalysis"])
        self.assertEqual(
            blueprint["stages"][2]["exitCriteria"]["mergeDecisionTraceability"],
            "intent-analysis",
        )
        self.assertEqual(blueprint["enablement"]["preflight"], "python3 scripts/workflow-install.py check --workflow merge-code")
        for capability in ["core-tools", "skills", "tool-entrypoints", "global-instructions", "pre-commit-hook", "kanban-board"]:
            self.assertIn(capability, blueprint["enablement"]["requires"])
        smoke = run(["python3", "scripts/workflow-smoke-test.py", "merge-code"], cwd=ROOT)
        self.assertIn("OK:workflow-smoke-test:merge-code", smoke.stdout)

    def test_10_fast_forward_add_file(self) -> None:
        repo = self.new_repo({"README.md": "base\n"})
        git(repo, "checkout", "source")
        write_text(repo, "feature.txt", "source feature\n")
        commit_all(repo, "source feature")
        git(repo, "checkout", "target")

        merged = git(repo, "merge", "--ff-only", "source", check=False)

        self.assertEqual(merged.returncode, 0, merged.stderr)
        self.assertEqual((repo / "feature.txt").read_text(encoding="utf-8"), "source feature\n")
        self.assertEqual(self.unmerged_files(repo), set())

    def test_11_already_merged_is_idempotent(self) -> None:
        repo = self.new_repo({"README.md": "base\n"})
        git(repo, "checkout", "source")
        write_text(repo, "feature.txt", "source feature\n")
        commit_all(repo, "source feature")
        git(repo, "checkout", "target")
        git(repo, "merge", "--no-edit", "source")

        second_merge = self.merge_source(repo)

        self.assertEqual(second_merge.returncode, 0, second_merge.stderr)
        self.assertIn("Already up to date", second_merge.stdout)

    def test_20_non_overlapping_files_auto_merge(self) -> None:
        repo = self.new_repo({"target.txt": "base target\n", "source.txt": "base source\n"})
        self.diverge(
            repo,
            target_change=lambda root: write_text(root, "target.txt", "target branch\n"),
            source_change=lambda root: write_text(root, "source.txt", "source branch\n"),
        )

        merged = self.merge_source(repo)

        self.assertEqual(merged.returncode, 0, merged.stderr)
        self.assertEqual((repo / "target.txt").read_text(encoding="utf-8"), "target branch\n")
        self.assertEqual((repo / "source.txt").read_text(encoding="utf-8"), "source branch\n")

    def test_21_same_file_different_hunks_auto_merge(self) -> None:
        base = "".join(f"line {index:02d}\n" for index in range(1, 31))
        repo = self.new_repo({"policy.txt": base})

        def target_change(root: Path) -> None:
            write_text(root, "policy.txt", base.replace("line 02", "target rule"))

        def source_change(root: Path) -> None:
            write_text(root, "policy.txt", base.replace("line 29", "source rule"))

        self.diverge(repo, target_change=target_change, source_change=source_change)
        merged = self.merge_source(repo)

        self.assertEqual(merged.returncode, 0, merged.stderr)
        result = (repo / "policy.txt").read_text(encoding="utf-8")
        self.assertIn("target rule", result)
        self.assertIn("source rule", result)

    def test_22_executable_mode_and_content_auto_merge(self) -> None:
        repo = self.new_repo({"deploy.sh": "#!/bin/sh\necho base\n"})

        def source_mode_change(root: Path) -> None:
            (root / "deploy.sh").chmod(0o755)

        self.diverge(
            repo,
            target_change=lambda root: write_text(root, "deploy.sh", "#!/bin/sh\necho target\n"),
            source_change=source_mode_change,
        )
        merged = self.merge_source(repo)

        self.assertEqual(merged.returncode, 0, merged.stderr)
        self.assertEqual((repo / "deploy.sh").read_text(encoding="utf-8"), "#!/bin/sh\necho target\n")
        self.assertTrue((repo / "deploy.sh").stat().st_mode & 0o111)

    def test_30_same_line_text_conflict(self) -> None:
        repo = self.new_repo({"policy.txt": "discount=10\n"})
        self.diverge(
            repo,
            target_change=lambda root: write_text(root, "policy.txt", "discount=30\n"),
            source_change=lambda root: write_text(root, "policy.txt", "discount=50\n"),
        )

        merged = self.merge_source(repo)

        self.assertNotEqual(merged.returncode, 0)
        self.assertEqual(self.unmerged_files(repo), {"policy.txt"})
        content = (repo / "policy.txt").read_text(encoding="utf-8")
        self.assertIn("<<<<<<< HEAD", content)
        self.assertIn(">>>>>>> source", content)

    def test_31_modify_delete_conflict(self) -> None:
        repo = self.new_repo({"legacy-policy.txt": "legacy=true\n"})

        def source_delete(root: Path) -> None:
            git(root, "rm", "legacy-policy.txt")

        self.diverge(
            repo,
            target_change=lambda root: write_text(root, "legacy-policy.txt", "legacy=false\n"),
            source_change=source_delete,
        )
        merged = self.merge_source(repo)

        self.assertNotEqual(merged.returncode, 0)
        self.assertEqual(self.unmerged_files(repo), {"legacy-policy.txt"})
        self.assertIn("modify/delete", merged.stdout + merged.stderr)

    def test_32_rename_modify_keeps_both_intents(self) -> None:
        repo = self.new_repo({"policy.txt": "name=discount\nlimit=10\n"})

        def source_rename(root: Path) -> None:
            git(root, "mv", "policy.txt", "discount-policy.txt")

        self.diverge(
            repo,
            target_change=lambda root: write_text(root, "policy.txt", "name=discount\nlimit=30\n"),
            source_change=source_rename,
        )
        merged = self.merge_source(repo)

        self.assertEqual(merged.returncode, 0, merged.stderr)
        self.assertFalse((repo / "policy.txt").exists())
        self.assertEqual(
            (repo / "discount-policy.txt").read_text(encoding="utf-8"),
            "name=discount\nlimit=30\n",
        )

    def test_33_binary_conflict(self) -> None:
        repo = self.new_repo({"asset.bin": b"\x00base\x01"})
        self.diverge(
            repo,
            target_change=lambda root: write_bytes(root, "asset.bin", b"\x00target\x01"),
            source_change=lambda root: write_bytes(root, "asset.bin", b"\x00source\x01"),
        )

        merged = self.merge_source(repo)

        self.assertNotEqual(merged.returncode, 0)
        self.assertEqual(self.unmerged_files(repo), {"asset.bin"})
        self.assertIn("binary", (merged.stdout + merged.stderr).lower())

    def test_34_add_add_same_path_conflict(self) -> None:
        repo = self.new_repo({"README.md": "base\n"})
        self.diverge(
            repo,
            target_change=lambda root: write_text(root, "new-policy.txt", "target policy\n"),
            source_change=lambda root: write_text(root, "new-policy.txt", "source policy\n"),
        )
        merged = self.merge_source(repo)

        self.assertNotEqual(merged.returncode, 0)
        self.assertEqual(self.unmerged_files(repo), {"new-policy.txt"})
        self.assertIn("add/add", merged.stdout + merged.stderr)

    def test_35_rename_rename_conflict(self) -> None:
        repo = self.new_repo({"policy.txt": "discount=10\n"})

        def target_rename(root: Path) -> None:
            git(root, "mv", "policy.txt", "target-policy.txt")

        def source_rename(root: Path) -> None:
            git(root, "mv", "policy.txt", "source-policy.txt")

        self.diverge(repo, target_change=target_rename, source_change=source_rename)
        merged = self.merge_source(repo)

        self.assertNotEqual(merged.returncode, 0)
        self.assertIn("rename/rename", merged.stdout + merged.stderr)
        self.assertTrue(self.unmerged_files(repo))

    def test_36_file_directory_conflict(self) -> None:
        repo = self.new_repo({"README.md": "base\n"})
        self.diverge(
            repo,
            target_change=lambda root: write_text(root, "config", "target config file\n"),
            source_change=lambda root: write_text(root, "config/rules.txt", "source config directory\n"),
        )
        merged = self.merge_source(repo)

        self.assertNotEqual(merged.returncode, 0)
        self.assertIn("file/directory", (merged.stdout + merged.stderr).lower())

    def test_37_dirty_target_worktree_is_refused_without_overwrite(self) -> None:
        repo = self.new_repo({"policy.txt": "discount=10\n"})
        git(repo, "checkout", "source")
        write_text(repo, "policy.txt", "discount=50\n")
        commit_all(repo, "source change")
        git(repo, "checkout", "target")
        write_text(repo, "policy.txt", "local uncommitted decision\n")

        merged = self.merge_source(repo)

        self.assertNotEqual(merged.returncode, 0)
        self.assertIn("would be overwritten by merge", merged.stdout + merged.stderr)
        self.assertEqual(
            (repo / "policy.txt").read_text(encoding="utf-8"),
            "local uncommitted decision\n",
        )

    def test_40_git_auto_merge_still_blocks_unresolved_business_semantics(self) -> None:
        repo = self.new_repo(
            {
                "pricing.py": "MAX_DISCOUNT = 10\n",
                "checkout.py": "def allowed(discount):\n    return discount <= 10\n",
            }
        )
        self.diverge(
            repo,
            target_change=lambda root: write_text(root, "pricing.py", "MAX_DISCOUNT = 30\n"),
            source_change=lambda root: write_text(
                root,
                "checkout.py",
                "def allowed(discount):\n    return discount <= 50\n",
            ),
        )
        merged = self.merge_source(repo)
        gate = self.workflow_gate_for_analysis(unresolved_analysis_plan())

        self.assertEqual(merged.returncode, 0, merged.stderr)
        self.assertEqual(gate["current_state"], "intent-analysis", gate)
        self.assertTrue(
            any("mergeAnalysis" in blocker and "D-001" in blocker for blocker in gate["blockers"]),
            gate,
        )

    def test_41_resolved_business_semantics_require_code_and_test_traceability(self) -> None:
        missing_trace = self.validate(
            resolved_analysis_plan(),
            implementation_plan(include_decision=False),
        )
        complete = self.validate(
            resolved_analysis_plan(),
            implementation_plan(include_decision=True),
        )

        self.assertNotEqual(missing_trace.returncode, 0)
        self.assertIn("D-001", missing_trace.stdout)
        self.assertEqual(complete.returncode, 0, complete.stdout + complete.stderr)
        self.assertIn("OK:merge-analysis:analysis+implementation", complete.stdout)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MergeCodeWorkflowScenarioTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    print(f"OK:merge-code-workflow-scenarios:{result.testsRun}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
