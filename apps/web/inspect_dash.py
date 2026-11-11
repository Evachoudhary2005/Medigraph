from pathlib import Path

f = Path("src/app/clinician/page.tsx")
lines = f.read_text(encoding="utf-8").splitlines()

for n in [360, 361, 362, 363, 364, 365, 366, 378, 379, 380, 381, 382, 383, 384, 385, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452]:
    if n <= len(lines):
        print(f"{n:5}  {lines[n-1]}")
