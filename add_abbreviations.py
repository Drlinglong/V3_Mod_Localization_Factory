#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为BA词典添加多语言缩写
"""

import json
import re

def add_multi_language_abbreviations(glossary_file):
    """为词典添加多语言缩写"""
    
    print("🔧 开始添加多语言缩写...")
    
    # 读取词典文件
    with open(glossary_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entries = data.get('entries', [])
    updated_count = 0
    
    for entry in entries:
        abbreviations = entry.get('abbreviations', {})
        
        # 只处理有中文缩写但没有其他语言缩写的词条
        if 'zh-CN' in abbreviations and len(abbreviations) == 1:
            zh_abbr = abbreviations['zh-CN']
            translations = entry.get('translations', {})
            
            # 基于全名和中文缩写推理其他语言缩写
            new_abbreviations = {'zh-CN': zh_abbr}
            
            # 英文缩写
            if 'en' in translations:
                en_full = translations['en']
                en_abbr = generate_english_abbreviation(en_full, zh_abbr)
                if en_abbr:
                    new_abbreviations['en'] = en_abbr
            
            # 日语缩写
            if 'ja' in translations:
                ja_full = translations['ja']
                ja_abbr = generate_japanese_abbreviation(ja_full, zh_abbr)
                if ja_abbr:
                    new_abbreviations['ja'] = ja_abbr
            
            # 韩语缩写
            if 'ko' in translations:
                ko_full = translations['ko']
                ko_abbr = generate_korean_abbreviation(ko_full, zh_abbr)
                if ko_abbr:
                    new_abbreviations['ko'] = ko_abbr
            
            # 更新词条
            if len(new_abbreviations) > 1:
                entry['abbreviations'] = new_abbreviations
                updated_count += 1
                print(f"✅ 更新 {entry.get('id', 'unknown')}: {new_abbreviations}")
    
    # 保存更新后的文件
    with open(glossary_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 完成！更新了 {updated_count} 个词条的缩写")
    return updated_count

def generate_english_abbreviation(full_name, zh_abbr):
    """生成英文缩写"""
    # 基于中文缩写的长度和英文全名来推理
    if len(zh_abbr) == 2:  # 中文缩写通常是2个字符
        # 提取英文名的关键部分
        words = full_name.split()
        if len(words) >= 2:
            # 取第一个词的首字母 + 第二个词
            if len(words[1]) <= 4:  # 第二个词不太长
                return words[1]
            else:
                return words[1][:4]  # 截取前4个字母
        elif len(words) == 1:
            return words[0][:4]  # 单个词取前4个字母
    elif len(zh_abbr) == 3:
        # 中文缩写是3个字符，英文可能取前几个字母
        return full_name[:5]
    
    return None

def generate_japanese_abbreviation(full_name, zh_abbr):
    """生成日语缩写"""
    # 日语缩写通常保持假名形式
    if len(zh_abbr) == 2:
        # 提取日语名的关键部分
        # 通常取姓氏或名字的关键部分
        if '学園' in full_name or '学院' in full_name:
            # 学校名称，去掉"学園"/"学院"
            return full_name.replace('学園', '').replace('学院', '')
        elif len(full_name) <= 6:  # 日语名不太长
            return full_name
        else:
            # 取前几个假名
            return full_name[:4]
    elif len(zh_abbr) == 3:
        return full_name[:5]
    
    return None

def generate_korean_abbreviation(full_name, zh_abbr):
    """生成韩语缩写"""
    # 韩语缩写通常保持韩文形式
    if len(zh_abbr) == 2:
        # 提取韩语名的关键部分
        if '학원' in full_name:
            # 学校名称，去掉"학원"
            return full_name.replace('학원', '')
        elif len(full_name) <= 6:  # 韩语名不太长
            return full_name
        else:
            # 取前几个韩文字符
            return full_name[:4]
    elif len(zh_abbr) == 3:
        return full_name[:5]
    
    return None

def main():
    """主函数"""
    glossary_file = "data/glossary/stellaris/blue_archive_fixed.json"
    
    try:
        updated_count = add_multi_language_abbreviations(glossary_file)
        print(f"\n🎉 缩写补充完成！")
        print(f"📈 总共更新了 {updated_count} 个词条")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
