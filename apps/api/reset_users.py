import sqlite3
c = sqlite3.connect("medigraph.db")
c.execute("DELETE FROM users")
c.commit()
print("cleared users table")
