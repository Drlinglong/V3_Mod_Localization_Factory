import re, os

# ------------------------------------------------------------------
#   Hook dla plików customizable_localization/*.txt
# ------------------------------------------------------------------
def parse_custom_loc(file_path, original_lines, texts, key_map):
    # Obsługujemy wyłącznie *.txt we właściwym katalogu
    if (not file_path.endswith(".txt") or
        "customizable_localization" not in file_path.replace("\\", "/")):
        return

    for ln, line in enumerate(original_lines):
        m = re.search(r'add_custom_loc\s*=\s*"([^"]+)"', line)
        if not m:
            continue

        value = m.group(1)
        if not value or (value.startswith("$") and value.endswith("$")):
            continue                 # placeholdery typu $SOME_KEY$

        idx = len(texts)
        texts.append(value)
        key_map[idx] = {
            # „pseudo-klucz” – potrzebny tylko, by zapisać zmianę w tej samej linii
            "key_part"            : f"custom_loc_line_{ln}",  
            "original_value_part" : line.strip(),
            "line_num"            : ln,
        }

def register_hooks():
    # Zwracamy listę hooków, które parser ma uruchamiać
    return [parse_custom_loc]
