# scripts/core/qwen_handler.py
import os
import re
import time
import concurrent.futures
from openai import OpenAI
import logging

from scripts.utils import i18n
from scripts.config import CHUNK_SIZE, MAX_RETRIES, API_PROVIDERS
from scripts.utils.text_clean import strip_pl_diacritics, strip_outer_quotes
from scripts.utils.punctuation_handler import generate_punctuation_prompt
from .glossary_manager import glossary_manager

# Alias required by the audit.py script for compatibility
_strip_pl_diacritics = strip_pl_diacritics  # noqa: N816

def initialize_client(api_key: str = None) -> "OpenAI | None":
    """Initializes the Qwen client using OpenAI-compatible interface."""
    if not api_key and not os.getenv("DASHSCOPE_API_KEY"):
        logging.error("API Key not found in environment variables.")
        return None
    try:
        # 使用阿里云百炼的OpenAI兼容接口
        provider_config = API_PROVIDERS.get("qwen", {})
        base_url = provider_config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        model_name = provider_config.get("default_model", "qwen-plus")
        logging.info(f"Qwen client initialized successfully, using model: {model_name}")
        logging.info(f"Using base URL: {base_url}")
        return client
    except Exception as e:
        logging.exception(f"Error initializing Qwen client: {e}")
        return None

def translate_single_text(
    client: "OpenAI",
    provider_name: str,  # 添加缺失的provider_name参数
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
        model_name = API_PROVIDERS["qwen"]["default_model"]
        
        # 根据配置决定是否启用思考功能
        
        # 构建prompt，根据配置决定是否添加/no_think
        if not API_PROVIDERS["qwen"]["enable_thinking"]:
            # 禁用思考功能：在prompt末尾添加/no_think
            prompt += " /no_think"
            logging.info(i18n.t("qwen_single_translation_thinking_disabled"))
        else:
            logging.info(i18n.t("qwen_single_translation_thinking_enabled"))
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional translator for game mods."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3,  # 降低随机性，提高翻译一致性
            extra_body={"enable_thinking": API_PROVIDERS["qwen"]["enable_thinking"]}  # 通过API参数控制思考功能
        )
        translated = strip_outer_quotes(response.choices[0].message.content.strip())

        # Post-processing for EU4 Polish
        if game_profile.get("strip_pl_diacritics") and target_lang["code"] == "pl":
            translated = _strip_pl_diacritics(translated)

        return translated
    except Exception as e:
        logging.exception(i18n.t("api_call_error", error=e))
        return text

def _translate_chunk(client, chunk, source_lang, target_lang, game_profile, mod_context, batch_num):
    """[Worker Function] Translates a single chunk of text, with retry logic."""
    for attempt in range(MAX_RETRIES):
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

            model_name = API_PROVIDERS["qwen"]["default_model"]
            
            # 根据配置决定是否启用思考功能
            
            # 构建prompt，根据配置决定是否添加/no_think
            if not API_PROVIDERS["qwen"]["enable_thinking"]:
                # 禁用思考功能：在prompt末尾添加/no_think
                prompt += " /no_think"
                logging.info(i18n.t("qwen_batch_thinking_disabled", batch_num=batch_num))
            else:
                logging.info(i18n.t("qwen_batch_thinking_enabled", batch_num=batch_num))
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a professional translator for game mods."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3,  # 降低随机性，提高翻译一致性
                extra_body={"enable_thinking": API_PROVIDERS["qwen"]["enable_thinking"]}  # 通过API参数控制思考功能
            )
            
            # 使用与OpenAI和Gemini一致的解析方法
            translated_chunk = re.findall(
                r'^\s*\d+\.\s*"?(.+?)"?$', response.choices[0].message.content, re.MULTILINE | re.DOTALL
            )

            if len(translated_chunk) == len(chunk):
                translated_chunk = [strip_outer_quotes(t) for t in translated_chunk]
                # Post-processing for EU4 Polish
                if game_profile.get("strip_pl_diacritics") and target_lang["code"] == "pl":
                    translated_chunk = [_strip_pl_diacritics(t) for t in translated_chunk]
                return translated_chunk

            logging.error(i18n.t("mismatch_error", original_count=len(chunk), translated_count=len(translated_chunk)))

        except Exception as e:
            logging.exception(i18n.t("api_call_error", error=e))

        if attempt < MAX_RETRIES - 1:
            delay = (attempt + 1) * 2
            logging.warning(i18n.t("retrying_batch", batch_num=batch_num, attempt=attempt + 1, max_retries=MAX_RETRIES, delay=delay))
            time.sleep(delay)

    # 修复：与OpenAI和Gemini一致，失败时返回None
    return None

def translate_texts_in_batches(
    client: "OpenAI",
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
    if not texts_to_translate:
        return []

    logging.info(i18n.t("extracted_texts", count=len(texts_to_translate)))
    
    if len(texts_to_translate) <= CHUNK_SIZE:
        return _translate_chunk(client, texts_to_translate, source_lang, target_lang, game_profile, mod_context, 1)

    # 将文本分成批次
    chunks = [texts_to_translate[i:i + CHUNK_SIZE] for i in range(0, len(texts_to_translate), CHUNK_SIZE)]
    logging.info(i18n.t("parallel_processing_start", count=len(chunks)))

    # 串行处理所有批次，避免嵌套线程池
    # 注意：真正的并行处理由调用者（ParallelProcessor）负责
    results = []
    for i, chunk in enumerate(chunks):
        try:
            result = _translate_chunk(client, chunk, source_lang, target_lang, game_profile, mod_context, i + 1)
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
