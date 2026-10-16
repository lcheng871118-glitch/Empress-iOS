# Installation Guide

How to install `Empress-Pokemon-2D-iOS-0.4.1.ipa` on your iPhone.

## Prerequisites

- iPhone with **iOS 14 or later** (landscape game)
- One `.ipa` file (download from [Releases](https://github.com/lcheng871118-glitch/Empress-iOS/releases) or build yourself — see [BUILD.md](BUILD.md))
- A way to transfer the file to the phone: AirDrop, USB, cloud drive, ...

---

## Option 1 — TrollStore (recommended)

No re-signing, installs permanently. Requires a TrollStore-supported iOS version (see [trollstore.app](https://trollstore.app)).

1. Install [TrollStore](https://trollstore.app) on your device.
2. Get the `.ipa` onto your iPhone (AirDrop, Files app, cloud drive...).
3. Open the `.ipa` — the system asks which app should handle it → choose **TrollStore**.
4. Tap **Install** in TrollStore.
5. Wait for the install to finish. The app appears on the home screen.

> The IPA includes JIT entitlements (`com.apple.security.cs.allow-jit`). TrollStore preserves them during re-signing, which lets the embedded Node.js engine start at full speed. If you ever rebuild from source, keep `ios/entitlements.plist` in the signing step.

### Troubleshooting TrollStore

| Error | Fix |
|---|---|
| `ldid: operator(): No such file or directory` | The IPA contains dangling symlinks, or a non-ASCII app name. Use the latest Release IPA — both issues are fixed there. |
| Install hangs or fails after an update | Fully uninstall the old version first, then install the new IPA. |

---

## Option 2 — AltStore (free Apple ID, re-sign every 7 days)

No TrollStore needed, but the app expires after 7 days. Re-signing is one tap.

### Windows

1. Install **iTunes** and **iCloud** from the Microsoft Store (AltServer depends on them).
2. Download **AltServer** from [altstore.io](https://altstore.io) and run it (system tray icon).
3. Connect your iPhone via USB, tap **Trust this computer** on the phone.
4. Tray icon → **Install AltStore** → select your iPhone → enter an **Apple ID** (a throwaway one is safer).
5. On the phone, open **AltStore** → *My Apps* → tap **+** → pick the `.ipa`.
6. First launch: Settings → General → VPN & Device Management → **Trust** your Apple ID.

### macOS

Same flow; AltServer runs natively (no iTunes needed).

### Re-signing before expiry

- iPhone and PC on the same Wi-Fi (or iPhone USB-connected).
- AltStore → *My Apps* → **Refresh All**.
- Refresh before the 7-day deadline, or the app won't open.

---

## After installation

1. Launch **Empress Pokémon 2D**.
2. The app starts its embedded Node engine (usually a few seconds; the very first launch can take longer).
3. The main menu appears — campaign, team builder, real-time battles all work.
4. Saves live in the app's Documents folder (`empress-profile`).

If "游戏引擎启动失败" persists for more than 2 minutes, open the app's Documents folder (e.g. with Filza) and share `empress-node.log` — it contains the Node engine diagnostics.
