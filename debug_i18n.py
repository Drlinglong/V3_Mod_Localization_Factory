#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的国际化系统调试脚本
"""

import os
import json

def main():
    print("🔍 调试国际化系统...")
    
    # 检查当前目录
    print(f"当前目录: {os.getcwd()}")
    
    # 检查文件是否存在
    zh_file = 'data/lang/zh_CN.json'
    en_file = 'data/lang/en_US.json'
    
    print(f"中文语言文件存在: {os.path.exists(zh_file)}")
    print(f"英文语言文件存在: {os.path.exists(en_file)}")
    
    # 尝试加载中文语言文件
    try:
        with open(zh_file, 'r', encoding='utf-8') as f:
            zh_data = json.load(f)
        print(f"中文语言文件加载成功，包含 {len(zh_data)} 个键")
        
        # 检查特定的键
        test_keys = ['processing_metadata', 'translating_mod_name', 'metadata_success', 
                    'processing_assets', 'asset_copied', 'parsing_file', 'extracted_texts', 'writing_file_success']
        
        print("\n检查特定键:")
        for key in test_keys:
            if key in zh_data:
                print(f"  ✅ {key}: {zh_data[key][:50]}...")
            else:
                print(f"  ❌ {key}: 缺失")
                
    except Exception as e:
        print(f"加载中文语言文件时出错: {e}")
    
    # 尝试加载英文语言文件
    try:
        with open(en_file, 'r', encoding='utf-8') as f:
            en_data = json.load(f)
        print(f"\n英文语言文件加载成功，包含 {len(en_data)} 个键")
        
        # 检查特定的键
        print("\n检查特定键:")
        for key in test_keys:
            if key in en_data:
                print(f"  ✅ {key}: {en_data[key][:50]}...")
            else:
                print(f"  ❌ {key}: 缺失")
                
    except Exception as e:
        print(f"加载英文语言文件时出错: {e}")

if __name__ == '__main__':
    main()
