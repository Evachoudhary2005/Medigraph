from pathlib import Path

f = Path("src/app/intake/page.tsx")
content = f.read_text(encoding="utf-8")

# Apply the mojibake reversal repeatedly until it stops helping
for step in range(4):
    try:
        recovered_bytes = content.encode("latin-1")
    except UnicodeEncodeError:
        print(f"  step {step}: cannot go further (real non-Latin1 chars)")
        break
    try:
        new_content = recovered_bytes.decode("utf-8")
    except UnicodeDecodeError:
        print(f"  step {step}: bytes are not valid UTF-8, stopping")
        break
    if new_content == content:
        print(f"  step {step}: no change, stopping")
        break
    content = new_content
    print(f"  step {step}: reversed one level")

f.write_text(content, encoding="utf-8")
print("WROTE src/app/intake/page.tsx")

# Report any remaining non-ASCII
non_ascii = sorted(set(c for c in content if ord(c) > 127))
if non_ascii:
    print(f"\nRemaining non-ASCII characters ({len(non_ascii)}):")
    for c in non_ascii:
        print(f"  U+{ord(c):04X}  {c!r}")
else:
    print("\nFile is pure ASCII")
