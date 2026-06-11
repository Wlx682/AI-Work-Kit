#!/usr/bin/env bash
# 学习会话开场：读取进度摘要，供 learn-assistant 动态出资料
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLANS_DIR="Plans/学习"
SNAPSHOT="$ROOT/Contexts/LLM学习/笔记/学习进度快照.md"
NOTES_DIR="$ROOT/Contexts/LLM学习/笔记"

echo "# 学习进度摘要（开场必读）"
echo ""

echo "## 机械取证"
"$ROOT/scripts/learning-audit-collect.sh" "$PLANS_DIR" 2>/dev/null || echo "（取证脚本失败）"
echo ""

echo "## 当前推荐课程"
current=""
shopt -s nullglob
for f in "$ROOT/$PLANS_DIR"/*.md; do
  status="$(awk 'BEGIN{in_fm=0} /^---$/{in_fm++; next} in_fm==1 && /^status:/{sub(/^status:[[:space:]]*/,""); print; exit}' "$f")"
  if [[ "$status" == "进行中" ]]; then
    current="$(basename "$f" .md)"
    echo "- **进行中**：$current"
    break
  fi
done
if [[ -z "$current" ]]; then
  for f in "$ROOT/$PLANS_DIR"/*.md; do
    checked="$(grep -cE '^[[:space:]]*-[[:space:]]+\[[xX]\]' "$f" 2>/dev/null || true)"
    total="$(grep -cE '^[[:space:]]*-[[:space:]]+\[[ xX]\]' "$f" 2>/dev/null || true)"
    if [[ "$total" -gt 0 && "$checked" -lt "$total" ]]; then
      echo "- **未完成步骤**：$(basename "$f" .md)（${checked}/${total}）"
      current="$(basename "$f" .md)"
      break
    fi
  done
fi
[[ -z "$current" ]] && echo "- （无明显进行中课程，见上方取证或学习路线）"
echo ""

if [[ -f "$SNAPSHOT" ]]; then
  echo "## 最近快照（最多 3 条）"
  awk '
    /^## [0-9]{4}-[0-9]{2}-[0-9]{2}/ { if (n>=3) exit; buf=$0; block=buf"\n"; n++; next }
    n>0 && /^## / && !/^## [0-9]{4}/ { exit }
    n>0 { block=block $0 "\n" }
    END {
      # 简化：打印文件末尾约 40 行
    }
  ' "$SNAPSHOT" 2>/dev/null || true
  tail -n 25 "$SNAPSHOT" | sed 's/^/  /'
  echo ""
fi

latest_audit="$(ls -t "$NOTES_DIR"/*-学习进度审计报告.md 2>/dev/null | head -1 || true)"
if [[ -n "$latest_audit" ]]; then
  echo "## 最近审计报告"
  echo "- $(basename "$latest_audit")"
  grep -m1 '^经交叉验证' "$latest_audit" 2>/dev/null | sed 's/^/  /' || true
  echo ""
fi

echo "## 动态出资料提示"
echo "- 优先讲「未完成步骤」中的第一项，不重复已勾选内容"
echo "- 无本课笔记 → 本次侧重练习或整理笔记"
echo "- frontmatter 与勾选矛盾 → 以勾选和笔记为准"
