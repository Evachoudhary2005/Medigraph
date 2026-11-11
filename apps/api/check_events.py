import sqlite3
c = sqlite3.connect("medigraph.db")
pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"
rows = c.execute(
    "SELECT label, value, source, source_ref FROM timeline_events WHERE patient_id=?",
    (pid,),
).fetchall()
print(f"Total events: {len(rows)}")
for r in rows:
    print(r)
