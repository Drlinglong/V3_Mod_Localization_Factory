# scripts/core/ollama_handler.py
import os
import requests
import logging
from typing import Any

from scripts.app_settings import API_PROVIDERS
from scripts.core.base_handler import BaseApiHandler

class OllamaHandler(BaseApiHandler):
    """Ollama API Handler子类，用于与本地Ollama服务交互。"""

    def initialize_client(self) -> Any:
        """【必须由子类实现】初始化Ollama配置。"""
        try:
            provider_config = self.get_provider_config()
            # 从环境变量 OLLAMA_BASE_URL 读取URL，如果未设置，则从配置读取，最后使用默认值
            self.base_url = os.getenv("OLLAMA_BASE_URL", provider_config.get("base_url", "http://localhost:11434"))

            # 检查Ollama版本是否支持/api/chat
            try:
                response = requests.get(f"{self.base_url}/api/version", timeout=10)
                response.raise_for_status()
                version_str = response.json().get("version", "0.0.0")
                
                # 版本号比较
                current_version = tuple(map(int, version_str.split('.')))
                required_version = (0, 1, 14)

                if current_version < required_version:
                    error_msg = (
                        f"您的Ollama版本 ({version_str}) 过低，不支持 '/api/chat' 接口。\n"
                        f"请升级到 0.1.14 或更高版本。\n"
                        f"请访问 https://ollama.com/download 下载最新版本。"
                    )
                    raise RuntimeError(error_msg)
            
            except requests.exceptions.RequestException as e:
                self.logger.error(f"无法连接到Ollama或检查其版本。请确保Ollama正在运行于 {self.base_url}。错误: {e}")
                raise

            self.model = provider_config.get("default_model", "llama3.2")
            
            self.logger.info(f"Ollama client configured. Base URL: {self.base_url}, Model: {self.model}, Version: {version_str}")
            # 返回自身实例作为客户端，因为它持有配置信息
            return self
        except Exception as e:
            self.logger.exception(f"Error initializing Ollama client: {e}")
            raise

    def _call_api(self, client: Any, prompt: str) -> str:
        """【必须由子类实现】使用requests调用本地Ollama API。"""
        handler_instance = client

        # Split the prompt into system instructions and user data
        # to use the API more effectively.
        try:
            system_prompt, user_prompt = prompt.split("--- INPUT LIST ---", 1)
            user_prompt = "--- INPUT LIST ---" + user_prompt
        except ValueError:
            # Fallback if the separator is not found
            system_prompt = "You are a professional translator. Your response MUST be a valid JSON array of strings."
            user_prompt = prompt

        payload = {
            "model": handler_instance.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            #"format": "json" 有很多模型不支持这个参数 暂时先注释掉
        }

        try:
            proxies = {
                "http": None,
                "https": None,
            }
            response = requests.post(
                f"{handler_instance.base_url}/api/generate",
                json=payload,
                timeout=300,
                proxies=proxies
            )
            response.raise_for_status()
            
            result = response.json()
            
            return result.get("response", "").strip()
            
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"Ollama API call failed: {e}")
            raise
