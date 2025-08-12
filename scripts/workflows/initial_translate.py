# scripts/workflows/initial_translate.py
import os
import logging

from scripts.core import file_parser, api_handler, file_builder, asset_handler, directory_handler
from scripts.config import SOURCE_DIR, DEST_DIR, LANGUAGES
from scripts.utils import i18n


def run(mod_name: str,
        source_lang: dict,
        target_languages: list[dict],
        game_profile: dict,
        mod_context: str,
        selected_provider: str = "gemini"):
    """【最终版】初次翻译工作流（多语言 & 多游戏兼容）"""

    # ───────────── 1. ścieżki i tryb ─────────────
    is_batch_mode = len(target_languages) > 1
    if is_batch_mode:
        output_folder_name = f"Multilanguage-{mod_name}"
        primary_target_lang = LANGUAGES["1"]  # English jako lingua franca do metadata
    else:
        target_lang = target_languages[0]
        prefix = target_lang.get("folder_prefix", f"{target_lang['code']}-")
        output_folder_name = f"{prefix}{mod_name}"
        primary_target_lang = target_lang

    logging.info(i18n.t("start_workflow",
                 workflow_name=i18n.t("workflow_initial_translate_name"),
                 mod_name=mod_name))

    # ───────────── 2. init klienta ─────────────
    client, provider_name = api_handler.initialize_client(selected_provider)
    if not client:
        logging.warning(i18n.t("api_client_init_fail"))
        return

    # ───────────── 3. metadata + assety ─────────────
    asset_handler.process_metadata(
        mod_name, client, source_lang, primary_target_lang,
        output_folder_name, mod_context, game_profile, provider_name
    )
    asset_handler.copy_assets(mod_name, output_folder_name, game_profile)

    # ───────────── 4. przygotuj ścieżki źródłowe ─────────────
    source_loc_folder = game_profile["source_localization_folder"]
    source_loc_path = os.path.join(SOURCE_DIR, mod_name, source_loc_folder)
    cust_loc_root = os.path.join(SOURCE_DIR, mod_name, "customizable_localization")

    all_files_data = []

    # —— 4.a parsuj .yml w localisation/
    if os.path.isdir(source_loc_path):
        suffix = f"_l_{source_lang['key'][2:]}.yml"
        for root, _, files in os.walk(source_loc_path):
            for fn in files:
                if not fn.endswith(suffix):
                    continue
                fp = os.path.join(root, fn)
                orig, texts, km = file_parser.extract_translatable_content(fp)
                all_files_data.append({
                    "filename": fn,
                    "root": root,
                    "original_lines": orig,
                    "texts_to_translate": texts,
                    "key_map": km,
                    "is_custom_loc": False
                })

    # —— 4.b parsuj *.txt w customizable_localization/
    if os.path.isdir(cust_loc_root):
        for root, _, files in os.walk(cust_loc_root):
            for fn in files:
                if not fn.endswith(".txt"):
                    continue
                fp = os.path.join(root, fn)
                orig, texts, km = file_parser.extract_translatable_content(fp)
                all_files_data.append({
                    "filename": fn,
                    "root": root,
                    "original_lines": orig,
                    "texts_to_translate": texts,
                    "key_map": km,
                    "is_custom_loc": True
                })

    # ───────────── 5. tłumaczenie + zapis ─────────────
    for target_lang in target_languages:
        logging.info(i18n.t("translating_to_language", lang_name=target_lang["name"]))

        for fd in all_files_data:
            src_fp = os.path.join(fd["root"], fd["filename"])

            # wybór dest_dir_path zależnie od typu pliku
            if fd["is_custom_loc"]:
                rel = os.path.relpath(fd["root"], cust_loc_root)
                dest_dir = os.path.join(
                    DEST_DIR,
                    output_folder_name,
                    "customizable_localization",
                    target_lang["key"][2:],
                    rel,
                )
            else:
                rel = os.path.relpath(fd["root"], source_loc_path)
                dest_dir = os.path.join(
                    DEST_DIR,
                    output_folder_name,
                    source_loc_folder,
                    target_lang["key"][2:],
                    rel,
                )

            os.makedirs(dest_dir, exist_ok=True)

            # fallback gdy brak tekstów
            if not fd["texts_to_translate"]:
                file_builder.create_fallback_file(
                    src_fp, dest_dir, fd["filename"],
                    source_lang, target_lang, game_profile
                )
                continue

            # samo tłumaczenie
            translated = api_handler.translate_texts_in_batches(
                client,
                provider_name,
                fd["texts_to_translate"],
                source_lang,
                target_lang,
                game_profile,
                mod_context,
            )

            # AI błąd → fallback
            if translated is None:
                file_builder.create_fallback_file(
                    src_fp, dest_dir, fd["filename"],
                    source_lang, target_lang, game_profile
                )
                continue

            # zapis przetłumaczonego pliku
            file_builder.rebuild_and_write_file(
                fd["original_lines"],
                fd["texts_to_translate"],
                translated,
                fd["key_map"],
                dest_dir,
                fd["filename"],
                source_lang,
                target_lang,
                game_profile,
            )
