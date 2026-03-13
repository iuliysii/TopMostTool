"""
test_app_state.py  —  应用状态管理模块测试
"""

import threading
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.app_state import AppState, get_state, reset_state


class TestAppState(unittest.TestCase):
    """AppState 测试"""
    
    def setUp(self):
        """每个测试前重置状态"""
        reset_state()
    
    def tearDown(self):
        """每个测试后重置状态"""
        reset_state()
    
    def test_singleton(self):
        """测试单例模式"""
        state1 = get_state()
        state2 = get_state()
        self.assertIs(state1, state2)
    
    def test_add_hwnd(self):
        """测试添加窗口句柄"""
        state = get_state()
        state.add_hwnd(12345)
        
        self.assertIn(12345, state.managed_hwnds)
        self.assertTrue(state.has_topmost())
    
    def test_remove_hwnd(self):
        """测试移除窗口句柄"""
        state = get_state()
        state.add_hwnd(12345)
        state.remove_hwnd(12345)
        
        self.assertNotIn(12345, state.managed_hwnds)
        self.assertFalse(state.has_topmost())
    
    def test_clear_hwnds(self):
        """测试清空句柄"""
        state = get_state()
        state.add_hwnd(111)
        state.add_hwnd(222)
        state.add_hwnd(333)
        
        count = state.clear_hwnds()
        
        self.assertEqual(count, 3)
        self.assertFalse(state.has_topmost())
    
    def test_get_hwnds_returns_copy(self):
        """测试 get_hwnds 返回副本"""
        state = get_state()
        state.add_hwnd(12345)
        
        hwnds = state.get_hwnds()
        hwnds.append(99999)
        
        self.assertNotIn(99999, state.managed_hwnds)
    
    def test_thread_safety(self):
        """测试线程安全"""
        state = get_state()
        state.clear_hwnds()
        
        def add_hwnds(start, count):
            for i in range(start, start + count):
                state.add_hwnd(i)
        
        threads = [
            threading.Thread(target=add_hwnds, args=(i * 1000, 100))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(state.managed_hwnds), 1000)
    
    def test_state_changed_callback(self):
        """测试状态变化回调"""
        state = get_state()
        callback_calls = []
        
        def on_changed(has_topmost):
            callback_calls.append(has_topmost)
        
        state.on_state_changed = on_changed
        state.add_hwnd(12345)
        state.remove_hwnd(12345)
        
        self.assertEqual(len(callback_calls), 2)
        self.assertTrue(callback_calls[0])
        self.assertFalse(callback_calls[1])


if __name__ == "__main__":
    unittest.main()
