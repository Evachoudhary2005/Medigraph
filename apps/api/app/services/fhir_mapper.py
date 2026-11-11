"""ABDM FHIR R4 mapper - HAPI-clean.

Emits only standard FHIR fields. Custom metadata is preserved on our side
(via the internal timeline / audit trail) and NOT injected as non-registered
extensions, which would fail HL7 validation.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.patient import Patient
from app.models.timeline import TimelineEvent

# ABDM profiles - loaded by name; if the IG isn't installed the validator
# only emits informational messages (not errors).
ABDM_PROFILE_PATIENT = "https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient"
ABDM_PROFILE_ENCOUNTER = "https://nrces.in/ndhm/fhir/r4/StructureDefinition/Encounter"
ABDM_PROFILE_MEDICATION_REQUEST = "https://nrces.in/ndhm/fhir/r4/StructureDefinition/MedicationRequest"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _uid() -> str:
    return str(uuid.uuid4())


def _narrative(text: str) -> dict:
    """Minimal narrative block to satisfy dom-6 (best-practice recommendation)."""
    return {
        "status": "generated",
        "div": f'<div xmlns="http://www.w3.org/1999/xhtml">{text}</div>',
    }


def _escape(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _patient_resource(p: Patient) -> dict:
    return {
        "resourceType": "Patient",
        "id": p.id,
        "text": _narrative(f"Patient {_escape(p.synthetic_id)}"),
        "identifier": [
            {
                "system": "https://medigraph.example.com/patient-id",
                "value": p.synthetic_id,
            },
        ],
        "active": True,
    }


def _encounter_resource(patient_id: str, started_at: str, encounter_id: str) -> dict:
    return {
        "resourceType": "Encounter",
        "id": encounter_id,
        "text": _narrative("Pre-consultation encounter"),
        "status": "finished",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory",
        },
        "subject": {"reference": "Patient/" + patient_id},
        "period": {"start": started_at},
    }


def _medication_request(patient_id: str, event: TimelineEvent, encounter_id: str) -> dict | None:
    generic = event.label
    if not generic:
        return None

    dosage: dict[str, Any] = {"text": event.value or generic}
    norm = {}
    try:
        import json as _j
        norm = _j.loads(event.normalized_json or "{}")
    except Exception:
        norm = {}

    if norm.get("frequency"):
        dosage["timing"] = {"code": {"text": norm["frequency"]}}
    if norm.get("duration"):
        dosage["patientInstruction"] = "for " + norm["duration"]

    authored = (event.event_date or datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "resourceType": "MedicationRequest",
        "id": _uid(),
        "text": _narrative(f"Prescription: {_escape(generic)}"),
        "status": "active",
        "intent": "order",
        "subject": {"reference": "Patient/" + patient_id},
        "encounter": {"reference": "Encounter/" + encounter_id},
        "authoredOn": authored,
        "medicationCodeableConcept": {"text": generic},
        "dosageInstruction": [dosage],
        "note": [{"text": "Source: " + (event.source_excerpt or "")}] if event.source_excerpt else [],
    }


def _condition(patient_id: str, event: TimelineEvent, encounter_id: str) -> dict | None:
    text = event.value or event.label
    if not text:
        return None
    return {
        "resourceType": "Condition",
        "id": _uid(),
        "text": _narrative(f"Condition: {_escape(str(text))}"),
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active",
                "display": "Active",
            }],
        },
        "subject": {"reference": "Patient/" + patient_id},
        "encounter": {"reference": "Encounter/" + encounter_id},
        "code": {"text": str(text)},
    }


def _observation(patient_id: str, event: TimelineEvent) -> dict | None:
    return {
        "resourceType": "Observation",
        "id": _uid(),
        "text": _narrative(f"Observation: {_escape(event.label)}"),
        "status": "preliminary",
        "subject": {"reference": "Patient/" + patient_id},
        "code": {"text": event.label},
        "valueString": event.value or "",
    }


def build_bundle(patient: Patient, events: list[TimelineEvent]) -> dict:
    started_at = min(
        (e.event_date for e in events if e.event_date),
        default=datetime.utcnow(),
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    encounter_id = _uid()
    entries: list[dict] = []

    # Patient
    patient_res = _patient_resource(patient)
    entries.append({"fullUrl": "urn:uuid:" + patient.id, "resource": patient_res})

    # Encounter
    enc_res = _encounter_resource(patient.id, started_at, encounter_id)
    entries.append({"fullUrl": "urn:uuid:" + encounter_id, "resource": enc_res})

    # Facts
    for e in events:
        if e.verification_status == "rejected":
            continue
        r = None
        if e.kind == "medication":
            r = _medication_request(patient.id, e, encounter_id)
        elif e.kind == "intake_answer":
            r = _condition(patient.id, e, encounter_id)
        elif e.kind == "investigation":
            r = _observation(patient.id, e)
        if r:
            entries.append({"fullUrl": "urn:uuid:" + r["id"], "resource": r})

    return {
        "resourceType": "Bundle",
        "id": _uid(),
        "type": "collection",
        "timestamp": _now_iso(),
        "entry": entries,
    }