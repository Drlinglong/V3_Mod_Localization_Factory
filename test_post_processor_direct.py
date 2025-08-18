#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试后处理器脚本
直接处理 test_validation_issues 目录中的测试文件，验证后处理器的功能
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量跳过语言选择
os.environ['SKIP_LANGUAGE_SELECTION'] = '1'

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def test_post_processor_directly():
    """直接测试后处理器"""
    print("=== 直接测试后处理器 ===")
    
    # 检查测试文件是否存在
    test_dir = "test_validation_issues"
    if not os.path.exists(test_dir):
        print(f"❌ 测试目录 {test_dir} 不存在，请先运行 test_validation_with_issues.py")
        return
    
    # 导入后处理管理器
    try:
        from scripts.core.post_processing_manager import PostProcessingManager
        from scripts.config import GAME_PROFILES
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return
    
    # 创建模拟的游戏配置（Victoria 3）
    game_profile = GAME_PROFILES["1"]  # Victoria 3
    
    # 创建输出目录
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建后处理管理器
    post_processor = PostProcessingManager(game_profile, output_dir)
    
    # 模拟目标语言
    target_lang = {"key": "l_simp_chinese", "name": "简体中文"}
    
    print(f"🎮 游戏: {post_processor.game_name}")
    print(f"🔑 游戏ID: {post_processor.game_id}")
    print(f"🔧 标准化键: {post_processor.normalized_game_key}")
    print(f"📁 输出目录: {output_dir}")
    
    # 运行验证
    print("\n--- 开始验证 ---")
    success = post_processor.run_validation(target_lang)
    
    if success:
        # 获取统计信息
        stats = post_processor.get_validation_stats()
        print(f"\n📊 验证统计:")
        print(f"   总文件数: {stats['total_files']}")
        print(f"   正常文件: {stats['valid_files']}")
        print(f"   问题文件: {stats['files_with_issues']}")
        print(f"   错误数: {stats['total_errors']}")
        print(f"   警告数: {stats['total_warnings']}")
        print(f"   信息数: {stats['total_info']}")
        
        # 显示详细结果
        if post_processor.validation_results:
            print(f"\n🔍 详细问题:")
            for file_path, results in post_processor.validation_results.items():
                filename = os.path.basename(file_path)
                print(f"\n📄 文件: {filename}")
                
                # 按行号分组
                line_results = {}
                for result in results:
                    line_num = result.line_number or 0
                    if line_num not in line_results:
                        line_results[line_num] = []
                    line_results[line_num].append(result)
                
                # 显示每行的问题
                for line_num in sorted(line_results.keys()):
                    print(f"   第 {line_num} 行:")
                    for result in line_results[line_num]:
                        level_icon = {
                            "ERROR": "🔴",
                            "WARNING": "🟡", 
                            "INFO": "🔵"
                        }.get(result.level.value.upper(), "⚪")
                        
                        print(f"     {level_icon} {result.level.value.upper()}: {result.message}")
                        if result.details:
                            print(f"       详情: {result.details}")
        else:
            print("\n✅ 所有文件验证通过，未发现格式问题")
    else:
        print("\n❌ 验证过程中发生错误")

def test_specific_validators():
    """测试特定的验证器"""
    print("\n=== 测试特定验证器 ===")
    
    try:
        from scripts.utils.post_process_validator import Victoria3Validator, StellarisValidator
        
        # 测试Victoria 3验证器
        print("\n🎮 测试 Victoria 3 验证器:")
        vic3_validator = Victoria3Validator()
        
        test_texts = [
            ("正常文本", "这是一个正常的翻译文本 [concept_legitimacy]"),
            ("方括号中文", "方括号内包含中文 [中文函数] 这是错误的"),
            ("概念键中文", "[Concept('中文key', '显示文本')] 概念键包含中文"),
            ("缺少空格", "格式化命令缺少空格 #b粗体文本#! 应该 #b 粗体文本#!"),
            ("未知命令", "使用未知的格式化命令 #bold 粗体文本#! 应该是 #b")
        ]
        
        for desc, text in test_texts:
            print(f"\n  📝 {desc}: {text}")
            results = vic3_validator.validate_text(text, 1)
            if results:
                for result in results:
                    level_icon = {
                        "ERROR": "🔴",
                        "WARNING": "🟡",
                        "INFO": "🔵"
                    }.get(result.level.value.upper(), "⚪")
                    print(f"    {level_icon} {result.level.value.upper()}: {result.message}")
                    if result.details:
                        print(f"      详情: {result.details}")
            else:
                print("    ✅ 无问题")
        
        # 测试Stellaris验证器
        print("\n🎮 测试 Stellaris 验证器:")
        stellaris_validator = StellarisValidator()
        
        stellaris_texts = [
            ("正常文本", "这是一个正常的群星翻译文本 [Root.GetName]"),
            ("方括号中文", "方括号内包含中文 [Root.中文函数] 错误"),
            ("变量中文", "变量包含中文 $中文变量$ 错误"),
            ("颜色标签不匹配", "颜色标签不匹配 §R 红色文本 §Y 黄色文本 没有结束符")
        ]
        
        for desc, text in stellaris_texts:
            print(f"\n  📝 {desc}: {text}")
            results = stellaris_validator.validate_text(text, 1)
            if results:
                for result in results:
                    level_icon = {
                        "ERROR": "🔴",
                        "WARNING": "🟡",
                        "INFO": "🔵"
                    }.get(result.level.value.upper(), "⚪")
                    print(f"    {level_icon} {result.level.value.upper()}: {result.message}")
                    if result.details:
                        print(f"      详情: {result.details}")
            else:
                print("    ✅ 无问题")
                
    except ImportError as e:
        print(f"❌ 导入验证器失败: {e}")

if __name__ == "__main__":
    setup_logging()
    
    # 测试后处理器
    test_post_processor_directly()
    
    # 测试特定验证器
    test_specific_validators()
    
    print("\n=== 测试完成 ===")
