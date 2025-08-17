# scripts/core/api_handler.py
import os
import re
import time
import logging
import concurrent.futures
from scripts.utils import i18n
from scripts.config import CHUNK_SIZE, MAX_RETRIES, API_PROVIDERS
from scripts.utils.text_clean import strip_pl_diacritics, strip_outer_quotes

# 【核心修正】直接从当前(core)目录导入我们所有的"引擎模块"
from . import gemini_handler
from . import openai_handler
from . import qwen_handler

def get_handler(provider_name):
    """这是一个"工厂函数"，根据名称返回对应的API处理器模块。"""
    if provider_name == "openai":
        return openai_handler
    elif provider_name == "qwen":
        return qwen_handler
    
    # 默认返回Gemini
    return gemini_handler

def initialize_client(provider_name):
    """
    为选定的API供应商初始化客户端。
    """
    handler = get_handler(provider_name)
    provider_config = API_PROVIDERS.get(provider_name, {})
    api_key_env = provider_config.get("api_key_env")
    api_key = os.getenv(api_key_env) if api_key_env else None
    
    if not api_key:
        logging.error(f"API key environment variable '{api_key_env}' not set.")
        return None, None
        
    client = handler.initialize_client(api_key)
    return client, provider_name

def translate_texts_in_batches(client, provider_name, texts_to_translate, source_lang, target_lang, game_profile, mod_context):
    """调用当前选定API供应商的批量翻译函数。"""
    handler = get_handler(provider_name)
    return handler.translate_texts_in_batches(client, texts_to_translate, source_lang, target_lang, game_profile, mod_context)

def translate_single_text(client, provider_name, text, task_description, mod_name, source_lang, target_lang, mod_context, game_profile):
    """调用当前选定API供应商的单条文本翻译函数。"""
    handler = get_handler(provider_name)
    return handler.translate_single_text(client, provider_name, text, task_description, mod_name, source_lang, target_lang, mod_context, game_profile)