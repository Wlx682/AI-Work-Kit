#!/usr/bin/env bash
# 通用工作流机械门禁：读工具中性蓝图 manifest（.workflows/blueprints/<name>.json）驱动，逐 stage 检查退出条件。
# 退出条件全部基于「子 Plan 文件系统事实」（childPlanExists / status / plan-gate-check / 子 Plan WBS），
# 绝不读 Epic 的 lifecycle_state。
#
# 用法：
#   ./scripts/workflow-gate.sh --workflow client-dev --epic Plans/Epic/xxx.md
#   ./scripts/workflow-gate.sh --workflow client-dev --project 新版工作空间
#   ./scripts/workflow-gate.sh --workflow computer-mgmt            # 无 Epic 轻量清单
#   ./scripts/workflow-gate.sh --workflow client-dev --epic ... --json
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKFLOW=""
EPIC=""
PROJECT=""
JSON=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workflow) WORKFLOW="${2:-}"; shift 2 ;;
    --epic) EPIC="${2:-}"; shift 2 ;;
    --project) PROJECT="${2:-}"; shift 2 ;;
    --json) JSON=1; shift ;;
    -h|--help)
      echo "Usage: workflow-gate.sh --workflow <name> [--epic Plans/Epic/xxx.md] [--project 模块名] [--json]"
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
      sub(/[[:space:]]+#.*$/, "")   # 去行内注释（如 lifecycle_state: requirement  # DEPRECATED）
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
  [[ -n "$PROJECT" ]] && return
  [[ -n "$best" ]] && echo "$best"
}

wbs_slice_done() {
  local f="$1" n="$2"
  local line
  line="$(sed -n '/^```$/,/^```$/p' "$f" | grep -E "^\[[ xX~]\][[:space:]]*${n}\.[[:space:]]" | head -1 || true)"
  if [[ -n "$line" ]]; then
    [[ "$line" =~ ^\[[xX]\] ]] && return 0
    return 1
  fi

  line="$(grep -E "^\|[[:space:]]*${n}[[:space:]]*\|" "$f" | head -1 || true)"
  if [[ -n "$line" ]]; then
    [[ "$line" == *"✅"* || "$line" == *"[x]"* || "$line" == *"[X]"* ]] && return 0
  fi
  return 1
}

wbs_slices_done() {
  # $1=file, remaining args = slice numbers
  local f="$1"; shift
  local n
  for n in "$@"; do
    wbs_slice_done "$f" "$n" || return 1
  done
  return 0
}

wbs_missing_slices() {
  local f="$1"; shift
  local n missing=()
  for n in "$@"; do
    wbs_slice_done "$f" "$n" || missing+=("$n")
  done
  local IFS=','
  echo "${missing[*]}"
}

emit_json() {
  python3 - "$@" <<'PY'
import json, sys
print(json.dumps(json.loads(sys.argv[1]), ensure_ascii=False, indent=2))
PY
}

# --- 解析蓝图：默认从 Epic frontmatter workflow 读，再默认 client-dev ---
BP_DEFAULT="client-dev"
if [[ -z "$WORKFLOW" ]]; then
  EPIC_PROBE="$(find_epic || true)"
  if [[ -n "$EPIC_PROBE" && -f "$EPIC_PROBE" ]]; then
    WF_FROM_EPIC="$(read_fm workflow "$EPIC_PROBE" || true)"
    WORKFLOW="${WF_FROM_EPIC:-$BP_DEFAULT}"
  else
    WORKFLOW="$BP_DEFAULT"
  fi
fi

BLUEPRINT="$ROOT/.workflows/blueprints/${WORKFLOW}.json"
if [[ ! -f "$BLUEPRINT" ]]; then
  LEGACY_BLUEPRINT="$ROOT/.claude/workflows/${WORKFLOW}.json"
  if [[ -f "$LEGACY_BLUEPRINT" ]]; then
    BLUEPRINT="$LEGACY_BLUEPRINT"
    echo "WARN: 使用 legacy 蓝图路径 .claude/workflows/${WORKFLOW}.json；请迁移到 .workflows/blueprints/" >&2
  else
    echo "BLOCKED: 蓝图不存在: .workflows/blueprints/${WORKFLOW}.json" >&2
    exit 1
  fi
