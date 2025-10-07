# scripts/core/gemini_cli_handler.py
import os
import re
import time
import json
import logging
import tempfile
import subprocess
import concurrent.futures
from datetime import datetime
from typing import List, Optional, Dict

from scripts.core.parallel_processor import BatchTask
from scripts.utils.response_parser import parse_json_response

# 【核心修正】统一使用绝对导入
from scripts.utils import i18n
from scripts.app_settings import CHUNK_SIZE, MAX_RETRIES, API_PROVIDERS, GEMINI_CLI_CHUNK_SIZE, GEMINI_CLI_MAX_RETRIES
from scripts.utils.text_clean import strip_outer_quotes, strip_pl_diacritics
from scripts.utils.punctuation_handler import generate_punctuation_prompt
from .glossary_manager import glossary_manager

logger = logging.getLogger(__name__)

class GeminiCLIHandler:
    """Gemini CLI处理器"""
    
    def __init__(self, cli_path: str = "gemini", model: str = "gemini-2.5-pro"):
        self.cli_path = cli_path
        self.model = model
        self.daily_calls = 0
        self.call_history = []
        self._verify_cli_availability()
    
    def _verify_cli_availability(self):
        """验证Gemini CLI是否可用"""
        try:
            # 使用PowerShell执行策略检查CLI可用性
            cmd = [
                "powershell", "-Command", 
                f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; {self.cli_path} --version"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(i18n.t("gemini_cli_available", version=result.stdout.strip()))
            else:
                logger.warning(i18n.t("gemini_cli_version_check_failed", error=result.stderr))
        except FileNotFoundError:
            raise Exception(i18n.t("gemini_cli_not_found", cli_path=self.cli_path))
        except subprocess.TimeoutExpired:
            raise Exception(i18n.t("gemini_cli_timeout"))
    
    def _execute_prompt(self, prompt: str) -> str:
        """执行单个prompt并返回结果"""
        try:
            # logger.info(f"开始CLI翻译调用 (第{self.daily_calls + 1}次)")  # 已注释，减少日志噪音
            start_time = time.time()
            
            # 使用临时文件避免命令行参数过长的问题
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # 调用Gemini CLI - 使用headless模式和PowerShell执行策略
                # 使用管道将prompt内容传递给stdin，避免参数注入
                cmd = [
                    "powershell", "-Command", 
                    f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; Get-Content '{temp_file}' -Raw | {self.cli_path} --model {self.model} --output-format json"
                ]
                
                # 【核心修复】强制清空环境变量，只保留必要的系统变量
                # 明确设置GEMINI_API_KEY为空，强制gemini CLI使用OAuth认证而不是API key
                clean_env = {
                    'PATH': os.environ.get('PATH', ''),
                    'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                    'TEMP': os.environ.get('TEMP', ''),
                    'TMP': os.environ.get('TMP', ''),
                    'USERPROFILE': os.environ.get('USERPROFILE', ''),
                    'APPDATA': os.environ.get('APPDATA', ''),
                    'LOCALAPPDATA': os.environ.get('LOCALAPPDATA', ''),
                    'PROGRAMDATA': os.environ.get('PROGRAMDATA', ''),
                    'WINDIR': os.environ.get('WINDIR', ''),
                    'COMSPEC': os.environ.get('COMSPEC', ''),
                    'PATHEXT': os.environ.get('PATHEXT', ''),
                    'PSModulePath': os.environ.get('PSModulePath', ''),
                    'GEMINI_API_KEY': '',  # 明确设置为空，强制使用OAuth认证
                }
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5分钟超时，适应Gemini 2.5 Pro的慢速处理
                    encoding='utf-8',
                    env=clean_env  # 【关键修复】使用清理后的环境变量
                )
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                # 调试信息生成模块 - 已注释，避免对用户造成视觉轰炸
                # 如需调试，可取消注释以下代码块
                # debug_file = f"cli_single_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                # with open(debug_file, 'w', encoding='utf-8') as f:
                #     f.write("=== CLI单个翻译原始输出 ===\n")
                #     f.write(f"返回码: {result.returncode}\n")
                #     f.write(f"输出长度: {len(result.stdout)} 字符\n")
                #     f.write(f"错误输出: {result.stderr}\n")
                #     f.write("=" * 50 + "\n")
                #     f.write(result.stdout)
                #     f.write("\n" + "=" * 50 + "\n")
                # 
                # logger.info(f"CLI单个翻译原始输出已保存到: {debug_file}")
                # logger.info(f"CLI原始输出长度: {len(result.stdout)} 字符")
                # logger.info(f"CLI原始输出:")
                # logger.info("-" * 30)
                # logger.info(result.stdout)
                # logger.info("-" * 30)
                
                translated_text = self._parse_response(result.stdout)
                
                self.daily_calls += 1
                self.call_history.append({
                    'timestamp': datetime.now(),
                    'type': 'single',
                    'duration': elapsed_time,
                    'success': True
                })
                
                logger.info(i18n.t("gemini_cli_translation_success", elapsed_time=elapsed_time))
                return translated_text
            else:
                error_msg = i18n.t("gemini_cli_call_failed", error=result.stderr)
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except subprocess.TimeoutExpired:
            logger.error(i18n.t("gemini_cli_call_timeout"))
            raise Exception(i18n.t("gemini_cli_call_timeout"))
        except Exception as e:
            logger.error(i18n.t("gemini_cli_translation_exception", error=str(e)))
            raise

    def _execute_batch_prompt(self, prompt: str, expected_count: int) -> List[str]:
        """执行批量prompt并返回结果列表"""
        try:
            # logger.info(f"开始CLI批量翻译调用，文本数量: {expected_count}")  # 已注释，减少日志噪音
            start_time = time.time()
            
            # 使用临时文件避免命令行参数过长的问题
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # 调用Gemini CLI - 使用快速模式和PowerShell执行策略
                # 使用管道将prompt内容传递给stdin，避免参数注入
                cmd = [
                    "powershell", "-Command", 
                    f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; Get-Content '{temp_file}' -Raw | {self.cli_path} --model {self.model} --output-format json"
                ]
                
                # 【核心修复】强制清空环境变量，只保留必要的系统变量
                # 明确设置GEMINI_API_KEY为空，强制gemini CLI使用OAuth认证而不是API key
                clean_env = {
                    'PATH': os.environ.get('PATH', ''),
                    'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                    'TEMP': os.environ.get('TEMP', ''),
                    'TMP': os.environ.get('TMP', ''),
                    'USERPROFILE': os.environ.get('USERPROFILE', ''),
                    'APPDATA': os.environ.get('APPDATA', ''),
                    'LOCALAPPDATA': os.environ.get('LOCALAPPDATA', ''),
                    'PROGRAMDATA': os.environ.get('PROGRAMDATA', ''),
                    'WINDIR': os.environ.get('WINDIR', ''),
                    'COMSPEC': os.environ.get('COMSPEC', ''),
                    'PATHEXT': os.environ.get('PATHEXT', ''),
                    'PSModulePath': os.environ.get('PSModulePath', ''),
                    'GEMINI_API_KEY': '',  # 明确设置为空，强制使用OAuth认证
                }
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5分钟超时，适应Gemini 2.5 Pro的慢速处理
                    encoding='utf-8',
                    env=clean_env  # 【关键修复】使用清理后的环境变量
                )
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                # 调试信息生成模块 - 已注释，避免对用户造成视觉轰炸
                # 如需调试，可取消注释以下代码块
                # debug_file = f"cli_batch_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                # with open(debug_file, 'w', encoding='utf-8') as f:
                #     f.write("=== CLI批量翻译原始输出 ===\n")
                #     f.write(f"返回码: {result.returncode}\n")
                #     f.write(f"输出长度: {len(result.stdout)} 字符\n")
                #     f.write(f"错误输出: {result.stderr}\n")
                #     f.write("=" * 50 + "\n")
                #     f.write(result.stdout)
                #     f.write("\n" + "=" * 50 + "\n")
                # 
                # logger.info(f"CLI批量翻译原始输出已保存到: {debug_file}")
                # logger.info(f"CLI原始输出长度: {len(result.stdout)} 字符")
                
                translated_texts = self._parse_batch_response(result.stdout, expected_count)
                
                self.daily_calls += 1
                self.call_history.append({
                    'timestamp': datetime.now(),
                    'type': 'batch',
                    'duration': elapsed_time,
                    'success': True,
                    'count': len(translated_texts)
                })
                
                logger.info(i18n.t("gemini_cli_batch_success", elapsed_time=elapsed_time))
                return translated_texts
            else:
                error_msg = i18n.t("gemini_cli_call_failed", error=result.stderr)
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except subprocess.TimeoutExpired:
            logger.error(i18n.t("gemini_cli_call_timeout"))
            raise Exception(i18n.t("gemini_cli_call_timeout"))
        except Exception as e:
            logger.error(i18n.t("gemini_cli_batch_exception", error=str(e)))
            raise

    def _parse_response(self, response: str) -> str:
        """解析CLI JSON响应"""
        try:
            # 尝试解析JSON响应
            response_data = json.loads(response)
            
            # 检查是否有错误
            if 'error' in response_data:
                error_msg = response_data['error'].get('message', 'Unknown error')
                raise Exception(i18n.t("gemini_cli_return_error", error=error_msg))
            
            # 检查是否有候选响应
            if 'stats' in response_data and 'models' in response_data['stats']:
                models_stats = response_data['stats']['models']
                for model_name, model_stats in models_stats.items():
                    if 'tokens' in model_stats and model_stats['tokens'].get('candidates', 0) == 0:
                        # 【增强调试】如果因为安全设置等原因被阻止，提供更详细的错误
                        finish_reason = response_data.get('finishReason', '未知')
                        error_message = i18n.t("gemini_cli_no_candidates", model_name=model_name)
                        error_message += i18n.t("gemini_cli_finish_reason", finish_reason=finish_reason)
                        
                        if finish_reason == 'SAFETY':
                            safety_ratings = response_data.get('safetyRatings', [])
                            error_message += i18n.t("gemini_cli_safety_ratings", safety_ratings=safety_ratings)
                            logger.error(i18n.t("gemini_cli_safety_warning"))
                        
                        error_message += i18n.t("gemini_cli_prompt_too_long")
                        
                        logger.error(error_message)
                        raise Exception(error_message)
            
            # 提取响应内容
            if 'response' in response_data:
                response_text = response_data['response'].strip()
                if response_text == "?????" or len(response_text) < 2:
                    raise Exception(i18n.t("gemini_cli_invalid_response"))
                return response_text
            else:
                raise Exception(i18n.t("gemini_cli_response_format_error"))
                
        except json.JSONDecodeError:
            # 如果不是JSON格式，回退到文本解析
            logger.warning(i18n.t("gemini_cli_not_json"))
            lines = response.strip().split('\n')
            
            # 查找翻译结果（通常在最后几行）
            for line in reversed(lines):
                line = line.strip()
                if line and not line.startswith('>') and not line.startswith('Gemini'):
                    return line
            
            # 如果没有找到合适的行，返回整个响应
            return response.strip()

    def _parse_batch_response(self, response: str, expected_count: int) -> List[str]:

        """[REFACTORED] Delegates parsing to the centralized JSON response parser."""

        # The raw response from the CLI's stdout is passed directly.

        return parse_json_response(response, expected_count)

    def _analyze_problematic_content(self, lines, empty_lines, invalid_lines, short_lines):
        """分析问题内容，尝试找出导致翻译失败的具体原因"""
        try:
            # 收集所有问题行号
            all_problem_lines = set(empty_lines)
            all_problem_lines.update([line_num for line_num, _ in invalid_lines])
            all_problem_lines.update([line_num for line_num, _ in short_lines])
            
            if not all_problem_lines:
                return
            
            logger.warning(i18n.t("gemini_cli_analyze_lines", count=len(all_problem_lines)))
            
            # 分析问题行的特征
            suspicious_patterns = []
            for line_num in sorted(all_problem_lines):
                # 找到对应的原始输入行（需要从调用上下文获取）
                # 这里我们只能分析响应中的问题
                for i, line in enumerate(lines):
                    line = line.strip()
                    if re.match(r'^\d+\.\s*', line):
                        number = int(re.match(r'^(\d+)\.\s*', line).group(1))
                        if number == line_num:
                            content = re.sub(r'^\d+\.\s*', '', line).strip()
                            content = content.strip('"\'')
                            
                            # 分析问题特征
                            if line_num in empty_lines:
                                suspicious_patterns.append(i18n.t("gemini_cli_empty_line", line_num=line_num))
                            elif line_num in [ln for ln, _ in invalid_lines]:
                                invalid_content = next(content for ln, content in invalid_lines if ln == line_num)
                                if invalid_content == 'WARNING: Source localization entry is incomplete':
                                    suspicious_patterns.append(i18n.t("gemini_cli_incomplete_line", line_num=line_num))
                                else:
                                    suspicious_patterns.append(i18n.t("gemini_cli_invalid_placeholder", line_num=line_num, invalid_content=invalid_content))
                            elif line_num in [ln for ln, _ in short_lines]:
                                short_content = next(content for ln, content in short_lines if ln == line_num)
                                suspicious_patterns.append(i18n.t("gemini_cli_short_line", line_num=line_num, short_content=short_content))
                            break
            
            # 输出分析结果
            if suspicious_patterns:
                logger.warning(i18n.t("gemini_cli_problem_details"))
                for pattern in suspicious_patterns[:10]:  # 只显示前10个
                    logger.warning(f"   {pattern}")
                if len(suspicious_patterns) > 10:
                    logger.warning(i18n.t("gemini_cli_more_problems", count=len(suspicious_patterns) - 10))
            
            # 提供针对性建议
            logger.warning(i18n.t("gemini_cli_suggestions"))
            if empty_lines:
                logger.warning(i18n.t("gemini_cli_empty_suggestion", count=len(empty_lines)))
            
            # 分别统计不同类型的无效内容
            warning_lines = [ln for ln, content in invalid_lines if content == 'WARNING: Source localization entry is incomplete']
            other_invalid_lines = [ln for ln, content in invalid_lines if content != 'WARNING: Source localization entry is incomplete']
            
            if warning_lines:
                logger.warning(i18n.t("gemini_cli_incomplete_suggestion", count=len(warning_lines)))
            if other_invalid_lines:
                logger.warning(i18n.t("gemini_cli_invalid_suggestion", count=len(other_invalid_lines)))
            if short_lines:
                logger.warning(i18n.t("gemini_cli_short_suggestion", count=len(short_lines)))
            
            logger.warning(i18n.t("gemini_cli_solutions"))
            logger.warning(i18n.t("gemini_cli_solution_1"))
            logger.warning(i18n.t("gemini_cli_solution_2"))
            logger.warning(i18n.t("gemini_cli_solution_3"))
            logger.warning(i18n.t("gemini_cli_solution_4"))
            
        except Exception as e:
            logger.warning(i18n.t("gemini_cli_analysis_failed", error=e))

    def get_usage_stats(self):
        """获取使用统计"""
        return {
            'daily_calls': self.daily_calls,
            'call_history': self.call_history
        }


