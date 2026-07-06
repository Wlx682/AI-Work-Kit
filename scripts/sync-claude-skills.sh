#!/usr/bin/env bash
# sync-claude-skills.sh — Skill 多端一致性校验 / 同步
#
# 用法：
#   ./scripts/sync-claude-skills.sh             # 默认 --check：校验 .cursor / .claude / .codex / Skills，有差异 exit 1
#   ./scripts/sync-claude-skills.sh --sync      # 强制以 .cursor/skills 为基准刷新 .claude / .codex 及全局副本
#   ./scripts/sync-claude-skills.sh --check     # 同默认
#
# 多端约定：
#   .cursor/skills/<name>/SKILL.md  → Cursor Agent 入口（agent-readable stub）
#   .claude/skills/<name>/SKILL.md  → Claude Code 入口（gitignore 中，由本脚本生成）
#   .codex/skills/<name>/SKILL.md   → Codex 入口（gitignore 中，由本脚本生成）
#   Skills/<name>.md                → 人类阅读真理源（下划线，dash → underscore）
#
# 校验三项：
#   1. .cursor / .claude / .codex 名称集合一致
#   2. 同名 Skill 在三端内容字节级一致
#   3. 每个 Skill 在 Skills/ 有对应真理源文件存在
#
# 注意：Skills/<name>.md 的内容**不**与 stub 强制字节相等（master 是长文档，stub 是短入口）；只检查存在性。
# --sync 会清理项目生成端中不在 .cursor/skills 的旧目录；全局副本只覆盖项目同名，保留用户自装。

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CURSOR_DIR="$ROOT/.cursor/skills"
CLAUDE_DIR="$ROOT/.claude/skills"
CODEX_DIR="$ROOT/.codex/skills"
SKILLS_DIR="$ROOT/Skills"

MODE="${1:---check}"

case "$MODE" in
  --check|--sync) ;;
  -h|--help)
    head -n 20 "$0" | sed -n '2,18p' | sed 's/^# \?//'
    exit 0 ;;
  *)
    echo "未知参数：$MODE（用 --check 或 --sync）" >&2
    exit 2 ;;
esac

mkdir -p "$CLAUDE_DIR" "$CODEX_DIR"

errors=0

