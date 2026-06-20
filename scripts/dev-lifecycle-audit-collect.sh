#!/usr/bin/env bash
# Epic 开发流程机械取证（dev-lifecycle-audit 前置）
# 用法：./scripts/dev-lifecycle-audit-collect.sh [Plans/Epic]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EPIC_DIR="${1:-Plans/Epic}"
EPIC_PATH="$ROOT/$EPIC_DIR"

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

resolve_path() {
  local p="$1"
  [[ "$p" == /* ]] && echo "$p" || p="$ROOT/$p"
  [[ "$p" == *.md ]] || p="${p}.md"
  echo "$p"
}

wbs_counts() {
  local f="$1"
  local total=0 done=0
  while IFS= read -r line; do
    [[ "$line" =~ ^\[[xX]\] ]] && done=$((done + 1)) && total=$((total + 1)) && continue
    [[ "$line" =~ ^\[[[:space:]]\] ]] && total=$((total + 1))
  done < <(sed -n '/^```$/,/^```$/p' "$f" | grep -E '^\[[ xX]\]' || true)
  echo "$done/$total"
}

echo "# dev-lifecycle-audit 机械取证"
echo "# vault: $ROOT"
echo "# epics: $EPIC_DIR"
echo "# generated: $(date +%Y-%m-%d)"
echo ""

if [[ ! -d "$EPIC_PATH" ]]; then
  echo "（Epic 目录不存在）"
  exit 0
fi

shopt -s nullglob
files=("$EPIC_PATH"/*.md)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "（无 Epic plan）"
  exit 0
fi

for f in "${files[@]}"; do
  [[ "$(basename "$f")" == .* ]] && continue
  rel="${f#"$ROOT"/}"
  name="$(basename "$f" .md)"
  epic_id="$(read_fm epic_id "$f")"
  status="$(read_fm status "$f")"
  lc="$(read_fm lifecycle_state "$f")"
  p0="$(read_fm p0_open "$f")"
  biz="$(read_fm 含业务逻辑 "$f")"
  wbs="$(wbs_counts "$f")"

  echo "## Epic: $name"
  echo "path: $rel"
  echo "epic_id: ${epic_id:-（无）}"
  echo "status: ${status:-（无）}"
  echo "lifecycle_state: ${lc:-（无）}"
  echo "p0_open: ${p0:-0}"
  echo "含业务逻辑: ${biz:-（无）}"
  echo "wbs_done_total: $wbs"
  echo ""

  while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]+(requirement|architecture|development|test|deploy):[[:space:]]+(.+)$ ]] || continue
    stage="${BASH_REMATCH[1]}"
    raw="${BASH_REMATCH[2]}"
    raw="${raw%%#*}"
    raw="$(echo "$raw" | tr -d ' ')"
    [[ "$raw" == "null" || -z "$raw" ]] && {
      echo "  plan_${stage}: null"
      echo "  plan_${stage}_exists: false"
      echo ""
      continue
    }
    sub="$(resolve_path "$raw")"
    if [[ -f "$sub" ]]; then
      st="$(read_fm status "$sub")"
      sub_lc="$(read_fm lifecycle_state "$sub")"
      sub_p0="$(read_fm p0_open "$sub")"
      echo "  plan_${stage}: $raw"
      echo "  plan_${stage}_exists: true"
      echo "  plan_${stage}_status: ${st:-（无）}"
      echo "  plan_${stage}_lifecycle: ${sub_lc:-（无）}"
      [[ -n "$sub_p0" ]] && echo "  plan_${stage}_p0_open: $sub_p0"
    else
      echo "  plan_${stage}: $raw"
      echo "  plan_${stage}_exists: false"
    fi
    echo ""
  done < "$f"

  dev_raw="$(awk '
    /^plans:/ { in_p=1; next }
    in_p && /^[^ ]/ { exit }
    in_p && /development:/ { sub(/.*development:[[:space:]]*/, ""); gsub(/"/, ""); print; exit }
  ' "$f" | tr -d ' ')"
  if [[ -n "$dev_raw" && "$dev_raw" != "null" ]]; then
    dev_file="$(resolve_path "$dev_raw")"
    if [[ -f "$dev_file" ]]; then
      gate_out="$(bash "$ROOT/scripts/plan-gate-check.sh" "$dev_file" --stage development 2>&1 || true)"
      echo "  gate_development: $gate_out"
    fi
  fi
  echo "---"
  echo ""
done
