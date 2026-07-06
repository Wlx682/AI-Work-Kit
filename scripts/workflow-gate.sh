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
PROBE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workflow) WORKFLOW="${2:-}"; shift 2 ;;
    --epic) EPIC="${2:-}"; shift 2 ;;
    --project) PROJECT="${2:-}"; shift 2 ;;
    --json) JSON=1; shift ;;
    --probe) PROBE=1; shift ;;
    -h|--help)
      echo "Usage: workflow-gate.sh --workflow <name> [--epic Plans/Epic/xxx.md] [--project 模块名] [--json] [--probe]"
      echo "  --probe  只读探测：不写审计事件（供 render-epic-board.py / pre-commit 派生用）"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

read_fm() {
  python3 "$ROOT/scripts/gate_parse.py" read-frontmatter-key "$2" "$1"
}

read_plan_key() {
  local f="$1" key="$2"
  python3 "$ROOT/scripts/gate_parse.py" read-plan-key "$f" "$key"
}

resolve_path() {
  local p="$1"
  if [[ "$p" == /* ]]; then
    echo "$p"
    return
  fi
  p="$ROOT/$p"
  [[ "$p" == *.md ]] || p="${p}.md"
  echo "$p"
}

# 不补 .md 后缀的路径解析（用于 verdict json 等非 md 产物）。
resolve_path_raw() {
  local p="$1"
  if [[ "$p" == /* ]]; then
    echo "$p"
  else
    echo "$ROOT/$p"
  fi
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

wbs_slice_status() {
  local f="$1" n="$2"
  python3 "$ROOT/scripts/gate_parse.py" wbs-slice-status "$f" "$n" 2>/dev/null || true
}

csv_has() {
  local csv="$1" needle="$2"
  local item
  IFS=',' read -ra _csv_items <<<"$csv"
  for item in "${_csv_items[@]:-}"; do
    [[ "$item" == "$needle" ]] && return 0
  done
  return 1
}

wbs_slice_satisfied() {
  local f="$1" n="$2" optional_csv="$3"
  local status
  status="$(wbs_slice_status "$f" "$n")"
  if [[ "$status" == "x" ]]; then
    return 0
  fi
  if [[ "$status" == "-" ]] && csv_has "$optional_csv" "$n"; then
    return 0
  fi
  return 1
}

wbs_slices_done() {
  # $1=file, $2=optional slice csv, remaining args = slice numbers
  local f="$1" optional_csv="$2"; shift 2
  local n
  for n in "$@"; do
    wbs_slice_satisfied "$f" "$n" "$optional_csv" || return 1
  done
  return 0
}

wbs_missing_slices() {
  local f="$1" optional_csv="$2"; shift 2
  local n missing=()
  for n in "$@"; do
    wbs_slice_satisfied "$f" "$n" "$optional_csv" || missing+=("$n")
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
  echo "BLOCKED: 蓝图不存在: .workflows/blueprints/${WORKFLOW}.json" >&2
  exit 1
fi

if ! python3 "$ROOT/scripts/validate-workflow-blueprint.py" --quiet "${BLUEPRINT#"$ROOT"/}" >/dev/null; then
  exit 1
fi

# 读蓝图元信息
USES_EPIC="$(python3 -c 'import json,sys; print("1" if json.load(open(sys.argv[1])).get("usesEpic") else "0")' "$BLUEPRINT")"
# stages：每行用 \x1f(US) 分隔 key|label|epicField|planFolder|wbsSlices(逗号)|exitCriteria(json)|onlyIf(json)|planPrefix|requiredSections(json)|optionalWbsSlices(逗号)
# 用非空白分隔符，避免 read 折叠空字段（如空 epicField）导致字段错位。
STAGE_ROWS=()
while IFS= read -r line; do
  STAGE_ROWS+=("$line")
done < <(python3 - "$BLUEPRINT" <<'PY'
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
    req_sections = json.dumps(s.get("requiredSections", []), ensure_ascii=False)
    optional_slices = ",".join(str(n) for n in s.get("optionalWbsSlices", []))
    print(US.join([key, label, epic_field, folder, slices, exitc, onlyif, prefix, req_sections, optional_slices]))
PY
)

# exitCriteria helper：查某 json 布尔/值
crit_has() { python3 -c 'import json,sys; c=json.loads(sys.argv[1]); print("1" if c.get(sys.argv[2]) else "0")' "$1" "$2"; }
crit_status_list() { python3 -c 'import json,sys; c=json.loads(sys.argv[1]); print("\n".join(c.get("status",[])))' "$1"; }

blockers=()
plans_found=()
passed_stage_records=()
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
    IFS=$'\x1f' read -r s_key s_label s_epicfield s_folder s_slices s_exit s_onlyif s_prefix s_reqsections s_optional_slices <<<"${STAGE_ROWS[$i]}"

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

      # verdictPass（对抗式视觉验证裁决）：读子 Plan frontmatter 的 verdict: 路径，
      # 要求裁决文件存在、JSON 合法、pass==true 且 reviewed==true（经主控复核，防原始误报直接放行）。
      # 门禁只读文件事实，不实时跑验证子 Agent。
      # verdictPass 模式：
      #   true / "required" → 缺 verdict: 字段即 BLOCK（纯 UI 流程强制，如 ui-change）
      #   "ifPresent"       → 缺 verdict: 字段则豁免（混合开发阶段条件触发，如 client-dev development：
      #                        figma-ui 做了 UI 还原才写 verdict，纯逻辑开发不写则自动跳过）
      verdict_mode="$(python3 -c 'import json,sys; c=json.loads(sys.argv[1]); v=c.get("verdictPass"); print("" if v in (None,False) else ("ifPresent" if v=="ifPresent" else "required"))' "$s_exit")"
      if [[ -n "$verdict_mode" ]]; then
        verdict_raw="$(read_fm verdict "$child_file" || true)"
        if [[ -z "$verdict_raw" || "$verdict_raw" == "null" ]]; then
          [[ "$verdict_mode" == "required" ]] && stage_blockers+=("${s_label}：子 Plan 缺少 verdict: 字段（须指向对抗验证裁决 json）")
        else
          verdict_file="$(resolve_path_raw "$verdict_raw")"
          if [[ ! -f "$verdict_file" ]]; then
            stage_blockers+=("${s_label}：裁决文件不存在: $verdict_raw")
          else
            verdict_msg="$(python3 - "$verdict_file" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as e:
    print(f"裁决 json 解析失败: {e}"); raise SystemExit
if d.get("pass") is not True:
    print("裁决 pass!=true（还原未通过，见 deviations）"); raise SystemExit
if d.get("reviewed") is not True:
    print("裁决 reviewed!=true（未经主控复核，不得放行）"); raise SystemExit
print("OK")
PY
)"
            [[ "$verdict_msg" == "OK" ]] || stage_blockers+=("${s_label}：verdictPass: $verdict_msg")
          fi
        fi
      fi

      # sectionsPresent（交接契约）：requiredSections 声明的每个章节须「标题存在 + 内容非空非纯占位」。
      # 堵「交接物有标题空架子/漏章节」这类信息丢失。
      if [[ "$(crit_has "$s_exit" sectionsPresent)" == "1" && -n "$s_reqsections" && "$s_reqsections" != "[]" ]]; then
        sect_msg="$(python3 "$ROOT/scripts/gate_parse.py" check-sections "$child_file" "$s_reqsections" --msg 2>/dev/null || true)"
        [[ -z "$sect_msg" ]] || stage_blockers+=("${s_label}：交接契约未满足 [${sect_msg}]")
      fi


      if [[ "$(crit_has "$s_exit" testTraceability)" == "1" ]]; then
        traceability_check="$(python3 "$ROOT/scripts/traceability-check.py" --epic "$EPIC_FILE" --check test 2>&1 || true)"
        [[ "$traceability_check" == *"OK:traceability"* ]] || stage_blockers+=("${s_label}：testTraceability: ${traceability_check#BLOCKED:traceability:}")
      fi

      # devTraceability：需求 P0 AC → 功能开发任务覆盖闭环。
      if [[ "$(crit_has "$s_exit" devTraceability)" == "1" ]]; then
        traceability_check="$(python3 "$ROOT/scripts/traceability-check.py" --epic "$EPIC_FILE" --check dev 2>&1 || true)"
        [[ "$traceability_check" == *"OK:traceability"* ]] || stage_blockers+=("${s_label}：devTraceability: ${traceability_check#BLOCKED:traceability:}")
      fi
    fi

    # wbsDone：本 stage 覆盖的 WBS 切片全勾。Epic 只是投影，门禁只读子 Plan。
    if [[ "$(crit_has "$s_exit" wbsDone)" == "1" && -n "$s_slices" ]]; then
      if [[ -n "$child_file" && -f "$child_file" ]]; then
        IFS=',' read -ra slice_arr <<<"$s_slices"
        if ! wbs_slices_done "$child_file" "$s_optional_slices" "${slice_arr[@]}"; then
          missing_slices="$(wbs_missing_slices "$child_file" "$s_optional_slices" "${slice_arr[@]}")"
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
    passed_stage_records+=("$s_key:$child_raw")
  done

  if [[ -z "$found_stage" ]]; then
    current_state="done"
    current_label="全部完成"
    recommended_skill="（归档 / 收尾）"
    next_state="done"
  fi
fi

# --- 审计旁路（auditd 哲学）：判定完成后被动追加一条事件到时间账本。 ---
# 铁律：只读现场、只 append、写失败绝不影响门禁退出码，也不参与任何路由判定。
# 信号源是 blockers 数组（空=pass），不是 $?——本门禁 pass/fail 都 exit 0。
# 事件按 Epic 聚合：.workflows/events/<epic-stem>.events.jsonl（无 Epic 用 workflow 名）。
emit_gate_event() {
  # 整个函数包在子 shell + || true 里，任何失败都被吞掉，绝不冒泡到门禁主流程。
  (
    set +e
    local event_dir="$ROOT/.workflows/events"
    mkdir -p "$event_dir" 2>/dev/null || return 0

    local stem
    if [[ -n "${epic_rel:-}" ]]; then
      stem="$(basename "${epic_rel%.md}")"
    else
      stem="$WORKFLOW"
    fi
    local event_file="$event_dir/${stem}.events.jsonl"

    # 判定结果：blockers 空即 pass。
    local result reason=""
    if [[ ${#blockers[@]} -eq 0 ]]; then
      result="gate_pass"
    else
      result="gate_fail"
      reason="${blockers[0]}"
    fi

    # 恢复密钥（回溯用）：代码版本 + 当前卡住 stage 的子 Plan 内容指纹。
    local git_commit plan_snapshot=""
    git_commit="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo "")"
    local cur_child=""
    local p
    for p in "${plans_found[@]:-}"; do
      if [[ "$p" == "${current_state}:"* ]]; then
        cur_child="${p#*:}"
        break
      fi
    done
    if [[ -n "$cur_child" ]]; then
      local cf
      cf="$(resolve_path "$cur_child")"
      [[ -f "$cf" ]] && plan_snapshot="$(shasum -a 256 "$cf" 2>/dev/null | awk '{print $1}')"
    fi

    local passed_json
    passed_json="$(printf '%s\n' "${passed_stage_records[@]:-}" | python3 -c 'import json,sys; print(json.dumps([l for l in sys.stdin.read().splitlines() if l.strip()], ensure_ascii=False))' 2>/dev/null || echo '[]')"

    # 时间戳来自执行现场（date），不伪造。JSONL 由 python 安全序列化。
    python3 - "$event_file" "$result" "$current_state" "$reason" "$git_commit" "$plan_snapshot" "$WORKFLOW" "${epic_rel:-}" "$cur_child" "$passed_json" "$ROOT" <<'PY' 2>/dev/null || true
import datetime, hashlib, json, pathlib, sys

event_file, etype, stage, reason, git_commit, plan_snapshot, workflow, epic, child, passed_json, root = sys.argv[1:12]
root_path = pathlib.Path(root)
event_path = pathlib.Path(event_file)
created_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

events = []
if event_path.exists():
    for line in event_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass

latest_by_stage = {}
for ev in events:
    if ev.get("type") in ("gate_pass", "gate_fail") and ev.get("stage"):
        latest_by_stage[ev["stage"]] = ev.get("type")

def snapshot(rel):
    if not rel:
        return None
    p = pathlib.Path(rel)
    if not p.is_absolute():
        p = root_path / p
    if not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()

to_write = []
for item in json.loads(passed_json):
    passed_stage, _, passed_child = item.partition(":")
    if not passed_stage or latest_by_stage.get(passed_stage) == "gate_pass":
        continue
    to_write.append({
        "type": "gate_pass",
        "stage": passed_stage,
        "workflow": workflow,
        "epic": epic or None,
        "child_plan": passed_child or None,
        "reason": "阶段门禁已通过；历史阻塞已解除" if latest_by_stage.get(passed_stage) == "gate_fail" else "阶段门禁已通过",
        "git_commit": git_commit or None,
        "plan_snapshot": snapshot(passed_child),
        "created_at": created_at,
    })
    latest_by_stage[passed_stage] = "gate_pass"

to_write.append({
    "type": etype,
    "stage": stage,
    "workflow": workflow,
    "epic": epic or None,
    "child_plan": child or None,
    "reason": reason,
    "git_commit": git_commit or None,
    "plan_snapshot": plan_snapshot or None,
    "created_at": created_at,
})
with event_path.open("a", encoding="utf-8") as fh:
    for ev in to_write:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
PY
    return 0
  ) 2>/dev/null || true
}
# --probe（只读派生）时跳过审计写入：render/pre-commit 高频探测不应污染时间账本。
[[ "$PROBE" == "1" ]] || emit_gate_event

lc_hint=""
if [[ "$USES_EPIC" == "1" && -n "$EPIC_FILE" ]]; then
  # 仅对照展示，门禁不采用
  lc_hint="$(read_fm lifecycle_state "$EPIC_FILE" || true)"
fi

bl_json="$(printf '%s\n' "${blockers[@]:-}" | python3 -c 'import json,sys; print(json.dumps([l for l in sys.stdin.read().splitlines() if l.strip()], ensure_ascii=False))')"
pf_json="$(printf '%s\n' "${plans_found[@]:-}" | python3 -c 'import json,sys; print(json.dumps([l for l in sys.stdin.read().splitlines() if l.strip()], ensure_ascii=False))')"
constitution_json="$(python3 - "$ROOT" "$BLUEPRINT" "$bl_json" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
blueprint = pathlib.Path(sys.argv[2])
blockers = json.loads(sys.argv[3])
bp = json.loads(blueprint.read_text(encoding="utf-8"))
raw = bp.get("constitution")
if not raw:
    print(json.dumps({"configured": False, "path": None, "status": "not-configured", "rules": []}, ensure_ascii=False))
    raise SystemExit
path = pathlib.Path(raw)
if not path.is_absolute():
    path = root / path
rules = []
status = "blocked" if blockers else "ok"
if path.exists():
    data = json.loads(path.read_text(encoding="utf-8"))
    for rule in data.get("rules", []):
        item = dict(rule)
        checked_by = str(rule.get("checkedBy", ""))
        rule_id = str(rule.get("id", ""))
        if checked_by.startswith("deferred:"):
            item["status"] = "indexed"
        elif not blockers:
            item["status"] = "ok"
        else:
            needles = {
                "tdd_first": ["验收测试先行", "WBS 切片 4"],
                "skill_run_required": ["skill_run"],
                "epic_required": ["无 Epic"],
                "traceability": ["testTraceability", "devTraceability", "traceability"],
                "wbs_single_truth": ["母子 plan 投影", "epic-projection"],
            }.get(rule_id, [rule_id])
            item["status"] = "blocked" if any(any(needle in b for needle in needles) for b in blockers) else "delegated"
        rules.append(item)
print(json.dumps({
    "configured": True,
    "path": str(path.relative_to(root)),
    "status": status,
    "rules": rules,
}, ensure_ascii=False))
PY
)"

if [[ "$JSON" -eq 1 ]]; then
  python3 - "$WORKFLOW" "$USES_EPIC" "${epic_rel:-}" "${lc_hint:-}" "$current_state" "$next_state" "$recommended_skill" "$gate_development" "$bl_json" "$pf_json" "$constitution_json" <<'PY'
import json
import sys

workflow, uses_epic, epic, lc_hint, current_state, next_state, recommended_skill, gate_development, blockers, plans_found, constitution = sys.argv[1:]
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
    "constitution": json.loads(constitution),
}
print(json.dumps(payload, ensure_ascii=True, indent=2))
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
python3 - "$constitution_json" <<'PY'
import json
import sys

constitution = json.loads(sys.argv[1])
print("constitution:")
if not constitution.get("configured"):
    print("  not-configured")
else:
    print(f"  path: {constitution['path']}")
    print(f"  status: {constitution['status']}")
    for rule in constitution.get("rules", []):
        print(f"  - {rule['id']}: {rule['status']}")
PY
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
