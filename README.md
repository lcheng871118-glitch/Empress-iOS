# Empress Pokémon 2D · iOS 移植工程

把《宝可梦竞技场2D》（Empress: Pokémon 2D Arena，玩家自制同人游戏）从安卓移植到 iOS 的工程。
游戏本体为**纯 JavaScript**（Web 前端 + Node.js 服务端），移植采用**同构换壳**方案：

- 安卓壳（Java + WebView + 内嵌 Node.js）→ iOS 壳（Swift + WKWebView + nodejs-mobile 内嵌 Node.js）
- **游戏本体（client/ server/ node_modules/）一行不改**

## 技术架构

```
┌─ 安卓壳（原版）─────────────┐      ┌─ iOS 壳（本工程）──────────────┐
│ Java Activity (17KB)       │      │ Swift GameViewController      │
│ WebView 加载 :3210          │      │ WKWebView 加载 :3210           │
│ libnode.so (Node 运行时)    │      │ NodeMobile.framework (Node 18)│
└──────────┬──────────────────┘      └──────────┬────────────────────┘
           │ 游戏本体（共享，纯 JS）              │
           ▼                                    ▼
      server/index.cjs ── express + ws + @pkmn/sim
      client/          ── Canvas 前端（HTML5）
      node_modules/    ── express / ws / @pkmn/sim 等（纯 JS 依赖）
```

## 目录结构

```
├── game/                    # 游戏本体（从安卓 APK 的 assets/game.zip 解包，本地验证用）
├── ios/
│   ├── xcodegen.yml         # Xcode 工程定义（CI 用 XcodeGen 生成）
│   ├── EmpressApp/          # iOS 壳源码（Swift + Bridging Header）
│   │   ├── AppDelegate.swift
│   │   ├── GameViewController.swift   # Node 启动 + WKWebView 容器
│   │   ├── Bridging-Header.h          # 引用 NodeMobile.h
│   │   ├── Info.plist                 # ATS 本地网络例外、横屏
│   │   └── Assets.xcassets            # App 图标
│   ├── game-data/           # 打包进 App 的游戏资源（构建时生成）
│   └── node-mobile-dist/    # nodejs-mobile iOS xcframework（构建时下载）
├── scripts/
│   └── build-ios.sh         # 一键构建脚本（下载运行时→资源→生成工程→构建→打包 ipa）
├── .github/workflows/
│   └── build-ios.yml        # GitHub Actions 云构建（macOS runner）
└── docs/
    └── INSTALL.md           # Windows + AltStore 自签安装指南
```

## 关键版本

| 组件 | 版本 | 说明 |
|---|---|---|
| 游戏 | 0.4.1（验证版） | itch.io 最新为 1.0.0，流程通用 |
| nodejs-mobile | v18.20.4 | 基于 Node 18.20.4，满足 express 5 要求 |
| 部署目标 | iOS 14.0+ | iPhone 横屏 |

## 构建方式

无 Mac 场景走 **GitHub Actions 云构建**：

1. 本仓库 push 到你的 GitHub
2. 把 `game-data.zip`（游戏资源包）上传到仓库 **Releases**
3. Actions → build-ios → **Run workflow**
4. 下载产物 `.ipa` → AltStore 签名安装（详见 `docs/INSTALL.md`）

有 Mac 的场景可直接本地执行：`bash scripts/build-ios.sh`（需 Xcode + XcodeGen）。

## 验证记录

- 本机（Windows / Node v22）启动 `node android-bootstrap.cjs`：
  - `/api/health` → `{"ok":true,"name":"Empress: Pokémon 2D","version":"0.4.0"}`
  - `/api/catalog` 返回全国图鉴 JSON；`/` 返回游戏前端 HTML ✓

## 免责声明

游戏为玩家自制的宝可梦同人作品，所有宝可梦 IP 归任天堂/Game Freak/The Pokémon Company 所有。本工程仅用于个人设备移植学习，不用于任何商业分发。
