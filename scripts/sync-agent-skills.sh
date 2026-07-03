#!/usr/bin/env bash
# Backward-compatible wrapper for multi-agent skill sync.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/scripts/sync-claude-skills.sh" "$@"
