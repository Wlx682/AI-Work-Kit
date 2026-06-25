#!/usr/bin/env bash
# Claude Code PostToolUse hook — Edit/Write/MultiEdit 完成 plan 文件后自动跑投影校验。
#
# 输入：Claude Code 通过 stdin 传 JSON：
#   { "tool_name": "Edit", "tool_input": { "file_path": "..." }, ... }
# 行为：
#   - file_path 非 Plans/ 下 .md → 静默 exit 0
#   - file_path 是 Plans/Epic/*.md 或带 `epic:` frontmatter 的子 plan → 跑校验
#   - 校验失败：exit 2（Claude Code 会把 stderr 反馈给 AI 触发自修）
# 协议：Contexts/决策/母子plan投影规则.md
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INPUT="$(cat)"

FILE_PATH="$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get("tool_input", {}).get("file_path", ""))
except Exception:
    pass
')"

[[ -z "$FILE_PATH" ]] && exit 0
case "$FILE_PATH" in *.md) ;; *) exit 0 ;; esac
case "$FILE_PATH" in */Plans/*) ;; *) exit 0 ;; esac
[[ -f "$FILE_PATH" ]] || exit 0

NEED_CHECK=0
case "$FILE_PATH" in
  */Plans/Epic/*.md)
    NEED_CHECK=1
    ;;
  */Plans/*/*.md|*/Plans/*.md)
    if grep -qE '^epic:' "$FILE_PATH" 2>/dev/null; then
      NEED_CHECK=1
    fi
    ;;
esac
[[ $NEED_CHECK -eq 0 ]] && exit 0

if ! python3 "$ROOT/scripts/validate-epic-projection.py" "$FILE_PATH" >&2; then
  echo "" >&2
  echo "[母子 plan 投影校验] 本次写入触发违规，需修复 plan 状态格/备注后再继续。" >&2
  echo "协议：Contexts/决策/母子plan投影规则.md" >&2
  exit 2
fi
exit 0
