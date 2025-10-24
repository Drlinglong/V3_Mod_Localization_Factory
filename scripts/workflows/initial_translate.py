# scripts/workflows/initial_translate.py
import os
import logging
import time
from typing import Any, Optional, List

from scripts.core import file_parser, api_handler, file_builder, asset_handler, directory_handler
from scripts.core.glossary_manager import glossary_manager
from scripts.core.proofreading_tracker import create_proofreading_tracker
from scripts.core.parallel_processor import ParallelProcessor, FileTask
from scripts.core.archive_manager import archive_manager
from scripts.core.progress_db_manager import ProgressDBManager
from scripts.core.file_aggregator import assemble_files_from_db
from scripts.app_settings import SOURCE_DIR, DEST_DIR, LANGUAGES, RECOMMENDED_MAX_WORKERS, ARCHIVE_RESULTS_AFTER_TRANSLATION
from scripts.utils import i18n


def run(mod_name: str,
        source_lang: dict,
        target_languages: list[dict],
        game_profile: dict,
        mod_context: str,
        selected_provider: str = "gemini",
        selected_glossary_ids: Optional[List[int]] = None,
        mod_id_for_archive: Optional[int] = None):
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
    logging.info(i18n.t("log_selected_provider", provider=selected_provider))

    # ARCHIVE STAGE 1 is now handled in main.py

    # ───────────── 2. init klienta ─────────────
    gemini_cli_model = None
    if selected_provider == "gemini_cli":
        while True:
            print(i18n.t("gemini_cli_model_selection_prompt"))
            print("1. gemini-2.5-pro ")
            print("2. gemini-2.5-flash ")
            choice = input(i18n.t("setup_enter_choice")).strip()
            if choice == "1":
                gemini_cli_model = "gemini-2.5-pro"
                break
            elif choice == "2":
                gemini_cli_model = "gemini-2.5-flash"
                break
            else:
                print(i18n.t("setup_invalid_choice"))

    handler = api_handler.get_handler(selected_provider, model_name=gemini_cli_model)
    if not handler or not handler.client:
        logging.warning(i18n.t("api_client_init_fail"))
        return

    # ───────────── 2.5. 加载游戏专用词典 ─────────────
    game_id = game_profile.get("id", "")
    if game_id:
        if selected_glossary_ids:
            glossary_manager.load_selected_glossaries(selected_glossary_ids)
        else:
            glossary_manager.load_game_glossary(game_id)

    # ───────────── 3. 创建输出目录 + 复制资源 ─────────────
    directory_handler.create_output_structure(
        mod_name, output_folder_name, game_profile
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

    if not all_files_data:
        logging.warning(i18n.t("no_localisable_files_found", lang_name=source_lang['name']))
        return

    # ───────────── ARCHIVE STAGE 2: Create Source Version Snapshot ─────────────
    version_id_for_archive = None
    if ARCHIVE_RESULTS_AFTER_TRANSLATION and mod_id_for_archive:
        version_id_for_archive = archive_manager.create_source_version(mod_id_for_archive, all_files_data)

    # ───────────── 5. 多语言并行翻译 (CRASH-SAFE WORKFLOW) ─────────────
    for target_lang in target_languages:
        # ─── 5.1. 初始化任务 & 进度数据库 ───
        job_id = f"{mod_name}-{target_lang['code']}-{int(time.time())}"
        progress_manager = ProgressDBManager(job_id=job_id)
        logging.info(i18n.t("translating_to_language_job", lang_name=target_lang["name"], job_id=job_id))
        
        proofreading_tracker = create_proofreading_tracker(
            mod_name, output_folder_name, target_lang.get("code", "zh-CN")
        )
        
        file_tasks = []
        for fd in all_files_data:
            if not fd["texts_to_translate"]: # Fallback logic for empty files
                dest_dir = _build_dest_dir_from_info(
                    {"is_custom_loc": fd["is_custom_loc"], "root": fd["root"], "mod_name": mod_name},
                    target_lang, output_folder_name, game_profile
                )
                os.makedirs(dest_dir, exist_ok=True)
                dest_file_path = file_builder.create_fallback_file(
                    os.path.join(fd["root"], fd["filename"]), dest_dir, fd["filename"],
                    source_lang, target_lang, game_profile
                )
                if dest_file_path:
                    proofreading_tracker.add_file_info({
                        'source_path': os.path.join(fd["root"], fd["filename"]),
                        'dest_path': dest_file_path, 'translated_lines': 0,
                        'filename': fd["filename"], 'is_custom_loc': fd["is_custom_loc"]
                    })
                continue
            
            file_tasks.append(FileTask(
                filename=fd["filename"], root=fd["root"], original_lines=fd["original_lines"],
                texts_to_translate=fd["texts_to_translate"], key_map=fd["key_map"],
                is_custom_loc=fd["is_custom_loc"], target_lang=target_lang, source_lang=source_lang,
                game_profile=game_profile, mod_context=mod_context, provider_name=handler.provider_name,
                output_folder_name=output_folder_name, source_dir=SOURCE_DIR, dest_dir=DEST_DIR,
                client=handler.client, mod_name=mod_name
            ))
        
        # ─── 5.2. [生产阶段] 并行处理，填充数据库 ───
        all_ok = True
        if file_tasks:
            max_workers = RECOMMENDED_MAX_WORKERS
            if selected_provider == "ollama":
                max_workers = 1
                logging.info(i18n.t("ollama_single_thread_warning"))
            processor = ParallelProcessor(max_workers=max_workers)
            translation_function = handler.translate_batch
            
            all_ok, all_warnings = processor.process_files_parallel(
                file_tasks=file_tasks,
                translation_function=translation_function,
                progress_manager=progress_manager
            )
            
            if all_warnings:
                logging.warning(i18n.t("glossary_consistency_warning_header"))
                for warning in all_warnings: logging.warning(warning['message'])
                logging.warning(i18n.t("cjk_glossary_warning"))

        if not all_ok:
            logging.error(i18n.t("log_error_parallel_processing_failed", job_id=job_id, lang_name=target_lang["name"]))
            progress_manager.close()
            continue

        # ─── 5.3. [消费阶段] 从数据库组装文件 ───
        assemble_files_from_db(
            job_id=job_id, progress_manager=progress_manager, all_files_data=all_files_data,
            target_lang=target_lang, source_lang=source_lang, game_profile=game_profile,
            output_folder_name=output_folder_name, mod_name=mod_name
        )

        # ─── 5.4. 更新校对追踪器 (文件写入后) ───
        for fd in all_files_data:
            if not fd["texts_to_translate"]: continue
            dest_dir_path = _build_dest_dir_from_info(
                {"is_custom_loc": fd["is_custom_loc"], "root": fd["root"], "mod_name": mod_name},
                target_lang, output_folder_name, game_profile
            )
            dest_file_path = file_builder.get_dest_filepath(
                dest_dir_path, fd['filename'], source_lang, target_lang, game_profile
            )
            proofreading_tracker.add_file_info({
                'source_path': os.path.join(fd["root"], fd["filename"]),
                'dest_path': dest_file_path, 'translated_lines': len(fd["texts_to_translate"]),
                'filename': fd['filename'], 'is_custom_loc': fd['is_custom_loc']
            })

        # ─── 6. 后处理 & 校对看板 ───
        _run_post_processing(game_profile, mod_name, output_folder_name, target_lang, source_lang, proofreading_tracker)

        logging.info(i18n.t("generating_proofreading_board"))
        if proofreading_tracker.save_proofreading_progress():
            logging.info(i18n.t("proofreading_board_generated_success"))
        else:
            logging.warning(i18n.t("proofreading_board_generation_failed"))

        # ─── 7. 归档翻译结果 (从数据库获取) ───
        if ARCHIVE_RESULTS_AFTER_TRANSLATION and version_id_for_archive:
            completed_batches = progress_manager.get_all_completed_batches_for_job()
            file_results_from_db = {}
            for batch in completed_batches:
                filename = os.path.basename(batch['file_path'])
                if filename not in file_results_from_db: file_results_from_db[filename] = []
                file_results_from_db[filename].extend(batch['translated_texts'])

            if file_results_from_db:
                archive_manager.archive_translated_results(
                    version_id=version_id_for_archive, file_results=file_results_from_db,
                    all_files_data=all_files_data, target_lang_code=target_lang['code']
                )

        # ─── 8. 清理本次任务 ───
        progress_manager.cleanup_job_data()
        progress_manager.close()

    # ───────────── 7. 处理元数据 ─────────────
    if is_batch_mode:
        # 多语言模式：使用英语作为主要语言处理元数据
        process_metadata_for_language(
            mod_name, handler, source_lang, primary_target_lang,
            output_folder_name, mod_context, game_profile
        )
    else:
        # 单语言模式：处理目标语言的元数据
        process_metadata_for_language(
            mod_name, handler, source_lang, target_lang,
            output_folder_name, mod_context, game_profile
        )

    # ───────────── 8. 完成提示 ─────────────
    logging.info(i18n.t("translation_workflow_completed"))
    logging.info(i18n.t("output_folder_created", folder=output_folder_name))


def _build_dest_dir_from_info(file_info: dict, target_lang: dict, output_folder_name: str, game_profile: dict) -> str:
    """(Refactored) 构建目标目录路径"""
    if file_info["is_custom_loc"]:
        cust_loc_root = os.path.join(SOURCE_DIR, file_info["mod_name"], "customizable_localization")
        rel = os.path.relpath(file_info["root"], cust_loc_root)
        dest_dir = os.path.join(
            DEST_DIR, output_folder_name, "customizable_localization",
            target_lang["key"][2:], rel
        )
    else:
        source_loc_folder = game_profile["source_localization_folder"]
        source_loc_path = os.path.join(SOURCE_DIR, file_info["mod_name"], source_loc_folder)
        rel = os.path.relpath(file_info["root"], source_loc_path)
        dest_dir = os.path.join(
            DEST_DIR, output_folder_name, source_loc_folder,
            target_lang["key"][2:], rel
        )
    return dest_dir

def _run_post_processing(game_profile, mod_name, output_folder_name, target_lang, source_lang, proofreading_tracker):
    """(Extracted) 运行后处理格式验证"""
    try:
        from scripts.core.post_processing_manager import PostProcessingManager
        from scripts.utils import tag_scanner

        dynamic_tags = None
        official_tags_path = game_profile.get("official_tags_codex")

        if official_tags_path:
            logging.info(i18n.t("log.tag_analysis.starting_dynamic_validation"))
            mod_loc_path_for_scan = os.path.join(SOURCE_DIR, mod_name, game_profile["source_localization_folder"])
            dynamic_tags = tag_scanner.analyze_mod_and_get_all_valid_tags(
                mod_loc_path=mod_loc_path_for_scan,
                official_tags_json_path=official_tags_path
            )
        else:
            logging.warning(f"Skipping dynamic tag analysis: 'official_tags_codex' not defined for game '{game_profile.get('id')}'.")

        output_folder_path = os.path.join(DEST_DIR, output_folder_name)
        post_processor = PostProcessingManager(game_profile, output_folder_path)
        validation_success = post_processor.run_validation(target_lang, source_lang, dynamic_valid_tags=dynamic_tags)

        if validation_success:
            stats = post_processor.get_validation_stats()
            logging.info(i18n.t("post_processing_completion_summary",
                               total_files=stats['total_files'], valid_files=stats['valid_files'],
                               files_with_issues=stats['files_with_issues'], total_errors=stats['total_errors'],
                               total_warnings=stats['total_warnings']))
            post_processor.attach_results_to_proofreading_tracker(proofreading_tracker)
        else:
            logging.warning("后处理验证过程中发生错误")

    except ImportError:
        logging.warning("后处理验证模块未找到，跳过格式验证")
    except Exception as e:
        logging.error(f"后处理验证失败: {e}")


def process_metadata_for_language(
    mod_name: str,
    handler: Any,
    source_lang: dict,
    target_lang: dict,
    output_folder_name: str,
    mod_context: str,
    game_profile: dict
) -> None:
    """为指定语言处理元数据"""
    try:
        asset_handler.process_metadata(
            mod_name, handler, source_lang, target_lang,
            output_folder_name, mod_context, game_profile
        )
    except Exception as e:
        logging.exception(i18n.t("metadata_processing_failed", error=e))
