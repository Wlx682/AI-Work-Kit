#!/usr/bin/env bash
# 学习收尾自动采集：追加进度快照（轻量，非完整审计）
# 用法：
#   ./scripts/learning-progress-snapshot.sh --mode 续学 --plan Plans/学习/xxx.md --summary "本次摘要"
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODE=""
PLAN=""
SUMMARY=""
SNAPSHOT="$ROOT/Contexts/LLM学习/笔记/学习进度快照.md"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:-}"; shift 2 ;;
    --plan) PLAN="${2:-}"; shift 2 ;;
    --summary) SUMMARY="${2:-}"; shift 2 ;;
    *) echo "未知参数: $1" >&2; exit 1 ;;
  esac
done

[[ -z "$MODE" ]] && MODE="学习"
DATE="$(date '+%Y-%m-%d')"
TIME="$(date '+%H:%M')"
STAMP="${DATE} ${TIME}"

COLLECT="$("$ROOT/scripts/learning-audit-collect.sh" "Plans/学习" 2>/dev/null || true)"

mkdir -p "$(dirname "$SNAPSHOT")"
if [[ ! -f "$SNAPSHOT" ]]; then
  cat > "$SNAPSHOT" <<'EOF'
---
tags: [学习, 进度快照, 自动采集]
---

# 学习进度快照

> 由 `learn-assistant` 每次学习收尾自动追加。完整交叉审计：`/learning-audit-assistant`。

EOF
fi

{
  echo ""
  echo "## ${STAMP} · ${MODE}"
  [[ -n "$PLAN" ]] && echo "- **plan**：\`${PLAN}\`"
  [[ -n "$SUMMARY" ]] && echo "- **摘要**：${SUMMARY}"
  echo ""
  echo "| 课程 | 声称状态 | 勾选 |"
  echo "|------|----------|------|"

  if [[ -n "$PLAN" ]]; then
    lesson="$(basename "$PLAN" .md)"
    block="$(echo "$COLLECT" | awk -v lesson="$lesson" '
      $0 ~ "^## " lesson "$" { found=1; next }
      found && /^## / { exit }
      found && /^claimed_status:/ { status=$2; for(i=3;i<=NF;i++) status=status" "$i }
      found && /^checkbox_checked:/ { c=$2 }
      found && /^checkbox_total:/ { t=$2; print "| " lesson " | " status " | " c "/" t " |"; exit }
    ')"
    if [[ -n "$block" ]]; then
      echo "$block"
    else
      echo "| ${lesson} | （未在采集中找到） | — |"
    fi
  else
    echo "$COLLECT" | awk '
      /^## / { lesson=$0; sub(/^## /,"",lesson); next }
      /^claimed_status:/ { status=$0; sub(/^claimed_status: /,"",status); next }
      /^checkbox_checked:/ { c=$2; next }
      /^checkbox_total:/ { print "| " lesson " | " status " | " c "/" $2 " |"; status=""; c="" }
    '
  fi
} >> "$SNAPSHOT"

echo "已追加快照：Contexts/LLM学习/笔记/学习进度快照.md"
