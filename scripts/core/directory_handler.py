# scripts/core/directory_handler.py
import os
import shutil
import sys

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.utils import i18n
from scripts.config import SOURCE_DIR
# ↓↓↓ nowo dodane importy ↓↓↓
from scripts.utils.text_clean import strip_pl_diacritics
# ↑↑↑------------------------↑↑↑
import logging


def select_mod_directory():
    """扫描source_mod目录，让用户选择一个mod文件夹。"""
    # 检查源目录是否存在
    if not os.path.exists(SOURCE_DIR):
        logging.error(f"源目录不存在: {SOURCE_DIR}")
        logging.error("请确保以下任一条件满足：")
        logging.error("1. 在项目根目录下运行程序")
        logging.error("2. source_mod 文件夹存在且包含mod文件")
        logging.error("3. 检查文件夹名称是否正确（应为 'source_mod'）")
        return None
    
    logging.info(i18n.t("scan_source_folder", dir=SOURCE_DIR))
    try:
        mod_folders = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
        if not mod_folders:
            logging.error(i18n.t("error_no_mods_found", dir=SOURCE_DIR))
            logging.error("请在 source_mod 文件夹中添加要翻译的mod文件夹")
            return None

        logging.info(i18n.t("select_mod_prompt"))
        for i, folder_name in enumerate(mod_folders):
            logging.info(f"  [{i + 1}] {folder_name}")

        while True:
            try:
                choice = int(input(i18n.t("enter_choice_prompt"))) - 1
                if 0 <= choice < len(mod_folders):
                    selected_mod = mod_folders[choice]
                    logging.info(i18n.t("you_selected", mod_name=selected_mod))
                    return selected_mod
                else:
                    logging.warning(i18n.t("invalid_input_number"))
            except ValueError:
                logging.warning(i18n.t("invalid_input_not_number"))
    except FileNotFoundError:
        logging.error(i18n.t("error_source_folder_not_found", dir=SOURCE_DIR))
        return None
    except PermissionError:
        logging.error(f"权限不足，无法访问目录: {SOURCE_DIR}")
        return None
    except Exception as e:
        logging.error(f"扫描目录时发生未知错误: {e}")
        return None


def cleanup_source_directory(mod_name, game_profile):
    """清理源mod文件夹，现在会根据游戏档案来决定保护哪些文件。"""
    logging.info(i18n.t("cleanup_start", mod_name=mod_name))

    confirm = input(i18n.t("cleanup_warning_detailed", mod_name=mod_name))
    if confirm.lower() not in ['y', 'yes']:
        logging.info(i18n.t("cleanup_cancelled"))
        return False

    mod_path = os.path.join(SOURCE_DIR, mod_name)
    protected_items = game_profile.get('protected_items', set())

    logging.info(i18n.t("cleanup_deleting"))
    try:
        for item in os.listdir(mod_path):
            if item not in protected_items:
                item_path = os.path.join(mod_path, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        logging.info(i18n.t("cleanup_deleted_folder", item=item))
                    else:
                        os.remove(item_path)
                        logging.info(i18n.t("cleanup_deleted_file", item=item))
                except Exception as e:
                    logging.error(i18n.t("cleanup_delete_error", path=item_path, error=e))
        logging.info(i18n.t("cleanup_success"))
        return True
    except Exception as e:
        logging.error(i18n.t("cleanup_error", error=e))
        return False


# ────────────────────────────────────────────────────────────────
# ↓↓↓        NOWA FUNKCJA – zapis plików tłumaczenia        ↓↓↓
# ────────────────────────────────────────────────────────────────
def write_localisation_file(dest_path: str, content: str, game_profile: dict):
    """
    Zapisuje przetłumaczony plik lokalizacji z uwzględnieniem
    specyfiki gry (ANSI vs UTF-8, usuwanie ogonków dla EU4).

    Parametry:
        dest_path    – pełna ścieżka docelowa
        content      – tekst po tłumaczeniu
        game_profile – słownik z config.GAME_PROFILES[...]
    """
    # 1) EU4 → zdejmujemy diakrytyki, inne gry bez zmian
    if game_profile.get("strip_pl_diacritics", False):
        content = strip_pl_diacritics(content)

    # 2) wybór kodowania (EU4: cp1252, reszta: utf-8)
    encoding = game_profile.get("encoding", "utf-8")

    # 3) upewniamy się, że folder docelowy istnieje
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # 4) zapis
    with open(dest_path, "w", encoding=encoding, newline="") as f:
        f.write(content)
