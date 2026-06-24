#!/usr/bin/env bash
# pre-commit-relations.sh — 枢纽文件依赖提醒
#
# 安装：
#   cp scripts/pre-commit-relations.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# 用法：commit 时自动触发；非交互模式（CI / commit --no-verify）跳过。
#
# 触发条件：暂存区包含下列枢纽文件之一。
# 输出：列出每个枢纽文件的 dependents，让用户确认。
#
# 跳过：git commit --no-verify

set -euo pipefail

# 枢纽文件清单（与 关系图谱协议.md §四 一致）
HUB_FILES=(
  "Contexts/决策/Kit核心原则.md"
  "Contexts/决策/AI-Work-Kit工作流总览.md"
  "Contexts/决策/Skill反馈协议.md"
  "Contexts/决策/资料与代码仓库边界.md"
  "Contexts/决策/关系图谱协议.md"
  "Templates/模板约定.md"
  "Contexts/需求分析/需求分析产出标准.md"
)

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# 暂存区文件
STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)

# 找暂存区里的枢纽文件
touched_hubs=()
for hub in "${HUB_FILES[@]}"; do
  if echo "$STAGED" | grep -Fxq "$hub"; then
    touched_hubs+=("$hub")
  fi
done

if [ ${#touched_hubs[@]} -eq 0 ]; then
  exit 0
fi

echo "ℹ️  本次 commit 涉及枢纽文件："
for hub in "${touched_hubs[@]}"; do
  echo "  · $hub"
done
echo ""
echo "📎 以下文件依赖被修改的枢纽文件，请确认是否同步："

# 提取每个枢纽文件的 dependents
extract_dependents() {
  local file="$1"
  awk '
    BEGIN { in_fm=0; in_rel=0; in_dep=0 }
    /^---$/ {
      if (in_fm == 0) { in_fm = 1; next }
      else { exit }
    }
    in_fm == 1 && /^relations:/ { in_rel = 1; next }
    in_fm == 1 && in_rel == 1 && /^  dependents:/ { in_dep = 1; next }
    in_fm == 1 && in_rel == 1 && in_dep == 1 && /^    - / {
      sub(/^    - /, "")
      print
      next
    }
    in_fm == 1 && in_rel == 1 && in_dep == 1 && !/^    / { in_dep = 0 }
    in_fm == 1 && in_rel == 1 && !/^  / && !/^---$/ { in_rel = 0 }
  ' "$file"
}

found_any=0
for hub in "${touched_hubs[@]}"; do
  deps=$(extract_dependents "$hub" || true)
  if [ -n "$deps" ]; then
    count=$(echo "$deps" | grep -c . || true)
    echo ""
    echo "依赖 $hub（共 $count 个 dependents）："
    while IFS= read -r dep; do
      [ -z "$dep" ] && continue
      echo "  · $dep"
    done <<< "$deps"
    found_any=1
  fi
done

if [ $found_any -eq 0 ]; then
  echo "  （无 dependents 字段，跳过）"
  exit 0
fi

echo ""
echo "----------"
echo "确认你已同步上述依赖文件，或它们不受本次变更影响。"
echo "跳过本次提示：git commit --no-verify"

# 非交互式环境（CI）允许通过；交互式提示用户确认
if [ ! -t 0 ]; then
  exit 0
fi

read -rp "已确认同步 (y/N)? " ans
case "$ans" in
  y|Y|yes|YES) exit 0 ;;
  *) echo "❌ 已取消 commit"; exit 1 ;;
esac
