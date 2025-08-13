# scripts/core/qwen_handler.py
import os
import re
import time
import concurrent.futures
from openai import OpenAI
import logging

from scripts.utils import i18n
from scripts.config import CHUNK_SIZE, MAX_RETRIES, API_PROVIDERS
from utils.text_clean import strip_pl_diacritics, strip_outer_quotes

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
    prompt = (
        base_prompt
        + f"CRITICAL CONTEXT: The mod's theme is '{mod_context}'. Use this to ensure accuracy.\n"
        "CRITICAL FORMATTING: Your response MUST ONLY contain the translated text. "
        "DO NOT include explanations, pinyin, or any other text.\n"
        'For example, if the input is "Flavor Pack", your output must be "风味包" and nothing else.\n\n'
        f'Translate this: "{text}"'
    )

    try:
        model_name = API_PROVIDERS["qwen"]["default_model"]
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional translator for game mods."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3  # 降低随机性，提高翻译一致性
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
                "--- END INPUT LIST ---\n\n"
                "Now provide your numbered translation list:"
            )

            full_prompt = base_prompt + context_prompt_part + format_prompt_part

            model_name = API_PROVIDERS["qwen"]["default_model"]
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a professional translator for game mods."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=4000,
                temperature=0.3  # 降低随机性，提高翻译一致性
            )

            response_text = response.choices[0].message.content.strip()
            translated_lines = _parse_numbered_response(response_text, len(chunk))

            if len(translated_lines) == len(chunk):
                # Post-processing for EU4 Polish
                if game_profile.get("strip_pl_diacritics") and target_lang["code"] == "pl":
                    translated_lines = [_strip_pl_diacritics(line) for line in translated_lines]
                return translated_lines
            else:
                logging.warning(
                    f"Batch {batch_num}: Response count mismatch. Expected {len(chunk)}, got {len(translated_lines)}"
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logging.error(i18n.t("mismatch_error", original_count=len(chunk), translated_count=len(translated_lines)))
                    return chunk  # Return original text as fallback

        except Exception as e:
            logging.error(f"Batch {batch_num} failed on attempt {attempt + 1}/{MAX_RETRIES}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                logging.error(i18n.t("api_call_error", error=e))
                return chunk  # Return original text as fallback

    return chunk  # Fallback

def _parse_numbered_response(response_text: str, expected_count: int) -> list[str]:
    """Parses the numbered response from the API and extracts translated texts."""
    lines = response_text.strip().split('\n')
    translated_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try to match numbered patterns like "1. text", "1) text", "1- text", etc.
        match = re.match(r'^\d+[\.\)\-\s]+(.+)$', line)
        if match:
            translated_text = match.group(1).strip()
            # Remove quotes if present
            translated_text = strip_outer_quotes(translated_text)
            translated_lines.append(translated_text)
    
    # If we didn't get the expected count, try alternative parsing
    if len(translated_lines) != expected_count:
        logging.warning(f"Numbered parsing failed, trying alternative methods. Got {len(translated_lines)}, expected {expected_count}")
        
        # Alternative: split by newlines and filter out empty lines
        alternative_lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        if len(alternative_lines) == expected_count:
            translated_lines = [strip_outer_quotes(line) for line in alternative_lines]
        else:
            logging.warning(f"Alternative parsing also failed. Got {len(alternative_lines)}, expected {expected_count}")
    
    return translated_lines

def translate_texts_in_batches(
    client: "OpenAI",
    texts_to_translate: list[str],
    source_lang: dict,
    target_lang: dict,
    game_profile: dict,
    mod_context: str,
) -> list[str]:
    """
    Translates a list of texts in batches using the Qwen API.
    """
    if not texts_to_translate:
        return []

    logging.info(i18n.t("extracted_texts", count=len(texts_to_translate)))
    
    # Split texts into chunks
    chunks = [texts_to_translate[i:i + CHUNK_SIZE] for i in range(0, len(texts_to_translate), CHUNK_SIZE)]
    
    if len(chunks) > 1:
        logging.info(i18n.t("parallel_processing_start", count=len(chunks)))
    
    all_translated = []
    
    # Process chunks in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_chunk = {
            executor.submit(_translate_chunk, client, chunk, source_lang, target_lang, game_profile, mod_context, i + 1): chunk
            for i, chunk in enumerate(chunks)
        }
        
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk = future_to_chunk[future]
            try:
                translated_chunk = future.result()
                all_translated.extend(translated_chunk)
            except Exception as e:
                logging.error(f"Chunk processing failed: {e}")
                all_translated.extend(chunk)  # Use original text as fallback
    
    if len(chunks) > 1:
        logging.info(i18n.t("parallel_processing_end"))
    
    return all_translated
