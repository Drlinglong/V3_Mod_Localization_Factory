#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目结构整理脚本
将测试文件和文档移动到合适的位置，保持项目根目录整洁
"""

import os
import shutil
from pathlib import Path

def organize_project():
    """整理项目结构"""
    print("=== 开始整理项目结构 ===")
    
    # 创建必要的目录
    archive_tests_dir = Path("archive/tests")
    archive_tests_dir.mkdir(parents=True, exist_ok=True)
    
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # 要移动到archive/tests的测试文件
    test_files = [
        "test_vic3_simple.py",
        "test_eu4_validator.py", 
        "test_ck3_validator.py",
        "test_stellaris_validator.py",
        "test_vic3_validator.py",
        "test_simple_eu4.py",
        "test_hoi4_validator.py",
        "test_simple_validator.py",
        "test_post_process_validator.py",
        "test_config_syntax.py",
        "test_punctuation_system.py",
        "test_punctuation_integration.py",
        "test_chinese_punctuation_fix.py",
        "test_version_display.py"
    ]
    
    # 要移动到docs的文档文件
    doc_files = [
        "REFACTORING_SUMMARY.md",
        "POST_PROCESS_VALIDATOR_SUMMARY.md"
    ]
    
    # 要删除的日志和临时文件
    delete_files = [
        "test_post_process_validation.log",
        "chinese_punctuation_fix.log"
    ]
    
    # 移动测试文件
    print("\n📁 移动测试文件到 archive/tests/")
    for test_file in test_files:
        if os.path.exists(test_file):
            try:
                shutil.move(test_file, archive_tests_dir / test_file)
                print(f"  ✅ {test_file} → archive/tests/")
            except Exception as e:
                print(f"  ❌ 移动 {test_file} 失败: {e}")
        else:
            print(f"  ⚠️  {test_file} 不存在，跳过")
    
    # 移动文档文件
    print("\n📚 移动文档文件到 docs/")
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            try:
                shutil.move(doc_file, docs_dir / doc_file)
                print(f"  ✅ {doc_file} → docs/")
            except Exception as e:
                print(f"  ❌ 移动 {doc_file} 失败: {e}")
        else:
            print(f"  ⚠️  {doc_file} 不存在，跳过")
    
    # 删除临时文件
    print("\n🗑️ 删除临时文件")
    for temp_file in delete_files:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"  ✅ 删除 {temp_file}")
            except Exception as e:
                print(f"  ❌ 删除 {temp_file} 失败: {e}")
        else:
            print(f"  ⚠️  {temp_file} 不存在，跳过")
    
    # 保留重要的测试文件
    print("\n🔒 保留重要测试文件在根目录")
    important_tests = [
        "test_validation_with_issues.py",      # 生成测试用例
        "test_post_processor_direct.py"        # 直接测试后处理器
    ]
    
    for test_file in important_tests:
        if os.path.exists(test_file):
            print(f"  ✅ 保留 {test_file}")
        else:
            print(f"  ⚠️  {test_file} 不存在")
    
    # 检查archive目录结构
    print("\n📋 检查archive目录结构")
    if archive_tests_dir.exists():
        test_count = len(list(archive_tests_dir.glob("*.py")))
        print(f"  📁 archive/tests/ 包含 {test_count} 个测试文件")
    
    # 检查docs目录结构
    if docs_dir.exists():
        doc_count = len(list(docs_dir.glob("*.md")))
        print(f"  📚 docs/ 包含 {doc_count} 个文档文件")
    
    print("\n=== 项目整理完成 ===")
    print("\n📁 目录结构:")
    print("  📂 archive/tests/     - 过时的测试文件")
    print("  📂 docs/              - 项目文档")
    print("  📂 scripts/           - 核心脚本")
    print("  📂 data/              - 数据和配置")
    print("  📂 README.md          - 项目说明")
    print("  📂 test_validation_with_issues.py     - 生成测试用例")
    print("  📂 test_post_processor_direct.py      - 直接测试后处理器")

if __name__ == "__main__":
    organize_project()




