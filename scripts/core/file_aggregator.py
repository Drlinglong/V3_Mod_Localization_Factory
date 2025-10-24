# scripts/core/file_aggregator.py
import os
import logging
from typing import List, Dict, Any

from scripts.core.progress_db_manager import ProgressDBManager
from scripts.core import file_builder
from scripts.core.parallel_processor import FileTask # Re-using the data structure
from scripts.utils import i18n
from scripts.app_settings import SOURCE_DIR, DEST_DIR


def assemble_files_from_db(
    job_id: str,
    progress_manager: ProgressDBManager,
    all_files_data: List[Dict[str, Any]],
    target_lang: Dict[str, Any],
    source_lang: Dict[str, Any],
    game_profile: Dict[str, Any],
    output_folder_name: str,
    mod_name: str
):
    """
    从进度数据库中获取所有已完成的批次，并将它们组装成最终的翻译文件。
    这是一个同步的、单线程的过程。

    Args:
        job_id: 当前翻译任务的唯一ID。
        progress_manager: 进度数据库管理器实例。
        all_files_data: 包含所有源文件元数据的列表，用于重建文件。
        target_lang: 目标语言信息。
        source_lang: 源语言信息。
        game_profile: 游戏配置信息。
        output_folder_name: 输出文件夹名称。
    """
    logging.info(i18n.t("log_info_assembly_start", job_id=job_id))

    # 1. 从数据库获取所有已完成的批次
    completed_batches = progress_manager.get_all_completed_batches_for_job()
    if not completed_batches:
        logging.warning(i18n.t("log_warn_no_batches_to_assemble", job_id=job_id))
        return

    # 2. 按 file_path 分组
    grouped_batches: Dict[str, List[Dict]] = {}
    for batch in completed_batches:
        file_path = batch["file_path"]
        if file_path not in grouped_batches:
            grouped_batches[file_path] = []
        grouped_batches[file_path].append(batch)

    logging.info(i18n.t("log_info_assembly_files_count", count=len(grouped_batches)))

    # 3. 遍历每个文件，排序、组装并写入
    for file_path, batches in grouped_batches.items():
        # 找到对应的原始文件数据
        # file_path is the full path, need to match it with (root, filename) in all_files_data
        file_data = next((fd for fd in all_files_data if os.path.join(fd["root"], fd["filename"]) == file_path), None)

        if not file_data:
            logging.error(f"Could not find original file data for '{file_path}'. Skipping assembly.")
            continue

        # 3a. 按 batch_index 严格升序排序
        batches.sort(key=lambda b: b["batch_index"])

        # 3b. 组装 translated_texts
        translated_texts = []
        for batch in batches:
            translated_texts.extend(batch["translated_texts"])

        # 检查组装后的文本数量是否与源文件匹配
        if len(translated_texts) != len(file_data["texts_to_translate"]):
            logging.error(f"Assembly failed for '{file_path}': Mismatched text count. "
                          f"Expected {len(file_data['texts_to_translate'])}, got {len(translated_texts)}. "
                          "The file will not be written.")
            continue

        # 3c. 构建目标目录
        # This part requires re-creating a temporary FileTask-like object to reuse the logic
        # Or refactoring _build_dest_dir to not depend on a FileTask object
        file_info = {
            "is_custom_loc": file_data["is_custom_loc"],
            "root": file_data["root"],
            "mod_name": mod_name
        }

        dest_dir = _build_dest_dir_standalone(
            file_info, target_lang, output_folder_name, game_profile
        )
        os.makedirs(dest_dir, exist_ok=True)

        # 3d. 重建并写入文件
        file_builder.rebuild_and_write_file(
            file_data["original_lines"],
            file_data["texts_to_translate"],
            translated_texts,
            file_data["key_map"],
            dest_dir,
            file_data["filename"],
            source_lang,
            target_lang,
            game_profile,
        )
        logging.info(i18n.t("file_build_completed", filename=file_data["filename"]))

    logging.info(i18n.t("log_info_assembly_completed", job_id=job_id))


def _build_dest_dir_standalone(file_info: Dict, target_lang: dict, output_folder_name: str, game_profile: dict) -> str:
    """构建目标目录路径 (独立版本)"""
    # This logic is duplicated from initial_translate.py and should ideally be centralized
    if file_info["is_custom_loc"]:
        cust_loc_root = os.path.join(SOURCE_DIR, file_info["mod_name"], "customizable_localization")
        rel = os.path.relpath(file_info["root"], cust_loc_root)
        dest_dir = os.path.join(
            DEST_DIR,
            output_folder_name,
            "customizable_localization",
            target_lang["key"][2:],
            rel,
        )
    else:
        source_loc_folder = game_profile["source_localization_folder"]
        source_loc_path = os.path.join(SOURCE_DIR, file_info["mod_name"], source_loc_folder)
        rel = os.path.relpath(file_info["root"], source_loc_path)
        dest_dir = os.path.join(
            DEST_DIR,
            output_folder_name,
            source_loc_folder,
            target_lang["key"][2:],
            rel,
        )
    return dest_dir
