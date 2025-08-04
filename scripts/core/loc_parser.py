# scripts/core/loc_parser.py
# ---------------------------------------------------------------
# Parser i generator plików lokalizacyjnych Paradoxu (EU4, Vic3, Stellaris)

import re
from pathlib import Path

from scripts.utils import read_text_bom, write_text_bom

# KEY:0 "Tekst"
ENTRY_RE = re.compile(r'^([A-Za-z0-9_\.]+):0\s+"(.*)"$')

def parse_loc_file(path: Path) -> list[tuple[str, str]]:
    """
    Wczytaj plik .yml i zwróć listę krotek (key, text).
    UTF-8 + BOM obsługiwane przez read_text_bom().
    """
    entries: list[tuple[str, str]] = []
    for line in read_text_bom(path).splitlines():
        match = ENTRY_RE.match(line)
        if match:
            key, value = match.groups()
            entries.append((key, value))
    return entries


def emit_loc_file(header: str, entries: list[tuple[str, str]]) -> str:
    """
    Zamień listę krotek z powrotem na tekst pliku lokalizacyjnego.
    """
    rows = [header]                       # np. „l_polish:” lub „l_english:”
    for key, value in entries:
        safe = value.replace('"', r'\"')  # escape podwójnych cudzysłowów
        rows.append(f' {key}:0 "{safe}"')
    return "\n".join(rows)


def save_loc_file(path: Path, header: str, entries: list[tuple[str, str]]) -> None:
    """
    Skrót: wypisz plik na dysk, zachowując BOM.
    """
    write_text_bom(path, emit_loc_file(header, entries))
