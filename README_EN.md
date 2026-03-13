# 📌 TopMost Tool

English | [简体中文](README.md)

<div align="center">

**A lightweight cross-platform window pinning tool**

Pin any window to stay on top with a single hotkey

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](https://github.com/iuliysii/TopMostTool)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Release](https://img.shields.io/github/v/release/iuliysii/TopMostTool?color=orange)](https://github.com/iuliysii/TopMostTool/releases)
[![Tests](https://img.shields.io/badge/Tests-53%20passed-brightgreen)](tests/)
[![Downloads](https://img.shields.io/github/downloads/iuliysii/TopMostTool/total?color=blue)](https://github.com/iuliysii/TopMostTool/releases)

[📥 Download](#-download) · [🚀 Quick Start](#-quick-start) · [⚙️ Configuration](#️-configuration) · [🌍 Multilingual](#-multilingual)

</div>

---

## ✨ Features

- **🔑 Global Hotkey** — Press `Ctrl+Space` to pin/unpin the focused window instantly
- **📋 System Tray Menu** — Right-click to view all pinned windows, unpin individually or in batch
- **🔄 One-Click Clear** — Unpin all windows from the menu
- **🚀 Auto-start** — Automatically start on boot (Windows)
- **🌍 Multilingual Support** — Supports Chinese / English, switch in real-time
- **💻 Cross-Platform** — Supports Windows, macOS, Linux
- **⚙️ Settings GUI** — Graphical settings window with hotkey recording
- **🪶 Lightweight** — Stays in system tray, uses < 30MB memory

---

## 📥 Download

### Option 1: Download Executable

Visit the [Releases](https://github.com/iuliysii/TopMostTool/releases) page to download for your platform:

| Platform | File | Description |
|----------|------|-------------|
| Windows | `TopMostTool-Windows.exe` | Single file, no installation |
| macOS | `TopMostTool-macOS` | Executable |
| Linux | `TopMostTool-Linux` | Executable |

### Option 2: Run from Source

```bash
# Clone repository
git clone https://github.com/iuliysii/TopMostTool.git
cd TopMostTool

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

> ⚠️ **Windows**: Run as Administrator (global hotkey hook requires admin rights)
> 
> ⚠️ **macOS**: Grant accessibility permission in System Preferences → Security & Privacy → Accessibility
> 
> ⚠️ **Linux**: Requires X11, Wayland not supported

---

## 🚀 Quick Start

### Windows

```bash
# Download TopMostTool-Windows.exe, right-click → Run as Administrator
```

### macOS

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Linux

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt install libx11-dev libxext-dev python3-gi libappindicator3-1

# Install Python dependencies
pip install -r requirements.txt

# Run
python main.py
```

---

## 🎮 Usage

| Action | Effect |
|--------|--------|
| Click any window (to focus it) | Select target window |
| Press `Ctrl+Space` | Pin/unpin the window |
| Right-click tray icon | View pinned windows list |
| Tray menu → Unpin All | Clear all pinned windows |
| Tray menu → Settings | Open settings window |
| Tray menu → Language | Switch Chinese / English |
| Tray menu → Auto-start | Enable/disable auto-start (Windows) |
| Tray menu → Exit | Exit and unpin all windows |

---

## ⚙️ Configuration

Configuration file located at `config/config.json`:

```json
{
  "hotkey": "ctrl+space",
  "autostart": false,
  "notify_on_topmost": true,
  "show_title_prefix": false,
  "language": "en",
  "version": "1.1"
}
```

| Field | Description | Default |
|-------|-------------|---------|
| `hotkey` | Hotkey, e.g., `ctrl+f9`, `alt+space` | `ctrl+space` |
| `autostart` | Auto-start on boot | `false` |
| `notify_on_topmost` | Show notification when pinning | `true` |
| `show_title_prefix` | Show pin marker in window title | `false` |
| `language` | UI language (`zh_CN` / `en`) | `en` |

Changes take effect after restart.

---

## 🌍 Multilingual

Supported languages:

| Code | Language |
|------|----------|
| `zh_CN` | Simplified Chinese |
| `en` | English |

Switch: Right-click tray icon → Language → Select language

---

## 📁 Project Structure

```
TopMostTool/
├── core/                      # Core modules
│   ├── app_state.py           # Global state management
│   ├── i18n.py                # Internationalization
│   └── logger.py              # Logging configuration
├── platforms/                 # Cross-platform support
│   ├── base.py                # Abstract base class
│   ├── windows/               # Windows implementation
│   ├── macos/                 # macOS implementation
│   └── linux/                 # Linux implementation
├── config/                    # Configuration management
├── ui/                        # User interface
├── locales/                   # Language resources
├── tests/                     # Unit tests (53 cases)
├── scripts/                   # Build scripts
└── main.py                    # Entry point
```

---

## 🔧 Tech Stack

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Window Management | pywin32 | pyobjc | python-xlib + ewmh |
| Hotkey Listener | keyboard | pynput | pynput |
| System Tray | pystray (Win32) | pystray (Darwin) | pystray (GTK) |
| Auto-start | Registry | LaunchAgent | .desktop |

---

## 🔒 Permissions & Security

### Windows
- `keyboard` library requires admin rights for global hotkey hook
- `pywin32` requires admin rights to manipulate some system process windows

### macOS
- Grant accessibility permission in System Preferences → Security & Privacy → Accessibility

### Linux
- Requires X11 display server
- Supports EWMH-compliant window managers (GNOME, KDE, Xfce, i3wm, etc.)

### Privacy
- Tray menu displays titles of pinned windows
- Windows auto-start implemented via registry
- This tool does not connect to the internet or collect any data

---

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/iuliysii/TopMostTool.git
cd TopMostTool

# Create virtual environment
python -m venv .venv

# Install dependencies
.venv/Scripts/pip install -r requirements.txt  # Windows
.venv/bin/pip install -r requirements.txt      # macOS/Linux

# Run tests
python -m pytest tests/ -v

# Run application
python main.py
```

---

## 🤝 Contributing

Contributions are welcome! Please see [Contributing Guide](CONTRIBUTING.md) for details.

---

## 📄 License

[MIT](LICENSE) © 2026 iuliysii

---

## 🙏 Acknowledgments

- [pystray](https://github.com/moses-palmer/pystray) - Cross-platform system tray library
- [pynput](https://github.com/moses-palmer/pynput) - Cross-platform input device control
- [python-xlib](https://github.com/python-xlib/python-xlib) - X11 Python bindings
- [ewmh](https://github.com/parkouss/pyewmh) - EWMH implementation
