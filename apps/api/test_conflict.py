import sqlite3, uuid
from datetime import datetime, timezone

pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"
now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(sep=" ")
c = sqlite3.connect("medigraph.db")

# Clean up any prior test data
c.execute("DELETE FROM intake_answers WHERE question_id = 'diabetes_status'")
c.execute("DELETE FROM clinical_facts WHERE label = 'diabetes_status'")

row = c.execute(
    "SELECT id FROM intake_sessions WHERE patient_id=? LIMIT 1", (pid,)
).fetchone()
if not row:
    raise SystemExit("no intake session found for this patient")
session_id = row[0]

# 1. Patient says "no" — becomes source=intake
c.execute("""
    INSERT INTO intake_answers
    (id, session_id, question_id, value_json, source, confidence, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (str(uuid.uuid4()), session_id, "diabetes_status",
      '"no"', "touch", 0.9, now, now))

# 2. Document says "yes" — becomes source=document
c.execute("""
    INSERT INTO clinical_facts
    (id, patient_id, document_id, session_id, kind, label, value, unit,
     normalized_json, source_text, confidence, needs_review,
     verification_status, fact_date, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (str(uuid.uuid4()), pid, None, None,
      "intake_answer", "diabetes_status", "yes", None,
      "{}", "prescription: diabetic",
      0.9, 0, "pending", now, now))

c.commit()
print("inserted 1 intake_answer + 1 clinical_fact (both labeled diabetes_status)")
