#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能安装配置引导器
支持多语言界面，引导用户完成项目依赖安装和配置
"""

import os
import sys
import subprocess
import json
import platform
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils import i18n

class SetupInstaller:
    """智能安装配置引导器"""
    
    def __init__(self):
        self.project_root = project_root
        self.requirements_file = self.project_root / "requirements.txt"
        self.api_providers = {
            "1": {
                "name": "Google Gemini",
                "package": "google-genai",
                "env_key": "GEMINI_API_KEY",
                "url": "https://aistudio.google.com/app/apikey",
                "description": "setup_desc_gemini",
                "type": "key_required"
            },
            "2": {
                "name": "OpenAI GPT",
                "package": "openai", 
                "env_key": "OPENAI_API_KEY",
                "url": "https://platform.openai.com/api-keys",
                "description": "setup_desc_openai",
                "type": "key_required"
            },
            "3": {
                "name": "DeepSeek",
                "package": "deepseek",
                "env_key": "DEEPSEEK_API_KEY",
                "url": "https://platform.deepseek.com/api_keys",
                "description": "setup_desc_deepseek",
                "type": "key_required"
            },
            "4": {
                "name": "阿里云通义千问 (Qwen)",
                "package": "dashscope",
                "env_key": "DASHSCOPE_API_KEY", 
                "url": "https://help.aliyun.com/zh/model-studio/get-api-key?spm=a2c4g.11186623.0.0.222a5980mhxw9D",
                "description": "setup_desc_qwen",
                "type": "key_required"
            },
            "5": {
                "name": "Grok (xAI)",
                "package": "openai",
                "env_key": "XAI_API_KEY",
                "url": "https://console.x.ai/team/default/api-keys",
                "description": "setup_desc_grok",
                "type": "key_required"
            },
            "6": {
                "name": "Ollama (本地模型)",
                "url": "https://ollama.com/",
                "description": "setup_desc_ollama",
                "type": "info_only",
                "info": """
Ollama 是一个本地化运行大语言模型的框架，它不需要API Key。
您需要自行在电脑上安装Ollama，并下载您想使用的模型。

1. 访问Ollama官网并下载安装程序:
   https://ollama.com/

2. 安装后，在您的终端或CMD中运行模型，例如 `ollama run llama3`。

3. 确保Ollama程序在后台持续运行，本工具才能连接到它。
"""
            },
            "7": {
                "name": "Gemini CLI (谷歌官方CLI)",
                "url": "https://github.com/google/gemini-cli",
                "description": "setup_desc_gemini_cli",
                "type": "info_only",
                "info": """
Gemini CLI 是谷歌官方的命令行工具，它通过Google账户认证，无需API Key。
您需要自行安装它。

1. 访问Gemini CLI的GitHub页面获取安装指南:
   https://github.com/google/gemini-cli

2. 安装通常需要Node.js环境，然后通过 `npm install -g @google/gemini-cli` 命令安装。

