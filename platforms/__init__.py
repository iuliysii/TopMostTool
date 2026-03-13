"""
platforms/__init__.py  —  跨平台支持模块
自动检测操作系统并加载对应实现
支持 Windows、macOS、Linux
"""

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platforms.base import WindowManager, HotkeyListener

_current_platform = None


def get_platform() -> str:
    """获取当前平台名称"""
    global _current_platform
    if _current_platform is None:
        if sys.platform == 'win32':
            _current_platform = 'windows'
        elif sys.platform == 'darwin':
            _current_platform = 'macos'
        elif sys.platform.startswith('linux'):
            _current_platform = 'linux'
        else:
            _current_platform = 'unknown'
    return _current_platform


def get_window_manager() -> 'WindowManager':
    """获取当前平台的窗口管理器"""
    platform = get_platform()
    
    if platform == 'windows':
        from platforms.windows.window_manager import WindowsWindowManager
        return WindowsWindowManager()
    elif platform == 'macos':
        from platforms.macos.window_manager import MacOSWindowManager
        return MacOSWindowManager()
    elif platform == 'linux':
        from platforms.linux.window_manager import LinuxWindowManager
        return LinuxWindowManager()
    else:
        raise RuntimeError(f"Unsupported platform: {platform}")


def get_hotkey_listener() -> 'HotkeyListener':
    """获取当前平台的快捷键监听器"""
    platform = get_platform()
    
    if platform == 'windows':
        from platforms.windows.hotkey_listener import WindowsHotkeyListener
        return WindowsHotkeyListener()
    elif platform == 'macos':
        from platforms.macos.hotkey_listener import MacOSHotkeyListener
        return MacOSHotkeyListener()
    elif platform == 'linux':
        from platforms.linux.hotkey_listener import LinuxHotkeyListener
        return LinuxHotkeyListener()
    else:
        raise RuntimeError(f"Unsupported platform: {platform}")


__all__ = [
    'get_platform',
    'get_window_manager',
    'get_hotkey_listener',
]
