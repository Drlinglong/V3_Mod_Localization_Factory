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
import importlib.util

# --- 路径修复与环境设置 ---
def _setup_portable_environment():
    """
    检测并设置便携式环境
    如果检测到便携式环境，将packages目录添加到Python路径中
    """
    # 检测便携式环境：检查是否存在packages目录
    packages_dir = None
    
    # 检查当前目录
    if os.path.exists('packages'):
        packages_dir = os.path.abspath('packages')
    # 检查上级目录（当在app目录下运行时）
    elif os.path.exists('../packages'):
        packages_dir = os.path.abspath('../packages')
    
    if packages_dir and packages_dir not in sys.path:
        sys.path.insert(0, packages_dir)
        print(f"[INFO] 便携式环境检测到，已添加依赖包路径: {packages_dir}")

# 在所有导入之前首先设置环境
_setup_portable_environment()

try:
    # The path to this file (main.py) is .../app/scripts/main.py
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(scripts_dir)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
except Exception:
    # 在某些环境下 __file__ 可能不可用，使用备用方案
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

from scripts.utils import i18n, logger
from scripts.utils.banner import print_banner
from scripts.workflows import initial_translate
from scripts.core import directory_handler
from scripts.core.glossary_manager import glossary_manager
from scripts.ui import menu_handler # 导入新的UI模块
from scripts.app_settings import SOURCE_DIR

def main_menu_workflow():
    """
    主菜单工作流，循环运行直到用户选择退出。
    """
    while True:
        # --- 1. 用户交互阶段 ---
        # 所有菜单交互都委托给 menu_handler
        game_profile = menu_handler.select_game_profile()
        if not game_profile: return

        api_provider = menu_handler.select_api_provider()
        if not api_provider: return

        mods = directory_handler.scan_source_directory(SOURCE_DIR)
        if not mods:
            return

        mod_name = directory_handler.select_mod(mods)
        if not mod_name: return
        
        cleanup_choice = menu_handler.ask_cleanup_choice(mod_name)
        mod_context = menu_handler.gather_mod_context(mod_name)
        source_lang = menu_handler.select_language("select_source_language_prompt", game_profile)
        if not source_lang: return

        target_languages = menu_handler.select_target_languages(game_profile, source_lang)
        if not target_languages: return

        auxiliary_glossaries_indices = menu_handler.select_auxiliary_glossaries(game_profile)
        fuzzy_mode = menu_handler.select_fuzzy_matching_mode()

        # --- 2. 工程总览与确认 ---
        user_confirmed = menu_handler.show_project_overview(
            mod_name, api_provider, game_profile, source_lang, target_languages,
            auxiliary_glossaries_indices, cleanup_choice, fuzzy_mode
        )

        if not user_confirmed:
            continue # 用户选择“否”，返回主菜单

        # --- 3. 核心逻辑执行阶段 ---
        # 根据用户的选择，编排和执行核心工作流
        
        # 3.1 清理
        if cleanup_choice:
            logging.info(i18n.t("executing_cleanup"))
            directory_handler.cleanup_source_directory(mod_name, game_profile)
            logging.info(i18n.t("cleanup_completed"))

        # 3.2 词典加载
        glossary_manager.set_fuzzy_matching_mode(fuzzy_mode)
        if auxiliary_glossaries_indices:
            glossary_manager.load_auxiliary_glossaries(auxiliary_glossaries_indices)
        
        # 显示最终的词典状态
        final_glossary_status = glossary_manager.get_glossary_status_summary()
        logging.info(i18n.t("glossary_status_display", status=final_glossary_status))
        
        # 3.3 执行翻译工作流
        initial_translate.run(
            mod_name=mod_name,
            source_lang=source_lang,
            target_languages=target_languages,
            game_profile=game_profile,
            mod_context=mod_context,
            selected_provider=api_provider
        )

        logging.info(i18n.t("workflow_completed_ask_next"))
        choice = input(i18n.t("enter_workflow_completed_choice")).strip().upper()
        if choice != 'Y':
            break # 结束循环

def main():
    """主函数 - 应用程序的入口点"""
    try:
        # --- 初始化阶段 ---
        print_banner()
        logger.setup_logger()
        menu_handler.display_version_info()
        
        interface_lang = menu_handler.select_interface_language()
        i18n.load_language(interface_lang)

        # --- 环境自检 ---
        if not menu_handler.preflight_checks():
            # 如果自检失败，可以选择是否退出
            if input(i18n.t("preflight_failed_ask_continue")).strip().upper() != 'Y':
                return

        # --- 进入主菜单循环 ---
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