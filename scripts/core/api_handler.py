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
    
def translate_single_text(client, text, task_description, mod_name, source_lang, target_lang, mod_context):
    """
    【V2.9 修正版】调用API翻译单条文本。
    签名已更新，可以正确接收 mod_context 参数。
    """
    if not text:
        return ""
        
    if task_description == "mod name":
        print_key = "translating_mod_name"
    else:
        print_key = "translating_mod_desc"
    
    print(i18n.t(print_key, text=text[:30]))

    # 从游戏档案中获取正确的prompt模板
    # 我们假设 game_profile 已经被正确传递，或者在这里用一个通用模板
    # 为避免引入更多错误，我们先用一个通用模板
    prompt = (
        "You are a direct, one-to-one translation engine. "
        f"The text you are translating is for a game mod with the following context: '{mod_context}'. Use this thematic context to ensure accuracy.\n"
        f"Translate the following {task_description} from {source_lang['name']} to {target_lang['name']}.\n"
        "CRITICAL: Your response MUST ONLY contain the translated text. "
        "DO NOT include explanations, pinyin, English, or any other conversational text or formatting.\n"
        f"For example, if the input is 'Flavor Pack' in English, and the target is Simplified Chinese, your output must be '风味包' and nothing else.\n\n"
        f"Translate this: \"{text}\""
    )
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text.strip().strip('"')
    except Exception as e:
        print(i18n.t("api_call_error", error=e))
        return text
    
    
def translate_texts_in_batches(client, texts_to_translate, source_lang, target_lang, game_profile, mod_context):
    """
    【最终版】分批次翻译文本列表。
    集成了游戏档案(game_profile)和Mod主题上下文(mod_context)以生成动态指令。
    """
    all_translated_texts = []
    
    for i in range(0, len(texts_to_translate), CHUNK_SIZE):
        chunk = texts_to_translate[i:i + CHUNK_SIZE]
        batch_num = i//CHUNK_SIZE + 1
        
        print(i18n.t("processing_batch", batch_num=batch_num, chunk_size=len(chunk)))
        
        numbered_list = "\n".join([f"{j+1}. \"{text}\"" for j, text in enumerate(chunk)])
        
        # 1. 从游戏档案中获取基础的Prompt模板
        base_prompt = game_profile['prompt_template'].format(
            source_lang_name=source_lang['name'],
            target_lang_name=target_lang['name']
        )
        
        # 2. 准备Mod主题上下文的指令部分
        context_prompt_part = (
            f"CRITICAL CONTEXT: The mod you are translating is '{mod_context}'. "
            "Use this information to ensure all translations are thematically appropriate.\n"
        )

        # 3. 准备后续的、严格的格式指令
        format_prompt_part = (
            "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
            f"{len(chunk)}. "
            "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
            "DO NOT merge, add, or omit lines. DO NOT add any explanations. "
            "Preserve all special placeholders like $...$ or [...] and internal newlines (\\n).\n\n"
            "--- INPUT LIST ---\n"
            f"{numbered_list}\n"
            "--- END OF INPUT LIST ---"
        )
        
        # 4. 将所有部分拼接成最终的、完整的Prompt
        prompt = base_prompt + context_prompt_part + format_prompt_part
        
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