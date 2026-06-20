#!/usr/bin/env bash
# Epic 进度 → Web 看板同步（Agent 写回 Epic/plan 后必跑）
#
# 用法：
#   ./scripts/kanban-sync.sh --boot [--epic Plans/Epic/xxx.md]     # 确保看板服务运行
#   ./scripts/kanban-sync.sh --epic Plans/Epic/xxx.md --slice 2 --done
#   ./scripts/kanban-sync.sh --epic Plans/Epic/xxx.md --slice 3 --open
#   ./scripts/kanban-sync.sh --epic Plans/Epic/xxx.md --slices-done 1,2,3
#   ./scripts/kanban-sync.sh --epic Plans/Epic/xxx.md --lifecycle development
#   ./scripts/kanban-sync.sh --epic Plans/Epic/xxx.md --plan-status Plans/需求分析/xxx.md 已采纳
#
# 说明：
# - 直接改 markdown 后跑 --boot 即可；浏览器每 2.5s 轮询 /api/revision 自动刷新
# - WBS 勾选推荐走 --slice / --slices-done（写回 markdown + 变更日志，与看板一致）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="127.0.0.1"
PORT=7777
BASE="http://${HOST}:${PORT}"
EPIC=""
BOOT=0
SLICE=""
SLICE_DONE=""
SLICES_DONE=""
LIFECYCLE=""
PLAN_PATH=""
PLAN_STATUS=""
OPERATOR="agent"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --boot) BOOT=1; shift ;;
    --epic) EPIC="${2:-}"; shift 2 ;;
    --slice) SLICE="${2:-}"; shift 2 ;;
    --done) SLICE_DONE=1; shift ;;
    --open) SLICE_DONE=0; shift ;;
    --slices-done) SLICES_DONE="${2:-}"; shift 2 ;;
    --lifecycle) LIFECYCLE="${2:-}"; shift 2 ;;
    --plan-status)
      PLAN_PATH="${2:-}"
      PLAN_STATUS="${3:-}"
      shift 3
      ;;
    --operator) OPERATOR="${2:-agent}"; shift 2 ;;
    -h|--help)
      sed -n '2,18p' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

api_ok() {
  curl -sf "${BASE}/api/board" >/dev/null 2>&1
}

api_post() {
  local path="$1"
  local body="$2"
  curl -sf -X POST "${BASE}${path}" \
    -H 'Content-Type: application/json' \
    -d "$body" \
    -o /dev/null
}

if [[ "$BOOT" -eq 1 ]] || ! api_ok; then
  boot_args=(--no-open)
  [[ -n "$EPIC" ]] && boot_args=(--epic "$EPIC" --no-open)
  bash "$ROOT/scripts/full-cycle-boot.sh" "${boot_args[@]}"
fi

if ! api_ok; then
  echo "kanban-sync: server not reachable at ${BASE}" >&2
  exit 1
fi

if [[ -n "$SLICES_DONE" ]]; then
  [[ -n "$EPIC" ]] || { echo "kanban-sync: --slices-done requires --epic" >&2; exit 1; }
  IFS=',' read -ra nums <<< "$SLICES_DONE"
  for n in "${nums[@]}"; do
    n="$(echo "$n" | tr -d ' ')"
    [[ -n "$n" ]] || continue
    api_post /api/slice "$(printf '{"file":"%s","slice":%s,"done":true,"operator":"%s"}' "$EPIC" "$n" "$OPERATOR")"
    echo "kanban-sync: WBS ${n} → done"
  done
fi

if [[ -n "$SLICE" ]]; then
  [[ -n "$EPIC" ]] || { echo "kanban-sync: --slice requires --epic" >&2; exit 1; }
  [[ -n "$SLICE_DONE" ]] || SLICE_DONE=1
  api_post /api/slice "$(printf '{"file":"%s","slice":%s,"done":%s,"operator":"%s"}' "$EPIC" "$SLICE" "$SLICE_DONE" "$OPERATOR")"
  echo "kanban-sync: WBS ${SLICE} → $([ "$SLICE_DONE" = 1 ] && echo done || echo open)"
fi

if [[ -n "$LIFECYCLE" ]]; then
  [[ -n "$EPIC" ]] || { echo "kanban-sync: --lifecycle requires --epic" >&2; exit 1; }
  api_post /api/lifecycle "$(printf '{"file":"%s","lifecycle_state":"%s","operator":"%s"}' "$EPIC" "$LIFECYCLE" "$OPERATOR")"
  echo "kanban-sync: lifecycle_state → ${LIFECYCLE}"
fi

if [[ -n "$PLAN_PATH" && -n "$PLAN_STATUS" ]]; then
  body="$(printf '{"file":"%s","status":"%s","operator":"%s"' "$PLAN_PATH" "$PLAN_STATUS" "$OPERATOR")"
  [[ -n "$EPIC" ]] && body="${body},$(printf '"epic":"%s"' "$EPIC")"
  body="${body}}"
  api_post /api/status "$body"
  echo "kanban-sync: ${PLAN_PATH} → ${PLAN_STATUS}"
fi

if [[ -n "$EPIC" ]]; then
  enc="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$EPIC")"
  echo "KANBAN_URL=${BASE}/?epic=${enc}"
else
  echo "KANBAN_URL=${BASE}/"
fi

rev="$(curl -sf "${BASE}/api/revision" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("revision",""))' 2>/dev/null || echo "?")"
echo "KANBAN_REVISION=${rev}"
