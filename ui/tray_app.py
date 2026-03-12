import os
import sys
import threading
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item, Menu

# Allow running this file directly: add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core import window_manager
from config import config_manager

class TrayApp:
    def __init__(
        self,
        on_clear_all: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
    ):
        self.on_clear_all = on_clear_all
        self.on_quit = on_quit
        
        self.icon_active = self._load_icon(True)
        self.icon_inactive = self._load_icon(False)
        
        self.icon = pystray.Icon(
            "TopMostTool",
            self.icon_inactive,
            "TopMost Tool",
            menu=Menu(self._generate_menu)
        )

    def _load_icon(self, active: bool) -> Image.Image:
        filename = "icon_active.png" if active else "icon_inactive.png"
        filepath = os.path.join("assets", filename)
        
        if os.path.exists(filepath):
            try:
                return Image.open(filepath)
            except Exception:
                pass
                
        # Fallback: Generate 64x64 pin icon
        img = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        color = (30, 78, 140, 255) if active else (80, 80, 80, 255)
        
        # Draw a simple pin shape
        # Head
        draw.ellipse((20, 10, 44, 34), fill=color)
        # Body
        draw.rectangle((28, 34, 36, 44), fill=color)
        # Point
        draw.polygon([(28, 44), (36, 44), (32, 60)], fill=color)
        
        return img

    def _generate_menu(self):
        # 1. '📌 TopMost Tool' (disabled)
        yield item('📌 TopMost Tool', lambda: None, enabled=False)
        
        # 2. Separator
        yield pystray.Menu.SEPARATOR
        
        # 3. '已置顶窗口' Submenu
        topmost_windows = window_manager.get_topmost_windows()
        if topmost_windows:
            def create_unpin_callback(hwnd):
                def callback(icon, item):
                    threading.Thread(
                        target=window_manager.set_topmost,
                        args=(hwnd, False),
                        daemon=True
                    ).start()
                return callback

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
                submenu_items.append(item(f'📌 {display_title}', create_unpin_callback(hwnd)))
            if submenu_items:
                yield item('已置顶窗口', Menu(*submenu_items))
            else:
                yield item('已置顶窗口', Menu(item('（无置顶窗口）', lambda: None, enabled=False)))
        else:
            yield item('已置顶窗口', Menu(item('（无置顶窗口）', lambda: None, enabled=False)))
            
        # 4. Separator
        yield pystray.Menu.SEPARATOR
        
        # 5. '取消全部置顶'
        def on_clear_all_wrapper(icon, item):
            if self.on_clear_all:
                threading.Thread(target=self.on_clear_all, daemon=True).start()
        yield item('取消全部置顶', on_clear_all_wrapper)
        
        # 6. Separator
        yield pystray.Menu.SEPARATOR
        
        # 7. '开机自启'
        is_autostart = config_manager.get_autostart()
        prefix = '✅ ' if is_autostart else '   '
        
        def toggle_autostart(icon, item):
            def task():
                config_manager.set_autostart(not is_autostart)
                icon.update_menu()
            threading.Thread(target=task, daemon=True).start()
            
        yield item(f'{prefix}开机自启', toggle_autostart)
        
        # 8. Separator
        yield pystray.Menu.SEPARATOR
        
        # 9. '退出'
        def quit_wrapper(icon, item):
            def task():
                if self.on_quit:
                    self.on_quit()
                icon.stop()
            threading.Thread(target=task, daemon=True).start()
        yield item('退出', quit_wrapper)

    def run(self) -> None:
        self.icon.run()

    def notify(self, title: str, msg: str) -> None:
        if self.icon.HAS_NOTIFICATION:
            self.icon.notify(msg, title)

    def update_icon(self, has_topmost: bool) -> None:
        self.icon.icon = self.icon_active if has_topmost else self.icon_inactive

    def stop(self) -> None:
        self.icon.stop()
