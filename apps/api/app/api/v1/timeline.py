import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.patient import Patient
from app.models.timeline import TimelineEvent
from app.services.timeline_builder import build_timeline

router = APIRouter(prefix="/timeline", tags=["timeline"])


def _out(e: TimelineEvent) -> dict:
    return {
        "id": e.id,
        "event_date": e.event_date,
        "kind": e.kind,
        "label": e.label,
        "value": e.value,
        "normalized": json.loads(e.normalized_json or "{}"),
        "source": e.source,
        "source_ref": e.source_ref,
        "source_excerpt": e.source_excerpt,
        "confidence": e.confidence,
        "needs_review": e.needs_review,
        "verification_status": e.verification_status,
        "conflict_group": e.conflict_group,
    }


@router.post("/build/{patient_id}")
def build(patient_id: str, db: Session = Depends(get_db)):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")
    events = build_timeline(patient_id, db)
    return {"patient_id": patient_id, "count": len(events),
            "events": [_out(e) for e in events]}


@router.get("")
def list_timeline(patient_id: str, db: Session = Depends(get_db)):
    events = (
        db.query(TimelineEvent)
        .filter_by(patient_id=patient_id)
        .order_by(TimelineEvent.event_date.desc().nullslast(),
                  TimelineEvent.created_at.desc())
        .all()
    )
    return [_out(e) for e in events]


@router.post("/{event_id}/verify")
def verify_event(event_id: str, action: str = "approve",
                 db: Session = Depends(get_db)):
    e = db.get(TimelineEvent, event_id)
    if not e:
        raise HTTPException(404, "event not found")
    e.verification_status = "verified" if action == "approve" else "rejected"
    e.needs_review = False
    db.commit()
    return _out(e)

@router.get("/review-queue")
def review_queue(db: Session = Depends(get_db)):
    """All events flagged needs_review across all patients."""
    rows = (
        db.query(TimelineEvent)
        .filter(TimelineEvent.needs_review == True)  # noqa: E712
        .filter(TimelineEvent.verification_status.in_(["pending", "conflicting"]))
        .order_by(TimelineEvent.created_at.desc())
        .limit(200)
        .all()
    )
    return [
        {
            "id": e.id,
            "patient_id": e.patient_id,
            "event_date": e.event_date,
            "kind": e.kind,
            "label": e.label,
            "value": e.value,
            "source": e.source,
            "source_excerpt": e.source_excerpt,
            "confidence": e.confidence,
            "needs_review": e.needs_review,
            "verification_status": e.verification_status,
        }
        for e in rows
    ]