def initialize_client(api_key: str = None, model_name: str = None) -> "GeminiCLIHandler | None":
    """Initializes the Gemini CLI client."""
    try:
        provider_config = API_PROVIDERS.get("gemini_cli", {})
        cli_path = provider_config.get("cli_path", "gemini")
        
        if model_name is None:
            model_name = provider_config.get("default_model", "gemini-2.5-pro")
            
        client = GeminiCLIHandler(cli_path=cli_path, model=model_name)
        logging.info(f"Gemini CLI client initialized successfully")
        return client
    except Exception as e:
        logging.exception(f"Error initializing Gemini CLI client: {e}")
        return None


def translate_single_text(
    client: GeminiCLIHandler,
    provider_name: str,
    text: str,
    task_description: str,
    mod_name: str,
    source_lang: dict,
    target_lang: dict,
    mod_context: str,
    game_profile: dict,
) -> str:
    """Translates a single text string (e.g., mod name or description)."""
    if not text:
        return ""

    print_key = "translating_mod_name" if task_description == "mod name" else "translating_mod_desc"
    logging.info(i18n.t(print_key, text=text[:30]))

    # 使用name_en字段避免非ASCII字符在subprocess调用中的编码问题
    # 这是为了解决韩语、中文、日语等语言名称在CLI调用链中的编码损坏问题
    source_lang_name = source_lang.get("name_en", source_lang["name"])
    target_lang_name = target_lang.get("name_en", target_lang["name"])
    
    base_prompt = game_profile["single_prompt_template"].format(
        mod_name=mod_name,
        task_description=task_description,
        source_lang_name=source_lang_name,
        target_lang_name=target_lang_name,
    )
    
    # ───────────── 词典提示注入 ─────────────
    glossary_prompt_part = ""
    if glossary_manager.current_game_glossary:
        # 提取相关术语
        relevant_terms = glossary_manager.extract_relevant_terms(
            [text], source_lang["code"], target_lang["code"]
        )
        if relevant_terms:
            glossary_prompt_part = glossary_manager.create_dynamic_glossary_prompt(
                relevant_terms, source_lang["code"], target_lang["code"]
            ) + "\n\n"
            logging.info(i18n.t("single_translation_glossary_injected", count=len(relevant_terms)))
    
    # 智能生成标点符号转换提示词
    punctuation_prompt = generate_punctuation_prompt(
        source_lang["code"], 
        target_lang["code"]
    )
    
    prompt = (
        base_prompt
        + f"CRITICAL CONTEXT: The mod's theme is '{mod_context}'. Use this to ensure accuracy.\n"
        + glossary_prompt_part
        + "CRITICAL FORMATTING: Your response MUST ONLY contain the translated text. "
        "DO NOT include explanations, pinyin, or any other text.\n"
        'For example, if the input is "Flavor Pack", your output must be "风味包" and nothing else.\n\n'
        + (f"PUNCTUATION CONVERSION:\n{punctuation_prompt}\n\n" if punctuation_prompt else "")
        + f'Translate this: "{text}"'
    )

    try:
        translated_text = client._execute_prompt(prompt)
        
        # 清理翻译结果
        cleaned_text = strip_outer_quotes(translated_text)
        
        logging.info(i18n.t("gemini_cli_translation_complete", text=cleaned_text[:30]))
        return cleaned_text
        
    except Exception as e:
        logging.error(i18n.t("gemini_cli_translation_failed", error=str(e)))
        return text  # 返回原文


