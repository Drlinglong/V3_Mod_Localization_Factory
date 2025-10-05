# scripts/main.py
import os
import sys
import json
import argparse
import logging
import re
import subprocess
import importlib.util

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 现在，我们使用全新的、从 "scripts." 开始的“绝对路径”来导入
from scripts.utils import i18n, logger
from scripts.workflows import initial_translate
from scripts.core import directory_handler
from scripts.config import LANGUAGES, GAME_PROFILES, SOURCE_DIR, API_PROVIDERS, PROJECT_INFO

def display_version_info():
    """显示项目版本信息"""
    print("=" * 60)
    print(f"🎯 {PROJECT_INFO['display_name']}")
    print(f"🔧 {PROJECT_INFO['engineering_name']}")
    print(f"📦 版本version: {PROJECT_INFO['version']}")
    print(f"📅 最后更新last update: {PROJECT_INFO['last_update']}")
    print(f"{PROJECT_INFO['copyright']}")
    print("=" * 60)

def display_banner():
    """显示项目横幅"""
    try:
        if os.path.exists("banner.txt"):
            with open("banner.txt", "r", encoding="utf-8") as f:
                banner_content = f.read()
                print(banner_content)
        else:
            # 默认横幅
            print("=" * 60)
            print("         Project Remis - 蕾姆丝计划")
            print("=" * 60)
    except Exception as e:
        logging.warning(f"显示横幅时出错: {e}")
        print("=" * 60)
        print("         Project Remis - 蕾姆丝计划")
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
    required_files = ["scripts/main.py", "scripts/config.py", "data/lang/zh_CN.json", "data/lang/en_US.json"]
    
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
        import subprocess
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
        # 简洁的成功信息
        lib_names = ", ".join(available_libraries)
        key_count = len(available_keys)
        print(f"✅ {i18n.t('preflight_success', libs=lib_names, keys=key_count, mods=mod_count)}")
    else:
        # 详细的错误信息
        print(f"❌ {i18n.t('preflight_failed')}:")
        for msg in error_messages:
            print(f"   - {msg}")
        print(f"\n{i18n.t('preflight_retry_prompt')}")
    
    return checks_passed

