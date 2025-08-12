# scripts/main.py
import os
import re
import json
import argparse
import logging
from utils import i18n, logger
from workflows import initial_translate
from core import directory_handler
from config import LANGUAGES, GAME_PROFILES, SOURCE_DIR

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

def select_game_profile():
    """Displays a menu for the user to select a game profile."""
    print(i18n.t("select_game_profile_prompt"))
    for key, profile in GAME_PROFILES.items():
        print(f"  [{key}] {profile['name']}")
    
    while True:
        choice = input(i18n.t("enter_choice_prompt")).strip()
        if choice in GAME_PROFILES:
            return GAME_PROFILES[choice]
        else:
            print(i18n.t("invalid_input_number"))

def select_language(prompt_key, game_profile, source_lang_key=None):
    """
    Displays a language selection menu based on the chosen game profile.
    Can be used for selecting both source and target languages.
    """
    print(i18n.t(prompt_key))
    
    supported_languages = {key: LANGUAGES[key] for key in game_profile.get("supported_language_keys", []) if key in LANGUAGES}
    
    # For the target language menu, add the "all" and "custom" options
    if prompt_key == "select_target_language_prompt":
        print(f"  [0] {i18n.t('target_option_all_dynamic', count=len(supported_languages) - 1)}")

    for key, lang_info in supported_languages.items():
        if source_lang_key and lang_info['key'] == source_lang_key:
            print(f"  [{key}] {lang_info['name']} (Source)")
        else:
            print(f"  [{key}] {lang_info['name']}")
    
    if prompt_key == "select_target_language_prompt":
        print(f"  [c] {i18n.t('target_option_custom')}")

    # Define which inputs are allowed for this menu
    allowed_choices = list(supported_languages.keys())
    if prompt_key == "select_target_language_prompt":
        allowed_choices.extend(['0', 'c'])

    while True:
        choice = input(i18n.t("enter_choice_prompt")).strip().lower()
        if choice in allowed_choices:
            return choice
        else:
            print(i18n.t("invalid_input_number"))

def main_menu():
    """
    Main interactive menu for the user.
    Orchestrates the entire workflow from user selection to calling the translation process.
    """
    # 1. Select Game
    selected_game_profile = select_game_profile()
    
    # 2. Select Mod
    selected_mod = directory_handler.select_mod_directory()
    if not selected_mod: return

    # 3. Get Mod Context from user
    mod_context = gather_mod_context(selected_mod)

    # 4. Ask for Cleanup
    directory_handler.cleanup_source_directory(selected_mod, selected_game_profile)
    
    # 5. Select Source Language
    source_lang_choice = select_language("select_source_language_prompt", selected_game_profile)
    source_lang = LANGUAGES[source_lang_choice]
    
    # 6. Select Target Language(s)
    target_choice = select_language("select_target_language_prompt", selected_game_profile, source_lang['key'])

    # 7. Prepare the list of target languages based on user's choice
    target_languages = []
    if target_choice == '0':
        # Batch mode: create a list of all supported languages except the source
        supported_keys = selected_game_profile.get("supported_language_keys", [])
        for key in supported_keys:
            if LANGUAGES[key]['key'] != source_lang['key']:
                target_languages.append(LANGUAGES[key])
    elif target_choice == 'c':
        # Custom language mode: prompt user for details
        logging.info(i18n.t("entering_custom_mode"))
        custom_name = input(i18n.t("prompt_custom_lang_name"))
        custom_key = input(i18n.t("prompt_custom_lang_key"))
        custom_prefix = input(i18n.t("prompt_custom_lang_prefix"))
        custom_lang = {
            "code": "custom", "key": custom_key, 
            "name": custom_name, "folder_prefix": custom_prefix
        }
        target_languages.append(custom_lang)
    elif target_choice in LANGUAGES:
        # Single language mode
        target_lang = LANGUAGES[target_choice]
        if target_lang['key'] == source_lang['key']:
            print(i18n.t("error_same_language"))
            return
        target_languages.append(target_lang)
    
    # 8. If we have valid targets, run the main translation workflow
    if target_languages:
        initial_translate.run(selected_mod, source_lang, target_languages, selected_game_profile, mod_context)

if __name__ == '__main__':
    # Setup logger and i18n first
    logger.setup_logger()
    i18n.load_language()
    
    # For now, we only run the interactive menu.
    # The non-interactive argparse logic can be added back here later if needed for CI/CD.
    main_menu()

    logging.info(i18n.t("workflow_completed"))