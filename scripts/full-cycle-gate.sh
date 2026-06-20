#!/usr/bin/env bash
# 全流程机械门禁：Epic 优先，对齐 full-cycle.json 五阶段
# 用法：
#   ./scripts/full-cycle-gate.sh
#   ./scripts/full-cycle-gate.sh --epic Plans/Epic/2026-06-20-新版工作空间.md
#   ./scripts/full-cycle-gate.sh --project 新版工作空间
#   ./scripts/full-cycle-gate.sh --json --epic Plans/Epic/xxx.md
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EPIC=""
PROJECT=""
JSON=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --epic) EPIC="${2:-}"; shift 2 ;;
    --project) PROJECT="${2:-}"; shift 2 ;;
    --json) JSON=1; shift ;;
    -h|--help)
      echo "Usage: full-cycle-gate.sh [--epic Plans/Epic/xxx.md] [--project 模块名] [--json]"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

read_fm() {
  awk -v key="$1" '
    BEGIN { in_fm=0 }
    /^---$/ { in_fm++; next }
    in_fm==1 && $0 ~ "^" key ":" {
      sub("^" key ":[[:space:]]*", "")
      gsub(/"/, "")
      print
      exit
    }
  ' "$2"
}

read_plan_key() {
  local f="$1" key="$2"
  awk -v k="$key" '
    /^plans:/ { in_p=1; next }
    in_p && /^[^ ]/ { exit }
    in_p && $0 ~ "^[[:space:]]+" k ":" {
      sub(/^[[:space:]]*[a-z_]+:[[:space:]]*/, "")
      gsub(/"/, "")
      print
      exit
    }
  ' "$f" | tr -d ' '
}

resolve_path() {
  local p="$1"
  [[ "$p" == /* ]] && echo "$p" || p="$ROOT/$p"
  [[ "$p" == *.md ]] || p="${p}.md"
  echo "$p"
}

find_epic() {
  if [[ -n "$EPIC" ]]; then
    resolve_path "$EPIC"
    return
  fi
  shopt -s nullglob
  local f best=""
  for f in "$ROOT"/Plans/Epic/*.md; do
    [[ "$(basename "$f")" == .* ]] && continue
    if [[ -n "$PROJECT" && "$(basename "$f")" == *"$PROJECT"* ]]; then
      echo "$f"
      return
    fi
    [[ -z "$best" ]] && best="$f"
  done
  [[ -n "$best" ]] && echo "$best"
}

wbs_slice_done() {
  local f="$1" n="$2"
  local line
  line="$(sed -n '/^```$/,/^```$/p' "$f" | grep -E "^\[[ xX~]\][[:space:]]*${n}\.[[:space:]]" | head -1 || true)"
  [[ -z "$line" ]] && return 1
  [[ "$line" =~ ^\[[xX]\] ]] && return 0
  return 1
}

wbs_range_done() {
  local f="$1" start="$2" end="$3" n
  for ((n=start; n<=end; n++)); do
    wbs_slice_done "$f" "$n" || return 1
  done
  return 0
}

emit_json() {
  python3 - "$@" <<'PY'
import json, sys
print(json.dumps(json.loads(sys.argv[1]), ensure_ascii=False, indent=2))
PY
}

EPIC_FILE="$(find_epic || true)"
blockers=()
plans_found=()
current_state="requirement"
recommended_skill="requirement-analyst"
next_state="architecture"
gate_development="SKIP"

if [[ -z "$EPIC_FILE" || ! -f "$EPIC_FILE" ]]; then
  blockers+=("无 Epic plan（Plans/Epic/）；须先 bootstrap Epic")
  current_state="requirement"
  recommended_skill="full-cycle-assistant / requirement-analyst"
else
  epic_rel="${EPIC_FILE#"$ROOT"/}"
  biz="$(read_fm 含业务逻辑 "$EPIC_FILE")"
  p0="$(read_fm p0_open "$EPIC_FILE")"
  p0="${p0:-0}"
  lc="$(read_fm lifecycle_state "$EPIC_FILE")"

  req_raw="$(read_plan_key "$EPIC_FILE" requirement)"
  arch_raw="$(read_plan_key "$EPIC_FILE" architecture)"
  dev_raw="$(read_plan_key "$EPIC_FILE" development)"
  test_raw="$(read_plan_key "$EPIC_FILE" test)"
  deploy_raw="$(read_plan_key "$EPIC_FILE" deploy)"

  [[ -n "$req_raw" && "$req_raw" != "null" ]] && plans_found+=("requirement:$req_raw")
  [[ -n "$arch_raw" && "$arch_raw" != "null" ]] && plans_found+=("architecture:$arch_raw")
  [[ -n "$dev_raw" && "$dev_raw" != "null" ]] && plans_found+=("development:$dev_raw")
  [[ -n "$test_raw" && "$test_raw" != "null" ]] && plans_found+=("test:$test_raw")
  [[ -n "$deploy_raw" && "$deploy_raw" != "null" ]] && plans_found+=("deploy:$deploy_raw")

  # --- requirement ---
  if [[ -z "$req_raw" || "$req_raw" == "null" ]]; then
    blockers+=("Epic plans.requirement 未填")
    current_state="requirement"
    recommended_skill="requirement-analyst"
    next_state="architecture"
  else
    req_file="$(resolve_path "$req_raw")"
    if [[ ! -f "$req_file" ]]; then
      blockers+=("需求 plan 不存在: $req_raw")
      current_state="requirement"
      recommended_skill="requirement-analyst"
    else
      req_status="$(read_fm status "$req_file")"
      req_p0="$(read_fm p0_open "$req_file")"
      req_p0="${req_p0:-$p0}"
      [[ "$req_p0" =~ ^[0-9]+$ ]] || req_p0=0
      grep -qE '验收标准|## 九、验收标准' "$req_file" || blockers+=("需求 plan 缺少验收标准章节")
      [[ "$req_status" == "已采纳" ]] || blockers+=("需求 status 须为「已采纳」（当前: ${req_status:-无}）")
      [[ "$req_p0" -eq 0 ]] || blockers+=("p0_open=${req_p0}，须闭环 P0")
      if [[ ${#blockers[@]} -gt 0 ]]; then
        current_state="requirement"
        recommended_skill="requirement-analyst"
        next_state="architecture"
      fi
    fi
  fi

  # --- architecture ---
  if [[ ${#blockers[@]} -eq 0 && "$biz" == "是" ]]; then
    if [[ -z "$arch_raw" || "$arch_raw" == "null" ]]; then
      blockers+=("含业务逻辑=是 但 Epic plans.architecture 未填")
      current_state="architecture"
      recommended_skill="architecture-design-assistant"
      next_state="development"
    else
      arch_file="$(resolve_path "$arch_raw")"
      if [[ ! -f "$arch_file" ]]; then
        blockers+=("技术方案 plan 不存在: $arch_raw")
        current_state="architecture"
        recommended_skill="architecture-design-assistant"
      else
        arch_status="$(read_fm status "$arch_file")"
        [[ "$arch_status" == "已采纳" ]] || blockers+=("技术方案 status 须为「已采纳」（当前: ${arch_status:-无}）")
        if [[ ${#blockers[@]} -gt 0 ]]; then
          current_state="architecture"
          recommended_skill="architecture-design-assistant"
          next_state="development"
        fi
      fi
    fi
  fi

  # --- development ---
  if [[ ${#blockers[@]} -eq 0 ]]; then
    if [[ -z "$dev_raw" || "$dev_raw" == "null" ]]; then
      blockers+=("Epic plans.development 未填")
      current_state="development"
      recommended_skill="task-splitter"
      next_state="test"
    else
      dev_file="$(resolve_path "$dev_raw")"
      if [[ ! -f "$dev_file" ]]; then
        blockers+=("功能开发 plan 不存在: $dev_raw")
        current_state="development"
        recommended_skill="task-splitter"
      else
        gate_development="$(bash "$ROOT/scripts/plan-gate-check.sh" "$dev_file" --stage development 2>&1 || true)"
        [[ "$gate_development" == OK ]] || blockers+=("plan-gate-check: ${gate_development#BLOCKED:}")
        wbs_range_done "$EPIC_FILE" 1 10 || blockers+=("WBS 切片 1–10 未全部完成")
        if [[ ${#blockers[@]} -gt 0 ]]; then
          current_state="development"
          recommended_skill="task-splitter / feature-dev-assistant"
          next_state="test"
        fi
      fi
    fi
  fi

  # --- test ---
  if [[ ${#blockers[@]} -eq 0 ]]; then
    if [[ -z "$test_raw" || "$test_raw" == "null" ]]; then
      blockers+=("Epic plans.test 未填；须 test-generator 产出")
      current_state="test"
      recommended_skill="test-generator"
      next_state="deploy"
    else
      test_file="$(resolve_path "$test_raw")"
      [[ -f "$test_file" ]] || blockers+=("测试 plan 不存在: $test_raw")
      wbs_slice_done "$EPIC_FILE" 11 || blockers+=("WBS 切片 11（单元/集成测试）未完成")
      if [[ ${#blockers[@]} -gt 0 ]]; then
        current_state="test"
        recommended_skill="test-generator"
        next_state="deploy"
      fi
    fi
  fi

  # --- deploy ---
  if [[ ${#blockers[@]} -eq 0 ]]; then
    if [[ -z "$deploy_raw" || "$deploy_raw" == "null" ]]; then
      blockers+=("Epic plans.deploy 未填；须 deployment-assistant 产出")
      current_state="deploy"
      recommended_skill="deployment-assistant"
      next_state="done"
    else
      deploy_file="$(resolve_path "$deploy_raw")"
      [[ -f "$deploy_file" ]] || blockers+=("部署 plan 不存在: $deploy_raw")
      wbs_slice_done "$EPIC_FILE" 13 || blockers+=("WBS 切片 13（发布检查）未完成")
      wbs_slice_done "$EPIC_FILE" 14 || blockers+=("WBS 切片 14（线上冒烟）未完成")
      if [[ ${#blockers[@]} -gt 0 ]]; then
        current_state="deploy"
        recommended_skill="deployment-assistant"
        next_state="done"
      else
        current_state="done"
        recommended_skill="（归档 Epic / WBS 15）"
        next_state="done"
      fi
    fi
  fi

  # lifecycle_state 提示（不覆盖机械结论，仅作对照）
  lc_hint="$lc"
fi

if [[ "$JSON" -eq 1 ]]; then
  bl_json="$(printf '%s\n' "${blockers[@]:-}" | python3 -c 'import json,sys; print(json.dumps([l for l in sys.stdin.read().splitlines() if l.strip()], ensure_ascii=False))')"
  pf_json="$(printf '%s\n' "${plans_found[@]:-}" | python3 -c 'import json,sys; print(json.dumps([l for l in sys.stdin.read().splitlines() if l.strip()], ensure_ascii=False))')"
  payload="$(cat <<EOF
{
  "epic": "${epic_rel:-}",
  "lifecycle_state_hint": "${lc_hint:-}",
  "current_state": "$current_state",
  "next_state": "$next_state",
  "recommended_skill": "$recommended_skill",
  "gate_development": "$gate_development",
  "blockers": $bl_json,
  "plans_found": $pf_json
}
EOF
)"
  emit_json "$payload"
  exit 0
fi

echo "# full-cycle-gate 机械门禁"
echo "# vault: $ROOT"
echo "# generated: $(date +%Y-%m-%dT%H:%M:%S)"
echo ""
if [[ -n "${epic_rel:-}" ]]; then
  echo "epic: $epic_rel"
  echo "lifecycle_state_hint: ${lc_hint:-（无）}"
  echo "gate_development: $gate_development"
  echo ""
fi
echo "current_state: $current_state"
echo "next_state: $next_state"
echo "recommended_skill: $recommended_skill"
echo ""
echo "plans_found:"
if [[ ${#plans_found[@]} -eq 0 ]]; then
  echo "  （无）"
else
  for p in "${plans_found[@]}"; do
    echo "  - $p"
  done
fi
echo ""
echo "blockers:"
if [[ ${#blockers[@]} -eq 0 ]]; then
  echo "  （无 — 全流程门禁通过）"
else
  for b in "${blockers[@]}"; do
    echo "  - $b"
  done
fi
echo ""
echo "report: 📌 当前阶段：[$current_state] | 下一个阶段：[$next_state / $recommended_skill] | 如需中断：/resume plan=${epic_rel:-Plans/代码重构/2026-06-20-全流程闭环改造计划-最终版.md}"
