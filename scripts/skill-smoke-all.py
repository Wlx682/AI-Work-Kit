#!/usr/bin/env python3
"""聚合跑所有 skill fixture smoke test + 覆盖率报告。

- 发现 tests/fixtures/skills/<skill>/<case>.input.md 逐个校验（复用 skill-smoke-test.py）。
- 覆盖率：对照 .cursor/skills 真理源，列出「应有 fixture 但缺」的产物类 Skill。
- 路由/运维类 Skill 不产出文档产物（由 workflow-router-check / gate 测试覆盖），列入豁免集，不计缺口。

退出码：任一 fixture 结构非法 → 1；仅覆盖缺口 → 0（缺口是 warning，打印不阻塞）。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_ROOT = ROOT / "tests/fixtures/skills"
CURSOR_SKILLS = ROOT / ".cursor/skills"

# 无文档产物、不走 fixture 模型的 Skill（路由/运维/编排类）。
# 这些由 workflow-router-check.py / test-workflow-refactor.py 的门禁与路由用例覆盖，
# 不纳入 fixture 覆盖率缺口，避免逼出无意义的桩 fixture。
FIXTURE_EXEMPT = {
    "workflow-router",       # 路由：test_workflow_router_* 覆盖
    "resume-assistant",      # 续做编排：无固定产物结构
    "skill-sync",            # 运维：sync-claude-skills.sh 自带校验
    "kanban-restart",        # 运维：重启看板服务，kanban-server.sh + HTTP 健康检查覆盖
    "workflow-evolution-assistant",  # 聚合 skill_run：feedback-aggregate 覆盖
    "feature-dev-assistant",  # 开发编排：产物是 plan/代码，由 workflow gate 覆盖
    "merge-code-assistant",  # 合并执行：产物是 Git 变更，由 merge-code workflow gate 覆盖
    "visual-markdown-toolbox",  # 表达路由工具箱：无单一固定产物结构
}


def discover_fixtures() -> list[tuple[str, Path]]:
    """返回 [(skill, input_path)]，按 skill/case 排序。"""
    found: list[tuple[str, Path]] = []
    if not FIXTURE_ROOT.is_dir():
        return found
    for skill_dir in sorted(FIXTURE_ROOT.iterdir()):
        if not skill_dir.is_dir():
            continue
        for inp in sorted(skill_dir.glob("*.input.md")):
            found.append((skill_dir.name, inp))
    return found


def all_skills() -> list[str]:
    if not CURSOR_SKILLS.is_dir():
        return []
    return sorted(d.name for d in CURSOR_SKILLS.iterdir() if d.is_dir())


def run_one(skill: str, inp: Path) -> tuple[bool, str]:
    proc = subprocess.run(
        ["python3", "scripts/skill-smoke-test.py", skill, str(inp.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, out


def main() -> int:
    fixtures = discover_fixtures()
    skills = all_skills()

    if not fixtures:
        print("BLOCKED:skill-smoke-all: 未发现任何 fixture（tests/fixtures/skills/*/*.input.md）", file=sys.stderr)
        return 1

    failed = 0
    covered: set[str] = set()
    for skill, inp in fixtures:
        ok, out = run_one(skill, inp)
        print(out)
        if ok:
            covered.add(skill)
        else:
            failed += 1

    # 覆盖率报告
    testable = [s for s in skills if s not in FIXTURE_EXEMPT]
    missing = sorted(s for s in testable if s not in covered)
    print()
    print(f"覆盖率：{len(covered)}/{len(testable)} 产物类 Skill 有通过的 fixture"
          f"（豁免 {len(FIXTURE_EXEMPT)} 个路由/运维类）")
    if missing:
        print("尚缺 fixture 的产物类 Skill（warning，不阻塞）：")
        for s in missing:
            print(f"  · {s}")

    if failed:
        print(f"\n❌ {failed} 个 fixture 结构校验失败。", file=sys.stderr)
        return 1
    print(f"\n✓ 全部 {len(fixtures)} 个 fixture 结构合法。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
