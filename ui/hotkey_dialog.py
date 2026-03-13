"""
hotkey_dialog.py  —  快捷键设置对话框
支持快捷键录制和预设选择，多语言支持
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional

from core.i18n import t

log = logging.getLogger(__name__)

_dialog_result: Optional[str] = None


def show_hotkey_dialog(current_hotkey: str) -> Optional[str]:
    """
    显示快捷键设置对话框
    
    Args:
        current_hotkey: 当前快捷键
        
    Returns:
        新快捷键，如果取消则返回 None
    """
    global _dialog_result
    _dialog_result = None
    
    dialog = tk.Toplevel()
    dialog.title(t('hotkey_dialog.title'))
    dialog.geometry("350x280")
    dialog.resizable(False, False)
    dialog.transient()
    dialog.grab_set()
    
    frame = ttk.Frame(dialog, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    title_label = ttk.Label(
        frame,
        text=t('hotkey_dialog.header'),
        font=('Microsoft YaHei UI', 12, 'bold')
    )
    title_label.pack(pady=(0, 15))
    
    hotkey_var = tk.StringVar(value=current_hotkey.upper())
    
    record_frame = ttk.LabelFrame(frame, text=t('hotkey_dialog.record_section'), padding="10")
    record_frame.pack(fill=tk.X, pady=(0, 10))
    
    hotkey_display = ttk.Label(
        record_frame,
        textvariable=hotkey_var,
        font=('Consolas', 16, 'bold'),
        anchor=tk.CENTER
    )
    hotkey_display.pack(fill=tk.X, pady=5)
    
    recording_label = ttk.Label(record_frame, text=t('hotkey_dialog.hint'))
    recording_label.pack()
    
    is_recording = [False]
    recorded_keys = []
    
    def start_recording():
        is_recording[0] = True
        recorded_keys.clear()
        hotkey_var.set(t('hotkey_dialog.press_keys'))
        record_btn.config(text=t('hotkey_dialog.recording'))
        dialog.focus_set()
    
    def on_key_press(event):
        if not is_recording[0]:
            return
        
        key = event.keysym.lower()
        
        if key in ('control_l', 'control_r'):
            key = 'ctrl'
        elif key in ('alt_l', 'alt_r'):
            key = 'alt'
        elif key in ('shift_l', 'shift_r'):
            key = 'shift'
        elif key in ('win_l', 'win_r'):
            key = 'win'
        elif key == 'space':
            key = 'space'
        elif key.startswith('f') and key[1:].isdigit():
            key = key
        else:
            return
        
        if key not in recorded_keys:
            recorded_keys.append(key)
            hotkey_var.set('+'.join(k.upper() for k in recorded_keys))
        
        if len(recorded_keys) >= 2 or key in ('space',) or (key.startswith('f') and len(recorded_keys) >= 1):
            is_recording[0] = False
            record_btn.config(text=t('hotkey_dialog.start_recording'))
    
    def on_key_release(event):
        if is_recording[0] and len(recorded_keys) >= 1:
            is_recording[0] = False
            record_btn.config(text=t('hotkey_dialog.start_recording'))
    
    dialog.bind('<KeyPress>', on_key_press)
    dialog.bind('<KeyRelease>', on_key_release)
    
    record_btn = ttk.Button(record_frame, text=t('hotkey_dialog.start_recording'), command=start_recording)
    record_btn.pack(pady=10)
    
    preset_frame = ttk.LabelFrame(frame, text=t('hotkey_dialog.preset_section'), padding="10")
    preset_frame.pack(fill=tk.X, pady=(0, 10))
    
    presets = ["ctrl+space", "ctrl+f9", "ctrl+f12", "alt+space", "ctrl+alt+t"]
    
    preset_buttons_frame = ttk.Frame(preset_frame)
    preset_buttons_frame.pack()
    
    for i, preset in enumerate(presets):
        btn = ttk.Button(
            preset_buttons_frame,
            text=preset.upper(),
            width=10,
            command=lambda p=preset: hotkey_var.set(p.upper())
        )
        btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=(15, 0))
    
    def on_ok():
        global _dialog_result
        new_hotkey = hotkey_var.get().lower()
        if new_hotkey and '+' in new_hotkey:
            parts = new_hotkey.split('+')
            valid_modifiers = {'ctrl', 'alt', 'shift', 'win'}
            has_modifier = any(p in valid_modifiers for p in parts)
            if has_modifier and len(parts) >= 2:
                _dialog_result = new_hotkey
            else:
                from tkinter import messagebox
                messagebox.showwarning(
                    t('hotkey_dialog.invalid_title'),
                    t('hotkey_dialog.invalid_message')
                )
                return
        dialog.destroy()
    
    def on_cancel():
        dialog.destroy()
    
    ok_btn = ttk.Button(button_frame, text=t('hotkey_dialog.ok'), command=on_ok)
    ok_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    cancel_btn = ttk.Button(button_frame, text=t('hotkey_dialog.cancel'), command=on_cancel)
    cancel_btn.pack(side=tk.RIGHT)
    
    dialog.wait_window()
    
    return _dialog_result
