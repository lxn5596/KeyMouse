import json
import os
from pathlib import Path

class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "window": {
            "stay_on_top": True,
            "transparency": 0.8
        },
        "keyboard": {
            "show_single_key": True,
            "show_combination": True
        },
        "mouse": {
            "show_clicks": True,
            "show_track": True
        },
        "visual": {
            "theme": "dark",
            "animation": True
        }
    }
    
    def __init__(self):
        self.config_file = Path.home() / ".keymouse" / "config.json"
        self.config = self.load_config()
        
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return self.DEFAULT_CONFIG.copy()
        
    def save_config(self):
        """保存配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)
            
    def get(self, key, default=None):
        """获取配置项"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value
        
    def set(self, key, value):
        """设置配置项"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self.save_config() 