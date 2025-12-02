# scripts/core/loc_parser.py
# ---------------------------------------------------------------
# Parser i generator plików lokalizacyjnych Paradoxu (EU4, Vic3, Stellaris)

import re
from pathlib import Path

from scripts.utils import read_text_bom, write_text_bom

# KEY:0 "Tekst"
ENTRY_RE = re.compile(r'^\s*([A-Za-z0-9_\.\-]+):[0-9]*\s*"(.*)"\s*$')

def parse_loc_file(path: Path) -> list[tuple[str, str]]:
    """
    Wczytaj plik .yml lub .json i zwróć listę krotek (key, text).
    UTF-8 + BOM obsługiwane przez read_text_bom().
    """
    entries: list[tuple[str, str]] = []
    
    if path.suffix.lower() == '.json':
        import json
        try:
            content = read_text_bom(path)
            data = json.loads(content)
            # Flatten JSON if needed, or assume simple key-value
            # If it's a list of objects? Or a dict?
            # Paradox metadata.json is usually a dict.
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, str):
                        entries.append((k, v))
                    else:
                        # Handle nested or non-string values as string representation
                        entries.append((k, str(v)))
            elif isinstance(data, list):
                 # Handle list if necessary (unlikely for loc, but possible for metadata)
                 pass
        except Exception as e:
            print(f"JSON parse error: {e}")
            pass
    else:
        # YAML / Paradox Loc
        for line in read_text_bom(path).splitlines():
            match = ENTRY_RE.match(line)
            if match:
                key, value = match.groups()
                entries.append((key, value))
    return entries


def parse_loc_file_with_lines(path: Path) -> list[tuple[str, str, int]]:
    """
    Same as parse_loc_file but returns (key, value, line_number).
    Line numbers are 1-based.
    """
    entries: list[tuple[str, str, int]] = []
    
    if path.suffix.lower() == '.json':
        # JSON usually doesn't have line numbers in a meaningful way for this context
        # We'll just use 0 or index + 1
        import json
        try:
            content = read_text_bom(path)
            data = json.loads(content)
            if isinstance(data, dict):
                for i, (k, v) in enumerate(data.items()):
                    val = str(v)
                    entries.append((k, val, i + 1))
        except Exception:
            pass
    else:
        # YAML / Paradox Loc
        lines = read_text_bom(path).splitlines()
        for i, line in enumerate(lines):
            match = ENTRY_RE.match(line)
            if match:
                key, value = match.groups()
                entries.append((key, value, i + 1))
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
