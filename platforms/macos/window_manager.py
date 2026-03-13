"""
macOS 窗口管理器
基于 pyobjc 实现
"""

import logging
from typing import List, Optional

from platforms.base import WindowManager

try:
    from AppKit import NSWorkspace, NSApplicationActivationPolicyRegular
    from Cocoa import NSRunningApplication
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGNullWindowID,
        CGWindowLevelForKey,
        kCGFloatingWindowLevel,
    )
except ImportError as e:
    raise ImportError(
        "无法导入 pyobjc\n"
        "请运行：pip install pyobjc-framework-Quartz pyobjc-framework-Cocoa\n"
        f"原始错误：{e}"
    ) from e

log = logging.getLogger(__name__)

FLOATING_WINDOW_LEVEL = CGWindowLevelForKey(kCGFloatingWindowLevel)


class MacOSWindowManager(WindowManager):
    """macOS 窗口管理器实现"""
    
    def __init__(self):
        self._workspace = NSWorkspace.sharedWorkspace()
    
    def get_foreground_window(self) -> tuple[int, str]:
        """获取当前焦点窗口"""
        try:
            app = self._workspace.frontmostApplication()
            if app is None:
                log.warning("无法获取前台应用")
                return 0, ""
            
            pid = app.processIdentifier()
            title = self._get_app_title(app)
            
            log.info(f"当前焦点窗口: pid={pid}  title={title!r}")
            return pid, title
        except Exception as e:
            log.error(f"get_foreground_window 异常: {e}")
            return 0, ""
    
    def _get_app_title(self, app) -> str:
        """获取应用标题"""
        try:
            return app.localizedName() or ""
        except Exception:
            return ""
    
    def _get_window_info(self, pid: int) -> Optional[dict]:
        """获取指定 PID 的窗口信息"""
        try:
            options = 0x100 | 0x1
            window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            
            for window in window_list:
                window_pid = window.get('kCGWindowOwnerPID', 0)
                if window_pid == pid:
                    return window
            return None
        except Exception as e:
            log.error(f"_get_window_info 异常 pid={pid}: {e}")
            return None
    
    def is_topmost(self, hwnd: int) -> bool:
        """判断窗口是否置顶"""
        try:
            window_info = self._get_window_info(hwnd)
            if window_info is None:
                return False
            
            window_level = window_info.get('kCGWindowLayer', 0)
            return window_level >= FLOATING_WINDOW_LEVEL
        except Exception as e:
            log.error(f"is_topmost 异常 hwnd={hwnd}: {e}")
            return False
    
    def set_topmost(self, hwnd: int, on: bool) -> bool:
        """设置窗口置顶状态"""
        try:
            app = NSRunningApplication.runningApplicationWithProcessIdentifier_(hwnd)
            if app is None:
                log.warning(f"找不到进程 pid={hwnd}")
                return False
            
            title = self._get_app_title(app)
            action = "置顶" if on else "取消置顶"
            
            if on:
                success = app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
                if success:
                    app.activateWithOptions_(0)
            else:
                success = True
            
            if success:
                log.info(f"{action}成功: pid={hwnd}  title={title!r}")
            else:
                log.warning(f"{action}失败: pid={hwnd}  title={title!r}")
            
            return success
        except Exception as e:
            log.error(f"set_topmost 异常 hwnd={hwnd}: {e}")
            return False
    
    def get_topmost_windows(self) -> List[dict]:
        """获取所有置顶窗口"""
        result: List[dict] = []
        
        try:
            options = 0x100 | 0x1
            window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            
            for window in window_list:
                try:
                    window_level = window.get('kCGWindowLayer', 0)
                    if window_level < FLOATING_WINDOW_LEVEL:
                        continue
                    
                    pid = window.get('kCGWindowOwnerPID', 0)
                    title = window.get('kCGWindowName', '') or window.get('kCGWindowOwnerName', '')
                    
                    if not title:
                        continue
                    
                    result.append({
                        "hwnd": pid,
                        "title": title,
                        "pid": pid
                    })
                except Exception as e:
                    log.debug(f"处理窗口信息时跳过: {e}")
            
            log.info(f"当前置顶窗口数量: {len(result)}")
        except Exception as e:
            log.error(f"get_topmost_windows 异常: {e}")
        
        return result
