#!/usr/bin/env python3
"""
调试韩语翻译过程中的语言代码传递
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from scripts.core.api_handler import initialize_client
from scripts.config import LANGUAGES, GAME_PROFILES

# 模拟韩语翻译的配置
print("=== 韩语翻译配置模拟 ===")

# 获取韩语配置
korean_lang = None
for key, lang in LANGUAGES.items():
    if lang["code"] == "ko":
        korean_lang = lang
        break

english_lang = None
for key, lang in LANGUAGES.items():
    if lang["code"] == "en":
        english_lang = lang
        break

print(f"源语言: {english_lang['name']} (code: {english_lang['code']})")
print(f"目标语言: {korean_lang['name']} (code: {korean_lang['code']})")

# 获取Victoria 3游戏配置
vic3_profile = GAME_PROFILES["1"]  # Victoria 3
print(f"\n游戏配置: {vic3_profile['name']}")

# 测试prompt模板
print(f"\n=== Prompt模板测试 ===")
test_texts = ["Hello", "World", "Test"]
numbered_list = "\n".join(f'{j + 1}. "{txt}"' for j, txt in enumerate(test_texts))

base_prompt = vic3_profile["prompt_template"].format(
    source_lang_name=english_lang["name"],
    target_lang_name=korean_lang["name"],
)

print(f"基础prompt:")
print(f"  {base_prompt}")
print(f"  {numbered_list}")

# 测试单个翻译prompt
single_prompt = vic3_profile["single_prompt_template"].format(
    mod_name="Test Mod",
    task_description="mod name",
    source_lang_name=english_lang["name"],
    target_lang_name=korean_lang["name"],
)

print(f"\n单个翻译prompt:")
print(f"  {single_prompt}")

# 检查语言代码在词典中的使用
print(f"\n=== 语言代码检查 ===")
print(f"源语言代码: '{english_lang['code']}'")
print(f"目标语言代码: '{korean_lang['code']}'")

# 模拟词典术语提取
print(f"\n=== 模拟词典术语提取 ===")
print(f"使用源语言代码: '{english_lang['code']}'")
print(f"使用目标语言代码: '{korean_lang['code']}'")
