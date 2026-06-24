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

# 8. skill_run 反馈块校验（Sprint 1 试点）
#    协议：Contexts/决策/Skill反馈协议.md
#    试点期：仅对 Plans/需求分析/ 强制要求块存在；其它路径仅在块存在时校验合法性
SKILL_RUN_FLAG=""
case "$PLAN" in
  *Plans/需求分析/*|*/Plans/需求分析/*)
    SKILL_RUN_FLAG="--require"
    ;;
esac
if command -v python3 >/dev/null 2>&1 && [[ -f "$ROOT/scripts/validate-skill-run.py" ]]; then
  if ! python3 "$ROOT/scripts/validate-skill-run.py" $SKILL_RUN_FLAG "$PLAN" >&2; then
    fail "skill_run 校验未通过（见上方日志）"
  fi
fi

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
