# ---------------------------------------------------------------
#  scripts/core/scripted_loc_parser.py
# ---------------------------------------------------------------
"""
Obsługa plików customizable_localization/*.txt (scripted loc).

•  znajdź linie     add_custom_loc = "Tekst"
•  zbierz do listy  -> zwracamy texts_to_translate i mapę pozycji
•  po tłumaczeniu   -> wstawiamy translated_text na pierwotne miejsce
"""
from __future__ import annotations
import re, pathlib
from typing import List, Tuple

_ADD_RE = re.compile(r'^(?P<prefix>\s*add_custom_loc\s*=\s*)"(?P<text>[^"]*)"', re.M)

def extract_texts(path: pathlib.Path) -> Tuple[List[str], List[Tuple[int, str]]]:
    """Zwraca (lista_tekstów, mapa_pozycji)"""
    src = path.read_text(encoding='utf-8', errors='ignore').splitlines(keepends=True)
    texts, positions = [], []
    for i, line in enumerate(src):
        m = _ADD_RE.match(line)
        if m:
            texts.append(m.group('text'))
            positions.append((i, m.group('prefix')))
    return texts, positions, src

def inject_texts(src_lines: List[str],
                 positions: List[Tuple[int, str]],
                 translated: List[str]) -> List[str]:
    for (i, prefix), new in zip(positions, translated):
        safe = new.replace('"', '\\"')
        src_lines[i] = f'{prefix}"{safe}"\n'
    return src_lines
