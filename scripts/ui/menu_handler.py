# scripts/ui/menu_handler.py
# ---------------------------------------------------------------
"""
这个模块包含了所有与用户界面（菜单显示、用户输入等）相关的函数。
将UI逻辑与核心工作流分离开来，可以提高代码的模块化和可维护性。
"""
import os
import sys
import json
import logging
import re
import subprocess
import importlib.util

from scripts.utils import i18n
from scripts.app_settings import (
    LANGUAGES,
    GAME_PROFILES,
    SOURCE_DIR,
    API_PROVIDERS,
    PROJECT_INFO,
)


def display_version_info():
    """显示项目版本信息"""
    print(f"📦 版本version: {PROJECT_INFO['version']}")
    print(f"📅 最后更新last update: {PROJECT_INFO['last_update']}")
    print(f"{PROJECT_INFO['copyright']}")
    print("=" * 60)

def preflight_checks():
    """
    执行开机自检，验证系统环境和项目结构

    Returns:
        bool: 检查是否通过
    """
    print(i18n.t("preflight_checking_environment"))

    checks_passed = True
    error_messages = []

    # 1. 检查项目结构
    required_dirs = ["scripts", "data", "source_mod"]
    required_files = ["scripts/main.py", "scripts/app_settings.py", "data/lang/zh_CN.json", "data/lang/en_US.json"]

    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            error_messages.append(f"缺少必要目录: {dir_path}")
            checks_passed = False

    for file_path in required_files:
        if not os.path.exists(file_path):
            error_messages.append(f"缺少必要文件: {file_path}")
            checks_passed = False

    # 2. 检查依赖库
    required_libraries = {
        "openai": "api_lib_openai",
        "google.genai": "api_lib_gemini",
        "dashscope": "api_lib_qwen"
    }

    available_libraries = []
    for lib_name, lib_key in required_libraries.items():
        try:
            if lib_name == "google.genai":
                import google.genai
            else:
                importlib.import_module(lib_name)
            available_libraries.append(i18n.t(lib_key))
        except ImportError:
            pass

    # 检查Gemini CLI
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Set-ExecutionPolicy RemoteSigned -Scope Process -Force; gemini --version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            available_libraries.append(i18n.t("api_lib_gemini_cli"))
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    if not available_libraries:
        error_messages.append("未找到任何API库")
        checks_passed = False

    # 3. 检查API密钥
    api_keys = ["OPENAI_API_KEY", "GEMINI_API_KEY", "DASHSCOPE_API_KEY"]
    available_keys = [key for key in api_keys if os.getenv(key)]

    if not available_keys:
        error_messages.append("未找到任何API密钥")
        checks_passed = False

    # 4. 检查source_mod目录内容
    mod_count = 0
    if os.path.exists("source_mod"):
        mod_dirs = [d for d in os.listdir("source_mod") if os.path.isdir(os.path.join("source_mod", d))]
        mod_count = len(mod_dirs)
        if mod_count == 0:
            error_messages.append("source_mod目录为空")
            checks_passed = False
    else:
        error_messages.append("source_mod目录不存在")
        checks_passed = False

    # 显示检查结果
    if checks_passed:
        lib_names = ", ".join(available_libraries)
        key_count = len(available_keys)
        print(f"✅ {i18n.t('preflight_success', libs=lib_names, keys=key_count, mods=mod_count)}")
    else:
        print(f"❌ {i18n.t('preflight_failed')}:")
        for msg in error_messages:
            print(f"   - {msg}")
        print(f"\n{i18n.t('preflight_retry_prompt')}")

    return checks_passed

