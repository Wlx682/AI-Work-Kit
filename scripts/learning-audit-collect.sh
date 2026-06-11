#!/usr/bin/env bash
# 学习进度审计 — 机械取证（复选框、frontmatter status）
# 用法：从 vault 根目录运行 ./scripts/learning-audit-collect.sh [Plans/学习]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLANS_DIR="${1:-Plans/学习}"
PLANS_PATH="$ROOT/$PLANS_DIR"

if [[ ! -d "$PLANS_PATH" ]]; then
  echo "错误：目录不存在 $PLANS_DIR" >&2
  exit 1
fi

echo "# learning-audit 机械取证"
echo "# vault: $ROOT"
echo "# plans: $PLANS_DIR"
echo ""

shopt -s nullglob
files=("$PLANS_PATH"/*.md)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "（无 plan 文件）"
  exit 0
fi

for f in "${files[@]}"; do
  rel="${f#"$ROOT"/}"
  title="$(basename "$f" .md)"

  status="$(awk 'BEGIN{in_fm=0} /^---$/{in_fm++; next} in_fm==1 && /^status:/{sub(/^status:[[:space:]]*/,""); print; exit}' "$f")"
  [[ -z "$status" ]] && status="（无 status 字段）"

  total="$(grep -cE '^[[:space:]]*-[[:space:]]+\[[ xX]\]' "$f" 2>/dev/null || true)"
  checked="$(grep -cE '^[[:space:]]*-[[:space:]]+\[[xX]\]' "$f" 2>/dev/null || true)"

  echo "## $title"
  echo "path: $rel"
  echo "claimed_status: $status"
  echo "checkbox_checked: $checked"
  echo "checkbox_total: $total"
  echo ""
done
