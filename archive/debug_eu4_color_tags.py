#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试EU4颜色标签检测
"""

import re

def test_color_tag_detection():
    text = "包含 §R 红色但没有 §!"
    
    print(f"测试文本: {text}")
    print(f"文本长度: {len(text)}")
    print()
    
    # 显示每个字符及其位置
    print("字符分析:")
    for i, char in enumerate(text):
        char_info = f"位置 {i:2d}: '{char}' (ASCII: {ord(char):3d})"
        if char == '§':
            char_info += " ← 这是 § 符号"
        elif char == 'R':
            char_info += " ← 这是 R 字母"
        elif char == '!':
            char_info += " ← 这是 ! 符号"
        print(char_info)
    print()
    
    # 测试起始标签检测
    start_pattern = r'§[a-zA-Z0-9]'
    start_tags = re.findall(start_pattern, text)
    print(f"起始标签模式: {start_pattern}")
    print(f"找到的起始标签: {start_tags}")
    print(f"起始标签数量: {len(start_tags)}")
    print()
    
    # 测试结束标签检测
    end_tags_count = text.count('§!')
    print(f"结束标签 '§!' 数量: {end_tags_count}")
    print()
    
    # 检查是否应该触发警告
    if len(start_tags) != end_tags_count:
        print(f"✅ 应该触发警告: {len(start_tags)} 个起始标签 vs {end_tags_count} 个结束标签")
    else:
        print(f"❌ 不应该触发警告: {len(start_tags)} 个起始标签 vs {end_tags_count} 个结束标签")
    
    # 使用re.finditer来查看具体匹配
    print("\n使用 re.finditer 查找起始标签:")
    for match in re.finditer(start_pattern, text):
        print(f"  匹配: '{match.group(0)}' 在位置 {match.start()}-{match.end()}")
    
    # 检查 §R 是否被正确识别
    print(f"\n检查 '§R' 是否被识别:")
    if '§R' in text:
        print("  '§R' 存在于文本中")
        r_index = text.find('§R')
        print(f"  '§R' 在位置 {r_index}")
        if r_index + 1 < len(text):
            next_char = text[r_index + 1]
            print(f"  '§R' 后面的字符是 '{next_char}' (ASCII: {ord(next_char)})")
            if next_char.isalnum():
                print(f"  '{next_char}' 是字母或数字")
            else:
                print(f"  '{next_char}' 不是字母或数字")
    else:
        print("  '§R' 不存在于文本中")

if __name__ == '__main__':
    test_color_tag_detection()
