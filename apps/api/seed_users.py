from app.db.session import SessionLocal
from app.services.auth_service import seed_default_admin
db = SessionLocal()
seed_default_admin(db)
db.close()
print("seeded with example.com emails")
