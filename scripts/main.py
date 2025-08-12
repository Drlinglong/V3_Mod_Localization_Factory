# scripts/main.py
# ---------------------------------------------------------------
"""
Main entry-point CLI for the “Mod-Localization-Factory”.

⚙️  Kluczowe zmiany vs. oryginał
────────────────────────────────
1. **game_profile propagation** – cały workflow (cleanup, assets, tłumaczenie)
   dostaje wybrany profil gry, aby mógł wiedzieć czy użyć UTF-8, CP-1252,
   czy np. zrzucać polskie ogonki.

2. **i18n everywhere** – wszystkie komunikaty przechodzą przez utils.i18n,
   więc aplikacja jest w pełni wielojęzyczna.

3. **Defensive-IO** – czytanie `.metadata/metadata.json` chronione try/except,
   aby narzędzie nie wywalało się dla modów bez metadanych.

Cała logika interakcji z użytkownikiem została zebrana w pojedynczy,
czytelny plik – bez zmian w innych modułach wystarczy dodać nowe profile
gier lub języki w `config.py`.
"""
# ---------------------------------------------------------------
import os
import json
import argparse
import logging # 导入logging模块


from utils import i18n, logger

from workflows import initial_translate
from core import directory_handler
from config import LANGUAGES, GAME_PROFILES, SOURCE_DIR

# ────────────────────────── helpers ─────────────────────────────


def gather_mod_context(mod_name: str) -> str:
    """Zczytuje nazwę moda z metadata + pozwala użytkownikowi dopisać kontekst."""
    print(i18n.t("getting_mod_context"))

    meta_path = os.path.join(SOURCE_DIR, mod_name, ".metadata", "metadata.json")
    mod_official_name = mod_name

    try:
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                if meta.get("name"):
                    mod_official_name = meta["name"]
    except Exception as e:  # pragma: no cover
        print(i18n.t("metadata_read_fail", path=meta_path, error=e))

    print(i18n.t("mod_name_identified", name=mod_official_name))
    extra = input(i18n.t("prompt_for_extra_context")).strip()

    final_context = mod_official_name if not extra else f"{mod_official_name} ({extra})"
    print(i18n.t("final_context_is", context=final_context))
    return final_context


def select_game_profile() -> dict:
    """Interaktywna lista profili gier."""
    print(i18n.t("select_game_profile_prompt"))
    for key, prof in GAME_PROFILES.items():
        print(f"  [{key}] {prof['name']}")

    while True:
        choice = input(i18n.t("enter_choice_prompt")).strip()
        if choice in GAME_PROFILES:
            return GAME_PROFILES[choice]
        print(i18n.t("invalid_input_number"))


def select_language(prompt_key: str, source_key: str | None = None) -> str:
    """Pokazuje dostępne języki i zwraca wybrany klucz z config.LANGUAGES."""
    print(i18n.t(prompt_key))
    if prompt_key == "select_target_language_prompt":
        print(f"  [0] {i18n.t('target_option_all')}")

    for key, lang in LANGUAGES.items():
        label = f"{lang['name']}{' (Source)' if lang['key']==source_key else ''}"
        print(f"  [{key}] {label}")

    valid = list(LANGUAGES.keys()) + (["0"] if prompt_key == "select_target_language_prompt" else [])
    while True:
        choice = input(i18n.t("enter_choice_prompt")).strip().lower()
        if choice in valid:
            return choice
        print(i18n.t("invalid_input_number"))


# ─────────────────────── main menu / cli ───────────────────────


def main_menu() -> None:
    """CLI główne – wywołuje odpowiedni workflow z poprawnymi parametrami."""
    logger.setup_logger()

    

    i18n.load_language()  # ustala locale na podstawie ENV lub inputu
    logging.info("--- New Session Started ---")

    game_profile = select_game_profile()
    mod_dir = directory_handler.select_mod_directory()
    if not mod_dir:
        return

    # 1) ewentualne czyszczenie źródła (np. backup .bak, BOMy) – wymaga profil
    directory_handler.cleanup_source_directory(mod_dir, game_profile)

    # 2) kontekst dla promptów LLM
    mod_context = gather_mod_context(mod_dir)

    # 3) języki
    src_choice = select_language("select_source_language_prompt")
    src_lang = LANGUAGES[src_choice]

    tgt_choice = select_language("select_target_language_prompt", src_lang["key"])
    target_langs: List[dict] = []

    if tgt_choice == "0":
        target_langs = [lang for lang in LANGUAGES.values() if lang["key"] != src_lang["key"]]
    else:
        tgt_lang = LANGUAGES[tgt_choice]
        if tgt_lang["key"] == src_lang["key"]:
            print(i18n.t("error_same_language"))
            return
        target_langs.append(tgt_lang)

    # 4) odpalamy workflow
    if target_langs:
        initial_translate.run(
            mod_dir,
            src_lang,
            target_langs,
            game_profile,
            mod_context,
        )


# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main_menu()
