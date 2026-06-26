#!/usr/bin/env bash
# sync-claude-skills.sh — Skill 三端一致性校验 / 同步
#
# 用法：
#   ./scripts/sync-claude-skills.sh             # 默认 --check：校验 .cursor / .claude / Skills 三端，有差异 exit 1
#   ./scripts/sync-claude-skills.sh --sync      # 强制以 .cursor/skills 为基准刷新 .claude/skills（旧行为）
#   ./scripts/sync-claude-skills.sh --check     # 同默认
#
# 三端约定：
#   .cursor/skills/<name>/SKILL.md  → Cursor Agent 入口（agent-readable stub）
#   .claude/skills/<name>/SKILL.md  → Claude Code 入口（gitignore 中，由本脚本生成）
#   Skills/<name>.md                → 人类阅读真理源（下划线，dash → underscore）
#
# 校验三项：
#   1. .cursor 与 .claude 名称集合一致
#   2. 同名 Skill 在两端内容字节级一致
#   3. 每个 Skill 在 Skills/ 有对应真理源文件存在
#
# 注意：Skills/<name>.md 的内容**不**与 stub 强制字节相等（master 是长文档，stub 是短入口）；只检查存在性。

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CURSOR_DIR="$ROOT/.cursor/skills"
CLAUDE_DIR="$ROOT/.claude/skills"
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

mkdir -p "$CLAUDE_DIR"

errors=0

cursor_names=$(find "$CURSOR_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort || true)
claude_names=$(find "$CLAUDE_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort || true)

# 1. 名称集合
only_cursor=$(comm -23 <(echo "$cursor_names") <(echo "$claude_names") || true)
only_claude=$(comm -13 <(echo "$cursor_names") <(echo "$claude_names") || true)

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

# 2. 同名 Skill 内容比对
common=$(comm -12 <(echo "$cursor_names") <(echo "$claude_names") || true)
diff_skills=""
for name in $common; do
  c="$CURSOR_DIR/$name/SKILL.md"
  l="$CLAUDE_DIR/$name/SKILL.md"
  if [ ! -f "$c" ] || [ ! -f "$l" ]; then
    echo "⚠️ $name: SKILL.md 文件缺失" >&2
    errors=$((errors+1))
    continue
  fi
  if ! diff -q "$c" "$l" > /dev/null 2>&1; then
    diff_skills="$diff_skills $name"
    errors=$((errors+1))
  fi
done

if [ -n "$diff_skills" ]; then
  echo "✗ 内容不一致的 Skill：" >&2
  for n in $diff_skills; do
    echo "  --- $n ---" >&2
    diff -u "$CURSOR_DIR/$n/SKILL.md" "$CLAUDE_DIR/$n/SKILL.md" | head -n 30 >&2 || true
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
  echo "❌ 三端校验失败：$errors 项差异。" >&2
  if [ "$MODE" != "--sync" ]; then
    echo "   修复建议：" >&2
    echo "     - 仅 .cursor 有 → 复制到 .claude 对应目录" >&2
    echo "     - 内容不一致 → 选 .cursor 为基准修 .claude（或反之），改完跑 --check 验证" >&2
    echo "     - Skills/ 缺真理源 → 创建对应 Skills/<name>.md" >&2
    echo "     - 仅当确认 .cursor 是正确基准时，可用 ./scripts/sync-claude-skills.sh --sync 强制刷新 .claude" >&2
    exit 1
  fi
  echo "   --sync 模式：以 .cursor 为基准强制覆盖 .claude 及全局副本。" >&2
else
  echo "✓ 三端一致：$(echo "$common" | wc -w | tr -d ' ') 个 Skill"
fi

if [ "$MODE" = "--sync" ]; then
  # 1) 项目内 .cursor → .claude
  for d in "$CURSOR_DIR"/*/; do
    name=$(basename "$d")
    rm -rf "$CLAUDE_DIR/$name"
    cp -r "$d" "$CLAUDE_DIR/$name"
  done
  echo "已同步 .cursor → .claude"

  # 2) 项目 .claude → 全局 ~/.claude/skills（仅覆盖项目内 Skill 名称，保留用户自装的）
  GLOBAL_DIR="$HOME/.claude/skills"
  mkdir -p "$GLOBAL_DIR"
  synced=0
  for d in "$CLAUDE_DIR"/*/; do
    name=$(basename "$d")
    rm -rf "$GLOBAL_DIR/$name"
    cp -r "$d" "$GLOBAL_DIR/$name"
    synced=$((synced + 1))
  done
  echo "已同步 .claude → ${GLOBAL_DIR}（覆盖 ${synced} 项）"

  # 3) 提示全局中存在但项目里没有的 Skill（用户自装，不动）
  global_names=$(find "$GLOBAL_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort || true)
  project_names=$(find "$CLAUDE_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort || true)
  extras=$(comm -23 <(echo "$global_names") <(echo "$project_names") || true)
  if [ -n "$extras" ]; then
    echo ""
    echo "ℹ️  全局保留用户自装 Skill（未触碰）："
    echo "$extras" | sed 's/^/  · /'
  fi
fi
