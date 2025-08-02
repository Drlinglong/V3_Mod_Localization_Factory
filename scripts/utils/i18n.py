# scripts/utils/i18n.py
import json
import os
import sys

_strings = {}

def load_language(cli_language=None):
    """向用户提问，加载选择的语言文件。"""
    global _strings
    if cli_language:
        lang_code = cli_language
    else:
        lang_choice = input("Please select a language (1: English, 2: 中文): ").strip()
        lang_code = 'en_US' if lang_choice == '1' else 'zh_CN'

    lang_file_path = os.path.join('data', 'lang', f'{lang_code}.json')

    try:
        with open(lang_file_path, 'r', encoding='utf-8') as f:
            _strings = json.load(f)
        print(t("language_set", lang_code=lang_code)) # 使用t()函数来输出
    except Exception as e:
        # 在i18n本身加载失败时，只能用硬编码的英文
        print(f"Error loading language file: {e}")
        _strings = {}

def t(key, **kwargs):
    """获取翻译后的字符串。"""
    # 提供一个备用值，防止因字典key不存在而崩溃
    return _strings.get(key, f"<{key}>").format(**kwargs)