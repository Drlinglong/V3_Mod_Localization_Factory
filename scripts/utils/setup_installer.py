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
                "url": "https://aistudio.google.com/",
                "description": "使用 Gemini 2.5 Flash 模型\n     - 翻译质量高，支持中文\n     - 需要Google账号",
                "recommended": True
            },
            "2": {
                "name": "OpenAI GPT",
                "package": "openai", 
                "env_key": "OPENAI_API_KEY",
                "url": "https://platform.openai.com/",
                "description": "使用 GPT-5 Mini 模型\n     - 翻译质量极高，支持多种语言\n     - 需要OpenAI账号",
                "recommended": False
            },
            "3": {
                "name": "阿里云通义千问",
                "package": "dashscope",
                "env_key": "DASHSCOPE_API_KEY", 
                "url": "https://dashscope.console.aliyun.com/",
                "description": "使用 Qwen Plus 模型\n     - 国产AI服务，允许国内用户直连\n     - 建议国内用户选择此选项\n     - 需要阿里云账号",
                "recommended": False
            }
        }
    
    def display_banner(self):
        """显示安装配置横幅"""
        print("=" * 60)
        print("🚀 Paradox Mod Localization Factory - Setup Installer")
        print("🚀 蕾姆丝计划 - 安装配置引导器")
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
    
    def check_python_environment(self):
        """检查Python环境"""
        print(f"\n{i18n.t('setup_checking_python')}")
        
        try:
            # 检查Python版本
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                print(f"❌ {i18n.t('setup_python_version_too_low', version=f'{python_version.major}.{python_version.minor}')}")
                print(f"   {i18n.t('setup_python_requires_38')}")
                return False
            else:
                print(f"✅ {i18n.t('setup_python_version_ok', version=f'{python_version.major}.{python_version.minor}.{python_version.micro}')}")
            
            # 检查pip
            try:
                import pip
                print(f"✅ {i18n.t('setup_pip_available')}")
                return True
            except ImportError:
                print(f"❌ {i18n.t('setup_pip_not_available')}")
                return False
                
        except Exception as e:
            print(f"❌ {i18n.t('setup_python_check_failed', error=str(e))}")
            return False
    
    def install_requirements(self):
        """安装项目依赖"""
        print(f"\n{i18n.t('setup_installing_requirements')}")
        
        if not self.requirements_file.exists():
            print(f"❌ {i18n.t('setup_requirements_file_not_found')}")
            return False
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ], capture_output=True, text=True, check=True)
            
            print(f"✅ {i18n.t('setup_requirements_installed')}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {i18n.t('setup_requirements_install_failed')}")
            print(f"   {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ {i18n.t('setup_requirements_install_error', error=str(e))}")
            return False
    
    def select_api_provider(self):
        """选择API提供商"""
        print(f"\n{i18n.t('setup_select_api_provider')}")
        print("=" * 60)
        
        for key, provider in self.api_providers.items():
            if provider.get('recommended', False):
                print(f"[{key}] {provider['name']} (推荐)")
            else:
                print(f"[{key}] {provider['name']}")
            print(f"     - {provider['description']}")
            print(f"     - {i18n.t('setup_api_url')}: {provider['url']}")
            print()
        
        print(f"⚠️  {i18n.t('setup_api_warning')}")
        print()
        
        while True:
            choice = input(f"{i18n.t('setup_enter_choice')} (1-3): ").strip()
            if choice in self.api_providers:
                return self.api_providers[choice]
            else:
                print(f"❌ {i18n.t('setup_invalid_choice')}")
    
    def install_api_package(self, provider):
        """安装API包"""
        print(f"\n{i18n.t('setup_installing_api_package', provider=provider['name'])}")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", provider['package']
            ], capture_output=True, text=True, check=True)
            
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
        
        # 设置环境变量
        print(f"\n{i18n.t('setup_setting_env_var')}")
        
        try:
            if platform.system() == "Windows":
                # Windows环境变量设置
                result = subprocess.run([
                    "setx", provider['env_key'], api_key
                ], capture_output=True, text=True, check=True)
                
                print(f"✅ {i18n.t('setup_env_var_set_success')}")
                print(f"   {i18n.t('setup_env_var_restart_required')}")
                
            else:
                # Linux/Mac环境变量设置
                shell_config = os.path.expanduser("~/.bashrc")
                env_line = f"export {provider['env_key']}='{api_key}'\n"
                
                with open(shell_config, "a") as f:
                    f.write(env_line)
                
                print(f"✅ {i18n.t('setup_env_var_set_success')}")
                print(f"   {i18n.t('setup_env_var_source_required')}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {i18n.t('setup_env_var_set_failed')}")
            print(f"   {i18n.t('setup_manual_env_var_instruction', key=provider['env_key'])}")
            return False
        except Exception as e:
            print(f"❌ {i18n.t('setup_env_var_set_error', error=str(e))}")
            return False
    
    def run_setup(self):
        """运行完整的安装配置流程"""
        self.display_banner()
        
        # 选择语言
        lang_code = self.select_language()
        i18n.load_language(lang_code)
        
        print(f"\n{i18n.t('setup_welcome_message')}")
        print(f"{i18n.t('setup_one_time_config')}")
        print()
        
        # 检查Python环境
        if not self.check_python_environment():
            print(f"\n{i18n.t('setup_python_install_instructions')}")
            print(f"1. {i18n.t('setup_visit_python_download')}")
            print(f"2. {i18n.t('setup_download_latest_python')}")
            print(f"3. {i18n.t('setup_install_with_path')}")
            print(f"4. {i18n.t('setup_restart_installer')}")
            input(f"\n{i18n.t('setup_press_enter_to_exit')}")
            return False
        
        # 安装项目依赖（如果有的话）
        if self.requirements_file.exists() and self.requirements_file.stat().st_size > 0:
            if not self.install_requirements():
                print(f"\n{i18n.t('setup_requirements_install_manual')}")
                input(f"\n{i18n.t('setup_press_enter_to_exit')}")
                return False
        else:
            print(f"ℹ️  {i18n.t('setup_no_requirements_to_install')}")
        
        # 选择API提供商
        provider = self.select_api_provider()
        
        # 安装API包
        if not self.install_api_package(provider):
            print(f"\n{i18n.t('setup_api_package_install_manual', package=provider['package'])}")
            input(f"\n{i18n.t('setup_press_enter_to_exit')}")
            return False
        
        # 设置API密钥
        if not self.setup_api_key(provider):
            print(f"\n{i18n.t('setup_api_key_setup_manual', key=provider['env_key'])}")
            input(f"\n{i18n.t('setup_press_enter_to_exit')}")
            return False
        
        # 完成配置
        print("\n" + "=" * 60)
        print(f"🎉 {i18n.t('setup_configuration_complete')}")
        print("=" * 60)
        print()
        print(f"✅ {i18n.t('setup_dependencies_installed')}")
        print(f"✅ {i18n.t('setup_env_vars_set')}")
        print(f"✅ {i18n.t('setup_api_configured')}")
        print()
        print(f"🚀 {i18n.t('setup_ready_to_use')}")
        print()
        print(f"📋 {i18n.t('setup_usage_instructions')}")
        print(f"1. {i18n.t('setup_double_click_run_bat')}")
        print(f"2. {i18n.t('setup_follow_prompts')}")
        print(f"3. {i18n.t('setup_start_translation')}")
        print()
        print(f"💡 {i18n.t('setup_tips')}")
        print(f"- {i18n.t('setup_one_time_only')}")
        print(f"- {i18n.t('setup_no_reconfig_needed')}")
        print(f"- {i18n.t('setup_check_readme_if_issues')}")
        print()
        print(f"🔄 {i18n.t('setup_env_vars_restart_note')}")
        print()
        
        input(f"{i18n.t('setup_press_enter_to_exit')}")
        return True

def main():
    """主函数"""
    installer = SetupInstaller()
    installer.run_setup()

if __name__ == '__main__':
    main()