def select_api_provider():
    """【新】显示API供应商列表并让用户选择。"""
    logging.info(i18n.t("select_api_provider_prompt")) # 需要在语言文件里新增词条
    
    provider_options = list(API_PROVIDERS.keys())
    
    for i, key in enumerate(provider_options):
        if key == "qwen":
            # 为Qwen添加特殊提示
            logging.info(f"  [{i + 1}] {key.capitalize()} - {i18n.t('qwen_china_hint')}")
        elif key == "deepseek":
            # 为Deepseek添加特殊提示
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
    This context is then used in the API prompt to improve translation quality.
    """
    logging.info(i18n.t("getting_mod_context"))
    mod_official_name = mod_name  # Fallback to folder name
    meta_path = os.path.join(SOURCE_DIR, mod_name, '.metadata', 'metadata.json')
    descriptor_path = os.path.join(SOURCE_DIR, mod_name, 'descriptor.mod')

    try:
        if os.path.exists(meta_path): # V3-style metadata
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
                if 'name' in meta_data and meta_data['name']:
                    mod_official_name = meta_data['name']
        elif os.path.exists(descriptor_path): # Stellaris/HOI4/EU4/CK3-style metadata
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
        return mod_name # Fallback to folder name on error

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
    for i, (key, profile) in enumerate(GAME_PROFILES.items()):
        logging.info(f"  [{i + 1}] {profile['name']}")
    
    while True:
        choice = input(i18n.t("enter_choice_prompt")).strip()
        if choice in GAME_PROFILES:
            return GAME_PROFILES[choice]
        else:
            logging.warning(i18n.t("invalid_input_number"))

def select_language(prompt_key, game_profile, source_lang_key=None):
    """
    Displays a language selection menu based on the chosen game profile.
    Can be used for selecting both source and target languages.
    """
    logging.info(i18n.t(prompt_key))
    
    # Filter languages based on game profile support
    supported_langs = [LANGUAGES[key] for key in game_profile['supported_language_keys']]
    
    for i, lang in enumerate(supported_langs, 1):
        logging.info(f"  [{i}] {lang['name']}")
    
    while True:
        try:
            choice = int(input(i18n.t("enter_choice_prompt"))) - 1
            if 0 <= choice < len(supported_langs):
                return supported_langs[choice]
            else:
                logging.warning(i18n.t("invalid_input_number"))
        except ValueError:
            logging.warning(i18n.t("invalid_input_not_number"))

def select_auxiliary_glossaries(game_profile):
    """
    选择外挂词典
    
    Args:
        game_profile: 游戏配置
        
    Returns:
        List[int]: 选中的外挂词典索引列表
    """
    from scripts.core.glossary_manager import glossary_manager
    
    # 先加载主词典以获取游戏ID
    main_glossary_loaded = glossary_manager.load_game_glossary(game_profile['id'])
    
    if not main_glossary_loaded:
        logging.warning(i18n.t("main_glossary_not_found"))
        return []
    
    # 获取外挂词典信息
    auxiliary_glossaries = glossary_manager.get_auxiliary_glossaries_info()
    
    if not auxiliary_glossaries:
        if i18n.get_current_language() == "en_US":
            logging.info("No auxiliary glossaries found")
        else:
            logging.info("未找到外挂词典")
        return []
    
    # 显示主词典状态
    main_stats = glossary_manager.get_glossary_stats()
    if main_stats['loaded']:
        logging.info(i18n.t("main_glossary_enabled", count=main_stats['total_entries']))
    else:
        if i18n.get_current_language() == "en_US":
            logging.warning("Main glossary not loaded")
        else:
            logging.warning("主词典未加载")
    
    # 显示外挂词典选项
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
    
    Returns:
        str: 选择的模式 ('strict' 或 'loose')
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
    
    Args:
        mod_name: MOD名称
        api_provider: API供应商
        game_profile: 游戏配置
        source_lang: 源语言
        target_languages: 目标语言列表
        auxiliary_glossaries: 外挂词典信息
        cleanup_choice: 是否清理源文件
        fuzzy_mode: 模糊匹配模式
        
    Returns:
        bool: 用户是否确认开始翻译
    """
    logging.info(i18n.t("project_overview_title"))
    
    # 显示基本信息
    logging.info(i18n.t("project_overview_mod", mod_name=mod_name))
    logging.info(i18n.t("project_overview_api", provider=api_provider.capitalize()))
    logging.info(i18n.t("project_overview_game", game_name=game_profile['name']))
    logging.info(i18n.t("project_overview_source", source_lang=source_lang['name']))
    
    # 显示目标语言
    if len(target_languages) == 1:
        target_lang_info = target_languages[0]['name']
    else:
        target_lang_info = i18n.t("target_languages_multiple", count=len(target_languages))
    logging.info(i18n.t("project_overview_target", target_lang=target_lang_info))
    
    # 显示词典配置
    if auxiliary_glossaries:
        glossary_status = i18n.t("glossary_status_combined_auxiliary", count=len(auxiliary_glossaries))
    else:
        # 获取主词典的条目数量
        from scripts.core.glossary_manager import glossary_manager
        if glossary_manager.current_game_glossary:
            main_count = len(glossary_manager.current_game_glossary.get('entries', []))
            glossary_status = i18n.t("glossary_status_main_only", count=main_count)
        else:
            glossary_status = i18n.t("glossary_status_none")
    logging.info(i18n.t("project_overview_glossary", glossary_status=glossary_status))
    
    # 显示模糊匹配状态
    fuzzy_status = i18n.t("fuzzy_matching_status_enabled") if fuzzy_mode == 'loose' else i18n.t("fuzzy_matching_status_disabled")
    logging.info(i18n.t("project_overview_fuzzy_matching", fuzzy_status=fuzzy_status))
    
    # 显示清理状态
    cleanup_status = i18n.t("cleanup_status_yes") if cleanup_choice else i18n.t("cleanup_status_no")
    logging.info(i18n.t("project_overview_cleanup", cleanup_status=cleanup_status))
    
    # 等待用户确认
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
    
    Returns:
        dict or None: 自定义语言字典，如果用户选择取消则返回 None
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
    
    Args:
        mod_name: MOD名称
        
    Returns:
        bool: 用户是否选择清理
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

