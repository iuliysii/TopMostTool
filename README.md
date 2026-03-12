# TopMost Tool

一个轻量的 Windows 窗口置顶工具，支持全局快捷键切换置顶、托盘菜单管理置顶窗口、开机自启。

**功能**
- 全局快捷键切换当前窗口置顶状态
- 托盘菜单查看/取消已置顶窗口
- 一键取消全部置顶
- 开机自启（写入注册表）

**环境要求**
- Windows 10/11
- Python 3.10+
- 需要管理员权限运行（全局钩子 + Win32 置顶）

## 安装

建议使用虚拟环境：

```powershell
python -m venv .venv
& .venv\Scripts\python.exe -m pip install --upgrade pip
& .venv\Scripts\python.exe -m pip install -r requirements.txt
```

如果你要打包成 exe：

```powershell
& .venv\Scripts\python.exe -m pip install pyinstaller
```

## 使用

从源码运行（推荐入口）：

```powershell
& .venv\Scripts\python.exe .\main.py
```

默认快捷键：`Ctrl+Space`  
托盘菜单支持查看置顶窗口、取消置顶、开机自启与退出。

## 配置

配置文件：`config\config.json`  
常用字段示例：
- `hotkey`: 快捷键字符串，例如 `ctrl+space`
- `autostart`: 是否开机自启

## 打包（exe）

最小命令：

```powershell
& .venv\Scripts\pyinstaller.exe --noconsole --onefile --name TopMostTool --hidden-import pystray._win32 main.py
```

带图标与版本信息（需要 `assets\icon.ico` 与 `version_info.txt`）：

```powershell
& .venv\Scripts\pyinstaller.exe --noconsole --onefile --name TopMostTool --hidden-import pystray._win32 --icon "assets\icon.ico" --version-file "version_info.txt" main.py
```

输出目录：`dist\TopMostTool.exe`

## 权限说明

本工具需要管理员权限运行，原因如下：
- `keyboard` 全局快捷键钩子在 Windows 下需要管理员权限
- `pywin32` 操作置顶窗口在部分场景会被系统权限限制

请确保以管理员身份启动程序或打包后的 exe。

## 安全与隐私说明

- 托盘菜单会显示窗口标题，可能包含敏感信息。  
  如有需要可自行修改代码隐藏标题或仅显示数量。
- 开机自启通过写入注册表：  
  `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`

## 目录结构

```
.
├─ core
│  ├─ hotkey_listener.py
│  └─ window_manager.py
├─ config
│  ├─ config_manager.py
│  └─ config.json
├─ ui
│  └─ tray_app.py
├─ assets
│  ├─ icon.png
│  └─ icon.ico
├─ main.py
├─ version_info.txt
└─ README.md
```
