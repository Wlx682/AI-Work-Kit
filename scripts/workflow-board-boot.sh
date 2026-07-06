#!/usr/bin/env bash
# 工作流看板启动：每次都重启 Epic 看板 + 打开浏览器
# 未指定 Epic 时仅在唯一 Epic 的情况下自动选择；多个 Epic 必须显式传 --epic。
# 用法：
#   ./scripts/workflow-board-boot.sh                # 重启服务 + 打开最新 Epic
#   ./scripts/workflow-board-boot.sh --epic Plans/Epic/2026-06-20-新版工作空间.md
#   ./scripts/workflow-board-boot.sh --no-open      # 仅重启服务，不弹浏览器
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIDFILE="$ROOT/scripts/.kanban-server.pid"
LOG="$ROOT/scripts/.kanban-server.log"
PORT=7777
HOST="127.0.0.1"
EPIC=""
NO_OPEN=""
NEW_REQUIREMENT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --epic) EPIC="${2:-}"; shift 2 ;;
    --no-open) NO_OPEN=1; shift ;;
    --new-requirement) NEW_REQUIREMENT=1; shift ;;
    -h|--help)
      echo "Usage: workflow-board-boot.sh [--epic Plans/Epic/xxx.md] [--no-open] [--new-requirement]"
      echo "  每次都重启看板服务；不传 --epic 时默认选 Plans/Epic/ 下最新的 Epic。"
      echo "  --new-requirement：新需求阶段，看板尚未创建，只起服务不弹浏览器。"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# 新需求阶段：看板还没创建，不要自动选旧 Epic、也不弹浏览器
if [[ -n "$NEW_REQUIREMENT" ]]; then
  EPIC=""
fi

# 未指定 --epic：只有唯一 Epic 时自动选择；多个 Epic 必须显式选择，避免并行项目误操作。
if [[ -z "$EPIC" && -z "$NEW_REQUIREMENT" ]]; then
  epic_candidates=()
  while IFS= read -r f; do
    epic_candidates+=("$f")
  done < <(find "$ROOT/Plans/Epic" -maxdepth 1 -type f -name "*.md" 2>/dev/null | sort -r)
  if [[ ${#epic_candidates[@]} -eq 1 ]]; then
    EPIC="Plans/Epic/$(basename "${epic_candidates[0]}")"
    echo "kanban: 未指定 --epic，使用唯一 Epic：$EPIC"
  elif [[ ${#epic_candidates[@]} -gt 1 ]]; then
    echo "kanban: 检测到多个 Epic，请显式指定 --epic，避免误操作：" >&2
    for f in "${epic_candidates[@]}"; do
      echo "  - Plans/Epic/$(basename "$f")" >&2
    done
    exit 1
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

# 新需求 / 还没有任何 Epic（看板为空）时，只起服务不弹浏览器
if [[ -z "$EPIC" && "$NO_OPEN" != "1" ]]; then
  if [[ -n "$NEW_REQUIREMENT" ]]; then
    echo "kanban: 新需求阶段，看板尚未创建，跳过自动打开浏览器；Epic 建好后再 boot 即会自动打开"
  else
    echo "kanban: 暂无 Epic（看板为空），跳过自动打开浏览器；创建 Epic 后再 boot 即会自动打开"
  fi
  NO_OPEN=1
fi

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
