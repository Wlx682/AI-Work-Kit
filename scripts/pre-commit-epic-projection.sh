#!/usr/bin/env bash
# git pre-commit — 拦截涉及 Epic 或带 epic: 子 plan 的违规 commit。
#
# 安装（追加到既有 pre-commit hook 末尾）：
#   cat scripts/pre-commit-epic-projection.sh >> .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
# 或独立挂：
#   ln -sf "$(pwd)/scripts/pre-commit-epic-projection.sh" .git/hooks/pre-commit
#
# 跳过：git commit --no-verify
# 协议：Contexts/决策/母子plan投影规则.md
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
[[ -z "$STAGED" ]] && exit 0

failed=0
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  [[ "$f" == *.md ]] || continue
  [[ -f "$f" ]] || continue
  need=0
  case "$f" in
    Plans/Epic/*.md) need=1 ;;
    Plans/*.md|Plans/*/*.md)
      grep -qE '^epic:' "$f" 2>/dev/null && need=1
      ;;
  esac
  [[ $need -eq 1 ]] || continue
  if ! python3 "$ROOT/scripts/validate-epic-projection.py" "$f" >&2; then
    echo "❌ 母子 plan 投影校验失败：$f" >&2
    failed=1
  fi
done <<< "$STAGED"

if [[ $failed -eq 1 ]]; then
  echo "" >&2
  echo "修复 plan 状态格/备注后重新 commit，或临时跳过：git commit --no-verify" >&2
  echo "协议：Contexts/决策/母子plan投影规则.md" >&2
  exit 1
fi
exit 0
