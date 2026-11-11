import sqlite3
c = sqlite3.connect("medigraph.db")
pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"

print("--- intake_answers with label diabetes_status ---")
rows = c.execute(
    """
    SELECT a.question_id, a.value_json, a.source
    FROM intake_answers a
    JOIN intake_sessions s ON a.session_id = s.id
    WHERE s.patient_id = ? AND a.question_id LIKE '%diabetes%'
    """,
    (pid,),
).fetchall()
for r in rows:
    print(" ", r)

print("--- clinical_facts with label diabetes_status ---")
rows = c.execute(
    "SELECT kind, label, value, source_text FROM clinical_facts WHERE patient_id=? AND label LIKE '%diabetes%'",
    (pid,),
).fetchall()
for r in rows:
    print(" ", r)
