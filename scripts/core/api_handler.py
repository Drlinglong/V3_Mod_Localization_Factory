# scripts/core/api_handler.py
import logging
from typing import TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular imports at runtime
if TYPE_CHECKING:
    from .base_handler import BaseApiHandler

# --- Handler Imports ---
from .openai_handler import OpenAIHandler
from .gemini_handler import GeminiHandler
from .gemini_cli_handler import GeminiCLIHandler
from .qwen_handler import QwenHandler
from .deepseek_handler import DeepSeekHandler
from .grok_handler import GrokHandler
from .ollama_handler import OllamaHandler


def get_handler(provider_name: str, model_name: str = None) -> 'BaseApiHandler':
    """
    【工厂函数】根据名称返回对应的API处理器实例。
    """
    try:
        if provider_name == "openai":
            return OpenAIHandler(provider_name)
        elif provider_name == "qwen":
            return QwenHandler(provider_name)
        elif provider_name == "gemini":
            return GeminiHandler(provider_name)
        elif provider_name == "gemini_cli":
            # GeminiCLIHandler has a custom constructor
            return GeminiCLIHandler(provider_name, model_name=model_name)
        elif provider_name == "deepseek":
            return DeepSeekHandler(provider_name)
        elif provider_name == "grok":
            return GrokHandler(provider_name)
        elif provider_name == "ollama":
            return OllamaHandler(provider_name)
        else:
            # 默认返回 Gemini
            logging.warning(f"Unknown provider '{provider_name}', falling back to 'gemini'.")
            return GeminiHandler("gemini")
    except Exception as e:
        logging.error(f"Failed to instantiate handler for {provider_name}: {e}", exc_info=True)
        raise
