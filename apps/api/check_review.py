import sqlite3
c = sqlite3.connect("medigraph.db")
rows = c.execute(
    "SELECT kind, label, value, needs_review, verification_status FROM timeline_events WHERE patient_id=?",
    ("4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb",),
).fetchall()
print(f"total: {len(rows)}")
for r in rows:
    print(f"  kind={r[0]!r:20} label={r[1]!r:25} needs_review={r[3]!r:8} vs={r[4]!r}")
