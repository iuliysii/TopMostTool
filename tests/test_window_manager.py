"""
test_window_manager.py  —  窗口管理器测试
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWindowsWindowManager(unittest.TestCase):
    """Windows 窗口管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        if sys.platform != 'win32':
            self.skipTest("Windows only test")
    
    def test_get_foreground_window_returns_tuple(self):
        """测试获取前台窗口返回元组"""
        from platforms.windows.window_manager import WindowsWindowManager
        wm = WindowsWindowManager()
        
        hwnd, title = wm.get_foreground_window()
        
        self.assertIsInstance(hwnd, int)
        self.assertIsInstance(title, str)
    
    def test_is_topmost_returns_bool(self):
        """测试 is_topmost 返回布尔值"""
        from platforms.windows.window_manager import WindowsWindowManager
        wm = WindowsWindowManager()
        
        result = wm.is_topmost(0)
        
        self.assertIsInstance(result, bool)
    
    def test_get_topmost_windows_returns_list(self):
        """测试获取置顶窗口返回列表"""
        from platforms.windows.window_manager import WindowsWindowManager
        wm = WindowsWindowManager()
        
        result = wm.get_topmost_windows()
        
        self.assertIsInstance(result, list)
    
    def test_toggle_topmost(self):
        """测试切换置顶状态"""
        from platforms.windows.window_manager import WindowsWindowManager
        wm = WindowsWindowManager()
        
        result = wm.toggle_topmost(0)
        self.assertIsInstance(result, bool)


class TestWindowManagerInterface(unittest.TestCase):
    """窗口管理器接口测试"""
    
    def test_abstract_methods_exist(self):
        """测试抽象方法存在"""
        from platforms.base import WindowManager
        
        required_methods = [
            'get_foreground_window',
            'is_topmost',
            'set_topmost',
            'get_topmost_windows',
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(WindowManager, method))
    
    def test_toggle_topmost_implementation(self):
        """测试 toggle_topmost 默认实现"""
        from platforms.base import WindowManager
        
        class MockWindowManager(WindowManager):
            def get_foreground_window(self):
                return 123, "Test Window"
            
            def is_topmost(self, hwnd):
                return False
            
            def set_topmost(self, hwnd, on):
                pass
            
            def get_topmost_windows(self):
                return []
        
        wm = MockWindowManager()
        result = wm.toggle_topmost(123)
        
        self.assertTrue(result)
    
    def test_clear_all_topmost(self):
        """测试清除所有置顶"""
        from platforms.base import WindowManager
        
        class MockWindowManager(WindowManager):
            def __init__(self):
                self.set_topmost_calls = []
            
            def get_foreground_window(self):
                return 0, ""
            
            def is_topmost(self, hwnd):
                return False
            
            def set_topmost(self, hwnd, on):
                self.set_topmost_calls.append((hwnd, on))
            
            def get_topmost_windows(self):
                return [
                    {"hwnd": 1, "title": "Window 1"},
                    {"hwnd": 2, "title": "Window 2"},
                ]
        
        wm = MockWindowManager()
        wm.clear_all_topmost()
        
        self.assertEqual(len(wm.set_topmost_calls), 2)


if __name__ == "__main__":
    unittest.main()
