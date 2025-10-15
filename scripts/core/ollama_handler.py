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
            # 从环境变量 OLLAMA_BASE_URL 读取URL，如果未设置，则使用默认值
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

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

            self.model = API_PROVIDERS.get("ollama", {}).get("default_model", "llama3.2")
            
            self.logger.info(f"Ollama client configured. Base URL: {self.base_url}, Model: {self.model}, Version: {version_str}")
            # 返回自身实例作为客户端，因为它持有配置信息
            return self
        except Exception as e:
            self.logger.exception(f"Error initializing Ollama client: {e}")
            raise

    def _call_api(self, client: Any, prompt: str) -> str:
        """【必须由子类实现】使用requests调用本地Ollama API。"""
        # 'client'参数是handler实例本身
        handler_instance = client
        
        provider_config = API_PROVIDERS.get(self.provider_name, {})
        enable_thinking = provider_config.get("enable_thinking", False)

        # Ollama API的请求体格式
        payload = {
            "model": handler_instance.model,
            "messages": [
                {"role": "system", "content": "You are a professional translator for game mods."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "think": enable_thinking  # 关键参数
        }

        try:
            response = requests.post(
                f"{handler_instance.base_url}/api/chat",
                json=payload,
                timeout=300  # 5分钟超时
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 提取并返回响应内容
            return result.get("message", {}).get("content", "").strip()
            
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"Ollama API call failed: {e}")
            raise
