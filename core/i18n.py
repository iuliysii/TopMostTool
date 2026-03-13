"""
i18n.py  —  国际化管理模块
支持中英双语切换
"""

import json
import logging
import os
import sys
from typing import Any, Callable, Optional

log = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "zh_CN": "简体中文",
    "en": "English",
}

DEFAULT_LANGUAGE = "zh_CN"

_current_lang: str = DEFAULT_LANGUAGE
_translations: dict[str, Any] = {}
_change_callbacks: list[Callable[[str], None]] = []


def _get_locales_dir() -> str:
    """获取语言资源目录路径"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "locales")


def _load_translations(lang: str) -> dict:
    """加载指定语言的翻译文件"""
    locales_dir = _get_locales_dir()
    file_path = os.path.join(locales_dir, f"{lang}.json")
    
    if not os.path.exists(file_path):
        log.warning(f"Language file not found: {file_path}")
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Failed to load language file {file_path}: {e}")
        return {}


def init(language: Optional[str] = None) -> None:
    """
    初始化国际化模块
    
    Args:
        language: 语言代码，如 'zh_CN' 或 'en'。为 None 时自动检测系统语言
    """
    global _current_lang, _translations
    
    if language is None:
        language = _detect_system_language()
    
    if language not in SUPPORTED_LANGUAGES:
        log.warning(f"Unsupported language '{language}', using default '{DEFAULT_LANGUAGE}'")
        language = DEFAULT_LANGUAGE
    
    _current_lang = language
    _translations = _load_translations(language)
    
    log.info(f"i18n initialized: {language} ({SUPPORTED_LANGUAGES.get(language, language)})")


def _detect_system_language() -> str:
    """检测系统语言"""
    try:
        import locale
        lang = locale.getdefaultlocale()[0]
        if lang:
            if lang.startswith('zh'):
                return 'zh_CN'
            elif lang.startswith('en'):
                return 'en'
    except Exception:
        pass
    
    return DEFAULT_LANGUAGE


def get_language() -> str:
    """获取当前语言代码"""
    return _current_lang


def set_language(lang: str) -> bool:
    """
    切换语言
    
    Args:
        lang: 语言代码
        
    Returns:
        是否切换成功
    """
    global _current_lang, _translations
    
    if lang not in SUPPORTED_LANGUAGES:
        log.warning(f"Unsupported language: {lang}")
        return False
    
    if lang == _current_lang:
        return True
    
    _translations = _load_translations(lang)
    _current_lang = lang
    
    log.info(f"Language changed to: {lang}")
    _notify_change(lang)
    
    return True


def t(key: str, **kwargs) -> str:
    """
    获取翻译文本
    
    Args:
        key: 翻译键，支持点分隔符如 'tray.title'
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    keys = key.split('.')
    value = _translations
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return key
    
    if isinstance(value, str):
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value
        return value
    
    return key


def on_change(callback: Callable[[str], None]) -> None:
    """注册语言变化回调"""
    _change_callbacks.append(callback)


def _notify_change(lang: str) -> None:
    """通知语言变化"""
    for callback in _change_callbacks:
        try:
            callback(lang)
        except Exception as e:
            log.error(f"Language change callback error: {e}")


def get_supported_languages() -> dict[str, str]:
    """获取支持的语言列表"""
    return SUPPORTED_LANGUAGES.copy()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    print("=== i18n 模块测试 ===")
    
    init()
    print(f"当前语言: {get_language()}")
    print(f"tray.title: {t('tray.title')}")
    print(f"tray.hotkey_label: {t('tray.hotkey_label', hotkey='CTRL+SPACE')}")
    
    print("\n切换到英文...")
    set_language('en')
    print(f"当前语言: {get_language()}")
    print(f"tray.title: {t('tray.title')}")
    print(f"tray.hotkey_label: {t('tray.hotkey_label', hotkey='CTRL+SPACE')}")
    
    print("\n切换回中文...")
    set_language('zh_CN')
    print(f"当前语言: {get_language()}")
    print(f"tray.title: {t('tray.title')}")
    
    print("=== 测试完成 ===")
