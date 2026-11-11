from fastapi import APIRouter
from app.api.v1 import (
    health, patients, questionnaires, intake_sessions, speech,
    documents, facts, timeline, summary, fhir, consents, orchestrate, auth,
    ai_review,
)

api_router = APIRouter(prefix="/api/v1")
for r in (health.router, patients.router, questionnaires.router,
          intake_sessions.router, speech.router, documents.router,
          facts.router, timeline.router, summary.router,
          fhir.router, consents.router, orchestrate.router, auth.router,
          ai_review.router):
    api_router.include_router(r)