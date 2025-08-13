#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复模块导入问题
统一使用绝对导入方式
"""

import os
import re

def fix_imports_in_file(file_path):
    """修复单个文件的导入问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复 from utils import i18n
        content = re.sub(
            r'from utils import i18n',
            'from scripts.utils import i18n',
            content
        )
        
        # 修复 from config import
        content = re.sub(
            r'from config import',
            'from scripts.config import',
            content
        )
        
        # 修复 from core. import
        content = re.sub(
            r'from core\.',
            'from scripts.core.',
            content
        )
        
        # 修复 from utils. import (除了scripts.utils)
        content = re.sub(
            r'from utils\.(?!text_clean)',
            'from scripts.utils.',
            content
        )
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 修复了 {file_path}")
            return True
        else:
            print(f"⏭️  无需修复 {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False

def main():
    """主函数"""
    print("🔧 开始批量修复模块导入问题...")
    
    # 要修复的目录
    scripts_dir = 'scripts'
    
    fixed_count = 0
    total_count = 0
    
    print(f"正在扫描目录: {scripts_dir}")
    
    # 遍历所有Python文件
    for root, dirs, files in os.walk(scripts_dir):
        print(f"  扫描目录: {root}")
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                total_count += 1
                print(f"    发现文件: {file}")
                
                if fix_imports_in_file(file_path):
                    fixed_count += 1
    
    print(f"\n📊 修复完成！")
    print(f"   总文件数: {total_count}")
    print(f"   修复文件数: {fixed_count}")
    print(f"   无需修复: {total_count - fixed_count}")

if __name__ == '__main__':
    main()
