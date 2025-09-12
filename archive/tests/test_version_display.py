#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试版本信息显示的国际化功能
"""

import os
import sys

# 根据当前文件位置计算项目根目录并加入 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_version_display():
    """测试版本信息显示"""
    try:
        # 1. 设置日志系统
        from scripts.utils import logger
        logger.setup_logger()
        
        # 2. 加载语言文件
        from scripts.utils import i18n
        i18n.load_language()
        
        # 3. 显示版本信息
        from scripts.main import display_version_info
        display_version_info()
        
        print("\n✅ 测试完成！版本信息显示功能正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_version_display()
