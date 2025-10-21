# scripts/core/yourfavourite_handler.py
import os
from openai import OpenAI
import logging

from scripts.app_settings import API_PROVIDERS
from scripts.core.base_handler import BaseApiHandler

class YourFavouriteHandler(BaseApiHandler):
    """(高级)通用OAI兼容API Handler子类"""

    def initialize_client(self):
        """【必须由子类实现】初始化并返回一个通用的、兼容OAI的API客户端。"""
        api_key = os.getenv("YOUR_FAVOURITE_API_KEY")
        if not api_key:
            self.logger.error("API Key 'YOUR_FAVOURITE_API_KEY' not found in environment variables.")
            raise ValueError("YOUR_FAVOURITE_API_KEY not set")

        try:
            provider_config = API_PROVIDERS.get("your_favourite_api", {})
            base_url = provider_config.get("base_url")
            if not base_url or base_url == "YOUR_BASE_URL_HERE":
                raise ValueError("Base URL for your_favourite_api is not configured in app_settings.py.")

            client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            model_name = provider_config.get("default_model")
            self.logger.info(f"Custom API client initialized successfully, using model: {model_name}")
            self.logger.info(f"Using base URL: {base_url}")
            return client
        except Exception as e:
            self.logger.exception(f"Error initializing Custom API client: {e}")
            raise

    def _call_api(self, client: OpenAI, prompt: str) -> str:
        """【必须由子类实现】执行对通用OAI兼容API的调用并返回原始文本响应。"""
        provider_config = API_PROVIDERS.get(self.provider_name, {})
        model_name = provider_config.get("default_model")
        if not model_name or model_name == "YOUR_MODEL_NAME_HERE":
            raise ValueError("Model name for your_favourite_api is not configured in app_settings.py.")

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a professional translator for game mods."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.exception(f"Custom API call failed: {e}")
            raise
