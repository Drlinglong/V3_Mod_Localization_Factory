#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强后的模糊匹配功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.glossary_manager import GlossaryManager

def test_enhanced_fuzzy_matching():
    """测试增强后的模糊匹配功能"""
    
    print("🔍 测试增强后的模糊匹配功能")
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
    
    # 测试用例1: 严格模式
    print("\n--- 测试用例1: 严格模式 ---")
    glossary_manager.set_fuzzy_matching_mode('strict')
    
    test_texts = ["This is about Alarai ships"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"严格模式找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  [{term.get('match_type', 'unknown').upper()}] "
              f"{term['translations']['en']} → {term['translations']['zh-CN']} "
              f"(置信度: {term.get('confidence', 1.0):.1f})")
    
    # 测试用例2: 宽松模式
    print("\n--- 测试用例2: 宽松模式 ---")
    glossary_manager.set_fuzzy_matching_mode('loose')
    
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"宽松模式找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  [{term.get('match_type', 'unknown').upper()}] "
              f"{term['translations']['en']} → {term['translations']['zh-CN']} "
              f"(置信度: {term.get('confidence', 1.0):.1f})")
    
    # 测试用例3: 中文断句测试
    print("\n--- 测试用例3: 中文断句测试 ---")
    test_texts = ["这是关于阿拉莱舰船和上古看护者的内容"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "zh-CN", "en")
    print(f"中文文本找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  [{term.get('match_type', 'unknown').upper()}] "
              f"{term['translations']['zh-CN']} → {term['translations']['en']} "
              f"(置信度: {term.get('confidence', 1.0):.1f})")
    
    # 测试用例4: 词典提示生成
    print("\n--- 测试用例4: 词典提示生成 ---")
    if relevant_terms:
        prompt = glossary_manager.create_dynamic_glossary_prompt(relevant_terms, "zh-CN", "en")
        print("生成的英文Prompt:")
        print(prompt)
    
    print("\n✅ 测试完成")
    print("\n💡 增强功能说明:")
    print("1. 支持严格模式（禁用模糊匹配）和宽松模式（启用模糊匹配）")
    print("2. 修复了中文断句问题，支持字符级别的模糊匹配")
    print("3. 调整置信度范围到0.3-0.6")
    print("4. 用户可以在选择外挂词典后选择模糊匹配模式")

if __name__ == "__main__":
    test_enhanced_fuzzy_matching()
