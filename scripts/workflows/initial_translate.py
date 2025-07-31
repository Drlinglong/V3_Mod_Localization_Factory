# scripts/workflows/initial_translate.py

import os
from core import file_parser, api_handler, file_builder, asset_handler, directory_handler
from config import SOURCE_DIR
from utils import i18n

def run(mod_name, source_lang, target_lang):
    """“首次翻译”工作流的主函数，现在能正确传递语言参数。"""
    
    workflow_name = i18n.t("workflow_initial_translate_name")
    print(i18n.t("start_workflow", workflow_name=workflow_name, mod_name=f"{mod_name} ({source_lang['name']} -> {target_lang['name']})"))
    
    client = api_handler.initialize_client()
    if not client:
        print(i18n.t("api_client_init_fail"))
        return

    # 资产处理流程现在也需要传递语言参数
    asset_handler.process_metadata(mod_name, client, source_lang, target_lang)
    asset_handler.copy_thumbnail(mod_name)

    # 核心翻译流程
    source_folder_name = source_lang['name'].lower().replace(' ', '_') # 例如 'english' 或 'português_do_brasil'
    source_localization_path = os.path.join(SOURCE_DIR, mod_name, 'localization', source_folder_name)
    
    if not os.path.isdir(source_localization_path):
        print(f"警告：在 {mod_name} 目录下找不到源语言文件夹 '{source_folder_name}'，跳过.yml文件处理。")
    else:
        for root, _, files in os.walk(source_localization_path):
            for filename in files:
                if not filename.endswith('.yml'): continue
                
                source_file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(root, source_localization_path)
                
                original_lines, texts_to_translate, key_map = file_parser.extract_translatable_content(source_file_path)
                
                target_folder_name = target_lang['key'][2:] # 从 l_simp_chinese 中提取 simp_chinese
                dest_dir_path = os.path.join('my_translation', f"汉化-{mod_name}", 'localization', target_folder_name, relative_path)
                os.makedirs(dest_dir_path, exist_ok=True)
                
                if not texts_to_translate:
                    file_builder.create_fallback_file(source_file_path, dest_dir_path, filename, source_lang, target_lang)
                    continue
                
                # 【核心修正】将 source_lang 和 target_lang 传递给API处理器
                translated_texts = api_handler.translate_texts_in_batches(client, texts_to_translate, source_lang, target_lang)
                
                if translated_texts is None:
                    file_builder.create_fallback_file(source_file_path, dest_dir_path, filename, source_lang, target_lang)
                    continue
                    
                # 【核心修正】将 source_lang 和 target_lang 传递给文件构造器
                file_builder.rebuild_and_write_file(original_lines, texts_to_translate, translated_texts, key_map, dest_dir_path, filename, source_lang, target_lang)

    # --- 清理流程 ---
    directory_handler.cleanup_source_directory(mod_name)