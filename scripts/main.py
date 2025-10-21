# scripts/main.py
# ---------------------------------------------------------------
"""
项目主入口点 (已重构)

这个文件是应用程序的“总开关”。它的职责有且仅有三件：
1. 初始化环境（日志、国际化等）。
2. 调用 menu_handler 显示主菜单并获取用户的所有选择。
3. 根据用户的选择，调用相应的工作流模块来执行核心任务。
"""

import os
import sys
import logging
from typing import List, Optional

# --- 路径修复与环境设置 ---
def _setup_portable_environment():
    """
    检测并设置便携式环境
    如果检测到便携式环境，将packages目录添加到Python路径中
    """
    packages_dir = None
    if os.path.exists('packages'):
        packages_dir = os.path.abspath('packages')
    elif os.path.exists('../packages'):
        packages_dir = os.path.abspath('../packages')
    
    if packages_dir and packages_dir not in sys.path:
        sys.path.insert(0, packages_dir)
        print(f"[INFO] 便携式环境检测到，已添加依赖包路径: {packages_dir}")

_setup_portable_environment()

try:
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(scripts_dir)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
except Exception:
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

from scripts.utils import i18n, logger
from scripts.utils.banner import print_banner
from scripts.workflows import initial_translate
from scripts.core import directory_handler
from scripts.core.glossary_manager import glossary_manager
from scripts.core.archive_manager import archive_manager
from scripts.core import workshop_handler
from scripts.ui import menu_handler
from scripts.app_settings import SOURCE_DIR

def main_menu_workflow():
    """
    主菜单工作流，循环运行直到用户选择退出。
    """
    while True:
        # --- 1. 用户交互阶段 ---
        game_profile = menu_handler.select_game_profile()
        if not game_profile: return

        api_provider = menu_handler.select_api_provider()
        if not api_provider: return

        mods = directory_handler.scan_source_directory(SOURCE_DIR)
        if not mods: return

        mod_name = directory_handler.select_mod(mods)
        if not mod_name: return
        
        cleanup_choice = menu_handler.ask_cleanup_choice(mod_name)
        mod_context = menu_handler.gather_mod_context(mod_name)
        source_lang = menu_handler.select_language("select_source_language_prompt", game_profile)
        if not source_lang: return

        target_languages = menu_handler.select_language("select_target_language_prompt", game_profile, source_lang)
        if not target_languages: return

        # NEW: Glossary and Workshop ID handling
        selected_glossary_ids = menu_handler.select_glossaries_from_db(game_profile)
        fuzzy_mode = menu_handler.select_fuzzy_matching_mode()
        
        # --- 2. 核心逻辑预处理 (ID获取) ---
        # Step 1: Try to auto-extract the ID
        workshop_id_info = workshop_handler.try_auto_extract_workshop_id(mod_name, game_profile)
        
        # Step 2: If auto-extraction fails, prompt the user manually
        if workshop_id_info['status'] == 'not_found':
            manual_id = menu_handler.prompt_for_manual_workshop_id()
            if manual_id:
                workshop_id_info = {'id': manual_id, 'status': 'manual'}

        final_remote_id = workshop_id_info['id']

        # --- 3. 工程总览与确认 ---
        user_confirmed = menu_handler.show_project_overview(
            mod_name, api_provider, game_profile, source_lang, target_languages,
            selected_glossary_ids, cleanup_choice, fuzzy_mode, workshop_id_info
        )

        if not user_confirmed:
            continue

        # --- 4. 核心逻辑执行阶段 ---
        
        # 4.1 清理
        if cleanup_choice:
            logging.info(i18n.t("executing_cleanup"))
            directory_handler.cleanup_source_directory(mod_name, game_profile)
            logging.info(i18n.t("cleanup_completed"))

        # 4.2 存档ID获取
        mod_id_for_archive = None
        if final_remote_id:
            mod_id_for_archive = archive_manager.get_or_create_mod_entry(mod_name, final_remote_id)

        # 4.3 词典加载
        glossary_manager.set_fuzzy_matching_mode(fuzzy_mode)
        
        # 4.4 执行翻译工作流
        initial_translate.run(
            mod_name=mod_name,
            source_lang=source_lang,
            target_languages=target_languages,
            game_profile=game_profile,
            mod_context=mod_context,
            selected_provider=api_provider,
            selected_glossary_ids=selected_glossary_ids, # Pass the selected IDs
            mod_id_for_archive=mod_id_for_archive # Pass the archive mod_id
        )

        logging.info(i18n.t("workflow_completed_ask_next"))
        choice = input(i18n.t("enter_workflow_completed_choice")).strip().upper()
        if choice != 'Y':
            break

def main():
    """主函数 - 应用程序的入口点"""
    try:
        print_banner()
        logger.setup_logger()
        menu_handler.display_version_info()
        
        interface_lang = menu_handler.select_interface_language()
        i18n.load_language(interface_lang)

        if not menu_handler.preflight_checks():
            if input(i18n.t("preflight_failed_ask_continue", default='N')).strip().upper() != 'Y':
                return

        main_menu_workflow()

        logging.info(i18n.t("program_exit_thank_you"))

    except KeyboardInterrupt:
        print("\n")
        logging.info(i18n.t("program_exit_interrupt"))
    except Exception as e:
        logging.exception(f"程序运行时发生未处理的异常: {e}")
        try:
            logging.error(i18n.t("unexpected_error_see_logs"))
        except:
            print(f"An unexpected error occurred: {e}. Please check the logs for details.")
    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
