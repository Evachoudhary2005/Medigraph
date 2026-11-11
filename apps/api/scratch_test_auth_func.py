from app.db.session import SessionLocal
from app.services.auth_service import authenticate
from app.models.user import User

db = SessionLocal()
u = authenticate(db, "clinician@medigraph.example.com", "clinic123")
print("authenticate clinician result:", u)
if u:
    print("User email:", u.email, "role:", u.role)
db.close()
