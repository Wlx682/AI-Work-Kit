#!/usr/bin/env bash
# 从「文件系统事实」派生 Epic 的当前阶段（derived_status），供看板/汇报显示。
# 与 workflow-gate.sh 共用同一套判定逻辑（本脚本仅做薄封装 + 输出格式化），
# 避免派生逻辑漂移。
#
# 关键约束（三层架构）：
#   - 只读，绝不写回 Epic frontmatter 的 lifecycle_state。
#   - derived_status 是「派生指标」，仅供人工阅读；引擎路由永远走 workflow-gate.sh。
#
# 用法：
#   ./scripts/derive-epic-status.sh Plans/Epic/xxx.md
#   ./scripts/derive-epic-status.sh Plans/Epic/xxx.md --workflow client-dev
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EPIC="${1:-}"
shift || true
WORKFLOW=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --workflow) WORKFLOW="${2:-}"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$EPIC" ]]; then
  echo "Usage: derive-epic-status.sh Plans/Epic/xxx.md [--workflow <name>]" >&2
  exit 1
fi

EPIC_ABS="$EPIC"
[[ "$EPIC_ABS" == /* ]] || EPIC_ABS="$ROOT/$EPIC"
if [[ ! -f "$EPIC_ABS" ]]; then
  echo "Epic 不存在: $EPIC" >&2
  exit 1
fi

read_fm() {
  awk -v key="$1" '
    BEGIN { in_fm=0 }
    /^---$/ { in_fm++; next }
    in_fm==1 && $0 ~ "^" key ":" {
      sub("^" key ":[[:space:]]*", ""); sub(/[[:space:]]+#.*$/, ""); gsub(/"/, ""); print; exit
    }
  ' "$2"
}

# 蓝图：命令行 > Epic frontmatter workflow > 默认 client-dev
if [[ -z "$WORKFLOW" ]]; then
  WORKFLOW="$(read_fm workflow "$EPIC_ABS" || true)"
  WORKFLOW="${WORKFLOW:-client-dev}"
fi

WF_ARG=(--workflow "$WORKFLOW" --epic "$EPIC")
GATE_JSON="$(bash "$ROOT/scripts/workflow-gate.sh" "${WF_ARG[@]}" --json 2>/dev/null || true)"

if [[ -z "$GATE_JSON" ]]; then
  echo "derived_status: unknown  # workflow-gate.sh 无输出"
  exit 0
fi

python3 - "$GATE_JSON" "$EPIC_ABS" <<'PY'
import json, sys
g = json.loads(sys.argv[1])
epic = sys.argv[2]

# frontmatter 里手写的 lifecycle_state（deprecated），用于对照
lc = ""
in_fm = 0
for line in open(epic, encoding="utf-8"):
    if line.strip() == "---":
        in_fm += 1
        if in_fm >= 2:
            break
        continue
    if in_fm == 1 and line.startswith("lifecycle_state:"):
        lc = line.split(":", 1)[1].strip().strip('"')
        # 去掉行内注释（如 "requirement  # DEPRECATED ..."）
        if "#" in lc:
            lc = lc.split("#", 1)[0].strip()

derived = g.get("current_state", "unknown")
print(f"workflow: {g.get('workflow','')}")
print(f"derived_status: {derived}  # 由蓝图 + 子 Plan/结构化证据派生（文件系统事实）")
print(f"next_state: {g.get('next_state','')}")
print(f"lifecycle_state_frontmatter: {lc or '(无)'}  # 仅对照，引擎不采用")
if lc and lc != derived:
    print(f"# ⚠️ 漂移提示：frontmatter lifecycle_state={lc} 与派生值 {derived} 不一致；以派生值为准，可手动清理 frontmatter。")
bl = g.get("blockers", [])
print(f"open_blockers: {len(bl)}")
for b in bl:
    print(f"  - {b}")
PY
