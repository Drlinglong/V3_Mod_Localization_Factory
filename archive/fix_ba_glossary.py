#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复BA词典语法错误并统计词条数量
"""

import json
import re
from collections import defaultdict

def fix_ba_glossary(input_file, output_file):
    """修复BA词典的语法错误"""
    
    print("🔧 开始修复BA词典...")
    
    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📖 原始文件大小: {len(content)} 字符")
    
    # 提取所有有效的词条
    entries = []
    seen_ids = set()
    
    # 使用更简单的方法：查找所有完整的JSON对象
    # 先尝试修复整个文件的结构
    print("🔍 分析文件结构...")
    
    # 查找所有可能的词条开始位置
    entry_starts = []
    for i, line in enumerate(content.split('\n')):
        if '"id":' in line and '"ba_' in line:
            entry_starts.append(i)
    
    print(f"🔍 找到 {len(entry_starts)} 个可能的词条开始位置")
    
    # 尝试手动重建JSON结构
    lines = content.split('\n')
    
    # 查找entries数组的开始和结束
    entries_start = -1
    entries_end = -1
    
    for i, line in enumerate(lines):
        if '"entries":' in line:
            entries_start = i
            break
    
    if entries_start == -1:
        print("❌ 找不到entries数组")
        return 0
    
    print(f"🔍 entries数组开始于第 {entries_start} 行")
    
    # 从entries开始位置开始，手动提取词条
    current_entry = []
    in_entry = False
    brace_count = 0
    
    for i in range(entries_start + 1, len(lines)):
        line = lines[i].strip()
        
        if line.startswith('{'):
            if not in_entry:
                in_entry = True
                brace_count = 1
                current_entry = [line]
            else:
                brace_count += 1
                current_entry.append(line)
        elif in_entry:
            current_entry.append(line)
            
            if line.startswith('}'):
                brace_count -= 1
                
                if brace_count == 0:
                    # 词条结束
                    in_entry = False
                    
                    try:
                        entry_text = '\n'.join(current_entry)
                        entry = json.loads(entry_text)
                        
                        entry_id = entry.get('id')
                        if entry_id and entry_id not in seen_ids:
                            if all(key in entry for key in ['id', 'translations']):
                                entries.append(entry)
                                seen_ids.add(entry_id)
                                print(f"✅ 提取词条: {entry_id}")
                            else:
                                print(f"⚠️  跳过不完整词条: {entry_id}")
                        else:
                            print(f"⚠️  跳过重复词条: {entry_id}")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析失败: {current_entry[0] if current_entry else 'unknown'} - {e}")
                    
                    current_entry = []
        
        # 检查是否到达entries数组的结束
        if line == ']' and not in_entry:
            entries_end = i
            break
    
    print(f"\n📊 统计结果:")
    print(f"   - 有效词条数量: {len(entries)}")
    print(f"   - 唯一ID数量: {len(seen_ids)}")
    
    # 按类别统计
    categories = defaultdict(int)
    for entry in entries:
        category = entry.get('metadata', {}).get('category', 'unknown')
        categories[category] += 1
    
    print(f"\n📂 按类别统计:")
    for category, count in sorted(categories.items()):
        print(f"   - {category}: {count}")
    
    # 创建修复后的词典结构
    fixed_glossary = {
        "metadata": {
            "name": "Blue Archive Stellaris Mod - Fixed Dictionary",
            "description": "A comprehensive glossary of all extracted terms (characters, schools, clubs, concepts, etc.) from the mod's localization files. Fixed and cleaned version.",
            "version": "1.2-fixed",
            "last_updated": "2025-01-27",
            "sources": [
                "BA_Club_l_simp_chinese.yml",
                "BA_common_l_simp_chinese.yml", 
                "BA_concepts_l_simp_chinese.yml",
                "BA_event_crisis_l_simp_chinese.yml",
                "BA_event_origins_l_simp_chinese.yml",
                "BA_event_Shittem_l_simp_chinese.yml",
                "BA_event_tr&ape_l_simp_chinese.yml",
                "BA_leader_l_simp_chinese.yml",
                "BA_modifiers_l_simp_chinese.yml",
                "BA_popmod_l_simp_chinese.yml",
                "BA_School_Idea_l_simp_chinese.yml",
                "BA_speciel_story_l_simp_chinese.yml",
                "BA_component_l_simp_chinese.yml",
                "BA_event_Emergencies_l_simp_chinese.yml",
                "BA_Project_l_simp_chinese.yml",
                "BA_Species&Goverments&Civics_l_simp_chinese.yml",
                "BA_Anomaly&Arc_site_l_simp_chinese.yml"
            ],
            "game_id": "stellaris",
            "type": "auxiliary"
        },
        "entries": entries
    }
    
    # 保存修复后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_glossary, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 修复后的词典已保存到: {output_file}")
    
    # 验证修复后的文件
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            json.load(f)
        print("✅ 修复后的文件JSON格式正确")
    except json.JSONDecodeError as e:
        print(f"❌ 修复后的文件仍有JSON错误: {e}")
    
    return len(entries)

def main():
    """主函数"""
    input_file = "data/glossary/stellaris/blue_archive.json"
    output_file = "data/glossary/stellaris/blue_archive_fixed.json"
    
    try:
        total_entries = fix_ba_glossary(input_file, output_file)
        print(f"\n🎉 修复完成！")
        print(f"📈 总共提取了 {total_entries} 个有效词条")
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
