#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
群星验证器测试
"""

import os
import sys
import logging

os.environ['SKIP_LANGUAGE_SELECTION'] = '1'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from utils.post_process_validator import StellarisValidator, ValidationLevel


def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


def test_stellaris_validator():
    print("开始测试群星验证器...\n")
    v = StellarisValidator()

    cases = [
        {
            "name": "正常 - 无错误",
            "text": "正常文本 [Root.GetName] 和 $variable$ 以及 £energy£",
            "errors": 0
        },
        {
            "name": "方括号含中文",
            "text": "[Root.中文函数]",
            "errors": 1
        },
        {
            "name": "变量含中文",
            "text": "这是 $中文变量$",
            "errors": 1
        },
        {
            "name": "图标含中文",
            "text": "这是 £中文图标£",
            "errors": 1
        },
        {
            "name": "颜色标签不成对",
            "text": "包含 §R 红色但没有 §!",
            "errors": 0,
            "warnings": 1
        },
        {
            "name": "颜色标签成对",
            "text": "§R红色文本§! 正常显示",
            "errors": 0,
            "warnings": 0
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
                icon = "❌" if r.level == ValidationLevel.ERROR else ("⚠️" if r.level == ValidationLevel.WARNING else "ℹ️")
                print(f"  - {icon} {r.level.value}: {r.message}")
                if r.details:
                    print(f"    详情: {r.details}")
        err = len([r for r in results if r.level == ValidationLevel.ERROR])
        warn = len([r for r in results if r.level == ValidationLevel.WARNING])
        info = len([r for r in results if r.level == ValidationLevel.INFO])
        
        if err == c.get('errors', 0):
            print(f"  ✅ 错误数符合预期: {err}")
        else:
            print(f"  ❌ 错误数不符: 期望 {c.get('errors',0)}, 实际 {err}")
        if 'warnings' in c:
            if warn == c['warnings']:
                print(f"  ✅ 警告数符合预期: {warn}")
            else:
                print(f"  ❌ 警告数不符: 期望 {c['warnings']}, 实际 {warn}")
        if 'infos' in c:
            if info == c['infos']:
                print(f"  ✅ 信息数符合预期: {info}")
            else:
                print(f"  ❌ 信息数不符: 期望 {c['infos']}, 实际 {info}")
        print()


if __name__ == '__main__':
    setup_logging()
    test_stellaris_validator()
    print("🎉 群星验证器测试完成！")
