# scripts/workflows/initial_translate.py

import os
from core import file_parser, api_handler, file_builder, asset_handler, directory_handler
# 【修正】同时导入 SOURCE_DIR 和 DEST_DIR
from config import SOURCE_DIR, DEST_DIR, LANGUAGES 
from utils import i18n

def run(mod_name, source_lang, target_languages):
    """
    “首次翻译”工作流的主函数。
    【V3.4】输出文件夹名称现在会根据目标语言动态变化。
    """
    
    is_batch_mode = len(target_languages) > 1
    
    # 【核心修正】根据模式和目标语言，从config中动态获取文件夹前缀
    if is_batch_mode:
        output_folder_name = f"Multilanguage-{mod_name}"
    else:
        # 在单一模式下，获取该语言专属的前缀
        target_lang = target_languages[0]
        prefix = target_lang.get("folder_prefix", f"{target_lang['code']}-") # 如果没定义前缀，则使用语言代码作为备用
        output_folder_name = f"{prefix}{mod_name}"

    workflow_name = i18n.t("workflow_initial_translate_name")
    print(i18n.t("start_workflow", workflow_name=workflow_name, mod_name=mod_name))
    
    client = api_handler.initialize_client()
    if not client:
        print(i18n.t("api_client_init_fail"))
        return

    # --- 第一部分：一次性任务 ---
    primary_target_lang = target_languages[0] if not is_batch_mode else LANGUAGES.get("1")
    asset_handler.process_metadata(mod_name, client, source_lang, primary_target_lang, output_folder_name)
    asset_handler.copy_thumbnail(mod_name, output_folder_name)    
   
    # --- 第二部分：循环任务 (.yml 文件翻译) ---
    source_folder_name = source_lang['name'].lower()
    source_localization_path = os.path.join(SOURCE_DIR, mod_name, 'localization', source_folder_name)

    if not os.path.isdir(source_localization_path):
        print(f"警告：在 {mod_name} 目录下找不到源语言文件夹 '{source_folder_name}'，跳过.yml文件处理。")
        return
    
    all_files_data = []
    for root, _, files in os.walk(source_localization_path):
        for filename in files:
            if not filename.endswith('.yml'): continue
            source_file_path = os.path.join(root, filename)
            original_lines, texts_to_translate, key_map = file_parser.extract_translatable_content(source_file_path)
            all_files_data.append({
                "filename": filename, "root": root, "original_lines": original_lines,
                "texts_to_translate": texts_to_translate, "key_map": key_map
            })
    
    for target_lang in target_languages:
        # 【核心修正】使用i18n来获取提示文本
        print(i18n.t("translating_to_language", lang_name=target_lang['name']))
        
        for file_data in all_files_data:
            source_file_path = os.path.join(file_data['root'], file_data['filename'])
            relative_path = os.path.relpath(file_data['root'], source_localization_path)
            target_folder_name = target_lang['key'][2:]
            
            dest_dir_path = os.path.join(DEST_DIR, output_folder_name, 'localization', target_folder_name, relative_path)
            os.makedirs(dest_dir_path, exist_ok=True)

            if not file_data['texts_to_translate']:
                file_builder.create_fallback_file(source_file_path, dest_dir_path, file_data['filename'], source_lang, target_lang)
                continue
            
            translated_texts = api_handler.translate_texts_in_batches(client, file_data['texts_to_translate'], source_lang, target_lang)
            
            if translated_texts is None:
                file_builder.create_fallback_file(source_file_path, dest_dir_path, file_data['filename'], source_lang, target_lang)
                continue
                
            file_builder.rebuild_and_write_file(file_data['original_lines'], file_data['texts_to_translate'], translated_texts, file_data['key_map'], dest_dir_path, file_data['filename'], source_lang, target_lang)