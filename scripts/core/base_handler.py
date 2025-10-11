# scripts/core/base_handler.py
import time
import logging
from abc import ABC, abstractmethod

from scripts.utils import i18n
from scripts.app_settings import MAX_RETRIES, FALLBACK_FORMAT_PROMPT
from scripts.core.parallel_processor import BatchTask
from scripts.utils.punctuation_handler import generate_punctuation_prompt
from scripts.core.glossary_manager import glossary_manager
from scripts.utils.response_parser import parse_json_response, ParsingFailedAfterRepairError


class BaseApiHandler(ABC):
    """【基类】API Handler 抽象基类，封装通用逻辑。"""

    def __init__(self, provider_name: str):
        """
        通用的构造函数。
        """
        self.provider_name = provider_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = self.initialize_client()

    @abstractmethod
    def initialize_client(self):
        """【必须由子类实现】初始化并返回特定于该Provider的API客户端。"""
        pass

    @abstractmethod
    def _call_api(self, client: any, prompt: str) -> str:
        """【必须由子类实现】执行对特定API的调用并返回原始文本响应。"""
        pass

    def _build_prompt(self, task: BatchTask) -> str:
        """
        【通用逻辑】根据任务构建完整的翻译提示。
        """
        chunk = task.texts
        source_lang = task.file_task.source_lang
        target_lang = task.file_task.target_lang
        game_profile = task.file_task.game_profile
        mod_context = task.file_task.mod_context
        batch_num = task.batch_index + 1

        numbered_list = "\n".join(f'{j + 1}. "{txt}"' for j, txt in enumerate(chunk))

        effective_target_lang_name = target_lang.get("custom_name", target_lang["name"]) if target_lang.get("is_shell") else target_lang["name"]

        base_prompt = game_profile["prompt_template"].format(
            source_lang_name=source_lang["name"],
            target_lang_name=effective_target_lang_name,
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
                self.logger.info(i18n.t("batch_translation_glossary_injected", batch_num=batch_num, count=len(relevant_terms)))

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
            format_prompt_part = FALLBACK_FORMAT_PROMPT.format(
                chunk_size=len(chunk),
                numbered_list=numbered_list
            )

        punctuation_prompt_part = f"\nPUNCTUATION CONVERSION:\n{punctuation_prompt}\n" if punctuation_prompt else ""

        prompt = base_prompt + context_prompt_part + glossary_prompt_part + format_prompt_part + punctuation_prompt_part
        return prompt

    def _parse_response(self, response: str, expected_count: int) -> list[str] | None:
        """【通用逻辑】调用通用解析器来解析API响应。"""
        return parse_json_response(response, expected_count)

    def translate_batch(self, task: BatchTask) -> BatchTask:
        """
        【核心工作流】处理单个批次的翻译任务，包含重试逻辑。
        """
        prompt = self._build_prompt(task)
        batch_num = task.batch_index + 1

        for attempt in range(MAX_RETRIES):
            try:
                raw_response = self._call_api(self.client, prompt)
                translated_texts = self._parse_response(raw_response, len(task.texts))

                if translated_texts and len(translated_texts) == len(task.texts):
                    task.translated_texts = translated_texts
                    self.logger.debug(i18n.t("batch_success", batch_num=batch_num, attempt=attempt + 1))
                    return task
                else:
                    self.logger.warning(
                        f"Response parsing failed for batch {batch_num} on attempt {attempt + 1}. "
                        f"Expected {len(task.texts)} items, got {len(translated_texts) if translated_texts else 0}."
                    )

            except ParsingFailedAfterRepairError as e:
                self.logger.warning(f"Response parsing failed for batch {batch_num} on attempt {attempt + 1}, even after repair. Error: {e}")

            except Exception as e:
                self.logger.exception(f"API call failed for batch {batch_num} on attempt {attempt + 1}: {e}")

            if attempt < MAX_RETRIES - 1:
                delay = (attempt + 1) * 2
                self.logger.warning(i18n.t("retrying_batch", batch_num=batch_num, attempt=attempt + 1, max_retries=MAX_RETRIES, delay=delay))
                time.sleep(delay)

        self.logger.error(f"Batch {batch_num} failed after {MAX_RETRIES} attempts.")
        task.translated_texts = None
        return task

    def _build_single_text_prompt(self, text: str, task_description: str, mod_name: str, source_lang: dict, target_lang: dict, mod_context: str, game_profile: dict) -> str:
        """【通用逻辑】为单条文本构建专用的翻译提示。"""
        base_prompt = game_profile["single_prompt_template"].format(
            mod_name=mod_name,
            task_description=task_description,
            source_lang_name=source_lang["name"],
            target_lang_name=target_lang["name"],
        )

        glossary_prompt_part = ""
        if glossary_manager.current_game_glossary:
            relevant_terms = glossary_manager.extract_relevant_terms(
                [text], source_lang["code"], target_lang["code"]
            )
            if relevant_terms:
                glossary_prompt_part = glossary_manager.create_dynamic_glossary_prompt(
                    relevant_terms, source_lang["code"], target_lang["code"]
                ) + "\n\n"

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
        return prompt

    def translate_single_text(self, text: str, task_description: str, mod_name: str, source_lang: dict, target_lang: dict, mod_context: str, game_profile: dict) -> str:
        """【通用工作流】翻译单条文本，带一次调用，失败则返回原文。"""
        if not text:
            return ""

        prompt = self._build_single_text_prompt(text, task_description, mod_name, source_lang, target_lang, mod_context, game_profile)

        try:
            raw_response = self._call_api(self.client, prompt)
            # Simple cleanup for single text
            translated_text = raw_response.strip().strip('"')
            return translated_text
        except Exception as e:
            self.logger.exception(f"Single text translation failed for '{text[:30]}...': {e}")
            return text # Fallback to original text
