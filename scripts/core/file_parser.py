# scripts/core/file_parser.py
# ---------------------------------------------------------------
"""
Domyślny parser dla plików .yml (Paradox localisation) oraz
*.txt w customizable_localization (add_custom_loc hook).

⚠️  *Hook system*  
Jeśli potrzebujesz obsłużyć dodatkowe formaty albo niestandardowe reguły
(np. inne pliki), utwórz plik:

    hooks/file_parser_hook.py

i zdefiniuj w nim funkcję `register_hooks()`, która zwraca listę
callable’ów o sygnaturze:

    def my_hook(file_path: str,
                original_lines: list[str],
                texts: list[str],
                key_map: dict[int, dict]) -> None: ...
"""
# ---------------------------------------------------------------
from __future__ import annotations

import os
import re
from types import ModuleType
from typing import Callable, List
import logging

from utils import i18n  # komunikaty wielojęzykowe

# ───────────────────── 1. PRÓBA ZAŁADOWANIA HOOKÓW ─────────────────────
HOOKS: List[Callable[[str, list[str], list[str], dict[int, dict]], None]] = []

try:
    import importlib.util

    spec = importlib.util.find_spec("hooks.file_parser_hook")
    if spec is not None:
        module: ModuleType = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(module)  # type: ignore
        if hasattr(module, "register_hooks"):
            _hooks: list = module.register_hooks()  # type: ignore
            if isinstance(_hooks, list):
                HOOKS.extend(_hooks)
except Exception as e:  # pragma: no cover – hook opcjonalny
    logging.error(f"[parser-hook] ⚠️  Failed to load hooks: {e}")


def extract_translatable_content(
    file_path: str,
) -> tuple[list[str], list[str], dict[int, dict]]:
    """
    Extracts translatable texts from a single .yml file or a .txt file
    from a customizable_localization directory, now with improved filtering.

    Returns:
        original_lines (list[str]): The original lines of the file.
        texts_to_translate (list[str]): A list of strings to be translated.
        key_map (dict): A map to reconstruct the file: {index: {key_part, original_value_part, line_num}}.
    """
    rel_path = os.path.relpath(file_path)
    logging.info(i18n.t("parsing_file", filename=rel_path))

    # 1) Read file lines with a fallback to cp1252 for unexpected encodings.
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            original_lines = f.readlines()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="cp1252", errors="ignore") as f:
            original_lines = f.readlines()

    texts_to_translate: list[str] = []
    key_map: dict[int, dict] = {}

    # Check if this is a .txt file in a customizable_localization directory.
    is_txt = file_path.lower().endswith(".txt") and "customizable_localization" in file_path.replace("\\", "/")

    for line_num, line in enumerate(original_lines):
        stripped = line.strip()

        # Common check: skip comments and empty lines.
        if not stripped or stripped.startswith("#"):
            continue

        if is_txt:
            # Handle the format: add_custom_loc = "Text"
            if "add_custom_loc" not in stripped:
                continue
            match = re.search(r'add_custom_loc\s*=\s*"(.*?)"', stripped)
            if not match:
                continue
            value = match.group(1)
            key_part = "add_custom_loc"
            value_part = stripped.split("=", 1)[1]
        else:
            # --- Handle the classic Paradox-yml format: key:0 "Text" ---
            # Skip headers like l_english, l_polish etc.
            if any(stripped.startswith(pref) for pref in (
                "l_english", "l_simp_chinese", "l_french", "l_german",
                "l_spanish", "l_russian", "l_polish"
            )):
                continue

            # Split the line into key and value parts at the first colon.
            parts = stripped.split(":", 1)
            if len(parts) < 2:
                continue
            key_part, value_part = parts[0], parts[1]

            # Find the string within quotes "..." in the value part.
            m = re.search(r'"(.*)"', value_part)
            if not m:
                continue
            value = m.group(1)

        # --- Filtering Logic ---

        # 【核心修正 1】Filter out self-referencing keys (e.g., a_key: "a_key").
        # We strip the key_part to get a clean key for comparison.
        if key_part.strip() == value:
            continue

        # 【核心修正 2】Filter out pure variables (e.g., "$VAR$").
        is_pure_variable = False
        if value.startswith('$') and value.endswith('$'):
            if value.count('$') == 2:
                is_pure_variable = True

        # 【核心修正 3】Filter out pure variables AND empty values (e.g., key: "").
        if is_pure_variable or not value:
            continue

        # Save the extracted text and its metadata to the lists.
        idx = len(texts_to_translate)
        texts_to_translate.append(value)
        key_map[idx] = {
            "key_part": key_part,
            "original_value_part": value_part.strip(),
            "line_num": line_num,
        }

    # --- (The Hook system logic remains the same) ---
    if HOOKS:
        for hook in HOOKS:
            try:
                hook(file_path, original_lines, texts_to_translate, key_map)
            except Exception as e:
                logging.error(f"[parser-hook] ⚠️  {hook.__name__} failed: {e}")

    # --- Final Summary ---
    logging.info(i18n.t("extracted_texts", count=len(texts_to_translate)))
    return original_lines, texts_to_translate, key_map