cursor_names=$(find "$CURSOR_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort || true)
claude_names=$(find "$CLAUDE_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort || true)
codex_names=$(find "$CODEX_DIR" -mindepth 1 -maxdepth 1 -type d ! -name '.system' -exec basename {} \; 2>/dev/null | sort || true)

# 1. 名称集合
only_cursor=$(comm -23 <(echo "$cursor_names") <(echo "$claude_names") || true)
only_claude=$(comm -13 <(echo "$cursor_names") <(echo "$claude_names") || true)
only_cursor_codex=$(comm -23 <(echo "$cursor_names") <(echo "$codex_names") || true)
only_codex=$(comm -13 <(echo "$cursor_names") <(echo "$codex_names") || true)

if [ -n "$only_cursor" ]; then
  echo "⚠️ 仅 .cursor/skills 有，.claude/skills 缺：" >&2
  echo "$only_cursor" | sed 's/^/  - /' >&2
  errors=$((errors+1))
fi
if [ -n "$only_claude" ]; then
  echo "⚠️ 仅 .claude/skills 有，.cursor/skills 缺：" >&2
  echo "$only_claude" | sed 's/^/  - /' >&2
  errors=$((errors+1))
fi
if [ -n "$only_cursor_codex" ]; then
  echo "⚠️ 仅 .cursor/skills 有，.codex/skills 缺：" >&2
  echo "$only_cursor_codex" | sed 's/^/  - /' >&2
  errors=$((errors+1))
fi
if [ -n "$only_codex" ]; then
  echo "⚠️ 仅 .codex/skills 有，.cursor/skills 缺：" >&2
  echo "$only_codex" | sed 's/^/  - /' >&2
  errors=$((errors+1))
fi

# 2. 同名 Skill 内容比对
common=$(comm -12 <(echo "$cursor_names") <(echo "$claude_names") | comm -12 - <(echo "$codex_names") || true)
diff_skills=""
for name in $common; do
  c="$CURSOR_DIR/$name/SKILL.md"
  l="$CLAUDE_DIR/$name/SKILL.md"
  x="$CODEX_DIR/$name/SKILL.md"
  if [ ! -f "$c" ] || [ ! -f "$l" ] || [ ! -f "$x" ]; then
    echo "⚠️ $name: SKILL.md 文件缺失" >&2
    errors=$((errors+1))
    continue
  fi
  if ! diff -q "$c" "$l" > /dev/null 2>&1 || ! diff -q "$c" "$x" > /dev/null 2>&1; then
    diff_skills="$diff_skills $name"
    errors=$((errors+1))
  fi
done

if [ -n "$diff_skills" ]; then
  echo "✗ 内容不一致的 Skill：" >&2
  for n in $diff_skills; do
    echo "  --- $n ---" >&2
    if ! diff -q "$CURSOR_DIR/$n/SKILL.md" "$CLAUDE_DIR/$n/SKILL.md" > /dev/null 2>&1; then
      echo "  .cursor ↔ .claude" >&2
      diff -u "$CURSOR_DIR/$n/SKILL.md" "$CLAUDE_DIR/$n/SKILL.md" | head -n 30 >&2 || true
    fi
    if ! diff -q "$CURSOR_DIR/$n/SKILL.md" "$CODEX_DIR/$n/SKILL.md" > /dev/null 2>&1; then
      echo "  .cursor ↔ .codex" >&2
      diff -u "$CURSOR_DIR/$n/SKILL.md" "$CODEX_DIR/$n/SKILL.md" | head -n 30 >&2 || true
    fi
  done
fi

# 3. Skills/ 真理源存在性
missing_master=""
for name in $cursor_names; do
  master_underscore="$SKILLS_DIR/$(echo "$name" | tr '-' '_').md"
  master_dash="$SKILLS_DIR/$name.md"
  if [ ! -f "$master_underscore" ] && [ ! -f "$master_dash" ]; then
    missing_master="$missing_master $name"
    errors=$((errors+1))
  fi
done

if [ -n "$missing_master" ]; then
  echo "⚠️ Skills/ 缺真理源文件：" >&2
  for n in $missing_master; do
    echo "  - $n （期望 Skills/$(echo "$n" | tr '-' '_').md 或 Skills/$n.md）" >&2
  done
fi

# 终判
if [ "$errors" -gt 0 ]; then
  echo "" >&2
  echo "❌ 多端校验失败：$errors 项差异。" >&2
  if [ "$MODE" != "--sync" ]; then
    echo "   修复建议：" >&2
    echo "     - 仅 .cursor 有 → 复制到 .claude / .codex 对应目录" >&2
    echo "     - 内容不一致 → 选 .cursor 为基准修目标端（或反之），改完跑 --check 验证" >&2
    echo "     - Skills/ 缺真理源 → 创建对应 Skills/<name>.md" >&2
    echo "     - 仅当确认 .cursor 是正确基准时，可用 ./scripts/sync-claude-skills.sh --sync 强制刷新生成端" >&2
    exit 1
  fi
  echo "   --sync 模式：以 .cursor 为基准强制覆盖 .claude / .codex 及全局副本。" >&2
else
  echo "✓ 多端一致：$(echo "$common" | wc -w | tr -d ' ') 个 Skill"
fi

if [ "$MODE" = "--sync" ]; then
  # 1) 项目内 .cursor → .claude / .codex
  for d in "$CURSOR_DIR"/*/; do
    name=$(basename "$d")
    rm -rf "$CLAUDE_DIR/$name"
    cp -r "$d" "$CLAUDE_DIR/$name"
    rm -rf "$CODEX_DIR/$name"
    cp -r "$d" "$CODEX_DIR/$name"
  done
  echo "已同步 .cursor → .claude / .codex"

  # 1.5) 清理项目生成端旧 Skill，保证 --sync 后 --check 可直接通过。
  # 全局目录不做清理；那里可能包含用户自装 Skill，只覆盖项目同名。
  cleaned=0
  for d in "$CLAUDE_DIR"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    if ! printf '%s\n' "$cursor_names" | grep -Fxq "$name"; then
      rm -rf "$d"
      cleaned=$((cleaned + 1))
    fi
  done
  for d in "$CODEX_DIR"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    [ "$name" = ".system" ] && continue
    if ! printf '%s\n' "$cursor_names" | grep -Fxq "$name"; then
      rm -rf "$d"
      cleaned=$((cleaned + 1))
    fi
  done
  if [ "$cleaned" -gt 0 ]; then
    echo "已清理项目生成端旧 Skill（${cleaned} 项）"
  fi

  # 2) 项目生成端 → 全局 ~/.claude/skills 与 ~/.codex/skills（仅覆盖项目内 Skill 名称，保留用户自装的）
  GLOBAL_CLAUDE_DIR="$HOME/.claude/skills"
  GLOBAL_CODEX_DIR="$HOME/.codex/skills"
  mkdir -p "$GLOBAL_CLAUDE_DIR" "$GLOBAL_CODEX_DIR"
  synced=0
  for d in "$CLAUDE_DIR"/*/; do
    name=$(basename "$d")
    rm -rf "$GLOBAL_CLAUDE_DIR/$name"
    cp -r "$d" "$GLOBAL_CLAUDE_DIR/$name"
    synced=$((synced + 1))
  done
  echo "已同步 .claude → ${GLOBAL_CLAUDE_DIR}（覆盖 ${synced} 项）"

  synced=0
  for d in "$CODEX_DIR"/*/; do
    name=$(basename "$d")
    [ "$name" = ".system" ] && continue
    rm -rf "$GLOBAL_CODEX_DIR/$name"
    cp -r "$d" "$GLOBAL_CODEX_DIR/$name"
    synced=$((synced + 1))
  done
  echo "已同步 .codex → ${GLOBAL_CODEX_DIR}（覆盖 ${synced} 项）"

  # 3) 提示全局中存在但项目里没有的 Skill（用户自装 / 系统内置，不动）
  project_names=$(find "$CURSOR_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort || true)
  global_claude_names=$(find "$GLOBAL_CLAUDE_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort || true)
  claude_extras=$(comm -23 <(echo "$global_claude_names") <(echo "$project_names") || true)
  global_codex_names=$(find "$GLOBAL_CODEX_DIR" -mindepth 1 -maxdepth 1 -type d ! -name '.system' -exec basename {} \; 2>/dev/null | sort || true)
  codex_extras=$(comm -23 <(echo "$global_codex_names") <(echo "$project_names") || true)
  extras=""
  if [ -n "$claude_extras" ]; then
    extras="${extras}$(printf '%s\n' "$claude_extras" | sed 's/^/Claude: /')"$'\n'
  fi
  if [ -n "$codex_extras" ]; then
    extras="${extras}$(printf '%s\n' "$codex_extras" | sed 's/^/Codex: /')"$'\n'
  fi
  if [ -n "$extras" ]; then
    echo ""
    echo "ℹ️  全局保留用户自装 Skill（未触碰）："
    printf '%s\n' "$extras" | sed '/^$/d; s/^/  · /'
  fi
fi
