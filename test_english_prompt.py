#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的英文prompt
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.glossary_manager import GlossaryManager

def test_english_prompt():
    """测试新的英文prompt"""
    
    print("🔍 测试新的英文Prompt")
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
    
    # 测试用例：英文到中文
    print("\n--- 测试用例1: 英文到中文 ---")
    test_texts = ["This is about Alarai ships and the Ancient Caretaker"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    
    if relevant_terms:
        prompt = glossary_manager.create_dynamic_glossary_prompt(relevant_terms, "en", "zh-CN")
        print("\n生成的英文Prompt:")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
    
    # 测试用例：中文到英文
    print("\n--- 测试用例2: 中文到英文 ---")
    test_texts = ["这是关于阿拉莱舰船和上古看护者的内容"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "zh-CN", "en")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    
    if relevant_terms:
        prompt = glossary_manager.create_dynamic_glossary_prompt(relevant_terms, "zh-CN", "en")
        print("\n生成的英文Prompt:")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
    
    print("\n✅ 测试完成")
    print("\n💡 新Prompt的特点:")
    print("1. 使用英文，与API handler保持一致")
    print("2. 语言无关，支持任何语言对")
    print("3. 保留了所有匹配类型和置信度信息")
    print("4. 中文版本保留在注释中，便于参考")

if __name__ == "__main__":
    test_english_prompt()
