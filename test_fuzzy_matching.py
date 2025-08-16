#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模糊匹配功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.glossary_manager import GlossaryManager

def test_fuzzy_matching():
    """测试模糊匹配功能"""
    
    print("🔍 模糊匹配功能测试")
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
    
    # 测试用例3: 词典提示生成
    print("\n--- 测试用例3: 词典提示生成 ---")
    if relevant_terms:
        prompt = glossary_manager.create_dynamic_glossary_prompt(relevant_terms, "en", "zh-CN")
        print("生成的词典提示:")
        print(prompt)
    
    print("\n✅ 测试完成")
    print("\n💡 模糊匹配功能说明:")
    print("1. 支持拼写错误的容忍（如：联邦→联合）")
    print("2. 使用编辑距离算法计算相似度")
    print("3. 置信度较低（0.5-0.8），需要AI谨慎处理")
    print("4. 适用于处理原mod作者的拼写错误")

if __name__ == "__main__":
    test_fuzzy_matching()
