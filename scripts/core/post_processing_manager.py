#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后处理验证管理器
负责在翻译完成后自动运行格式验证，并将结果记录到日志和CSV文件中
"""

import os
import csv
import logging
from typing import Dict, List, Optional
from datetime import datetime

from scripts.utils.post_process_validator import PostProcessValidator, ValidationResult, ValidationLevel
from scripts.config import GAME_PROFILES
from scripts.utils import i18n


class PostProcessingManager:
    """后处理验证管理器"""
    
    def __init__(self, game_profile: dict, output_folder: str):
        """
        初始化后处理验证管理器
        
        Args:
            game_profile: 游戏配置信息
            output_folder: 输出文件夹路径
        """
        self.game_profile = game_profile
        self.output_folder = output_folder
        self.game_id = game_profile.get("id", "")
        # 优先使用配置中的 name，其次回退到 id
        self.game_name = game_profile.get("name") or game_profile.get("display_name") or game_profile.get("id") or "Unknown Game"
        self.validator = PostProcessValidator()
        self.logger = logging.getLogger(__name__)

        # 解析并规范化游戏键（转换成验证器需要的数字键 "1"~"5"）
        self.normalized_game_key = self._resolve_game_key(self.game_id)
        
        # 验证结果统计
        self.total_files = 0
        self.valid_files = 0
        self.files_with_issues = 0
        self.total_errors = 0
        self.total_warnings = 0
        self.total_info = 0
        
        # 详细的验证结果
        self.validation_results: Dict[str, List[ValidationResult]] = {}
    
    def run_validation(self, target_lang: dict) -> bool:
        """
        运行后处理验证
        
        Args:
            target_lang: 目标语言信息
            
        Returns:
            bool: 验证是否成功完成
        """
        try:
            # 启动验证
            self.logger.info(i18n.t("post_processing_start"))
            self.logger.info(i18n.t("post_processing_game", game_name=self.game_name))
            
            # 输出验证级别说明
            self._log_validation_levels_explanation()
            
            # 扫描翻译后的文件
            translated_files = self._scan_translated_files(target_lang)
            self.total_files = len(translated_files)
            
            if not translated_files:
                self.logger.info(i18n.t("post_processing_no_issues"))
                return True
            
            self.logger.info(i18n.t("post_processing_scanning", file_count=self.total_files))
            
            # 验证每个文件
            for file_path in translated_files:
                self._validate_single_file(file_path, target_lang)
            
            # 输出验证摘要
            self._log_validation_summary()
            
            self.logger.info(i18n.t("post_processing_validation_complete"))
            return True
            
        except Exception as e:
            self.logger.error(i18n.t("post_processing_validation_error", error=str(e)))
            return False

    def _resolve_game_key(self, game_id: str) -> str:
        """将配置中的字符串ID（如 'victoria3'）映射到验证器使用的数字键（'1'~'5'）。"""
        if not game_id:
            return ""
        # 直接匹配：若传入已经是'1'~'5'
        if game_id in {"1", "2", "3", "4", "5"}:
            return game_id
        # 通过 GAME_PROFILES 反查
        try:
            for numeric_key, profile in GAME_PROFILES.items():
                if profile.get("id") == game_id:
                    return numeric_key
        except Exception:
            pass
        return ""
    
    def _scan_translated_files(self, target_lang: dict) -> List[str]:
        """
        扫描翻译后的文件
        
        Args:
            target_lang: 目标语言信息
            
        Returns:
            List[str]: 文件路径列表
        """
        translated_files = []
        
        # 扫描localization文件夹
        loc_folder = self.game_profile.get("source_localization_folder", "localization")
        target_lang_key = target_lang.get("key", "l_english")
        
        # 构建目标语言文件夹路径
        target_lang_folder = target_lang_key[2:] if target_lang_key.startswith("l_") else target_lang_key
        
        loc_path = os.path.join(self.output_folder, loc_folder, target_lang_folder)
        
        if os.path.exists(loc_path):
            for root, _, files in os.walk(loc_path):
                for file in files:
                    if file.endswith('.yml'):
                        file_path = os.path.join(root, file)
                        translated_files.append(file_path)
        
        # 扫描customizable_localization文件夹（如果存在）
        cust_loc_path = os.path.join(self.output_folder, "customizable_localization", target_lang_folder)
        if os.path.exists(cust_loc_path):
            for root, _, files in os.walk(cust_loc_path):
                for file in files:
                    if file.endswith('.yml'):
                        file_path = os.path.join(root, file)
                        translated_files.append(file_path)
        
        return translated_files
    
    def _extract_translatable_content(self, line: str) -> str:
        """
        从YAML行中提取需要翻译的内容（引号内的内容）
        
        处理各种情况：
        1. key: "value" #注释
        2. key: "He said \"Hello World\" to me" #注释
        3. key: "value"
        4. key: "value" #注释
        5. 无效格式（没有引号）
        
        Args:
            line: YAML行内容
            
        Returns:
            str: 引号内的内容，如果没有找到则返回None
        """
        import re
        
        # 先移除行内注释（#后面的内容）
        # 但要小心不要移除引号内的#符号
        comment_pos = -1
        in_quotes = False
        escape_next = False
        
        for i, char in enumerate(line):
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_quotes = not in_quotes
            elif char == '#' and not in_quotes:
                comment_pos = i
                break
        
        # 如果有注释，移除注释部分
        if comment_pos != -1:
            line = line[:comment_pos].strip()
        
        # 查找 key:0 "value" 或 key: "value" 格式
        # 先找到冒号后的第一个引号
        colon_pos = line.find(':')
        if colon_pos == -1:
            return None
        
        # 从冒号后开始查找引号
        after_colon = line[colon_pos + 1:].strip()
        
        # 查找引号位置（可能在数字后面）
        quote_pos = after_colon.find('"')
        if quote_pos == -1:
            return None
        
        # 从引号位置开始处理
        after_colon = after_colon[quote_pos:]
        
        # 找到第一个引号的位置
        first_quote_pos = after_colon.find('"')
        if first_quote_pos == -1:
            return None
        
        # 从第一个引号后开始查找匹配的结束引号
        content_start = first_quote_pos + 1
        content = ""
        i = content_start
        escape_next = False
        
        while i < len(after_colon):
            char = after_colon[i]
            
            if escape_next:
                # 转义字符，直接添加到内容中
                content += char
                escape_next = False
            elif char == '\\':
                # 反斜杠，标记下一个字符为转义
                content += char
                escape_next = True
            elif char == '"':
                # 找到结束引号
                return content
            else:
                # 普通字符
                content += char
            
            i += 1
        
        # 如果没有找到结束引号，返回None
        return None
    
    def _log_validation_levels_explanation(self):
        """输出验证级别说明，帮助用户理解不同级别的含义"""
        self.logger.info("\n" + "="*60)
        self.logger.info(i18n.t("validation_levels_explanation_title"))
        self.logger.info("="*60)
        
        self.logger.info("\n" + i18n.t("validation_levels_error_title"))
        self.logger.info(i18n.t("validation_levels_error_brackets"))
        self.logger.info(i18n.t("validation_levels_error_concept"))
        self.logger.info(i18n.t("validation_levels_error_variable"))
        self.logger.info(i18n.t("validation_levels_error_icon"))
        
        self.logger.info("\n" + i18n.t("validation_levels_warning_title"))
        self.logger.info(i18n.t("validation_levels_warning_space"))
        self.logger.info(i18n.t("validation_levels_warning_unknown"))
        self.logger.info(i18n.t("validation_levels_warning_unpaired"))
        self.logger.info(i18n.t("validation_levels_warning_color"))
        
        self.logger.info("\n" + i18n.t("validation_levels_info_title"))
        self.logger.info(i18n.t("validation_levels_info_tooltip"))
        self.logger.info(i18n.t("validation_levels_info_scope"))
        
        self.logger.info("\n" + "="*60)
    
    def _validate_single_file(self, file_path: str, target_lang: dict):
        """
        验证单个文件
        
        Args:
            file_path: 文件路径
            target_lang: 目标语言信息
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 按行分割内容
            lines = content.split('\n')
            
            # 验证每一行
            file_results = []
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # 跳过空行和注释行
                if not stripped or stripped.startswith("#"):
                    continue
                
                # 提取引号内的内容进行检查
                translatable_content = self._extract_translatable_content(line)
                if translatable_content:
                    # 只检查引号内的内容
                    results = self.validator.validate_game_text(self.normalized_game_key, translatable_content, line_num)
                    if results:
                        file_results.extend(results)
            
            # 记录文件验证结果
            if file_results:
                self.validation_results[file_path] = file_results
                self.files_with_issues += 1
                
                # 统计问题数量
                for result in file_results:
                    if result.level == ValidationLevel.ERROR:
                        self.total_errors += 1
                    elif result.level == ValidationLevel.WARNING:
                        self.total_warnings += 1
                    elif result.level == ValidationLevel.INFO:
                        self.total_info += 1
            else:
                self.valid_files += 1
                
        except Exception as e:
            self.logger.warning(f"验证文件失败 {file_path}: {e}")

    def attach_results_to_proofreading_tracker(self, proofreading_tracker) -> None:
        """将验证结果合并写入校对进度追踪器的每个文件记录"""
        if not self.validation_results:
            return
        # 构建路径到结果的映射
        results_by_path = self.validation_results
        # 遍历追踪器的文件数据，匹配并写入摘要与详情
        for file_info in getattr(proofreading_tracker, 'files_data', []):
            dest_path = file_info.get('dest_path') or ""
            if not dest_path:
                continue
            results = results_by_path.get(dest_path)
            # 如果无法直接匹配，尝试通过文件名匹配（尽量减少误匹配）
            if results is None:
                filename = os.path.basename(dest_path)
                # 寻找第一个同名文件的结果
                for fp, rs in results_by_path.items():
                    if os.path.basename(fp) == filename:
                        results = rs
                        break
            if not results:
                continue

            # 统计摘要
            errors = sum(1 for r in results if r.level == ValidationLevel.ERROR)
            warnings = sum(1 for r in results if r.level == ValidationLevel.WARNING)
            info = sum(1 for r in results if r.level == ValidationLevel.INFO)
            
            # 添加验证级别说明到摘要中
            level_explanation = i18n.t("validation_csv_level_explanation")
            summary_text = f"Errors: {errors}, Warnings: {warnings}, Info: {info} | {level_explanation}"

            # 组装详情（多行）
            details_lines: List[str] = []
            
            # 在详情开头添加验证级别说明
            details_lines.append(i18n.t("validation_csv_details_header"))
            details_lines.append(i18n.t("validation_csv_details_error"))
            details_lines.append(i18n.t("validation_csv_details_warning"))
            details_lines.append(i18n.t("validation_csv_details_info"))
            details_lines.append("-" * 40)
            
            for r in results:
                level_text = r.level.value.upper()
                line_num = r.line_number if r.line_number is not None else "-"
                if r.details:
                    details_lines.append(f"L{line_num} | {level_text} | {r.message} | {r.details}")
                else:
                    details_lines.append(f"L{line_num} | {level_text} | {r.message}")
            details_text = "\n".join(details_lines)

            # 写入到校对追踪器的标准列
            file_info['proofreading_progress'] = summary_text
            file_info['proofreading_notes'] = details_text
    
    def _generate_validation_report(self, target_lang: dict):
        """
        生成验证报告CSV文件
        
        Args:
            target_lang: 目标语言信息
        """
        try:
            # 构建CSV文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"format_validation_report_{timestamp}.csv"
            csv_path = os.path.join(self.output_folder, csv_filename)
            
            # 写入CSV文件
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['File', 'Line', 'Level', 'Message', 'Details', 'Text Sample']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                # 写入验证结果
                for file_path, results in self.validation_results.items():
                    filename = os.path.basename(file_path)
                    for result in results:
                        writer.writerow({
                            'File': filename,
                            'Line': result.line_number or 'N/A',
                            'Level': result.level.value.upper(),
                            'Message': result.message,
                            'Details': result.details or '',
                            'Text Sample': result.text_sample or ''
                        })
            
            self.logger.info(i18n.t("post_processing_csv_generated", path=csv_path))
            
        except Exception as e:
            self.logger.error(i18n.t("post_processing_csv_generation_failed", error=str(e)))
    
    def _log_validation_summary(self):
        """记录验证摘要到日志"""
        # 计算统计信息
        self.valid_files = self.total_files - self.files_with_issues
        
        # 输出摘要
        if self.files_with_issues == 0:
            self.logger.info(i18n.t("post_processing_no_issues"))
        else:
            self.logger.info(i18n.t("post_processing_summary", 
                                   valid_count=self.valid_files, 
                                   error_count=self.files_with_issues))
            
            # 输出详细问题列表
            self.logger.info(i18n.t("post_processing_issues_found"))
            
            file_index = 1
            for file_path, results in self.validation_results.items():
                filename = os.path.basename(file_path)
                
                # 按行号分组结果
                line_results = {}
                for result in results:
                    line_num = result.line_number or 0
                    if line_num not in line_results:
                        line_results[line_num] = []
                    line_results[line_num].append(result)
                
                # 输出每个文件的问题
                for line_num in sorted(line_results.keys()):
                    self.logger.info(i18n.t("post_processing_file_issue", 
                                           file_index=file_index, 
                                           filename=filename, 
                                           line_number=line_num))
                    
                    for result in line_results[line_num]:
                        if result.details:
                            self.logger.info(i18n.t("post_processing_issue_details_with_details",
                                                   level=result.level.value.upper(),
                                                   message=result.message,
                                                   details=result.details))
                        else:
                            self.logger.info(i18n.t("post_processing_issue_details",
                                                   level=result.level.value.upper(),
                                                   message=result.message))
                
                file_index += 1
    
    def get_validation_stats(self) -> Dict[str, int]:
        """
        获取验证统计信息
        
        Returns:
            Dict[str, int]: 统计信息字典
        """
        return {
            'total_files': self.total_files,
            'valid_files': self.valid_files,
            'files_with_issues': self.files_with_issues,
            'total_errors': self.total_errors,
            'total_warnings': self.total_warnings,
            'total_info': self.total_info
        }
