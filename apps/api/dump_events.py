import sqlite3
c = sqlite3.connect("medigraph.db")
pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"
rows = c.execute(
    "SELECT kind, label, value, source, conflict_group FROM timeline_events WHERE patient_id=?",
    (pid,),
).fetchall()
print(f"total events: {len(rows)}")
for r in rows:
    print(f"  kind={r[0]!r:20} label={r[1]!r:25} value={r[2]!r:20} source={r[3]!r:12} cg={r[4]!r}")
