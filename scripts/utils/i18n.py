# scripts/utils/i18n.py
import json
import os
import logging

_strings = {}
_default_lang = 'zh_CN'  # 设置默认语言为中文
_language_loaded = False  # 添加标志，避免重复加载
_current_lang = 'zh_CN'  # 当前语言代码

def load_language(lang_code=None):
    """加载语言文件，如果未指定则显示语言选择菜单。"""
    global _strings, _language_loaded, _current_lang
    
    # 如果已经加载过语言，直接返回
    if _language_loaded and _strings:
        return True
    
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
    
    # 获取项目根目录的路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    lang_file_path = os.path.join(project_root, 'data', 'lang', f'{lang_code}.json')

    try:
        with open(lang_file_path, 'r', encoding='utf-8') as f:
            _strings = json.load(f)
        _language_loaded = True  # 设置标志
        _current_lang = lang_code  # 设置当前语言
        try:
            logging.info(i18n.t("language_loaded", lang_code=lang_code))
        except:
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
            _language_loaded = True  # 设置标志
            _current_lang = lang_code  # 设置当前语言
            return False

def t(key, **kwargs):
    """获取翻译后的字符串。"""
    # 检查键是否存在
    if key not in _strings:
        # 记录缺失的键，帮助调试
        logging.warning(f"国际化键缺失: '{key}'，当前语言文件包含 {len(_strings)} 个键")
        
        # 提供更有用的备用值
        if key in ['processing_metadata', 'translating_mod_name', 'metadata_success', 
                   'processing_assets', 'asset_copied', 'parsing_file', 'extracted_texts', 'writing_file_success']:
            # 这些是重要的键，提供硬编码的备用值
            fallback_values = {
                'processing_metadata': '正在处理 metadata.json',
                'translating_mod_name': '正在翻译 mod name',
                'metadata_success': 'metadata.json 处理完成',
                'processing_assets': '正在处理资产文件',
                'asset_copied': '资产文件复制完成',
                'parsing_file': '正在解析文件',
                'extracted_texts': '提取到可翻译文本',
                'writing_file_success': '文件写入成功'
            }
            return fallback_values.get(key, f"[缺失键: {key}]")
        else:
            return f"[缺失键: {key}]"
    
    try:
        # 尝试格式化字符串
        return _strings[key].format(**kwargs)
    except KeyError as e:
        # 如果格式化失败，记录错误并返回原始值
        logging.error(f"国际化键 '{key}' 格式化失败，缺少参数: {e}")
        return _strings[key]
    except Exception as e:
        # 其他错误
        logging.error(f"国际化键 '{key}' 处理失败: {e}")
        return f"[错误: {key}]"

def get_current_language():
    """获取当前语言代码"""
    return _current_lang