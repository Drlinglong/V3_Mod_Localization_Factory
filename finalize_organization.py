#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终项目整理脚本
将重要的测试文件移回根目录，完成项目结构整理
"""

import os
import shutil

def finalize_organization():
    """完成项目整理"""
    print("=== 完成项目整理 ===")
    
    # 将重要的测试文件移回根目录
    important_tests = [
        "test_validation_with_issues.py",
        "test_post_processor_direct.py"
    ]
    
    print("\n📁 将重要测试文件移回根目录")
    for test_file in important_tests:
        source_path = f"archive/tests/{test_file}"
        if os.path.exists(source_path):
            try:
                shutil.move(source_path, test_file)
                print(f"  ✅ {test_file} → 根目录")
            except Exception as e:
                print(f"  ❌ 移动 {test_file} 失败: {e}")
        else:
            print(f"  ⚠️  {test_file} 不存在，跳过")
    
    # 删除整理脚本
    cleanup_files = [
        "organize_project.py",
        "finalize_organization.py"
    ]
    
    print("\n🗑️ 清理整理脚本")
    for script_file in cleanup_files:
        if os.path.exists(script_file):
            try:
                os.remove(script_file)
                print(f"  ✅ 删除 {script_file}")
            except Exception as e:
                print(f"  ❌ 删除 {script_file} 失败: {e}")
        else:
            print(f"  ⚠️  {script_file} 不存在，跳过")
    
    print("\n=== 项目整理完成 ===")
    print("\n📁 最终目录结构:")
    print("  📂 archive/tests/     - 过时的测试文件")
    print("  📂 docs/              - 项目文档")
    print("  📂 scripts/           - 核心脚本")
    print("  📂 data/              - 数据和配置")
    print("  📂 test_validation_issues/ - 测试用例目录")
    print("  📂 README.md          - 项目说明")
    print("  📂 test_validation_with_issues.py     - 生成测试用例")
    print("  📂 test_post_processor_direct.py      - 直接测试后处理器")

if __name__ == "__main__":
    finalize_organization()

