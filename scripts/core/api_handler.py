# scripts/core/api_handler.py

import os
import re
import time
from google import genai
from utils import i18n
from config import MODEL_NAME, CHUNK_SIZE

def initialize_client():
    """初始化Gemini客户端。"""
    if not os.getenv('GEMINI_API_KEY'):
        print("API Key not found in environment variables.")
        return None
    try:
        client = genai.Client()
        print(f"Gemini client initialized successfully, using model: {MODEL_NAME}")
        return client
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return None
def translate_single_text(client, text, task_description, mod_name, source_lang, target_lang):
    """
    【V2.7】调用API翻译单条文本，已完全支持多语言。
    """
    if not text:
        return ""
        
    if task_description == "mod name":
        print_key = "translating_mod_name"
    else:
        print_key = "translating_mod_desc"
    
    print(i18n.t(print_key, text=text[:30]))

    # 【核心修改】将Prompt完全模板化，以支持任何语言对
    prompt = (
        "You are a direct, one-to-one translation engine. "
        f"The text you are translating is for a Victoria 3 game mod named '{mod_name}'. "
        f"Translate the following {task_description} from {source_lang['name']} to {target_lang['name']}.\n"
        "CRITICAL: Your response MUST ONLY contain the translated text. "
        "DO NOT include explanations, pinyin, English, or any other conversational text or formatting.\n"
        "For example, if the input is 'Flavor Pack' in English, and the target is Simplified Chinese, your output must be '风味包' and nothing else.\n\n"
        f"Translate this: \"{text}\""
    )
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text.strip().strip('"')
    except Exception as e:
        print(i18n.t("api_call_error", error=e))
        return text
    
    
def translate_texts_in_batches(client, texts_to_translate, source_lang, target_lang):
    """
    分批次翻译文本列表，现在支持指定源语言和目标语言。
    """
    all_translated_texts = []
    
    for i in range(0, len(texts_to_translate), CHUNK_SIZE):
        chunk = texts_to_translate[i:i + CHUNK_SIZE]
        batch_num = i//CHUNK_SIZE + 1
        
        print(i18n.t("processing_batch", batch_num=batch_num, chunk_size=len(chunk)))
        
        numbered_list = "\n".join([f"{j+1}. \"{text}\"" for j, text in enumerate(chunk)])
        
        # 【核心修改】将Prompt模板化，以支持任何语言
        prompt = (
            f"You are a professional translator for the game Victoria 3. "
            f"Translate the following numbered list of texts from {source_lang['name']} to {target_lang['name']}.\n"
            "CRITICAL: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
            f"{len(chunk)}. "
            "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
            "DO NOT merge, add, or omit lines. DO NOT add any explanations. "
            "Preserve all special placeholders like $...$ or [...] and internal newlines (\\n).\n\n"
            "--- INPUT LIST ---\n"
            f"{numbered_list}\n"
            "--- END OF INPUT LIST ---"
        )
        
        # ... (后续API调用和解析逻辑无变化) ...
        
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
            translated_chunk = re.findall(r'^\s*\d+\.\s*"?(.+?)"?$', response.text, re.DOTALL | re.MULTILINE)

            if len(translated_chunk) != len(chunk):
                print(i18n.t("mismatch_error", original_count=len(chunk), translated_count=len(translated_chunk)))
                print(f"AI Response Preview: {response.text[:300]}...")
                return None

            all_translated_texts.extend(translated_chunk)
            if len(texts_to_translate) > CHUNK_SIZE:
                time.sleep(1)

        except Exception as e:
            print(i18n.t("api_call_error", error=e))
            return None
            
    return all_translated_texts