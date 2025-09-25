#!/usr/bin/env python3
"""
调试韩语语言代码映射问题
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from scripts.config import LANGUAGES, LANGUAGE_PUNCTUATION_CONFIG

# 检查韩语配置
print("=== 韩语语言配置检查 ===")

# 找到韩语配置
korean_config = None
for key, lang in LANGUAGES.items():
    if lang["code"] == "ko":
        korean_config = lang
        print(f"找到韩语配置 (键: {key}):")
        print(f"  code: {lang['code']}")
        print(f"  name: {lang['name']}")
        print(f"  key: {lang['key']}")
        print(f"  folder_prefix: {lang['folder_prefix']}")
        break

if not korean_config:
    print("❌ 未找到韩语配置!")
    exit(1)

# 检查标点配置
print(f"\n=== 韩语标点配置检查 ===")
if "ko" in LANGUAGE_PUNCTUATION_CONFIG:
    korean_punct = LANGUAGE_PUNCTUATION_CONFIG["ko"]
    print(f"找到韩语标点配置:")
    print(f"  name: {korean_punct['name']}")
    print(f"  标点符号数量: {len(korean_punct.get('punctuation', {}))}")
else:
    print("❌ 未找到韩语标点配置!")

# 检查中文配置对比
print(f"\n=== 中文配置对比 ===")
chinese_config = None
for key, lang in LANGUAGES.items():
    if lang["code"] == "zh-CN":
        chinese_config = lang
        print(f"找到中文配置 (键: {key}):")
        print(f"  code: {lang['code']}")
        print(f"  name: {lang['name']}")
        print(f"  key: {lang['key']}")
        print(f"  folder_prefix: {lang['folder_prefix']}")
        break

print(f"\n=== 潜在的映射冲突检查 ===")
print(f"韩语 code: '{korean_config['code']}' vs 中文 code: '{chinese_config['code']}'")
print(f"韩语 name: '{korean_config['name']}' vs 中文 name: '{chinese_config['name']}'")

# 测试prompt模板
print(f"\n=== Prompt模板测试 ===")
test_prompt_template = "Translate from {source_lang_name} to {target_lang_name}"
test_prompt = test_prompt_template.format(
    source_lang_name="English",
    target_lang_name=korean_config["name"]
)
print(f"示例prompt: {test_prompt}")
