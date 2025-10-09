# scripts/core/parallel_processor.py
"""
多文件并行处理器
实现真正的批次级全局并行调度，确保所有批次能同时运行
职责：批次级并行调度，不包含文件操作逻辑
"""

import os
import logging
import concurrent.futures
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass, field

from scripts.core.glossary_manager import glossary_manager
from scripts.utils import i18n
from scripts.app_settings import CHUNK_SIZE, GEMINI_CLI_CHUNK_SIZE


@dataclass
class FileTask:
    """文件任务数据结构"""
    filename: str
    root: str
    original_lines: List[str]
    texts_to_translate: List[str]
    key_map: Dict[str, Any]
    is_custom_loc: bool
    target_lang: Dict[str, Any]
    source_lang: Dict[str, Any]
    game_profile: Dict[str, Any]
    mod_context: str
    provider_name: str
    output_folder_name: str
    source_dir: str
    dest_dir: str
    client: Any  # API客户端
    mod_name: str  # 添加mod_name字段


@dataclass
class BatchTask:
    """批次任务数据结构"""
    file_task: FileTask
    batch_index: int
    start_index: int
    end_index: int
    texts: List[str]
    translated_texts: Optional[List[str]] = field(default=None, init=False)
    failed: bool = field(default=False, init=False)


class ParallelProcessor:
    """批次级全局并行处理器 - 实现真正的批次级并行调度"""

    def __init__(self, max_workers: int = 24):
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

    def process_files_parallel(
        self,
        file_tasks: List[FileTask],
        translation_function: Callable
    ) -> Tuple[Dict[str, List[str]], List[Dict[str, Any]]]:
        if not file_tasks:
            return {}, []
        
        batch_tasks = self._create_batch_tasks(file_tasks)
        self.logger.info(i18n.t("parallel_processing_start", count=len(batch_tasks)))
        
        batch_results, all_warnings = self._process_batches_parallel(batch_tasks, translation_function)
        
        file_results = self._collect_file_results(file_tasks, batch_results)
        
        self.logger.info(i18n.t("all_files_processing_completed", count=len(file_results)))
        return file_results, all_warnings

    def _create_batch_tasks(self, file_tasks: List[FileTask]) -> List[BatchTask]:
        batch_tasks = []
        global_batch_index = 0
        
        for file_task in file_tasks:
            if not file_task.texts_to_translate:
                continue

            chunk_size = GEMINI_CLI_CHUNK_SIZE if file_task.provider_name == "gemini_cli" else CHUNK_SIZE
            
            texts = file_task.texts_to_translate
            for i in range(0, len(texts), chunk_size):
                batch_texts = texts[i:i + chunk_size]
                batch_task = BatchTask(
                    file_task=file_task,
                    batch_index=global_batch_index,
                    start_index=i,
                    end_index=i + len(batch_texts),
                    texts=batch_texts
                )
                batch_tasks.append(batch_task)
                global_batch_index += 1
        
        return batch_tasks

    def _process_batches_parallel(
        self,
        batch_tasks: List[BatchTask],
        translation_function: Callable
    ) -> Tuple[Dict[Tuple[str, int], BatchTask], List[Dict[str, Any]]]:
        if not batch_tasks:
            return {}, []

        batch_results = {}
        all_warnings = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_batch = {
                executor.submit(self._process_single_batch, batch, translation_function): batch
                for batch in batch_tasks
            }

            for future in concurrent.futures.as_completed(future_to_batch):
                batch_task = future_to_batch[future]
                processed_task, warnings = future.result()
                batch_key = (batch_task.file_task.filename, batch_task.batch_index)
                batch_results[batch_key] = processed_task
                if warnings:
                    all_warnings.extend(warnings)

        if any(task.failed for task in batch_results.values()):
            failed_count = sum(1 for task in batch_results.values() if task.failed)
            self.logger.error(f"{failed_count}/{len(batch_tasks)} translation batches failed.")
            raise RuntimeError("One or more translation batches failed. Halting workflow.")

        return batch_results, all_warnings

    def _process_single_batch(
        self,
        batch_task: BatchTask,
        translation_function: Callable
    ) -> Tuple[BatchTask, List[Dict[str, Any]]]:
        warnings = []
        processed_task = translation_function(batch_task)

        if processed_task.translated_texts is None:
            processed_task.failed = True
            return processed_task, warnings

        # Post-translation validation
        glossary = glossary_manager.get_glossary_for_translation()
        if glossary:
            simple_glossary = {}
            source_lang_code = processed_task.file_task.source_lang.get("code")
            target_lang_code = processed_task.file_task.target_lang.get("code")
            if source_lang_code and target_lang_code and 'entries' in glossary:
                for entry in glossary.get('entries', []):
                    translations = entry.get('translations', {})
                    source_term = translations.get(source_lang_code)
                    target_term = translations.get(target_lang_code)
                    if source_term and target_term and isinstance(source_term, str) and isinstance(target_term, str):
                        simple_glossary[source_term] = target_term
            if simple_glossary:
                from scripts.utils.glossary_validator import GlossaryValidator
                validator = GlossaryValidator()
                validation_warnings = validator.validate_batch(processed_task, simple_glossary)
                if validation_warnings:
                    warnings.extend(validation_warnings)

        return processed_task, warnings

    def _collect_file_results(
        self,
        file_tasks: List[FileTask],
        batch_results: Dict[Tuple[str, int], BatchTask]
    ) -> Dict[str, List[str]]:
        file_results = {}
        
        grouped_batch_results: Dict[str, Dict[int, BatchTask]] = {}
        for (filename, batch_idx), task in batch_results.items():
            if filename not in grouped_batch_results:
                grouped_batch_results[filename] = {}
            grouped_batch_results[filename][batch_idx] = task

        for file_task in file_tasks:
            if not file_task.texts_to_translate:
                file_results[file_task.filename] = []
                continue

            file_translated_texts = []
            file_failed = False
            
            file_batches = grouped_batch_results.get(file_task.filename, {})
            sorted_batch_indices = sorted(file_batches.keys())

            for batch_idx in sorted_batch_indices:
                task = file_batches[batch_idx]
                if task.failed:
                    file_failed = True
                    break
                file_translated_texts.extend(task.translated_texts)

            if file_failed or len(file_translated_texts) != len(file_task.texts_to_translate):
                self.logger.error(f"File translation failed for {file_task.filename}, using fallback.")
                file_results[file_task.filename] = file_task.texts_to_translate
            else:
                file_results[file_task.filename] = file_translated_texts
                self.logger.info(i18n.t("file_translation_completed", filename=file_task.filename))

        return file_results
