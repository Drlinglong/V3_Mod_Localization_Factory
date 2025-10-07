# scripts/core/gemini_cli_handler.py
import os
import logging
import tempfile
import subprocess
from typing import Any

from scripts.core.base_handler import BaseApiHandler
from scripts.app_settings import API_PROVIDERS
from scripts.utils import i18n

class GeminiCLIHandler(BaseApiHandler):
    """Gemini CLI Handler子类，通过命令行工具与API交互。"""

    def __init__(self, provider_name: str, model_name: str = None):
        """
        自定义构造函数，用于接收和存储模型名称。
        """
        self.model = model_name or API_PROVIDERS.get("gemini_cli", {}).get("default_model", "gemini-1.5-flash")
        super().__init__(provider_name)

    def initialize_client(self) -> Any:
        """【必须由子类实现】验证CLI可用性并返回Handler实例作为客户端。"""
        self.cli_path = API_PROVIDERS.get("gemini_cli", {}).get("cli_path", "gemini")
        self._verify_cli_availability()
        self.logger.info(f"Gemini CLI handler initialized. Path: {self.cli_path}, Model: {self.model}")
        return self

    def _verify_cli_availability(self):
        """验证Gemini CLI是否可用。"""
        try:
            cmd = ["powershell", "-Command", f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; {self.cli_path} --version"]
            kwargs = { "capture_output": True, "text": True, "timeout": 10 }
            if os.name == 'nt':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            result = subprocess.run(cmd, **kwargs)
            if result.returncode == 0:
                self.logger.info(i18n.t("gemini_cli_available", version=result.stdout.strip()))
            else:
                error_msg = i18n.t("gemini_cli_version_check_failed", error=result.stderr)
                self.logger.warning(error_msg)
                raise RuntimeError(f"Gemini CLI version check failed: {result.stderr}")
        except FileNotFoundError:
            self.logger.error(i18n.t("gemini_cli_not_found", cli_path=self.cli_path))
            raise
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred during Gemini CLI availability check: {e}")
            raise

    def _call_api(self, client: Any, prompt: str) -> str:
        """【必须由子类实现】通过subprocess和PowerShell管道调用Gemini CLI。"""
        handler_instance = client
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(prompt)
            temp_file = f.name
        
        try:
            cmd = [
                "powershell", "-Command",
                f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; Get-Content '{temp_file}' -Raw | {handler_instance.cli_path} --model {handler_instance.model} --output-format json"
            ]
            
            clean_env = {
                'PATH': os.environ.get('PATH', ''),
                'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                'TEMP': os.environ.get('TEMP', ''),
                'USERPROFILE': os.environ.get('USERPROFILE', ''),
                'APPDATA': os.environ.get('APPDATA', ''),
                'WINDIR': os.environ.get('WINDIR', ''),
                'COMSPEC': os.environ.get('COMSPEC', ''),
                'GEMINI_API_KEY': '',
            }
            
            kwargs = {
                "capture_output": True,
                "text": True,
                "timeout": 300,
                "encoding": 'utf-8',
                "env": clean_env
            }
            if os.name == 'nt':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

            result = subprocess.run(cmd, **kwargs)
            
            if result.returncode == 0:
                return result.stdout
            else:
                error_msg = f"Gemini CLI call failed with return code {result.returncode}: {result.stderr}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

        finally:
            try:
                os.unlink(temp_file)
            except OSError as e:
                self.logger.warning(f"Could not delete temp file {temp_file}: {e}")
