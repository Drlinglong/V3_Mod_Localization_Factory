# scripts/core/api_handler.py
import os
import re
import time
import logging
import concurrent.futures
from typing import Any

from scripts.core.parallel_processor import BatchTask
from typing import Any

from scripts.core.parallel_processor import BatchTask
from scripts.utils import i18n
from scripts.app_settings import CHUNK_SIZE, MAX_RETRIES, API_PROVIDERS
from scripts.utils.text_clean import strip_pl_diacritics, strip_outer_quotes

# 【核心修正】动态导入，避免不必要的依赖要求
# 移除静态导入，改为按需动态导入

def get_handler(provider_name):
    """这是一个"工厂函数"，根据名称返回对应的API处理器模块。"""
    # 检测并设置便携式环境
    _setup_portable_environment()
    
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

def _setup_portable_environment():
    """
    检测并设置便携式环境
    如果检测到便携式环境，将packages目录添加到Python路径中
    """
    import sys
    import os
    
    # 检测便携式环境：检查是否存在packages目录
    packages_dir = None
    
    # 检查当前目录
    if os.path.exists('packages'):
        packages_dir = os.path.abspath('packages')
    # 检查上级目录（当在app目录下运行时）
    elif os.path.exists('../packages'):
        packages_dir = os.path.abspath('../packages')
    
    if packages_dir and packages_dir not in sys.path:
        sys.path.insert(0, packages_dir)
        logging.info(f"便携式环境检测到，已添加依赖包路径: {packages_dir}")

def initialize_client(provider_name, model_name: str = None):
    """
    为选定的API供应商初始化客户端。
    """
    handler = get_handler(provider_name)
    if not handler:
        logging.error(f"Handler for {provider_name} is not available")
        return None, None
    
    # CLI处理器不需要API密钥
    if provider_name == "gemini_cli":
        client = handler.initialize_client(model_name=model_name)
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

def translate_single_batch(task: BatchTask) -> BatchTask:
    """(Modernized) Calls the single-batch translation function of the current API provider."""
    provider_name = task.file_task.provider_name
    client = task.file_task.client
    handler = get_handler(provider_name)
    if not handler:
        logging.error(f"Handler for {provider_name} is not available")
        task.translated_texts = None
        return task

    if hasattr(handler, '_translate_chunk'):
        # Modern handlers expect the full BatchTask object
        return handler._translate_chunk(client, task)
    else:
        # Fallback for legacy handlers that don't accept BatchTask
        logging.warning(f"Handler for {provider_name} does not have a modern `_translate_chunk` that accepts BatchTask. Falling back to legacy text-based translation.")
        translated_texts = handler.translate_texts_in_batches(
            client,
            provider_name,
            task.texts,
            task.file_task.source_lang,
            task.file_task.target_lang,
            task.file_task.game_profile,
            task.file_task.mod_context
        )
        task.translated_texts = translated_texts
        return task

def translate_single_batch_with_batch_num(task: BatchTask) -> BatchTask:
    """
    (Modernized) Calls the single-batch translation function of the current API provider.
    This function is the primary entry point for the ParallelProcessor.
    """
    # The batch number is now implicitly part of the task object (task.batch_index).
    # The modernized _translate_chunk function in handlers will use this index.
    # Therefore, this function is now an alias for translate_single_batch.
    return translate_single_batch(task)