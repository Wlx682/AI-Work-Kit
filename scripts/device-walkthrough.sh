#!/usr/bin/env bash
# WBS 10d — 真机自动启动 Claw + XCUITest 走查并导出截图到 Vault
set -euo pipefail

CLAWAI_ROOT="${CLAWAI_ROOT:-$HOME/git/ClawAI}"
VAULT_ROOT="${AI_WORK_KIT:-$(cd "$(dirname "$0")/.." && pwd)}"
WALKTHROUGH_SLUG="${WALKTHROUGH_SLUG:-walkthrough}"
SCREENSHOT_DIR="${SCREENSHOT_DIR:-$VAULT_ROOT/Plans/功能开发/screenshots/${WALKTHROUGH_SLUG}}"
RESULT_BUNDLE="${RESULT_BUNDLE:-/tmp/workspace-walkthrough-$(date +%Y%m%d-%H%M%S).xcresult}"
TEST_CLASS="ClawUITests/NMNewWorkspaceDeviceWalkthroughUITests/testWBS10dDeviceWalkthroughWithScreenshots"

export LANG=en_US.UTF-8

pick_device_udid() {
  if [[ -n "${DEVICE_UDID:-}" ]]; then
    echo "$DEVICE_UDID"
    return
  fi
  # 优先 USB 已连接真机
  local line udid name
  while IFS= read -r line; do
    if [[ "$line" =~ Found\ ([0-9A-Fa-f-]+)\ .*\ connected\ through\ USB ]]; then
      udid="${BASH_REMATCH[1]}"
      echo "$udid"
      return
    fi
  done < <(ios-deploy -c 2>/dev/null || true)
  while IFS= read -r line; do
    if [[ "$line" =~ Found\ ([0-9A-Fa-f-]+)\ .*\ connected ]]; then
      udid="${BASH_REMATCH[1]}"
      echo "$udid"
      return
    fi
  done < <(ios-deploy -c 2>/dev/null || true)
  echo ""
}

UDID="$(pick_device_udid)"
if [[ -z "$UDID" ]]; then
  echo "❌ 未检测到已连接 iOS 真机。请 USB 连接并信任，或 export DEVICE_UDID=..." >&2
  exit 1
fi

echo "📱 使用设备 UDID: $UDID"
mkdir -p "$SCREENSHOT_DIR"

cd "$CLAWAI_ROOT"
echo "📦 pod install（若已装则跳过）..."
pod install --silent 2>/dev/null || pod install

echo "🚀 安装并运行 UI 走查（会自动启动 App）..."
rm -rf "$RESULT_BUNDLE"
set +e
xcodebuild test \
  -workspace Claw.xcworkspace \
  -scheme ClawUITests \
  -destination "platform=iOS,id=$UDID" \
  -only-testing:"$TEST_CLASS" \
  -resultBundlePath "$RESULT_BUNDLE" \
  | tee /tmp/device-walkthrough-xcodebuild.log
TEST_EXIT=$?
set -e

echo "📸 导出截图到 $SCREENSHOT_DIR"
xcrun xcresulttool export attachments \
  --path "$RESULT_BUNDLE" \
  --output-path "$SCREENSHOT_DIR"

# 按附件名重命名为 D1-01-xxx.png 便于 Obsidian 引用
python3 - "$SCREENSHOT_DIR" <<'PY'
import json, os, re, sys
shot_dir = sys.argv[1]
manifest_path = os.path.join(shot_dir, "manifest.json")
if not os.path.isfile(manifest_path):
    sys.exit(0)
with open(manifest_path, encoding="utf-8") as f:
    data = json.load(f)
for entry in data:
    for att in entry.get("attachments", []):
        src_name = att.get("exportedFileName", "")
        human = att.get("suggestedHumanReadableName", src_name)
        short = re.sub(r"_.*", "", human)
        if not short.endswith(".png"):
            short += ".png"
        src = os.path.join(shot_dir, src_name)
        dst = os.path.join(shot_dir, short)
        if os.path.isfile(src) and src != dst:
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(src, dst)
PY

manifest_path="$SCREENSHOT_DIR/manifest.json"
if [[ -f "$manifest_path" ]]; then
  echo "OK screenshots exported to $SCREENSHOT_DIR (see manifest.json)"
  ls -la "$SCREENSHOT_DIR"/*.png 2>/dev/null | head -20 || true
else
  echo "WARN manifest.json missing; check xcresult: $RESULT_BUNDLE" >&2
fi

if [[ "$TEST_EXIT" -ne 0 ]]; then
  echo "⚠️ xcodebuild 退出码 $TEST_EXIT（截图若已导出仍可用）" >&2
  exit "$TEST_EXIT"
fi

echo ""
echo "截图目录：$SCREENSHOT_DIR"
echo "续做：把路径写入当前 Plans/功能开发/ 下的走查 plan（见 Templates/Figma设计走查模板）"
