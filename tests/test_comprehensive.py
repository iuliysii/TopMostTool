"""
test_comprehensive.py  —  全面自测用例
包含功能测试、边界条件测试、异常场景测试
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFunctionalCore(unittest.TestCase):
    """核心功能测试"""
    
    def test_app_state_singleton(self):
        """测试状态管理单例"""
        from core.app_state import AppState, get_state, reset_state
        
        reset_state()
        state1 = get_state()
        state2 = get_state()
        
        self.assertIs(state1, state2)
        reset_state()
    
    def test_app_state_hwnd_management(self):
        """测试窗口句柄管理"""
        from core.app_state import get_state, reset_state
        
        reset_state()
        state = get_state()
        
        state.add_hwnd(12345)
        self.assertTrue(state.has_topmost())
        self.assertIn(12345, state.managed_hwnds)
        
        state.remove_hwnd(12345)
        self.assertFalse(state.has_topmost())
        
        reset_state()
    
    def test_app_state_thread_safety(self):
        """测试状态管理线程安全"""
        from core.app_state import get_state, reset_state
        
        reset_state()
        state = get_state()
        
        errors = []
        
        def add_hwnds(start, count):
            try:
                for i in range(start, start + count):
                    state.add_hwnd(i)
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=add_hwnds, args=(i * 1000, 100))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(state.managed_hwnds), 1000)
        
        reset_state()
    
    def test_i18n_translation(self):
        """测试国际化翻译"""
        from core.i18n import init, t, set_language, get_language
        
        init('zh_CN')
        self.assertEqual(get_language(), 'zh_CN')
        self.assertIn('置顶', t('notifications.pinned'))
        
        set_language('en')
        self.assertEqual(get_language(), 'en')
        self.assertIn('Pinned', t('notifications.pinned'))
        
        init('zh_CN')
    
    def test_i18n_missing_key(self):
        """测试缺失翻译键"""
        from core.i18n import init, t
        
        init('zh_CN')
        result = t('nonexistent.key.path')
        
        self.assertEqual(result, 'nonexistent.key.path')


class TestBoundaryConditions(unittest.TestCase):
    """边界条件测试"""
    
    def test_config_empty_values(self):
        """测试配置空值"""
        from config.config_manager import AppConfig
        
        config = AppConfig(hotkey="")
        self.assertEqual(config.hotkey, "ctrl+space")
    
    def test_config_whitespace_values(self):
        """测试配置空白字符"""
        from config.config_manager import AppConfig
        
        config = AppConfig(hotkey="   CTRL+SPACE   ")
        self.assertEqual(config.hotkey, "ctrl+space")
    
    def test_config_invalid_language(self):
        """测试无效语言"""
        from config.config_manager import AppConfig
        
        config = AppConfig(language="invalid_lang")
        self.assertEqual(config.language, "zh_CN")
    
    def test_config_unknown_keys_ignored(self):
        """测试未知配置键被忽略"""
        from config.config_manager import AppConfig
        
        config = AppConfig.from_dict({
            "hotkey": "ctrl+f9",
            "unknown_key": "value",
            "another_unknown": 123
        })
        
        self.assertEqual(config.hotkey, "ctrl+f9")
        self.assertFalse(hasattr(config, "unknown_key"))
    
    def test_window_title_truncation(self):
        """测试窗口标题截断"""
        long_title = "A" * 100
        short_title = (long_title[:28] + "…") if len(long_title) > 28 else long_title
        
        self.assertEqual(len(short_title), 29)
        self.assertTrue(short_title.endswith("…"))
    
    def test_app_state_large_hwnd_count(self):
        """测试大量窗口句柄"""
        from core.app_state import get_state, reset_state
        
        reset_state()
        state = get_state()
        
        for i in range(10000):
            state.add_hwnd(i)
        
        self.assertEqual(len(state.managed_hwnds), 10000)
        
        count = state.clear_hwnds()
        self.assertEqual(count, 10000)
        
        reset_state()


class TestExceptionHandling(unittest.TestCase):
    """异常场景测试"""
    
    def test_config_invalid_json(self):
        """测试无效 JSON 配置"""
        from config import config_manager
        
        original_path = config_manager._config_path
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            config_manager._config_path = lambda: temp_path
            config_manager._config_cache = None
            
            config = config_manager.load()
            
            self.assertIsInstance(config, config_manager.AppConfig)
        finally:
            config_manager._config_path = original_path
            config_manager._config_cache = None
            os.unlink(temp_path)
    
    def test_config_missing_file(self):
        """测试配置文件缺失"""
        from config import config_manager
        
        original_path = config_manager._config_path
        config_manager._config_path = lambda: "/nonexistent/path/config.json"
        config_manager._config_cache = None
        
        try:
            config = config_manager.load()
            self.assertIsInstance(config, config_manager.AppConfig)
        finally:
            config_manager._config_path = original_path
            config_manager._config_cache = None
    
    def test_i18n_missing_language_file(self):
        """测试缺失语言文件"""
        from core.i18n import set_language, get_language
        
        original_lang = get_language()
        
        result = set_language('nonexistent')
        
        self.assertFalse(result)
        self.assertEqual(get_language(), original_lang)
    
    def test_window_manager_invalid_hwnd(self):
        """测试无效窗口句柄"""
        if sys.platform != 'win32':
            self.skipTest("Windows only test")
        
        from platforms.windows.window_manager import WindowsWindowManager
        
        wm = WindowsWindowManager()
        
        result = wm.is_topmost(99999999)
        self.assertFalse(result)
        
        result = wm.set_topmost(99999999, True)
        self.assertFalse(result)


class TestCompatibility(unittest.TestCase):
    """兼容性测试"""
    
    def test_python_version(self):
        """测试 Python 版本兼容性"""
        self.assertGreaterEqual(sys.version_info, (3, 10))
    
    def test_required_modules_import(self):
        """测试必需模块导入"""
        required_modules = [
            'PIL',
            'pystray',
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError as e:
                self.fail(f"Failed to import {module}: {e}")
    
    def test_platform_detection(self):
        """测试平台检测"""
        from platforms import get_platform
        
        platform = get_platform()
        
        self.assertIn(platform, ['windows', 'macos', 'linux', 'unknown'])
    
    def test_platform_module_loading(self):
        """测试平台模块加载"""
        from platforms import get_platform, get_window_manager, get_hotkey_listener
        
        platform = get_platform()
        
        if platform == 'windows':
            wm = get_window_manager()
            hl = get_hotkey_listener()
            
            self.assertIsNotNone(wm)
            self.assertIsNotNone(hl)


class TestUserExperience(unittest.TestCase):
    """用户体验测试"""
    
    def test_hotkey_validation(self):
        """测试快捷键验证"""
        from config.config_manager import AppConfig
        
        valid_hotkeys = [
            "ctrl+space",
            "ctrl+f1",
            "alt+space",
            "ctrl+alt+t",
        ]
        
        for hotkey in valid_hotkeys:
            config = AppConfig(hotkey=hotkey)
            self.assertTrue(config.is_valid_hotkey(), f"Should be valid: {hotkey}")
    
    def test_invalid_hotkey_reset(self):
        """测试无效快捷键重置"""
        from config.config_manager import AppConfig
        
        invalid_hotkeys = [
            "invalid",
            "a",
            "",
            "   ",
        ]
        
        for hotkey in invalid_hotkeys:
            config = AppConfig(hotkey=hotkey)
            self.assertEqual(config.hotkey, "ctrl+space", f"Should reset: {hotkey}")
    
    def test_language_switch_persistence(self):
        """测试语言切换持久化"""
        from core.i18n import set_language, get_language
        
        set_language('en')
        self.assertEqual(get_language(), 'en')
        
        set_language('zh_CN')
        self.assertEqual(get_language(), 'zh_CN')


if __name__ == "__main__":
    unittest.main(verbosity=2)
