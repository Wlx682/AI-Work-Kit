#!/usr/bin/env bash
# 扫描 Plans/ 各生命周期目录，生成全链路进度看板 Markdown
# 用法：./scripts/generate-pipeline-status.sh [--write]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INDEX="$ROOT/索引.md"
WRITE=false
[[ "${1:-}" == "--write" ]] && WRITE=true

status_icon() {
  case "$1" in
    已采纳|done) echo "✅" ;;
    进行中|doing|评审中|review|pending-change) echo "⏳" ;;
    *) echo "⬜" ;;
  esac
}

read_status() {
  awk 'BEGIN{in_fm=0} /^---$/{in_fm++; next} in_fm==1 && /^status:/{sub(/^status:[[:space:]]*/,""); print; exit}' "$1" 2>/dev/null || true
}

read_lifecycle() {
  awk 'BEGIN{in_fm=0} /^---$/{in_fm++; next} in_fm==1 && /^lifecycle_state:/{sub(/^lifecycle_state:[[:space:]]*/,""); print; exit}' "$1" 2>/dev/null || true
}

best_status_in_dir() {
  local proj="$1" dir="$2"
  [[ -d "$ROOT/$dir" ]] || { echo "⬜"; return; }
  shopt -s nullglob
  local f st best="⬜"
  for f in "$ROOT/$dir"/*.md; do
    [[ "$(basename "$f")" == *"$proj"* ]] || continue
    st="$(read_status "$f")"
    st="${st:-草稿}"
    case "$st" in
      已采纳|done) echo "✅"; return ;;
      进行中|doing|评审中|review|pending-change) best="⏳" ;;
    esac
  done
  echo "$best"
}

current_stage() {
  local proj="$1"
  local d f st lc
  for d in Plans/部署 Plans/自动化测试 Plans/功能开发 Plans/客户端技术方案 Plans/服务端技术方案 Plans/需求分析; do
    [[ -d "$ROOT/$d" ]] || continue
    shopt -s nullglob
    for f in "$ROOT/$d"/*.md; do
      [[ "$(basename "$f")" == *"$proj"* ]] || continue
      st="$(read_status "$f")"
      case "$st" in
        进行中|doing|评审中|pending-change)
          lc="$(read_lifecycle "$f")"
          echo "${lc:-${d#Plans/}}"
          return
          ;;
      esac
    done
  done
  echo "—"
}

# 收集项目名（去日期前缀、去子任务后缀）
PROJECTS_FILE="$(mktemp)"
for dir in Plans/需求分析 Plans/功能开发 Plans/客户端技术方案 Plans/服务端技术方案; do
  [[ -d "$ROOT/$dir" ]] || continue
  shopt -s nullglob
  for f in "$ROOT/$dir"/*.md; do
    bn="$(basename "$f" .md)"
    name="${bn#????-??-??-}"
    name="${name%-子任务*}"
    echo "$name"
  done
done | sort -u > "$PROJECTS_FILE"

TMP="$(mktemp)"
{
  today="$(date +%Y-%m-%d)"
  echo "## 全链路进度看板（自动生成）"
  echo ""
  echo "> 由 \`scripts/generate-pipeline-status.sh\` 生成 · 更新：${today}"
  echo ""
  echo "| 项目 | 需求 | 框架 | 开发 | 测试 | 部署 | Bug | 当前阶段 |"
  echo "|------|------|------|------|------|------|-----|----------|"

  if [[ ! -s "$PROJECTS_FILE" ]]; then
    echo "| （暂无进行中的 plan） | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | — |"
  else
    while IFS= read -r proj; do
      [[ -z "$proj" ]] && continue
      req="$(best_status_in_dir "$proj" "Plans/需求分析")"
      ac="$(best_status_in_dir "$proj" "Plans/客户端技术方案")"
      as="$(best_status_in_dir "$proj" "Plans/服务端技术方案")"
      if [[ "$ac" == "✅" || "$as" == "✅" ]]; then arch="✅"
      elif [[ "$ac" == "⏳" || "$as" == "⏳" ]]; then arch="⏳"
      else arch="⬜"; fi
      dev="$(best_status_in_dir "$proj" "Plans/功能开发")"
      tst="$(best_status_in_dir "$proj" "Plans/自动化测试")"
      dep="$(best_status_in_dir "$proj" "Plans/部署")"
      bug="$(best_status_in_dir "$proj" "Plans/Bug排查")"
      cur="$(current_stage "$proj")"
      # 开发已采纳且无进行中项 → 其余空列视为归档完成
      if [[ "$dev" == "✅" && "$cur" == "—" ]]; then
        [[ "$req" == "⬜" ]] && req="✅"
        [[ "$arch" == "⬜" ]] && arch="✅"
        [[ "$tst" == "⬜" ]] && tst="✅"
        [[ "$dep" == "⬜" ]] && dep="✅"
        cur="done"
      fi
      echo "| ${proj} | ${req} | ${arch} | ${dev} | ${tst} | ${dep} | ${bug} | ${cur} |"
    done < "$PROJECTS_FILE"
  fi

  echo ""
  echo "### 图例"
  echo ""
  echo "- ✅ 已采纳 / done"
  echo "- ⏳ 进行中 / 评审中 / pending-change"
  echo "- ⬜ 未开始或无 plan"
} > "$TMP"

cat "$TMP"
rm -f "$PROJECTS_FILE"

if $WRITE; then
  START="<!-- PIPELINE-STATUS-START -->"
  END="<!-- PIPELINE-STATUS-END -->"
  python3 - "$INDEX" "$TMP" "$START" "$END" <<'PY'
import sys
index_path, block_path, start, end = sys.argv[1:5]
with open(block_path) as f:
    block = f.read().rstrip() + "\n"
with open(index_path) as f:
    text = f.read()
si = text.index(start)
ei = text.index(end) + len(end)
with open(index_path, "w") as f:
    f.write(text[:si] + start + "\n" + block + end + text[ei:])
print("已写入", index_path)
PY
fi

rm -f "$TMP"
