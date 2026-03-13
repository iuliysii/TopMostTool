"""
test_hotkey_listener.py  —  快捷键监听器测试
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWindowsHotkeyListener(unittest.TestCase):
    """Windows 快捷键监听器测试"""
    
    def setUp(self):
        """测试前准备"""
        if sys.platform != 'win32':
            self.skipTest("Windows only test")
    
    def test_init(self):
        """测试初始化"""
        from platforms.windows.hotkey_listener import WindowsHotkeyListener
        listener = WindowsHotkeyListener()
        
        self.assertIsNone(listener.hotkey)
        self.assertIsNone(listener._callback)
    
    def test_hotkey_property(self):
        """测试 hotkey 属性"""
        from platforms.windows.hotkey_listener import WindowsHotkeyListener
        listener = WindowsHotkeyListener()
        listener._hotkey = "ctrl+space"
        
        self.assertEqual(listener.hotkey, "ctrl+space")
    
    @patch('platforms.windows.hotkey_listener.keyboard')
    def test_start_creates_thread(self, mock_keyboard):
        """测试 start 创建线程"""
        from platforms.windows.hotkey_listener import WindowsHotkeyListener
        listener = WindowsHotkeyListener()
        callback = Mock()
        
        listener.start("ctrl+space", callback)
        
        self.assertIsNotNone(listener._thread)
        self.assertEqual(listener.hotkey, "ctrl+space")
        
        listener.stop()
    
    @patch('platforms.windows.hotkey_listener.keyboard')
    def test_stop_stops_thread(self, mock_keyboard):
        """测试 stop 停止线程"""
        from platforms.windows.hotkey_listener import WindowsHotkeyListener
        listener = WindowsHotkeyListener()
        listener.start("ctrl+space", Mock())
        listener.stop()
        
        time.sleep(0.1)
        
        self.assertFalse(listener._thread.is_alive())
    
    @patch('platforms.windows.hotkey_listener.keyboard')
    def test_update_hotkey(self, mock_keyboard):
        """测试热更新快捷键"""
        from platforms.windows.hotkey_listener import WindowsHotkeyListener
        listener = WindowsHotkeyListener()
        listener.start("ctrl+space", Mock())
        listener.update_hotkey("ctrl+f9")
        
        self.assertEqual(listener.hotkey, "ctrl+f9")
        
        listener.stop()


class TestHotkeyListenerInterface(unittest.TestCase):
    """快捷键监听器接口测试"""
    
    def test_abstract_methods_exist(self):
        """测试抽象方法存在"""
        from platforms.base import HotkeyListener
        
        required_methods = [
            'start',
            'stop',
            'update_hotkey',
            'hotkey',
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(HotkeyListener, method))


if __name__ == "__main__":
    unittest.main()
