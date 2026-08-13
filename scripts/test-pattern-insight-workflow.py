#!/usr/bin/env python3
"""Dedicated regression for the pattern-insight-workflow Zhihu publishing protocol."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / ".cursor/skills/pattern-insight-workflow"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_fragments(path: Path, fragments: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path
    for fragment in fragments:
        require(fragment in text, f"{display_path} missing: {fragment}")


def main() -> int:
    require_fragments(
        SKILL_DIR / "SKILL.md",
        [
            "知乎发布协议",
            "08-zhihu-answer.md",
            "草稿验收",
            "行动时确认",
            "公开 URL",
        ],
    )
    require_fragments(
        SKILL_DIR / "references/method.md",
        [
            "内容、账号与位置审批 D",
            "草稿写入与结构验收",
            "行动时确认",
            "点击发布并回写链接",
        ],
    )
    require_fragments(
        ROOT / "Skills/pattern_insight_workflow.md",
        ["知乎发布硬门禁", "图片数量及加载状态", "最终点击授权"],
    )

    with tempfile.TemporaryDirectory(prefix="pattern-insight-regression-") as temp:
        workspace = Path(temp)
        result = subprocess.run(
            [
                sys.executable,
                str(SKILL_DIR / "scripts/init_cycle.py"),
                "--workspace",
                str(workspace),
                "--domain",
                "AI Agent 工作流",
                "--question",
                "如何把知乎发布固化到流程？",
                "--date",
                "2026-08-13",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cycle = Path(result.stdout.strip())
        require((cycle / "08-zhihu-answer.md").exists(), "initializer missing Zhihu answer artifact")
        require_fragments(
            cycle / "07-publish-package.md",
            [
                "默认平台：知乎问答",
                "草稿验收：待执行",
                "行动时确认：未取得",
                "发布状态：未发布",
            ],
        )

    print("OK:pattern-insight-workflow:Zhihu publishing protocol regression passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
