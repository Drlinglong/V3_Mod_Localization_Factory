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
        model_name = API_PROVIDERS.get("gemini", {}).get("default_model", "gemini-1.5-flash")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            self.logger.exception(f"Gemini API call failed: {e}")
            raise
