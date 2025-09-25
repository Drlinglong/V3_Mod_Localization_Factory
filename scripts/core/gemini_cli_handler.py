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

# 【核心修正】统一使用绝对导入
from scripts.utils import i18n
from scripts.config import CHUNK_SIZE, MAX_RETRIES, API_PROVIDERS, GEMINI_CLI_CHUNK_SIZE, GEMINI_CLI_MAX_RETRIES
from scripts.utils.text_clean import strip_outer_quotes, strip_pl_diacritics
from scripts.utils.punctuation_handler import generate_punctuation_prompt
from .glossary_manager import glossary_manager

logger = logging.getLogger(__name__)

class GeminiCLIHandler:
    """Gemini CLI处理器"""
    
    def __init__(self, cli_path: str = "gemini"):
        self.cli_path = cli_path
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
                logger.info(f"Gemini CLI 可用: {result.stdout.strip()}")
            else:
                logger.warning(f"Gemini CLI 版本检查失败: {result.stderr}")
        except FileNotFoundError:
            raise Exception(f"Gemini CLI 未找到，请确保已安装: {self.cli_path}")
        except subprocess.TimeoutExpired:
            raise Exception("Gemini CLI 响应超时，请检查安装状态")
    
    def _execute_prompt(self, prompt: str) -> str:
        """执行单个prompt并返回结果"""
        try:
            logger.info(f"开始CLI翻译调用 (第{self.daily_calls + 1}次)")
            start_time = time.time()
            
            # 使用临时文件避免命令行参数过长的问题
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # 调用Gemini CLI - 使用headless模式和PowerShell执行策略
                # 使用位置参数传递prompt，确保每次调用都是无状态的
                cmd = [
                    "powershell", "-Command", 
                    f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; {self.cli_path} (Get-Content '{temp_file}' -Raw) --model gemini-2.5-pro --output-format json"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5分钟超时，适应Gemini 2.5 Pro的慢速处理
                    encoding='utf-8'
                )
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                # 保存原始输出
                debug_file = f"cli_single_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write("=== CLI单个翻译原始输出 ===\n")
                    f.write(f"返回码: {result.returncode}\n")
                    f.write(f"输出长度: {len(result.stdout)} 字符\n")
                    f.write(f"错误输出: {result.stderr}\n")
                    f.write("=" * 50 + "\n")
                    f.write(result.stdout)
                    f.write("\n" + "=" * 50 + "\n")
                
                logger.info(f"CLI单个翻译原始输出已保存到: {debug_file}")
                logger.info(f"CLI原始输出长度: {len(result.stdout)} 字符")
                logger.info(f"CLI原始输出:")
                logger.info("-" * 30)
                logger.info(result.stdout)
                logger.info("-" * 30)
                
                translated_text = self._parse_response(result.stdout)
                
                self.daily_calls += 1
                self.call_history.append({
                    'timestamp': datetime.now(),
                    'type': 'single',
                    'duration': elapsed_time,
                    'success': True
                })
                
                logger.info(f"CLI翻译成功，耗时 {elapsed_time:.2f}秒")
                return translated_text
            else:
                error_msg = f"CLI调用失败: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except subprocess.TimeoutExpired:
            logger.error("CLI调用超时")
            raise Exception("CLI调用超时")
        except Exception as e:
            logger.error(f"CLI翻译异常: {str(e)}")
            raise

    def _execute_batch_prompt(self, prompt: str, expected_count: int) -> List[str]:
        """执行批量prompt并返回结果列表"""
        try:
            logger.info(f"开始CLI批量翻译调用，文本数量: {expected_count}")
            start_time = time.time()
            
            # 使用临时文件避免命令行参数过长的问题
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # 调用Gemini CLI - 使用headless模式和PowerShell执行策略
                # 使用位置参数传递prompt，确保每次调用都是无状态的
                cmd = [
                    "powershell", "-Command", 
                    f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; {self.cli_path} (Get-Content '{temp_file}' -Raw) --model gemini-2.5-pro --output-format json"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5分钟超时，适应Gemini 2.5 Pro的慢速处理
                    encoding='utf-8'
                )
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                # 保存原始输出
                debug_file = f"cli_batch_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write("=== CLI批量翻译原始输出 ===\n")
                    f.write(f"返回码: {result.returncode}\n")
                    f.write(f"输出长度: {len(result.stdout)} 字符\n")
                    f.write(f"错误输出: {result.stderr}\n")
                    f.write("=" * 50 + "\n")
                    f.write(result.stdout)
                    f.write("\n" + "=" * 50 + "\n")
                
                logger.info(f"CLI批量翻译原始输出已保存到: {debug_file}")
                logger.info(f"CLI原始输出长度: {len(result.stdout)} 字符")
                
                translated_texts = self._parse_batch_response(result.stdout, expected_count)
                
                self.daily_calls += 1
                self.call_history.append({
                    'timestamp': datetime.now(),
                    'type': 'batch',
                    'duration': elapsed_time,
                    'success': True,
                    'count': len(translated_texts)
                })
                
                logger.info(f"CLI批量翻译成功，耗时 {elapsed_time:.2f}秒")
                return translated_texts
            else:
                error_msg = f"CLI调用失败: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except subprocess.TimeoutExpired:
            logger.error("CLI调用超时")
            raise Exception("CLI调用超时")
        except Exception as e:
            logger.error(f"CLI批量翻译异常: {str(e)}")
            raise

    def _parse_response(self, response: str) -> str:
        """解析CLI JSON响应"""
        try:
            # 尝试解析JSON响应
            response_data = json.loads(response)
            
            # 检查是否有错误
            if 'error' in response_data:
                error_msg = response_data['error'].get('message', 'Unknown error')
                raise Exception(f"CLI返回错误: {error_msg}")
            
            # 检查是否有候选响应
            if 'stats' in response_data and 'models' in response_data['stats']:
                models_stats = response_data['stats']['models']
                for model_name, model_stats in models_stats.items():
                    if 'tokens' in model_stats and model_stats['tokens'].get('candidates', 0) == 0:
                        raise Exception(f"Gemini模型 {model_name} 没有生成任何候选响应 (candidates: 0)，可能是prompt过长或内容不当")
            
            # 提取响应内容
            if 'response' in response_data:
                response_text = response_data['response'].strip()
                if response_text == "?????" or len(response_text) < 2:
                    raise Exception("CLI返回了无效的响应内容")
                return response_text
            else:
                raise Exception("CLI响应格式异常：缺少response字段")
                
        except json.JSONDecodeError:
            # 如果不是JSON格式，回退到文本解析
            logger.warning("CLI响应不是JSON格式，尝试文本解析")
            lines = response.strip().split('\n')
            
            # 查找翻译结果（通常在最后几行）
            for line in reversed(lines):
                line = line.strip()
                if line and not line.startswith('>') and not line.startswith('Gemini'):
                    return line
            
            # 如果没有找到合适的行，返回整个响应
            return response.strip()

    def _parse_batch_response(self, response: str, expected_count: int) -> List[str]:
        """解析批量翻译JSON响应"""
        logger.info(f"开始解析批量响应，期望数量: {expected_count}")
        
        try:
            # 尝试解析JSON响应
            logger.info("尝试解析JSON响应...")
            response_data = json.loads(response)
            logger.info("JSON解析成功")
            
            # 检查是否有错误
            if 'error' in response_data:
                error_msg = response_data['error'].get('message', 'Unknown error')
                logger.error(f"CLI返回错误: {error_msg}")
                raise Exception(f"CLI返回错误: {error_msg}")
            
            # 检查是否有候选响应
            if 'stats' in response_data and 'models' in response_data['stats']:
                models_stats = response_data['stats']['models']
                for model_name, model_stats in models_stats.items():
                    if 'tokens' in model_stats and model_stats['tokens'].get('candidates', 0) == 0:
                        logger.error(f"Gemini模型 {model_name} 没有生成任何候选响应 (candidates: 0)")
                        raise Exception(f"Gemini模型 {model_name} 没有生成任何候选响应 (candidates: 0)，可能是prompt过长或内容不当")
            
            # 提取响应内容
            if 'response' in response_data:
                response_text = response_data['response'].strip()
                logger.info(f"响应文本长度: {len(response_text)} 字符")
                logger.info(f"响应文本前200字符: {response_text[:200]}")
                
                # 解析批量翻译结果 - 按照编号列表格式
                translations = []
                lines = response_text.split('\n')
                logger.info(f"响应文本行数: {len(lines)}")
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    logger.debug(f"处理第{i+1}行: {line[:50]}...")
                    
                    # 查找编号开头的行
                    if re.match(r'^\d+\.\s*', line):
                        # 提取翻译内容（去掉编号）
                        translation = re.sub(r'^\d+\.\s*', '', line).strip()
                        # 去掉可能的引号
                        translation = translation.strip('"\'')
                        if translation:
                            translations.append(translation)
                            logger.debug(f"找到翻译 {len(translations)}: {translation[:30]}...")
                
                logger.info(f"解析完成，找到 {len(translations)} 个翻译")
                
                if len(translations) == expected_count:
                    logger.info("批量翻译解析完整")
                    return translations
                elif len(translations) > 0:
                    logger.warning(f"批量翻译解析不完整，期望{expected_count}个，实际得到{len(translations)}个")
                    # 用原文填充缺失的翻译
                    while len(translations) < expected_count:
                        translations.append("")  # 或者使用原文
                    return translations[:expected_count]
                else:
                    logger.warning("批量翻译解析失败，尝试备用解析方法")
                    raise Exception("批量翻译解析失败")
            else:
                raise Exception("CLI响应格式异常：缺少response字段")
                
        except json.JSONDecodeError:
            logger.warning("CLI响应不是JSON格式，尝试文本解析")
            lines = response.strip().split('\n')
            
            # 查找翻译结果（通常在最后几行）
            translations = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('>') and not line.startswith('Gemini'):
                    # 尝试提取编号列表
                    if re.match(r'^\d+\.\s*', line):
                        translation = re.sub(r'^\d+\.\s*', '', line).strip()
                        translation = translation.strip('"\'')
                        if translation:
                            translations.append(translation)
            
            if translations:
                logger.info(f"备用解析方法找到 {len(translations)} 个可能的翻译")
                return translations[:expected_count]
            else:
                raise Exception("无法解析CLI响应")

    def get_usage_stats(self):
        """获取使用统计"""
        return {
            'daily_calls': self.daily_calls,
            'call_history': self.call_history
        }


