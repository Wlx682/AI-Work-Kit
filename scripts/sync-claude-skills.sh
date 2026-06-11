#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/.claude/skills"
for d in "$ROOT/.cursor/skills"/*/; do
  name=$(basename "$d")
  rm -rf "$ROOT/.claude/skills/$name"
  cp -r "$d" "$ROOT/.claude/skills/$name"
done
echo "Synced .cursor/skills → .claude/skills"
