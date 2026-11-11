from pathlib import Path

f = Path("src/app/intake/page.tsx")
content = f.read_text(encoding="utf-8")

print("=== Lines containing native= ===")
for i, line in enumerate(content.splitlines(), 1):
    if "native" in line and "=" in line:
        print(f"{i:4}  {line}")

print()
print("=== Lines containing the Hindi tile ===")
for i, line in enumerate(content.splitlines(), 1):
    if "Hindi" in line or 'value="hi"' in line or 'setLang("hi")' in line:
        print(f"{i:4}  {line}")
