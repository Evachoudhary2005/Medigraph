import sqlite3
c = sqlite3.connect("medigraph.db")
print(f'{"synthetic_id":14} {"patient_id":38} {"sess":>4} {"ans":>4} {"docs":>4} {"facts":>5}')
for pid, sid in c.execute("SELECT id, synthetic_id FROM patients").fetchall():
    s = c.execute("SELECT COUNT(*) FROM intake_sessions WHERE patient_id=?", (pid,)).fetchone()[0]
    a = c.execute("SELECT COUNT(*) FROM intake_answers a JOIN intake_sessions s ON a.session_id=s.id WHERE s.patient_id=?", (pid,)).fetchone()[0]
    d = c.execute("SELECT COUNT(*) FROM documents WHERE patient_id=?", (pid,)).fetchone()[0]
    f = c.execute("SELECT COUNT(*) FROM clinical_facts WHERE patient_id=?", (pid,)).fetchone()[0]
    if s or a or d or f:
        print(f'{sid:14} {pid:38} {s:>4} {a:>4} {d:>4} {f:>5}')
