# scripts/core/parallel_processor.py
"""
多文件并行处理器
实现真正的多文件并行处理，确保所有文件能同时运行
职责：纯并行调度，不包含文件操作逻辑
"""

import os
import logging
import concurrent.futures
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from scripts.utils import i18n
from scripts.config import CHUNK_SIZE


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


class ParallelProcessor:
    """多文件并行处理器 - 纯并行调度，不包含文件操作逻辑"""
    
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
        并行处理多个文件，每个文件内部由API Handler处理
        
        Args:
            file_tasks: 文件任务列表
            translation_function: 翻译函数 (API Handler的translate_texts_in_batches)
            
        Returns:
            Dict[str, List[str]]: {filename: translated_texts} - 每个文件的完整翻译结果
        """
        if not file_tasks:
            self.logger.info(i18n.t("no_files_to_process"))
            return {}
        
        self.logger.info(i18n.t("parallel_processing_start", count=len(file_tasks)))
        
        # 使用线程池并行处理所有文件
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有文件任务
            future_to_file = {
                executor.submit(
                    self._process_single_file,
                    file_task,
                    translation_function
                ): file_task
                for file_task in file_tasks
            }
            
            # 收集结果
            file_results = {}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_task = future_to_file[future]
                filename = file_task.filename
                
                try:
                    result = future.result()
                    if result is not None:
                        file_results[filename] = result
                        self.logger.info(i18n.t("file_translation_completed", filename=filename))
                    else:
                        self.logger.error(i18n.t("file_translation_failed", filename=filename))
                        # 翻译失败时，使用原文作为fallback
                        file_results[filename] = file_task.texts_to_translate
                
                except Exception as e:
                    self.logger.exception(i18n.t("file_processing_failed", filename=filename, error=e))
                    # 异常时，使用原文作为fallback
                    file_results[filename] = file_task.texts_to_translate
        
        self.logger.info(i18n.t("all_files_processing_completed", count=len(file_results)))
        return file_results
    
    def _process_single_file(
        self,
        file_task: FileTask,
        translation_function: Callable
    ) -> Optional[List[str]]:
        """
        处理单个文件的所有文本，返回完整的翻译结果
        
        Args:
            file_task: 文件任务
            translation_function: 翻译函数
            
        Returns:
            List[str] 或 None: 完整的翻译结果，失败时返回None
        """
        try:
            if not file_task.texts_to_translate:
                # 空文件，返回空列表
                return []
            
            # 调用翻译函数处理整个文件
            # 注意：API Handler负责文件内部的批次分割和处理
            translated_texts = translation_function(
                file_task.client,
                file_task.provider_name,
                file_task.texts_to_translate,
                file_task.source_lang,
                file_task.target_lang,
                file_task.game_profile,
                file_task.mod_context,
            )
            
            if translated_texts and len(translated_texts) == len(file_task.texts_to_translate):
                return translated_texts
            else:
                self.logger.error(i18n.t("translation_result_mismatch", 
                                       filename=file_task.filename,
                                       original_count=len(file_task.texts_to_translate),
                                       translated_count=len(translated_texts) if translated_texts else 0))
                return None
                
        except Exception as e:
            self.logger.exception(i18n.t("file_translation_error", filename=file_task.filename, error=e))
            return None
