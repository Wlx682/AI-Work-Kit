#!/usr/bin/env bash
# pre-commit-relations.sh — 提交前门禁（两职责）：
#   1) Epic 看板新鲜度：暂存区含 Epic / 带 epic: 子 Plan 时，跑 render-epic-board.py --check，
#      §三 看板与子 Plan 事实漂移即拦截（协议：Contexts/决策/母子plan投影规则.md）。
#   2) 枢纽文件依赖提醒：暂存区含枢纽文件时列出 dependents 让用户确认。
#
# 安装：
#   cp scripts/pre-commit-relations.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# 用法：commit 时自动触发；非交互模式（CI / commit --no-verify）跳过交互确认。
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

# 暂存区文件（core.quotepath=false：中文路径不转义八进制，否则 case 匹配失效）
STAGED=$(git -c core.quotepath=false diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)

# ── Epic 看板新鲜度门禁（派生渲染规则）─────────────────────────────────
# 三层架构：Epic §三 看板是子 Plan 事实的只读投影，禁止手写漂移。
# 暂存区含 Epic 或带 epic: 的子 Plan 时，回扫其 Epic 跑 render --check：
#   退出 1（漂移）→ 拦截 commit，提示跑 --write 刷新；
#   退出 2（基础设施失败）→ 仅告警放行，不阻断日常提交。
# 协议：Contexts/决策/母子plan投影规则.md
if [ -n "$STAGED" ] && command -v python3 >/dev/null 2>&1; then
  epics_to_check=()
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    case "$f" in
      *.md) ;;
      *) continue ;;
    esac
    epic_target=""
    case "$f" in
      Plans/Epic/*.md)
        epic_target="$f" ;;
      Plans/*.md)
        if [ -f "$f" ]; then
          ev="$(python3 "$ROOT/scripts/gate_parse.py" read-frontmatter-key "$f" epic 2>/dev/null || true)"
          [ -n "$ev" ] && epic_target="$ev"
        fi ;;
    esac
    [ -z "$epic_target" ] && continue
    [[ "$epic_target" == *.md ]] || epic_target="${epic_target}.md"
    dup=0
    for e in "${epics_to_check[@]:-}"; do [ "$e" = "$epic_target" ] && dup=1; done
    [ "$dup" = "0" ] && epics_to_check+=("$epic_target")
  done <<< "$STAGED"

  board_blocked=0
  for epic in "${epics_to_check[@]:-}"; do
    [ -z "$epic" ] && continue
    [ -f "$epic" ] || continue
    # 用 if/else 捕获真实退出码：`if ! cmd` 会把 1 反转成 0，丢失「漂移」信号。
    if python3 "$ROOT/scripts/render-epic-board.py" "$epic" --check >&2; then
      :
    else
      [ "$?" = "1" ] && board_blocked=1
    fi
  done
  if [ "$board_blocked" = "1" ]; then
    echo "" >&2
    echo "❌ Epic 看板与子 Plan 事实漂移，已拦截 commit。" >&2
    echo "   刷新：python3 scripts/render-epic-board.py <epic> --write" >&2
    echo "   跳过（不推荐）：git commit --no-verify" >&2
    exit 1
  fi
fi

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
