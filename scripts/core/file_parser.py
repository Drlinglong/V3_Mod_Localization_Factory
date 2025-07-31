# scripts/core/file_parser.py
import os
import re
from utils import i18n # 确保导入i18n

def extract_translatable_content(file_path):
    """从单个.yml文件中提取所有可翻译的文本。"""
    relative_path = os.path.relpath(file_path)
    print(i18n.t("parsing_file", filename=relative_path))

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        original_lines = f.readlines()

    texts_to_translate = []
    key_map = {}



    for line_num, line in enumerate(original_lines):
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('#') or stripped_line.startswith('l_english'):
            continue

        parts = stripped_line.split(':', 1)
        if len(parts) < 2:
            continue

        key_part = parts[0]
        value_part = parts[1]
        
        match = re.search(r'"(.*)"', value_part)
        if not match:
            continue
        
        value = match.group(1)

        if (value.startswith('$') and value.endswith('$')) or not value:
            continue
        
        texts_to_translate.append(value)
        key_map[len(texts_to_translate) - 1] = {
            'key_part': key_part,
            'original_value_part': value_part.strip(),
            'line_num': line_num
        }
        
    # ... (解析逻辑无变化) ...

    print(i18n.t("extracted_texts", count=len(texts_to_translate)))
    return original_lines, texts_to_translate, key_map