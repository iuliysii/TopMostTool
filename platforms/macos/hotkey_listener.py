"""
macOS 快捷键监听器
基于 pynput 实现
"""

import logging
import threading
from typing import Callable, Optional, Set

from platforms.base import HotkeyListener

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
except ImportError as e:
    raise ImportError(
        "无法导入 pynput 库\n"
        "请运行：pip install pynput>=1.7.0\n"
        f"原始错误：{e}"
    ) from e

log = logging.getLogger(__name__)


class MacOSHotkeyListener(HotkeyListener):
    """macOS 快捷键监听器实现"""
    
    def __init__(self):
        self._hotkey: Optional[str] = None
        self._callback: Optional[Callable] = None
        self._listener: Optional[keyboard.Listener] = None
        self._pressed_keys: Set = set()
        self._lock = threading.Lock()
    
    @property
    def hotkey(self) -> Optional[str]:
        return self._hotkey
    
    def start(self, hotkey: str, callback: Callable) -> None:
        """启动监听"""
        with self._lock:
            if self._listener is not None:
                log.warning("HotkeyListener 已在运行，请先调用 stop()")
                return
            
            self._hotkey = hotkey.lower().strip()
            self._callback = callback
            self._pressed_keys.clear()
            
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self._listener.start()
            log.info(f"快捷键监听已启动: {self._hotkey!r}")
    
    def stop(self) -> None:
        """停止监听"""
        with self._lock:
            if self._listener is None:
                log.debug("HotkeyListener 未在运行，无需 stop")
                return
            
            self._listener.stop()
            self._listener = None
            self._pressed_keys.clear()
        
        log.info("快捷键监听已停止")
    
    def update_hotkey(self, new_hotkey: str) -> None:
        """热更新快捷键"""
        new_hotkey = new_hotkey.lower().strip()
        with self._lock:
            old = self._hotkey
            self._hotkey = new_hotkey
            self._pressed_keys.clear()
        log.info(f"快捷键已更新: {old!r} → {new_hotkey!r}")
    
    def _parse_hotkey(self) -> Set[str]:
        """解析快捷键字符串为按键集合"""
        if not self._hotkey:
            return set()
        return set(self._hotkey.split('+'))
    
    def _key_to_name(self, key) -> str:
        """将按键转换为名称"""
        if isinstance(key, KeyCode):
            char = key.char
            if char:
                return char.lower()
            vk = key.vk
            if vk:
                if 96 <= vk <= 105:
                    return f"f{vk - 95}"
                if vk == 32:
                    return 'space'
            return str(vk)
        
        if isinstance(key, Key):
            key_name = key.name.lower()
            if key_name.startswith('ctrl'):
                return 'ctrl'
            if key_name.startswith('alt') or key_name.startswith('option'):
                return 'alt'
            if key_name.startswith('shift'):
                return 'shift'
            if key_name.startswith('cmd'):
                return 'cmd'
            return key_name
        
        return str(key).lower()
    
    def _on_press(self, key) -> None:
        """按键按下事件"""
        key_name = self._key_to_name(key)
        self._pressed_keys.add(key_name)
        
        required = self._parse_hotkey()
        if required and required.issubset(self._pressed_keys):
            log.info(f"快捷键触发: {self._hotkey!r}")
            threading.Thread(
                target=self._safe_callback,
                name="HotkeyCallbackThread",
                daemon=True,
            ).start()
            self._pressed_keys.clear()
    
    def _on_release(self, key) -> None:
        """按键释放事件"""
        key_name = self._key_to_name(key)
        self._pressed_keys.discard(key_name)
    
    def _safe_callback(self) -> None:
        """安全执行回调"""
        try:
            if self._callback:
                self._callback()
        except Exception as e:
            log.error(f"快捷键回调执行异常: {e}")
