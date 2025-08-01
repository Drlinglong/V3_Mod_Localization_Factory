# scripts/main.py
import os
import json
from utils import i18n
from workflows import initial_translate
from core import directory_handler
# 【核心修正】在这里把 SOURCE_DIR 也导入进来
from config import LANGUAGES, GAME_PROFILES, SOURCE_DIR

def gather_mod_context(mod_name):
    """读取metadata获取Mod名，并询问用户是否补充上下文。"""
    print("\n--- 正在获取Mod主题上下文 ---")
    mod_official_name = mod_name
    meta_path = os.path.join(SOURCE_DIR, mod_name, '.metadata', 'metadata.json')
    
    try:
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
                if 'name' in meta_data and meta_data['name']:
                    mod_official_name = meta_data['name']
        
        print(f"已识别Mod名称为: '{mod_official_name}'")
        extra_context = input("（可选）请输入关于该Mod主题的额外信息（如'科幻'、'经济'等），或直接按回车跳过: ").strip()
        
        final_context = mod_official_name
        if extra_context:
            final_context += f" ({extra_context})"
            
        print(f"最终使用的主题上下文为: '{final_context}'")
        return final_context
        
    except Exception as e:
        print(f"获取Mod上下文时出错: {e}")
        return mod_name

def select_game_profile():
    """让用户选择一个游戏档案。"""
    print(i18n.t("select_game_profile_prompt"))
    for key, profile in GAME_PROFILES.items():
        print(f"  [{key}] {profile['name']}")
    
    while True:
        choice = input(i18n.t("enter_choice_prompt")).strip()
        if choice in GAME_PROFILES:
            return GAME_PROFILES[choice]
        else:
            print(i18n.t("invalid_input_number"))

def select_language(prompt_key, source_lang_key=None):
    """显示语言列表并让用户选择一个语言。"""
    print(i18n.t(prompt_key))
    
    if prompt_key == "select_target_language_prompt":
        print(f"  [0] {i18n.t('target_option_all')}")

    for key, lang_info in LANGUAGES.items():
        if source_lang_key and lang_info['key'] == source_lang_key:
            print(f"  [{key}] {lang_info['name']} (Source)")
        else:
            print(f"  [{key}] {lang_info['name']}")
    
    allowed_choices = list(LANGUAGES.keys())
    if prompt_key == "select_target_language_prompt":
        allowed_choices.append('0')

    while True:
        choice = input(i18n.t("enter_choice_prompt")).strip().lower()
        if choice in allowed_choices:
            return choice
        else:
            print(i18n.t("invalid_input_number"))

def main_menu():
    """【最终版】程序主菜单和业务流程调度。"""
    i18n.load_language()
    
    selected_game_profile = select_game_profile()
    selected_mod = directory_handler.select_mod_directory()
    if not selected_mod: return

    mod_context = gather_mod_context(selected_mod)

    directory_handler.cleanup_source_directory(selected_mod)
    source_lang_choice = select_language("select_source_language_prompt")
    source_lang = LANGUAGES[source_lang_choice]
    target_choice = select_language("select_target_language_prompt", source_lang['key'])

    target_languages = []
    if target_choice == '0':
        for key, lang_info in LANGUAGES.items():
            if lang_info['key'] != source_lang['key']:
                target_languages.append(lang_info)
    elif target_choice in LANGUAGES:
        target_lang = LANGUAGES[target_choice]
        if target_lang['key'] == source_lang['key']:
            print(i18n.t("error_same_language"))
            return
        target_languages.append(target_lang)
    
    if target_languages:
        initial_translate.run(selected_mod, source_lang, target_languages, selected_game_profile, mod_context)

if __name__ == '__main__':
    main_menu()