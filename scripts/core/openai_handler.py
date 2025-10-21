# scripts/core/openai_handler.py
import os
from openai import OpenAI
import logging

from scripts.app_settings import API_PROVIDERS
from scripts.core.base_handler import BaseApiHandler

class OpenAIHandler(BaseApiHandler):
    """OpenAI API Handler子类"""

    def initialize_client(self):
        """【必须由子类实现】初始化并返回OpenAI的API客户端。"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.error("API Key 'OPENAI_API_KEY' not found in environment variables.")
            raise ValueError("OPENAI_API_KEY not set")
        try:
            client = OpenAI(api_key=api_key)
            model_name = API_PROVIDERS["openai"]["default_model"]
            self.logger.info(f"OpenAI client initialized successfully, using model: {model_name}")
            return client
        except Exception as e:
            self.logger.exception(f"Error initializing OpenAI client: {e}")
            raise

    def _call_api(self, client: OpenAI, prompt: str) -> str:
        """【必须由子类实现】执行对OpenAI API的调用并返回原始文本响应。"""
        provider_config = API_PROVIDERS.get(self.provider_name, {})
        model_name = provider_config.get("default_model", "gpt-5-mini")
        
        enable_thinking = provider_config.get("enable_thinking", False)
        reasoning_effort_value = provider_config.get("reasoning_effort")

        extra_params = {}
        if not enable_thinking and reasoning_effort_value:
            extra_params["reasoning_effort"] = reasoning_effort_value

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a professional translator for game mods."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=4000,  # 保持较大的token以适应大批次
                **extra_params
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.exception(f"OpenAI API call failed: {e}")
            # 重新引发异常，让基类的重试逻辑捕获
            raise