fi

if [[ "$BLUEPRINT" == "$ROOT/.workflows/blueprints/"* ]]; then
  if ! python3 "$ROOT/scripts/validate-workflow-blueprint.py" --quiet "${BLUEPRINT#"$ROOT"/}" >/dev/null; then
    exit 1
  fi
fi

# 读蓝图元信息
USES_EPIC="$(python3 -c 'import json,sys; print("1" if json.load(open(sys.argv[1])).get("usesEpic") else "0")' "$BLUEPRINT")"
# stages：每行用 \x1f(US) 分隔 key|label|epicField|planFolder|wbsSlices(逗号)|exitCriteria(json)|onlyIf(json)|planPrefix
# 用非空白分隔符，避免 read 折叠空字段（如空 epicField）导致字段错位。
mapfile -t STAGE_ROWS < <(python3 - "$BLUEPRINT" <<'PY'
import json, sys
bp = json.load(open(sys.argv[1]))
US = "\x1f"
for s in bp.get("stages", []):
    key = s.get("key", "")
    label = s.get("label", "")
    epic_field = s.get("epicField", "")
    folder = s.get("planFolder", "")
    slices = ",".join(str(n) for n in s.get("wbsSlices", []))
    exitc = json.dumps(s.get("exitCriteria", {}), ensure_ascii=False)
    onlyif = json.dumps(s.get("onlyIf", {}), ensure_ascii=False)
    prefix = s.get("planPrefix", "")
    print(US.join([key, label, epic_field, folder, slices, exitc, onlyif, prefix]))
PY
)

# exitCriteria helper：查某 json 布尔/值
crit_has() { python3 -c 'import json,sys; c=json.loads(sys.argv[1]); print("1" if c.get(sys.argv[2]) else "0")' "$1" "$2"; }
crit_status_list() { python3 -c 'import json,sys; c=json.loads(sys.argv[1]); print("\n".join(c.get("status",[])))' "$1"; }

blockers=()
plans_found=()
current_state=""
current_label=""
recommended_skill=""
next_state="done"
gate_development="SKIP"
epic_rel=""

EPIC_FILE=""
biz=""
if [[ "$USES_EPIC" == "1" ]]; then
  EPIC_FILE="$(find_epic || true)"
  if [[ -z "$EPIC_FILE" || ! -f "$EPIC_FILE" ]]; then
    blockers+=("无 Epic plan（Plans/Epic/）；须先 bootstrap Epic")
    current_state="$(echo "${STAGE_ROWS[0]}" | cut -d$'\x1f' -f1)"
    current_label="$(echo "${STAGE_ROWS[0]}" | cut -d$'\x1f' -f2)"
    recommended_skill="template-generator"
    next_state="bootstrap-epic"
  else
    epic_rel="${EPIC_FILE#"$ROOT"/}"
    biz="$(read_fm 含业务逻辑 "$EPIC_FILE")"
  fi
fi

# stage 级 skill 建议（从蓝图 skills[0]）
stage_skill() {
  python3 -c 'import json,sys
bp=json.load(open(sys.argv[1]))
for s in bp.get("stages",[]):
    if s.get("key")==sys.argv[2]:
        sk=s.get("skills",[]); print(sk[0] if sk else "")
        break' "$BLUEPRINT" "$1"
}

