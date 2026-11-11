import sqlite3
c = sqlite3.connect("medigraph.db")
rows = c.execute(
    "SELECT label, value, source, source_ref FROM timeline_events WHERE source_ref LIKE ?",
    ("conflict-test%",),
).fetchall()
print("rows:", len(rows))
for r in rows:
    print(r)
