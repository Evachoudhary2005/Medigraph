import sqlite3, json
c = sqlite3.connect("medigraph.db")
pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"
rows = c.execute(
    "SELECT id, version, status, actor, notes, created_at FROM summary_drafts WHERE patient_id=? ORDER BY version DESC LIMIT 10",
    (pid,),
).fetchall()
print(f"Total drafts: {len(rows)}")
for r in rows:
    print(f"  v{r[1]} status={r[2]:15} by {r[3]:10} {r[4][:50] if r[4] else ''}")
