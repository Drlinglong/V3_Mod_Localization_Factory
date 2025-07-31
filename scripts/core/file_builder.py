# scripts/core/file_builder.py

import os
from utils import i18n
def create_fallback_file(source_path, dest_dir, original_filename, source_lang, target_lang):
    """安全网现在支持多语言的文件头和文件名转换。"""
    print(i18n.t("creating_fallback_file"))
    try:
        with open(source_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        # 【核心修改】动态替换文件头
        header_found_and_replaced = False
        for i, line in enumerate(lines):
            if source_lang['key'] in line:
                lines[i] = line.replace(source_lang['key'], target_lang['key'])
                header_found_and_replaced = True
                break
        if not header_found_and_replaced:
            lines.insert(0, f"{target_lang['key']}:\n")

        # 【核心修改】动态替换文件名
        source_suffix = f"_l_{source_lang['name'].lower()}.yml"
        target_suffix = f"_l_{target_lang['name'].lower()}.yml"
        # 这是一个更通用的替换方法，处理Victoria3和Stellaris等不同命名
        if f"_l_{source_lang['key'][2:]}" in original_filename:
             new_filename = original_filename.replace(f"_l_{source_lang['key'][2:]}", f"_l_{target_lang['key'][2:]}")
        else:
             new_filename = original_filename # 如果找不到，则保持原样

        dest_file_path = os.path.join(dest_dir, new_filename)
        
        with open(dest_file_path, 'w', encoding='utf-8-bom') as f:
            f.writelines(lines)
        print(i18n.t("fallback_file_created", filename=new_filename))
    except Exception as e:
        print(i18n.t("fallback_creation_error", error=e))

def rebuild_and_write_file(original_lines, texts_to_translate, translated_texts, key_map, dest_dir_path, original_filename, source_lang, target_lang):
    """
    【V2.8 完整版】根据翻译结果重建.yml文件内容并写入磁盘。
    """
    # 【缺失的逻辑 1】创建原文到译文的映射
    translation_map = dict(zip(texts_to_translate, translated_texts))
    
    # 【缺失的逻辑 2】创建一个原始文件内容的副本，我们将在副本上进行修改
    new_lines = list(original_lines)

    # 【缺失的逻辑 3】遍历所有翻译结果，替换副本中对应行的内容
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

    # 动态替换文件头
    header_found_and_replaced = False
    for i, line in enumerate(new_lines):
        if source_lang['key'] in line:
            new_lines[i] = line.replace(source_lang['key'], target_lang['key'])
            header_found_and_replaced = True
            break
    if not header_found_and_replaced:
        new_lines.insert(0, f"{target_lang['key']}:\n")
        
    # 动态替换文件名
    source_suffix = f"_l_{source_lang['key'][2:]}" # e.g., _l_english
    target_suffix = f"_l_{target_lang['key'][2:]}" # e.g., _l_simp_chinese
    
    if source_suffix in original_filename:
        new_filename = original_filename.replace(source_suffix, target_suffix)
    else:
        new_filename = original_filename
        
    dest_file_path = os.path.join(dest_dir_path, new_filename)
    with open(dest_file_path, 'w', encoding='utf-8-sig') as f: # 确保使用 utf-8-sig
        f.writelines(new_lines)
        
    print(i18n.t("writing_file_success", filename=os.path.join(os.path.relpath(dest_dir_path, 'my_translation'), new_filename)))