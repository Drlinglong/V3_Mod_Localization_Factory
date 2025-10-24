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
from scripts.core.progress_db_manager import ProgressDBManager
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


class ParallelProcessor:
    """批次级全局并行处理器 - 实现真正的批次级并行调度"""
    
    def __init__(self, max_workers: int = 24):
        """
        初始化并行处理器
        
        Args:
            max_workers: 最大并行工作线程数
        """
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
    
    def process_files_parallel(
        self,
        file_tasks: List[FileTask],
        translation_function: Callable,
        progress_manager: ProgressDBManager
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        批次级全局并行处理多个文件
        
        Args:
            file_tasks: 文件任务列表
            translation_function: 翻译函数 (API Handler的translate_texts_in_batches)
            progress_manager: 进度数据库管理器
            
        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (是否全部成功, [所有警告信息])
        """
        if not file_tasks:
            self.logger.info(i18n.t("no_files_to_process"))
            return True, []
        
        # 1. 将所有文件分解为批次任务
        batch_tasks = self._create_batch_tasks(file_tasks)
        total_batches = len(batch_tasks)
        completed_batches = progress_manager.get_completed_batch_count()
        self.logger.info(i18n.t("parallel_processing_start_resumable",
                                 total=total_batches,
                                 completed=completed_batches,
                                 remaining=total_batches - completed_batches))
        
        # 2. 全局批次并行处理
        all_ok, all_warnings = self._process_batches_parallel(batch_tasks, translation_function, progress_manager)
        
        self.logger.info(i18n.t("all_files_processing_completed"))
        return all_ok, all_warnings
    
    def _create_batch_tasks(self, file_tasks: List[FileTask]) -> List[BatchTask]:
        """将所有文件分解为批次任务"""
        batch_tasks = []
        
        for file_task in file_tasks:
            if not file_task.texts_to_translate:
                continue
                
            # 根据provider选择chunk大小
            chunk_size = GEMINI_CLI_CHUNK_SIZE if file_task.provider_name == "gemini_cli" else CHUNK_SIZE
            
            # 将文件文本分成批次
            texts = file_task.texts_to_translate
            file_batch_index = 0 # 文件内的批次索引
            for i in range(0, len(texts), chunk_size):
                start_index = i
                end_index = min(i + chunk_size, len(texts))
                batch_texts = texts[start_index:end_index]
                
                batch_task = BatchTask(
                    file_task=file_task,
                    batch_index=file_batch_index,  # 使用文件内批次索引
                    start_index=start_index,
                    end_index=end_index,
                    texts=batch_texts
                )
                batch_tasks.append(batch_task)
                self.logger.debug(f"Created batch {file_batch_index} for file {file_task.filename} with {len(batch_texts)} texts")
                file_batch_index += 1
        
        return batch_tasks
    
    def _process_batches_parallel(
        self,
        batch_tasks: List[BatchTask],
        translation_function: Callable,
        progress_manager: ProgressDBManager
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """全局批次并行处理"""
        if not batch_tasks:
            return True, []
        
        all_ok = True
        # 使用线程池并行处理所有批次
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有批次任务
            future_to_batch = {
                executor.submit(
                    self._process_single_batch,
                    batch_task,
                    translation_function,
                    progress_manager
                ): batch_task
                for batch_task in batch_tasks
            }
            
            # 收集结果
            all_warnings = []
            
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_task = future_to_batch[future]
                
                try:
                    is_success, warnings = future.result()
                    if not is_success:
                        all_ok = False
                    if warnings:
                        all_warnings.extend(warnings)
                
                except Exception as e:
                    all_ok = False
                    self.logger.exception(f"Batch processing failed: {batch_task.file_task.filename} batch {batch_task.batch_index}, error: {e}")
        
        return all_ok, all_warnings
    
    def _process_single_batch(
        self,
        batch_task: BatchTask,
        translation_function: Callable,
        progress_manager: ProgressDBManager
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        处理单个批次.
        1. 检查数据库中是否已完成
        2. 如果未完成，则执行翻译
        3. 成功后，将结果存入数据库
        """
        warnings = []
        # 使用完整相对路径作为数据库中的 file_path
        file_path = os.path.join(batch_task.file_task.root, batch_task.file_task.filename)

        # 1. 检查是否已完成
        if progress_manager.is_batch_completed(file_path, batch_task.batch_index):
            self.logger.info(f"Skipping completed batch: {batch_task.file_task.filename}, batch index {batch_task.batch_index}")
            return True, []

        # 2. 如果未完成，则执行翻译
        try:
            self.logger.debug(f"Processing batch {batch_task.batch_index} for file {batch_task.file_task.filename}")
            
            # Modernized call: the function expects the task object
            processed_task = translation_function(batch_task)
            
            # Post-translation validation
            if processed_task and processed_task.translated_texts:
                glossary = glossary_manager.get_glossary_for_translation()
                if glossary:
                    # Transform the glossary into the simple Dict[str, str] format expected by the validator
                    simple_glossary = {}
                    source_lang_code = batch_task.file_task.source_lang.get("code")
                    target_lang_code = batch_task.file_task.target_lang.get("code")

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

                # 3. 成功后，将结果存入数据库
                progress_manager.add_batch_result(
                    file_path=file_path,
                    batch_index=batch_task.batch_index,
                    translated_texts=processed_task.translated_texts
                )
                return True, warnings
            else:
                self.logger.error(f"Translation returned empty result for {batch_task.file_task.filename} batch {batch_task.batch_index}")
                return False, warnings
                
        except Exception as e:
            self.logger.exception(f"Batch translation error for {batch_task.file_task.filename} batch {batch_task.batch_index}: {e}")
            return False, warnings
