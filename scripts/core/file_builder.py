# scripts/core/file_builder.py

import os
from utils import i18n

def create_fallback_file(source_path, dest_dir, original_filename):
    """翻译失败时的安全网，复制并重命名英文原文件。"""
    print(i18n.t("creating_fallback_file"))
    try:
        with open(source_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        header_found_and_replaced = False
        for i, line in enumerate(lines):
            if 'l_english:' in line:
                lines[i] = line.replace('l_english:', 'l_simp_chinese:')
                header_found_and_replaced = True
                break
        if not header_found_and_replaced:
            lines.insert(0, "l_simp_chinese:\n")

        new_filename = original_filename.replace('_l_english.yml', '_l_simp_chinese.yml') if original_filename.endswith('_l_english.yml') else original_filename
        dest_file_path = os.path.join(dest_dir, new_filename)
        
        with open(dest_file_path, 'w', encoding='utf-8-bom') as f:
            f.writelines(lines)
        print(i18n.t("fallback_file_created", filename=new_filename))
    except Exception as e:
        print(i18n.t("fallback_creation_error", error=e))

def rebuild_and_write_file(original_lines, texts_to_translate, translated_texts, key_map, dest_dir_path, original_filename):
    """
    根据翻译结果重建.yml文件内容并写入磁盘。
    """
    translation_map = dict(zip(texts_to_translate, translated_texts))
    
    new_lines = list(original_lines)
    for i, original_text in enumerate(texts_to_translate):
        translated_text = translation_map.get(original_text, original_text)
        line_info = key_map[i]
        original_line_num = line_info['line_num']
        original_key_part = line_info['key_part']
        original_value_part = line_info['original_value_part']
        
        safe_translated_text = translated_text.strip().replace('"', '\\"')
        new_value_part = original_value_part.replace(f'"{original_text}"', f'"{safe_translated_text}"')
        
        indent = original_lines[original_line_num][:original_lines[original_line_num].find(original_key_part)]
        
        new_lines[original_line_num] = f'{indent}{original_key_part}:{new_value_part}\n'

    header_found_and_replaced = False
    for i, line in enumerate(new_lines):
        if 'l_english:' in line:
            new_lines[i] = line.replace('l_english:', 'l_simp_chinese:')
            header_found_and_replaced = True
            break
    if not header_found_and_replaced:
        new_lines.insert(0, "l_simp_chinese:\n")
        
    new_filename = original_filename.replace('_l_english.yml', '_l_simp_chinese.yml') if original_filename.endswith('_l_english.yml') else original_filename
    dest_file_path = os.path.join(dest_dir_path, new_filename)
    with open(dest_file_path, 'w', encoding='utf-8-sig') as f:
        f.writelines(new_lines)
        
    print(i18n.t("writing_file_success", filename=os.path.join(os.path.relpath(dest_dir_path, 'my_translation'), new_filename)))