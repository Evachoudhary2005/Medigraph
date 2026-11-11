from pathlib import Path

f = Path("src/app/intake/page.tsx")
lines = f.read_text(encoding="utf-8").splitlines()

# Fix line 160 (0-indexed 159). Match any native= whose value is just spaces+a
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('native="') and stripped.endswith('"'):
        inner = stripped[len('native="'):-1]
        if inner.strip() in ("a", "", "hi"):
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = f'{indent}native="Hindi"'
            print(f"  fixed line {i+1}: {line.strip()!r} -> native=\"Hindi\"")

f.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("WROTE src/app/intake/page.tsx")
