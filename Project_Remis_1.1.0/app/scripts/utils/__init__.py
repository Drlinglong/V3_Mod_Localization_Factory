# --- EU4 BOM support ----------------------------------------------

EU4_ENCODING = "utf-8-sig"           # UTF-8 + BOM (EU4 style)

from pathlib import Path

def read_text_bom(path: Path) -> str:
    """Wczytaj plik .yml, usuwając nagłówek BOM przy odczycie."""
    return path.read_text(encoding=EU4_ENCODING)

def write_text_bom(path: Path, data: str) -> None:
    """Zapisz plik .yml, dodając BOM jeśli go brakuje."""
    path.write_text(data, encoding=EU4_ENCODING)
