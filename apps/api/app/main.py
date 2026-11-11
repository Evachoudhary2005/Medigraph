import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1 import api_router
from app.db.session import Base, engine, SessionLocal
from app.models import patient, intake, document, fact, timeline, audit, user, summary_draft  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    from app.services.auth_service import seed_default_admin
    db = SessionLocal()
    try:
        seed_default_admin(db)
    finally:
        db.close()


# Serve uploaded sample files (images, PDFs) for the document viewer
app.mount("/samples", StaticFiles(directory="data/samples"), name="samples")

app.include_router(api_router)