import os
import sys
import json
import winreg
from typing import Any, Optional

# 默认配置
DEFAULT_CONFIG = {
    "hotkey": "ctrl+space",
    "autostart": False,
    "notify_on_topmost": True,
    "show_title_prefix": False,
    "version": "1.0"
}

# 内存中的配置缓存
_config_cache: dict = {}

def _config_path() -> str:
    """
    获取配置文件路径。
    PyInstaller 打包时返回 exe 所在目录，开发模式返回脚本所在目录。
    """
    if getattr(sys, 'frozen', False):
        # 打包后的 exe 所在目录
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发模式脚本所在目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "config.json")

def load() -> dict:
    """加载配置，合并默认值以保证向前兼容"""
    global _config_cache
    path = _config_path()
    file_data = {}
    
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
        except Exception:
            file_data = {}
            
    # 合并默认配置与文件配置
    _config_cache = {**DEFAULT_CONFIG, **file_data}
    return _config_cache

def save(config: Optional[dict] = None) -> None:
    """保存配置到文件"""
    global _config_cache
    if config is not None:
        _config_cache = config
        
    path = _config_path()
    parent_dir = os.path.dirname(path)
    
    # 自动创建父目录
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
        
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(_config_cache, f, indent=2, ensure_ascii=False)

def get(key: str, default=None) -> Any:
    """获取配置项"""
    if not _config_cache:
        load()
    return _config_cache.get(key, default)

def set(key: str, value: Any) -> None:
    """设置配置项并立即保存"""
    if not _config_cache:
        load()
    _config_cache[key] = value
    save()

def set_autostart(enable: bool) -> None:
    """
    设置或取消开机自启。
    写入注册表: HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
    """
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key_name = "TopMostTool"
    
    # 确定启动命令行
    if getattr(sys, 'frozen', False):
        # 打包后的路径
        app_path = sys.executable
    else:
        # 开发模式，入口文件在项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_script = os.path.join(project_root, "main.py")
        app_path = f'"{sys.executable}" "{main_script}"'

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, app_path)
        else:
            try:
                winreg.DeleteValue(key, key_name)
            except FileNotFoundError:
                pass # 键不存在时静默忽略
        winreg.CloseKey(key)
        # 同步更新内存配置
        if _config_cache.get("autostart") != enable:
            _config_cache["autostart"] = enable
            save()
    except PermissionError:
        raise PermissionError("权限不足，无法修改注册表自启项")
    except Exception as e:
        raise e

def get_autostart() -> bool:
    """从注册表检查当前自启状态"""
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
    # --- 测试块 ---
    print("=== 配置管理模块测试 ===")
    
    # 1. 加载并打印
    current_cfg = load()
    print(f"当前完整配置: {current_cfg}")
    
    # 2. 修改测试
    original_hotkey = get('hotkey')
    print(f"原始热键: {original_hotkey}")
    
    set('hotkey', 'ctrl+f9')
    print(f"修改后热键: {get('hotkey')}")
    
    # 3. 恢复原值
    set('hotkey', original_hotkey)
    print(f"已恢复原始热键: {get('hotkey')}")
    
    # 4. 路径与自启状态
    print(f"配置文件路径: {_config_path()}")
    print(f"当前注册表自启状态: {get_autostart()}")
    
    print("=== 测试完成 ===")
