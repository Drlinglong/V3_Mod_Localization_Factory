# scripts/workflows/initial_translate.py

import os
from core import file_parser, api_handler, file_builder, asset_handler, directory_handler
from config import SOURCE_DIR
from utils import i18n

def run(mod_name):
    """“首次翻译”工作流的主函数，负责调度所有核心模块。"""
    
    print(i18n.t("start_workflow", workflow_name="'首次翻译'", mod_name=mod_name))
    
    # 初始化API客户端
    client = api_handler.initialize_client()
    if not client:
        print(i18n.t("api_client_init_fail"))
        return

    # --- 其他资产处理流程 ---
    asset_handler.process_metadata(mod_name, client)
    asset_handler.copy_thumbnail(mod_name)

    # --- 核心翻译流程 ---
    source_localization_path = os.path.join(SOURCE_DIR, mod_name, 'localization', 'english')
    
    # 检查本地化文件夹是否存在
    if not os.path.isdir(source_localization_path):
        print(f"警告：在 {mod_name} 目录下找不到 'localization/english' 文件夹，跳过.yml文件处理。")
    else:
        for root, _, files in os.walk(source_localization_path):
            for filename in files:
                if not filename.endswith('.yml'): continue
                
                source_file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(root, source_localization_path)
                
                original_lines, texts_to_translate, key_map = file_parser.extract_translatable_content(source_file_path)
                
                dest_dir_path = os.path.join('my_translation', f"汉化-{mod_name}", 'localization', 'simp_chinese', relative_path)
                os.makedirs(dest_dir_path, exist_ok=True)
                
                if not texts_to_translate:
                    file_builder.create_fallback_file(source_file_path, dest_dir_path, filename)
                    continue
                
                translated_texts = api_handler.translate_texts_in_batches(client, texts_to_translate)
                
                if translated_texts is None:
                    file_builder.create_fallback_file(source_file_path, dest_dir_path, filename)
                    continue
                    
                file_builder.rebuild_and_write_file(original_lines, texts_to_translate, translated_texts, key_map, dest_dir_path, filename)

    # --- 清理流程 ---
    directory_handler.cleanup_source_directory(mod_name)