"""
test_config_manager.py  —  配置管理模块测试
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config_manager


class TestAppConfig(unittest.TestCase):
    """AppConfig 数据类测试"""
    
    def test_default_values(self):
        """测试默认值"""
        config = config_manager.AppConfig()
        self.assertEqual(config.hotkey, "ctrl+space")
        self.assertFalse(config.autostart)
        self.assertTrue(config.notify_on_topmost)
        self.assertFalse(config.show_title_prefix)
    
    def test_hotkey_normalization(self):
        """测试快捷键规范化"""
        config = config_manager.AppConfig(hotkey="  CTRL+SPACE  ")
        self.assertEqual(config.hotkey, "ctrl+space")
    
    def test_is_valid_hotkey(self):
        """测试快捷键验证"""
        config = config_manager.AppConfig(hotkey="ctrl+space")
        self.assertTrue(config.is_valid_hotkey())
        
        config2 = config_manager.AppConfig(hotkey="ctrl+f9")
        self.assertTrue(config2.is_valid_hotkey())
    
    def test_invalid_hotkey_gets_reset(self):
        """测试无效快捷键被重置"""
        config = config_manager.AppConfig(hotkey="invalid")
        self.assertEqual(config.hotkey, "ctrl+space")
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = config_manager.AppConfig(hotkey="ctrl+f9")
        data = config.to_dict()
        self.assertEqual(data["hotkey"], "ctrl+f9")
        self.assertIn("version", data)
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {"hotkey": "ctrl+f12", "autostart": True}
        config = config_manager.AppConfig.from_dict(data)
        self.assertEqual(config.hotkey, "ctrl+f12")
        self.assertTrue(config.autostart)
    
    def test_from_dict_ignores_unknown_keys(self):
        """测试从字典创建时忽略未知字段"""
        data = {"hotkey": "ctrl+f12", "unknown_field": "value"}
        config = config_manager.AppConfig.from_dict(data)
        self.assertEqual(config.hotkey, "ctrl+f12")
        self.assertFalse(hasattr(config, "unknown_field"))


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager._config_cache = None
    
    def test_load_default(self):
        """测试加载默认配置"""
        config = config_manager.load()
        self.assertIsInstance(config, config_manager.AppConfig)
    
    def test_get_returns_cached(self):
        """测试 get 返回缓存实例"""
        config1 = config_manager.get()
        config2 = config_manager.get()
        self.assertIs(config1, config2)
    
    def test_update_changes_config(self):
        """测试更新配置"""
        config_manager._config_cache = config_manager.AppConfig()
        
        config_manager.update(notify_on_topmost=False)
        config = config_manager.get()
        self.assertFalse(config.notify_on_topmost)
        
        config_manager.update(notify_on_topmost=True)


class TestConfigPersistence(unittest.TestCase):
    """配置持久化测试"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "config.json")
        
        self.original_path = config_manager._config_path
        config_manager._config_path = lambda: self.config_file
        config_manager._config_cache = None
    
    def tearDown(self):
        """清理临时目录"""
        config_manager._config_path = self.original_path
        config_manager._config_cache = None
        
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_save_and_load(self):
        """测试保存和加载"""
        config = config_manager.AppConfig(hotkey="ctrl+f9", autostart=True)
        config_manager.save(config)
        
        self.assertTrue(os.path.exists(self.config_file))
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data["hotkey"], "ctrl+f9")
        self.assertTrue(data["autostart"])


if __name__ == "__main__":
    unittest.main()
