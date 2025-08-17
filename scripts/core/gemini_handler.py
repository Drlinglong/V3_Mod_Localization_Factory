# scripts/core/gemini_handler.py
import os
import re
import time
import logging
import concurrent.futures
from typing import List
from google import genai

# 【核心修正】统一使用绝对导入
from scripts.utils import i18n
from scripts.config import CHUNK_SIZE, MAX_RETRIES, API_PROVIDERS
from scripts.utils.text_clean import strip_outer_quotes, strip_pl_diacritics
from .glossary_manager import glossary_manager

def initialize_client(api_key: str = None) -> "genai.Client | None":
    """Initializes the Gemini client."""
    if not api_key and not os.getenv("GEMINI_API_KEY"):
        logging.error("API Key not found in environment variables.")
        return None
    try:
        client = genai.Client()
        model_name = API_PROVIDERS["gemini"]["default_model"]
        logging.info(f"Gemini client initialized successfully, using model: {model_name}")
        return client
    except Exception as e:
        logging.exception(f"Error initializing Gemini client: {e}")
        return None

def translate_single_text(
    client: "genai.Client",
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
    
    prompt = (
        base_prompt
        + f"CRITICAL CONTEXT: The mod's theme is '{mod_context}'. Use this to ensure accuracy.\n"
        + glossary_prompt_part
        + "CRITICAL FORMATTING: Your response MUST ONLY contain the translated text. "
        "DO NOT include explanations, pinyin, or any other text.\n"
        'For example, if the input is "Flavor Pack", your output must be "风味包" and nothing else.\n\n'
        f'Translate this: "{text}"'
    )

    try:
        model_name = API_PROVIDERS["gemini"]["default_model"]
        
        # 根据配置决定是否启用思考功能
        
        if API_PROVIDERS["gemini"]["enable_thinking"]:
            # 启用思考功能（可能增加成本）
            from google.genai import types
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=API_PROVIDERS["gemini"]["thinking_budget"]
                    )
                )
            )
            logging.info(i18n.t("single_translation_thinking_enabled", budget=API_PROVIDERS["gemini"]["thinking_budget"]))
        else:
            # 禁用思考功能（节约成本）
            from google.genai import types
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            logging.info(i18n.t("single_translation_thinking_disabled"))
        
        translated = strip_outer_quotes(response.text.strip())

        # Post-processing for EU4 Polish
        if game_profile.get("strip_pl_diacritics") and target_lang["code"] == "pl":
            translated = strip_pl_diacritics(translated)

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
            
            format_prompt_part = (
                "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
                f"{len(chunk)}. "
                "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
                "DO NOT merge, add, or omit lines. DO NOT add any explanations. "
                "There are two types of special syntax:\n"
                "1.  **Variables** like `$variable$`, `[Concept('key', '$concept_name$')]`, `[SCOPE.some.Function]`. You MUST preserve these variables completely. DO NOT translate any text inside them.\n"
                "2.  **Formatting Tags** like `#R ... #!`, `§Y...§!`. You MUST preserve the tags themselves (e.g., `#R`, `#!`), but you SHOULD translate the plain text that is inside them.\n\n"
                "3.  **Icon Tags** like `@prestige!`, `£minerals£`. These are variables. You MUST preserve them completely. DO NOT translate any text inside them.\n\n"
                "4.  **Internal Keys** like `mm_strategic_region` or `com_topbar_interests`. These are strings that often contain underscores and no spaces. They are code references and MUST NOT be translated. Preserve them completely.\n\n"
                "Preserve all internal newlines (\\n).\n\n"
                "--- INPUT LIST ---\n"
                f"{numbered_list}\n"
                "--- END OF INPUT LIST ---"
            )
            prompt = base_prompt + context_prompt_part + glossary_prompt_part + format_prompt_part

            model_name = API_PROVIDERS["gemini"]["default_model"]
            
            # 根据配置决定是否启用思考功能
            
            if API_PROVIDERS["gemini"]["enable_thinking"]:
                # 启用思考功能（可能增加成本）
                from google.genai import types
                response = client.models.generate_content(
                    model=model_name, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(
                            thinking_budget=API_PROVIDERS["gemini"]["thinking_budget"]
                        )
                    )
                )
                logging.info(i18n.t("batch_thinking_enabled", batch_num=batch_num, budget=API_PROVIDERS["gemini"]["thinking_budget"]))
            else:
                # 禁用思考功能（节约成本）
                from google.genai import types
                response = client.models.generate_content(
                    model=model_name, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=0)
                    )
                )
                logging.info(i18n.t("batch_thinking_disabled", batch_num=batch_num))
            
            translated_chunk = re.findall(
                r'^\s*\d+\.\s*"?(.+?)"?$', response.text, re.MULTILINE | re.DOTALL
            )

            if len(translated_chunk) == len(chunk):
                translated_chunk = [strip_outer_quotes(t) for t in translated_chunk]
                if game_profile.get("strip_pl_diacritics") and target_lang["code"] == "pl":
                    translated_chunk = [strip_pl_diacritics(t) for t in translated_chunk]
                return translated_chunk

            logging.error(i18n.t("mismatch_error", original_count=len(chunk), translated_count=len(translated_chunk)))

        except Exception as e:
            logging.exception(i18n.t("api_call_error", error=e))

        if attempt < MAX_RETRIES - 1:
            delay = (attempt + 1) * 2
            logging.warning(i18n.t("retrying_batch", batch_num=batch_num, attempt=attempt + 1, max_retries=MAX_RETRIES, delay=delay))
            time.sleep(delay)

    return None

def translate_texts_in_batches(
    client: "genai.Client",
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
    if len(texts_to_translate) <= CHUNK_SIZE:
        return _translate_chunk(client, texts_to_translate, source_lang, target_lang, game_profile, mod_context, 1)

    # 将文本分成批次
    chunks = [texts_to_translate[i : i + CHUNK_SIZE] for i in range(0, len(texts_to_translate), CHUNK_SIZE)]
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