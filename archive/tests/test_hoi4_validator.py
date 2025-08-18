#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钢铁雄心4验证器测试文件
测试重构后的HOI4Validator的各种规则
"""

import os
import sys
import logging
import re # Added missing import for re

# 设置环境变量跳过语言选择
os.environ['SKIP_LANGUAGE_SELECTION'] = '1'

# 添加scripts目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from utils.post_process_validator import HOI4Validator, ValidationLevel

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )

def test_hoi4_validator():
    """测试钢铁雄心4验证器"""
    print("开始测试钢铁雄心4验证器...\n")
    
    validator = HOI4Validator()
    
    # 测试用例
    test_cases = [
        {
            "name": "正常文本 - 应该没有错误",
            "text": "这是一个正常的文本，包含[GER.GetName]和$VARIABLE$",
            "expected_errors": 0
        },
        {
            "name": "命名空间内非ASCII字符",
            "text": "有问题的文本，包含[GER.中文函数]",
            "expected_errors": 1
        },
        {
            "name": "格式化变量内非ASCII字符",
            "text": "有问题的文本，包含[?中文变量|default]",
            "expected_errors": 1
        },
        {
            "name": "嵌套字符串内非ASCII字符",
            "text": "有问题的文本，包含$中文变量$",
            "expected_errors": 1
        },
        {
            "name": "图标标签内非ASCII字符",
            "text": "有问题的文本，包含£中文图标",
            "expected_errors": 1
        },
        {
            "name": "国家旗帜标签内非ASCII字符",
            "text": "有问题的文本，包含@中A",
            "expected_errors": 1
        },
        {
            "name": "独立的格式化器内非ASCII字符",
            "text": "中文格式化器|token",
            "expected_errors": 1
        },
        {
            "name": "颜色标签配对检查",
            "text": "有问题的文本，包含§R红色文本但没有结束标签",
            "expected_errors": 0,  # 这个在custom_checks中，不算在rules里
            "expected_warnings": 1
        },
        {
            "name": "复杂混合文本",
            "text": "混合文本：包含[GER.GetName]和$VARIABLE$，但[GER.中文函数]有问题，还有£中文图标",
            "expected_errors": 2
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"=== 测试用例 {i}: {test_case['name']} ===")
        print(f"文本: {test_case['text']}")
        
        results = validator.validate_text(test_case['text'], i)
        
        if not results:
            print("  - 无问题")
        else:
            for result in results:
                level_icon = "❌" if result.level == ValidationLevel.ERROR else "⚠️"
                print(f"  - {level_icon} {result.level.value}: {result.message}")
                if result.details:
                    print(f"    详情: {result.details}")
        
        # 验证结果数量
        error_count = len([r for r in results if r.level == ValidationLevel.ERROR])
        warning_count = len([r for r in results if r.level == ValidationLevel.WARNING])
        
        if error_count == test_case['expected_errors']:
            print(f"  ✅ 错误数量符合预期: {error_count}")
        else:
            print(f"  ❌ 错误数量不符合预期: 期望 {test_case['expected_errors']}, 实际 {error_count}")
        
        if 'expected_warnings' in test_case:
            if warning_count == test_case['expected_warnings']:
                print(f"  ✅ 警告数量符合预期: {warning_count}")
            else:
                print(f"  ❌ 警告数量不符合预期: 期望 {test_case['expected_warnings']}, 实际 {warning_count}")
        
        print()

def test_hoi4_specific_patterns():
    """测试钢铁雄心4特定的正则表达式模式"""
    print("=== 测试钢铁雄心4特定模式 ===\n")
    
    validator = HOI4Validator()
    
    # 测试各种模式
    patterns_to_test = [
        ("命名空间", "[GER.GetName]", "应该匹配"),
        ("命名空间", "[GER.中文函数]", "应该检测到中文"),
        ("格式化变量", "[?variable|default]", "应该匹配"),
        ("格式化变量", "[?中文变量|default]", "应该检测到中文"),
        ("嵌套字符串", "$VARIABLE$", "应该匹配"),
        ("嵌套字符串", "$中文变量$", "应该检测到中文"),
        ("图标标签", "£energy", "应该匹配"),
        ("图标标签", "£中文图标", "应该检测到中文"),
        ("国家旗帜", "@GER", "应该匹配"),
        ("国家旗帜", "@中A", "应该检测到中文"),
        ("独立格式化器", "formatter|token", "应该匹配"),
        ("独立格式化器", "中文格式化器|token", "应该检测到中文")
    ]
    
    for pattern_name, test_text, expected in patterns_to_test:
        print(f"测试 {pattern_name}: '{test_text}' - {expected}")
        
        # 检查是否被任何规则匹配
        matched = False
        for rule in validator.rules:
            if re.search(rule.pattern, test_text):
                matched = True
                print(f"  ✅ 被规则 '{rule.name}' 匹配")
                break
        
        if not matched:
            print(f"  ❌ 未被任何规则匹配")
        
        print()

if __name__ == "__main__":
    setup_logging()
    
    try:
        test_hoi4_validator()
        test_hoi4_specific_patterns()
        print("🎉 钢铁雄心4验证器测试完成！")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
