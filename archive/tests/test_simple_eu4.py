#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单EU4测试
"""

import os
import sys
import re

os.environ['SKIP_LANGUAGE_SELECTION'] = '1'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from utils.post_process_validator import EU4Validator

def test_color_tags():
    print("测试EU4颜色标签检测...")
    
    # 创建验证器
    v = EU4Validator()
    
    # 测试文本
    text = "包含 §R 红色但没有 §!"
    print(f"测试文本: {text}")
    
    # 直接测试正则表达式
    start_pattern = r'§[a-zA-Z0-9]'
    start_tags = re.findall(start_pattern, text)
    end_count = text.count('§!')
    
    print(f"起始标签模式: {start_pattern}")
    print(f"找到的起始标签: {start_tags}")
    print(f"起始标签数量: {len(start_tags)}")
    print(f"结束标签数量: {end_count}")
    
    # 运行验证
    results = v.validate_text(text, 1)
    print(f"\n验证结果数量: {len(results)}")
    
    for i, result in enumerate(results):
        print(f"结果 {i+1}:")
        print(f"  级别: {result.level.value}")
        print(f"  消息: {result.message}")
        print(f"  详情: {result.details}")
        print(f"  是否有效: {result.is_valid}")

if __name__ == '__main__':
    test_color_tags()
