import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.patient import Patient
from app.models.timeline import TimelineEvent
from app.services.summary_builder import build_draft
from app.services.alert_rules import evaluate

router = APIRouter(prefix="/summary", tags=["summary"])


def _event_to_dict(e: TimelineEvent) -> dict:
    return {
        "id": e.id,
        "event_date": e.event_date.isoformat() if e.event_date else None,
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


@router.get("/{patient_id}")
def get_summary(patient_id: str, db: Session = Depends(get_db)):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")

    events = (
        db.query(TimelineEvent)
        .filter_by(patient_id=patient_id)
        .order_by(TimelineEvent.event_date.asc().nullslast(),
                  TimelineEvent.created_at.asc())
        .all()
    )
    dicts = [_event_to_dict(e) for e in events]

    draft = build_draft(patient_id, dicts)
    alerts = evaluate(dicts)

    return {
        "patient_id": patient_id,
        "draft": draft,
        "alerts": alerts,
        "events_count": len(dicts),
    }


@router.get("/{patient_id}/alerts")
def get_alerts(patient_id: str, db: Session = Depends(get_db)):
    events = (
        db.query(TimelineEvent)
        .filter_by(patient_id=patient_id)
        .all()
    )
    dicts = [_event_to_dict(e) for e in events]
    return evaluate(dicts)

# ---------- Saved drafts (edit + resave) ----------

class SaveDraftRequest(BaseModel):
    sections: list          # [{key, title, items:[{event_id, text, ...}]}]
    notes: str = ""
    actor: str = "clinician"
    status: str = "draft"   # draft | approved


@router.post("/{patient_id}/save")
def save_draft(patient_id: str, payload: SaveDraftRequest,
               db: Session = Depends(get_db)):
    """Persist a clinician-edited version of the summary."""
    import uuid as _uuid
    from app.models.summary_draft import SummaryDraft
    from app.services import audit

    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")

    # next version number
    prev = (
        db.query(SummaryDraft)
        .filter_by(patient_id=patient_id)
        .order_by(SummaryDraft.version.desc())
        .first()
    )
    next_ver = (prev.version + 1) if prev else 1

    d = SummaryDraft(
        id=str(_uuid.uuid4()),
        patient_id=patient_id,
        version=next_ver,
        sections_json=json.dumps(payload.sections, ensure_ascii=False),
        notes=payload.notes,
        actor=payload.actor,
        status=payload.status,
    )
    db.add(d)
    db.commit()
    db.refresh(d)

    audit.record(
        db, action="summary.save", actor=payload.actor, patient_id=patient_id,
        resource_type="SummaryDraft", resource_id=d.id,
        details={"version": next_ver, "status": payload.status,
                 "sections": len(payload.sections)},
    )

    return {
        "id": d.id,
        "version": d.version,
        "status": d.status,
        "actor": d.actor,
        "notes": d.notes,
        "created_at": d.created_at,
    }


@router.get("/{patient_id}/drafts")
def list_drafts(patient_id: str, db: Session = Depends(get_db)):
    from app.models.summary_draft import SummaryDraft
    rows = (
        db.query(SummaryDraft)
        .filter_by(patient_id=patient_id)
        .order_by(SummaryDraft.version.desc())
        .all()
    )
    return [
        {
            "id": d.id,
            "version": d.version,
            "status": d.status,
            "actor": d.actor,
            "notes": d.notes,
            "created_at": d.created_at,
            "section_count": len(json.loads(d.sections_json or "[]")),
        }
        for d in rows
    ]


@router.get("/drafts/{draft_id}")
def get_draft(draft_id: str, db: Session = Depends(get_db)):
    from app.models.summary_draft import SummaryDraft
    d = db.get(SummaryDraft, draft_id)
    if not d:
        raise HTTPException(404, "draft not found")
    return {
        "id": d.id,
        "patient_id": d.patient_id,
        "version": d.version,
        "status": d.status,
        "actor": d.actor,
        "notes": d.notes,
        "created_at": d.created_at,
        "sections": json.loads(d.sections_json or "[]"),
    }


# ---------- Saved drafts (edit + resave) ----------

class SaveDraftRequest(BaseModel):
    sections: list          # [{key, title, items:[{event_id, text, ...}]}]
    notes: str = ""
    actor: str = "clinician"
    status: str = "draft"   # draft | approved


class SaveDraftRequest(BaseModel):
    sections: list          # [{key, title, items:[{event_id, text, ...}]}]
    notes: str = ""
    actor: str = "clinician"
    status: str = "draft"   # draft | approved


class SaveDraftRequest(BaseModel):
    sections: list          # [{key, title, items:[{event_id, text, ...}]}]
    notes: str = ""
    actor: str = "clinician"
    status: str = "draft"   # draft | approved


class SaveDraftRequest(BaseModel):
    sections: list          # [{key, title, items:[{event_id, text, ...}]}]
    notes: str = ""
    actor: str = "clinician"
    status: str = "draft"   # draft | approved


@router.get("/{patient_id}/pdf")
def export_pdf(patient_id: str, db: Session = Depends(get_db)):
    """Render the current summary draft to a PDF and return it as a download."""
    from fastapi.responses import Response
    from app.services.pdf_renderer import build_summary_pdf
    from app.models.timeline import TimelineEvent
    from app.services.summary_builder import build_draft
    from app.services.alert_rules import evaluate as evaluate_alerts
    from app.services import audit

    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")

    events = (
        db.query(TimelineEvent)
        .filter_by(patient_id=patient_id)
        .order_by(TimelineEvent.event_date.asc().nullslast(),
                  TimelineEvent.created_at.asc())
        .all()
    )
    dicts = [_event_to_dict(e) for e in events]
    draft = build_draft(patient_id, dicts)
    alerts = evaluate_alerts(dicts)

    pdf_bytes = build_summary_pdf(
        patient_id=patient_id,
        patient_label=p.synthetic_id,
        sections=draft["sections"],
        alerts=alerts,
        generated_by="clinician",
    )

    audit.record(db, action="summary.pdf_export", actor="clinician",
                 patient_id=patient_id, resource_type="SummaryPDF",
                 details={"bytes": len(pdf_bytes),
                          "sections": len(draft["sections"]),
                          "alerts": len(alerts)})

    filename = f"medigraph-summary-{p.synthetic_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------- AI-generated narrative ----------

@router.post("/{patient_id}/generate")
def generate_ai_summary(patient_id: str, actor: str = "clinician",
                        db: Session = Depends(get_db)):
    """Run the local LLM and produce one cohesive clinical note."""
    import uuid as _uuid
    from app.services.clinical_summary_generator import generate_narrative
    from app.models.summary_draft import SummaryDraft
    from app.services import audit

    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")

    result = generate_narrative(patient_id, db)

    # Store as a summary_draft with a single-section narrative
    prev = (
        db.query(SummaryDraft)
        .filter_by(patient_id=patient_id)
        .order_by(SummaryDraft.version.desc())
        .first()
    )
    next_ver = (prev.version + 1) if prev else 1

    narrative_section = [{
        "key": "narrative",
        "title": "Clinical Note (AI-generated)",
        "items": [{
            "event_id": "narrative",
            "text": result["narrative"],
            "confidence": 1.0,
            "source": "ai",
            "needs_review": False,
            "verification_status": "pending",
            "warnings": [],
        }],
    }]

    d = SummaryDraft(
        id=str(_uuid.uuid4()),
        patient_id=patient_id,
        version=next_ver,
        sections_json=json.dumps(narrative_section, ensure_ascii=False),
        notes=f"AI-generated narrative via {result.get('model','?')}",
        actor=actor,
        status="ai_generated",
    )
    db.add(d)
    db.commit()
    db.refresh(d)

    audit.record(
        db, action="summary.generate_ai", actor=actor, patient_id=patient_id,
        resource_type="SummaryDraft", resource_id=d.id,
        details={"model": result.get("model"), "facts_used": result.get("facts_used"),
                 "error": result.get("error")},
    )

    return {
        "patient_id": patient_id,
        "narrative": result["narrative"],
        "model": result.get("model"),
        "generated_at": result.get("generated_at"),
        "facts_used": result.get("facts_used", 0),
        "error": result.get("error"),
        "draft_id": d.id,
        "version": next_ver,
    }
