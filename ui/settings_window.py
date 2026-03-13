"""
settings_window.py  —  设置窗口模块
提供图形化配置界面，支持多语言
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ui.tray_app import TrayApp
    from config.config_manager import AppConfig

from core.i18n import t

log = logging.getLogger(__name__)

_settings_window: Optional[tk.Tk] = None


def show_settings_window(tray: 'TrayApp', config: 'AppConfig') -> None:
    """显示设置窗口"""
    global _settings_window
    
    if _settings_window is not None:
        try:
            _settings_window.lift()
            _settings_window.focus_force()
            return
        except tk.TclError:
            _settings_window = None
    
    _settings_window = tk.Tk()
    _settings_window.title(t('settings.title'))
    _settings_window.geometry("400x380")
    _settings_window.resizable(False, False)
    
    _settings_window.protocol("WM_DELETE_WINDOW", _on_close)
    
    _create_widgets(_settings_window, tray, config)
    
    _settings_window.mainloop()
    _settings_window = None


def _create_widgets(window: tk.Tk, tray: 'TrayApp', config: 'AppConfig') -> None:
    main_frame = ttk.Frame(window, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    title_label = ttk.Label(
        main_frame, 
        text=f"⚙️ {t('settings.title')}",
        font=('Microsoft YaHei UI', 14, 'bold')
    )
    title_label.pack(pady=(0, 20))
    
    settings_frame = ttk.LabelFrame(main_frame, text=t('settings.general'), padding="10")
    settings_frame.pack(fill=tk.X, pady=(0, 15))
    
    notify_var = tk.BooleanVar(value=config.notify_on_topmost)
    notify_check = ttk.Checkbutton(
        settings_frame,
        text=t('settings.show_notifications'),
        variable=notify_var
    )
    notify_check.pack(anchor=tk.W, pady=5)
    
    prefix_var = tk.BooleanVar(value=config.show_title_prefix)
    prefix_check = ttk.Checkbutton(
        settings_frame,
        text=t('settings.show_title_prefix'),
        variable=prefix_var
    )
    prefix_check.pack(anchor=tk.W, pady=5)
    
    hotkey_frame = ttk.LabelFrame(main_frame, text=t('settings.hotkey_section'), padding="10")
    hotkey_frame.pack(fill=tk.X, pady=(0, 15))
    
    hotkey_label = ttk.Label(hotkey_frame, text=t('settings.current_hotkey', hotkey=config.hotkey.upper()))
    hotkey_label.pack(side=tk.LEFT, padx=(0, 10))
    
    def change_hotkey():
        from ui.hotkey_dialog import show_hotkey_dialog
        new_hotkey = show_hotkey_dialog(config.hotkey)
        if new_hotkey:
            hotkey_label.config(text=t('settings.current_hotkey', hotkey=new_hotkey.upper()))
            if tray.on_hotkey_change:
                tray.on_hotkey_change(new_hotkey)
    
    change_btn = ttk.Button(hotkey_frame, text=t('settings.change'), command=change_hotkey)
    change_btn.pack(side=tk.RIGHT)
    
    about_frame = ttk.LabelFrame(main_frame, text=t('settings.about'), padding="10")
    about_frame.pack(fill=tk.X, pady=(0, 15))
    
    about_text = f"""{t('settings.version', version=config.version)}
{t('settings.author')}
{t('settings.license')}

{t('settings.hotkey_hint', hotkey=config.hotkey.upper())}"""
    
    about_label = ttk.Label(about_frame, text=about_text, justify=tk.LEFT)
    about_label.pack(anchor=tk.W)
    
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    def save_settings():
        from config import config_manager
        config_manager.update(
            notify_on_topmost=notify_var.get(),
            show_title_prefix=prefix_var.get(),
        )
        messagebox.showinfo(t('settings.saved'), t('settings.saved'))
        log.info("设置已保存")
    
    save_btn = ttk.Button(button_frame, text=t('settings.save'), command=save_settings)
    save_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    close_btn = ttk.Button(button_frame, text=t('settings.close'), command=_on_close)
    close_btn.pack(side=tk.RIGHT)


def _on_close() -> None:
    global _settings_window
    if _settings_window:
        _settings_window.destroy()
        _settings_window = None
