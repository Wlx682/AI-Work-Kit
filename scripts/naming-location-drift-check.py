#!/usr/bin/env python3
"""
Check naming/location drift for AI-Work-Kit workflow assets.

This complements doc-script-refs-check.py:
- every Templates/*.md file must be represented in Templates/模板约定.md;
- operational docs must not reference removed workflow/skill names;
- AGENTS.md wikilinks must point to existing markdown files.

Historical Contexts/ and Plans/ notes are intentionally not hard-failed here.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OPERATIONAL_MD = [
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / "README.md",
    ROOT / "索引.md",
    *sorted((ROOT / "Skills").glob("*.md")),
    *sorted((ROOT / "Templates").glob("*.md")),
]

LEGACY_TERMS = {
    "Templates/Epic母版.md": "Use Templates/Epic模板-client-dev.md.",
    "Templates/Epic母版-client-dev.md": "Use Templates/Epic模板-client-dev.md.",
    "Skills/figma_ui_assistant.md": "Use Skills/figma_ui.md.",
    "figma_ui_assistant": "Use figma-ui / Skills/figma_ui.md.",
    "full_cycle_assistant": "Use workflow-router + full-cycle engine.",
    "full-cycle-assistant": "Use workflow-router + full-cycle engine.",
    ".Codex/": "Use .codex/ for skills and .workflows/blueprints/ for workflows.",
    ".codex/workflows": "Use .workflows/blueprints/.",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def check_template_index() -> list[str]:
    index = ROOT / "Templates" / "模板约定.md"
    text = index.read_text(encoding="utf-8")
    errors: list[str] = []
    for template in sorted((ROOT / "Templates").glob("*.md")):
        if template.name not in text:
            errors.append(
                f"{rel(index)}: 模板清单缺少 {template.name}"
            )
    return errors


def check_operational_legacy_terms() -> list[str]:
    errors: list[str] = []
    for path in OPERATIONAL_MD:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), 1):
            for term, hint in LEGACY_TERMS.items():
                if term in line:
                    errors.append(f"{rel(path)}:{lineno}: legacy `{term}`. {hint}")
    return errors


def check_agents_wikilinks() -> list[str]:
    path = ROOT / "AGENTS.md"
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in re.finditer(r"\[\[([^]|#]+)(?:#[^]|]+)?(?:\|[^]]+)?\]\]", line):
            target = match.group(1).strip()
            if target in {"索引"}:
                candidates = [ROOT / f"{target}.md"]
            else:
                candidates = [ROOT / target, ROOT / f"{target}.md"]
            if not any(candidate.exists() for candidate in candidates):
                errors.append(f"AGENTS.md:{lineno}: broken wikilink [[{target}]]")
    return errors


def main() -> int:
    errors = []
    errors.extend(check_template_index())
    errors.extend(check_operational_legacy_terms())
    errors.extend(check_agents_wikilinks())

    if errors:
        print("✗ 命名/定位漂移检查失败：", file=sys.stderr)
        for err in errors:
            print(f"  · {err}", file=sys.stderr)
        return 1

    print("✓ 命名/定位漂移检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