def select_api_provider():
    """【新】显示API供应商列表并让用户选择。"""
    logging.info(i18n.t("select_api_provider_prompt"))

    provider_options = list(API_PROVIDERS.keys())

    for i, key in enumerate(provider_options):
        if key == "qwen":
            logging.info(f"  [{i + 1}] {key.capitalize()} - {i18n.t('qwen_china_hint')}")
        elif key == "deepseek":
            logging.info(f"  [{i + 1}] {key.capitalize()} - {i18n.t('deepseek_china_hint')}")
        else:
            logging.info(f"  [{i + 1}] {key.capitalize()}")

    while True:
        try:
            choice = int(input(i18n.t("enter_choice_prompt"))) - 1
            if 0 <= choice < len(provider_options):
                return provider_options[choice]
            else:
                logging.warning(i18n.t("invalid_input_number"))
        except ValueError:
            logging.warning(i18n.t("invalid_input_not_number"))

def gather_mod_context(mod_name):
    """
    Reads the mod name from its metadata and prompts the user for additional context.
    """
    logging.info(i18n.t("getting_mod_context"))
    mod_official_name = mod_name
    meta_path = os.path.join(SOURCE_DIR, mod_name, '.metadata', 'metadata.json')
    descriptor_path = os.path.join(SOURCE_DIR, mod_name, 'descriptor.mod')

    try:
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
                if 'name' in meta_data and meta_data['name']:
                    mod_official_name = meta_data['name']
        elif os.path.exists(descriptor_path):
            with open(descriptor_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('name='):
                        match = re.search(r'"(.*)"', line)
                        if match:
                            mod_official_name = match.group(1)
                        break

        logging.info(i18n.t("mod_name_identified", name=mod_official_name))
        extra_context = input(i18n.t("prompt_for_extra_context")).strip()

        final_context = mod_official_name
        if extra_context:
            final_context += f" ({extra_context})"

        logging.info(i18n.t("final_context_is", context=final_context))
        return final_context

    except Exception as e:
        logging.exception(i18n.t("error_getting_context", error=e))
        return mod_name

def select_interface_language():
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

def select_game_profile():
    """Displays a menu for the user to select a game profile."""
    logging.info(i18n.t("select_game_profile_prompt"))
    profiles = list(GAME_PROFILES.values())
    for i, profile in enumerate(profiles):
        logging.info(f"  [{i + 1}] {profile['name']}")

    while True:
        try:
            choice = int(input(i18n.t("enter_choice_prompt"))) - 1
            if 0 <= choice < len(profiles):
                return profiles[choice]
            else:
                logging.warning(i18n.t("invalid_input_number"))
        except ValueError:
            logging.warning(i18n.t("invalid_input_not_number"))

def select_language(prompt_key, game_profile, source_lang=None):
    """
    显示基于所选游戏配置文件的语言选择菜单。
    现在支持多选和“套壳”模式。
    """
    logging.info(i18n.t(prompt_key))

    supported_langs = [LANGUAGES[key] for key in game_profile['supported_language_keys']]

    # 如果提供了源语言，则在目标语言选择中将其过滤掉
    if source_lang:
        display_options = [lang for lang in supported_langs if lang['key'] != source_lang['key']]
    else:
        display_options = supported_langs

    # --- 显示菜单 ---
    is_target_selection = bool(source_lang)

    if is_target_selection:
        logging.info(f"  [0] 一键翻译为其余 {len(display_options)} 种语言")

    for i, lang in enumerate(display_options, 1):
        logging.info(f"  [{i}] {lang['name']}")

    if is_target_selection:
        logging.info(f"  [99] 套壳模式 (自定义语言)")


    while True:
        try:
            choice_str = input(i18n.t("enter_choice_prompt")).strip()
            choice = int(choice_str)

            if is_target_selection:
                if choice == 0:
                    logging.info(f"已选择翻译为所有其他 {len(display_options)} 种语言。")
                    return display_options
                elif 1 <= choice <= len(display_options):
                    selected = display_options[choice - 1]
                    logging.info(f"已选择: {selected['name']}")
                    return [selected]
                elif choice == 99:
                    shell_config = handle_shell_language_selection(game_profile)
                    return [shell_config] if shell_config else None
                else:
                    logging.warning(i18n.t("invalid_input_number"))
            else:  # 源语言选择
                if 1 <= choice <= len(display_options):
                    selected = display_options[choice - 1]
                    logging.info(f"已选择: {selected['name']}")
                    return selected
                else:
                    logging.warning(i18n.t("invalid_input_number"))
        except ValueError:
            logging.warning(i18n.t("invalid_input_not_number"))

def handle_shell_language_selection(game_profile):
    """
    处理“套壳”语言选择
    """
    logging.info("进入套壳模式...")
    custom_name = input("请输入自定义语言的名称 (例如 'Italiano'): ").strip()
    if not custom_name:
        logging.warning("自定义语言名称不能为空。")
        return None

    logging.info("请选择一个“套壳”语言 (例如 English)，生成的文件将使用此语言的格式:")

    supported_langs = [LANGUAGES[key] for key in game_profile['supported_language_keys']]
    for i, lang in enumerate(supported_langs, 1):
        logging.info(f"  [{i}] {lang['name']}")

    while True:
        try:
            choice = int(input("请输入选择: ")) - 1
            if 0 <= choice < len(supported_langs):
                shell_lang = supported_langs[choice]

                shell_lang_config = {
                    "is_shell": True,
                    "name": f"{custom_name} (套壳: {shell_lang['name']})",
                    "custom_name": custom_name,
                    "key": shell_lang['key'],
                    "folder_prefix": shell_lang['folder_prefix'],
                    "code": shell_lang['code']
                }
                logging.info(f"已选择套壳模式: {custom_name} 将伪装为 {shell_lang['name']}")
                return shell_lang_config
            else:
                logging.warning("无效选择，请输入列表中的数字。")
        except ValueError:
            logging.warning("无效输入，请输入一个数字。")

def select_auxiliary_glossaries(game_profile):
    """
    选择外挂词典
    """
    from scripts.core.glossary_manager import glossary_manager

    main_glossary_loaded = glossary_manager.load_game_glossary(game_profile['id'])

    if not main_glossary_loaded:
        logging.warning(i18n.t("main_glossary_not_found"))
        return []

    auxiliary_glossaries = glossary_manager.get_auxiliary_glossaries_info()

    if not auxiliary_glossaries:
        if i18n.get_current_language() == "en_US":
            logging.info("No auxiliary glossaries found")
        else:
            logging.info("未找到外挂词典")
        return []

    main_stats = glossary_manager.get_glossary_stats()
    if main_stats['loaded']:
        logging.info(i18n.t("main_glossary_enabled", count=main_stats['total_entries']))
    else:
        if i18n.get_current_language() == "en_US":
            logging.warning("Main glossary not loaded")
        else:
            logging.warning("主词典未加载")

    logging.info(i18n.t("auxiliary_glossaries_detected"))
    for i, glossary in enumerate(auxiliary_glossaries, 1):
        logging.info(i18n.t("auxiliary_glossary_option",
                           index=i,
                           name=glossary['name'],
                           description=glossary['description'],
                           entry_count=glossary['entry_count']))

    logging.info(i18n.t("select_all_auxiliary"))
    logging.info(i18n.t("no_auxiliary_glossary"))

    while True:
        choice = input(i18n.t("enter_auxiliary_choice")).strip().upper()

        if choice == 'N':
            return []
        elif choice == '0':
            return list(range(len(auxiliary_glossaries)))
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(auxiliary_glossaries):
                    return [idx]
                else:
                    logging.warning(i18n.t("invalid_auxiliary_choice"))
            except ValueError:
                logging.warning(i18n.t("invalid_auxiliary_choice"))

def select_fuzzy_matching_mode():
    """
    选择术语模糊匹配模式
    """
    logging.info(i18n.t("fuzzy_matching_mode_prompt"))
    logging.info(i18n.t("fuzzy_matching_strict"))
    logging.info(i18n.t("fuzzy_matching_loose"))
    logging.info(i18n.t("fuzzy_matching_hint"))

    while True:
        choice = input(i18n.t("enter_fuzzy_choice")).strip()

        if choice == "1":
            return "strict"
        elif choice == "2":
            return "loose"
        else:
            logging.warning(i18n.t("invalid_fuzzy_choice"))

def show_project_overview(mod_name, api_provider, game_profile, source_lang, target_languages, auxiliary_glossaries, cleanup_choice, fuzzy_mode):
    """
    显示工程总览并等待用户确认
    """
    logging.info(i18n.t("project_overview_title"))

    logging.info(i18n.t("project_overview_mod", mod_name=mod_name))
    logging.info(i18n.t("project_overview_api", provider=api_provider.capitalize()))
    logging.info(i18n.t("project_overview_game", game_name=game_profile['name']))
    logging.info(i18n.t("project_overview_source", source_lang=source_lang['name']))

    if len(target_languages) == 1:
        target_lang_info = target_languages[0]['name']
    else:
        target_lang_info = i18n.t("target_languages_multiple", count=len(target_languages))
    logging.info(i18n.t("project_overview_target", target_lang=target_lang_info))

    if auxiliary_glossaries:
        glossary_status = i18n.t("glossary_status_combined_auxiliary", count=len(auxiliary_glossaries))
    else:
        from scripts.core.glossary_manager import glossary_manager
        if glossary_manager.current_game_glossary:
            main_count = len(glossary_manager.current_game_glossary.get('entries', []))
            glossary_status = i18n.t("glossary_status_main_only", count=main_count)
        else:
            glossary_status = i18n.t("glossary_status_none")
    logging.info(i18n.t("project_overview_glossary", glossary_status=glossary_status))

    fuzzy_status = i18n.t("fuzzy_matching_status_enabled") if fuzzy_mode == 'loose' else i18n.t("fuzzy_matching_status_disabled")
    logging.info(i18n.t("project_overview_fuzzy_matching", fuzzy_status=fuzzy_status))

    cleanup_status = i18n.t("cleanup_status_yes") if cleanup_choice else i18n.t("cleanup_status_no")
    logging.info(i18n.t("project_overview_cleanup", cleanup_status=cleanup_status))

    while True:
        choice = input(i18n.t("confirm_translation_start")).strip().upper()
        if choice == 'Y':
            logging.info(i18n.t("translation_confirmed"))
            return True
        elif choice == 'N':
            logging.info(i18n.t("returning_to_language_selection"))
            return False
        else:
            logging.warning(i18n.t("invalid_confirm_choice"))

def handle_custom_language_selection():
    """
    处理自定义语言选择
    """
    logging.info(i18n.t("entering_custom_mode"))
    custom_name = input(i18n.t("prompt_custom_lang_name"))
    custom_key = input(i18n.t("prompt_custom_lang_key"))
    custom_prefix = input(i18n.t("prompt_custom_lang_prefix"))

    if custom_name.lower() == "cancel":
        logging.info(i18n.t("custom_language_selection_cancelled"))
        return None

    if not custom_key or not custom_prefix:
        logging.warning(i18n.t("custom_language_selection_incomplete"))
        return None

    custom_lang = {
        "code": "custom", "key": custom_key,
        "name": custom_name, "folder_prefix": custom_prefix
    }
    logging.info(i18n.t("custom_language_selected", name=custom_name, key=custom_key, prefix=custom_prefix))
    return custom_lang

def ask_cleanup_choice(mod_name):
    """
    询问用户是否清理源文件
    """
    logging.info(i18n.t("ask_cleanup_prompt", mod_name=mod_name))
    while True:
        choice = input(i18n.t("enter_cleanup_choice")).strip().upper()
        if choice == 'Y':
            logging.info(i18n.t("cleanup_confirmed"))
            return True
        elif choice == 'N':
            logging.info(i18n.t("cleanup_cancelled"))
            return False
        else:
            logging.warning(i18n.t("invalid_cleanup_choice"))