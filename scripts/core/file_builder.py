# scripts/core/file_builder.py
import os
import re
import logging
from scripts.utils import i18n
from scripts.app_settings import DEST_DIR
from scripts.utils.punctuation_handler import clean_language_specific_punctuation

def create_fallback_file(
    source_path: str,
    dest_dir: str,
    original_filename: str,
    source_lang: dict,
    target_lang: dict,
    game_profile: dict,
) -> str:
    """
    [Fallback Function] Copies the source file, changing only the header and filename.
    This is a safety net for when translation fails or is not needed.
    """
    logging.info(i18n.t("creating_fallback_file"))
    try:
        with open(source_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()

        # Robustly find and replace the language header
        header_found_and_replaced = False
        for i, line in enumerate(lines):
            if line.strip().startswith(source_lang["key"]):
                lines[i] = line.replace(source_lang["key"], target_lang["key"])
                header_found_and_replaced = True
                break
        if not header_found_and_replaced:
            lines.insert(0, f"{target_lang['key']}:\n")

        # Dynamically generate the new filename based on language keys
        source_suffix = f"_l_{source_lang['key'][2:]}"
        target_suffix = f"_l_{target_lang['key'][2:]}"
        new_filename = (
            original_filename.replace(source_suffix, target_suffix)
            if source_suffix in original_filename
            else original_filename
        )
        dest_file_path = os.path.join(dest_dir, new_filename)

        # Write the file using the encoding specified in the game profile
        with open(dest_file_path, "w", encoding=game_profile.get("encoding", "utf-8-sig")) as f:
            f.writelines(lines)
        logging.info(i18n.t("fallback_file_created", filename=new_filename))
        return dest_file_path
    except Exception as e:
        logging.error(i18n.t("fallback_creation_error", error=e))
        return ""


def rebuild_and_write_file(
    original_lines: list[str],
    texts_to_translate: list[str],
    translated_texts: list[str],
    key_map: dict[int, dict],
    dest_dir_path: str,
    original_filename: str,
    source_lang: dict,
    target_lang: dict,
    game_profile: dict,
) -> str:
    """
    Reconstructs the .yml file with the translated text and saves it to disk.
    """
    # Create a map from original text to translated text for easy lookup.
    translation_map = dict(zip(texts_to_translate, translated_texts))
    
    # Work on a copy of the original lines to preserve comments and structure.
    new_lines = list(original_lines)

    # --- Reconstruct each translated line ---
    for i, original_text in enumerate(texts_to_translate):
        translated_text = translation_map.get(original_text, original_text)
        
        # 智能清理标点符号（后处理层）
        cleaned_translated_text = clean_language_specific_punctuation(
            translated_text, 
            source_lang["code"], 
            target_lang["code"]
        )
        
        line_info = key_map[i]
        
        line_num = line_info["line_num"]
        key_part = line_info["key_part"]
        original_value_part = line_info["original_value_part"]
        
        # Rebuild the value part, preserving things like the ":0" and escaping quotes.
        safe_translated_text = cleaned_translated_text.strip().replace('"', r"\"")
        new_value_part = original_value_part.replace(f'"{original_text}"', f'"{safe_translated_text}"')
        
        # Preserve the original indentation.
        indent = original_lines[line_num][: original_lines[line_num].find(key_part)]
        
        # Reconstruct the full line without adding an extra colon.
        new_lines[line_num] = f"{indent}{key_part}:{new_value_part}\n"

    # --- Replace the language header ---
    header_found_and_replaced = False
    for i, line in enumerate(new_lines):
        if line.strip().startswith(source_lang["key"]):
            new_lines[i] = line.replace(source_lang["key"], target_lang["key"])
            header_found_and_replaced = True
            break
    if not header_found_and_replaced:
        new_lines.insert(0, f"{target_lang['key']}:\n")
        
    # --- Generate the new filename ---
    source_suffix = f"_l_{source_lang['key'][2:]}"
    target_suffix = f"_l_{target_lang['key'][2:]}"
    new_filename = (
        original_filename.replace(source_suffix, target_suffix)
        if source_suffix in original_filename
        else original_filename
    )
    
    dest_file_path = os.path.join(dest_dir_path, new_filename)

    # --- Save the file using the correct encoding from the game profile ---
    with open(dest_file_path, "w", encoding=game_profile.get("encoding", "utf-8-sig")) as f:
        f.writelines(new_lines) # Use the modified 'new_lines' list
        
    try:
        log_filename = os.path.join(os.path.relpath(dest_dir_path, "my_translation"), new_filename)
    except ValueError:
        log_filename = new_filename

    logging.info(
        i18n.t(
            "writing_file_success",
            filename=log_filename,
        )
    )
    
    # 返回生成的文件路径
    return dest_file_path