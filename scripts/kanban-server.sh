#!/usr/bin/env bash
# 启动 Epic Web 看板（127.0.0.1:$KANBAN_PORT，默认 7777）
# 默认：后台启动 + 日志（/tmp/kanban.log），端口已在监听则直接退出
# 前台：bash scripts/kanban-server.sh -f
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${KANBAN_PORT:-7777}"
LOG="${KANBAN_LOG:-/tmp/kanban.log}"

case "${1:-}" in
  -f|--foreground)
    shift
    exec python3 "$ROOT/scripts/kanban-server.py" "$@"
    ;;
esac

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "看板已在运行：http://127.0.0.1:${PORT}/  (log: ${LOG})"
  exit 0
fi

nohup python3 "$ROOT/scripts/kanban-server.py" "$@" >"$LOG" 2>&1 &
disown || true
sleep 0.8
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "看板已启动：http://127.0.0.1:${PORT}/  (log: ${LOG})"
else
  echo "启动失败，最近日志：" >&2
  tail -20 "$LOG" >&2 || true
  exit 1
fi
