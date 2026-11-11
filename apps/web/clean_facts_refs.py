from pathlib import Path
import re

pages = [
    "src/app/clinician/page.tsx",
    "src/app/clinician/[patientId]/timeline/page.tsx",
    "src/app/clinician/[patientId]/summary/page.tsx",
    "src/app/clinician/[patientId]/orchestrate/page.tsx",
    "src/app/clinician/review/page.tsx",
    "src/app/clinician/ai-review/page.tsx",
]

total = 0
for rel in pages:
    f = Path(rel)
    if not f.exists():
        print(f"  (skip) {rel} not found")
        continue
    content = f.read_text(encoding="utf-8")
    before = content

    # Remove any <Link ... /facts ...>...</Link> block
    patterns = [
        r'\s*<Link\s+href=\{[^}]*?/facts[^}]*?\}[\s\S]*?</Link>',
        r'\s*<Link\s+href=\{[^}]*?facts["\']?[^}]*?\}[\s\S]*?</Link>',
    ]
    removed = 0
    for pat in patterns:
        content, n = re.subn(pat, "", content)
        removed += n

    if content != before:
        f.write_text(content, encoding="utf-8")
        print(f"  FIXED {rel} ({removed} link(s) removed)")
        total += removed
    else:
        # check for leftovers
        leftovers = [ln.strip() for ln in content.splitlines() if "/facts" in ln]
        if leftovers:
            print(f"  ! {rel} still has /facts on {len(leftovers)} line(s):")
            for l in leftovers:
                print(f"      {l}")
        else:
            print(f"  clean {rel}")

print(f"\nTotal removed: {total}")
