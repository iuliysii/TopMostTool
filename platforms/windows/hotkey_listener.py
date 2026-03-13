"""
Windows 快捷键监听器
基于 keyboard 库实现
"""

import logging
import threading
from typing import Callable, Optional

from platforms.base import HotkeyListener

try:
    import keyboard
except ImportError as e:
    raise ImportError(
        "无法导入 keyboard 库\n"
        "请运行：pip install keyboard>=0.13.5\n"
        f"原始错误：{e}"
    ) from e

log = logging.getLogger(__name__)


class WindowsHotkeyListener(HotkeyListener):
    """Windows 快捷键监听器实现"""
    
    def __init__(self):
        self._hotkey: Optional[str] = None
        self._callback: Optional[Callable] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
    
    @property
    def hotkey(self) -> Optional[str]:
        return self._hotkey
    
    def start(self, hotkey: str, callback: Callable) -> None:
        """启动监听"""
        with self._lock:
            if self._thread and self._thread.is_alive():
                log.warning("HotkeyListener 已在运行，请先调用 stop()")
                return
            
            self._hotkey = hotkey.lower().strip()
            self._callback = callback
            self._stop_event.clear()
            
            self._thread = threading.Thread(
                target=self._listen_loop,
                name="HotkeyListenerThread",
                daemon=True,
            )
            self._thread.start()
            log.info(f"快捷键监听已启动: {self._hotkey!r}")
    
    def stop(self) -> None:
        """停止监听"""
        with self._lock:
            if not self._thread or not self._thread.is_alive():
                log.debug("HotkeyListener 未在运行，无需 stop")
                return
            self._stop_event.set()
            self._unregister()
        if self._thread:
            self._thread.join(timeout=2.0)
        log.info("快捷键监听已停止")
    
    def update_hotkey(self, new_hotkey: str) -> None:
        """热更新快捷键"""
        new_hotkey = new_hotkey.lower().strip()
        with self._lock:
            old = self._hotkey
            self._unregister()
            self._hotkey = new_hotkey
            self._register()
        log.info(f"快捷键已更新: {old!r} → {new_hotkey!r}")
    
    def _register(self) -> None:
        """注册快捷键钩子"""
        if not self._hotkey or not self._callback:
            return
        try:
            keyboard.add_hotkey(
                self._hotkey,
                self._on_triggered,
                suppress=False,
            )
            log.debug(f"已注册快捷键: {self._hotkey!r}")
        except Exception as e:
            log.error(f"注册快捷键失败 {self._hotkey!r}: {e}")
    
    def _unregister(self) -> None:
        """注销快捷键钩子"""
        if not self._hotkey:
            return
        try:
            keyboard.remove_hotkey(self._hotkey)
            log.debug(f"已注销快捷键: {self._hotkey!r}")
        except Exception as e:
            log.debug(f"注销快捷键时忽略异常 {self._hotkey!r}: {e}")
    
    def _on_triggered(self) -> None:
        """快捷键触发回调"""
        log.info(f"快捷键触发: {self._hotkey!r}")
        threading.Thread(
            target=self._safe_callback,
            name="HotkeyCallbackThread",
            daemon=True,
        ).start()
    
    def _safe_callback(self) -> None:
        """安全执行回调"""
        try:
            if self._callback:
                self._callback()
        except Exception as e:
            log.error(f"快捷键回调执行异常: {e}")
    
    def _listen_loop(self) -> None:
        """监听线程主循环"""
        with self._lock:
            self._register()
        self._stop_event.wait()
        log.debug("listen_loop 退出")
