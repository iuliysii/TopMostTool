"""
tray_app.py  —  系统托盘应用模块
支持动态菜单、设置界面、状态同步、多语言、跨平台
"""

import logging
import os
import sys
import threading
from typing import Callable, Optional

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item, Menu

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.i18n import t, get_language, set_language, get_supported_languages, on_change
from config import config_manager

log = logging.getLogger(__name__)


class TrayApp:
    """系统托盘应用"""
    
    def __init__(
        self,
        on_clear_all: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
        on_hotkey_change: Optional[Callable[[str], None]] = None,
    ):
        self.on_clear_all = on_clear_all
        self.on_quit = on_quit
        self.on_hotkey_change = on_hotkey_change
        
        self._menu_cache: Optional[list] = None
        self._menu_cache_time: float = 0
        self._cache_ttl: float = 1.0
        
        self.icon_active = self._load_icon(True)
        self.icon_inactive = self._load_icon(False)
        
        self.icon = pystray.Icon(
            "TopMostTool",
            self.icon_inactive,
            t('tray.title'),
            menu=Menu(self._generate_menu)
        )
        
        config_manager.on_change(self._on_config_changed)
        on_change(self._on_language_changed)
    
    def _load_icon(self, active: bool) -> Image.Image:
        filename = "icon_active.png" if active else "icon_inactive.png"
        filepath = os.path.join(ROOT_DIR, "assets", filename)
        
        if os.path.exists(filepath):
            try:
                return Image.open(filepath)
            except Exception as e:
                log.debug(f"图标加载失败: {filepath}, {e}")
        
        return self._create_default_icon(active)
    
    def _create_default_icon(self, active: bool) -> Image.Image:
        img = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        color = (30, 78, 140, 255) if active else (80, 80, 80, 255)
        
        draw.ellipse((20, 10, 44, 34), fill=color)
        draw.rectangle((28, 34, 36, 44), fill=color)
        draw.polygon([(28, 44), (36, 44), (32, 60)], fill=color)
        
        return img
    
    def _generate_menu(self):
        config = config_manager.get()
        
        yield item('📌 ' + t('app_name'), lambda: None, enabled=False)
        yield pystray.Menu.SEPARATOR
        
        yield item(
            t('tray.hotkey_label', hotkey=config.hotkey.upper()),
            self._show_hotkey_settings,
            default=True
        )
        
        yield pystray.Menu.SEPARATOR
        
        yield from self._generate_topmost_submenu()
        
        yield pystray.Menu.SEPARATOR
        
        yield item(t('tray.unpin_all'), self._on_clear_all_click)
        
        yield pystray.Menu.SEPARATOR
        
        yield item(t('tray.settings'), self._show_settings)
        
        from platforms import get_platform
        platform = get_platform()
        
        if platform == 'windows':
            is_autostart = config_manager.get_autostart()
            prefix = '✅ ' if is_autostart else '   '
            yield item(f'{prefix}{t("tray.autostart")}', self._toggle_autostart)
        
        yield from self._generate_language_submenu()
        
        yield pystray.Menu.SEPARATOR
        
        yield item(t('tray.exit'), self._on_quit_click)
    
    def _generate_topmost_submenu(self):
        from platforms import get_window_manager
        
        try:
            window_manager = get_window_manager()
            topmost_windows = window_manager.get_topmost_windows()
        except Exception:
            topmost_windows = []
        
        if not topmost_windows:
            yield item(t('tray.topmost_windows'), Menu(item(t('tray.no_topmost_windows'), lambda: None, enabled=False)))
            return
        
        submenu_items = []
        for w in topmost_windows:
            if isinstance(w, dict):
                hwnd = w.get("hwnd")
                title = w.get("title", "")
            else:
                try:
                    hwnd, title = w
                except Exception:
                    continue
            
            if not hwnd:
                continue
            
            display_title = title[:30] + ('...' if len(title) > 30 else '')
            submenu_items.append(
                item(f'📌 {display_title}', self._create_unpin_callback(hwnd))
            )
        
        if submenu_items:
            yield item(t('tray.topmost_windows'), Menu(*submenu_items))
        else:
            yield item(t('tray.topmost_windows'), Menu(item(t('tray.no_topmost_windows'), lambda: None, enabled=False)))
    
    def _generate_language_submenu(self):
        current_lang = get_language()
        supported = get_supported_languages()
        
        menu_items = []
        for lang_code, lang_name in supported.items():
            prefix = '✅ ' if lang_code == current_lang else '   '
            menu_items.append(
                item(f'{prefix}{lang_name}', self._create_language_callback(lang_code))
            )
        
        yield pystray.Menu.SEPARATOR
        yield item(f'🌐 {t("language.current")}', Menu(*menu_items))
    
    def _create_language_callback(self, lang_code: str):
        def callback(icon, item):
            def task():
                set_language(lang_code)
                config_manager.update(language=lang_code)
                icon.update_menu()
            threading.Thread(target=task, daemon=True).start()
        return callback
    
    def _create_unpin_callback(self, hwnd: int):
        def callback(icon, item):
            def task():
                try:
                    from platforms import get_window_manager
                    window_manager = get_window_manager()
                    window_manager.set_topmost(hwnd, False)
                    icon.update_menu()
                except Exception as e:
                    log.error(f"取消置顶失败 hwnd={hwnd}: {e}")
            threading.Thread(target=task, daemon=True).start()
        return callback
    
    def _on_clear_all_click(self, icon, item):
        if self.on_clear_all:
            threading.Thread(target=self.on_clear_all, daemon=True).start()
            icon.update_menu()
    
    def _on_quit_click(self, icon, item):
        def task():
            if self.on_quit:
                self.on_quit()
            icon.stop()
        threading.Thread(target=task, daemon=True).start()
    
    def _toggle_autostart(self, icon, item):
        def task():
            try:
                current = config_manager.get_autostart()
                config_manager.set_autostart(not current)
                icon.update_menu()
            except PermissionError:
                self.notify(t('notifications.permission_denied'), t('notifications.run_as_admin'))
            except Exception as e:
                log.error(f"切换自启失败: {e}")
        threading.Thread(target=task, daemon=True).start()
    
    def _show_settings(self, icon, item):
        def task():
            try:
                from ui.settings_window import show_settings_window
                show_settings_window(self, config_manager.get())
            except ImportError:
                self.notify(t('tray.settings'), "设置界面暂不可用")
            except Exception as e:
                log.error(f"打开设置窗口失败: {e}")
        threading.Thread(target=task, daemon=True).start()
    
    def _show_hotkey_settings(self, icon, item):
        def task():
            try:
                from ui.hotkey_dialog import show_hotkey_dialog
                new_hotkey = show_hotkey_dialog(config_manager.get().hotkey)
                if new_hotkey and self.on_hotkey_change:
                    self.on_hotkey_change(new_hotkey)
                    icon.update_menu()
            except ImportError:
                self.notify(t('tray.settings'), "请通过配置文件修改快捷键")
            except Exception as e:
                log.error(f"打开快捷键设置失败: {e}")
        threading.Thread(target=task, daemon=True).start()
    
    def _on_config_changed(self, config: config_manager.AppConfig) -> None:
        try:
            self.icon.update_menu()
        except Exception:
            pass
    
    def _on_language_changed(self, lang: str) -> None:
        try:
            self.icon.title = t('tray.title')
            self.icon.update_menu()
        except Exception:
            pass
    
    def run(self) -> None:
        self.icon.run()
    
    def notify(self, title: str, msg: str) -> None:
        config = config_manager.get()
        if not config.notify_on_topmost:
            return
        
        if self.icon.HAS_NOTIFICATION:
            self.icon.notify(msg, title)
    
    def update_icon(self, has_topmost: bool) -> None:
        self.icon.icon = self.icon_active if has_topmost else self.icon_inactive
    
    def stop(self) -> None:
        self.icon.stop()
    
    def update_menu(self) -> None:
        self.icon.update_menu()
