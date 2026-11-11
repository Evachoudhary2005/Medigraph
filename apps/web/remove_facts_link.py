from pathlib import Path
import re

f = Path("src/app/clinician/page.tsx")
content = f.read_text(encoding="utf-8")

before = len(content)

# Remove any <Link href={"/clinician/" + p.id + "/facts"}>...</Link> block
pattern = r'\s*<Link\s+href=\{[^}]*?/facts"[^}]*?\}[\s\S]*?</Link>'
content, n1 = re.subn(pattern, "", content)

# Also catch a possible inline variant without template expression
pattern2 = r'\s*<Link\s+href=\{[^}]*?\}/facts"[^}]*?\}[\s\S]*?</Link>'
content, n2 = re.subn(pattern2, "", content)

print(f"  removed {n1 + n2} Facts link(s)")

# Sanity: any /facts references left?
leftover = [ln.strip() for ln in content.splitlines() if "/facts" in ln]
if leftover:
    print(f"  ! still {len(leftover)} line(s) with /facts:")
    for l in leftover:
        print("   ", l)
else:
    print("  + no /facts references remain")

f.write_text(content, encoding="utf-8")
print(f"WROTE src/app/clinician/page.tsx")
print(f"  bytes: {before} -> {len(content)}")
