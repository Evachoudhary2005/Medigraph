import sqlite3
c = sqlite3.connect("medigraph.db")
n = c.execute("DELETE FROM timeline_events WHERE source_ref='test'").rowcount
c.commit()
print(f"deleted {n} test events")

# Show what remains
rows = c.execute(
    "SELECT label, value, source FROM timeline_events WHERE patient_id=?",
    ("4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb",),
).fetchall()
print(f"remaining events: {len(rows)}")
for r in rows:
    print(" ", r)
