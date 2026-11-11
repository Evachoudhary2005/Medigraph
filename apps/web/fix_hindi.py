from pathlib import Path

f = Path("src/app/intake/page.tsx")
content = f.read_text(encoding="utf-8")

before = content
content = content.replace('native="a"', 'native="Hindi"')
content = content.replace('native=""', 'native="Hindi"')

if content != before:
    f.write_text(content, encoding="utf-8")
    print("FIXED: native= now Hindi")
else:
    print("No match for native=\"a\" - showing all native= lines:")
    for line in content.splitlines():
        if "native=" in line:
            print("  " + line.strip())
