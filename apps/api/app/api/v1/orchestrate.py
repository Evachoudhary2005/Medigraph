"""LangGraph orchestration endpoint.

Runs the full pipeline in one call:
    extract -> validate -> (review?) -> timeline -> summarize -> alerts -> fhir
"""
from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.patient import Patient
from app.orchestration.graph import GRAPH
from app.orchestration.state import PipelineState

log = logging.getLogger("medigraph.orchestrate")
router = APIRouter(prefix="/orchestrate", tags=["orchestrate"])


class OrchestrateRequest(BaseModel):
    document_id: str | None = None
    actor: str = "clinician"


@router.post("/{patient_id}")
def run_pipeline(patient_id: str, payload: OrchestrateRequest,
                 db: Session = Depends(get_db)):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")

    initial: PipelineState = {
        "patient_id": patient_id,
        "document_id": payload.document_id,
        "actor": payload.actor,
        "retries": 0,
        "errors": [],
        "log": [],
    }

    try:
        final = GRAPH.invoke(initial)
    except Exception as e:
        log.exception("graph failed: %s", e)
        raise HTTPException(500, f"graph failed: {type(e).__name__}: {e}")

    # Strip things that are too big to serialize fully
    bundle = final.get("bundle") or {}
    return {
        "patient_id": patient_id,
        "stage": final.get("stage"),
        "log": final.get("log", []),
        "confidence": final.get("confidence"),
        "needs_review": final.get("needs_review"),
        "timeline_count": final.get("timeline_count"),
        "alerts": final.get("alerts", []),
        "narrative": final.get("narrative"),
        "draft_id": final.get("draft_id"),
        "draft_version": final.get("draft_version"),
        "summary_sections": [
            {"key": s["key"], "title": s["title"], "item_count": len(s["items"])}
            for s in (final.get("summary") or {}).get("sections", [])
        ],
        "fhir": {
            "resource_types": [
                e["resource"]["resourceType"]
                for e in bundle.get("entry", [])
            ],
            "validation": final.get("validation"),
        },
        "errors": final.get("errors", []),
    }