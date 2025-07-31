# scripts/main.py

from utils import i18n
from workflows import initial_translate
from core import directory_handler
from config import LANGUAGES

def select_language(prompt_key):
    """显示语言列表并让用户选择一个语言。"""
    print(i18n.t(prompt_key))
    for key, lang_info in LANGUAGES.items():
        print(f"  [{key}] {lang_info['name']}")
    
    while True:
        choice = input(i18n.t("enter_choice_prompt")).strip()
        if choice in LANGUAGES:
            return LANGUAGES[choice]
        else:
            print(i18n.t("invalid_input_number"))

def main_menu():
    """程序主菜单和业务流程调度 (V3.2)。"""
    i18n.load_language()
    
    # 步骤 1: 选择Mod
    selected_mod = directory_handler.select_mod_directory()
    if not selected_mod:
        return

    # 步骤 2: (按你的建议) 在所有操作之前，首先询问是否清理源文件
    directory_handler.cleanup_source_directory(selected_mod)
    
    # 步骤 3: 选择源语言
    source_lang = select_language("select_source_language_prompt")
    
    # 步骤 4: 选择目标语言
    print(i18n.t("select_target_language_prompt"))
    print(f"  [0] {i18n.t('target_option_all')}")
    for key, lang_info in LANGUAGES.items():
        if lang_info['key'] == source_lang['key']:
            print(f"  [{key}] {lang_info['name']} (Source)")
        else:
            print(f"  [{key}] {lang_info['name']}")
    
    target_choice = input(i18n.t("enter_choice_prompt")).strip()

    # 步骤 5: 准备目标语言列表
    target_languages = []
    if target_choice == '0':
        # 批量模式：构建包含所有其他语言的列表
        for key, lang_info in LANGUAGES.items():
            if lang_info['key'] != source_lang['key']:
                target_languages.append(lang_info)
    elif target_choice in LANGUAGES:
        # 单一模式：列表只包含一个元素
        target_lang = LANGUAGES[target_choice]
        if target_lang['key'] == source_lang['key']:
            print(i18n.t("error_same_language"))
            return
        target_languages.append(target_lang)
    else:
        print(i18n.t("invalid_input_number"))
        return

    # 步骤 6: 一次性调用工作流，传入所有需要处理的目标语言
    if target_languages:
        initial_translate.run(selected_mod, source_lang, target_languages)

if __name__ == '__main__':
    main_menu()