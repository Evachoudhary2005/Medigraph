import sqlite3, uuid
from datetime import datetime, timezone

pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"
now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(sep=" ")
c = sqlite3.connect("medigraph.db")

events = [
    ("q_hpi_associated", '["chest pain", "sweating"]', "chest pain and sweating for 2 hours"),
    ("q_cc_main",         "chest pain",                 "chest pain"),
]

for qid, val, excerpt in events:
    c.execute("""
        INSERT INTO timeline_events
        (id, patient_id, event_date, kind, label, value, normalized_json,
         source, source_ref, source_excerpt, confidence, needs_review,
         verification_status, conflict_group, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()), pid, now,
        "intake_answer", qid, val, "{}",
        "intake", "test", excerpt, 0.9, 0,
        "pending", None, now,
    ))

c.commit()
print("inserted", len(events), "red-flag events")
