#!/bin/bash
# =============================================================
# 宝可梦竞技场2D iOS 移植 —— 一键构建脚本（在 macOS / CI 运行）
# 产出：Empress-Pokemon-2D-iOS-<version>.ipa（ad-hoc 占位签名，供 AltStore 重签）
# =============================================================
set -euxo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IOS_DIR="$ROOT_DIR/ios"
NODE_MOBILE_VERSION="v18.20.4"
GAME_VERSION="${GAME_VERSION:-0.4.1}"

cd "$ROOT_DIR"

# ---------- 1. 获取 nodejs-mobile iOS 预编译 xcframework ----------
NODE_MOBILE_DIST="$IOS_DIR/node-mobile-dist"
if [ ! -d "$NODE_MOBILE_DIST/NodeMobile.xcframework" ]; then
  echo ">> 下载 nodejs-mobile ${NODE_MOBILE_VERSION} iOS 包"
  curl -sL -o /tmp/node-mobile-ios.zip \
    "https://github.com/nodejs-mobile/nodejs-mobile/releases/download/${NODE_MOBILE_VERSION}/nodejs-mobile-v18.20.4-ios.zip"
  rm -rf "$NODE_MOBILE_DIST"
  mkdir -p "$NODE_MOBILE_DIST"
  unzip -q /tmp/node-mobile-ios.zip -d "$NODE_MOBILE_DIST"
fi
echo ">> xcframework 已就绪：$(ls "$NODE_MOBILE_DIST"/NodeMobile.xcframework 2>/dev/null || echo MISSING)"

# ---------- 2. 准备 game-data 游戏资源（来自 game/ 本体，去重压缩包） ----------
GAME_DATA="$IOS_DIR/game-data"
rm -rf "$GAME_DATA"
mkdir -p "$GAME_DATA"
if [ ! -d "$ROOT_DIR/game/server" ]; then
  echo "ERROR: $ROOT_DIR/game 目录缺少 server/，请确认 game 本体已解包（或用 make-game-data 重新打包）" >&2
  exit 1
fi
cp -R "$ROOT_DIR/game/client"    "$GAME_DATA/"
cp -R "$ROOT_DIR/game/server"    "$GAME_DATA/"
cp -R "$ROOT_DIR/game/node_modules" "$GAME_DATA/"
cp "$ROOT_DIR/game/package.json"         "$GAME_DATA/"
cp "$ROOT_DIR/game/android-bootstrap.cjs" "$GAME_DATA/"
if [ -f "$ROOT_DIR/game/LICENSE.html" ]; then
  cp "$ROOT_DIR/game/LICENSE.html" "$GAME_DATA/"
fi
echo ">> game-data 资源大小：$(du -sh "$GAME_DATA" | cut -f1)"

# ---------- 3. 生成 Xcode 工程 ----------
if ! command -v xcodegen >/dev/null 2>&1; then
  echo ">> 安装 xcodegen"
  brew install xcodegen
fi
cd "$IOS_DIR"
xcodegen generate
echo ">> Xcode 工程已生成"

# ---------- 4. 构建（不签名，产出 .app） ----------
xcodebuild -project EmpressApp.xcodeproj \
  -scheme EmpressApp \
  -configuration Release \
  -sdk iphoneos \
  -derivedDataPath "$IOS_DIR/build" \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO \
  build

APP_DIR="$IOS_DIR/build/Build/Products/Release-iphoneos"
# PRODUCT_NAME 含空格（"Empress Pokémon 2D"），实际产物名不等于 target 名，用通配符定位
APP_PATH=$(find "$APP_DIR" -maxdepth 1 -name "*.app" 2>/dev/null | head -1)
if [ ! -d "$APP_PATH" ]; then
  echo "ERROR: 构建产物不存在 $APP_DIR" >&2
  exit 1
fi
echo ">> 构建完成：$APP_PATH"

# ---------- 5. 打包 .ipa（ad-hoc 占位签名，AltStore 会用 Apple ID 重签） ----------
cd "$IOS_DIR"
rm -rf Payload Empress-Pokemon-2D-iOS-${GAME_VERSION}.ipa
mkdir -p Payload
cp -R "$APP_PATH" Payload/

# 先对嵌入的动态库签名，再对 App 主体签名（ad-hoc 占位签名）
if [ -d "Payload/EmpressApp.app/Frameworks/NodeMobile.framework" ]; then
  codesign --force --sign - "Payload/EmpressApp.app/Frameworks/NodeMobile.framework"
fi
codesign --force --sign - "Payload/EmpressApp.app"

zip -qry "Empress-Pokemon-2D-iOS-${GAME_VERSION}.ipa" Payload
rm -rf Payload
echo ">> 产物：$IOS_DIR/Empress-Pokemon-2D-iOS-${GAME_VERSION}.ipa"
