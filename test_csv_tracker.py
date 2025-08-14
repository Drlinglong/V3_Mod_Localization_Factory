#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CSV格式校对进度追踪功能
"""

import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.core.proofreading_tracker import create_proofreading_tracker


def test_csv_tracker():
    """测试CSV格式校对进度追踪器"""
    
    print("=== 测试CSV格式校对进度追踪器 ===\n")
    
    # 测试数据
    test_files = [
        {
            'source_path': '/source/localisation/events_l_english.yml',
            'dest_path': '/dest/localisation/simp_chinese/events_l_simp_chinese.yml',
            'translated_lines': 648,
            'filename': 'events_l_simp_chinese.yml',
            'is_custom_loc': False
        },
        {
            'source_path': '/source/localisation/decisions_l_english.yml',
            'dest_path': '/dest/localisation/simp_chinese/decisions_l_simp_chinese.yml',
            'translated_lines': 85,
            'filename': 'decisions_l_simp_chinese.yml',
            'is_custom_loc': False
        },
        {
            'source_path': '/source/customizable_localization/names.txt',
            'dest_path': '/dest/customizable_localization/simp_chinese/names.txt',
            'translated_lines': 42,
            'filename': 'names.txt',
            'is_custom_loc': True
        }
    ]
    
    # 测试不同语言
    test_languages = [
        ("zh-CN", "简体中文"),
        ("en", "English"),
        ("fr", "Français"),
        ("de", "Deutsch"),
        ("es", "Español")
    ]
    
    for lang_code, lang_name in test_languages:
        print(f"--- 测试 {lang_name} ({lang_code}) ---")
        
        # 创建追踪器
        tracker = create_proofreading_tracker("TestMod", "汉化-TestMod", lang_code)
        
        # 添加文件信息
        for file_info in test_files:
            tracker.add_file_info(file_info)
        
        # 生成CSV内容
        csv_content = tracker.generate_csv_content()
        
        # 显示CSV内容
        print(f"CSV内容预览:")
        print(csv_content)
        
        # 测试保存功能
        print(f"\n=== 测试保存功能 ===")
        # 临时修改输出目录为测试目录
        with tempfile.TemporaryDirectory() as temp_dir:
            original_output_root = tracker.output_root
            tracker.output_root = temp_dir
            
            if tracker.save_proofreading_progress():
                print("✅ CSV校对进度表格保存成功")
                
                # 检查生成的文件
                csv_filename = tracker.lang_template.get('csv_filename', 'proofreading_progress.csv')
                output_file = os.path.join(temp_dir, csv_filename)
                
                if os.path.exists(output_file):
                    print(f"✅ 文件已生成: {output_file}")
                    
                    # 读取并显示文件内容
                    with open(output_file, 'r', encoding='utf-8-sig') as f:
                        saved_content = f.read()
                        print(f"✅ 文件内容长度: {len(saved_content)} 字符")
                        print(f"✅ 文件内容预览:")
                        print(saved_content)
                else:
                    print("❌ 文件未生成")
            else:
                print("❌ CSV校对进度表格保存失败")
            
            # 恢复原始输出目录
            tracker.output_root = original_output_root
        
        print()
    
    print("=== CSV格式测试完成 ===")


def test_csv_format():
    """测试CSV格式的正确性"""
    
    print("\n=== 测试CSV格式正确性 ===")
    
    tracker = create_proofreading_tracker("TestMod", "Test", "zh-CN")
    
    # 添加测试文件
    tracker.add_file_info({
        'source_path': '/test/path with, comma.yml',
        'dest_path': '/dest/test_simp_chinese.yml',
        'translated_lines': 100,
        'filename': 'test.yml',
        'is_custom_loc': False
    })
    
    csv_content = tracker.generate_csv_content()
    
    # 检查CSV格式
    lines = csv_content.strip().split('\n')
    if len(lines) >= 2:  # 至少应该有标题行和一个数据行
        print("✅ CSV格式正确：包含标题行和数据行")
        
        # 检查列数
        title_columns = lines[0].split(',')
        data_columns = lines[1].split(',')
        
        if len(title_columns) == 5 and len(data_columns) == 5:
            print("✅ CSV列数正确：5列")
        else:
            print(f"❌ CSV列数错误：标题行{len(title_columns)}列，数据行{len(data_columns)}列")
            
        # 检查标题
        expected_titles = ["状态", "源文件", "汉化文件", "已翻译行数", "校对进度/备注"]
        if all(title in lines[0] for title in expected_titles):
            print("✅ CSV标题正确")
        else:
            print("❌ CSV标题不正确")
            
    else:
        print("❌ CSV格式错误：行数不足")
    
    print("CSV格式测试完成")


if __name__ == "__main__":
    try:
        test_csv_tracker()
        test_csv_format()
        print("\n🎉 所有CSV测试通过！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

