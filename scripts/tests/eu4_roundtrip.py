from pathlib import Path
from scripts.core.loc_parser import parse_loc_file, emit_loc_file   # ← UWAGA: scripts.core
from scripts.utils import write_text_bom                            # ← scripts.utils

# pełna ścieżka do pliku w source_mod
from glob import glob
src = Path(glob("source_mod/Anbennar/localisation/*_l_english.yml")[0])
entries = parse_loc_file(src)

write_text_bom(Path("roundtrip_test.yml"),
               emit_loc_file("l_english:", entries))

print("✔ Round-trip gotowy – diff powinien być pusty")
