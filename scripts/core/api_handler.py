# scripts/core/api_handler.py
import os
import re
import time
import logging
import concurrent.futures
from scripts.utils import i18n
from scripts.app_settings import CHUNK_SIZE, MAX_RETRIES, API_PROVIDERS
from scripts.utils.text_clean import strip_pl_diacritics, strip_outer_quotes

# 【核心修正】动态导入，避免不必要的依赖要求
# 移除静态导入，改为按需动态导入

def get_handler(provider_name):
    """这是一个"工厂函数"，根据名称返回对应的API处理器模块。"""
    try:
        if provider_name == "openai":
            from . import openai_handler
            return openai_handler
        elif provider_name == "qwen":
            from . import qwen_handler
            return qwen_handler
        elif provider_name == "gemini":
            from . import gemini_handler
            return gemini_handler
        elif provider_name == "gemini_cli":
            from . import gemini_cli_handler
            return gemini_cli_handler
        else:
            # 默认返回Gemini
            from . import gemini_handler
            return gemini_handler
    except ImportError as e:
        logging.error(f"Failed to import {provider_name} handler: {e}")
        logging.error(f"Please install required dependencies for {provider_name}")
        return None

def initialize_client(provider_name, model_name=None):
    """
    为选定的API供应商初始化客户端。
    """
    handler = get_handler(provider_name)
    if not handler:
        logging.error(f"Handler for {provider_name} is not available")
        return None, None
    
    # CLI处理器不需要API密钥
    if provider_name == "gemini_cli":
        provider_config = API_PROVIDERS.get(provider_name, {})
        cli_path = provider_config.get("cli_path", "gemini")

        # 如果未指定模型，则使用默认模型
        if not model_name:
            model_name = provider_config.get("default_model", "gemini-2.5-pro")

        client = handler.GeminiCLIHandler(cli_path=cli_path, model=model_name)
        return client, provider_name
        
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
    if not handler:
        logging.error(f"Handler for {provider_name} is not available")
        return None
    return handler.translate_texts_in_batches(client, provider_name, texts_to_translate, source_lang, target_lang, game_profile, mod_context)

def translate_single_text(client, provider_name, text, task_description, mod_name, source_lang, target_lang, mod_context, game_profile):
    """调用当前选定API供应商的单条文本翻译函数。"""
    handler = get_handler(provider_name)
    if not handler:
        logging.error(f"Handler for {provider_name} is not available")
        return None
    return handler.translate_single_text(client, provider_name, text, task_description, mod_name, source_lang, target_lang, mod_context, game_profile)

def translate_single_batch(client, provider_name, texts, source_lang, target_lang, game_profile, mod_context):
    """调用当前选定API供应商的单批次翻译函数。"""
    handler = get_handler(provider_name)
    if not handler:
        logging.error(f"Handler for {provider_name} is not available")
        return None
    
    # 直接调用单批次翻译函数，而不是批量翻译函数
    if hasattr(handler, '_translate_chunk'):
        return handler._translate_chunk(client, texts, source_lang, target_lang, game_profile, mod_context, 1)
    else:
        # 如果没有单批次函数，回退到批量翻译
        return handler.translate_texts_in_batches(client, provider_name, texts, source_lang, target_lang, game_profile, mod_context)

def translate_single_batch_with_batch_num(client, provider_name, texts, source_lang, target_lang, game_profile, mod_context, batch_num):
    """调用当前选定API供应商的单批次翻译函数，并传递批次编号。"""
    handler = get_handler(provider_name)
    if not handler:
        logging.error(f"Handler for {provider_name} is not available")
        return None
    
    # 直接调用单批次翻译函数，传递正确的批次编号
    if hasattr(handler, '_translate_chunk'):
        return handler._translate_chunk(client, texts, source_lang, target_lang, game_profile, mod_context, batch_num)
    else:
        # 如果没有单批次函数，回退到批量翻译
        return handler.translate_texts_in_batches(client, provider_name, texts, source_lang, target_lang, game_profile, mod_context)