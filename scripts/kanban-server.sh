#!/usr/bin/env bash
# 启动 Epic Web 看板（127.0.0.1:7777）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/kanban-server.py" "$@"
