#!/usr/bin/env bash
# 功能 / 子任务 plan 开工门禁
# 用法：bash scripts/plan-gate-check.sh <plan.md> [--stage development]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLAN="${1:-}"
STAGE="${2:-development}"
if [[ "$STAGE" == "--stage" ]]; then
  STAGE="${3:-development}"
fi

fail() {
  echo "BLOCKED:$1" >&2
  echo "BLOCKED:$1"
  exit 1
}

ok() {
  echo "OK"
  exit 0
}

[[ -n "$PLAN" ]] || fail "缺少 plan 路径"
[[ -f "$PLAN" ]] || fail "plan 文件不存在: $PLAN"

# 1. frontmatter
fm_count="$(grep -c '^---$' "$PLAN" || true)"
[[ "$fm_count" -ge 2 ]] || fail "缺少 YAML frontmatter"

read_fm() {
  awk -v key="$1" '
    BEGIN { in_fm=0 }
    /^---$/ { in_fm++; next }
    in_fm==1 && $0 ~ "^" key ":" {
      sub("^" key ":[[:space:]]*", "")
      print
      exit
    }
  ' "$PLAN"
}

resolve_path() {
  local p="$1"
  [[ "$p" == /* ]] && echo "$p" || p="$ROOT/$p"
  [[ "$p" == *.md ]] || p="${p}.md"
  echo "$p"
}

# 7. 子任务 parent
bn="$(basename "$PLAN")"
if [[ "$bn" == *子任务* ]]; then
  parent="$(read_fm parent)"
  [[ -n "$parent" ]] || fail "子任务 plan 缺少 parent:"
  [[ -f "$(resolve_path "$parent")" ]] || fail "parent plan 不存在: $parent"
fi

# 6. epic 链接
epic="$(read_fm epic)"
if [[ -n "$epic" ]]; then
  [[ -f "$(resolve_path "$epic")" ]] || fail "epic plan 不存在: $epic"
fi

# 8. skill_run 反馈块校验
#    协议：Contexts/决策/Skill反馈协议.md
#    全量强制：所有 plan 通过门禁时都必须在末尾包含合法 skill_run 块
SKILL_RUN_FLAG="--require"
if command -v python3 >/dev/null 2>&1 && [[ -f "$ROOT/scripts/validate-skill-run.py" ]]; then
  if ! python3 "$ROOT/scripts/validate-skill-run.py" $SKILL_RUN_FLAG "$PLAN" >&2; then
    fail "skill_run 校验未通过（见上方日志）"
  fi
fi

# 8b. 文档脚本引用一致性（防止文档说 .sh、实际是 .py 这类漂移）
#     协议：见 Contexts/决策/孤立反馈记录.md → scripts/doc-script-refs-check.py
if command -v python3 >/dev/null 2>&1 && [[ -f "$ROOT/scripts/doc-script-refs-check.py" ]]; then
  if ! python3 "$ROOT/scripts/doc-script-refs-check.py" --quiet "$PLAN" >&2; then
    fail "文档脚本引用校验未通过（见上方日志）"
  fi
fi

# 10. Epic 看板 SLICE_RE 解析预检
#     约束：fenced checklist 行必须能被 kanban-server.py 的 SLICE_RE 匹配
#     真理源：scripts/kanban-server.py SLICE_RE（importlib 复用，避免正则漂移）
case "$PLAN" in
  */Plans/Epic/*|*Plans/Epic/*)
    if command -v python3 >/dev/null 2>&1 && [[ -f "$ROOT/scripts/kanban-server.py" ]]; then
      python3 - "$ROOT" "$PLAN" >&2 <<'PY' || fail "Epic 看板 checklist 解析失败（见上方日志）"
import importlib.util, pathlib, re, sys
root = pathlib.Path(sys.argv[1])
plan = pathlib.Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("kanban_server", root / "scripts" / "kanban-server.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
text = plan.read_text(encoding="utf-8")
in_fence = False
bad = []
for ln, line in enumerate(text.splitlines(), 1):
    if line.strip() == "```":
        in_fence = not in_fence
        continue
    if not in_fence:
        continue
    if re.match(r"^\s*\[[^\]]*\]\s*\S", line) and not mod.SLICE_RE.match(line):
        bad.append((ln, line.rstrip()))
if bad:
    print(f"[epic-slice-check] {len(bad)} 行 checklist 无法被看板解析（kanban-server.py SLICE_RE）:", file=sys.stderr)
    for ln, l in bad[:5]:
        print(f"  L{ln}: {l}", file=sys.stderr)
    print("  约束见 Templates/Epic模板-client-dev.md §三 注释。", file=sys.stderr)
    sys.exit(1)
PY
    fi
    ;;
esac

# 9. Epic 看板新鲜度：不在此校验。
#    §三 看板是子 Plan 事实的只读派生，由 pre-commit（scripts/pre-commit-relations.sh
#    → render-epic-board.py --check）在提交时统一把关。
#    ⚠️ 不得在此调用 render-epic-board.py：它会跑 workflow-gate.sh，而 development 阶段
#       的 planGateCheck 又回调本脚本，形成无限递归。派生渲染的唯一门禁入口是 pre-commit。
#    协议：Contexts/决策/母子plan投影规则.md

# 仅对功能开发 plan 做完整门禁（路径在 Plans/功能开发/）
case "$PLAN" in
  *Plans/功能开发/*|*/Plans/功能开发/*)
    ;;
  *)
    ok
    ;;
esac

strip_wikilink() {
  local p="$1"
  p="${p%%]]*}"
  p="${p%%\`*}"
  echo "$p"
}

# 2. §一 需求链接
req_path=""
while IFS= read -r line; do
  if [[ "$line" =~ (Plans/需求分析/[^]]+) ]]; then
    req_path="$(strip_wikilink "${BASH_REMATCH[1]}")"
    break
  fi
done < <(sed -n '/^## 一、需求分析/,/^## 二/p' "$PLAN" | head -n 40)

if [[ -z "$req_path" ]]; then
  req_path="$(read_fm requirement_plan)"
fi

[[ -n "$req_path" ]] || fail "§一 缺少 Plans/需求分析/ 链接"
req_file="$(resolve_path "$req_path")"
[[ -f "$req_file" ]] || fail "需求 plan 不存在: $req_path"

# 3. 需求 plan 非空 + 验收标准
req_chars="$(wc -m < "$req_file" | tr -d ' ')"
[[ "$req_chars" -ge 500 ]] || fail "需求 plan 内容不足 500 字（当前 ${req_chars}）"
grep -qE '验收标准|## 九、验收标准' "$req_file" || fail "需求 plan 缺少「验收标准」章节"

# 4. p0_open
p0="$(read_fm p0_open)"
if [[ -z "$p0" && -f "$req_file" ]]; then
  p0="$(awk -v f="$req_file" 'BEGIN{in_fm=0} FNR==NR && /^---$/{in_fm++; next} FNR==NR && in_fm==1 && /^p0_open:/{sub(/^p0_open:[[:space:]]*/,""); print; exit}' "$req_file")"
fi
if [[ -z "$p0" && -n "$epic" ]]; then
  p0="$(awk -v f="$(resolve_path "$epic")" 'BEGIN{in_fm=0} FNR==NR && /^---$/{in_fm++; next} FNR==NR && in_fm==1 && /^p0_open:/{sub(/^p0_open:[[:space:]]*/,""); print; exit}' "$(resolve_path "$epic")")"
fi
p0="${p0:-0}"
if [[ "$STAGE" == "development" && "$p0" =~ ^[0-9]+$ && "$p0" -gt 0 ]]; then
  fail "p0_open=${p0}，开发阶段被拦截"
fi

# 5. 含业务逻辑 → 技术方案已采纳
biz="$(read_fm 含业务逻辑)"
if [[ -z "$biz" ]]; then
  biz="$(grep -E '^\*\*含业务逻辑\*\*' "$PLAN" | head -1 | sed 's/.*：//' | tr -d ' ' || true)"
fi
if [[ "$biz" == "是" && "$STAGE" == "development" ]]; then
  arch_path=""
  if [[ -n "$epic" && -f "$(resolve_path "$epic")" ]]; then
    arch_path="$(awk -v f="$(resolve_path "$epic")" '
      BEGIN { in_fm=0 }
      FNR==NR && /^---$/{ in_fm++; next }
      FNR==NR && in_fm==1 && /^[[:space:]]*architecture:[[:space:]]*/ {
        sub(/^[[:space:]]*architecture:[[:space:]]*/, "")
        gsub(/"/, "")
        if ($0 != "null" && $0 != "") print
        exit
      }
    ' "$(resolve_path "$epic")")"
  fi
  if [[ -z "$arch_path" ]]; then
    while IFS= read -r line; do
      if [[ "$line" =~ (Plans/技术方案/[^]]+) ]]; then
        arch_path="$(strip_wikilink "${BASH_REMATCH[1]}")"
        break
      fi
      if [[ "$line" =~ (Plans/客户端技术方案/[^]]+) ]]; then
        arch_path="$(strip_wikilink "${BASH_REMATCH[1]}")"
        break
      fi
      if [[ "$line" =~ (Plans/服务端技术方案/[^]]+) ]]; then
        arch_path="$(strip_wikilink "${BASH_REMATCH[1]}")"
        break
      fi
    done < "$PLAN"
  fi
  [[ -n "$arch_path" ]] || fail "含业务逻辑=是 但缺少技术方案 plan 链接"
  arch_file="$(resolve_path "$arch_path")"
  [[ -f "$arch_file" ]] || fail "技术方案 plan 不存在: $arch_path"
  arch_status="$(awk 'BEGIN{in_fm=0} /^---$/{in_fm++; next} in_fm==1 && /^status:/{sub(/^status:[[:space:]]*/,""); print; exit}' "$arch_file")"
  [[ "$arch_status" == "已采纳" ]] || fail "技术方案 status 须为「已采纳」（当前: ${arch_status:-无}）"
fi

ok
