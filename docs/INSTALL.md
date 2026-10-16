# 宝可梦竞技场2D · iOS 自签安装指南（Windows + AltStore）

本指南适用于：**没有 Mac，只有 Windows 电脑 + iPhone** 的用户。
构建在 GitHub Actions 云端 macOS 上完成，你只需要在 Windows 上签名安装。

---

## 一、总体流程

```
GitHub Actions 云构建 .ipa  →  下载 .ipa  →  AltServer(Windows) 签名  →  安装到 iPhone
```

---

## 二、一次性准备（约 30 分钟）

### 1. Windows 侧

1. 安装 **iCloud for Windows**（微软商店搜索 iCloud，AltServer 依赖它）
   - https://www.microsoft.com/store/productId/9P2SB0J4Q0J 或官网 https://www.icloud.com/
2. 安装 **AltServer**（AltStore 的电脑端）
   - 官网下载：https://altstore.io/ （Windows 版本）
   - 安装后运行，任务栏出现 AltServer 图标

### 2. iPhone 侧

1. iPhone 与 Windows 连接到**同一个 Wi-Fi**
2. 用数据线连接 iPhone 到 Windows（首次需在 iPhone 上点"信任此电脑"）
3. 在 Windows 任务栏 AltServer 图标 → Install AltStore → 选择你的 iPhone
4. iPhone 上会出现 **AltStore** App（首次打开需在 设置→通用→VPN与设备管理 中信任开发者证书）

### 3. 获取 .ipa

1. 在 GitHub 仓库 Actions 页点 **Run workflow**（或手动触发 build-ios）
2. 构建完成后（约 15–25 分钟）在 Actions 运行详情页下载 **Empress-Pokemon-2D-iOS-ipa** 构件
3. 解压得到 `Empress-Pokemon-2D-iOS-0.4.1.ipa`

---

## 三、安装游戏

1. Windows 打开 **AltServer**，iPhone 连接同一 Wi-Fi + 数据线
2. iPhone 打开 **AltStore** → 我的 App → 右上角 **+** → 选择下载的 `.ipa`
3. 输入你的 **Apple ID 和密码**（仅用于签名，AltStore 本地生成开发证书，不会上传）
4. 等待安装完成，桌面出现 **Empress Pokémon 2D**

---

## 四、7 天过期重签（免费账号须知）

免费 Apple ID 签名的 App **7 天后失效**，失效后打开会闪退，需要重签：

1. 保持 iPhone 连接同一 Wi-Fi（可不用数据线）
2. 打开 AltStore → 我的 App → 点击 Empress Pokémon 2D 的 **刷新** 按钮
3. 刷新成功即可继续玩

> 小技巧：AltStore 支持"自动刷新"（连接 Wi-Fi 且 AltServer 在运行时，AltStore 会自动在过期前刷新）。

---

## 五、常见问题

| 问题 | 解决办法 |
|---|---|
| AltStore 无法安装到 iPhone | 检查 iCloud for Windows 已安装；iPhone 信任此电脑；关闭 VPN/代理 |
| 安装报"无法验证开发者" | 设置 → 通用 → VPN与设备管理 → 信任该开发者证书 |
| 游戏打开黑屏/转圈 | 首次启动需等 3–10 秒（Node 引擎加载），耐心等待；若仍失败，重装一次 |
| 7 天后 App 打不开 | 按"四、7 天过期重签"刷新 |
| 想要一直不用重签 | 付费 Apple 开发者账号（$99/年）签名一次管一年 |

---

## 六、风险提示

- 本应用为**玩家自制同人游戏移植**，非官方发行，仅供个人游玩
- 免费签名 7 天重签是 Apple 机制限制，无法绕过（付费账号除外）
