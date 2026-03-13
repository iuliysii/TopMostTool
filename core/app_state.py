"""
app_state.py  —  应用状态管理模块
使用单例模式管理全局状态，替代分散的全局变量
"""

import threading
from typing import Callable, Optional


class AppState:
    """
    应用全局状态容器
    
    使用单例模式确保状态一致性，支持线程安全操作
    """
    _instance: Optional['AppState'] = None
    _class_lock = threading.Lock()
    
    def __new__(cls) -> 'AppState':
        if cls._instance is None:
            with cls._class_lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._lock = threading.Lock()
                    instance._managed_hwnds: set[int] = set()
                    instance._tray_ref = None
                    instance._on_state_changed: Optional[Callable[[bool], None]] = None
                    cls._instance = instance
        return cls._instance
    
    @property
    def managed_hwnds(self) -> set[int]:
        """获取已置顶窗口句柄集合的只读视图"""
        with self._lock:
            return self._managed_hwnds.copy()
    
    @property
    def tray_ref(self):
        """获取托盘实例引用"""
        with self._lock:
            return self._tray_ref
    
    @property
    def on_state_changed(self):
        """获取状态变化回调"""
        return self._on_state_changed
    
    @on_state_changed.setter
    def on_state_changed(self, callback: Optional[Callable[[bool], None]]):
        self._on_state_changed = callback
    
    def add_hwnd(self, hwnd: int) -> None:
        """添加已置顶窗口句柄"""
        with self._lock:
            self._managed_hwnds.add(hwnd)
        self._notify_state_changed()
    
    def remove_hwnd(self, hwnd: int) -> None:
        """移除窗口句柄"""
        with self._lock:
            self._managed_hwnds.discard(hwnd)
        self._notify_state_changed()
    
    def clear_hwnds(self) -> int:
        """清空所有句柄，返回清除数量"""
        with self._lock:
            count = len(self._managed_hwnds)
            self._managed_hwnds.clear()
        self._notify_state_changed()
        return count
    
    def has_topmost(self) -> bool:
        """是否有置顶窗口"""
        with self._lock:
            return bool(self._managed_hwnds)
    
    def get_hwnds(self) -> list[int]:
        """获取所有句柄的副本"""
        with self._lock:
            return list(self._managed_hwnds)
    
    def set_tray(self, tray: object) -> None:
        """设置托盘实例引用"""
        with self._lock:
            self._tray_ref = tray
    
    def _notify_state_changed(self) -> None:
        """通知状态变化"""
        if self._on_state_changed:
            try:
                has_topmost = self.has_topmost()
                self._on_state_changed(has_topmost)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"State change callback error: {e}")


def get_state() -> AppState:
    """获取全局状态实例"""
    return AppState()


def reset_state() -> None:
    """重置状态（仅用于测试）"""
    AppState._instance = None
