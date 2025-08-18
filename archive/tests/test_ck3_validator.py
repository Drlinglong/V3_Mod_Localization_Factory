#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CK3 验证器测试文件
"""

import os
import sys
import logging
import re

# 跳过语言选择
os.environ['SKIP_LANGUAGE_SELECTION'] = '1'

# 添加scripts目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from utils.post_process_validator import CK3Validator, ValidationLevel

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


def test_ck3_validator():
    print("开始测试CK3验证器...\n")
    v = CK3Validator()

    cases = [
        {
            "name": "正常 - 简单scope",
            "text": "包含[This.GetName]和@icon_name! 以及 $VARIABLE$",
            "errors": 0
        },
        {
            "name": "方括号指令含中文",
            "text": "包含[This.中文函数]",
            "errors": 1
        },
        {
            "name": "Concept key 含中文",
            "text": "[Concept('中文key', '显示文本')]",
            "errors": 1
        },
        {
            "name": "Trait/Title key 含中文",
            "text": "[GetTrait('中文_trait')] 与 [GetTitleByKey('中文_title')]",
            "errors": 2
        },
        {
            "name": "美元变量含中文",
            "text": "这是$key$和$中文变量$",
            "errors": 1
        },
        {
            "name": "图标key含中文",
            "text": "这里有@中文图标!",
            "errors": 1
        },
        {
            "name": "#key 后缺空格",
            "text": "这里有#bold粗体#!",
            "errors": 0,
            "warnings": 1
        },
        {
            "name": "#...#! 不成对",
            "text": "开始#bold 加粗，没有结束符",
            "errors": 0,
            "warnings": 1
        },
    ]

    for i, c in enumerate(cases, 1):
        print(f"=== 用例 {i}: {c['name']} ===")
        print(f"文本: {c['text']}")
        results = v.validate_text(c['text'], i)
        if not results:
            print("  - 无问题")
        else:
            for r in results:
                icon = "❌" if r.level == ValidationLevel.ERROR else "⚠️"
                print(f"  - {icon} {r.level.value}: {r.message}")
                if r.details:
                    print(f"    详情: {r.details}")
        err = len([r for r in results if r.level == ValidationLevel.ERROR])
        warn = len([r for r in results if r.level == ValidationLevel.WARNING])
        if err == c.get('errors', 0):
            print(f"  ✅ 错误数符合预期: {err}")
        else:
            print(f"  ❌ 错误数不符: 期望 {c.get('errors',0)}, 实际 {err}")
        if 'warnings' in c:
            if warn == c['warnings']:
                print(f"  ✅ 警告数符合预期: {warn}")
            else:
                print(f"  ❌ 警告数不符: 期望 {c['warnings']}, 实际 {warn}")
        print()

if __name__ == '__main__':
    setup_logging()
    test_ck3_validator()
    print("🎉 CK3 验证器测试完成！")
