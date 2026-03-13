"""
Windows 窗口管理器
基于 pywin32 实现
"""

import ctypes
import logging
import sys
from typing import List, Optional

from platforms.base import WindowManager

try:
    import win32con
    import win32gui
    import win32process
except ImportError as e:
    raise ImportError(
        f"无法导入 pywin32（当前 Python {sys.version_info.major}.{sys.version_info.minor}）\n"
        f"请运行：pip install \"pywin32>=311\"\n"
        f"原始错误：{e}"
    ) from e

log = logging.getLogger(__name__)

HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_FLAGS = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
WS_EX_TOPMOST = win32con.WS_EX_TOPMOST


class WindowsWindowManager(WindowManager):
    """Windows 窗口管理器实现"""
    
    def __init__(self):
        self._is_admin = self._check_admin()
    
    def _check_admin(self) -> bool:
        """检查是否有管理员权限"""
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    
    def _get_window_title(self, hwnd: int) -> str:
        """安全获取窗口标题"""
        try:
            return win32gui.GetWindowText(hwnd)
        except Exception:
            return ""
    
    def get_foreground_window(self) -> tuple[int, str]:
        """获取当前焦点窗口"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                log.warning("GetForegroundWindow 返回空句柄")
                return 0, ""
            title = self._get_window_title(hwnd)
            log.info(f"当前焦点窗口: hwnd={hwnd}  title={title!r}")
            return hwnd, title
        except Exception as e:
            log.error(f"get_foreground_window 异常: {e}")
            return 0, ""
    
    def is_topmost(self, hwnd: int) -> bool:
        """判断窗口是否置顶"""
        try:
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            return bool(ex_style & WS_EX_TOPMOST)
        except Exception as e:
            log.error(f"is_topmost 异常 hwnd={hwnd}: {e}")
            return False
    
    def set_topmost(self, hwnd: int, on: bool) -> bool:
        """设置窗口置顶状态"""
        if not hwnd:
            log.warning("set_topmost: hwnd 为空，跳过")
            return False
        
        insert_after = HWND_TOPMOST if on else HWND_NOTOPMOST
        action = "置顶" if on else "取消置顶"
        title = self._get_window_title(hwnd)
        
        try:
            if not win32gui.IsWindow(hwnd):
                log.warning(f"set_topmost: 无效窗口句柄 hwnd={hwnd}")
                return False
            win32gui.SetWindowPos(hwnd, insert_after, 0, 0, 0, 0, SWP_FLAGS)
            log.info(f"{action}成功: hwnd={hwnd}  title={title!r}")
            return True
        except PermissionError:
            raise
        except Exception as e:
            error_code = getattr(e, 'winerror', getattr(e, 'args', [None])[0])
            if error_code in (1400, 1401, 1402):
                log.warning(f"set_topmost: 无效窗口句柄 hwnd={hwnd}")
                return False
            log.error(f"set_topmost 异常 hwnd={hwnd}: {e}")
            if not self._is_admin:
                raise PermissionError(
                    f"无法操作窗口: {title!r}，请以管理员运行"
                ) from e
            return False
    
    def get_topmost_windows(self) -> List[dict]:
        """获取所有置顶窗口"""
        result: List[dict] = []
        
        def _callback(hwnd: int, _) -> None:
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return
                title = self._get_window_title(hwnd)
                if not title:
                    return
                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                if not (ex_style & WS_EX_TOPMOST):
                    return
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                result.append({"hwnd": hwnd, "title": title, "pid": pid})
            except Exception as e:
                log.debug(f"枚举窗口跳过 hwnd={hwnd}: {e}")
        
        try:
            win32gui.EnumWindows(_callback, None)
        except Exception as e:
            log.error(f"get_topmost_windows EnumWindows 失败: {e}")
        
        log.info(f"当前置顶窗口数量: {len(result)}")
        return result
