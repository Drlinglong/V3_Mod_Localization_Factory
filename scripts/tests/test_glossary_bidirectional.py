#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试词典双向翻译功能
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.core.glossary_manager import GlossaryManager
from scripts.utils import i18n

def test_bidirectional_translation():
    """测试双向翻译功能"""
    print("=== 测试词典双向翻译功能 ===")
    
    # 先加载语言文件
    print("\n0. 加载语言文件...")
    i18n.load_language('zh_CN')  # 强制加载中文
    print("✅ 语言文件加载完成")
    
    # 创建词典管理器实例
    manager = GlossaryManager()
    
    # 测试加载Stellaris词典
    print("\n1. 测试加载Stellaris词典...")
    success = manager.load_game_glossary('stellaris')
    if success:
        print("✅ 主词典加载成功")
        stats = manager.get_glossary_stats()
        print(f"   条目数量: {stats['total_entries']}")
    else:
        print("❌ 主词典加载失败")
        return
    
    # 测试加载BA外挂词典
    print("\n2. 测试加载BA外挂词典...")
    auxiliary_glossaries = manager.scan_auxiliary_glossaries('stellaris')
    if auxiliary_glossaries:
        print(f"✅ 发现 {len(auxiliary_glossaries)} 个外挂词典")
        for i, aux in enumerate(auxiliary_glossaries):
            print(f"   [{i+1}] {aux['name']} - {aux['entry_count']} 条术语")
        
        # 加载第一个外挂词典
        success = manager.load_auxiliary_glossaries([0])
        if success:
            print("✅ 外挂词典加载成功")
        else:
            print("❌ 外挂词典加载失败")
    else:
        print("⚠️  未发现外挂词典")
    
    # 测试双向翻译
    print("\n3. 测试双向翻译功能...")
    
    # 测试用例：不同语言对
    test_cases = [
        ("en", "zh-CN", "Arona"),
        ("zh-CN", "en", "阿罗娜"),
        ("en", "ja", "EX Skill"),
        ("ja", "en", "EXスキル"),
        ("en", "ko", "Academy"),
        ("ko", "en", "학원"),
    ]
    
    for source_lang, target_lang, test_term in test_cases:
        print(f"\n   测试: {source_lang} → {target_lang}")
        print(f"   测试术语: '{test_term}'")
        
        # 模拟待翻译文本
        test_texts = [f"This is a test with {test_term} in it"]
        
        # 提取相关术语
        relevant_terms = manager.extract_relevant_terms(test_texts, source_lang, target_lang)
        
        if relevant_terms:
            print(f"   ✅ 找到 {len(relevant_terms)} 个相关术语")
            for term in relevant_terms:
                source = term['translations'][source_lang]
                target = term['translations'][target_lang]
                print(f"      '{source}' → '{target}'")
        else:
            print(f"   ❌ 未找到相关术语")
    
    # 测试词典状态
    print("\n4. 测试词典状态...")
    if manager.has_any_glossary():
        status = manager.get_glossary_status_summary()
        print(f"✅ 词典状态: {status}")
    else:
        print("❌ 无可用词典")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_bidirectional_translation()
