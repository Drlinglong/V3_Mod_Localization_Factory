# scripts/utils/text_clean.py
# ---------------------------------------------------------------
"""
Narzędzia do „czyszczenia” tekstu na potrzeby lokalizacji Paradox:

• strip_pl_diacritics(txt) – usuwa polskie znaki diakrytyczne
  (ą Ą ę Ę ó Ó ł Ł ś Ś ć Ć ń Ń ż Ż ź Ź) zachowując całą resztę bez zmian.
  Wywoływana automatycznie, jeśli w GAME_PROFILES dana gra ma
      "strip_pl_diacritics": True

• strip_outer_quotes(txt)  – odcina **pojedynczą** zewnętrzną parę
  cudzysłowów / „” / «» (częsty artefakt LLM-ów) pozostawiając
  cytaty wewnętrzne nietknięte.  
  Stosowana tuż po otrzymaniu odpowiedzi z modelu, dzięki czemu
  pliki .yml nie zawierają typograficznych znaków, które psują
  parser EU4.
"""

# --- Mapa zamian 1-do-1 (ogonków) ------------------------------
DIACRITIC_MAP = str.maketrans({
    "ł": "l", "Ł": "L",
    "ą": "a", "Ą": "A",
    "ę": "e", "Ę": "E",
    "ś": "s", "Ś": "S",
    "ć": "c", "Ć": "C",
    "ń": "n", "Ń": "N",
    "ó": "o", "Ó": "O",
    "ż": "z", "Ż": "Z",
    "ź": "z", "Ź": "Z",
})

def strip_pl_diacritics(txt: str) -> str:
    """
    Zwraca kopię `txt` z usuniętymi polskimi ogonkami.
    Szybsze niż unicodedata.normalize() i nie rusza innych znaków.
    """
    if not txt:
        return txt
    return txt.translate(DIACRITIC_MAP)

# --- Pary cudzysłowów do wycięcia -----------------------------
QUOTE_PAIRS = [
    ('"', '"'),
    ('„', '”'),
    ('«', '»'),
]
def strip_outer_quotes(txt: str) -> str:
    """
    Usuwa **jedną** zewnętrzną parę cudzysłowów, jeśli tekst
    zaczyna się i kończy pasującymi znakami cudzysłowu.
    Pozostawia cytaty wewnętrzne (np. That's, O'Neil) nietknięte.
    """
    if not txt:
        return txt
    txt = txt.strip()
    if len(txt) < 2:
        return txt

    for open_quote, close_quote in QUOTE_PAIRS:
        if txt.startswith(open_quote) and txt.endswith(close_quote):
            return txt[1:-1].strip()

    return txt
