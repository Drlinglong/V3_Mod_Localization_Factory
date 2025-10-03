import os
import logging
from typing import Any
from google import genai

from scripts.app_settings import API_PROVIDERS
from scripts.core.base_handler import BaseApiHandler

class GeminiHandler(BaseApiHandler):
    """Gemini API Handler子类"""

    def initialize_client(self) -> Any:
        """【必须由子类实现】初始化并配置Gemini的API客户端。"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.logger.error("API Key 'GEMINI_API_KEY' not found in environment variables.")
            raise ValueError("GEMINI_API_KEY not set")
        try:
            # The genai.configure() method is deprecated.
            # The API key is now passed directly to the genai.Client constructor.
            client = genai.Client(api_key=api_key)
            self.logger.info("Gemini client initialized successfully.")
            return client
        except Exception as e:
            self.logger.exception(f"Error initializing Gemini client: {e}")
            raise

    def _call_api(self, client: Any, prompt: str) -> str:
        """【必须由子类实现】执行对Gemini API的调用并返回原始文本响应。"""
        provider_config = API_PROVIDERS.get(self.provider_name, {})
        model_name = provider_config.get("default_model", "gemini-1.5-flash")
        
        enable_thinking = provider_config.get("enable_thinking", False)
        thinking_budget = provider_config.get("thinking_budget", 0)

        generation_config = {}
        if not enable_thinking:
            generation_config["thinking_config"] = {"thinking_budget": 0}
        elif thinking_budget != 0: # If thinking is enabled, use the specified budget
            generation_config["thinking_config"] = {"thinking_budget": thinking_budget}

        try:
            # Pass the generation_config to the API call
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                generation_config=generation_config if generation_config else None
            )
            return response.text.strip()
        except Exception as e:
            self.logger.exception(f"Gemini API call failed: {e}")
            raise
