#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级修复BA词典语法错误并统计词条数量
"""

import json
import re
from collections import defaultdict

def extract_valid_entries(content):
    """提取所有有效的词条"""
    entries = []
    seen_ids = set()
    
    # 使用正则表达式查找所有完整的词条
    # 匹配从 { 开始到 } 结束的完整JSON对象
    pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.finditer(pattern, content)
    
    for match in matches:
        entry_text = match.group(0)
        
        # 检查是否包含必要的字段
        if '"id":' in entry_text and '"translations":' in entry_text:
            try:
                entry = json.loads(entry_text)
                
                entry_id = entry.get('id')
                if entry_id and entry_id not in seen_ids:
                    if all(key in entry for key in ['id', 'translations']):
                        entries.append(entry)
                        seen_ids.add(entry_id)
                        print(f"✅ 提取词条: {entry_id}")
                    else:
                        print(f"⚠️  跳过不完整词条: {entry_id}")
                        
            except json.JSONDecodeError:
                # 尝试修复常见的JSON问题
                fixed_text = fix_json_syntax(entry_text)
                try:
                    entry = json.loads(fixed_text)
                    
                    entry_id = entry.get('id')
                    if entry_id and entry_id not in seen_ids:
                        if all(key in entry for key in ['id', 'translations']):
                            entries.append(entry)
                            seen_ids.add(entry_id)
                            print(f"✅ 修复并提取词条: {entry_id}")
                        else:
                            print(f"⚠️  跳过不完整词条: {entry_id}")
                            
                except json.JSONDecodeError as e:
                    print(f"❌ 无法修复词条: {entry_text[:50]}... - {e}")
                    continue
    
    return entries

def fix_json_syntax(text):
    """修复常见的JSON语法问题"""
    # 移除多余的逗号
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    
    # 修复缺少引号的属性名
    text = re.sub(r'(\s+)(\w+):', r'\1"\2":', text)
    
    # 修复缺少引号的值
    text = re.sub(r':\s*([^",\{\}\[\]]+?)(?=\s*[,}\s])', r': "\1"', text)
    
    return text

def fix_ba_glossary(input_file, output_file):
    """修复BA词典的语法错误"""
    
    print("🔧 开始高级修复BA词典...")
    
    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📖 原始文件大小: {len(content)} 字符")
    
    # 尝试直接解析整个文件
    try:
        data = json.loads(content)
        print("✅ 文件可以直接解析，结构基本正确")
        
        # 提取所有词条
        entries = []
        seen_ids = set()
        
        if 'entries' in data:
            for entry in data['entries']:
                entry_id = entry.get('id')
                if entry_id and entry_id not in seen_ids:
                    if all(key in entry for key in ['id', 'translations']):
                        entries.append(entry)
                        seen_ids.add(entry_id)
                        print(f"✅ 提取词条: {entry_id}")
                    else:
                        print(f"⚠️  跳过不完整词条: {entry_id}")
        
        print(f"📊 直接解析结果: {len(entries)} 个词条")
        
    except json.JSONDecodeError as e:
        print(f"❌ 文件无法直接解析: {e}")
        print("🔧 尝试高级修复...")
        
        # 使用高级修复方法
        entries = extract_valid_entries(content)
    
    print(f"\n📊 最终统计结果:")
    print(f"   - 有效词条数量: {len(entries)}")
    print(f"   - 唯一ID数量: {len(set(entry.get('id') for entry in entries))}")
    
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

