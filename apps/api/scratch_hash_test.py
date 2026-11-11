from app.services.auth_service import hash_password, _pwd
import bcrypt

print("Testing _pwd.hash:")
try:
    h = hash_password("test1234")
    print("hash_password:", h)
except Exception as e:
    import traceback
    traceback.print_exc()

print("Testing direct bcrypt:")
salt = bcrypt.gensalt()
bh = bcrypt.hashpw("test1234".encode("utf-8"), salt).decode("utf-8")
print("direct hash:", bh)
print("direct verify:", bcrypt.checkpw("test1234".encode("utf-8"), bh.encode("utf-8")))
