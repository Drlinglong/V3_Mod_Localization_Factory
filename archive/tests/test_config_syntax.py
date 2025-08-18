#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试config.py的语法正确性
"""

import sys
import os

def test_config_syntax():
    """测试配置文件语法"""
    try:
        # 尝试导入配置文件
        sys.path.insert(0, os.path.abspath('.'))
        import scripts.config
        
        print("✅ 配置文件语法正确！")
        print(f"  - 项目名称: {scripts.config.PROJECT_NAME}")
        print(f"  - 版本: {scripts.config.VERSION}")
        print(f"  - 支持语言数: {len(scripts.config.LANGUAGES)}")
        print(f"  - 标点符号配置语言数: {len(scripts.config.LANGUAGE_PUNCTUATION_CONFIG)}")
        print(f"  - 游戏配置数: {len(scripts.config.GAME_PROFILES)}")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ 配置文件存在语法错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置文件存在其他错误: {e}")
        return False

if __name__ == "__main__":
    success = test_config_syntax()
    sys.exit(0 if success else 1)