3. 首次使用时，根据提示运行 `gemini auth` 并登录您的Google账户完成认证。
"""
            }
        }
    
    def display_banner(self):
        """显示安装配置横幅"""
        print("=" * 60)
        print("🚀 Paradox Mod Localization Factory - Setup Installer")
        print("🚀 Project Remis - 安装配置引导器")
        print("=" * 60)
        print()
    
    def select_language(self):
        """选择界面语言"""
        print("🌍 请选择界面语言 / Please select interface language")
        print("=" * 60)
        print("1. English")
        print("2. 中文 (简体)")
        print("=" * 60)
        
        while True:
            choice = input("请输入选择 (1 或 2) / Enter choice (1 or 2): ").strip()
            if choice == "1":
                return "en_US"
            elif choice == "2":
                return "zh_CN"
            else:
                print("❌ 无效选择，请重新输入 / Invalid choice, please try again")

    def select_api_provider(self):
        """选择API提供商"""
        print(f"\n{i18n.t('setup_select_api_provider')}")
        print("=" * 60)
        
        provider_keys = list(self.api_providers.keys())

        for key in provider_keys:
            provider = self.api_providers[key]
            print(f"[{key}] {provider['name']}")
            print(f"     - {i18n.t(provider['description'])}")
            if provider['type'] == 'key_required':
                print(f"     - {i18n.t('setup_api_url')}: {provider['url']}")
            print()
        
        print(f"⚠️  {i18n.t('setup_api_warning')}")
        print()
        
        while True:
            choice = input(f"{i18n.t('setup_enter_choice')} (1-{len(provider_keys)}): ").strip()
            if choice in self.api_providers:
                return self.api_providers[choice]
            else:
                print(f"❌ {i18n.t('setup_invalid_choice')}")

    def show_info_and_pause(self, provider):
        """显示信息并暂停"""
        print("\n" + "=" * 60)
        print(f" informational_setup_for {provider['name']} informational_setup_for")
        print("=" * 60)
        print(provider["info"])
        print("=" * 60)
        input(f"\n{i18n.t('setup_press_enter_to_return')}")

    def is_portable_environment(self):
        """检测是否为便携式环境"""
        try:
            # 尝试导入pip，如果失败说明是便携式环境
            import pip
            return False
        except ImportError:
            return True
    
    def install_api_package(self, provider):
        """安装API包"""
        package_name = provider.get("package")
        if not package_name:
            print(f"ℹ️ {i18n.t('setup_no_package_to_install', provider=provider['name'])}")
            return True

        # 检测便携式环境
        if self.is_portable_environment():
            print(f"\n📦 {i18n.t('setup_installing_api_package', provider=provider['name'])}")
            print(f"{i18n.t('setup_portable_environment_detected')}")
            print(f"{i18n.t('setup_api_package_preinstalled', provider=provider['name'])}")
            return True

        print(f"\n{i18n.t('setup_installing_api_package', provider=provider['name'])}")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", package_name],
                capture_output=True, text=True, check=True, encoding='utf-8'
            )
            
            print(f"✅ {i18n.t('setup_api_package_installed', provider=provider['name'])}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {i18n.t('setup_api_package_install_failed', provider=provider['name'])}")
            print(f"   {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ {i18n.t('setup_api_package_install_error', provider=provider['name'], error=str(e))}")
            return False
    
    def setup_api_key(self, provider):
        """设置API密钥"""
        print(f"\n{i18n.t('setup_api_key_instructions', provider=provider['name'])}")
        print(f"1. {i18n.t('setup_visit_url')}: {provider['url']}")
        print(f"2. {i18n.t('setup_login_account')}")
        print(f"3. {i18n.t('setup_create_api_key')}")
        print(f"4. {i18n.t('setup_copy_api_key')}")
        print()
        
        while True:
            api_key = input(f"{i18n.t('setup_enter_api_key', provider=provider['name'])}: ").strip()
            if api_key:
                break
            else:
                print(f"❌ {i18n.t('setup_api_key_cannot_be_empty')}")
        
        print(f"\n{i18n.t('setup_setting_env_var')}")
        
        try:
            if platform.system() == "Windows":
                subprocess.run(
                    ["setx", provider['env_key'], api_key],
                    capture_output=True, text=True, check=True, encoding='gbk'
                )
            else:
                shell_name = os.path.basename(os.environ.get("SHELL", "bash"))
                if "zsh" in shell_name:
                    shell_config_path = os.path.expanduser("~/.zshrc")
                else:
                    shell_config_path = os.path.expanduser("~/.bashrc")
                
                env_line = f"\nexport {provider['env_key']}='{api_key}'\n"
                with open(shell_config_path, "a", encoding='utf-8') as f:
                    f.write(env_line)
                
                print(f"   {i18n.t('setup_env_var_source_required', shell_config=shell_config_path)}")

            print(f"✅ {i18n.t('setup_env_var_set_success')}")
            print(f"   {i18n.t('setup_env_var_restart_required')}")
            return True
            
        except Exception as e:
            print(f"❌ {i18n.t('setup_env_var_set_failed')}")
            print(f"   Error: {e}")
            print(f"   {i18n.t('setup_manual_env_var_instruction', env_key=provider['env_key'])}")
            return False
    
    def run_setup(self):
        """运行完整的安装配置流程"""
        self.display_banner()
        
        lang_code = self.select_language()
        i18n.load_language(lang_code)
        
        while True:
            provider = self.select_api_provider()
            
            if provider['type'] == 'info_only':
                self.show_info_and_pause(provider)
                continue # 返回主菜单

            if not self.install_api_package(provider):
                input(f"\n{i18n.t('setup_press_enter_to_exit')}")
                break

            if not self.setup_api_key(provider):
                input(f"\n{i18n.t('setup_press_enter_to_exit')}")
                break
            
            print("\n" + "=" * 60)
            print(f"🎉 {i18n.t('setup_configuration_complete_provider', provider=provider['name'])}")
            print("=" * 60)
            
            while True:
                another = input(f"\n{i18n.t('setup_configure_another_provider')} (y/n): ").strip().lower()
                if another in ['y', 'n']:
                    break
                print(f"❌ {i18n.t('setup_invalid_choice')}")
            
            if another == 'n':
                break
        
        print("\n" + "=" * 60)
        print(f"🚀 {i18n.t('setup_ready_to_use')}")
        print("=" * 60)
        print(f"   {i18n.t('setup_double_click_run_bat')}")
        print(f"   {i18n.t('setup_env_var_restart_note')}")
        print()
        input(f"{i18n.t('setup_press_enter_to_exit')}")

def main():
    """主函数"""
    installer = SetupInstaller()
    installer.run_setup()

if __name__ == '__main__':
    main()
