# scripts/workflows/initial_translate.py
import os
import logging

from scripts.core import file_parser, api_handler, file_builder, asset_handler, directory_handler
from scripts.core.glossary_manager import glossary_manager
from scripts.core.proofreading_tracker import create_proofreading_tracker
from scripts.config import SOURCE_DIR, DEST_DIR, LANGUAGES
from scripts.utils import i18n


def run(mod_name: str,
        source_lang: dict,
        target_languages: list[dict],
        game_profile: dict,
        mod_context: str,
        selected_provider: str = "gemini"):
    """【最终版】初次翻译工作流（多语言 & 多游戏兼容）"""

    # ───────────── 1. ścieżki i tryb ─────────────
    is_batch_mode = len(target_languages) > 1
    if is_batch_mode:
        output_folder_name = f"Multilanguage-{mod_name}"
        primary_target_lang = LANGUAGES["1"]  # English jako lingua franca do metadata
    else:
        target_lang = target_languages[0]
        prefix = target_lang.get("folder_prefix", f"{target_lang['code']}-")
        output_folder_name = f"{prefix}{mod_name}"
        primary_target_lang = target_lang

    logging.info(i18n.t("start_workflow",
                 workflow_name=i18n.t("workflow_initial_translate_name"),
                 mod_name=mod_name))

    # ───────────── 2. init klienta ─────────────
    client, provider_name = api_handler.initialize_client(selected_provider)
    if not client:
        logging.warning(i18n.t("api_client_init_fail"))
        return

    # ───────────── 2.5. 加载游戏专用词典 ─────────────
    game_id = game_profile.get("id", "")
    if game_id:
        glossary_loaded = glossary_manager.load_game_glossary(game_id)
        if glossary_loaded:
            stats = glossary_manager.get_glossary_stats()
            if i18n.get_current_language() == "en_US":
                logging.info(f"Glossary loaded successfully: {stats['description']} ({stats['total_entries']} entries)")
            else:
                logging.info(f"词典加载成功: {stats['description']} ({stats['total_entries']} 个条目)")
        else:
            if i18n.get_current_language() == "en_US":
                logging.info(f"Glossary file for {game_id} not found, will use no-glossary mode")
            else:
                logging.info(f"未找到 {game_id} 的词典文件，将使用无词典模式")
    else:
        if i18n.get_current_language() == "en_US":
            logging.warning("Game profile missing ID, cannot load glossary")
        else:
            logging.warning("游戏配置中缺少ID，无法加载词典")

    # ───────────── 2.6. 初始化校对进度追踪器 ─────────────
    # 获取主要目标语言代码用于生成对应语言的校对进度看板
    primary_lang_code = primary_target_lang.get("code", "zh-CN")
    proofreading_tracker = create_proofreading_tracker(mod_name, output_folder_name, primary_lang_code)
    # 根据脚本启动语言选择语言名称显示
    lang_name_map = {
        "zh-CN": "简体中文",
        "en": "English", 
        "fr": "Français",
        "de": "Deutsch",
        "es": "Español",
        "ja": "日本語",
        "ko": "한국어",
        "pl": "Polski",
        "pt-BR": "Português do Brasil",
        "ru": "Русский",
        "tr": "Türkçe"
    }
    display_name = lang_name_map.get(primary_target_lang.get("code", "zh-CN"), "中文")
    logging.info(i18n.t("proofreading_tracker_init", lang_name=display_name))

    # ───────────── 3. metadata + assety ─────────────
    asset_handler.process_metadata(
        mod_name, client, source_lang, primary_target_lang,
        output_folder_name, mod_context, game_profile, provider_name
    )
    asset_handler.copy_assets(mod_name, output_folder_name, game_profile)

    # ───────────── 4. przygotuj ścieżki źródłowe ─────────────
    source_loc_folder = game_profile["source_localization_folder"]
    source_loc_path = os.path.join(SOURCE_DIR, mod_name, source_loc_folder)
    cust_loc_root = os.path.join(SOURCE_DIR, mod_name, "customizable_localization")

    all_files_data = []

    # —— 4.a parsuj .yml w localisation/
    if os.path.isdir(source_loc_path):
        suffix = f"_l_{source_lang['key'][2:]}.yml"
        for root, _, files in os.walk(source_loc_path):
            for fn in files:
                if not fn.endswith(suffix):
                    continue
                fp = os.path.join(root, fn)
                orig, texts, km = file_parser.extract_translatable_content(fp)
                all_files_data.append({
                    "filename": fn,
                    "root": root,
                    "original_lines": orig,
                    "texts_to_translate": texts,
                    "key_map": km,
                    "is_custom_loc": False
                })

    # —— 4.b parsuj *.txt w customizable_localization/
    if os.path.isdir(cust_loc_root):
        for root, _, files in os.walk(cust_loc_root):
            for fn in files:
                if not fn.endswith(".txt"):
                    continue
                fp = os.path.join(root, fn)
                orig, texts, km = file_parser.extract_translatable_content(fp)
                all_files_data.append({
                    "filename": fn,
                    "root": root,
                    "original_lines": orig,
                    "texts_to_translate": texts,
                    "key_map": km,
                    "is_custom_loc": True
                })

    # ───────────── 5. tłumaczenie + zapis ─────────────
    for target_lang in target_languages:
        logging.info(i18n.t("translating_to_language", lang_name=target_lang["name"]))

        for fd in all_files_data:
            src_fp = os.path.join(fd["root"], fd["filename"])

            # wybór dest_dir_path zależnie od typu pliku
            if fd["is_custom_loc"]:
                rel = os.path.relpath(fd["root"], cust_loc_root)
                dest_dir = os.path.join(
                    DEST_DIR,
                    output_folder_name,
                    "customizable_localization",
                    target_lang["key"][2:],
                    rel,
                )
            else:
                rel = os.path.relpath(fd["root"], source_loc_path)
                dest_dir = os.path.join(
                    DEST_DIR,
                    output_folder_name,
                    source_loc_folder,
                    target_lang["key"][2:],
                    rel,
                )

            os.makedirs(dest_dir, exist_ok=True)

            # fallback gdy brak tekstów
            if not fd["texts_to_translate"]:
                dest_file_path = file_builder.create_fallback_file(
                    src_fp, dest_dir, fd["filename"],
                    source_lang, target_lang, game_profile
                )
                
                # 收集fallback文件信息用于校对进度追踪
                if dest_file_path:
                    source_file_path = os.path.join(fd["root"], fd["filename"])
                    proofreading_tracker.add_file_info({
                        'source_path': source_file_path,
                        'dest_path': dest_file_path,
                        'translated_lines': 0,  # fallback文件没有翻译行数
                        'filename': fd["filename"],
                        'is_custom_loc': fd["is_custom_loc"]
                    })
                continue

            # samo tłumaczenie
            translated = api_handler.translate_texts_in_batches(
                client,
                provider_name,
                fd["texts_to_translate"],
                source_lang,
                target_lang,
                game_profile,
                mod_context,
            )

            # AI błąd → fallback
            if translated is None:
                dest_file_path = file_builder.create_fallback_file(
                    src_fp, dest_dir, fd["filename"],
                    source_lang, target_lang, game_profile
                )
                
                # 收集fallback文件信息用于校对进度追踪
                if dest_file_path:
                    source_file_path = os.path.join(fd["root"], fd["filename"])
                    proofreading_tracker.add_file_info({
                        'source_path': source_file_path,
                        'dest_path': dest_file_path,
                        'translated_lines': 0,  # fallback文件没有翻译行数
                        'filename': fd["filename"],
                        'is_custom_loc': fd["is_custom_loc"]
                    })
                continue

            # zapis przetłumaczonego pliku
            dest_file_path = file_builder.rebuild_and_write_file(
                fd["original_lines"],
                fd["texts_to_translate"],
                translated,
                fd["key_map"],
                dest_dir,
                fd["filename"],
                source_lang,
                target_lang,
                game_profile,
            )
            
            # 收集文件信息用于校对进度追踪
            if dest_file_path:
                source_file_path = os.path.join(fd["root"], fd["filename"])
                translated_lines_count = len(fd["texts_to_translate"])
                
                proofreading_tracker.add_file_info({
                    'source_path': source_file_path,
                    'dest_path': dest_file_path,
                    'translated_lines': translated_lines_count,
                    'filename': fd["filename"],
                    'is_custom_loc': fd["is_custom_loc"]
                })

        # ───────────── 6. 生成校对进度看板 ─────────────
        if i18n.get_current_language() == "en_US":
            logging.info("Generating proofreading progress board...")
            if proofreading_tracker.save_proofreading_progress():
                logging.info("Proofreading progress board generated successfully")
            else:
                logging.warning("Failed to generate proofreading progress board")
        else:
            logging.info("正在生成校对进度看板...")
            if proofreading_tracker.save_proofreading_progress():
                logging.info("校对进度看板生成成功")
            else:
                logging.warning("校对进度看板生成失败")

    # ───────────── 7. 询问是否清理多余文件 ─────────────
    if i18n.get_current_language() == "en_US":
        cleanup_prompt = f"\nTranslation completed! Do you want to clean up the source mod folder '{mod_name}' to save disk space?"
    else:
        cleanup_prompt = f"\n翻译完成！是否要清理源MOD文件夹 '{mod_name}' 以节省磁盘空间？"
    
    cleanup_prompt += "\nThis will delete all files except '.metadata', 'localization', and 'thumbnail.png'."
    cleanup_prompt += "\nDo you want to continue? (Enter 'y' or 'yes' to confirm): "
    
    cleanup_choice = input(cleanup_prompt).strip().lower()
    if cleanup_choice in ['y', 'yes']:
        if i18n.get_current_language() == "en_US":
            logging.info("Starting source mod folder cleanup...")
        else:
            logging.info("开始清理源MOD文件夹...")
        
        directory_handler.cleanup_source_directory(mod_name, game_profile)
    else:
        if i18n.get_current_language() == "en_US":
            logging.info("Cleanup skipped by user")
        else:
            logging.info("用户选择跳过清理")

    if i18n.get_current_language() == "en_US":
        logging.info(f"Workflow completed! Mod '{mod_name}' translation task finished")
    else:
        logging.info(f"工作流完成！Mod '{mod_name}' 的翻译任务已完成")
