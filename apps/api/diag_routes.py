from app.main import app
from app.api.v1 import api_router

print("api_router routes:", len(api_router.routes))
print("app.routes:", len(app.routes))
print("app.router.routes:", len(app.router.routes))
print("openapi paths:", len(app.openapi()["paths"]))
print()
print("--- first 10 entries in app.routes ---")
for r in list(app.routes)[:10]:
    print(" ", getattr(r, "path", getattr(r, "path_format", r)))
print()
print("--- first 10 entries in api_router.routes ---")
for r in list(api_router.routes)[:10]:
    print(" ", getattr(r, "path", getattr(r, "path_format", r)))
