#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实际使用场景中的简称匹配功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.glossary_manager import GlossaryManager

def test_practical_matching():
    """测试实际使用场景中的简称匹配"""
    
    print("🔍 实际使用场景测试")
    print("=" * 50)
    
    # 初始化词典管理器
    glossary_manager = GlossaryManager()
    
    # 加载群星词典
    print("加载群星词典...")
    success = glossary_manager.load_game_glossary('stellaris')
    if not success:
        print("❌ 无法加载群星词典")
        return
    
    print("✅ 群星词典加载成功")
    
    # 测试用例1: 组织名称全称
    print("\n--- 测试用例1: 组织名称全称 ---")
    test_texts = ["This is about Allied Hyakkiyako Academy"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  [{term.get('match_type', 'unknown').upper()}] "
              f"{term['translations']['en']} → {term['translations']['zh-CN']} "
              f"(置信度: {term.get('confidence', 1.0):.1f})")
    
    # 测试用例2: 组织名称简称
    print("\n--- 测试用例2: 组织名称简称 ---")
    test_texts = ["This is about Hyakkiyako"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  [{term.get('match_type', 'unknown').upper()}] "
              f"{term['translations']['en']} → {term['translations']['zh-CN']} "
              f"(置信度: {term.get('confidence', 1.0):.1f})")
    
    # 测试用例3: 中文简称
    print("\n--- 测试用例3: 中文简称 ---")
    test_texts = ["这是关于百鬼夜行的内容"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "zh-CN", "en")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  [{term.get('match_type', 'unknown').upper()}] "
              f"{term['translations']['zh-CN']} → {term['translations']['en']} "
              f"(置信度: {term.get('confidence', 1.0):.1f})")
    
    # 测试用例4: 词典提示生成
    print("\n--- 测试用例4: 词典提示生成 ---")
    if relevant_terms:
        prompt = glossary_manager.create_dynamic_glossary_prompt(relevant_terms, "zh-CN", "en")
        print("生成的词典提示:")
        print(prompt)
    
    print("\n✅ 测试完成")
    print("\n💡 实际使用建议:")
    print("1. 大部分词汇只需要 'variants' 字段")
    print("2. 需要明确简称时，添加 'abbreviations' 字段")
    print("3. 系统会自动识别简称和全称的关系")
    print("4. 适用于组织名称、人名等场景")

if __name__ == "__main__":
    test_practical_matching()