def initialize_client(api_key: str = None) -> "GeminiCLIHandler | None":
    """Initializes the Gemini CLI client."""
    try:
        provider_config = API_PROVIDERS.get("gemini_cli", {})
        cli_path = provider_config.get("cli_path", "gemini")
        client = GeminiCLIHandler(cli_path=cli_path)
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

    base_prompt = game_profile["single_prompt_template"].format(
        mod_name=mod_name,
        task_description=task_description,
        source_lang_name=source_lang["name"],
        target_lang_name=target_lang["name"],
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
        
        logging.info(f"CLI翻译完成: {cleaned_text[:30]}")
        return cleaned_text
        
    except Exception as e:
        logging.error(f"CLI翻译失败: {str(e)}")
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


def _translate_cli_chunk(client: GeminiCLIHandler, chunk: list[str], source_lang: dict, target_lang: dict, 
                        game_profile: dict, mod_context: str, batch_num: int) -> "list[str] | None":
    """[Worker Function] Translates a single chunk of text using CLI, with retry logic."""
    for attempt in range(GEMINI_CLI_MAX_RETRIES):
        try:
            numbered_list = "\n".join(f'{j + 1}. "{txt}"' for j, txt in enumerate(chunk))
            base_prompt = game_profile["prompt_template"].format(
                source_lang_name=source_lang["name"],
                target_lang_name=target_lang["name"],
            )
            context_prompt_part = (
                f"CRITICAL CONTEXT: The mod you are translating is '{mod_context}'. "
                "Use this information to ensure all translations are thematically appropriate.\n"
            )
            
            # ───────────── 词典提示注入 ─────────────
            glossary_prompt_part = ""
            if glossary_manager.current_game_glossary:
                # 提取相关术语
                relevant_terms = glossary_manager.extract_relevant_terms(
                    chunk, source_lang["code"], target_lang["code"]
                )
                if relevant_terms:
                    glossary_prompt_part = glossary_manager.create_dynamic_glossary_prompt(
                        relevant_terms, source_lang["code"], target_lang["code"]
                    ) + "\n\n"
                    logging.info(i18n.t("batch_translation_glossary_injected", batch_num=batch_num, count=len(relevant_terms)))
            
            # 智能生成标点符号转换提示词
            punctuation_prompt = generate_punctuation_prompt(
                source_lang["code"], 
                target_lang["code"]
            )
            
            # 优先使用游戏特定的format_prompt，如果没有则使用保底选项
            if "format_prompt" in game_profile:
                format_prompt_part = game_profile["format_prompt"].format(
                    chunk_size=len(chunk),
                    numbered_list=numbered_list
                )
            else:
                # 导入保底选项
                from scripts.config import FALLBACK_FORMAT_PROMPT
                format_prompt_part = FALLBACK_FORMAT_PROMPT.format(
                    chunk_size=len(chunk),
                    numbered_list=numbered_list
                )
            
            # 构建punctuation_prompt_part
            punctuation_prompt_part = f"\nPUNCTUATION CONVERSION:\n{punctuation_prompt}\n" if punctuation_prompt else ""
            
            prompt = base_prompt + context_prompt_part + glossary_prompt_part + format_prompt_part + punctuation_prompt_part
            
            translated_texts = client._execute_batch_prompt(prompt, len(chunk))
            
            if translated_texts and len(translated_texts) == len(chunk):
                cleaned_texts = [strip_outer_quotes(text) for text in translated_texts]
                return cleaned_texts
            else:
                logging.warning(f"CLI batch {batch_num} returned {len(translated_texts) if translated_texts else 0} results, expected {len(chunk)}")
                if attempt < GEMINI_CLI_MAX_RETRIES - 1:
                    continue
                else:
                    return None
        except Exception as e:
            logging.exception(f"CLI batch {batch_num} attempt {attempt + 1} failed: {e}")
            if attempt < GEMINI_CLI_MAX_RETRIES - 1:
                continue
            else:
                return None
    return None