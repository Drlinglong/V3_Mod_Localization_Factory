# test_post_process_validator.py
# ---------------------------------------------------------------
"""
测试后处理验证器的功能
"""

import sys
import os
import logging

# 根据当前文件位置计算项目根目录并加入 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.utils.post_process_validator import (
    PostProcessValidator, 
    Victoria3Validator, 
    StellarisValidator,
    EU4Validator,
    HOI4Validator,
    CK3Validator,
    ValidationLevel
)

def setup_logging():
    """设置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_post_process_validation.log', encoding='utf-8')
        ]
    )
    
    # 设置环境变量跳过国际化选择
    os.environ['SKIP_LANGUAGE_SELECTION'] = '1'

def test_victoria3_validator():
    """测试维多利亚3验证器"""
    print("\n=== 测试维多利亚3验证器 ===")
    validator = Victoria3Validator()
    
    # 测试用例
    test_cases = [
        # 正常情况
        ("这是一个正常的文本，包含[GetName]和#bold 粗体文本#!", "应该没有错误"),
        
        # 方括号内有中文字符 - 错误
        ("文本包含[GetName中文]和[中文变量]", "应该检测到方括号内的中文字符错误"),
        
        # 格式化命令格式错误 - 警告
        ("文本包含#123invalid 内容#!", "应该检测到格式化命令格式警告"),
        
        # 工具提示格式错误 - 警告
        ("文本包含#tooltippable;tooltip:<中文键> 内容#!", "应该检测到工具提示键格式警告"),
        
        # 混合情况
        ("文本包含[GetName]和#bold 内容#!以及[中文变量]", "应该检测到多种错误")
    ]
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {description}")
        print(f"文本: {text}")
        results = validator.validate_text(text, i)
        
        if results:
            for result in results:
                print(f"  - {result.level.value}: {result.message}")
                if result.details:
                    print(f"    详情: {result.details}")
        else:
            print("  - 无问题")

def test_stellaris_validator():
    """测试群星验证器"""
    print("\n=== 测试群星验证器 ===")
    validator = StellarisValidator()
    
    test_cases = [
        # 正常情况
        ("这是一个正常的文本，包含[Root.GetName]和$variable$", "应该没有错误"),
        
        # 方括号内有中文字符 - 错误
        ("文本包含[Root.中文变量]和[GetName中文]", "应该检测到方括号内的中文字符错误"),
        
        # 变量内有中文字符 - 错误
        ("文本包含$中文变量$和$变量中文$", "应该检测到变量内的中文字符错误"),
        
        # 图标内有中文字符 - 错误
        ("文本包含£中文图标£和£图标中文£", "应该检测到图标内的中文字符错误")
    ]
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {description}")
        print(f"文本: {text}")
        results = validator.validate_text(text, i)
        
        if results:
            for result in results:
                print(f"  - {result.level.value}: {result.message}")
                if result.details:
                    print(f"    详情: {result.details}")
        else:
            print("  - 无问题")

def test_eu4_validator():
    """测试欧陆风云4验证器"""
    print("\n=== 测试欧陆风云4验证器 ===")
    validator = EU4Validator()
    
    test_cases = [
        # 正常情况
        ("这是一个正常的文本，包含[Root.GetAdjective]和$CAPITAL$", "应该没有错误"),
        
        # 方括号内有中文字符 - 错误
        ("文本包含[Root.中文变量]和[GetName中文]", "应该检测到方括号内的中文字符错误"),
        
        # 变量内有中文字符 - 错误
        ("文本包含$中文变量$和$变量中文$", "应该检测到变量内的中文字符错误"),
        
        # 国家标签格式错误 - 警告
        ("文本包含@中文和@12", "应该检测到国家标签格式警告")
    ]
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {description}")
        print(f"文本: {text}")
        results = validator.validate_text(text, i)
        
        if results:
            for result in results:
                print(f"  - {result.level.value}: {result.message}")
                if result.details:
                    print(f"    详情: {result.details}")
        else:
            print("  - 无问题")

def test_hoi4_validator():
    """测试钢铁雄心4验证器"""
    print("\n=== 测试钢铁雄心4验证器 ===")
    validator = HOI4Validator()
    
    test_cases = [
        # 正常情况
        ("这是一个正常的文本，包含[GetDateText]和$KEY_NAME$", "应该没有错误"),
        
        # 方括号内有中文字符 - 错误
        ("文本包含[GetName中文]和[中文变量]", "应该检测到方括号内的中文字符错误"),
        
        # 格式化变量内有中文字符 - 错误
        ("文本包含[?中文变量|codes]", "应该检测到格式化变量内的中文字符错误"),
        
        # 嵌套字符串内有中文字符 - 错误
        ("文本包含$中文嵌套$和$嵌套中文$", "应该检测到嵌套字符串内的中文字符错误")
    ]
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {description}")
        print(f"文本: {text}")
        results = validator.validate_text(text, i)
        
        if results:
            for result in results:
                print(f"  - {result.level.value}: {result.message}")
                if result.details:
                    print(f"    详情: {result.details}")
        else:
            print("  - 无问题")

def test_ck3_validator():
    """测试十字军之王3验证器"""
    print("\n=== 测试十字军之王3验证器 ===")
    validator = CK3Validator()
    
    test_cases = [
        # 正常情况
        ("这是一个正常的文本，包含[ROOT.Char.GetLadyLord]和$key$", "应该没有错误"),
        
        # 方括号内有中文字符 - 错误
        ("文本包含[ROOT.中文变量]和[GetName中文]", "应该检测到方括号内的中文字符错误"),
        
        # 嵌套字符串内有中文字符 - 错误
        ("文本包含$中文嵌套$和$嵌套中文$", "应该检测到嵌套字符串内的中文字符错误"),
        
        # 文本格式化命令格式错误 - 警告
        ("文本包含#123invalid 内容#!", "应该检测到文本格式化命令格式警告")
    ]
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {description}")
        print(f"文本: {text}")
        results = validator.validate_text(text, i)
        
        if results:
            for result in results:
                print(f"  - {result.level.value}: {result.message}")
                if result.details:
                    print(f"    详情: {result.details}")
        else:
            print("  - 无问题")

def test_main_validator():
    """测试主验证器"""
    print("\n=== 测试主验证器 ===")
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

def test_integration():
    """测试集成功能"""
    print("\n=== 测试集成功能 ===")
    
    # 测试所有游戏的验证
    games = [
        ("1", "Victoria 3", ["[GetName中文]", "正常的[GetName]"]),
        ("2", "Stellaris", ["$中文变量$", "正常的$variable$"]),
        ("3", "EU4", ["[Root.中文]", "正常的[Root.GetName]"]),
        ("4", "HOI4", ["[?中文|codes]", "正常的[GetDateText]"]),
        ("5", "CK3", ["$中文嵌套$", "正常的$key$"])
    ]
    
    for game_id, game_name, texts in games:
        print(f"\n测试游戏: {game_name}")
        validator = PostProcessValidator()
        batch_results = validator.validate_batch(game_id, texts, 1)
        validator.log_validation_summary(batch_results, game_name)

def main():
    """主测试函数"""
    print("开始测试后处理验证器...")
    
    # 设置日志
    setup_logging()
    
    try:
        # 测试各个验证器
        test_victoria3_validator()
        test_stellaris_validator()
        test_eu4_validator()
        test_hoi4_validator()
        test_ck3_validator()
        
        # 测试主验证器
        test_main_validator()
        
        # 测试集成功能
        test_integration()
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
