# 📌 TopMost Tool

<div align="center">

**一个轻量的 Windows 窗口置顶工具**

按一个快捷键，让任意窗口始终显示在最前面

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?logo=windows)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Release](https://img.shields.io/github/v/release/iuliysii/TopMostTool?color=orange)](https://github.com/iuliysii/TopMostTool/releases)

[📥 下载 .exe](#下载) · [🚀 快速上手](#快速上手) · [⚙️ 配置](#配置)

</div>

---

## ✨ 功能

- **🔑 全局快捷键** — 按 `Ctrl+Space` 立即置顶 / 取消置顶当前焦点窗口
- **📋 托盘菜单** — 右键查看所有已置顶窗口，单独或批量取消
- **🔄 一键清除** — 菜单中一键取消全部置顶
- **🚀 开机自启** — 写入注册表，开机自动常驻后台
- **🪶 轻量无感** — 常驻系统托盘，内存占用 < 20MB

---

## 📥 下载

前往 [Releases](https://github.com/iuliysii/TopMostTool/releases) 页面下载最新版 `TopMostTool.exe`，双击运行即可，无需安装 Python。

> ⚠️ 需要**以管理员身份运行**（全局快捷键钩子 + Win32 置顶操作需要管理员权限）

---

## 🚀 快速上手

### 方式一：下载 .exe（推荐）

1. 下载 [TopMostTool.exe](https://github.com/iuliysii/TopMostTool/releases)
2. 右键 → **以管理员身份运行**
3. 系统托盘出现图标，即可使用

### 方式二：从源码运行

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 安装依赖
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. 以管理员身份运行
.venv\Scripts\python.exe main.py
```

---

## 🎮 使用方法

| 操作 | 效果 |
|---|---|
| 点击任意窗口（使其获得焦点） | 选中目标窗口 |
| 按 `Ctrl+Space` | 置顶 / 取消置顶该窗口 |
| 右键托盘图标 | 查看已置顶窗口列表 |
| 托盘菜单 → 取消全部置顶 | 一键清除所有置顶 |
| 托盘菜单 → 开机自启 | 开启 / 关闭开机自启 |
| 托盘菜单 → 退出 | 退出程序并清除所有置顶 |

---

## ⚙️ 配置

配置文件位于 `config\config.json`，可直接编辑：

```json
{
  "hotkey": "ctrl+space",
  "autostart": false,
  "notify_on_topmost": true,
  "show_title_prefix": false,
  "version": "1.0"
}
```

| 字段 | 说明 | 默认值 |
|---|---|---|
| `hotkey` | 快捷键，如 `ctrl+f9` | `ctrl+space` |
| `autostart` | 开机自启 | `false` |
| `notify_on_topmost` | 置顶时显示气泡通知 | `true` |

修改后重启程序生效。

---

## 📦 自行打包

```bash
# 安装 PyInstaller
.venv\Scripts\python.exe -m pip install pyinstaller

# 打包（带图标和版本信息）
.venv\Scripts\pyinstaller.exe ^
  --noconsole --onefile ^
  --name TopMostTool ^
  --hidden-import pystray._win32 ^
  --icon "assets\icon.ico" ^
  --version-file "version_info.txt" ^
  main.py
```

输出文件：`dist\TopMostTool.exe`

---

## 📁 项目结构

```
TopMostTool/
├── core/
│   ├── window_manager.py     # Win32 窗口枚举与置顶操作
│   └── hotkey_listener.py    # 全局快捷键监听
├── config/
│   ├── config_manager.py     # 配置读写与开机自启
│   └── config.json           # 用户配置文件
├── ui/
│   └── tray_app.py           # 系统托盘与菜单
├── assets/
│   ├── icon.png
│   └── icon.ico
├── main.py                   # 程序入口
├── requirements.txt
└── README.md
```

---

## 🔒 权限与安全说明

**为什么需要管理员权限？**
- `keyboard` 库注册全局快捷键钩子需要管理员权限
- `pywin32` 操作部分系统进程窗口需要管理员权限

**隐私说明**
- 托盘菜单会显示已置顶窗口的标题
- 开机自启通过写入注册表实现：`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- 本工具不联网，不收集任何数据

---

## 📄 License

[MIT](LICENSE) © 2026 iuliysii