def translate_texts_in_batches(
    client: GeminiCLIHandler,
    provider_name: str,
    texts_to_translate: list[str],
    source_lang: dict,
    target_lang: dict,
    game_profile: dict,
    mod_context: str,
) -> "list[str] | None":
    """
    [Foreman Function] Translates a list of texts in batches.
    IMPORTANT: This function does NOT create its own thread pool to avoid thread explosion.
    It either processes sequentially or relies on the caller's thread pool.
    """
    if len(texts_to_translate) <= GEMINI_CLI_CHUNK_SIZE:
        return _translate_cli_chunk(client, texts_to_translate, source_lang, target_lang, game_profile, mod_context, 1)

    # 将文本分成批次
    chunks = [texts_to_translate[i : i + GEMINI_CLI_CHUNK_SIZE] for i in range(0, len(texts_to_translate), GEMINI_CLI_CHUNK_SIZE)]
    logging.info(i18n.t("parallel_processing_start", count=len(chunks)))

    # 串行处理所有批次，避免嵌套线程池
    # 注意：真正的并行处理由调用者（ParallelProcessor）负责
    results = []
    for i, chunk in enumerate(chunks):
        try:
            result = _translate_cli_chunk(client, chunk, source_lang, target_lang, game_profile, mod_context, i + 1)
            results.append(result)
        except Exception as e:
            logging.exception(f"Batch {i + 1} failed with error: {e}")
            results.append(None)

    # 合并结果
    all_translated_texts: list[str] = []
    has_failures = False
    for i, translated_chunk in enumerate(results):
        if translated_chunk is None:
            has_failures = True
            logging.warning(i18n.t("warning_batch_failed", batch_num=i + 1))
            original_chunk = chunks[i]
            all_translated_texts.extend(original_chunk)
        else:
            all_translated_texts.extend(translated_chunk)
    
    if has_failures:
        logging.error(i18n.t("warning_partial_failure"))

    logging.info(i18n.t("parallel_processing_end"))
    return all_translated_texts


