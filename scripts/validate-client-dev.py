#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import gate_parse


POINTS = {1, 2, 3, 5, 8, 13}
DONE_STATUSES = {"已完成", "done", "completed"}
TIME_ESTIMATE_KEYS = {"estimated_hours", "estimate_hours", "hours", "days", "duration_hours"}
TEST_PRIORITIES = {"P0", "P1", "P2"}
AUTOMATION_STATES = {"automated", "manual", "planned"}


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def resolve(root: Path, raw: str, label: str) -> Path:
    require(bool(raw), f"缺少 {label} 路径")
    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValidationError(f"{label} 超出工作区: {raw}") from exc
    require(path.exists(), f"{label} 不存在: {raw}")
    return path


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{label} JSON 非法: {exc}") from exc
    require(isinstance(payload, dict), f"{label} 顶层必须是 object")
    return payload


def fm(path: Path) -> dict[str, str]:
    require(path.exists(), f"plan 不存在: {path}")
    return gate_parse.read_frontmatter(path)


def no_time_estimates(value: Any, where: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            require(key not in TIME_ESTIMATE_KEYS, f"{where} 禁止故事点换算工时字段: {key}")
            no_time_estimates(item, where)
    elif isinstance(value, list):
        for item in value:
            no_time_estimates(item, where)


def validate_backlog(root: Path, plan: Path) -> None:
    frontmatter = fm(plan)
    index = resolve(root, frontmatter.get("backlog_index", ""), "backlog_index")
    payload = load_json(index, "Backlog")
    require(payload.get("confirmed") is True, "Backlog 尚未由团队确认")
    requirements = payload.get("requirements")
    require(isinstance(requirements, list) and requirements, "Backlog requirements 必须是非空数组")
    ids: set[str] = set()
    for pos, item in enumerate(requirements, 1):
        require(isinstance(item, dict), f"requirement #{pos} 必须是 object")
        rid = str(item.get("id", "")).strip()
        require(rid and rid not in ids, f"requirement #{pos} id 缺失或重复: {rid}")
        ids.add(rid)
        for key in ["title", "business_value", "urgency", "priority", "reason"]:
            require(bool(str(item.get(key, "")).strip()), f"{rid} 缺少 {key}")
        require(isinstance(item.get("dependencies"), list), f"{rid}.dependencies 必须是数组")
        require(item.get("confirmed") is True, f"{rid} 尚未确认")
    no_time_estimates(payload, "Backlog")


def story_index(root: Path, plan: Path) -> tuple[Path, dict[str, Any]]:
    frontmatter = fm(plan)
    index = resolve(root, frontmatter.get("story_index", ""), "story_index")
    return index, load_json(index, "Story index")


def validate_story_metadata(payload: dict[str, Any]) -> list[dict[str, Any]]:
    require(payload.get("scope_confirmed") is True, "迭代 Scope 尚未由团队确认")
    stories = payload.get("stories")
    require(isinstance(stories, list) and stories, "stories 必须是非空数组")
    ids: set[str] = set()
    for pos, story in enumerate(stories, 1):
        require(isinstance(story, dict), f"story #{pos} 必须是 object")
        sid = str(story.get("id", "")).strip()
        require(sid and sid not in ids, f"story #{pos} id 缺失或重复: {sid}")
        ids.add(sid)
        require(bool(str(story.get("title", "")).strip()), f"{sid} 缺少 title")
        require(story.get("vertical_slice") is True, f"{sid} 不是可独立验收的纵向功能故事")
        require(isinstance(story.get("path"), str) and story["path"].strip(), f"{sid} 缺少子 Plan path")
        points = story.get("story_points")
        require(points in POINTS, f"{sid}.story_points={points!r}，须为 1/2/3/5/8/13")
        require(story.get("estimate_confirmed") is True, f"{sid} 故事点尚未由团队确认")
        require(bool(str(story.get("priority", "")).strip()), f"{sid} 缺少 priority")
        require(isinstance(story.get("sprint_scope"), bool), f"{sid}.sprint_scope 必须是 boolean")
        require(isinstance(story.get("dependencies"), list), f"{sid}.dependencies 必须是数组")
        require(isinstance(story.get("acceptance_criteria"), list) and story["acceptance_criteria"], f"{sid} 缺少 AC")
        require(isinstance(story.get("architecture_refs"), list) and story["architecture_refs"], f"{sid} 缺少架构引用")
        if story.get("sprint_scope") is True and points == 13:
            require(
                bool(str(story.get("estimate_waiver", "")).strip()) and story.get("waiver_confirmed") is True,
                f"{sid} 为 13 点，须继续拆分或提供团队确认的 estimate_waiver",
            )
    no_time_estimates(payload, "Story index")
    return stories


def delivery_scope(payload: dict[str, Any], stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Resolve the whole Epic delivery scope, falling back to legacy sprint scope.

    `sprint_scope` may rotate one Story at a time during implementation.  It is
    therefore a work-in-progress selector, not the exit criterion for the
    entire story-development stage.
    """
    epic_scope = payload.get("epic_scope")
    if epic_scope is not None:
        require(isinstance(epic_scope, list) and epic_scope, "epic_scope 必须是非空数组")
        wanted = [str(item).strip() for item in epic_scope]
        require(all(wanted) and len(set(wanted)) == len(wanted), "epic_scope 不得包含空值或重复 Story")
        by_id = {str(story.get("id") or ""): story for story in stories}
        missing = [story_id for story_id in wanted if story_id not in by_id]
        require(not missing, "epic_scope 引用不存在的 Story: " + ", ".join(missing))
        return [by_id[story_id] for story_id in wanted]
    return [story for story in stories if story.get("sprint_scope") is True]


def validate_story_scope(root: Path, plan: Path) -> None:
    _, payload = story_index(root, plan)
    stories = validate_story_metadata(payload)
    require(delivery_scope(payload, stories), "Epic 交付 Scope 至少需要一个用户故事")


def require_run(evidence: dict[str, Any], key: str, expect_zero: bool) -> None:
    run = evidence.get(key)
    require(isinstance(run, dict), f"TDD evidence 缺少 {key}")
    require(bool(str(run.get("command", "")).strip()), f"{key}.command 为空")
    require(isinstance(run.get("exit_code"), int), f"{key}.exit_code 必须是整数")
    require(bool(str(run.get("at", "")).strip()), f"{key}.at 为空")
    if expect_zero:
        require(run["exit_code"] == 0, f"{key} 未通过（exit_code={run['exit_code']}）")
    else:
        require(run["exit_code"] != 0, "Red 阶段必须先失败")
        require(bool(str(run.get("reason", "")).strip()), "red.reason 必须说明失败仅因功能尚未实现")


def validate_story_evidence(root: Path, story: dict[str, Any]) -> None:
    sid = str(story["id"])
    plan = resolve(root, str(story["path"]), f"{sid} 子 Plan")
    frontmatter = fm(plan)
    require(frontmatter.get("story_id") == sid, f"{sid} 子 Plan story_id 不匹配")
    require(frontmatter.get("status") in DONE_STATUSES, f"{sid} status 未完成")
    evidence_path = resolve(root, frontmatter.get("tdd_evidence", ""), f"{sid}.tdd_evidence")
    evidence = load_json(evidence_path, f"{sid} TDD evidence")
    require(evidence.get("story_id") == sid, f"{sid} TDD evidence.story_id 不匹配")
    require(bool(str(evidence.get("commit", "")).strip()), f"{sid} TDD evidence 缺少 commit")
    require_run(evidence, "red", expect_zero=False)
    require_run(evidence, "green", expect_zero=True)
    require_run(evidence, "refactor", expect_zero=True)
    require_run(evidence, "integration_smoke", expect_zero=True)
    acceptance = evidence.get("acceptance")
    require(isinstance(acceptance, list), f"{sid}.acceptance 必须是数组")
    passed = {str(item.get("ac_id")) for item in acceptance if isinstance(item, dict) and item.get("pass") is True}
    missing = sorted(set(str(item) for item in story["acceptance_criteria"]) - passed)
    require(not missing, f"{sid} 缺少通过的 AC: {', '.join(missing)}")


def validate_story_development(
    root: Path,
    plan: Path,
    story_id: str | None = None,
    *,
    require_current_scope: bool = True,
) -> None:
    _, payload = story_index(root, plan)
    stories = validate_story_metadata(payload)
    scoped = delivery_scope(payload, stories)
    require(scoped, "Scope 内至少需要一个用户故事")
    if story_id:
        story = next((item for item in scoped if str(item.get("id")) == story_id), None)
        require(story is not None, f"story_id 不属于 Epic Scope: {story_id}")
        if require_current_scope:
            require(story.get("sprint_scope") is True, f"story_id 不是当前滚动 Scope: {story_id}")
        validate_story_evidence(root, story)
        return
    for story in scoped:
        validate_story_evidence(root, story)


def validate_test_plan(root: Path, plan: Path) -> None:
    frontmatter = fm(plan)
    target_commit = frontmatter.get("target_commit", "").strip()
    require(target_commit, "集成测试计划缺少 target_commit")
    _, story_payload = story_index(root, plan)
    stories = validate_story_metadata(story_payload)
    scoped = delivery_scope(story_payload, stories)
    require(scoped, "Scope 内至少需要一个用户故事")

    case_index_path = resolve(root, frontmatter.get("test_case_index", ""), "test_case_index")
    case_index = load_json(case_index_path, "Test case index")
    require(case_index.get("target_commit") == target_commit, "用例索引 target_commit 与测试计划不一致")
    cases = case_index.get("cases")
    require(isinstance(cases, list) and cases, "测试用例 cases 必须是非空数组")

    case_ids: set[str] = set()
    covered: set[tuple[str, str]] = set()
    for pos, case in enumerate(cases, 1):
        require(isinstance(case, dict), f"测试用例 #{pos} 必须是 object")
        case_id = str(case.get("id", "")).strip()
        require(case_id and case_id not in case_ids, f"测试用例 #{pos} id 缺失或重复: {case_id}")
        case_ids.add(case_id)
        require(bool(str(case.get("title", "")).strip()), f"{case_id} 缺少 title")
        require(case.get("priority") in TEST_PRIORITIES, f"{case_id}.priority 须为 P0/P1/P2")
        require(bool(str(case.get("type", "")).strip()), f"{case_id} 缺少 type")
        require(isinstance(case.get("preconditions"), list), f"{case_id}.preconditions 必须是数组")
        require(isinstance(case.get("test_data"), list), f"{case_id}.test_data 必须是数组")
        require(isinstance(case.get("steps"), list) and case["steps"], f"{case_id}.steps 必须是非空数组")
        require(
            isinstance(case.get("expected_results"), list) and case["expected_results"],
            f"{case_id}.expected_results 必须是非空数组",
        )
        require(case.get("automation") in AUTOMATION_STATES, f"{case_id}.automation 取值非法")
        require(bool(str(case.get("suite", "")).strip()), f"{case_id} 缺少 suite")
        ac_refs = case.get("ac_refs")
        require(isinstance(ac_refs, list) and ac_refs, f"{case_id}.ac_refs 必须是非空数组")
        for ref in ac_refs:
            require(isinstance(ref, dict), f"{case_id}.ac_refs 每项必须是 object")
            story_id = str(ref.get("story_id", "")).strip()
            ac_id = str(ref.get("ac_id", "")).strip()
            require(story_id and ac_id, f"{case_id}.ac_refs 缺少 story_id/ac_id")
            covered.add((story_id, ac_id))

    required_ac = {
        (str(story["id"]), str(ac_id))
        for story in scoped
        for ac_id in story.get("acceptance_criteria", [])
    }
    missing = sorted(required_ac - covered)
    require(
        not missing,
        "Scope Story/AC 缺测试用例覆盖: " + ", ".join(f"{story}/{ac}" for story, ac in missing),
    )

    review_path = resolve(root, frontmatter.get("test_review", ""), "test_review")
    review = load_json(review_path, "Test review")
    require(review.get("approved") is True, "测试审核尚未通过")
    require(bool(str(review.get("reviewer", "")).strip()), "测试审核缺少 reviewer")
    require(bool(str(review.get("reviewed_at", "")).strip()), "测试审核缺少 reviewed_at")
    require(review.get("target_commit") == target_commit, "测试审核 target_commit 与测试计划不一致")
    actual_sha = hashlib.sha256(case_index_path.read_bytes()).hexdigest()
    require(review.get("case_index_sha256") == actual_sha, "测试审核对应的用例索引已发生漂移")
    require(review.get("unresolved_comments") == 0, "测试审核仍有未解决意见")


def validate_integration(root: Path, plan: Path) -> None:
    frontmatter = fm(plan)
    target_commit = frontmatter.get("target_commit", "").strip()
    require(target_commit, "集成测试 Plan 缺少 target_commit")
    approved_plan = resolve(root, frontmatter.get("approved_test_plan", ""), "approved_test_plan")
    validate_test_plan(root, approved_plan)
    approved_frontmatter = fm(approved_plan)
    require(approved_frontmatter.get("target_commit", "").strip() == target_commit, "执行 target_commit 与已审核测试计划不一致")
    report_path = resolve(root, frontmatter.get("integration_report", ""), "integration_report")
    report = load_json(report_path, "Integration report")
    require(report.get("commit") == target_commit, "集成报告 commit 与 target_commit 不一致")
    require(report.get("all_scope_stories_completed") is True, "并非全部 Scope 故事均已完成")
    suites = report.get("suites")
    require(isinstance(suites, list) and suites, "integration suites 必须是非空数组")
    for pos, suite in enumerate(suites, 1):
        require(isinstance(suite, dict), f"suite #{pos} 必须是 object")
        require(bool(str(suite.get("name", "")).strip()), f"suite #{pos} 缺少 name")
        require(bool(str(suite.get("command", "")).strip()), f"suite #{pos} 缺少 command")
        require(suite.get("exit_code") == 0, f"suite {suite.get('name', pos)} 未通过")

    # 非空 story index 时，最终集成门禁再次核对所有 Scope 故事的 TDD 文件事实。
    _, payload = story_index(root, plan)
    stories = payload.get("stories")
    require(isinstance(stories, list), "Story index.stories 必须是数组")
    if stories:
        validate_story_metadata(payload)
        for story in delivery_scope(payload, stories):
            validate_story_evidence(root, story)


def validate_implementation_design(root: Path, plan: Path) -> None:
    proc = subprocess.run(
        [
            "python3",
            str(Path(__file__).resolve().parent / "validate-implementation-design.py"),
            "--root",
            str(root),
            "--plan",
            str(plan),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    require(proc.returncode == 0, (proc.stderr or proc.stdout).strip())


COMMANDS = {
    "backlog": validate_backlog,
    "implementation-design": validate_implementation_design,
    "story-scope": validate_story_scope,
    "story-development": validate_story_development,
    "test-plan": validate_test_plan,
    "integration": validate_integration,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 client-dev 敏捷工作流文件事实。")
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--plan", required=True)
    parser.add_argument("--story-id", help="验收当前滚动 Scope 的单个 Story；这是文件事实校验，不自动定义逐 Story 门禁事件")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    plan = Path(args.plan)
    if not plan.is_absolute():
        plan = root / plan
    try:
        if args.story_id:
            require(args.command == "story-development", "--story-id 仅适用于 story-development")
            validate_story_development(
                root,
                plan.resolve(),
                args.story_id,
            )
        else:
            COMMANDS[args.command](root, plan.resolve())
    except (ValidationError, OSError) as exc:
        print(f"BLOCKED:client-dev:{args.command}:{exc}", file=sys.stderr)
        return 1
    print(f"OK:client-dev:{args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
