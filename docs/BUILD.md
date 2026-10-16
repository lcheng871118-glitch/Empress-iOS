# Building the .ipa yourself

Two ways to build: **GitHub Actions (cloud, no Mac needed)** or **locally on macOS**.

The result is an unsigned/ad-hoc-signed `.ipa` — install it with **TrollStore** (recommended) or sign it with **AltStore** (see [INSTALL.md](INSTALL.md)).

---

## Option 1 — GitHub Actions (recommended, no Mac)

### 1. Get the repo

```bash
git clone https://github.com/lcheng871118-glitch/Empress-iOS.git
cd Empress-iOS
```

(or fork it to your own account and clone your fork.)

### 2. Publish the game asset bundle

The workflow downloads `game-data.zip` from the **latest Release** of the repo.

1. Create a `game-data.zip` (game asset bundle, ~185 MB — see "Where does game-data come from?" below).
2. GitHub → **Releases** → **Create a new release** → choose a tag (e.g. `game-data-v0.4.1`).
3. Attach `game-data.zip` as a release asset.
4. Publish.

### 3. Run the workflow

1. **Actions** tab → **build-ios** workflow → **Run workflow** (button on the right).
2. Wait ~15–25 minutes (macOS runners sometimes queue).
3. Open the run → **Artifacts** → download **Empress-Pokemon-2D-iOS-ipa** (a zip).
4. Unzip → you get `Empress-Pokemon-2D-iOS-0.4.1.ipa`.

### 4. Install

See [INSTALL.md](INSTALL.md) — TrollStore for no-re-sign installs.

> If you fork the repo, the Actions runner is free for public repos. For private repos you need to buy GitHub Actions minutes.

---

## Option 2 — Local macOS build

Requirements: macOS with **Xcode** (16.x) and **XcodeGen** (`brew install xcodegen`).

```bash
bash scripts/build-ios.sh
```

The script: downloads nodejs-mobile v18.20.4 → assembles `ios/game-data` from `game/` → generates the Xcode project → builds Release → ad-hoc signs with JIT entitlements → zips `Empress-Pokemon-2D-iOS-0.4.1.ipa` into `ios/`.

---

## Where does `game-data` come from?

The game (Empress: Pokémon 2D Arena) is a fan game published by **Omniscye** on itch.io.

- Get the latest APK from the [official itch.io page](https://empress-pokemon-2d.itch.io).
- Rename it to `.zip`, open it, extract **`assets/game.zip`**.
- That `game.zip` *is* the game-data bundle — rename it to `game-data.zip` and upload it to Releases.

Example with PowerShell:

```powershell
# rename APK -> zip, expand, grab assets/game.zip
Rename-Item Empress-Pokemon-2D.apk Empress-Pokemon-2D.zip
Expand-Archive Empress-Pokemon-2D.zip -DestinationPath apk-extract
Copy-Item apk-extract\assets\game.zip .\game-data.zip
```

## Upgrading to a newer game version

1. Download the new APK → extract its `assets/game.zip` → `game-data.zip`.
2. Replace the asset in the latest Release (or create a new Release).
3. Re-run the workflow. The game version in the IPA filename comes from the `GAME_VERSION` workflow input (default `0.4.1`); pass the new version there if you like.

---

## Build pipeline internals (what CI does)

1. Checkout repo.
2. Download `game-data.zip` from latest Release (authenticated API call).
3. Replace `android-bootstrap.cjs` with the repo version (`scripts/bootstrap-ios.cjs`).
4. `scripts/build-ios.sh`:
   - download nodejs-mobile v18.20.4 iOS xcframework
   - copy `game/{client,server,node_modules,...}` into `ios/game-data`
   - strip symlinks (fixes TrollStore ldid signing)
   - `xcodegen generate` → `xcodebuild -configuration Release -sdk iphoneos`
   - ad-hoc codesign with `ios/entitlements.plist` (JIT entitlements)
   - zip `Payload/` → `.ipa`
5. Upload artifact.

### Known pitfalls (already fixed in this repo)

| Pitfall | Fix |
|---|---|
| Symlinks in `node_modules/.bin` break ldid signing | `find game-data -type l -delete` before zipping |
| Non-ASCII `PRODUCT_NAME` breaks ldid (NFC/NFD mismatch) | `PRODUCT_NAME: EmpressPokemon2D` (pure ASCII); display name stays "Empress Pokémon 2D" |
| Unauthenticated GitHub API on runners gets rate-limited | All Release API calls send `Authorization: token GITHUB_TOKEN` |
| Xcode 16 project format unreadable on old runners | `runs-on: macos-15` |
| Engine "stuck initializing" without JIT | Ship `com.apple.security.cs.allow-jit` entitlement (kept by TrollStore) + long socket-probe wait loop |
