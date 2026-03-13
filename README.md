# 📌 TopMost Tool

<div align="center">

**一个轻量的跨平台窗口置顶工具**

按一个快捷键，让任意窗口始终显示在最前面

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](https://github.com/iuliysii/TopMostTool)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Release](https://img.shields.io/github/v/release/iuliysii/TopMostTool?color=orange)](https://github.com/iuliysii/TopMostTool/releases)
[![PyPI](https://img.shields.io/pypi/v/topmost-tool?color=blue)](https://pypi.org/project/topmost-tool/)
[![Tests](https://img.shields.io/badge/Tests-53%20passed-brightgreen)](tests/)
[![Downloads](https://img.shields.io/github/downloads/iuliysii/TopMostTool/total?color=blue)](https://github.com/iuliysii/TopMostTool/releases)

[📥 下载](#-下载) · [🚀 快速上手](#-快速上手) · [⚙️ 配置](#️-配置) · [🌍 多语言](#-多语言)

</div>

---

## ✨ 功能

- **🔑 全局快捷键** — 按 `Ctrl+Space` 立即置顶 / 取消置顶当前焦点窗口
- **📋 托盘菜单** — 右键查看所有已置顶窗口，单独或批量取消
- **🔄 一键清除** — 菜单中一键取消全部置顶
- **🚀 开机自启** — 写入注册表，开机自动常驻后台
- **🌍 多语言支持** — 支持中文 / English，实时切换
- **💻 跨平台** — 支持 Windows、macOS、Linux
- **⚙️ 设置界面** — 图形化设置窗口，快捷键录制
- **🪶 轻量无感** — 常驻系统托盘，内存占用 < 30MB

---

## 📥 下载

### 方式一：直接下载可执行文件

前往 [Releases](https://github.com/iuliysii/TopMostTool/releases) 页面下载对应平台的版本：

| 平台 | 文件 | 说明 |
|------|------|------|
| Windows | `TopMostTool.exe` | 单文件，无需安装 |
| macOS | `TopMostTool` | 可执行文件 |
| Linux | `TopMostTool` | 可执行文件 |

### 方式二：通过 PyPI 安装

```bash
# 基础安装
pip install topmost-tool

# Windows 用户 (包含平台依赖)
pip install topmost-tool[windows]

# macOS 用户
pip install topmost-tool[macos]

# Linux 用户
pip install topmost-tool[linux]

# 运行
topmost-tool
```

> ⚠️ **Windows**: 需要以管理员身份运行（全局快捷键钩子需要管理员权限）
> 
> ⚠️ **macOS**: 需要在「系统偏好设置 → 安全性与隐私 → 辅助功能」中授权
> 
> ⚠️ **Linux**: 需要 X11 环境，不支持 Wayland

---

## 🚀 快速上手

### Windows

```bash
# 方式一：下载 exe（推荐）
# 下载 TopMostTool.exe，右键 → 以管理员身份运行

# 方式二：从源码运行
git clone https://github.com/iuliysii/TopMostTool.git
cd TopMostTool
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

### macOS

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py

# 打包为 .app（可选）
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

### Linux

```bash
# 安装系统依赖 (Ubuntu/Debian)
sudo apt install libx11-dev libxext-dev python3-gi libappindicator3-1

# 安装 Python 依赖
pip install -r requirements.txt

# 运行
python main.py

# 打包（可选）
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

---

## 🎮 使用方法

| 操作 | 效果 |
|------|------|
| 点击任意窗口（使其获得焦点） | 选中目标窗口 |
| 按 `Ctrl+Space` | 置顶 / 取消置顶该窗口 |
| 右键托盘图标 | 查看已置顶窗口列表 |
| 托盘菜单 → 取消全部置顶 | 一键清除所有置顶 |
| 托盘菜单 → 设置 | 打开设置窗口 |
| 托盘菜单 → 语言 | 切换中文 / English |
| 托盘菜单 → 开机自启 | 开启 / 关闭开机自启 (Windows) |
| 托盘菜单 → 退出 | 退出程序并清除所有置顶 |

---

## ⚙️ 配置

配置文件位于 `config/config.json`，可直接编辑：

```json
{
  "hotkey": "ctrl+space",
  "autostart": false,
  "notify_on_topmost": true,
  "show_title_prefix": false,
  "language": "zh_CN",
  "version": "1.1"
}
```

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `hotkey` | 快捷键，如 `ctrl+f9`、`alt+space` | `ctrl+space` |
| `autostart` | 开机自启 | `false` |
| `notify_on_topmost` | 置顶时显示气泡通知 | `true` |
| `show_title_prefix` | 窗口标题显示置顶标记 | `false` |
| `language` | 界面语言 (`zh_CN` / `en`) | `zh_CN` |

修改后重启程序生效。

---

## 🌍 多语言

支持以下语言：

| 语言代码 | 显示名称 |
|----------|----------|
| `zh_CN` | 简体中文 |
| `en` | English |

切换方式：右键托盘图标 → 语言 → 选择语言

---

## 📁 项目结构

```
TopMostTool/
├── core/                      # 核心模块
│   ├── app_state.py           # 全局状态管理
│   ├── i18n.py                # 国际化模块
│   └── logger.py              # 日志配置
├── platforms/                 # 跨平台支持
│   ├── base.py                # 抽象基类
│   ├── windows/               # Windows 实现
│   ├── macos/                 # macOS 实现
│   └── linux/                 # Linux 实现
├── config/                    # 配置管理
│   ├── config_manager.py
│   └── config.json
├── ui/                        # 用户界面
│   ├── tray_app.py            # 系统托盘
│   ├── settings_window.py     # 设置窗口
│   └── hotkey_dialog.py       # 快捷键设置
├── locales/                   # 语言资源
│   ├── zh_CN.json
│   └── en.json
├── assets/                    # 资源文件
├── tests/                     # 单元测试 (53 个用例)
├── scripts/                   # 打包脚本
├── main.py                    # 程序入口
└── pyproject.toml             # PyPI 配置
```

---

## 🔧 技术栈

| 功能 | Windows | macOS | Linux |
|------|---------|-------|-------|
| 窗口管理 | pywin32 | pyobjc | python-xlib + ewmh |
| 快捷键监听 | keyboard | pynput | pynput |
| 系统托盘 | pystray (Win32) | pystray (Darwin) | pystray (GTK) |
| 开机自启 | 注册表 | LaunchAgent | .desktop |

---

## 🔒 权限与安全说明

### Windows
- `keyboard` 库注册全局快捷键钩子需要管理员权限
- `pywin32` 操作部分系统进程窗口需要管理员权限

### macOS
- 需要在「系统偏好设置 → 安全性与隐私 → 辅助功能」中授权

### Linux
- 需要 X11 显示服务器
- 支持 EWMH 规范的窗口管理器 (GNOME, KDE, Xfce, i3wm 等)

### 隐私说明
- 托盘菜单会显示已置顶窗口的标题
- Windows 开机自启通过写入注册表实现
- 本工具不联网，不收集任何数据

---

## 🧪 开发

```bash
# 克隆仓库
git clone https://github.com/iuliysii/TopMostTool.git
cd TopMostTool

# 创建虚拟环境
python -m venv .venv

# 安装依赖
.venv/Scripts/pip install -r requirements.txt  # Windows
.venv/bin/pip install -r requirements.txt      # macOS/Linux

# 运行测试
python -m pytest tests/ -v

# 运行程序
python main.py
```

---

## 📄 License

[MIT](LICENSE) © 2026 iuliysii

---

## 🙏 致谢

- [pystray](https://github.com/moses-palmer/pystray) - 跨平台系统托盘库
- [pynput](https://github.com/moses-palmer/pynput) - 跨平台输入设备控制
- [python-xlib](https://github.com/python-xlib/python-xlib) - X11 Python 绑定
- [ewmh](https://github.com/parkouss/pyewmh) - EWMH 实现
