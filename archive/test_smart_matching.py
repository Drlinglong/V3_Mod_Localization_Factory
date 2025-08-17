#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能术语匹配功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.glossary_manager import GlossaryManager

def test_smart_matching():
    """测试智能术语匹配功能"""
    
    # 初始化词典管理器
    glossary_manager = GlossaryManager()
    
    # 加载群星词典
    print("加载群星词典...")
    success = glossary_manager.load_game_glossary('stellaris')
    if not success:
        print("❌ 无法加载群星词典")
        return
    
    print("✅ 群星词典加载成功")
    
    # 测试用例1: 精确匹配
    print("\n--- 测试用例1: 精确匹配 ---")
    test_texts = ["This is about Alarai ships"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  [{term.get('match_type', 'unknown').upper()}] "
              f"{term['translations']['en']} → {term['translations']['zh-CN']} "
              f"(置信度: {term.get('confidence', 1.0):.1f})")
    
    # 测试用例2: 变体匹配
    print("\n--- 测试用例2: 变体匹配 ---")
    test_texts = ["This is about Alarei ships"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  [{term.get('match_type', 'unknown').upper()}] "
              f"{term['translations']['en']} → {term['translations']['zh-CN']} "
              f"(置信度: {term.get('confidence', 1.0):.1f})")
    
    # 测试用例3: 部分匹配（模拟）
    print("\n--- 测试用例3: 部分匹配（模拟） ---")
    print("注意：当前词典中可能没有适合部分匹配的条目")
    print("建议添加包含 'abbreviations' 或 'sub_terms' 字段的条目来测试")
    
    # 测试用例4: 词典提示生成
    print("\n--- 测试用例4: 词典提示生成 ---")
    if relevant_terms:
        prompt = glossary_manager.create_dynamic_glossary_prompt(relevant_terms, "en", "zh-CN")
        print("生成的词典提示:")
        print(prompt)
    
    print("\n✅ 测试完成")
    print("\n💡 使用建议：")
    print("1. 在词典条目中添加 'abbreviations' 字段来支持缩写匹配")
    print("2. 在词典条目中添加 'sub_terms' 字段来支持层级术语匹配")
    print("3. 系统会自动识别匹配类型并显示置信度")

if __name__ == "__main__":
    test_smart_matching()
