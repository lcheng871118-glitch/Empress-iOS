# Empress: Pokémon 2D · Unofficial iOS Port

[![Build](https://github.com/lcheng871118-glitch/Empress-iOS/actions/workflows/build-ios.yml/badge.svg)](https://github.com/lcheng871118-glitch/Empress-iOS/actions/workflows/build-ios.yml)
[![Release](https://img.shields.io/github/v/release/lcheng871118-glitch/Empress-iOS)](https://github.com/lcheng871118-glitch/Empress-iOS/releases)

An unofficial iOS port of **[Empress: Pokémon 2D Arena](https://empress-pokemon-2d.itch.io)** (v0.4.1), the fan-made Pokémon battle game by **Omniscye**. The game runs as a local Node.js server inside the app, with a WKWebView rendering the original HTML5 client — **zero changes to the game code**.

Works on **iOS 14+**, installable via **TrollStore** (recommended, no re-signing) or **AltStore** (free Apple ID, re-sign every 7 days).

> Personal-learning port. Pokémon IP belongs to Nintendo / Game Freak / The Pokémon Company. The game is © its original author Omniscye.

---

## How it works

The Android APK turned out to be a pure-JavaScript game: a 17 KB Java launcher + `libnode.so` + a WebView pointed at a local server (`http://127.0.0.1:3210`). The game itself (`game-data/`) is an HTML5 Canvas client plus a Node.js/Express server — zero native game logic.

So the port is a **same-code wrapper swap**:

```
┌───────────────────────────────────────────────────────┐
│  EmpressPokemon2D.app                                  │
│  ├─ Swift shell (AppDelegate / GameViewController)      │
│  ├─ NodeMobile.framework (nodejs-mobile v18.20.4)       │
│  ├─ game-data/    (original server + client, untouched) │
│  └─ WKWebView  →  http://127.0.0.1:3210                 │
└───────────────────────────────────────────────────────┘
```

## Features

- ✅ Full single-player campaign, team builder, real-time battles (same engine as Android)
- ✅ Saves stored in the app's Documents folder (`empress-profile`)
- ✅ Landscape-only, fullscreen
- ✅ No re-signing for **TrollStore** installs
- ✅ Cloud builds via **GitHub Actions** — no Mac needed
- ✅ LAN browser version included for instant play (`启动局域网版.bat`)

## Quick start

**Option A — download the .ipa (easiest)**

1. Grab `Empress-Pokemon-2D-iOS-0.4.1.ipa` from the [Releases page](https://github.com/lcheng871118-glitch/Empress-iOS/releases).
2. AirDrop / upload it to your iPhone.
3. Open it with **TrollStore** → *Install* (see [INSTALL.md](docs/INSTALL.md)).

**Option B — build it yourself** → [BUILD.md](docs/BUILD.md)

## Install

### TrollStore (recommended)

1. Install [TrollStore](https://trollstore.app) on your device (requires a supported iOS version).
2. Send the `.ipa` to your iPhone (AirDrop, cloud drive, ...).
3. Open the `.ipa` with TrollStore → tap **Install**.
4. Done — no re-signing, ever.

> The IPA ships with JIT entitlements (`allow-jit`), which TrollStore preserves at install time, so the embedded Node engine starts in seconds.

### AltStore (free Apple ID, re-sign every 7 days)

1. Install AltServer on a Mac/Windows PC (Windows needs iTunes + iCloud).
2. Connect your iPhone, install AltStore via AltServer, sign in with a **throwaway Apple ID**.
3. In AltStore → *My Apps* → **+** → pick the `.ipa`.
4. First launch: Settings → General → VPN & Device Management → trust your Apple ID.
5. Re-sign before expiry: AltStore → *Refresh All* (one tap; PC must be reachable).

Full details → [INSTALL.md](docs/INSTALL.md)

## Build from source

The CI workflow builds the `.ipa` in the cloud (macOS runner), so **no Mac is needed**:

1. Fork / clone this repo.
2. Upload your `game-data.zip` (game asset bundle, ~185 MB) to **Releases** — the workflow fetches the *latest* release's `game-data.zip`.
3. Actions → **build-ios** → **Run workflow**.
4. Download the produced `.ipa` artifact and install it.

Local build (macOS with Xcode + XcodeGen): `bash scripts/build-ios.sh`.

## Upgrading to a newer game version

The author periodically releases new versions on itch.io:

1. Download the new APK, extract `assets/game.zip` → repackage as `game-data.zip`.
2. Replace the Release asset on GitHub.
3. Re-run the workflow. Done.

## Troubleshooting / FAQ

| Symptom | Cause & fix |
|---|---|
| TrollStore: `ldid: operator(): No such file or directory` | **Symbolic links** inside `node_modules/.bin` break ldid's recursive signing. Fixed in the shipped IPA (`find ... -type l -delete` before packaging). |
| Same ldid error even after symlink fix | Non-ASCII app name (`Pokémon`) → NFC/NFD mismatch between macOS zip and iOS APFS. Use a pure-ASCII `PRODUCT_NAME`. |
| "游戏引擎启动失败" appears instantly (0 s) | Health check hits `Connection refused` immediately and exhausts retries while Node is still initializing. Fixed: JIT entitlements + socket-probe long-wait loop (up to 10 min). |
| Node log: `Warning: disabling flag --expose_wasm ...` | Harmless V8 warning in jitless mode; doesn't affect the game. |
| Actions fails downloading "releases/latest" | Unauthenticated curl on shared runner IPs is rate-limited. All Release API calls must send `Authorization: token ${{ secrets.GITHUB_TOKEN }}`. |
| xcodegen: project format 77 unreadable | Old runners can't read Xcode 16 project files; use `runs-on: macos-15`. |

## Project structure

```
├─ ios/
│  ├─ EmpressApp/        # Swift shell: AppDelegate, GameViewController (Node boot + WKWebView), Info.plist
│  ├─ entitlements.plist # JIT entitlements (kept by TrollStore)
│  └─ project.yml        # XcodeGen config
├─ scripts/
│  ├─ build-ios.sh       # One-shot build: assets → xcodegen → xcodebuild → codesign → .ipa
│  ├─ bootstrap-ios.cjs  # iOS server entry (repo version, replaces the one inside game-data)
│  └─ ci-monitor.ps1     # Trigger + monitor GitHub Actions from Windows
├─ .github/workflows/build-ios.yml  # Cloud build (macos-15 runner)
├─ docs/INSTALL.md · docs/BUILD.md · docs/README.zh-CN.md
└─ 启动局域网版.bat      # Instant LAN play: PC serves, iPhone Safari plays
```

## License & disclaimer

- The **porting shell** (Swift sources, scripts, workflows, docs) is © 2026 lcheng871118-glitch. You may view, fork, build and use it on your own devices; **any modification or derivative release requires the author's prior consent** — see [LICENSE](LICENSE).
- The **game** (`game-data/`) is © its original author **Omniscye** ([Empress: Pokémon 2D Arena on itch.io](https://empress-pokemon-2d.itch.io)), bundled here solely for personal learning. Do not redistribute it commercially.
- All **Pokémon** IP belongs to Nintendo / Game Freak / The Pokémon Company.

## Credits

- **Omniscye** — original game
- [nodejs-mobile](https://github.com/nodejs-mobile/nodejs-mobile) — Node.js runtime for iOS
- [XcodeGen](https://github.com/yonaskolb/XcodeGen) — project generation
