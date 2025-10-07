# scripts/core/gemini_cli_handler.py
import os
import logging
import tempfile
import subprocess
import time
from typing import Any

from scripts.core.base_handler import BaseApiHandler
from scripts.app_settings import API_PROVIDERS, GEMINI_CLI_MAX_RETRIES
from scripts.utils import i18n
from scripts.core.parallel_processor import BatchTask
from scripts.utils.response_parser import parse_json_response

class GeminiCLIHandler(BaseApiHandler):
    """
    Gemini CLI Handler子类。
    特殊之处在于它重写了父类的整个 `translate_batch` 工作流，
    因为它依赖于命令行子进程而不是直接的API SDK调用。
    """

    def __init__(self, provider_name: str, model_name: str = None):
        self.model = model_name or API_PROVIDERS.get("gemini_cli", {}).get("default_model", "gemini-1.5-flash")
        super().__init__(provider_name)

    def initialize_client(self) -> Any:
        self.cli_path = API_PROVIDERS.get("gemini_cli", {}).get("cli_path", "gemini")
        self._verify_cli_availability()
        self.logger.info(f"Gemini CLI handler initialized. Path: {self.cli_path}, Model: {self.model}")
        return self

    def _verify_cli_availability(self):
        try:
            cmd = ["powershell", "-Command", f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; {self.cli_path} --version"]
            kwargs = { "capture_output": True, "text": True, "timeout": 10 }
            if os.name == 'nt':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            result = subprocess.run(cmd, **kwargs)
            if result.returncode != 0:
                raise RuntimeError(f"Gemini CLI version check failed: {result.stderr}")
            self.logger.info(i18n.t("gemini_cli_available", version=result.stdout.strip()))
        except FileNotFoundError:
            self.logger.error(i18n.t("gemini_cli_not_found", cli_path=self.cli_path))
            raise
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred during Gemini CLI availability check: {e}")
            raise

    # This handler does NOT implement _call_api because it overrides the entire workflow.
    def _call_api(self, client: Any, prompt: str) -> str:
        # This method is required by the abstract base class, but since we override
        # the translate_batch method that calls it, this will never be executed.
        # We provide a dummy implementation to satisfy the ABC requirements.
        self.logger.warning("`_call_api` should not be called on GeminiCLIHandler.")
        pass

    def translate_batch(self, task: BatchTask) -> BatchTask:
        """
        【独有实现】重写整个翻译工作流，使用子进程和PowerShell管道与Gemini CLI交互。
        """
        prompt = self._build_prompt(task)
        batch_num = task.batch_index + 1

        for attempt in range(GEMINI_CLI_MAX_RETRIES):
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(prompt)
                    temp_file = f.name

                try:
                    gemini_command = f"{self.cli_path} --model {self.model} --output-format json"
                    full_command = f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; Get-Content '{temp_file}' -Raw | {gemini_command}"
                    cmd = ["powershell", "-Command", full_command]

                    clean_env = {
                        'PATH': os.environ.get('PATH', ''), 'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                        'TEMP': os.environ.get('TEMP', ''), 'TMP': os.environ.get('TMP', ''),
                        'USERPROFILE': os.environ.get('USERPROFILE', ''), 'APPDATA': os.environ.get('APPDATA', ''),
                        'LOCALAPPDATA': os.environ.get('LOCALAPPDATA', ''), 'PROGRAMDATA': os.environ.get('PROGRAMDATA', ''),
                        'WINDIR': os.environ.get('WINDIR', ''), 'COMSPEC': os.environ.get('COMSPEC', ''),
                        'PATHEXT': os.environ.get('PATHEXT', ''), 'PSModulePath': os.environ.get('PSModulePath', ''),
                        'GEMINI_API_KEY': '',
                    }

                    kwargs = {
                        "capture_output": True, "text": True, "timeout": 300,
                        "encoding": 'utf-8', "env": clean_env
                    }
                    if os.name == 'nt':
                        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

                    result = subprocess.run(cmd, **kwargs)
                finally:
                    os.unlink(temp_file)

                if result.returncode == 0:
                    translated_texts = parse_json_response(result.stdout, len(task.texts))
                    if translated_texts and len(translated_texts) == len(task.texts):
                        task.translated_texts = translated_texts
                        self.logger.info(f"Gemini CLI Batch {batch_num} translated successfully on attempt {attempt + 1}.")
                        return task
                    else:
                        self.logger.warning(f"Gemini CLI response parsing failed for batch {batch_num}, attempt {attempt + 1}. Expected {len(task.texts)}, got {len(translated_texts) if translated_texts else 0}.")
                else:
                    self.logger.error(f"Gemini CLI call failed for batch {batch_num}, attempt {attempt+1}. Stderr: {result.stderr}")

            except Exception as e:
                self.logger.exception(f"Exception in Gemini CLI batch {batch_num} on attempt {attempt + 1}: {e}")

            if attempt < GEMINI_CLI_MAX_RETRIES - 1:
                delay = (attempt + 1) * 2
                self.logger.warning(i18n.t("retrying_batch", batch_num=batch_num, attempt=attempt + 1, max_retries=GEMINI_CLI_MAX_RETRIES, delay=delay))
                time.sleep(delay)

        self.logger.error(f"Gemini CLI Batch {batch_num} failed after {GEMINI_CLI_MAX_RETRIES} attempts.")
        task.translated_texts = None
        return task
