#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria 3 验证器简单测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量跳过语言选择
os.environ['SKIP_LANGUAGE_SELECTION'] = '1'

from scripts.utils.post_process_validator import Victoria3Validator

def test_vic3_validator():
    """测试Victoria3Validator的基本功能"""
    print("=== Victoria 3 验证器测试 ===")
    
    # 创建验证器实例
    validator = Victoria3Validator()
    print(f"✅ 验证器创建成功: {validator.game_name}")
    
    # 测试用例1: 正常文本
    print("\n--- 测试用例1: 正常文本 ---")
    text1 = "正常文本 [concept_legitimacy] 和 @icon_name! 以及 #b 粗体文本#!"
    results1 = validator.validate_text(text1, 1)
    print(f"文本: {text1}")
    if results1:
        for result in results1:
            print(f"  - {result.level.value}: {result.message}")
            if result.details:
                print(f"    详情: {result.details}")
    else:
        print("  - 无问题")
    
    # 测试用例2: 错误的格式化命令 #bold
    print("\n--- 测试用例2: 错误的格式化命令 #bold ---")
    text2 = "包含 #bold 粗体文本#! 这是错误的"
    results2 = validator.validate_text(text2, 2)
    print(f"文本: {text2}")
    if results2:
        for result in results2:
            print(f"  - {result.level.value}: {result.message}")
            if result.details:
                print(f"    详情: {result.details}")
    else:
        print("  - 无问题")
    
    # 测试用例3: 缺少空格的格式化命令
    print("\n--- 测试用例3: 缺少空格的格式化命令 ---")
    text3 = "包含 #b粗体文本#! 缺少空格"
    results3 = validator.validate_text(text3, 3)
    print(f"文本: {text3}")
    if results3:
        for result in results3:
            print(f"  - {result.level.value}: {result.message}")
            if result.details:
                print(f"    详情: {result.details}")
    else:
        print("  - 无问题")
    
    # 测试用例4: 中文概念链接
    print("\n--- 测试用例4: 中文概念链接 ---")
    text4 = "包含 [中文概念] 这是错误的"
    results4 = validator.validate_text(text4, 4)
    print(f"文本: {text4}")
    if results4:
        for result in results4:
            print(f"  - {result.level.value}: {result.message}")
            if result.details:
                print(f"    详情: {result.details}")
    else:
        print("  - 无问题")
    
    # 测试用例5: 正确的格式化命令
    print("\n--- 测试用例5: 正确的格式化命令 ---")
    text5 = "包含 #b 粗体文本#! 和 #red 红色文本#! 和 #tooltippable;tooltip:<key>"
    results5 = validator.validate_text(text5, 5)
    print(f"文本: {text5}")
    if results5:
        for result in results5:
            print(f"  - {result.level.value}: {result.message}")
            if result.details:
                print(f"    详情: {result.details}")
    else:
        print("  - 无问题")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_vic3_validator()
