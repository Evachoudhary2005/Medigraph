"""Clinical summary generator via local Ollama.

Produces a cohesive clinical narrative that synthesizes the patient's
presenting complaints, medication profile, and documented facts into
a clinician-reviewable note.

Safety: NEVER diagnoses. The 'Clinical Impression' section proposes
working hypotheses only, explicitly marked for clinician review.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

log = logging.getLogger("medigraph.clinical_summary")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "medgemma:4b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))


_CLASS_INDICATIONS: dict[str, str] = {
    "beta_blocker":     "beta-blocker; commonly used for blood pressure, angina, or heart-rate control",
    "ace_inhibitor":    "ACE inhibitor; commonly used for blood pressure and heart failure",
    "arb":              "ARB; commonly used for blood pressure",
    "ccb":              "calcium-channel blocker; commonly used for blood pressure and angina",
    "diuretic":         "diuretic; commonly used for blood pressure and fluid overload",
    "statin":           "statin; commonly used for high cholesterol",
    "biguanide":        "biguanide; commonly used for type 2 diabetes",
    "sulfonylurea":     "sulfonylurea; commonly used for type 2 diabetes",
    "dpp4":             "DPP-4 inhibitor; commonly used for type 2 diabetes",
    "sglt2":            "SGLT2 inhibitor; commonly used for type 2 diabetes",
    "ppi":              "proton-pump inhibitor; commonly used for acid reflux",
    "h2_blocker":       "H2 blocker; commonly used for acid reflux and peptic ulcer disease",
    "anxiolytic":       "anxiolytic; commonly used for anxiety and short-term insomnia",
    "benzodiazepine":   "benzodiazepine; commonly used for anxiety, seizures, or muscle spasm",
    "ssri":             "SSRI; commonly used for depression and anxiety",
    "snri":             "SNRI; commonly used for depression and neuropathic pain",
    "tca":              "tricyclic antidepressant; commonly used for depression or neuropathic pain",
    "sedative":         "sedative; commonly used for procedural or ICU sedation",
    "analgesic":        "analgesic; commonly used for pain and fever",
    "nsaid":            "NSAID; commonly used for pain, fever, and inflammation",
    "opioid":           "opioid analgesic; commonly used for severe pain",
    "antibiotic":       "antibiotic; used to treat bacterial infection",
    "antiviral":        "antiviral; used to treat viral infection",
    "antifungal":       "antifungal; used to treat fungal infection",
    "antihistamine":    "antihistamine; commonly used for allergies",
    "antileukotriene":  "leukotriene inhibitor; commonly used for asthma and allergic rhinitis",
    "corticosteroid":   "corticosteroid; commonly used for inflammation or allergy",
    "thyroid":          "thyroid hormone replacement",
    "hormone":          "hormone therapy",
    "ca_inhibitor":     "carbonic-anhydrase inhibitor; commonly used for glaucoma",
    "supplement":       "nutritional supplement",
    "vitamin":          "vitamin supplement",
    "anticoagulant":    "anticoagulant; used to prevent blood clots",
    "antiplatelet":     "antiplatelet agent; used to prevent blood clots",
    "antiemetic":       "antiemetic; commonly used for nausea and vomiting",
    "antipyretic":      "antipyretic; used to reduce fever",
    "bronchodilator":   "bronchodilator; commonly used for asthma or COPD",
    "laxative":         "laxative; commonly used for constipation",
}


def _indication_for(drug_class: Optional[str]) -> str:
    if not drug_class:
        return ""
    return _CLASS_INDICATIONS.get(drug_class.lower(), "")


SYSTEM_PROMPT = """You are a clinical documentation assistant writing a summary for a clinician.

TASK: Write a coherent clinical narrative based ONLY on the recorded facts.

OUTPUT STRUCTURE (use these exact section headings, one blank line between sections):

Patient Summary
  One or two sentences: age, gender, date, presenting problem.

Presenting Complaints and History
  A short paragraph synthesizing the patient's reported symptoms.
  Use the RAW DOCUMENT TEXT below if the fact list is thin.
  List symptoms in natural prose, not bullets.

Medication Profile
  One line per medication in this exact format:
    - <name> <dose> <frequency> — <drug class>: <common purpose>
  The purpose comes from the drug-class hint provided. Do NOT invent.

Clinical Impression (for clinician review)
  Two or three sentences describing what the cluster of symptoms and
  medications could suggest. Use hedging language: "the pattern is
  consistent with", "may indicate", "commonly associated with".
  NEVER state a definite diagnosis. This section is a HYPOTHESIS ONLY.

Suggested Focus for Consultation
  Two or three bullets describing what the clinician should clarify
  or verify during the visit (e.g. symptom duration, triggers, safety).

