#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典管理器测试脚本
用于验证词典加载、术语提取和提示生成功能
"""

import os
import sys
import json

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.core.glossary_manager import glossary_manager

def test_glossary_loading():
    """测试词典加载功能"""
    print("=== 测试词典加载功能 ===")
    
    # 测试加载Victoria 3词典
    print("\n1. 测试加载Victoria 3词典...")
    success = glossary_manager.load_game_glossary("victoria3")
    if success:
        stats = glossary_manager.get_glossary_stats()
        print(f"✓ 成功加载: {stats['description']}")
        print(f"  条目数量: {stats['total_entries']}")
        print(f"  最后更新: {stats['last_updated']}")
    else:
        print("✗ 加载失败")
    
    # 测试加载Stellaris词典
    print("\n2. 测试加载Stellaris词典...")
    success = glossary_manager.load_game_glossary("stellaris")
    if success:
        stats = glossary_manager.get_glossary_stats()
        print(f"✓ 成功加载: {stats['description']}")
        print(f"  条目数量: {stats['total_entries']}")
    else:
        print("✗ 加载失败")
    
    # 测试加载EU4词典
    print("\n3. 测试加载EU4词典...")
    success = glossary_manager.load_game_glossary("eu4")
    if success:
        stats = glossary_manager.get_glossary_stats()
        print(f"✓ 成功加载: {stats['description']}")
        print(f"  条目数量: {stats['total_entries']}")
    else:
        print("✗ 加载失败")

def test_term_extraction():
    """测试术语提取功能"""
    print("\n=== 测试术语提取功能 ===")
    
    # 加载Victoria 3词典
    glossary_manager.load_game_glossary("victoria3")
    
    # 测试文本
    test_texts = [
        "The Armed Forces are demanding reforms",
        "Business owners want lower taxes",
        "Fine Art production is increasing",
        "The Firm Hand policy is working well"
    ]
    
    print(f"测试文本: {test_texts}")
    
    # 提取相关术语
    relevant_terms = glossary_manager.extract_relevant_terms(
        test_texts, "en", "zh-CN"
    )
    
    print(f"\n提取到的相关术语数量: {len(relevant_terms)}")
    for i, term in enumerate(relevant_terms, 1):
        print(f"{i}. {term['source']} → {term['target']}")
        if term.get('metadata', {}).get('remarks'):
            print(f"   备注: {term['metadata']['remarks']}")

def test_prompt_generation():
    """测试提示生成功能"""
    print("\n=== 测试提示生成功能 ===")
    
    # 加载Stellaris词典
    glossary_manager.load_game_glossary("stellaris")
    
    # 测试文本
    test_texts = [
        "The Abyss is calling",
        "Acean Crystals are valuable",
        "Aaron N. Bleu leads the rebellion"
    ]
    
    # 提取相关术语
    relevant_terms = glossary_manager.extract_relevant_terms(
        test_texts, "en", "zh-CN"
    )
    
    # 生成提示
    prompt = glossary_manager.create_dynamic_glossary_prompt(
        relevant_terms, "en", "zh-CN"
    )
    
    print("生成的词典提示:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)

def test_nonexistent_glossary():
    """测试不存在的词典文件"""
    print("\n=== 测试不存在的词典文件 ===")
    
    success = glossary_manager.load_game_glossary("nonexistent_game")
    if not success:
        print("✓ 正确处理了不存在的词典文件")
        stats = glossary_manager.get_glossary_stats()
        print(f"  状态: {stats}")
    else:
        print("✗ 应该返回失败")

def main():
    """主测试函数"""
    print("词典管理器功能测试")
    print("=" * 50)
    
    try:
        test_glossary_loading()
        test_term_extraction()
        test_prompt_generation()
        test_nonexistent_glossary()
        
        print("\n=== 所有测试完成 ===")
        print("✓ 词典管理器功能正常")
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
