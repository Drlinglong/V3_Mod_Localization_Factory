# scripts/core/directory_handler.py
import os
import shutil
from utils import i18n
from config import SOURCE_DIR

def select_mod_directory():
    """扫描source_mod目录，让用户选择一个mod文件夹。"""
    print(i18n.t("scan_source_folder", dir=SOURCE_DIR))
    try:
        mod_folders = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
        if not mod_folders:
            print(i18n.t("error_no_mods_found", dir=SOURCE_DIR))
            return None

        print(i18n.t("select_mod_prompt"))
        for i, folder_name in enumerate(mod_folders):
            print(f"  [{i + 1}] {folder_name}")

        while True:
            try:
                # 使用 i18n.t() 来获取输入提示
                choice = int(input(i18n.t("enter_choice_prompt"))) - 1
                if 0 <= choice < len(mod_folders):
                    selected_mod = mod_folders[choice]
                    print(i18n.t("you_selected", mod_name=selected_mod))
                    return selected_mod
                else:
                    print(i18n.t("invalid_input_number"))
            except ValueError:
                print(i18n.t("invalid_input_not_number"))
    except FileNotFoundError:
        print(i18n.t("error_source_folder_not_found", dir=SOURCE_DIR))
        return None
    
def cleanup_source_directory(mod_name, game_profile):
    """清理源mod文件夹，现在会根据游戏档案来决定保护哪些文件。"""
    print(i18n.t("cleanup_start", mod_name=mod_name))

    confirm = input(i18n.t("cleanup_warning_detailed", mod_name=mod_name))
    if confirm.lower() not in ['y', 'yes']:
        print(i18n.t("cleanup_cancelled"))
        return False

    mod_path = os.path.join(SOURCE_DIR, mod_name)
    # 【核心修改】从游戏档案中读取保护名单
    protected_items = game_profile.get('protected_items', set())

    print(i18n.t("cleanup_deleting"))
    try:
        for item in os.listdir(mod_path):
            if item not in protected_items:
                item_path = os.path.join(mod_path, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        print(i18n.t("cleanup_deleted_folder", item=item))
                    else:
                        os.remove(item_path)
                        print(i18n.t("cleanup_deleted_file", item=item))
                except Exception as e:
                    print(i18n.t("cleanup_delete_error", path=item_path, error=e))
        print(i18n.t("cleanup_success"))
        return True # 返回True表示清理成功
    except Exception as e:
        print(i18n.t("cleanup_error", error=e))
        return False # 返回False表示清理失败