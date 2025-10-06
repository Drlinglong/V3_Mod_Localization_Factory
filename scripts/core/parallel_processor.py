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
from dataclasses import dataclass
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
        translation_function: Callable
    ) -> Dict[str, List[str]]:
        """
        批次级全局并行处理多个文件
        
        Args:
            file_tasks: 文件任务列表
            translation_function: 翻译函数 (API Handler的translate_texts_in_batches)
            
        Returns:
            Dict[str, List[str]]: {filename: translated_texts} - 每个文件的完整翻译结果
        """
        if not file_tasks:
            self.logger.info(i18n.t("no_files_to_process"))
            return {}
        
        # 1. 将所有文件分解为批次任务
        batch_tasks = self._create_batch_tasks(file_tasks)
        self.logger.info(i18n.t("parallel_processing_start", count=len(batch_tasks)))
        
        # 2. 全局批次并行处理
        batch_results = self._process_batches_parallel(batch_tasks, translation_function)
        
        # 3. 按文件收集结果
        file_results = self._collect_file_results(file_tasks, batch_results)
        
        self.logger.info(i18n.t("all_files_processing_completed", count=len(file_results)))
        return file_results
    
    def _create_batch_tasks(self, file_tasks: List[FileTask]) -> List[BatchTask]:
        """将所有文件分解为批次任务"""
        batch_tasks = []
        global_batch_index = 0  # 全局批次索引，确保所有批次编号唯一
        
        for file_task in file_tasks:
            if not file_task.texts_to_translate:
                continue
                
            # 根据provider选择chunk大小
            chunk_size = GEMINI_CLI_CHUNK_SIZE if file_task.provider_name == "gemini_cli" else CHUNK_SIZE
            
            # 将文件文本分成批次
            texts = file_task.texts_to_translate
            for i in range(0, len(texts), chunk_size):
                start_index = i
                end_index = min(i + chunk_size, len(texts))
                batch_texts = texts[start_index:end_index]
                local_batch_index = i // chunk_size  # 文件内批次索引
                
                batch_task = BatchTask(
                    file_task=file_task,
                    batch_index=global_batch_index,  # 使用全局批次索引
                    start_index=start_index,
                    end_index=end_index,
                    texts=batch_texts
                )
                batch_tasks.append(batch_task)
                self.logger.debug(f"Created batch {global_batch_index + 1} for file {file_task.filename} with {len(batch_texts)} texts")
                global_batch_index += 1  # 递增全局批次索引
        
        return batch_tasks
    
    def _process_batches_parallel(
        self,
        batch_tasks: List[BatchTask],
        translation_function: Callable
    ) -> Dict[Tuple[str, int], List[str]]:
        """全局批次并行处理"""
        if not batch_tasks:
            return {}
        
        # 使用线程池并行处理所有批次
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有批次任务
            future_to_batch = {
                executor.submit(
                    self._process_single_batch,
                    batch_task,
                    translation_function
                ): batch_task
                for batch_task in batch_tasks
            }
            
            # 收集结果
            batch_results = {}
            
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_task = future_to_batch[future]
                batch_key = (batch_task.file_task.filename, batch_task.batch_index)
                
                try:
                    result = future.result()
                    if result is not None:
                        batch_results[batch_key] = result
                        self.logger.debug(f"Batch completed: {batch_task.file_task.filename} batch {batch_task.batch_index}")
                    else:
                        self.logger.error(f"Batch failed: {batch_task.file_task.filename} batch {batch_task.batch_index}")
                        # 翻译失败时，使用原文作为fallback
                        batch_results[batch_key] = batch_task.texts
                
                except Exception as e:
                    self.logger.exception(f"Batch processing failed: {batch_task.file_task.filename} batch {batch_task.batch_index}, error: {e}")
                    # 异常时，使用原文作为fallback
                    batch_results[batch_key] = batch_task.texts
        
        return batch_results
    
    def _process_single_batch(
        self,
        batch_task: BatchTask,
        translation_function: Callable
    ) -> Optional[List[str]]:
        """处理单个批次"""
        try:
            # 调试信息：显示批次编号
            actual_batch_num = batch_task.batch_index + 1
            self.logger.debug(f"Processing batch {actual_batch_num} for file {batch_task.file_task.filename}")
            
            # 使用传入的翻译函数，传递正确的批次编号
            translated_texts = translation_function(
                batch_task.file_task.client,
                batch_task.file_task.provider_name,
                batch_task.texts,
                batch_task.file_task.source_lang,
                batch_task.file_task.target_lang,
                batch_task.file_task.game_profile,
                batch_task.file_task.mod_context,
                actual_batch_num  # 批次编号从1开始
            )
            
            if translated_texts and len(translated_texts) == len(batch_task.texts):
                return translated_texts
            else:
                self.logger.error(f"Translation result mismatch for {batch_task.file_task.filename} batch {batch_task.batch_index}: "
                                f"expected {len(batch_task.texts)}, got {len(translated_texts) if translated_texts else 0}")
                return None
                
        except Exception as e:
            self.logger.exception(f"Batch translation error for {batch_task.file_task.filename} batch {batch_task.batch_index}: {e}")
            return None
    def _collect_file_results(
        self,
        file_tasks: List[FileTask],
        batch_results: Dict[Tuple[str, int], List[str]]
    ) -> Dict[str, List[str]]:
        """按文件收集批次结果"""
        file_results = {}
        
        # Group batch results by filename
        grouped_batch_results: Dict[str, Dict[int, List[str]]] = {}
        for (filename, batch_idx), result_list in batch_results.items():
            if filename not in grouped_batch_results:
                grouped_batch_results[filename] = {}
            grouped_batch_results[filename][batch_idx] = result_list

        for file_task in file_tasks:
            if not file_task.texts_to_translate:
                file_results[file_task.filename] = []
                continue

            file_translated_texts = []
            
            # Get all batches for this file, sorted by their global batch index
            file_batches = grouped_batch_results.get(file_task.filename, {})
            sorted_batch_indices = sorted(file_batches.keys())

            for batch_idx in sorted_batch_indices:
                file_translated_texts.extend(file_batches[batch_idx])
            
            # 检查结果完整性
            if len(file_translated_texts) == len(file_task.texts_to_translate):
                file_results[file_task.filename] = file_translated_texts
                self.logger.info(i18n.t("file_translation_completed", filename=file_task.filename))
            else:
                self.logger.error(f"File translation incomplete for {file_task.filename}: "
                                f"expected {len(file_task.texts_to_translate)}, got {len(file_translated_texts)}")
                # 使用原文作为fallback
                file_results[file_task.filename] = file_task.texts_to_translate

        return file_results
