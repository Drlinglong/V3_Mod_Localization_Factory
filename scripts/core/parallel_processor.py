# scripts/core/parallel_processor.py
"""
多文件并行处理器
实现真正的多文件并行处理，确保所有批次能同时运行
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


@dataclass
class BatchTask:
    """批次任务数据结构"""
    file_task: FileTask
    batch_index: int
    start_index: int
    end_index: int
    texts: List[str]


class ParallelProcessor:
    """多文件并行处理器"""
    
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
        file_builder_function: Callable,
        proofreading_tracker: Any
    ) -> None:
        """
        并行处理多个文件
        
        Args:
            file_tasks: 文件任务列表
            translation_function: 翻译函数
            file_builder_function: 文件构建函数
            proofreading_tracker: 校对追踪器
        """
        # 1. 将文件任务分解为批次任务
        batch_tasks = self._create_batch_tasks(file_tasks)
        
        # 2. 创建批次任务队列
        self.logger.info(i18n.t("parallel_processing_start", count=len(batch_tasks)))
        
        # 3. 使用线程池并行处理所有批次
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有批次任务
            future_to_batch = {
                executor.submit(
                    self._process_single_batch,
                    batch_task,
                    translation_function,
                    file_builder_function,
                    proofreading_tracker
                ): batch_task
                for batch_task in batch_tasks
            }
            
            # 处理完成的任务
            completed_files = set()
            file_results = {}  # 存储每个文件的翻译结果
            
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_task = future_to_batch[future]
                filename = batch_task.file_task.filename
                
                try:
                    result = future.result()
                    if result is not None:
                        # 存储批次结果
                        if filename not in file_results:
                            file_results[filename] = []
                        file_results[filename].append((batch_task.batch_index, result))
                        
                        # 记录批次完成
                        self.logger.info(i18n.t("batch_completed", filename=filename, batch_num=batch_task.batch_index + 1))
                        
                        # 检查文件是否完成
                        if self._is_file_complete(filename, file_results, batch_tasks):
                            self._finalize_file(
                                filename, 
                                file_results[filename], 
                                batch_tasks, 
                                file_builder_function,
                                proofreading_tracker
                            )
                            completed_files.add(filename)
                            self.logger.info(i18n.t("file_completed", filename=filename))
                
                except Exception as e:
                    self.logger.exception(i18n.t("batch_processing_failed", filename=filename, batch_num=batch_task.batch_index + 1, error=e))
        
        self.logger.info(i18n.t("all_files_processing_completed", count=len(completed_files)))
    
    def _create_batch_tasks(self, file_tasks: List[FileTask]) -> List[BatchTask]:
        """
        将文件任务分解为批次任务
        
        Args:
            file_tasks: 文件任务列表
            
        Returns:
            批次任务列表
        """
        batch_tasks = []
        
        for file_task in file_tasks:
            texts = file_task.texts_to_translate
            
            if not texts:
                # 空文件，创建fallback
                batch_tasks.append(BatchTask(
                    file_task=file_task,
                    batch_index=0,
                    start_index=0,
                    end_index=0,
                    texts=[]
                ))
                continue
            
            # 计算批次数量
            total_batches = (len(texts) + CHUNK_SIZE - 1) // CHUNK_SIZE
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * CHUNK_SIZE
                end_idx = min(start_idx + CHUNK_SIZE, len(texts))
                batch_texts = texts[start_idx:end_idx]
                
                batch_tasks.append(BatchTask(
                    file_task=file_task,
                    batch_index=batch_idx,
                    start_index=start_idx,
                    end_index=end_idx,
                    texts=batch_texts
                ))
        
        return batch_tasks
    
    def _process_single_batch(
        self,
        batch_task: BatchTask,
        translation_function: Callable,
        file_builder_function: Callable,
        proofreading_tracker: Any
    ) -> Optional[List[str]]:
        """
        处理单个批次
        
        Args:
            batch_task: 批次任务
            translation_function: 翻译函数
            file_builder_function: 文件构建函数
            proofreading_tracker: 校对追踪器
            
        Returns:
            翻译结果或None
        """
        try:
            if not batch_task.texts:
                # 空批次，返回空列表
                return []
            
            # 调用翻译函数
            translated = translation_function(
                batch_task.file_task.client,
                batch_task.file_task.provider_name,
                batch_task.texts,
                batch_task.file_task.source_lang,
                batch_task.file_task.target_lang,
                batch_task.file_task.game_profile,
                batch_task.file_task.mod_context,
            )
            
            return translated
            
        except Exception as e:
            self.logger.exception(i18n.t("batch_translation_failed", filename=batch_task.file_task.filename, batch_num=batch_task.batch_index + 1, error=e))
            return None
    
    def _is_file_complete(
        self, 
        filename: str, 
        file_results: Dict[str, List], 
        batch_tasks: List[BatchTask]
    ) -> bool:
        """
        检查文件是否完成
        
        Args:
            filename: 文件名
            file_results: 文件结果字典
            batch_tasks: 批次任务列表
            
        Returns:
            文件是否完成
        """
        if filename not in file_results:
            return False
        
        # 获取该文件的所有批次任务
        file_batch_tasks = [bt for bt in batch_tasks if bt.file_task.filename == filename]
        total_batches = len(file_batch_tasks)
        
        # 检查是否所有批次都完成
        completed_batches = len(file_results[filename])
        return completed_batches == total_batches
    
    def _finalize_file(
        self,
        filename: str,
        file_results: List,
        batch_tasks: List[BatchTask],
        file_builder_function: Callable,
        proofreading_tracker: Any
    ) -> None:
        """
        完成文件处理
        
        Args:
            filename: 文件名
            file_results: 文件结果列表
            batch_tasks: 批次任务列表
            file_builder_function: 文件构建函数
            proofreading_tracker: 校对追踪器
        """
        try:
            # 获取文件任务
            file_task = next(bt.file_task for bt in batch_tasks if bt.file_task.filename == filename)
            
            # 按批次索引排序结果
            sorted_results = sorted(file_results, key=lambda x: x[0])
            all_translated_texts = []
            
            # 合并所有批次结果
            for batch_idx, translated_batch in sorted_results:
                if translated_batch is None:
                    # 批次失败，使用原文
                    batch_task = next(bt for bt in batch_tasks 
                                    if bt.file_task.filename == filename and bt.batch_index == batch_idx)
                    all_translated_texts.extend(batch_task.texts)
                    self.logger.warning(i18n.t("batch_failed_using_original", batch_num=batch_idx + 1, filename=filename))
                else:
                    all_translated_texts.extend(translated_batch)
            
            # 构建目标目录
            dest_dir = self._build_dest_dir(file_task)
            os.makedirs(dest_dir, exist_ok=True)
            
            # 重建并写入文件
            dest_file_path = file_builder_function(
                file_task.original_lines,
                file_task.texts_to_translate,
                all_translated_texts,
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
                
                self.logger.info(i18n.t("file_build_completed", filename=filename))
            
        except Exception as e:
            self.logger.exception(i18n.t("file_completion_processing_failed", filename=filename, error=e))
    
    def _build_dest_dir(self, file_task: FileTask) -> str:
        """
        构建目标目录路径
        
        Args:
            file_task: 文件任务
            
        Returns:
            目标目录路径
        """
        if file_task.is_custom_loc:
            cust_loc_root = os.path.join(file_task.source_dir, file_task.mod_name, "customizable_localization")
            rel = os.path.relpath(file_task.root, cust_loc_root)
            dest_dir = os.path.join(
                file_task.dest_dir,
                file_task.output_folder_name,
                "customizable_localization",
                file_task.target_lang["key"][2:],
                rel,
            )
        else:
            source_loc_folder = file_task.game_profile["source_localization_folder"]
            source_loc_path = os.path.join(file_task.source_dir, file_task.mod_name, source_loc_folder)
            rel = os.path.relpath(file_task.root, source_loc_path)
            dest_dir = os.path.join(
                file_task.dest_dir,
                file_task.output_folder_name,
                source_loc_folder,
                file_task.target_lang["key"][2:],
                rel,
            )
        
        return dest_dir
