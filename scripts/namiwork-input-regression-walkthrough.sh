#!/usr/bin/env bash
# NAMIWork 输入栏重构 — WBS 4–10 真机走查辅助
# 用法：
#   ./scripts/namiwork-input-regression-walkthrough.sh [--wbs 4] [--build] [--device UDID]
#   EPIC=Plans/Epic/2026-06-20-输入重构-原case完整性排查.md ./scripts/namiwork-input-regression-walkthrough.sh
set -euo pipefail

VAULT="$(cd "$(dirname "$0")/.." && pwd)"
NAMI_ROOT="${NAMI_ROOT:-$HOME/git/NamiWork}"
BRANCH="${BRANCH:-feature/0618/agent_metion}"
WBS="${WBS:-4}"
DO_BUILD=0
DEVICE_UDID="${DEVICE_UDID:-}"
EPIC="${EPIC:-Plans/Epic/2026-06-20-输入重构-原case完整性排查.md}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wbs) WBS="${2:-4}"; shift 2 ;;
    --build) DO_BUILD=1; shift ;;
    --device) DEVICE_UDID="${2:-}"; shift 2 ;;
    --epic) EPIC="${2:-}"; shift 2 ;;
    -h|--help)
      sed -n '2,8p' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *) echo "Unknown: $1" >&2; exit 1 ;;
  esac
done

pick_device() {
  [[ -n "$DEVICE_UDID" ]] && { echo "$DEVICE_UDID"; return; }
  python3 - <<'PY' 2>/dev/null || true
import subprocess, re
out = subprocess.check_output(["xcrun", "xctrace", "list", "devices"], text=True, stderr=subprocess.DEVNULL)
for line in out.splitlines():
    m = re.search(r"longxiang.*\(([0-9A-Fa-f-]+)\)", line)
    if m and "Offline" not in line:
        print(m.group(1))
        break
PY
}

echo "=== NAMIWork 输入栏回归走查 · WBS ${WBS} ==="
echo "仓库: ${NAMI_ROOT} · 分支: ${BRANCH}"
echo "Epic: ${EPIC}"
echo "Checklist: Plans/客户端技术方案/2026-06-20-输入重构-原case完整性排查.md §五"
echo ""

cd "$NAMI_ROOT"
cur="$(git branch --show-current)"
if [[ "$cur" != "$BRANCH" ]]; then
  echo "⚠️  当前分支 ${cur} ≠ ${BRANCH}，请先 checkout"
fi

UDID="$(pick_device || true)"
if [[ -n "$UDID" ]]; then
  echo "📱 设备 UDID: ${UDID}"
else
  echo "⚠️  未检测到 longxiang 真机，走查步骤仍可用（跳过 --build）"
fi

if [[ "$DO_BUILD" -eq 1 ]]; then
  [[ -n "$UDID" ]] || { echo "❌ --build 需要已连接真机或 DEVICE_UDID" >&2; exit 1; }
  echo "📦 pod install..."
  pod install --silent 2>/dev/null || pod install
  echo "🔨 xcodebuild NAMIWork → 真机（workspace）..."
  xcodebuild build \
    -workspace NAMIWork.xcworkspace \
    -scheme NAMIWork \
    -destination "platform=iOS,id=${UDID}" \
    -quiet
  APP="$(find ~/Library/Developer/Xcode/DerivedData/NAMIWork-*/Build/Products/Debug-iphoneos/NAMIWork.app -maxdepth 0 2>/dev/null | head -1)"
  if [[ -n "$APP" && -d "$APP" ]]; then
    echo "📲 安装到真机..."
    xcrun devicectl device install app --device "${UDID}" "$APP" 2>&1 | grep -E 'App installed|bundleID|error:' || true
    echo "🚀 启动 App（bundle: com.qihoo.namiwork.dev）..."
    xcrun devicectl device process launch --device "${UDID}" com.qihoo.namiwork.dev 2>&1 || true
  fi
  echo "✅ Build Succeeded"
fi

print_wbs4() {
  cat <<'EOF'
--- WBS 4 · Slate/Porton（P0）---
[ ] T-SLATE-01  ChatVC · 输入 @ → 取消/删光 → 无隐藏 @/@@
[ ] T-SLATE-02  HomeShell+ChatVC · 多行输入/删改/光标 → 行距正常无 crash
[ ] T-SLATE-03  ChatVC 专家团 · @ Provider 可插入引用 chip
[ ] T-QUEUE-01  ChatVC · 打开旧 formTextList 队列项 → Slate 可编辑不丢字

代码静态（2026-06-20）：
  T-SLATE-01 ✅ NMPortonAtProcessor 拦截 @ 不写文档；取消 callback 不 insert
  T-QUEUE-01 ✅ NMInputState 解码 formTextList → NMLegacyFormBlock.toDocument
  T-SLATE-02/03 ⏳ 待真机

结果回填：方案 §五「结果」列 + Plans/功能开发/2026-06-20-输入重构-原case完整性排查.md §六
EOF
}

print_wbs5() {
  cat <<'EOF'
--- WBS 5 · @ chip（P0）---
[ ] T-MENTION-01~07 见方案 §五
入口：ChatVC 专家团 / 单龙虾对照
EOF
}

print_wbs6() {
  cat <<'EOF'
--- WBS 6 · ASR/长按（P0）---
[ ] T-ASR-01~03 · 空文本长按 · Dark+New 输入栏
EOF
}

case "$WBS" in
  4) print_wbs4 ;;
  5) print_wbs5 ;;
  6) print_wbs6 ;;
  *) echo "WBS ${WBS}：见 Plans/客户端技术方案/2026-06-20-输入重构-原case完整性排查.md §四–§五" ;;
esac

echo ""
echo "看板同步: bash ${VAULT}/scripts/kanban-sync.sh --boot --epic ${EPIC}"
echo "WBS 完成后: bash ${VAULT}/scripts/kanban-sync.sh --epic ${EPIC} --slice ${WBS} --done"
