# Empress: Pokémon 2D · iOS 非官方移植版（中文说明）

[![Build](https://github.com/lcheng871118-glitch/Empress-iOS/actions/workflows/build-ios.yml/badge.svg)](https://github.com/lcheng871118-glitch/Empress-iOS/actions/workflows/build-ios.yml)

《宝可梦竞技场2D》（**Empress: Pokémon 2D Arena**，作者 **Omniscye** 的玩家自制同人游戏）的 iOS 非官方移植。游戏本体以**本地 Node.js 服务端 + WKWebView 加载原版 HTML5 前端**的方式运行——**游戏代码一行未改**。

支持 **iOS 14+**，可通过 **TrollStore**（推荐，无需重签）或 **AltStore**（免费 Apple ID，每 7 天重签）安装。

> 本工程仅用于个人设备移植学习。宝可梦 IP 归任天堂 / Game Freak / The Pokémon Company；游戏版权归原作者 Omniscye。

---

## 技术方案

解包安卓 APK（v0.4.1）后发现游戏是**纯 JavaScript 技术栈**：17KB Java 启动桥 + libnode.so + WebView 加载本地 `http://127.0.0.1:3210`。游戏本体 = HTML5 Canvas 前端 + Node.js(Express) 服务端，原生层零游戏逻辑。

因此移植采用**同构换壳**：

```
┌───────────────────────────────────────────────────────┐
│  EmpressPokemon2D.app                                  │
│  ├─ Swift 壳（AppDelegate / GameViewController）        │
│  ├─ NodeMobile.framework（nodejs-mobile v18.20.4）      │
│  ├─ game-data/    （原版服务端 + 前端，未改动）           │
│  └─ WKWebView  →  http://127.0.0.1:3210                 │
└───────────────────────────────────────────────────────┘
```

## 功能

- ✅ 完整单人战役 / 组队 / 实时对战（与安卓同引擎）
- ✅ 存档保存到 App Documents（`empress-profile`）
- ✅ 横屏全屏
- ✅ TrollStore 安装免重签
- ✅ GitHub Actions 云构建，**无需 Mac**
- ✅ 附带局域网网页版（`启动局域网版.bat`），iPhone 浏览器即点即玩

## 快速开始

**方式 A：直接下载 .ipa（最省事）**

1. 到 [Releases 页面](https://github.com/lcheng871118-glitch/Empress-iOS/releases) 下载 `Empress-Pokemon-2D-iOS-0.4.1.ipa`
2. AirDrop / 网盘传到 iPhone
3. 用 **TrollStore** 打开安装（详见 [INSTALL.md](INSTALL.md)）

**方式 B：自己构建** → [BUILD.md](BUILD.md)

## 安装

### TrollStore（推荐）

1. 设备安装 [TrollStore](https://trollstore.app)（需支持的 iOS 版本）
2. 把 `.ipa` 传到 iPhone（AirDrop / 网盘等）
3. 用 TrollStore 打开 → 点 **Install**
4. 完成，永不需要重签

> 本 IPA 自带 JIT entitlement（`allow-jit`），TrollStore 安装时保留，内嵌 Node 引擎秒级启动。

### AltStore（免费 Apple ID，7 天重签一次）

1. 电脑装 AltServer（Windows 需先装 iTunes + iCloud）
2. iPhone 连电脑 USB → AltServer 安装 AltStore → 用**小号 Apple ID** 登录
3. AltStore → *My Apps* → **+** → 选 `.ipa`
4. 首次启动：设置 → 通用 → VPN与设备管理 → 信任该 Apple ID
5. 到期前重签：AltStore → *Refresh All*（一键）

## 自己构建

CI 在云端（macOS runner）构建 `.ipa`，**无需 Mac**：

1. Fork / clone 本仓库
2. 把 `game-data.zip`（游戏资源包，约 185MB）上传到 **Releases**——workflow 自动下载 latest release 的 `game-data.zip`
3. Actions → **build-ios** → **Run workflow**
4. 下载产物 `.ipa` 安装

本地构建（macOS 需 Xcode + XcodeGen）：`bash scripts/build-ios.sh`。

## 升级到新版游戏

作者会在 itch.io 陆续发布新版：

1. 下载新版 APK，解出 `assets/game.zip` → 重新打包为 `game-data.zip`
2. 替换 GitHub Release asset
3. 重新运行 workflow 即可

## 常见问题（踩坑记录）

| 现象 | 原因与修复 |
|---|---|
| TrollStore：`ldid: operator(): No such file or directory` | `node_modules/.bin` 里的**符号链接**导致 ldid 递归签名失败。已修复（打包前 `find ... -type l -delete`） |
| 符号链接清完后仍报同样错误 | App 名含非 ASCII（`Pokémon`）→ macOS zip（NFC）与 iOS 文件系统（NFD）Unicode 规范化不一致。改用纯 ASCII `PRODUCT_NAME` |
| “游戏引擎启动失败”秒出（0 秒） | 健康检查遇 `Connection refused` 瞬时耗尽重试，而 Node 还在初始化。已修复：JIT entitlement + socket 长等待（最长 10 分钟） |
| 日志 `Warning: disabling flag --expose_wasm ...` | jitless 模式下 V8 的无害警告，不影响游戏 |
| Actions 下载 Release 失败 | 共享 runner IP 未认证调用 GitHub API 被限流。所有 Release API 调用需带 `Authorization: token GITHUB_TOKEN` |
| xcodegen 工程格式 77 读不了 | 老 runner 读不了 Xcode 16 工程，需 `runs-on: macos-15` |

## 目录结构

```
├─ ios/
│  ├─ EmpressApp/        # Swift 壳：AppDelegate、GameViewController（Node 启动 + WKWebView）、Info.plist
│  ├─ entitlements.plist # JIT entitlements（TrollStore 会保留）
│  └─ project.yml        # XcodeGen 配置
├─ scripts/
│  ├─ build-ios.sh       # 一键构建：资源 → xcodegen → xcodebuild → 签名 → .ipa
│  ├─ bootstrap-ios.cjs  # iOS 版服务端入口（仓库版，覆盖 game-data 内旧版）
│  └─ ci-monitor.ps1     # Windows 下触发 + 监控 GitHub Actions
├─ .github/workflows/build-ios.yml  # 云构建（macos-15 runner）
├─ docs/INSTALL.md · docs/BUILD.md · docs/README.zh-CN.md
└─ 启动局域网版.bat      # 局域网网页版：电脑开服务，iPhone Safari 直接玩
```

## 快速开始：局域网网页版（不装 App 也能玩）

1. 双击 `启动局域网版.bat`（服务自动检测启动）
2. iPhone 连**同一 Wi-Fi**，Safari 打开 `http://192.168.1.80:3210`
3. 全功能游玩，存档自动保存到 `game-web/profile`
4. 想更接近 App：Safari → 分享 → 添加到主屏幕

> 电脑 IP 变化时，`ipconfig` 查看新 IPv4 地址。

## 验证记录

- 本机（Windows / Node v22）`node android-bootstrap.cjs`：
  - `/api/health` → `{"ok":true,"name":"Empress: Pokémon 2D","version":"0.4.0"}`
  - `/api/catalog` 返回全国图鉴 JSON；`/` 返回游戏前端 HTML ✓
- iPhone（TrollStore 安装，iOS 14+）实测可进入游戏并游玩 ✓

## 许可与免责

- **移植壳层**（Swift 源码、脚本、workflow、文档）© 2026 lcheng871118-glitch：允许查看、fork、构建、自用；**修改或发布衍生版本需事先获得作者同意**（见仓库 [LICENSE](LICENSE)）。
- **游戏本体**（`game-data/`）© 原作者 **Omniscye**，随仓仅用于个人学习，禁止商业分发。
- **宝可梦** IP 归任天堂 / Game Freak / The Pokémon Company。

## 致谢

- **Omniscye** — 原版游戏
- [nodejs-mobile](https://github.com/nodejs-mobile/nodejs-mobile) — iOS 上的 Node.js 运行时
- [XcodeGen](https://github.com/yonaskolb/XcodeGen) — Xcode 工程生成
