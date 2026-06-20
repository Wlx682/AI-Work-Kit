#!/usr/bin/env python3
"""批量将 Plans/ 下 plan 标记为已完成（Epic WBS 全勾 + frontmatter）。"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = date.today().isoformat()
SKIP_NAMES = {"README.md", ".gitkeep"}

STATUS_SKIP = {"索引"}  # 非 plan 状态


def is_fence_delimiter(line: str) -> bool:
    s = line.strip()
    return s == "```" or (s.startswith("```") and len(s) > 3)


def patch_numbered_and_list_checkboxes(text: str) -> str:
    """勾选 WBS 编号行、markdown 列表与行内 `[ ]`（反引号内除外）。"""
    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        parts = re.split(r"(`[^`]*`)", line)
        for i, part in enumerate(parts):
            if part.startswith("`"):
                continue
            part = re.sub(r"\[ \]", "[x]", part)
            part = re.sub(r"^- \[~\]", "- [x]", part)
            m = re.match(r"^\[[ xX~]\]\s*(\d+)\.\s*(.+)$", part)
            if m:
                part = f"[x] {m.group(1)}.  {m.group(2).strip()}"
            if "⏳" in part or "🟡" in part or "⬜" in part:
                part = (
                    part.replace("⬜", "✅")
                    .replace("🟡", "✅")
                    .replace("⏳", "✅")
                )
            parts[i] = part
        out.append("".join(parts))
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def patch_fence_numbered_checkboxes(text: str) -> str:
    return patch_numbered_and_list_checkboxes(text)


def patch_inline_checkboxes(text: str) -> str:
    return text


def patch_body_checkboxes(text: str) -> str:
    return text


def patch_frontmatter(text: str, is_epic: bool) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    fm = text[3:end]
    body = text[end + 4 :]

    def set_field(block: str, key: str, value: str) -> str:
        pat = re.compile(rf"^{re.escape(key)}:.*$", re.M)
        if pat.search(block):
            return pat.sub(f"{key}: {value}", block, count=1)
        return block.rstrip() + f"\n{key}: {value}"

    st = re.search(r"^status:\s*(.+)$", fm, re.M)
    if st and st.group(1).strip() not in STATUS_SKIP:
        fm = set_field(fm, "status", "已采纳")
    if re.search(r"^lifecycle_state:", fm, re.M):
        fm = set_field(fm, "lifecycle_state", "done")
    if is_epic:
        fm = set_field(fm, "status", "已采纳")
        fm = set_field(fm, "lifecycle_state", "done")

    return "---" + fm + "\n---" + body


def patch_epic_wbs(text: str) -> str:
    return patch_fence_numbered_checkboxes(text)


def patch_body_status_line(text: str) -> str:
    # **状态**：进行中 → 已采纳 · lifecycle done
    text = re.sub(
        r"(\*\*状态\*\*：)[^·\n]+",
        r"\1已采纳",
        text,
    )
    text = re.sub(
        r"(\*\*lifecycle_state\*\*：)[^\n]+",
        r"\1done",
        text,
    )
    return text


def append_epic_changelog(text: str) -> str:
    row = f"| {TODAY} | 批量归档 | done | 1–15 | 王龙祥 | 用户确认全部计划完成（含试点/测试项） |"
    if row in text:
        return text
    marker = "## 四、变更日志"
    if marker not in text:
        return text
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("|------") and i > 0 and "日期" in lines[i - 1]:
            lines.insert(i + 1, row)
            break
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def should_skip(path: Path) -> bool:
    if path.name in SKIP_NAMES:
        return True
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if rel.startswith("Plans/学习/"):
        return True
    return False


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.glob("Plans/**/*.md")):
        if should_skip(path):
            continue
        raw = path.read_text(encoding="utf-8")
        is_epic = "Plans/Epic" in str(path.relative_to(ROOT)).replace("\\", "/")
        new = patch_frontmatter(raw, is_epic)
        if is_epic:
            new = patch_epic_wbs(new)
            new = append_epic_changelog(new)
        else:
            new = patch_fence_numbered_checkboxes(new)
        new = patch_body_status_line(new)
        new = patch_numbered_and_list_checkboxes(new)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"Updated {len(changed)} files:")
    for p in changed:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
