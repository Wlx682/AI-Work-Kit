#!/usr/bin/env bash
# 扫描 Plans/Epic/*.md，输出看板 JSON（只读）
# 用法：./scripts/epic-scan.sh [epic.md]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-}"

read_fm() {
  awk -v key="$1" '
    BEGIN { in_fm=0 }
    /^---$/ { in_fm++; next }
    in_fm==1 && $0 ~ "^" key ":" {
      sub("^" key ":[[:space:]]*", "")
      gsub(/"/, "")
      print
      exit
    }
  ' "$2"
}

scan_epic() {
  local f="$1"
  local bn epic_id status lc p0
  epic_id="$(read_fm epic_id "$f")"
  status="$(read_fm status "$f")"
  lc="$(read_fm lifecycle_state "$f")"
  p0="$(read_fm p0_open "$f")"
  bn="$(basename "$f" .md)"

  local slices_json="["
  local first=1
  local line checked label
  while IFS= read -r line; do
    if [[ "$line" =~ ^\[([xX])\][[:space:]]*([0-9]+)\.[[:space:]]*(.+)$ ]]; then
      checked="true"
      [[ "${BASH_REMATCH[1]}" == "x" || "${BASH_REMATCH[1]}" == "X" ]] || checked="false"
      label="${BASH_REMATCH[3]}"
      label="${label//\\/\\\\}"
      label="${label//\"/\\\"}"
      [[ $first -eq 1 ]] || slices_json+=","
      first=0
      slices_json+="{\"n\":${BASH_REMATCH[2]},\"done\":${checked},\"label\":\"${label}\"}"
    elif [[ "$line" =~ ^\[[[:space:]]\][[:space:]]*([0-9]+)\.[[:space:]]*(.+)$ ]]; then
      label="${BASH_REMATCH[2]}"
      label="${label//\\/\\\\}"
      label="${label//\"/\\\"}"
      [[ $first -eq 1 ]] || slices_json+=","
      first=0
      slices_json+="{\"n\":${BASH_REMATCH[1]},\"done\":false,\"label\":\"${label}\"}"
    fi
  done < <(sed -n '/^```$/,/^```$/p' "$f" | grep -E '^\[[ xX]\]' || true)
  slices_json+="]"

  printf '{"file":"%s","name":"%s","epic_id":"%s","status":"%s","lifecycle_state":"%s","p0_open":%s,"slices":%s}\n' \
    "${f#$ROOT/}" "$bn" "${epic_id:-}" "${status:-}" "${lc:-}" "${p0:-0}" "$slices_json"
}

if [[ -n "$TARGET" ]]; then
  [[ -f "$TARGET" ]] || { echo "[]"; exit 1; }
  echo "["
  scan_epic "$TARGET"
  echo "]"
  exit 0
fi

echo "["
first=1
shopt -s nullglob
for f in "$ROOT"/Plans/Epic/*.md; do
  [[ "$(basename "$f")" == .* ]] && continue
  [[ $first -eq 1 ]] || echo ","
  first=0
  scan_epic "$f"
done
echo "]"
