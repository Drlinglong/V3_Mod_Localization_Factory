# scripts/workflows/initial_translate.py
import os
import logging
from typing import Any

from scripts.core import file_parser, api_handler, file_builder, asset_handler, directory_handler
from scripts.core.glossary_manager import glossary_manager
from scripts.core.proofreading_tracker import create_proofreading_tracker
from scripts.core.parallel_processor import ParallelProcessor, FileTask
from scripts.config import SOURCE_DIR, DEST_DIR, LANGUAGES, RECOMMENDED_MAX_WORKERS
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
            logging.info(i18n.t("glossary_loaded_success", count=stats['total_entries']))
        else:
            logging.warning(i18n.t("glossary_load_failed"))

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

    # ───────────── 5. 多语言并行翻译 ─────────────
    for target_lang in target_languages:
        logging.info(i18n.t("translating_to_language", lang_name=target_lang["name"]))
        
        # 创建校对进度追踪器
        proofreading_tracker = create_proofreading_tracker(
            mod_name, output_folder_name, target_lang.get("code", "zh-CN")
        )
        
        # 创建文件任务列表
        file_tasks = []
        for fd in all_files_data:
            # 检查是否需要创建fallback文件
            if not fd["texts_to_translate"]:
                # 空文件，创建fallback
                # 创建临时的FileTask对象用于构建目录
                temp_file_task = FileTask(
                    filename=fd["filename"],
                    root=fd["root"],
                    original_lines=fd["original_lines"],
                    texts_to_translate=fd["texts_to_translate"],
                    key_map=fd["key_map"],
                    is_custom_loc=fd["is_custom_loc"],
                    target_lang=target_lang,
                    source_lang=source_lang,
                    game_profile=game_profile,
                    mod_context=mod_context,
                    provider_name=provider_name,
                    output_folder_name=output_folder_name,
                    source_dir=SOURCE_DIR,
                    dest_dir=DEST_DIR,
                    client=client,
                    mod_name=mod_name
                )
                
                dest_dir = _build_dest_dir(temp_file_task, target_lang, output_folder_name, game_profile)
                os.makedirs(dest_dir, exist_ok=True)
                
                dest_file_path = file_builder.create_fallback_file(
                    os.path.join(fd["root"], fd["filename"]), 
                    dest_dir, 
                    fd["filename"],
                    source_lang, 
                    target_lang, 
                    game_profile
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
            
            # 创建文件任务
            file_task = FileTask(
                filename=fd["filename"],
                root=fd["root"],
                original_lines=fd["original_lines"],
                texts_to_translate=fd["texts_to_translate"],
                key_map=fd["key_map"],
                is_custom_loc=fd["is_custom_loc"],
                target_lang=target_lang,
                source_lang=source_lang,
                game_profile=game_profile,
                mod_context=mod_context,
                provider_name=provider_name,
                output_folder_name=output_folder_name,
                source_dir=SOURCE_DIR,
                dest_dir=DEST_DIR,
                client=client,
                mod_name=mod_name
            )
            file_tasks.append(file_task)
        
        # 使用并行处理器处理文件
        if file_tasks:
            # 计算最优并行数（建议24个批次同时运行）
            max_workers = RECOMMENDED_MAX_WORKERS
            processor = ParallelProcessor(max_workers=max_workers)
            
            # 获取翻译函数（使用统一的API Handler接口）
            # 使用单批次翻译函数，支持批次编号
            translation_function = api_handler.translate_single_batch_with_batch_num
            
            # 并行处理所有文件，获取翻译结果
            file_results = processor.process_files_parallel(
                file_tasks=file_tasks,
                translation_function=translation_function
            )
            
            # 处理每个文件的翻译结果
            for filename, translated_texts in file_results.items():
                # 找到对应的文件任务
                file_task = next(ft for ft in file_tasks if ft.filename == filename)
                
                if translated_texts is None:
                    logging.error(i18n.t("file_translation_failed", filename=filename))
                    continue
                
                # 构建目标目录
                dest_dir = _build_dest_dir(file_task, target_lang, output_folder_name, game_profile)
                os.makedirs(dest_dir, exist_ok=True)
                
                # 重建并写入文件
                dest_file_path = file_builder.rebuild_and_write_file(
                    file_task.original_lines,
                    file_task.texts_to_translate,
                    translated_texts,
                    file_task.key_map,
                    dest_dir,
                    file_task.filename,
                    file_task.source_lang,
                    file_task.target_lang,
                    file_task.game_profile,
                )
                
                # 更新校对进度追踪
                if dest_file_path:
                    source_file_path = os.path.join(file_task.root, file_task.filename)
                    translated_lines_count = len(file_task.texts_to_translate)
                    
                    proofreading_tracker.add_file_info({
                        'source_path': source_file_path,
                        'dest_path': dest_file_path,
                        'translated_lines': translated_lines_count,
                        'filename': file_task.filename,
                        'is_custom_loc': file_task.is_custom_loc
                    })
                    
                    logging.info(i18n.t("file_build_completed", filename=filename))
        
        # ───────────── 6. 运行后处理格式验证 ─────────────
        try:
            from scripts.core.post_processing_manager import PostProcessingManager
            
            # 构建输出文件夹路径
            output_folder_path = os.path.join(DEST_DIR, output_folder_name)
            
            # 创建后处理验证管理器
            post_processor = PostProcessingManager(game_profile, output_folder_path)
            
            # 运行验证
            validation_success = post_processor.run_validation(target_lang)
            
            if validation_success:
                # 获取验证统计信息
                stats = post_processor.get_validation_stats()
                logging.info(i18n.t("post_processing_completion_summary", 
                                   total_files=stats['total_files'],
                                   valid_files=stats['valid_files'],
                                   files_with_issues=stats['files_with_issues'],
                                   total_errors=stats['total_errors'],
                                   total_warnings=stats['total_warnings']))

                # 合并结果进校对进度表
                post_processor.attach_results_to_proofreading_tracker(proofreading_tracker)
            else:
                logging.warning("后处理验证过程中发生错误")
                
        except ImportError:
            logging.warning("后处理验证模块未找到，跳过格式验证")
        except Exception as e:
            logging.error(f"后处理验证失败: {e}")

        # ───────────── 6.5. 生成校对进度看板 ─────────────
        # 仅在此处保存一次，避免重复写入导致“复读”
        logging.info(i18n.t("generating_proofreading_board"))
        if proofreading_tracker.save_proofreading_progress():
            logging.info(i18n.t("proofreading_board_generated_success"))
        else:
            logging.warning(i18n.t("proofreading_board_generation_failed"))

    # ───────────── 7. 处理元数据 ─────────────
    if is_batch_mode:
        # 多语言模式：使用英语作为主要语言处理元数据
        process_metadata_for_language(
            mod_name, client, source_lang, primary_target_lang,
            output_folder_name, mod_context, game_profile, provider_name
        )
    else:
        # 单语言模式：处理目标语言的元数据
        process_metadata_for_language(
            mod_name, client, source_lang, target_lang,
            output_folder_name, mod_context, game_profile, provider_name
        )

    # ───────────── 8. 完成提示 ─────────────
    logging.info(i18n.t("translation_workflow_completed"))
    logging.info(i18n.t("output_folder_created", folder=output_folder_name))


def _build_dest_dir(file_task: FileTask, target_lang: dict, output_folder_name: str, game_profile: dict) -> str:
    """构建目标目录路径"""
    if file_task.is_custom_loc:
        cust_loc_root = os.path.join(SOURCE_DIR, file_task.mod_name, "customizable_localization")
        rel = os.path.relpath(file_task.root, cust_loc_root)
        dest_dir = os.path.join(
            DEST_DIR,
            output_folder_name,
            "customizable_localization",
            target_lang["key"][2:],
            rel,
        )
    else:
        source_loc_folder = game_profile["source_localization_folder"]
        source_loc_path = os.path.join(SOURCE_DIR, file_task.mod_name, source_loc_folder)
        rel = os.path.relpath(file_task.root, source_loc_path)
        dest_dir = os.path.join(
            DEST_DIR,
            output_folder_name,
            source_loc_folder,
            target_lang["key"][2:],
            rel,
        )
    return dest_dir


def process_metadata_for_language(
    mod_name: str,
    client: Any,
    source_lang: dict,
    target_lang: dict,
    output_folder_name: str,
    mod_context: str,
    game_profile: dict,
    provider_name: str
) -> None:
    """为指定语言处理元数据"""
    try:
        asset_handler.process_metadata(
            mod_name, client, source_lang, target_lang,
            output_folder_name, mod_context, game_profile, provider_name
        )
    except Exception as e:
        logging.exception(i18n.t("metadata_processing_failed", error=e))
