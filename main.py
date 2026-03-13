"""
main.py  —  应用入口
整合所有模块，启动托盘主循环。支持多语言、跨平台
"""

import logging
import sys

from core.logger import setup_logging, get_logger
from core.app_state import get_state
from core.i18n import init as init_i18n, t, get_language

setup_logging()
log = get_logger("main")

try:
    from config import config_manager
    from ui.tray_app import TrayApp
except ImportError as e:
    log.error(f"模块导入失败: {e}")
    log.error("请确认已安装依赖：pip install -r requirements.txt")
    sys.exit(1)


_window_manager = None
_hotkey_listener = None


def on_hotkey_triggered() -> None:
    """快捷键触发时的处理逻辑"""
    state = get_state()
    
    hwnd, title = _window_manager.get_foreground_window()
    
    if not hwnd:
        log.warning("on_hotkey_triggered: 未能获取焦点窗口，跳过")
        return
    
    try:
        new_state = _window_manager.toggle_topmost(hwnd)
    except PermissionError:
        log.warning(f"权限不足，无法操作窗口: {title!r}")
        if state.tray_ref:
            state.tray_ref.notify(t('notifications.permission_denied'), t('notifications.run_as_admin'))
        return
    except Exception as e:
        log.error(f"toggle_topmost 意外异常 hwnd={hwnd}: {e}")
        return
    
    short_title = (title[:28] + "…") if len(title) > 28 else title
    
    if new_state:
        state.add_hwnd(hwnd)
        log.info(t('log.pinned', hwnd=hwnd, title=title))
        if state.tray_ref:
            state.tray_ref.notify(t('notifications.pinned'), short_title)
    else:
        state.remove_hwnd(hwnd)
        log.info(t('log.unpinned', hwnd=hwnd, title=title))
        if state.tray_ref:
            state.tray_ref.notify(t('notifications.unpinned'), short_title)


def on_clear_all() -> None:
    """取消全部置顶窗口"""
    state = get_state()
    hwnds = state.get_hwnds()
    
    if not hwnds:
        log.info("on_clear_all: 当前无置顶窗口，跳过")
        return
    
    _window_manager.clear_all_topmost(hwnds)
    count = state.clear_hwnds()
    
    if state.tray_ref:
        state.tray_ref.notify(t('notifications.all_unpinned'), t('notifications.windows_restored'))
    
    log.info(t('log.clear_all', count=count))


def on_quit() -> None:
    """退出前清理"""
    log.info(t('log.exiting'))
    on_clear_all()
    if _hotkey_listener:
        _hotkey_listener.stop()
    log.info(t('log.cleanup_done'))


def on_hotkey_change(new_hotkey: str) -> None:
    """快捷键变化回调"""
    config_manager.update(hotkey=new_hotkey)
    if _hotkey_listener:
        _hotkey_listener.update_hotkey(new_hotkey)
    log.info(f"快捷键已更新为: {new_hotkey.upper()}")


def main() -> None:
    global _window_manager, _hotkey_listener
    
    log.info(t('log.starting'))
    
    try:
        from platforms import get_platform, get_window_manager, get_hotkey_listener
        log.info(f"检测到平台: {get_platform()}")
    except ImportError as e:
        log.error(f"平台模块导入失败: {e}")
        sys.exit(1)
    
    try:
        cfg = config_manager.load()
    except Exception as e:
        log.error(f"配置加载失败，使用默认值: {e}")
        cfg = config_manager.AppConfig()
    
    init_i18n(cfg.language)
    
    try:
        _window_manager = get_window_manager()
        _hotkey_listener = get_hotkey_listener()
    except RuntimeError as e:
        log.error(str(e))
        sys.exit(1)
    except ImportError as e:
        log.error(f"平台依赖缺失: {e}")
        sys.exit(1)
    
    hotkey = cfg.hotkey
    log.info(t('log.config_loaded', hotkey=hotkey))
    
    try:
        _hotkey_listener.start(hotkey, on_hotkey_triggered)
        log.info(t('log.hotkey_started', hotkey=hotkey.upper()))
    except Exception as e:
        log.error(f"快捷键监听启动失败: {e}")
        sys.exit(1)
    
    state = get_state()
    
    tray = TrayApp(
        on_clear_all=on_clear_all,
        on_quit=on_quit,
        on_hotkey_change=on_hotkey_change,
    )
    
    state.set_tray(tray)
    state.on_state_changed = lambda has_topmost, t=tray: t.update_icon(has_topmost)
    
    log.info(t('log.ready'))
    log.info(t('log.pin_hint', hotkey=hotkey.upper()))
    log.info(t('log.tray_hint'))
    
    tray.run()


if __name__ == "__main__":
    main()
