from pathlib import Path

f = Path("app/api/v1/ai_review.py")
content = f.read_text(encoding="utf-8")

# Remove the 400-character cap
old = '''        preview = narrative[:400] + ("..." if len(narrative) > 400 else "")'''
new = '''        # Return the full narrative - the review queue needs it for the clinician to read
        preview = narrative'''

if old in content:
    content = content.replace(old, new)
    f.write_text(content, encoding="utf-8")
    print("  + removed 400-char cap from ai_review.py")
else:
    print("  ! cap line not found - showing current")
    for line in content.splitlines():
        if "preview" in line and "=" in line:
            print("   ", line)