# --- 逐 stage 检查，落到第一个未通过的 stage ---
if [[ ${#blockers[@]} -eq 0 ]]; then
  found_stage=""
  n_stages=${#STAGE_ROWS[@]}
  for ((i=0; i<n_stages; i++)); do
    IFS=$'\x1f' read -r s_key s_label s_epicfield s_folder s_slices s_exit s_onlyif s_prefix <<<"${STAGE_ROWS[$i]}"

    # onlyIf：如 {"含业务逻辑":"是"}，不满足则跳过该 stage
    onlyif_skip=0
    if [[ "$s_onlyif" != "{}" && -n "$s_onlyif" ]]; then
      oif_key="$(python3 -c 'import json,sys; c=json.loads(sys.argv[1]); print(next(iter(c),""))' "$s_onlyif")"
      oif_val="$(python3 -c 'import json,sys; c=json.loads(sys.argv[1]); print(next(iter(c.values()),""))' "$s_onlyif")"
      if [[ "$oif_key" == "含业务逻辑" && "$biz" != "$oif_val" ]]; then
        onlyif_skip=1
      fi
    fi
    [[ "$onlyif_skip" == "1" ]] && continue

    # 计算下一 stage key（用于 next_state）
    if (( i+1 < n_stages )); then
      nxt="$(echo "${STAGE_ROWS[$((i+1))]}" | cut -d$'\x1f' -f1)"
    else
      nxt="done"
    fi

    stage_blockers=()

    # 子 Plan 路径解析：有 Epic 只用 epicField 从 Epic 读；无 Epic 按 planFolder 扫最新。
    # 关键：usesEpic=true 的蓝图不得回退扫目录，否则会串到别的 Epic 的 plan。
    child_raw=""
    if [[ "$USES_EPIC" == "1" && -n "$s_epicfield" && -n "$EPIC_FILE" ]]; then
      child_raw="$(read_plan_key "$EPIC_FILE" "$s_epicfield")"
      [[ -n "$child_raw" && "$child_raw" != "null" ]] && plans_found+=("$s_key:$child_raw")
    elif [[ "$USES_EPIC" != "1" && -n "$s_folder" ]]; then
      # 无 Epic：按 planFolder（+planPrefix）找子 Plan
      shopt -s nullglob
      cands=("$ROOT/$s_folder"/*"${s_prefix}"*.md)
      if [[ ${#cands[@]} -gt 0 ]]; then
        child_raw="${s_folder}/$(basename "${cands[-1]}")"
        plans_found+=("$s_key:$child_raw")
      fi
    fi

    # exitCriteria: childPlanExists
    if [[ "$(crit_has "$s_exit" childPlanExists)" == "1" ]]; then
      if [[ -z "$child_raw" || "$child_raw" == "null" ]]; then
        stage_blockers+=("${s_label}：子 Plan 未创建（${s_folder}/）")
      else
        child_file="$(resolve_path "$child_raw")"
        [[ -f "$child_file" ]] || stage_blockers+=("${s_label}：子 Plan 不存在: $child_raw")
      fi
    fi

    # 有子 Plan 文件时，做 status / p0 / requiredSections / gate 检查
    child_file=""
    [[ -n "$child_raw" && "$child_raw" != "null" ]] && child_file="$(resolve_path "$child_raw")"

    if [[ -n "$child_file" && -f "$child_file" ]]; then
      # requiredSections（验收标准等）—— 仅对 requirement 类做通用「验收标准」硬检查
      if [[ "$(crit_has "$s_exit" status)" == "1" ]]; then
        c_status="$(read_fm status "$child_file")"
        ok_status=0
        while IFS= read -r want; do
          [[ -z "$want" ]] && continue
          [[ "$c_status" == "$want" ]] && ok_status=1
        done < <(crit_status_list "$s_exit")
        [[ "$ok_status" == "1" ]] || stage_blockers+=("${s_label}：status 须为「$(crit_status_list "$s_exit" | tr '\n' '/')」（当前: ${c_status:-无}）")
      fi

      if [[ "$(crit_has "$s_exit" p0Open)" == "1" || "$s_exit" == *'"p0Open"'* ]]; then
        c_p0="$(read_fm p0_open "$child_file")"
        c_p0="${c_p0:-0}"
        [[ "$c_p0" =~ ^[0-9]+$ ]] || c_p0=0
        [[ "$c_p0" -eq 0 ]] || stage_blockers+=("${s_label}：p0_open=${c_p0}，须闭环 P0")
        grep -qE '验收标准|## 九、验收标准' "$child_file" || stage_blockers+=("${s_label}：子 Plan 缺少验收标准章节")
      fi

      # planGateCheck（开发阶段写代码前门禁）
      if [[ "$(crit_has "$s_exit" planGateCheck)" == "1" ]]; then
        if gate_development="$(bash "$ROOT/scripts/plan-gate-check.sh" "$child_file" --stage development 2>&1)"; then
          :
        else
          stage_blockers+=("${s_label}：plan-gate-check: ${gate_development#BLOCKED:}")
        fi
      fi

      # skillRun（阶段完成反馈回路）
      if [[ "$(crit_has "$s_exit" skillRun)" == "1" ]]; then
        skill_run_check="$(python3 "$ROOT/scripts/validate-skill-run.py" --require "$child_file" 2>&1 || true)"
        [[ "$skill_run_check" == OK:* ]] || stage_blockers+=("${s_label}：skill_run 校验未通过: ${skill_run_check#BLOCKED:skill_run:}")
      fi
    fi

    # wbsDone：本 stage 覆盖的 WBS 切片全勾。Epic 只是投影，门禁只读子 Plan。
    if [[ "$(crit_has "$s_exit" wbsDone)" == "1" && -n "$s_slices" ]]; then
      if [[ -n "$child_file" && -f "$child_file" ]]; then
        IFS=',' read -ra slice_arr <<<"$s_slices"
        if ! wbs_slices_done "$child_file" "${slice_arr[@]}"; then
          missing_slices="$(wbs_missing_slices "$child_file" "${slice_arr[@]}")"
          stage_blockers+=("${s_label}：WBS 切片 ${s_slices} 未全部完成（缺: ${missing_slices:-未知}）")
        fi
      fi
    fi

    if [[ ${#stage_blockers[@]} -gt 0 ]]; then
      current_state="$s_key"
      current_label="$s_label"
      recommended_skill="$(stage_skill "$s_key")"
      next_state="$nxt"
      blockers+=("${stage_blockers[@]}")
      found_stage="$s_key"
      break
    fi
  done

  if [[ -z "$found_stage" ]]; then
    current_state="done"
    current_label="全部完成"
    recommended_skill="（归档 / 收尾）"
    next_state="done"
  fi
fi

lc_hint=""
if [[ "$USES_EPIC" == "1" && -n "$EPIC_FILE" ]]; then
  # 仅对照展示，门禁不采用
  lc_hint="$(read_fm lifecycle_state "$EPIC_FILE" || true)"
fi

if [[ "$JSON" -eq 1 ]]; then
  bl_json="$(printf '%s\n' "${blockers[@]:-}" | python3 -c 'import json,sys; print(json.dumps([l for l in sys.stdin.read().splitlines() if l.strip()], ensure_ascii=False))')"
  pf_json="$(printf '%s\n' "${plans_found[@]:-}" | python3 -c 'import json,sys; print(json.dumps([l for l in sys.stdin.read().splitlines() if l.strip()], ensure_ascii=False))')"
  python3 - "$WORKFLOW" "$USES_EPIC" "${epic_rel:-}" "${lc_hint:-}" "$current_state" "$next_state" "$recommended_skill" "$gate_development" "$bl_json" "$pf_json" <<'PY'
import json
import sys

workflow, uses_epic, epic, lc_hint, current_state, next_state, recommended_skill, gate_development, blockers, plans_found = sys.argv[1:]
payload = {
    "workflow": workflow,
    "uses_epic": uses_epic == "1",
    "epic": epic,
    "lifecycle_state_hint_deprecated": lc_hint,
    "current_state": current_state,
    "next_state": next_state,
    "recommended_skill": recommended_skill,
    "gate_development": gate_development,
    "blockers": json.loads(blockers),
    "plans_found": json.loads(plans_found),
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
  exit 0
fi

echo "# workflow-gate 机械门禁"
echo "# vault: $ROOT"
echo "# workflow: ${WORKFLOW}（$([[ "$USES_EPIC" == "1" ]] && echo '有 Epic' || echo '无 Epic 轻量清单')）"
echo ""
if [[ -n "${epic_rel:-}" ]]; then
  echo "epic: $epic_rel"
  echo "lifecycle_state_hint: ${lc_hint:-（无）}"
  echo "gate_development: $gate_development"
  echo ""
fi
echo "current_state: ${current_state}（${current_label}）"
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
  echo "  （无 — 工作流门禁通过）"
else
  for b in "${blockers[@]}"; do
    echo "  - $b"
  done
fi
echo ""
echo "report: 📌 当前阶段：[$current_state] | 下一个阶段：[$next_state / $recommended_skill] | 如需中断：/resume plan=${epic_rel:-Plans/}"
