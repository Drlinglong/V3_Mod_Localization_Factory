#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典翻译功能演示脚本
展示如何使用词典管理器进行智能翻译
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.core.glossary_manager import glossary_manager

def demo_victoria3_translation():
    """演示Victoria 3的词典翻译功能"""
    print("🎮 Victoria 3 词典翻译演示")
    print("=" * 50)
    
    # 加载Victoria 3词典
    success = glossary_manager.load_game_glossary("victoria3")
    if not success:
        print("❌ 无法加载Victoria 3词典")
        return
    
    # 模拟待翻译的文本
    texts_to_translate = [
        "The Armed Forces demand higher wages",
        "Business owners are investing in new factories",
        "Fine Art production has increased by 25%",
        "The Firm Hand policy is unpopular with the people",
        "Charles is a popular monarch"
    ]
    
    print(f"📝 待翻译文本:")
    for i, text in enumerate(texts_to_translate, 1):
        print(f"  {i}. {text}")
    
    # 提取相关术语
    relevant_terms = glossary_manager.extract_relevant_terms(
        texts_to_translate, "en", "zh-CN"
    )
    
    print(f"\n🔍 提取到的相关术语 ({len(relevant_terms)} 个):")
    for term in relevant_terms:
        print(f"  • {term['source']} → {term['target']}")
        if term.get('metadata', {}).get('remarks'):
            print(f"    备注: {term['metadata']['remarks']}")
    
    # 生成词典提示
    glossary_prompt = glossary_manager.create_dynamic_glossary_prompt(
        relevant_terms, "en", "zh-CN"
    )
    
    print(f"\n📋 生成的词典提示:")
    print("-" * 50)
    print(glossary_prompt)
    print("-" * 50)
    
    # 模拟AI翻译结果（使用词典）
    print(f"\n🤖 模拟AI翻译结果（使用词典）:")
    for i, text in enumerate(texts_to_translate, 1):
        translated = text
        for term in relevant_terms:
            if term['source'].lower() in text.lower():
                translated = translated.replace(term['source'], term['target'])
        print(f"  {i}. {translated}")

def demo_stellaris_translation():
    """演示Stellaris的词典翻译功能"""
    print("\n🚀 Stellaris 词典翻译演示")
    print("=" * 50)
    
    # 加载Stellaris词典
    success = glossary_manager.load_game_glossary("stellaris")
    if not success:
        print("❌ 无法加载Stellaris词典")
        return
    
    # 模拟待翻译的文本
    texts_to_translate = [
        "The Abyss is calling to our scientists",
        "Acean Crystals are highly valuable resources",
        "Aaron N. Bleu leads the rebellion against the empire",
        "The Abyssal Crater Test Site has been discovered"
    ]
    
    print(f"📝 待翻译文本:")
    for i, text in enumerate(texts_to_translate, 1):
        print(f"  {i}. {text}")
    
    # 提取相关术语
    relevant_terms = glossary_manager.extract_relevant_terms(
        texts_to_translate, "en", "zh-CN"
    )
    
    print(f"\n🔍 提取到的相关术语 ({len(relevant_terms)} 个):")
    for term in relevant_terms:
        print(f"  • {term['source']} → {term['target']}")
        if term.get('metadata', {}).get('remarks'):
            print(f"    备注: {term['metadata']['remarks']}")
    
    # 生成词典提示
    glossary_prompt = glossary_manager.create_dynamic_glossary_prompt(
        relevant_terms, "en", "zh-CN"
    )
    
    print(f"\n📋 生成的词典提示:")
    print("-" * 50)
    print(glossary_prompt)
    print("-" * 50)

def demo_eu4_translation():
    """演示EU4的词典翻译功能"""
    print("\n⚔️ EU4 词典翻译演示")
    print("=" * 50)
    
    # 加载EU4词典
    success = glossary_manager.load_game_glossary("eu4")
    if not success:
        print("❌ 无法加载EU4词典")
        return
    
    # 模拟待翻译的文本
    texts_to_translate = [
        "The Advisor provides excellent counsel",
        "Aggressive Expansion has increased our infamy",
        "Our Alliance with France is strong",
        "The Army marches to war",
        "Artillery bombardment begins"
    ]
    
    print(f"📝 待翻译文本:")
    for i, text in enumerate(texts_to_translate, 1):
        print(f"  {i}. {text}")
    
    # 提取相关术语
    relevant_terms = glossary_manager.extract_relevant_terms(
        texts_to_translate, "en", "zh-CN"
    )
    
    print(f"\n🔍 提取到的相关术语 ({len(relevant_terms)} 个):")
    for term in relevant_terms:
        print(f"  • {term['source']} → {term['target']}")
        if term.get('metadata', {}).get('remarks'):
            print(f"    备注: {term['metadata']['remarks']}")

def main():
    """主演示函数"""
    print("🎯 词典翻译功能演示")
    print("本演示展示如何使用游戏专用词典进行智能翻译")
    print("=" * 60)
    
    try:
        # 演示各个游戏的词典功能
        demo_victoria3_translation()
        demo_stellaris_translation()
        demo_eu4_translation()
        
        print("\n🎉 演示完成！")
        print("\n💡 主要特性:")
        print("  ✅ 自动加载游戏专用词典")
        print("  ✅ 智能识别相关术语")
        print("  ✅ 生成高优先级翻译指令")
        print("  ✅ 确保术语翻译一致性")
        print("  ✅ 支持多种游戏和语言")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
