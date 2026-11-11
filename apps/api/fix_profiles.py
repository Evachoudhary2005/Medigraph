import re
from pathlib import Path

file = Path("app/services/fhir_mapper.py")
content = file.read_text(encoding="utf-8")

# Remove the three meta.profile lines
patterns = [
    r'\n\s*"meta":\s*\{"profile":\s*\[ABDM_PROFILE_PATIENT\]\},',
    r'\n\s*"meta":\s*\{"profile":\s*\[ABDM_PROFILE_ENCOUNTER\]\},',
    r'\n\s*"meta":\s*\{"profile":\s*\[ABDM_PROFILE_MEDICATION_REQUEST\]\},',
]

for pat in patterns:
    content = re.sub(pat, "", content)

file.write_text(content, encoding="utf-8")
print("Removed profile declarations")

# Verify
remaining = content.count("meta")
print(f"'meta' occurrences remaining: {remaining}")
print(f"'ABDM_PROFILE' occurrences: {content.count('ABDM_PROFILE')}")