def _translate_chunk(client: GeminiCLIHandler, task: BatchTask) -> BatchTask:
    """[Worker Function] Translates a single chunk of text using CLI, with retry logic."""
    return _translate_cli_chunk(client, task)

def _translate_cli_chunk(client: GeminiCLIHandler, task: BatchTask) -> BatchTask:
    """[Worker Function] Translates a single chunk of text using CLI, with retry logic."""
    # Extract data from BatchTask
    chunk = task.texts
    source_lang = task.file_task.source_lang
    target_lang = task.file_task.target_lang
    game_profile = task.file_task.game_profile
    mod_context = task.file_task.mod_context
    batch_num = task.batch_index + 1  # batch_index is 0-based

    for attempt in range(GEMINI_CLI_MAX_RETRIES):
        try:
            numbered_list = "\n".join(f'{j + 1}. "{txt}"' for j, txt in enumerate(chunk))
            source_lang_name = source_lang.get("name_en", source_lang["name"])
            target_lang_name = target_lang.get("name_en", target_lang["name"])
            
            base_prompt = game_profile["prompt_template"].format(
                source_lang_name=source_lang_name,
                target_lang_name=target_lang_name,
            )
            context_prompt_part = (
                f"CRITICAL CONTEXT: The mod you are translating is '{mod_context}'. "
                "Use this information to ensure all translations are thematically appropriate.\n"
            )
            
            glossary_prompt_part = ""
            if glossary_manager.current_game_glossary:
                relevant_terms = glossary_manager.extract_relevant_terms(
                    chunk, source_lang["code"], target_lang["code"]
                )
                if relevant_terms:
                    glossary_prompt_part = glossary_manager.create_dynamic_glossary_prompt(
                        relevant_terms, source_lang["code"], target_lang["code"]
                    ) + "\n\n"
                    logging.info(i18n.t("batch_translation_glossary_injected", batch_num=batch_num, count=len(relevant_terms)))
            
            punctuation_prompt = generate_punctuation_prompt(
                source_lang["code"], 
                target_lang["code"]
            )
            
            if "format_prompt" in game_profile:
                format_prompt_part = game_profile["format_prompt"].format(
                    chunk_size=len(chunk),
                    numbered_list=numbered_list
                )
            else:
                from scripts.app_settings import FALLBACK_FORMAT_PROMPT
                format_prompt_part = FALLBACK_FORMAT_PROMPT.format(
                    chunk_size=len(chunk),
                    numbered_list=numbered_list
                )
            
            punctuation_prompt_part = f"\nPUNCTUATION CONVERSION:\n{punctuation_prompt}\n" if punctuation_prompt else ""
            
            prompt = base_prompt + context_prompt_part + glossary_prompt_part + format_prompt_part + punctuation_prompt_part
            
            translated_texts = client._execute_batch_prompt(prompt, len(chunk))
            
            if translated_texts and len(translated_texts) == len(chunk):
                cleaned_texts = [strip_outer_quotes(text) for text in translated_texts]
                task.translated_texts = cleaned_texts
                return task
            else:
                logging.warning(f"CLI batch {batch_num} returned {len(translated_texts) if translated_texts else 0} results, expected {len(chunk)}")
                if attempt < GEMINI_CLI_MAX_RETRIES - 1:
                    continue
                else:
                    task.translated_texts = None # Indicate failure
                    return task
        except Exception as e:
            logging.exception(f"CLI batch {batch_num} attempt {attempt + 1} failed: {e}")
            if attempt < GEMINI_CLI_MAX_RETRIES - 1:
                continue
            else:
                task.translated_texts = None # Indicate failure
                return task

    task.translated_texts = None # Indicate failure
    return task