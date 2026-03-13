"""
base.py  —  平台抽象基类
定义窗口管理器和快捷键监听器的接口
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional, List


class WindowManager(ABC):
    """窗口管理器抽象基类"""
    
    @abstractmethod
    def get_foreground_window(self) -> tuple[int, str]:
        """
        获取当前焦点窗口
        
        Returns:
            (hwnd, title) — hwnd=0 表示获取失败
        """
        pass
    
    @abstractmethod
    def is_topmost(self, hwnd: int) -> bool:
        """
        判断窗口是否处于置顶状态
        
        Args:
            hwnd: 窗口句柄/ID
            
        Returns:
            True=置顶，False=非置顶
        """
        pass
    
    @abstractmethod
    def set_topmost(self, hwnd: int, on: bool) -> bool:
        """
        设置或取消窗口置顶
        
        Args:
            hwnd: 窗口句柄/ID
            on: True=置顶，False=取消置顶
            
        Returns:
            True=操作成功，False=操作失败
            
        Raises:
            PermissionError: 权限不足
        """
        pass
    
    def toggle_topmost(self, hwnd: int) -> bool:
        """
        切换窗口置顶状态
        
        Returns:
            切换后的置顶状态
        """
        current = self.is_topmost(hwnd)
        target = not current
        self.set_topmost(hwnd, target)
        return target
    
    @abstractmethod
    def get_topmost_windows(self) -> List[dict]:
        """
        获取所有置顶窗口
        
        Returns:
            列表，每项为 {"hwnd": int, "title": str, "pid": int}
        """
        pass
    
    def clear_all_topmost(self, hwnds: Optional[List[int]] = None) -> None:
        """
        取消所有置顶窗口
        
        Args:
            hwnds: 指定窗口列表，为 None 则取消所有
        """
        if hwnds is None:
            hwnds = [w["hwnd"] for w in self.get_topmost_windows()]
        
        for hwnd in hwnds:
            try:
                self.set_topmost(hwnd, False)
            except Exception:
                pass


class HotkeyListener(ABC):
    """快捷键监听器抽象基类"""
    
    @abstractmethod
    def start(self, hotkey: str, callback: Callable) -> None:
        """
        启动快捷键监听
        
        Args:
            hotkey: 快捷键字符串，如 'ctrl+space'
            callback: 触发时的回调函数
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止监听"""
        pass
    
    @abstractmethod
    def update_hotkey(self, new_hotkey: str) -> None:
        """
        热更新快捷键
        
        Args:
            new_hotkey: 新的快捷键字符串
        """
        pass
    
    @property
    @abstractmethod
    def hotkey(self) -> Optional[str]:
        """当前快捷键"""
        pass
