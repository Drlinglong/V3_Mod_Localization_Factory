#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试变体词汇查找功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.glossary_manager import GlossaryManager

def test_variant_lookup():
    """测试变体词汇查找功能"""
    
    # 初始化词典管理器
    glossary_manager = GlossaryManager()
    
    # 加载群星词典
    print("加载群星词典...")
    success = glossary_manager.load_game_glossary('stellaris')
    if not success:
        print("❌ 无法加载群星词典")
        return
    
    print("✅ 群星词典加载成功")
    
    # 测试用例1: 包含主术语的文本
    print("\n--- 测试用例1: 包含主术语的文本 ---")
    test_texts = ["This is about Alarai ships"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  {term['translations']['en']} → {term['translations']['zh-CN']}")
        if term.get('variants', {}).get('en'):
            print(f"    变体: {term['variants']['en']}")
    
    # 测试用例2: 包含变体词汇的文本
    print("\n--- 测试用例2: 包含变体词汇的文本 ---")
    test_texts = ["This is about Alarei ships"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  {term['translations']['en']} → {term['translations']['zh-CN']}")
        if term.get('variants', {}).get('en'):
            print(f"    变体: {term['variants']['en']}")
    
    # 测试用例3: 包含多个变体的文本
    print("\n--- 测试用例3: 包含多个变体的文本 ---")
    test_texts = ["This is about Alarei ships and Irradiated Planet"]
    relevant_terms = glossary_manager.extract_relevant_terms(test_texts, "en", "zh-CN")
    print(f"找到 {len(relevant_terms)} 个相关术语")
    for term in relevant_terms:
        print(f"  {term['translations']['en']} → {term['translations']['zh-CN']}")
        if term.get('variants', {}).get('en'):
            print(f"    变体: {term['variants']['en']}")
    
    # 测试用例4: 测试词典提示生成
    print("\n--- 测试用例4: 词典提示生成 ---")
    if relevant_terms:
        prompt = glossary_manager.create_dynamic_glossary_prompt(relevant_terms, "en", "zh-CN")
        print("生成的词典提示:")
        print(prompt)
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_variant_lookup()
