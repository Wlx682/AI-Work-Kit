#!/usr/bin/env bash
# 全流程闭环启动：后台拉起 Epic 看板 + 打开浏览器
# 用法：
#   ./scripts/full-cycle-boot.sh
#   ./scripts/full-cycle-boot.sh --epic Plans/Epic/2026-06-20-新版工作空间.md
#   ./scripts/full-cycle-boot.sh --no-open   # 仅启动服务，不弹浏览器
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIDFILE="$ROOT/scripts/.kanban-server.pid"
LOG="$ROOT/scripts/.kanban-server.log"
PORT=7777
HOST="127.0.0.1"
EPIC=""
NO_OPEN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --epic) EPIC="${2:-}"; shift 2 ;;
    --no-open) NO_OPEN=1; shift ;;
    -h|--help)
      echo "Usage: full-cycle-boot.sh [--epic Plans/Epic/xxx.md] [--no-open]"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

URL="http://${HOST}:${PORT}/"
if [[ -n "$EPIC" ]]; then
  enc="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$EPIC")"
  URL="${URL}?epic=${enc}"
fi

kanban_up() {
  curl -sf "http://${HOST}:${PORT}/api/board" >/dev/null 2>&1
}

start_server() {
  if kanban_up; then
    echo "kanban: already running on ${HOST}:${PORT}"
    return 0
  fi
  echo "kanban: starting ${HOST}:${PORT} ..."
  nohup python3 "$ROOT/scripts/kanban-server.py" >>"$LOG" 2>&1 &
  echo "$!" >"$PIDFILE"
  for _ in $(seq 1 40); do
    if kanban_up; then
      echo "kanban: ready (pid $(cat "$PIDFILE" 2>/dev/null || echo '?'))"
      return 0
    fi
    sleep 0.15
  done
  echo "kanban: failed to start — see $LOG" >&2
  exit 1
}

start_server

if [[ "$NO_OPEN" != "1" ]]; then
  if command -v open >/dev/null 2>&1; then
    open "$URL"
  else
    echo "Open in browser: $URL"
  fi
fi

echo "KANBAN_URL=$URL"
