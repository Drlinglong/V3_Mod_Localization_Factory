# scripts/utils/i18n.py
import json
import os
import logging

_strings = {}
_default_lang = 'zh_CN'  # 设置默认语言为中文

def load_language(lang_code=None):
    """加载语言文件，如果未指定则显示语言选择菜单。"""
    global _strings
    
    if lang_code is None:
        # 显示语言选择菜单
        try:
            print("=" * 50)
            print("🌍 请选择界面语言 / Please select interface language")
            print("=" * 50)
            print("1. English")
            print("2. 中文 (简体)")
            print("=" * 50)
            
            while True:
                try:
                    lang_choice = input("请输入选择 (1 或 2) / Enter choice (1 or 2): ").strip()
                    if lang_choice == '1':
                        lang_code = 'en_US'
                        break
                    elif lang_choice == '2':
                        lang_code = 'zh_CN'
                        break
                    else:
                        print("❌ 无效选择，请输入 1 或 2 / Invalid choice, please enter 1 or 2")
                except (EOFError, KeyboardInterrupt):
                    # 如果用户按Ctrl+C或遇到输入问题，使用默认语言
                    print("\n⚠️  使用默认语言 / Using default language")
                    lang_code = _default_lang
                    break
        except Exception as e:
            logging.warning(f"Language selection failed, using default: {e}")
            lang_code = _default_lang
    
    lang_file_path = os.path.join('data', 'lang', f'{lang_code}.json')

    try:
        with open(lang_file_path, 'r', encoding='utf-8') as f:
            _strings = json.load(f)
        logging.info(f"Language loaded: {lang_code}")
        return True
    except Exception as e:
        logging.error(f"Error loading language file {lang_file_path}: {e}")
        # 如果加载失败，尝试加载默认语言
        if lang_code != _default_lang:
            return load_language(_default_lang)
        else:
            # 最后的备用方案：使用硬编码的英文
            _strings = {
                "scan_source_folder": "--- Scanning source folder [{dir}] ---",
                "select_mod_prompt": "Please select a mod to translate:",
                "you_selected": "You selected: {mod_name}",
                "invalid_input_number": "Invalid input, please enter a number from the list.",
                "invalid_input_not_number": "Invalid input, please enter a number.",
                "error_no_mods_found": "Error: No mod folders found in '{dir}' directory.",
                "error_source_folder_not_found": "Error: Source folder '{dir}' does not exist.",
                "enter_choice_prompt": "Please enter your choice: ",
                "cleanup_start": "--- Starting source mod folder cleanup: {mod_name} ---",
                "cleanup_warning_detailed": "Warning: This operation will permanently delete all files and folders in source folder '{mod_name}', except '.metadata', 'localization', and 'thumbnail.png'.\nThis helps save disk space after translation.\nDo you want to continue? (Enter 'y' or 'yes' to confirm): ",
                "cleanup_cancelled": "Operation cancelled.",
                "cleanup_deleting": "Deleting non-essential files and folders...",
                "cleanup_success": "Source folder cleanup completed!",
                "select_game_profile_prompt": "Please select a game:",
                "select_api_provider_prompt": "Please select API provider:",
                "workflow_completed": "Workflow completed!"
            }
            return False

def t(key, **kwargs):
    """获取翻译后的字符串。"""
    if not _strings:
        load_language()  # 如果还没有加载语言，自动加载
    
    # 提供一个备用值，防止因字典key不存在而崩溃
    return _strings.get(key, f"<{key}>").format(**kwargs)