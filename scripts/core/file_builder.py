# scripts/core/file_builder.py
# ---------------------------------------------------------------
import os
from utils import i18n


# ---------------------------------------------------------------
# 1.  Fallback dla pustych/lang-only plików
# ---------------------------------------------------------------
def create_fallback_file(
    source_path: str,
    dest_dir: str,
    original_filename: str,
    source_lang: dict,
    target_lang: dict,
    game_profile: dict,                 # ← NOWY PARAMETR (dla encoding)
) -> None:
    """Kopiuje plik bez tłumaczenia, zmieniając nagłówek i nazwę."""
    print(i18n.t("creating_fallback_file"))

    try:
        # czytamy w UTF-8-SIG – bezpieczne również dla CP-1252
        with open(source_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()

        # ── 1) nagłówek ------------------------------------------------------------
        for i, ln in enumerate(lines):
            if source_lang["key"] in ln:
                lines[i] = ln.replace(source_lang["key"], target_lang["key"])
                break
        else:
            lines.insert(0, f"{target_lang['key']}:\n")

        # ── 2) nowa nazwa pliku ----------------------------------------------------
        def _swap_suffix(name: str) -> str:
            src = f"_l_{source_lang['key'][2:]}"
            tgt = f"_l_{target_lang['key'][2:]}"
            return name.replace(src, tgt) if src in name else name

        new_filename   = _swap_suffix(original_filename)
        dest_file_path = os.path.join(dest_dir, new_filename)

        # ── 3) zapis – zgodnie z profilem gry --------------------------------------
        with open(dest_file_path, "w", encoding=game_profile["encoding"]) as f:  # ★
            f.writelines(lines)

        print(i18n.t("fallback_file_created", filename=new_filename))

    except Exception as e:
        print(i18n.t("fallback_creation_error", error=e))


# ---------------------------------------------------------------
# 2.  Rekonstrukcja i zapis przetłumaczonego pliku
# ---------------------------------------------------------------
def rebuild_and_write_file(
    original_lines: list[str],
    texts_to_translate: list[str],
    translated_texts: list[str],
    key_map: dict[int, dict],
    dest_dir_path: str,
    original_filename: str,
    source_lang: dict,
    target_lang: dict,
    game_profile: dict,                 # ← NOWY PARAMETR
) -> None:
    """Buduje nowy *.yml z gotowymi tłumaczeniami i zapisuje go na dysk."""
    translation_map = dict(zip(texts_to_translate, translated_texts))
    new_lines       = list(original_lines)   # robimy kopię

    # ── wstawiamy tłumaczenia -------------------------------------------------------
    for i, original_text in enumerate(texts_to_translate):
        translated = translation_map.get(original_text, original_text)

        linfo      = key_map[i]
        line_num   = linfo["line_num"]
        key_part   = linfo["key_part"]
        val_part   = linfo["original_value_part"]

        safe_txt = translated.strip().replace('"', r"\"")
        new_val  = val_part.replace(f'"{original_text}"', f'"{safe_txt}"')

        indent   = original_lines[line_num][: original_lines[line_num].find(key_part)]
        new_lines[line_num] = f"{indent}{key_part}:{new_val}\n"

    # ── nagłówek (l_english → l_polish itd.) ---------------------------------------
    for i, ln in enumerate(new_lines):
        if source_lang["key"] in ln:
            new_lines[i] = ln.replace(source_lang["key"], target_lang["key"])
            break
    else:
        new_lines.insert(0, f"{target_lang['key']}:\n")

    # ── nazwa pliku ----------------------------------------------------------------
    src_suf = f"_l_{source_lang['key'][2:]}"
    tgt_suf = f"_l_{target_lang['key'][2:]}"
    new_filename = (
        original_filename.replace(src_suf, tgt_suf) if src_suf in original_filename else original_filename
    )
    dest_file_path = os.path.join(dest_dir_path, new_filename)

    # ── zapis w odpowiednim kodowaniu ----------------------------------------------
    with open(dest_file_path, "w", encoding=game_profile["encoding"]) as f:  # ★
        f.writelines(new_lines)

    print(
        i18n.t(
            "writing_file_success",
            filename=os.path.join(os.path.relpath(dest_dir_path, "my_translation"), new_filename),
        )
    )
