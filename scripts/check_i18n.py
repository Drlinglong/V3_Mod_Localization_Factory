#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查国际化系统的完整性
确保所有使用的国际化键都在语言文件中定义了
"""

import os
import re
import json
import sys

def find_i18n_keys_in_code():
    """在代码中查找所有使用的国际化键"""
    keys = set()
    
    # 搜索所有Python文件
    for root, dirs, files in os.walk('scripts'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 查找 i18n.t("key") 或 i18n.t('key') 模式
                        matches = re.findall(r'i18n\.t\(["\']([^"\']+)["\']', content)
                        keys.update(matches)
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {e}")
    
    return keys

def load_language_file(lang_code):
    """加载语言文件"""
    lang_file_path = os.path.join('data', 'lang', f'{lang_code}.json')
    try:
        with open(lang_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载语言文件 {lang_file_path} 时出错: {e}")
        return {}

def check_i18n_completeness():
    """检查国际化系统的完整性"""
    print("🔍 检查国际化系统完整性...")
    print("=" * 60)
    
    # 查找代码中使用的所有键
    used_keys = find_i18n_keys_in_code()
    print(f"📝 代码中使用的国际化键数量: {len(used_keys)}")
    
    # 检查中文语言文件
    zh_keys = load_language_file('zh_CN')
    print(f"🇨🇳 中文语言文件中的键数量: {len(zh_keys)}")
    
    # 检查英文语言文件
    en_keys = load_language_file('en_US')
    print(f"🇺🇸 英文语言文件中的键数量: {len(en_keys)}")
    
    print("\n" + "=" * 60)
    
    # 检查缺失的键
    missing_in_zh = used_keys - set(zh_keys.keys())
    missing_in_en = used_keys - set(en_keys.keys())
    
    if missing_in_zh:
        print("❌ 中文语言文件中缺失的键:")
        for key in sorted(missing_in_zh):
            print(f"   - {key}")
    
    if missing_in_en:
        print("❌ 英文语言文件中缺失的键:")
        for key in sorted(missing_in_en):
            print(f"   - {key}")
    
    # 检查未使用的键
    unused_zh = set(zh_keys.keys()) - used_keys
    unused_en = set(en_keys.keys()) - used_keys
    
    if unused_zh:
        print("\n⚠️  中文语言文件中未使用的键:")
        for key in sorted(unused_zh):
            print(f"   - {key}")
    
    if unused_en:
        print("\n⚠️  英文语言文件中未使用的键:")
        for key in sorted(unused_en):
            print(f"   - {key}")
    
    # 检查键值是否为空
    empty_zh = [key for key, value in zh_keys.items() if not value or value.strip() == ""]
    empty_en = [key for key, value in en_keys.items() if not value or value.strip() == ""]
    
    if empty_zh:
        print("\n⚠️  中文语言文件中值为空的键:")
        for key in empty_zh:
            print(f"   - {key}")
    
    if empty_en:
        print("\n⚠️  英文语言文件中值为空的键:")
        for key in empty_en:
            print(f"   - {key}")
    
    print("\n" + "=" * 60)
    
    if not missing_in_zh and not missing_in_en:
        print("✅ 所有国际化键都已正确定义！")
        return True
    else:
        print("❌ 发现缺失的国际化键，请修复后再运行程序。")
        return False

if __name__ == '__main__':
    # 确保在项目根目录下运行
    if not os.path.exists('scripts') or not os.path.exists('data'):
        print("❌ 请在项目根目录下运行此脚本")
        sys.exit(1)
    
    success = check_i18n_completeness()
    sys.exit(0 if success else 1)
