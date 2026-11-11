from pathlib import Path

f = Path("app/data/questionnaire_gm.py")
content = f.read_text(encoding="utf-8")

# 1. Rename the section title
content = content.replace(
    '"title_en": "Medications and Allergies"',
    '"title_en": "Allergies"'
)
content = content.replace(
    '"title_hi": "\u0926\u0935\u093e\u090f\u0902 \u0914\u0930 \u090f\u0932\u0930\u094d\u091c\u0940"',
    '"title_hi": "\u090f\u0932\u0930\u094d\u091c\u0940"'
)

# 2. Remove the "Which medicines are you currently taking?" question entirely
# It's a single JSON block:
# {
#   "id": "q_med_current", "type": "text",
#   "text_en": "Which medicines are you currently taking?",
#   "text_hi": "..."
# },

old_q = '''                {"id": "q_med_current", "type": "text",
                 "text_en": "Which medicines are you currently taking?",
                 "text_hi": "\u0935\u0930\u094d\u0924\u092e\u093e\u0928 \u092e\u0947\u0902 \u0906\u092a \u0915\u094c\u0928 \u0938\u0940 \u0926\u0935\u093e\u090f\u0902 \u0932\u0947 \u0930\u0939\u0947 \u0939\u0948\u0902?"},
'''

if old_q in content:
    content = content.replace(old_q, "")
    print("  - removed q_med_current")

# Try alternate formatting (in case of different whitespace)
if "q_med_current" in content:
    import re
    pattern = r'\s*\{"id":\s*"q_med_current".*?\},'
    content = re.sub(pattern, "", content, count=1, flags=re.DOTALL)
    if "q_med_current" not in content:
        print("  - removed q_med_current (regex fallback)")

# 3. Rename the section id so it doesn't say medications
content = content.replace('"id": "medications_allergies"', '"id": "allergies"')

# 4. Add an info-only placeholder question that tells the patient meds come from documents
# (a display-only note the frontend can render)
old_allergies_q = '''                {"id": "q_med_allergies", "type": "yes_no",
                 "text_en": "Do you have any known allergies?",'''

new_allergies_q = '''                {"id": "q_med_allergies_info", "type": "info",
                 "text_en": "Your current medications will be read automatically from the documents you upload. Please list any allergies below.",
                 "text_hi": "\u0906\u092a\u0915\u0940 \u0935\u0930\u094d\u0924\u092e\u093e\u0928 \u0926\u0935\u093e\u090f\u0902 \u0906\u092a\u0915\u0947 \u0905\u092a\u0932\u094b\u0921 \u0915\u093f\u090f \u0917\u090f \u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c\u094b\u0902 \u0938\u0947 \u0938\u094d\u0935\u091a\u093e\u0932\u093f\u0924 \u0930\u0942\u092a \u0938\u0947 \u092a\u0922\u093c\u0940 \u091c\u093e\u090f\u0902\u0917\u0940\u0964 \u0915\u0943\u092a\u092f\u093e \u0928\u0940\u091a\u0947 \u0905\u092a\u0928\u0940 \u0915\u094b\u0908 \u092d\u0940 \u090f\u0932\u0930\u094d\u091c\u0940 \u092c\u0924\u093e\u090f\u0902\u0964"},
                {"id": "q_med_allergies", "type": "yes_no",
                 "text_en": "Do you have any known allergies?",'''

if old_allergies_q in content:
    content = content.replace(old_allergies_q, new_allergies_q)
    print("  + added info note about medications")
else:
    print("  ! could not find q_med_allergies block to add info note")

f.write_text(content, encoding="utf-8")
print("WROTE app/data/questionnaire_gm.py")
print("bytes:", f.stat().st_size)

# Report
remaining = [line for line in content.splitlines() if "q_med" in line or "medications_allergies" in line]
print("\nLines still mentioning q_med or medications_allergies:")
for l in remaining:
    print(" ", l.strip())
