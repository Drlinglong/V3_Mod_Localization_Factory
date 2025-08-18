# test_simple_validator.py
# ---------------------------------------------------------------
"""
简化的后处理验证器测试
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_victoria3_validation():
    """测试维多利亚3验证逻辑"""
    print("\n=== 测试维多利亚3验证逻辑 ===")
    
    # 直接导入验证器类
    from scripts.utils.post_process_validator import Victoria3Validator, ValidationLevel
    
    validator = Victoria3Validator()
    
    # 测试用例
    test_cases = [
        ("正常的文本，包含[GetName]", "应该没有错误"),
        ("有问题的文本，包含[GetName中文]", "应该检测到方括号内的中文字符"),
        ("另一个有问题的文本，包含$中文变量$", "应该检测到变量内的中文字符"),
        ("正常的文本，包含#bold 内容#!", "应该没有错误")
    ]
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {description}")
        print(f"文本: {text}")
        
        try:
            results = validator.validate_text(text, i)
            
            if results:
                for result in results:
                    print(f"  - {result.level.value}: {result.message}")
                    if result.details:
                        print(f"    详情: {result.details}")
            else:
                print("  - 无问题")
        except Exception as e:
            print(f"  - 验证过程中发生错误: {e}")

def test_stellaris_validation():
    """测试群星验证逻辑"""
    print("\n=== 测试群星验证逻辑 ===")
    
    from scripts.utils.post_process_validator import StellarisValidator
    
    validator = StellarisValidator()
    
    test_cases = [
        ("正常的文本，包含[Root.GetName]", "应该没有错误"),
        ("有问题的文本，包含[Root.中文变量]", "应该检测到方括号内的中文字符"),
        ("有问题的文本，包含$中文变量$", "应该检测到变量内的中文字符"),
        ("有问题的文本，包含£中文图标£", "应该检测到图标内的中文字符")
    ]
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {description}")
        print(f"文本: {text}")
        
        try:
            results = validator.validate_text(text, i)
            
            if results:
                for result in results:
                    print(f"  - {result.level.value}: {result.message}")
                    if result.details:
                        print(f"    详情: {result.details}")
            else:
                print("  - 无问题")
        except Exception as e:
            print(f"  - 验证过程中发生错误: {e}")

def test_main_validator():
    """测试主验证器"""
    print("\n=== 测试主验证器 ===")
    
    from scripts.utils.post_process_validator import PostProcessValidator
    
    try:
        validator = PostProcessValidator()
        
        # 测试批量验证
        test_texts = [
            "正常的文本，包含[GetName]",
            "有问题的文本，包含[GetName中文]",
            "另一个有问题的文本，包含$中文变量$",
            "正常的文本，包含#bold 内容#!"
        ]
        
        print("测试批量验证...")
        batch_results = validator.validate_batch("1", test_texts, 1)
        
        print(f"批量验证结果: {len(batch_results)} 行有问题")
        for line_num, results in batch_results.items():
            print(f"  第 {line_num} 行:")
            for result in results:
                print(f"    - {result.level.value}: {result.message}")
        
        # 测试验证摘要
        print("\n验证摘要:")
        validator.log_validation_summary(batch_results, "Victoria 3")
        
    except Exception as e:
        print(f"主验证器测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("开始测试后处理验证器...")
    
    try:
        # 测试各个验证器
        test_victoria3_validation()
        test_stellaris_validation()
        
        # 测试主验证器
        test_main_validator()
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
