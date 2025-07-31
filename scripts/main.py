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
    """程序主菜单和业务流程调度 (V3.0)。"""
    i18n.load_language()
    
    selected_mod = directory_handler.select_mod_directory()
    if not selected_mod:
        return

    # 1. 选择源语言
    source_lang = select_language("select_source_language_prompt")
    
    # 2. 【核心修正】构建并显示新的目标语言菜单
    print(i18n.t("select_target_language_prompt"))
    print(f"  [0] {i18n.t('target_option_all')}")
    for key, lang_info in LANGUAGES.items():
        # 如果是源语言本身，则在后面做出标记
        if lang_info['key'] == source_lang['key']:
            print(f"  [{key}] {lang_info['name']} (Source)")
        else:
            print(f"  [{key}] {lang_info['name']}")
    
    target_choice = input(i18n.t("enter_choice_prompt")).strip()

    # 3. 根据用户的选择执行相应的流程
    if target_choice == '0':
        # “一键翻译十国语言”模式
        print(f"\n模式: 翻译为所有其他语言...")
        for key, target_lang in LANGUAGES.items():
            if target_lang['key'] == source_lang['key']:
                continue # 跳过源语言本身
            initial_translate.run(selected_mod, source_lang, target_lang)
    elif target_choice in LANGUAGES:
        # 一对一翻译模式
        target_lang = LANGUAGES[target_choice]
        if target_lang['key'] == source_lang['key']:
            print(i18n.t("error_same_language"))
            return
        initial_translate.run(selected_mod, source_lang, target_lang)
    else:
        print(i18n.t("invalid_input_number"))

if __name__ == '__main__':
    main_menu()