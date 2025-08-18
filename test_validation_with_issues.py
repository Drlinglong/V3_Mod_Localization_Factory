#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后处理验证器的问题检测功能
创建包含各种格式问题的翻译文件，以便测试验证器的错误、警告和信息检测
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量跳过语言选择
os.environ['SKIP_LANGUAGE_SELECTION'] = '1'

def create_test_files_with_issues():
    """创建包含格式问题的测试文件"""
    
    # 创建测试目录
    test_dir = "test_validation_issues"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建包含各种问题的Victoria 3翻译文件
    vic3_content = """l_simp_chinese:
# 正常文本
test_normal: "这是一个正常的翻译文本"
test_concept: "这是一个概念链接 [concept_legitimacy] 的文本"

# 错误级别问题 (ERROR) - 会导致游戏崩溃或无法识别
test_chinese_in_brackets: "方括号内包含中文 [中文函数] 这是错误的"
test_chinese_in_concept: "[Concept('中文key', '显示文本')] 概念键包含中文"
test_chinese_in_scope: "[SCOPE.sCountry('中文scope')] 作用域键包含中文"
test_chinese_in_icon: "图标标签包含中文 @中文图标!"

# 警告级别问题 (WARNING) - 可能导致显示异常但不会崩溃
test_missing_space: "格式化命令缺少空格 #b粗体文本#! 应该 #b 粗体文本#!"
test_unknown_formatting: "使用未知的格式化命令 #bold 粗体文本#! 应该是 #b"
test_unpaired_tags: "颜色标签不成对 #R 红色文本 没有结束符"

# 信息级别问题 (INFO) - 建议检查但影响较小
test_tooltip_complex: "复杂的提示框 #tooltippable;tooltip:<中文tooltip_key> 文本"
test_scope_complex: "复杂的作用域 [This.GetName|中文格式化] 包含中文"
"""

    # 创建包含各种问题的Stellaris翻译文件
    stellaris_content = """l_simp_chinese:
# 正常文本
test_normal: "这是一个正常的群星翻译文本"
test_scope: "作用域命令 [Root.GetName] 正常"

# 错误级别问题
test_chinese_in_brackets: "方括号内包含中文 [Root.中文函数] 错误"
test_chinese_in_vars: "变量包含中文 $中文变量$ 错误"
test_chinese_in_icons: "图标包含中文 £中文图标£ 错误"

# 警告级别问题
test_color_tags_mismatch: "颜色标签不匹配 §R 红色文本 §Y 黄色文本 没有结束符"
test_escaped_brackets: "转义括号错误 [[ 应该是单个 ["
"""

    # 写入测试文件
    with open(os.path.join(test_dir, "vic3_test.yml"), "w", encoding="utf-8-sig") as f:
        f.write(vic3_content)
    
    with open(os.path.join(test_dir, "stellaris_test.yml"), "w", encoding="utf-8-sig") as f:
        f.write(stellaris_content)
    
    print(f"✅ 测试文件已创建在 {test_dir} 目录中")
    print("这些文件包含各种格式问题，可以用来测试后处理验证器")
    
    return test_dir

def explain_validation_levels():
    """解释验证级别的区别"""
    print("\n" + "="*60)
    print("后处理验证级别说明")
    print("="*60)
    
    print("\n🔴 ERROR (错误) - 最高级别，必须修复：")
    print("   • 方括号内包含中文字符: [中文函数]")
    print("   • 概念键包含中文: [Concept('中文key', ...)]")
    print("   • 变量名包含中文: $中文变量$")
    print("   • 图标标签包含中文: @中文图标!")
    print("   → 这些会导致游戏崩溃、无法识别指令或显示异常")
    
    print("\n🟡 WARNING (警告) - 中等级别，建议修复：")
    print("   • 格式化命令缺少空格: #b粗体文本#! (应该是 #b 粗体文本#!)")
    print("   • 使用未知的格式化命令: #bold (应该是 #b)")
    print("   • 标签不成对: #R 红色文本 (缺少 #!)")
    print("   • 颜色标签不匹配: §R 红色 §Y 黄色 (没有 §!)")
    print("   → 这些可能导致文本显示异常，但不会崩溃")
    
    print("\n🔵 INFO (信息) - 最低级别，建议检查：")
    print("   • 复杂的提示框结构中的中文")
    print("   • 作用域格式化中的中文")
    print("   → 这些通常不会影响游戏运行，但建议保持一致性")
    
    print("\n📊 CSV输出说明：")
    print("   • 校对进度列: 显示统计摘要 (如: Errors: 3, Warnings: 2, Info: 1)")
    print("   • 备注列: 显示详细问题列表，每行一个问题")
    print("   • 格式: L行号 | 级别 | 消息 | 详情")

if __name__ == "__main__":
    print("=== 后处理验证器测试文件生成器 ===")
    
    # 创建测试文件
    test_dir = create_test_files_with_issues()
    
    # 解释验证级别
    explain_validation_levels()
    
    print(f"\n📁 测试文件位置: {os.path.abspath(test_dir)}")
    print("💡 提示: 将这些文件复制到你的mod的localization文件夹中，")
    print("   然后运行翻译流程，就能看到后处理验证器检测到的问题了！")
