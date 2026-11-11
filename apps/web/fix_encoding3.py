from pathlib import Path

f = Path("src/app/intake/page.tsx")
content = f.read_text(encoding="utf-8")

# Step 1: try one more round of mojibake reversal
for step in range(3):
    try:
        new_content = content.encode("latin-1").decode("utf-8")
        if new_content == content:
            break
        content = new_content
    except (UnicodeEncodeError, UnicodeDecodeError):
        break

# Step 2: force a known-good map for anything still weird
explicit = {
    # Hindi word -> ASCII fallback
    "\u0939\u093f\u0928\u094d\u0926\u0940": "Hindi (Devanagari)",
    # common punctuation to plain ASCII
    "\u00b7": "-",   # middle dot
    "\u2022": "-",   # bullet
    "\u2013": "-",   # en dash
    "\u2014": "-",   # em dash
    "\u2018": "'",   # left single quote
    "\u2019": "'",   # right single quote
    "\u201c": '"',   # left double quote
    "\u201d": '"',   # right double quote
    "\u2026": "...", # ellipsis
    "\u00a0": " ",   # non-breaking space
}
for k, v in explicit.items():
    content = content.replace(k, v)

# Step 3: replace any remaining non-ASCII char with a safe placeholder
def safe(ch: str) -> str:
    o = ord(ch)
    # Basic Latin is fine
    if o < 128:
        return ch
    # Latin-1 supplement accents we can strip
    if 0xA0 <= o <= 0xFF:
        # map some common ones
        map_latin1 = {
            0xA9: "(c)", 0xAE: "(R)", 0xB0: "deg", 0xB1: "+/-",
            0xB5: "u", 0xBD: "1/2", 0xE9: "e", 0xE8: "e", 0xEA: "e",
            0xE0: "a", 0xE2: "a", 0xE7: "c", 0xEE: "i", 0xEF: "i",
            0xF4: "o", 0xF6: "o", 0xFC: "u",
        }
        return map_latin1.get(o, "")
    return ""

content = "".join(safe(c) for c in content)

# Step 4: report
non_ascii = sorted(set(c for c in content if ord(c) > 127))
if non_ascii:
    print(f"STILL {len(non_ascii)} non-ASCII chars:")
    for c in non_ascii:
        print(f"  U+{ord(c):04X}  {c!r}")
else:
    print("OK - file is pure ASCII")

f.write_text(content, encoding="utf-8")
print("WROTE src/app/intake/page.tsx")
