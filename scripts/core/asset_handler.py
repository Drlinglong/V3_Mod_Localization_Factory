# scripts/core/asset_handler.py
import os
import json
import shutil
from utils import i18n
from config import SOURCE_DIR, DEST_DIR
from .api_handler import translate_single_text

def process_metadata(mod_name, client, source_lang, target_lang):
    """【V2.7】处理 metadata.json 文件，已完全支持多语言。"""
    print(i18n.t("processing_metadata"))
    source_meta_file = os.path.join(SOURCE_DIR, mod_name, '.metadata', 'metadata.json')
    dest_meta_dir = os.path.join(DEST_DIR, f"汉化-{mod_name}", '.metadata')
    
    if not os.path.exists(source_meta_file):
        print(i18n.t("metadata_not_found"))
        return
        
    with open(source_meta_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 【核心修改】在调用时，传入 source_lang 和 target_lang
    original_name = data.get('name', '')
    translated_name = translate_single_text(client, original_name, "mod name", mod_name, source_lang, target_lang)
    
    # 让后缀也支持国际化
    if target_lang['key'] == 'l_simp_chinese':
        suffix = " (中文汉化)"
    else:
        suffix = f" ({target_lang['name']} Translation)"
    data['name'] = f"{translated_name}{suffix}"

    original_desc = data.get('short_description', '')
    data['short_description'] = translate_single_text(client, original_desc, "mod short description", mod_name, source_lang, target_lang)

    os.makedirs(dest_meta_dir, exist_ok=True)
    dest_meta_file = os.path.join(dest_meta_dir, 'metadata.json')
    with open(dest_meta_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(i18n.t("metadata_success"))

def copy_thumbnail(mod_name):
    """复制 thumbnail.png 文件 (此函数无变化)。"""
    print(i18n.t("processing_thumbnail"))
    source_thumb_file = os.path.join(SOURCE_DIR, mod_name, 'thumbnail.png')
    dest_dir = os.path.join(DEST_DIR, f"汉化-{mod_name}")
    
    if not os.path.exists(source_thumb_file):
        print(i18n.t("thumbnail_not_found"))
        return
        
    shutil.copy2(source_thumb_file, dest_dir)
    print(i18n.t("thumbnail_copied"))