CRITICAL RULES:
1. Use ONLY information from the facts and raw text below.
2. NEVER state a definite diagnosis.
3. NEVER prescribe or recommend a specific drug.
4. If a section has no data, write "Not recorded."
5. Mark any item with confidence below 0.70 as "(low confidence)".
6. Mark any conflicting item as "(conflict)" and list both values.
7. Keep the entire note under 400 words.
8. Write in third person (the patient).
9. Return ONLY the note. No markdown fences, no preamble.
"""


def _gather_facts(patient_id: str, db: Session) -> dict:
    from app.models.timeline import TimelineEvent
    from app.models.patient import Patient
    from app.models.document import Document

    p = db.get(Patient, patient_id)

    events = (
        db.query(TimelineEvent)
        .filter_by(patient_id=patient_id)
        .order_by(TimelineEvent.event_date.asc().nullslast(),
                  TimelineEvent.created_at.asc())
        .all()
    )

    facts = []
    for e in events:
        if e.verification_status == "rejected":
            continue
        norm = {}
        try:
            norm = json.loads(e.normalized_json or "{}")
        except Exception:
            norm = {}

        drug_class = norm.get("drug_class")
        indication = _indication_for(drug_class) if e.kind == "medication" else ""

        facts.append({
            "kind": e.kind,
            "label": e.label,
            "value": e.value,
            "confidence": float(e.confidence or 0.0),
            "source": e.source,
            "status": e.verification_status,
            "brand": norm.get("brand"),
            "warning": norm.get("suspicious_reason"),
            "drug_class": drug_class,
            "indication": indication,
        })

    # Pull raw text from the patient's documents so the LLM can pick up
    # complaints that our regex extractor missed (e.g. symptom phrases).
    raw_excerpts: list[str] = []
    docs = db.query(Document).filter_by(patient_id=patient_id).all()
    for d in docs:
        txt = (d.verified_text or d.ocr_text or "").strip()
        if txt:
            raw_excerpts.append(txt[:1200])  # cap per document

    raw_text = "\n---\n".join(raw_excerpts)[:3000]  # global cap

    return {
        "patient_id": patient_id,
        "synthetic_id": p.synthetic_id if p else patient_id,
        "language": p.preferred_language if p else "en",
        "facts": facts,
        "raw_text": raw_text,
    }


def _build_user_prompt(bundle: dict) -> str:
    lines = [f"Patient ID: {bundle['synthetic_id']}", ""]

    if bundle["facts"]:
        lines.append("Structured facts:")
        for f in bundle["facts"]:
            tag = f["kind"]
            name = f["label"]
            val = f.get("value") or ""
            extra = []
            if f.get("drug_class"):
                extra.append(f"class={f['drug_class']}")
            if f.get("indication"):
                extra.append(f"purpose: {f['indication']}")
            if f.get("brand"):
                extra.append(f"brand={f['brand']}")
            if f.get("warning"):
                extra.append(f"warning={f['warning']}")
            if f["confidence"] < 0.7:
                extra.append(f"confidence={f['confidence']:.2f}")
            if f["status"] == "conflicting":
                extra.append("CONFLICT")
            suffix = " (" + "; ".join(extra) + ")" if extra else ""
            lines.append(f"  - [{tag}] {name} {val}{suffix}".rstrip())
    else:
        lines.append("(No structured facts recorded.)")

    lines.append("")
    if bundle.get("raw_text"):
        lines.append("Raw document text (for context, may contain OCR errors):")
        lines.append(bundle["raw_text"])
        lines.append("")

    lines.append("Write the clinical note following the structure and rules in your system prompt.")
    return "\n".join(lines)


def _normalize_dashes(text: str) -> str:
    replacements = {
        "\u2014": "-", "\u2013": "-", "\u2012": "-", "\u2015": "-",
        "\u2212": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00a0": " ",
    }
    for u, a in replacements.items():
        text = text.replace(u, a)
    return text


def generate_narrative(patient_id: str, db: Session) -> dict:
    bundle = _gather_facts(patient_id, db)

    if not bundle["facts"] and not bundle["raw_text"]:
        return {
            "patient_id": patient_id,
            "narrative": "No facts or documents available for this patient.",
            "model": "n/a",
            "generated_at": datetime.utcnow().isoformat(),
            "facts_used": 0,
            "error": "no_data",
        }

    try:
        import ollama
    except ImportError:
        return {
            "patient_id": patient_id,
            "narrative": "(Ollama not installed. Run: pip install ollama)",
            "model": "n/a",
            "generated_at": datetime.utcnow().isoformat(),
            "facts_used": len(bundle["facts"]),
            "error": "ollama_missing",
        }

    user_prompt = _build_user_prompt(bundle)
    log.info("generating clinical note with %s (%d facts, %d chars raw)",
             OLLAMA_MODEL, len(bundle["facts"]), len(bundle["raw_text"]))

    try:
        client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)
        resp = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": 0.2, "num_predict": 1500},
        )
        raw = resp["message"]["content"] if isinstance(resp, dict) else resp.message.content
        raw = (raw or "").strip()
        raw = _normalize_dashes(raw)

        if raw.startswith("```"):
            parts = raw.split("```")
            if len(parts) >= 2:
                raw = parts[1]
                if raw.lstrip().startswith(("markdown", "md", "text")):
                    raw = raw.split("\n", 1)[1] if "\n" in raw else raw
                raw = raw.strip()

        log.info("generated %d chars of clinical note", len(raw))

        return {
            "patient_id": patient_id,
            "narrative": raw,
            "model": OLLAMA_MODEL,
            "generated_at": datetime.utcnow().isoformat(),
            "facts_used": len(bundle["facts"]),
            "error": None,
        }
    except Exception as e:
        log.exception("clinical note generation failed: %s", e)
        return {
            "patient_id": patient_id,
            "narrative": f"(Generation failed: {type(e).__name__}: {e})",
            "model": OLLAMA_MODEL,
            "generated_at": datetime.utcnow().isoformat(),
            "facts_used": len(bundle["facts"]),
            "error": "generation_failed",
        }