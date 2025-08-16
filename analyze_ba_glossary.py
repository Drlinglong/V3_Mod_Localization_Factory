#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析修复后的BA词典
"""

import json
from collections import defaultdict

def analyze_glossary(file_path):
    """分析词典文件"""
    
    print("🔍 分析BA词典...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ 文件加载成功")
        
        # 基本信息
        metadata = data.get('metadata', {})
        print(f"\n📋 基本信息:")
        print(f"   - 名称: {metadata.get('name', 'N/A')}")
        print(f"   - 版本: {metadata.get('version', 'N/A')}")
        print(f"   - 最后更新: {metadata.get('last_updated', 'N/A')}")
        print(f"   - 游戏ID: {metadata.get('game_id', 'N/A')}")
        
        # 词条统计
        entries = data.get('entries', [])
        total_entries = len(entries)
        print(f"\n📊 词条统计:")
        print(f"   - 总词条数: {total_entries}")
        
        # 按类别统计
        categories = defaultdict(int)
        for entry in entries:
            category = entry.get('metadata', {}).get('category', 'unknown')
            categories[category] += 1
        
        print(f"\n📂 按类别统计:")
        for category, count in sorted(categories.items()):
            percentage = (count / total_entries) * 100
            print(f"   - {category}: {count} ({percentage:.1f}%)")
        
        # 按词性统计
        parts_of_speech = defaultdict(int)
        for entry in entries:
            pos = entry.get('metadata', {}).get('part_of_speech', 'unknown')
            parts_of_speech[pos] += 1
        
        print(f"\n🔤 按词性统计:")
        for pos, count in sorted(parts_of_speech.items()):
            percentage = (count / total_entries) * 100
            print(f"   - {pos}: {count} ({percentage:.1f}%)")
        
        # 缩写和变体统计
        has_abbreviations = 0
        has_variants = 0
        for entry in entries:
            if entry.get('abbreviations'):
                has_abbreviations += 1
            if entry.get('variants'):
                has_variants += 1
        
        print(f"\n🔗 特殊字段统计:")
        print(f"   - 有缩写的词条: {has_abbreviations} ({has_abbreviations/total_entries*100:.1f}%)")
        print(f"   - 有变体的词条: {has_variants} ({has_variants/total_entries*100:.1f}%)")
        
        # 语言覆盖统计
        languages = defaultdict(int)
        for entry in entries:
            translations = entry.get('translations', {})
            for lang in translations.keys():
                languages[lang] += 1
        
        print(f"\n🌍 语言覆盖统计:")
        for lang, count in sorted(languages.items()):
            percentage = (count / total_entries) * 100
            print(f"   - {lang}: {count} ({percentage:.1f}%)")
        
        # 示例词条
        print(f"\n📝 示例词条:")
        for i, entry in enumerate(entries[:3]):
            print(f"   {i+1}. {entry.get('id', 'N/A')}")
            print(f"      - 英文: {entry.get('translations', {}).get('en', 'N/A')}")
            print(f"      - 中文: {entry.get('translations', {}).get('zh-CN', 'N/A')}")
            print(f"      - 类别: {entry.get('metadata', {}).get('category', 'N/A')}")
            print()
        
        return total_entries
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        return 0

def main():
    """主函数"""
    file_path = "data/glossary/stellaris/blue_archive_fixed.json"
    
    try:
        total_entries = analyze_glossary(file_path)
        print(f"\n🎉 分析完成！")
        print(f"📈 词典包含 {total_entries} 个有效词条")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")

if __name__ == "__main__":
    main()