def main():
    """Main function."""
    # 初始化日志系统
    logger.setup_logger()
    
    # 显示横幅
    display_banner()
    
    # 显示版本信息
    display_version_info()
    
    # 选择界面语言
    interface_lang = select_interface_language()
    if not interface_lang:
        return
    
    # 加载语言文件
    i18n.load_language(interface_lang)
    
    # 执行开机自检
    preflight_checks()
    # 注意：自检失败不再阻止程序继续运行，让用户自行决定
    
    # 选择游戏配置
    game_profile = select_game_profile()
    if not game_profile:
        return
    
    # 选择API供应商
    api_provider = select_api_provider()
    if not api_provider:
        return
    
    # 扫描源目录
    mods = directory_handler.scan_source_directory(SOURCE_DIR)
    if not mods:
        logging.error(i18n.t("error_no_mods_found", dir=SOURCE_DIR))
        return
    
    # 选择MOD
    mod_name = directory_handler.select_mod(mods)
    if not mod_name:
        return
    
    # 询问是否清理源文件
    cleanup_choice = ask_cleanup_choice(mod_name)
    
    # 获取MOD上下文
    mod_context = gather_mod_context(mod_name)
    
    # 选择源语言
    source_lang = select_language("select_source_language_prompt", game_profile)
    if not source_lang:
        return
    
    # 选择目标语言
    target_languages = []
    while True:
        logging.info(i18n.t("select_target_language_prompt"))
        
        # 显示选项
        if len(game_profile['supported_language_keys']) > 1:
            # 排除源语言
            available_targets = []
            for key in game_profile['supported_language_keys']:
                lang = LANGUAGES[key]
                if lang['code'] != source_lang['code']:
                    available_targets.append(lang)
            
            # 先显示"全部语言"选项
            all_langs_count = len(available_targets)
            logging.info(f"  [0] {i18n.t('target_option_all_dynamic', count=all_langs_count)}")
            
            # 再显示"自定义"选项
            logging.info(f"  [c] {i18n.t('target_option_custom')}")
            
            # 最后显示具体语言选项（排除源语言）
            for i, lang in enumerate(available_targets, 1):
                logging.info(f"  [{i}] {lang['name']}")
            
            choice = input(i18n.t("enter_choice_prompt")).strip()
            
            if choice == "0":
                # 选择所有语言
                target_languages = available_targets
                break
            elif choice.lower() == "c":
                # 自定义语言模式
                custom_lang = handle_custom_language_selection()
                if custom_lang:
                    target_languages = [custom_lang]
                    break
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(available_targets):
                        target_languages = [available_targets[idx]]
                        break
                    else:
                        logging.warning(i18n.t("invalid_input_number"))
                except ValueError:
                    logging.warning(i18n.t("invalid_input_not_number"))
        else:
            # 只有一种语言的情况
            target_languages = [source_lang]
            break
    
    if not target_languages:
        return
    
    # 选择外挂词典
    auxiliary_glossaries = select_auxiliary_glossaries(game_profile)
    
    # 选择术语模糊匹配模式
    fuzzy_mode = select_fuzzy_matching_mode()
    
    # 显示工程总览并等待确认
    if not show_project_overview(mod_name, api_provider, game_profile, source_lang, target_languages, auxiliary_glossaries, cleanup_choice, fuzzy_mode):
        # 用户选择返回，重新开始
        main()
        return
    
    # 如果用户选择清理源文件，立即执行清理
    if cleanup_choice:
        logging.info(i18n.t("executing_cleanup"))
        directory_handler.cleanup_source_directory(mod_name, game_profile)
        logging.info(i18n.t("cleanup_completed"))
    
    # 加载选中的外挂词典
    from scripts.core.glossary_manager import glossary_manager
    
    # 设置术语模糊匹配模式
    glossary_manager.set_fuzzy_matching_mode(fuzzy_mode)
    
    # 检查词典状态
    if auxiliary_glossaries:
        success = glossary_manager.load_auxiliary_glossaries(auxiliary_glossaries)
        if success:
            logging.info(i18n.t("auxiliary_glossaries_loaded", count=len(auxiliary_glossaries)))
        else:
            logging.warning(i18n.t("auxiliary_glossary_load_failed"))
    
    # 最终检查词典状态
    if not glossary_manager.has_any_glossary():
        logging.warning(i18n.t("no_glossaries_available"))
    else:
        glossary_status_info = glossary_manager.get_glossary_status_summary()
        # 使用返回的键名和参数进行国际化
        if glossary_status_info["key"] == "glossary_status_main_plus_aux":
            status_text = i18n.t(glossary_status_info["key"], 
                                main_count=glossary_status_info["main_count"],
                                aux_count=glossary_status_info["aux_count"],
                                total_count=glossary_status_info["total_count"])
        elif glossary_status_info["key"] == "glossary_status_main_only":
            status_text = i18n.t(glossary_status_info["key"], 
                                count=glossary_status_info["count"])
        elif glossary_status_info["key"] == "glossary_status_aux_only":
            status_text = i18n.t(glossary_status_info["key"], 
                                aux_count=glossary_status_info["aux_count"])
        else:
            status_text = i18n.t(glossary_status_info["key"])
        
        logging.info(i18n.t("glossary_status_display", status=status_text))
    
    # 开始翻译工作流
    initial_translate.run(
        mod_name=mod_name,
        source_lang=source_lang,
        target_languages=target_languages,
        game_profile=game_profile,
        mod_context=mod_context,
        selected_provider=api_provider
    )

if __name__ == '__main__':
    # 确保日志系统和国际化系统正确初始化
    try:
        # 运行主菜单
        main()
        
        logging.info(i18n.t("workflow_completed"))
        
    except Exception as e:
        print(f"程序运行时发生错误: {e}")
        logging.exception("程序运行时发生未处理的异常")
        sys.exit(1)