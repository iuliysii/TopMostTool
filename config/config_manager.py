"""
config_manager.py  —  配置管理模块
支持配置验证、批量更新、热重载、类型安全
"""

import json
import logging
import os
import sys
import winreg
from dataclasses import dataclass, asdict, field
from typing import Any, Optional, Callable, List

log = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """应用配置数据类，提供类型安全的配置访问"""
    hotkey: str = "ctrl+space"
    autostart: bool = False
    notify_on_topmost: bool = True
    show_title_prefix: bool = False
    language: str = "zh_CN"
    version: str = "1.1"
    
    VALID_HOTKEYS: tuple = (
        "ctrl+space", "ctrl+f1", "ctrl+f2", "ctrl+f3", "ctrl+f4",
        "ctrl+f5", "ctrl+f6", "ctrl+f7", "ctrl+f8", "ctrl+f9",
        "ctrl+f10", "ctrl+f11", "ctrl+f12", "alt+space", "alt+f1",
        "win+t", "ctrl+alt+t", "ctrl+shift+t"
    )
    
    VALID_LANGUAGES: tuple = ("zh_CN", "en")
    
    def __post_init__(self):
        self.hotkey = self._normalize_hotkey(self.hotkey)
        self._validate()
    
    def _normalize_hotkey(self, hotkey: str) -> str:
        """规范化快捷键格式"""
        if not hotkey:
            return "ctrl+space"
        return hotkey.lower().strip()
    
    def _validate(self) -> None:
        """验证配置值"""
        if not self.is_valid_hotkey():
            log.warning(f"Invalid hotkey '{self.hotkey}', using default")
            self.hotkey = "ctrl+space"
        
        if self.language not in self.VALID_LANGUAGES:
            log.warning(f"Invalid language '{self.language}', using default")
            self.language = "zh_CN"
    
    def is_valid_hotkey(self) -> bool:
        """检查快捷键是否有效"""
        if self.hotkey in self.VALID_HOTKEYS:
            return True
        parts = self.hotkey.split('+')
        if len(parts) < 2:
            return False
        valid_modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd', 'super'}
        return any(p in valid_modifiers for p in parts)
    
    def validate_and_fix(self) -> List[str]:
        """验证并修复配置，返回警告列表"""
        warnings = []
        
        if not self.is_valid_hotkey():
            warnings.append(f"Invalid hotkey '{self.hotkey}', reset to default")
            self.hotkey = "ctrl+space"
        
        if self.language not in self.VALID_LANGUAGES:
            warnings.append(f"Invalid language '{self.language}', reset to default")
            self.language = "zh_CN"
        
        return warnings
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {k: v for k, v in asdict(self).items() if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """从字典创建配置，忽略未知字段"""
        if not isinstance(data, dict):
            return cls()
        
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        
        try:
            return cls(**filtered)
        except TypeError as e:
            log.warning(f"Config creation error: {e}")
            return cls()


_config_cache: Optional[AppConfig] = None
_change_callbacks: list[Callable[[AppConfig], None]] = []


def _config_path() -> str:
    """获取配置文件路径"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        parent = os.path.dirname(base_dir)
        if os.path.exists(os.path.join(parent, 'config.json')):
            base_dir = parent
    return os.path.join(base_dir, "config.json")


def load() -> AppConfig:
    """加载配置，返回 AppConfig 实例"""
    global _config_cache
    
    path = _config_path()
    file_data = {}
    
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            log.debug(f"Config loaded from: {path}")
        except json.JSONDecodeError as e:
            log.warning(f"Invalid JSON in config file: {e}")
        except Exception as e:
            log.warning(f"Failed to read config file: {e}")
    
    _config_cache = AppConfig.from_dict(file_data)
    warnings = _config_cache.validate_and_fix()
    
    for warning in warnings:
        log.warning(warning)
    
    return _config_cache


def save(config: Optional[AppConfig] = None) -> None:
    """保存配置到文件（原子写入）"""
    global _config_cache
    
    if config is not None:
        _config_cache = config
    
    if _config_cache is None:
        return
    
    path = _config_path()
    parent_dir = os.path.dirname(path)
    
    if parent_dir and not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except Exception as e:
            log.error(f"Failed to create config directory: {e}")
            return
    
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(_config_cache.to_dict(), f, indent=2, ensure_ascii=False)
        
        if os.path.exists(path):
            os.replace(temp_path, path)
        else:
            os.rename(temp_path, path)
        
        log.debug(f"Config saved to: {path}")
    except Exception as e:
        log.error(f"Failed to save config: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


def get() -> AppConfig:
    """获取当前配置实例"""
    global _config_cache
    if _config_cache is None:
        _config_cache = load()
    return _config_cache


def update(**kwargs) -> bool:
    """批量更新配置项，返回是否成功"""
    config = get()
    changed = False
    
    for key, value in kwargs.items():
        if not hasattr(config, key):
            log.warning(f"Unknown config key: {key}")
            continue
        
        old_value = getattr(config, key)
        if old_value != value:
            try:
                setattr(config, key, value)
                changed = True
                log.info(f"Config updated: {key} = {value}")
            except Exception as e:
                log.error(f"Failed to set {key}: {e}")
    
    if changed:
        save(config)
        _notify_change(config)
    
    return changed


def on_change(callback: Callable[[AppConfig], None]) -> None:
    """注册配置变化回调"""
    if callback not in _change_callbacks:
        _change_callbacks.append(callback)


def _notify_change(config: AppConfig) -> None:
    """通知配置变化"""
    for callback in _change_callbacks[:]:
        try:
            callback(config)
        except Exception as e:
            log.error(f"Config callback error: {e}")


def set_autostart(enable: bool) -> None:
    """设置或取消开机自启 (Windows only)"""
    if sys.platform != 'win32':
        log.warning("Autostart is only supported on Windows")
        return
    
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key_name = "TopMostTool"
    
    if getattr(sys, 'frozen', False):
        app_path = sys.executable
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_script = os.path.join(project_root, "main.py")
        app_path = f'"{sys.executable}" "{main_script}"'
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
        if enable:
            winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, app_path)
            log.info("Autostart enabled")
        else:
            try:
                winreg.DeleteValue(key, key_name)
                log.info("Autostart disabled")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        
        update(autostart=enable)
    except PermissionError:
        raise PermissionError("Permission denied: cannot modify registry")
    except Exception as e:
        log.error(f"Failed to set autostart: {e}")
        raise


def get_autostart() -> bool:
    """检查当前自启状态 (Windows only)"""
    if sys.platform != 'win32':
        return False
    
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key_name = "TopMostTool"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, key_name)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    print("=== Config Manager Test ===")
    config = load()
    print(f"Config: {config.to_dict()}")
    print(f"Valid hotkey: {config.is_valid_hotkey()}")
    print(f"Autostart: {get_autostart()}")
    print(f"Config path: {_config_path()}")
    print("=== Test Complete ===")
