#!/usr/bin/env bash
# 全流程闭环启动：每次都重启 Epic 看板 + 打开浏览器
# 默认选 Plans/Epic/ 下最新的 Epic（按文件名倒序）。
# 用法：
#   ./scripts/full-cycle-boot.sh                # 重启服务 + 打开最新 Epic
#   ./scripts/full-cycle-boot.sh --epic Plans/Epic/2026-06-20-新版工作空间.md
#   ./scripts/full-cycle-boot.sh --no-open      # 仅重启服务，不弹浏览器
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
      echo "  每次都重启看板服务；不传 --epic 时默认选 Plans/Epic/ 下最新的 Epic。"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# 未指定 --epic：自动选最新的 Epic（文件名倒序，日期前缀越新越靠前）
if [[ -z "$EPIC" ]]; then
  EPIC="$(ls -1 "$ROOT"/Plans/Epic/*.md 2>/dev/null | sort -r | head -1)"
  if [[ -n "$EPIC" ]]; then
    EPIC="Plans/Epic/$(basename "$EPIC")"
    echo "kanban: 未指定 --epic，使用最新 Epic：$EPIC"
  fi
fi

URL="http://${HOST}:${PORT}/"
if [[ -n "$EPIC" ]]; then
  enc="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$EPIC")"
  URL="${URL}?epic=${enc}"
fi

kanban_up() {
  curl -sf "http://${HOST}:${PORT}/api/board" >/dev/null 2>&1
}

stop_server() {
  if [[ -f "$PIDFILE" ]]; then
    local pid; pid="$(cat "$PIDFILE" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$PIDFILE"
  fi
  # 兜底：清掉占用端口的旧 kanban 进程
  pkill -f "scripts/kanban-server.py" 2>/dev/null || true
  for _ in $(seq 1 20); do
    kanban_up || return 0
    sleep 0.15
  done
}

start_server() {
  echo "kanban: 重启服务 ${HOST}:${PORT} ..."
  stop_server
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
  opened=""
  # 后台/子进程环境下 open 可能拿不到 GUI 会话；多路尝试并回退
  if command -v open >/dev/null 2>&1; then
    if open "$URL" 2>/dev/null; then
      opened=1
    else
      # 显式指定默认浏览器再试一次
      open -b com.apple.Safari "$URL" 2>/dev/null && opened=1
    fi
  fi
  if [[ -z "$opened" ]]; then
    echo "kanban: 浏览器未能自动打开，请手动访问 ↓"
  fi
fi

echo "KANBAN_URL=$URL"
