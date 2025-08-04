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
    print(f"[parser-hook] ⚠️  Failed to load hooks: {e}")


# ───────────────────── 2. GŁÓWNA FUNKCJA ──────────────────────────────
def extract_translatable_content(
    file_path: str,
) -> tuple[list[str], list[str], dict[int, dict]]:
    """Wyciąga teksty do tłumaczenia z pojedynczego pliku .yml lub
    z *.txt w customizable_localization (add_custom_loc).

    Zwraca:
        original_lines      – oryginalne linie pliku (list[str])
        texts_to_translate  – kolejność = kolejność wystąpień w pliku
        key_map             – {idx: {key_part, original_value_part, line_num}}
    """
    rel_path = os.path.relpath(file_path)
    print(i18n.t("parsing_file", filename=rel_path))

    # 1) Wczytanie linii z fallbackem na CP1252 dla niespodzianek
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            original_lines = f.readlines()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="cp1252", errors="ignore") as f:
            original_lines = f.readlines()

    texts_to_translate: list[str] = []
    key_map: dict[int, dict] = {}

    # Czy to plik txt w customizable_localization?
    is_txt = file_path.lower().endswith(".txt") and "customizable_localization" in file_path.replace("\\", "/")

    for line_num, line in enumerate(original_lines):
        stripped = line.strip()

        # wspólne pomijanie komentarzy i pustych
        if not stripped or stripped.startswith("#"):
            continue

        if is_txt:
            # obsługa: add_custom_loc = "Text"
            if "add_custom_loc" not in stripped:
                continue
            match = re.search(r'add_custom_loc\s*=\s*"(.*?)"', stripped)
            if not match:
                continue
            value = match.group(1)
            key_part = "add_custom_loc"
            value_part = stripped.split("=", 1)[1]
        else:
            # ——— klasyczny format Paradox-yml: key:0 "Text"
            # pomijamy nagłówki l_english, l_polish itd.
            if any(stripped.startswith(pref) for pref in (
                "l_english", "l_simp_chinese", "l_french", "l_german",
                "l_spanish", "l_russian", "l_polish"
            )):
                continue

            # rozdzielamy klucz od wartości
            parts = stripped.split(":", 1)
            if len(parts) < 2:
                continue
            key_part, value_part = parts[0], parts[1]

            # w wartości szukamy ciągu w "…"
            m = re.search(r'"(.*)"', value_part)
            if not m:
                continue
            value = m.group(1)

        # pomijamy placeholdery typu $VAL$
        if (value.startswith("$") and value.endswith("$")) or not value:
            continue

        # zapis do list
        idx = len(texts_to_translate)
        texts_to_translate.append(value)
        key_map[idx] = {
            "key_part": key_part,
            "original_value_part": value_part.strip(),
            "line_num": line_num,
        }

    # ───────────── 2.a Uruchamiamy ewentualne hooki ─────────────
    if HOOKS:
        for hook in HOOKS:
            try:
                hook(file_path, original_lines, texts_to_translate, key_map)
            except Exception as e:  # pragma: no cover
                print(f"[parser-hook] ⚠️  {hook.__name__} failed: {e}")

    # ───────────── 3. PODSUMOWANIE ─────────────
    print(i18n.t("extracted_texts", count=len(texts_to_translate)))
    return original_lines, texts_to_translate, key_map
