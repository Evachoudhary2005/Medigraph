import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.patient import Patient, Consent
from app.models.timeline import TimelineEvent
from app.models.document import Document
from app.services.fhir_mapper import build_bundle
from app.services.fhir_validator import validate_bundle, is_available
from app.services import audit

router = APIRouter(prefix="/fhir", tags=["fhir"])


@router.post("/export/{patient_id}")
def export_bundle(patient_id: str, actor: str = "clinician",
                  db: Session = Depends(get_db)):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")

    events = (
        db.query(TimelineEvent)
        .filter_by(patient_id=patient_id)
        .order_by(TimelineEvent.event_date.asc().nullslast())
        .all()
    )
    if not events:
        raise HTTPException(400, "no timeline events to export")

    bundle = build_bundle(p, events)

    # -------- Minimal structural validation --------
    issues: list[str] = []
    if bundle.get("resourceType") != "Bundle":
        issues.append("root must be a Bundle")
    entries = bundle.get("entry", [])
    if not any(e["resource"]["resourceType"] == "Patient" for e in entries):
        issues.append("missing Patient resource")
    if not any(e["resource"]["resourceType"] == "Encounter" for e in entries):
        issues.append("missing Encounter resource")
    for e in entries:
        r = e.get("resource", {})
        if not r.get("id"):
            issues.append(f"resource {r.get('resourceType')} has no id")
    valid = len(issues) == 0

    # ---- HAPI FHIR validator (official) ----
    hapi = None
    if is_available():
        try:
            hapi = validate_bundle(bundle, version="4.0")
        except Exception as e:
            log.exception("HAPI validation crashed: %s", e)

    audit.record(
        db, action="fhir.export", actor=actor, patient_id=patient_id,
        resource_type="Bundle", resource_id=bundle.get("id"),
        details={
            "entries": len(entries),
            "structural_valid": valid,
            "hapi_available": bool(hapi and hapi.get("available")),
            "hapi_valid": bool(hapi and hapi.get("valid")),
            "hapi_errors": (hapi or {}).get("error_count", 0),
        },
    )

    return {
        "bundle": bundle,
        "validation": {
            "valid": valid,
            "issues": issues,
            "entries": len(entries),
            "profile": "ABDM FHIR R4 (structural subset)",
        },
        "hapi_validation": hapi,
    }


@router.get("/export/{patient_id}")
def preview_bundle(patient_id: str, db: Session = Depends(get_db)):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")
    events = db.query(TimelineEvent).filter_by(patient_id=patient_id).all()
    return build_bundle(p, events)