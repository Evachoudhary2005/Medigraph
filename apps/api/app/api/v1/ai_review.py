"""AI summary review - separate router to avoid path collisions."""
from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.patient import Patient
from app.models.summary_draft import SummaryDraft
from app.services import audit

log = logging.getLogger("medigraph.ai_review")
router = APIRouter(prefix="/ai", tags=["ai-review"])


@router.get("/queue")
def ai_review_queue(db: Session = Depends(get_db)):
    """Every AI-generated narrative awaiting clinician review."""
    rows = (
        db.query(SummaryDraft)
        .filter(SummaryDraft.status == "ai_generated")
        .order_by(SummaryDraft.created_at.desc())
        .limit(100)
        .all()
    )

    out = []
    for d in rows:
        p = db.get(Patient, d.patient_id)
        sections = json.loads(d.sections_json or "[]")
        narrative = ""
        for s in sections:
            for it in s.get("items", []):
                narrative = it.get("text", "")
                break
            if narrative:
                break
        # Return the full narrative - the review queue needs it for the clinician to read
        preview = narrative
        out.append({
            "draft_id": d.id,
            "patient_id": d.patient_id,
            "synthetic_id": p.synthetic_id if p else d.patient_id[:8],
            "version": d.version,
            "status": d.status,
            "actor": d.actor,
            "model_note": d.notes,
            "generated_at": d.created_at,
            "preview": preview,
        })
    return out


@router.get("/drafts/{draft_id}")
def get_ai_draft(draft_id: str, db: Session = Depends(get_db)):
    d = db.get(SummaryDraft, draft_id)
    if not d:
        raise HTTPException(404, "draft not found")
    sections = json.loads(d.sections_json or "[]")
    narrative = ""
    for s in sections:
        for it in s.get("items", []):
            narrative = it.get("text", "")
            break
        if narrative:
            break
    return {
        "draft_id": d.id,
        "patient_id": d.patient_id,
        "version": d.version,
        "status": d.status,
        "narrative": narrative,
        "model_note": d.notes,
        "created_at": d.created_at,
    }


class DraftDecision(BaseModel):
    action: str = "approve"
    edited_narrative: str | None = None
    actor: str = "clinician"


@router.post("/drafts/{draft_id}/decision")
def decide_draft(draft_id: str, payload: DraftDecision,
                 db: Session = Depends(get_db)):
    d = db.get(SummaryDraft, draft_id)
    if not d:
        raise HTTPException(404, "draft not found")

    if payload.action not in ("approve", "reject", "edit"):
        raise HTTPException(400, "action must be approve, reject, or edit")

    sections = json.loads(d.sections_json or "[]")

    if payload.edited_narrative is not None:
        for s in sections:
            for it in s.get("items", []):
                it["text"] = payload.edited_narrative
                it["verification_status"] = "edited"

    if payload.action == "approve":
        for s in sections:
            for it in s.get("items", []):
                it["verification_status"] = "verified"
        d.status = "approved"
    elif payload.action == "reject":
        for s in sections:
            for it in s.get("items", []):
                it["verification_status"] = "rejected"
        d.status = "rejected"
    else:
        d.status = "edited"

    d.sections_json = json.dumps(sections, ensure_ascii=False)
    d.actor = payload.actor
    db.commit()
    db.refresh(d)

    audit.record(
        db, action="summary.ai_" + payload.action, actor=payload.actor,
        patient_id=d.patient_id, resource_type="SummaryDraft", resource_id=d.id,
        details={"version": d.version},
    )

    return {"draft_id": d.id, "status": d.status, "version": d.version}

@router.get("/patient/{patient_id}/latest")
def latest_ai_for_patient(patient_id: str, db: Session = Depends(get_db)):
    """Return the newest approved/edited AI narrative for a patient.

    Falls back to the newest ai_generated draft if nothing is approved yet.
    Returns null narrative if no AI draft exists.
    """
    rows = (
        db.query(SummaryDraft)
        .filter(SummaryDraft.patient_id == patient_id)
        .filter(SummaryDraft.status.in_(["approved", "edited", "ai_generated"]))
        .order_by(SummaryDraft.version.desc())
        .all()
    )
    if not rows:
        return {"patient_id": patient_id, "narrative": None, "status": None,
                "version": None, "model_note": None, "created_at": None}

    # Prefer the newest approved/edited, else fall back to the newest draft
    chosen = None
    for r in rows:
        if r.status in ("approved", "edited"):
            chosen = r
            break
    if chosen is None:
        chosen = rows[0]

    sections = json.loads(chosen.sections_json or "[]")
    narrative = ""
    for s in sections:
        for it in s.get("items", []):
            narrative = it.get("text", "")
            break
        if narrative:
            break

    return {
        "patient_id": patient_id,
        "draft_id": chosen.id,
        "narrative": narrative,
        "status": chosen.status,
        "version": chosen.version,
        "model_note": chosen.notes,
        "created_at": chosen.created_at,
    }
