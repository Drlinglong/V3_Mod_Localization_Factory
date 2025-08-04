# audit.py  ── szybki self-check repozytorium
import pathlib, re

checks = {
    # 1. flaga Eu4 → strip_pl_diacritics = True
    'config.py EU4 flag'      : (
        'scripts/config.py',
        r'"id":\s*"eu4".+?strip_pl_diacritics"\s*:\s*True',
        re.S
    ),

    # 2. utils/text_clean → funkcja istnieje
    'text_clean function'     : (
        'scripts/utils/text_clean.py',
        r'def\s+strip_pl_diacritics',
        0
    ),

    # 3. api_handler: pojedynczy tekst – używa strip_pl_diacritics
    'api_handler single'      : (
        'scripts/core/api_handler.py',
        r'strip_pl_diacritics.+?def\s+translate_single_text',
        re.S
    ),

    # 4. api_handler: batch – używa strip_pl_diacritics
    'api_handler batch'       : (
        'scripts/core/api_handler.py',
        r'strip_pl_diacritics.+?def\s+translate_texts_in_batches',
        re.S
    ),

    # 5. file_builder: zapis z dynamicznym encoding
    'file_builder encoding'   : (
        'scripts/core/file_builder.py',
        r'open\([^)]*encoding\s*=\s*game_profile\["encoding"\]',
        0
    ),
}

for name, (path, pattern, flags) in checks.items():
    try:
        code = pathlib.Path(path).read_text(encoding='utf8', errors='ignore')
        print(f'{name:<25}:', 'OK' if re.search(pattern, code, flags) else 'MISSING')
    except FileNotFoundError:
        print(f'{name:<25}:  FILE NOT FOUND')
