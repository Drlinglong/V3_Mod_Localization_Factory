# scripts/workflows/initial_translate.py
import os
from core import file_parser, api_handler, file_builder, asset_handler
from config import SOURCE_DIR, DEST_DIR, LANGUAGES
from utils import i18n

def run(mod_name, source_lang, target_languages, game_profile, mod_context):
    """【最终版】工作流，已完全集成多游戏文件结构。"""
    
    is_batch_mode = len(target_languages) > 1
    if is_batch_mode:
        output_folder_name = f"Multilanguage-{mod_name}"
    else:
        target_lang = target_languages[0]
        prefix = target_lang.get("folder_prefix", f"{target_lang['code']}-")
        output_folder_name = f"{prefix}{mod_name}"
    
    workflow_name = i18n.t("workflow_initial_translate_name")
    print(i18n.t("start_workflow", workflow_name=workflow_name, mod_name=mod_name))
    
    client = api_handler.initialize_client()
    if not client:
        print(i18n.t("api_client_init_fail")); return

    primary_target_lang = target_languages[0] if not is_batch_mode else LANGUAGES.get("1")
    asset_handler.process_metadata(mod_name, client, source_lang, primary_target_lang, output_folder_name, mod_context, game_profile)
    asset_handler.copy_assets(mod_name, output_folder_name, game_profile)
    
    source_loc_folder_name = game_profile['source_localization_folder']
    source_localization_path = os.path.join(SOURCE_DIR, mod_name, source_loc_folder_name)

    if not os.path.isdir(source_localization_path):
        print(f"警告：在 {mod_name} 目录下找不到源语言文件夹 '{source_loc_folder_name}'，跳过.yml文件处理。"); return
    
    all_files_data = []
    source_suffix = f"_l_{source_lang['key'][2:]}.yml"
    
    for root, _, files in os.walk(source_localization_path):
        for filename in files:
            if not filename.endswith(source_suffix): continue
            source_file_path = os.path.join(root, filename)
            original_lines, texts_to_translate, key_map = file_parser.extract_translatable_content(source_file_path)
            all_files_data.append({
                "filename": filename, "root": root, "original_lines": original_lines,
                "texts_to_translate": texts_to_translate, "key_map": key_map
            })
    
    for target_lang in target_languages:
        print(i18n.t("translating_to_language", lang_name=target_lang['name']))
        
        for file_data in all_files_data:
            source_file_path = os.path.join(file_data['root'], file_data['filename'])
            relative_path = os.path.relpath(file_data['root'], source_localization_path)
            
            target_loc_folder_name = game_profile['source_localization_folder']
            target_lang_folder_name = target_lang['key'][2:]
            dest_dir_path = os.path.join(DEST_DIR, output_folder_name, target_loc_folder_name, target_lang_folder_name, relative_path)
            os.makedirs(dest_dir_path, exist_ok=True)

            if not file_data['texts_to_translate']:
                file_builder.create_fallback_file(source_file_path, dest_dir_path, file_data['filename'], source_lang, target_lang)
                continue
            
            translated_texts = api_handler.translate_texts_in_batches(client, file_data['texts_to_translate'], source_lang, target_lang, game_profile, mod_context)
            
            if translated_texts is None:
                file_builder.create_fallback_file(source_file_path, dest_dir_path, file_data['filename'], source_lang, target_lang)
                continue
                
            file_builder.rebuild_and_write_file(file_data['original_lines'], file_data['texts_to_translate'], translated_texts, file_data['key_map'], dest_dir_path, file_data['filename'], source_lang, target_lang)