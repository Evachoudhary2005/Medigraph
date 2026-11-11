from pathlib import Path
import re

f = Path("src/app/clinician/[patientId]/summary/page.tsx")
content = f.read_text(encoding="utf-8")

pattern = r'\s*<Link\s+href=\{["\']/clinician/["\']\s*\+\s*patientId\s*\+\s*["\']/facts["\'][\s\S]*?</Link>'
content, n = re.subn(pattern, "", content)

print(f"  removed {n} Facts link(s) from summary page")

leftover = [ln.strip() for ln in content.splitlines() if "/facts" in ln]
if leftover:
    print(f"  ! still {len(leftover)} line(s) with /facts:")
    for l in leftover:
        print("   ", l)
else:
    print("  + clean")

f.write_text(content, encoding="utf-8")
print(f"WROTE src/app/clinician/[patientId]/summary/page.tsx")
