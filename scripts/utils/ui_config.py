"""UI 配置读写工具"""
import json
import os

# 配置文件路径，相对于项目根目录
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ui_config.json')

def load_ui_config():
    """读取UI配置，如果不存在则返回默认值"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 默认返回简体中文与 Soft 主题
    return {"language": "zh_CN", "theme": "Soft"}

def save_ui_config(cfg: dict):
    """保存UI配置"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
