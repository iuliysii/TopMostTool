"""
Linux 窗口管理器
基于 EWMH (Extended Window Manager Hints) 和 python-xlib 实现
支持大多数符合 EWMH 规范的窗口管理器 (GNOME, KDE, Xfce, etc.)
"""

import logging
from typing import List, Optional

from platforms.base import WindowManager

try:
    from Xlib import X, display
    from Xlib.protocol import event
    from ewmh import EWMH
except ImportError as e:
    raise ImportError(
        "无法导入 X11 相关库\n"
        "请运行：pip install python-xlib ewmh\n"
        "注意：需要 X11 环境\n"
        f"原始错误：{e}"
    ) from e

log = logging.getLogger(__name__)


class LinuxWindowManager(WindowManager):
    """Linux 窗口管理器实现 (基于 EWMH)"""
    
    def __init__(self):
        try:
            self._display = display.Display()
            self._ewmh = EWMH(self._display)
            self._screen = self._display.screen()
            self._root = self._screen.root
        except Exception as e:
            raise RuntimeError(f"无法连接到 X11 显示服务器: {e}") from e
    
    def _get_window_title(self, window) -> str:
        """获取窗口标题"""
        try:
            title = self._ewmh.getWmName(window)
            if title:
                if isinstance(title, bytes):
                    return title.decode('utf-8', errors='ignore')
                return str(title)
        except Exception:
            pass
        return ""
    
    def _get_window_pid(self, window) -> int:
        """获取窗口 PID"""
        try:
            pid = self._ewmh.getWmPid(window)
            return pid if pid else 0
        except Exception:
            return 0
    
    def get_foreground_window(self) -> tuple[int, str]:
        """获取当前焦点窗口"""
        try:
            window = self._ewmh.getActiveWindow()
            if window is None:
                log.warning("无法获取活动窗口")
                return 0, ""
            
            window_id = window.id
            title = self._get_window_title(window)
            
            log.info(f"当前焦点窗口: wid={window_id}  title={title!r}")
            return window_id, title
        except Exception as e:
            log.error(f"get_foreground_window 异常: {e}")
            return 0, ""
    
    def is_topmost(self, hwnd: int) -> bool:
        """判断窗口是否置顶"""
        try:
            window = self._display.create_resource_object('window', hwnd)
            
            state = self._ewmh.getWmState(window)
            if state:
                state_names = state[1] if len(state) > 1 else []
                return '_NET_WM_STATE_ABOVE' in state_names
            
            return False
        except Exception as e:
            log.error(f"is_topmost 异常 hwnd={hwnd}: {e}")
            return False
    
    def set_topmost(self, hwnd: int, on: bool) -> bool:
        """设置窗口置顶状态"""
        try:
            window = self._display.create_resource_object('window', hwnd)
            title = self._get_window_title(window)
            action = "置顶" if on else "取消置顶"
            
            state = self._ewmh.getWmState(window)
            current_states = state[1] if state and len(state) > 1 else []
            
            if on:
                if '_NET_WM_STATE_ABOVE' not in current_states:
                    self._ewmh.setWmState(window, 1, '_NET_WM_STATE_ABOVE')
                    self._ewmh.display.flush()
            else:
                if '_NET_WM_STATE_ABOVE' in current_states:
                    self._ewmh.setWmState(window, 0, '_NET_WM_STATE_ABOVE')
                    self._ewmh.display.flush()
            
            log.info(f"{action}成功: wid={hwnd}  title={title!r}")
            return True
        except Exception as e:
            log.error(f"set_topmost 异常 hwnd={hwnd}: {e}")
            return False
    
    def get_topmost_windows(self) -> List[dict]:
        """获取所有置顶窗口"""
        result: List[dict] = []
        
        try:
            windows = self._ewmh.getClientList()
            
            for window in windows:
                try:
                    state = self._ewmh.getWmState(window)
                    if not state:
                        continue
                    
                    state_names = state[1] if len(state) > 1 else []
                    if '_NET_WM_STATE_ABOVE' not in state_names:
                        continue
                    
                    title = self._get_window_title(window)
                    if not title:
                        continue
                    
                    pid = self._get_window_pid(window)
                    
                    result.append({
                        "hwnd": window.id,
                        "title": title,
                        "pid": pid
                    })
                except Exception as e:
                    log.debug(f"处理窗口信息时跳过: {e}")
            
            log.info(f"当前置顶窗口数量: {len(result)}")
        except Exception as e:
            log.error(f"get_topmost_windows 异常: {e}")
        
        return result
    
    def __del__(self):
        """清理资源"""
        try:
            if hasattr(self, '_display') and self._display:
                self._display.close()
        except Exception:
            pass
