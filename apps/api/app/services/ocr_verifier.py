"""Local LLM-based OCR verification using Ollama.

Runs entirely on-premises ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â no patient data leaves the machine.
Provides:
  - verify_ocr(): full document verification (text + fields + corrections)
  - correct_medications(): focused medicine-name-only correction pass
"""
from __future__ import annotations

import json
import logging
import os
import re as _re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

# ---- Load .env from repo root and apps/api so OLLAMA_* env vars are visible ----
try:
    from dotenv import load_dotenv
    for p in (
        Path(__file__).resolve().parents[3] / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    ):
        if p.exists():
            load_dotenv(p, override=False)
except ImportError:
    pass

log = logging.getLogger("medigraph.verifier")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "medgemma:4b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))


# ---------- Pydantic schema for structured output ----------

class Medication(BaseModel):
    generic: Optional[str] = None
    brand: Optional[str] = None
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    confidence: float = 0.0


class Investigation(BaseModel):
    name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    confidence: float = 0.0


class ExtractedFields(BaseModel):
    patient_name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    issue_date: Optional[str] = None
    complaints: list[str] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    diagnoses: list[str] = Field(default_factory=list)
    investigations: list[Investigation] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    follow_up: Optional[str] = None


class Correction(BaseModel):
    region_idx: int
    original: str
    corrected: str
    confidence: float


class VerificationResult(BaseModel):
    verified_text: str
    fields: ExtractedFields
    corrections: list[Correction] = Field(default_factory=list)
    overall_confidence: float = 0.0
    needs_human_review: bool = False
    review_reasons: list[str] = Field(default_factory=list)


SYSTEM_PROMPT = """You are a clinical OCR correction assistant for Indian and international medical documents.

INPUT: Raw OCR text from a prescription, lab report, or discharge summary.
Contains OCR errors: misread characters, misspelled English, garbled Hindi, mis-segmented words.

TASK: Produce a corrected, structured version.

RULES:
1. NEVER invent information not in the input. If unsure, keep the original.
2. NEVER add diagnoses, treatments, or clinical advice.
3. Preserve original text in each correction entry.
4. Recognize common drug brands:
   - "Betaloc" -> Metoprolol
   - "Oxprelol" -> Oxprenolol
   - "Dorzolamidum" -> Dorzolamide
   - "201calm" -> Etizolam
   - "Clonelst" / "Clonotril" -> Clonazepam
   - "Crocin" / "Dolo" -> Paracetamol
5. Normalize frequencies:
   OD = once daily, BD = twice daily, TDS = thrice daily,
   QID = four times daily, HS = at bedtime, SOS = if needed, STAT = immediately.
6. Normalize dates to YYYY-MM-DD (Indian format is often DDMMYYYY).
7. Per-field confidence 0-1:
   - 1.0 = verbatim in OCR, unambiguous
   - 0.8-0.99 = obvious OCR fix
   - 0.5-0.79 = plausible correction, human should verify
   - < 0.5 = guess, flag for review
8. Output ONLY valid JSON matching the schema. No markdown fences, no prose.
"""


_TYPICAL_MG = {
    "Metoprolol": (25, 200), "Oxprenolol": (20, 320), "Atenolol": (25, 100),
    "Propranolol": (10, 320), "Cimetidine": (200, 800), "Ranitidine": (75, 300),
    "Omeprazole": (10, 40), "Pantoprazole": (20, 80), "Etizolam": (0.25, 1.5),
    "Clonazepam": (0.25, 2), "Alprazolam": (0.25, 2), "Metformin": (250, 2000),
    "Amlodipine": (2.5, 10), "Atorvastatin": (5, 80), "Paracetamol": (325, 1000),
    "Ibuprofen": (200, 800), "Azithromycin": (250, 500), "Cetirizine": (5, 20),
    "Dorzolamide": (5, 20),
}


def _sanity(generic: str, value_mg: float) -> tuple[bool, Optional[str]]:
    rng = _TYPICAL_MG.get(generic)
    if rng and not (rng[0] <= value_mg <= rng[1]):
        return True, f"{generic} {value_mg}mg outside typical {rng[0]}-{rng[1]} mg"
    return False, None


def _ollama_chat(messages: list[dict], schema: Optional[dict] = None,
                 num_predict: int = 4096) -> Optional[str]:
    """Call Ollama and return raw content string, or None on failure."""
    try:
        import ollama
    except ImportError:
        log.warning("ollama not installed")
        return None
    try:
        client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)
        kwargs = dict(
            model=OLLAMA_MODEL,
            messages=messages,
            options={"temperature": 0, "num_predict": num_predict},
        )
        if schema is not None:
            kwargs["format"] = schema
        else:
            kwargs["format"] = "json"
        response = client.chat(**kwargs)
        raw = response["message"]["content"] if isinstance(response, dict) else response.message.content
        raw = (raw or "").strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            if len(parts) >= 2:
                raw = parts[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
        return raw
    except Exception as e:
        log.exception("ollama call failed: %s", e)
        return None


def verify_ocr(regions: list[dict], document_type: str = "other",
               language: str = "en") -> Optional[dict]:
    if not regions:
        return None

    lines = [f"[{i}] (conf={r.get('confidence', 0):.2f}) {r.get('text', '')}"
             for i, r in enumerate(regions)]
    regions_text = "\n".join(lines)

    user_prompt = (
        f"Document type (heuristic): {document_type}\n"
        f"Language hint: {language}\n\n"
        f"Raw OCR regions:\n{regions_text}\n\n"
        f"Return ONLY the JSON object described in the system prompt schema."
    )

    log.info("calling Ollama model=%s for %d regions", OLLAMA_MODEL, len(regions))
    raw = _ollama_chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        schema=VerificationResult.model_json_schema(),
        num_predict=4096,
    )
    if not raw:
        return None

    try:
        result = VerificationResult.model_validate_json(raw)
    except Exception as e:
        log.error("model_validate_json failed: %s", e)
        log.debug("raw response: %s", raw[:500])
        return None

    # ---------- Code-level guards (never trust the LLM on these) ----------

    # Age must be digits-only
    if result.fields.age:
        m = _re.search(r"\d+", str(result.fields.age))
        result.fields.age = m.group(0) if m else None
        if result.fields.age and not (1 <= int(result.fields.age) <= 120):
            result.fields.age = None

    # Fill blank medication names from corrections
    STOP = {"Tab", "Cap", "Inj", "Syp", "Syrup", "Day", "Days", "The", "And",
            "With", "For", "Take", "Rx", "Rx.", "Tab.", "Cap."}
    for med in result.fields.medications:
        if not med.generic and not med.brand:
            for corr in result.corrections:
                cand = (corr.corrected or "") + " " + (corr.original or "")
                words = [w for w in _re.findall(r"[A-Z][a-zA-Z]{2,}", cand) if w not in STOP]
                if words:
                    med.brand = words[0]
                    break

    # If the LLM left confidence at 0 but did resolve generic names,
    # derive a confidence score from the resolution outcome.
    for med in result.fields.medications:
        if med.confidence and med.confidence > 0.0:
            continue
        generic = (med.generic or "").strip()
        brand = (med.brand or "").strip()
        if generic and brand and generic.lower() != brand.lower():
            # LLM recognized a brand Ã¢â€ â€™ mapped it to a generic (reliable)
            med.confidence = 0.9
        elif generic and not brand:
            # LLM gave generic directly, no brand (moderately reliable)
            med.confidence = 0.8
        elif generic and brand and generic.lower() == brand.lower():
            # Brand = generic (common INN names like Cimetidine) Ã¢â‚¬â€ reliable
            med.confidence = 0.85
        else:
            # No name resolved at all
            med.confidence = 0.4

    # If ALL medication confidences were 0 initially, recompute overall_confidence
    if result.overall_confidence == 0.0 or (
        result.overall_confidence <= 0.5 and result.fields.medications
    ):
        confs = [m.confidence for m in result.fields.medications if m.confidence > 0]
        if confs:
            result.overall_confidence = round(sum(confs) / len(confs), 2)

    # Compute overall_confidence if the LLM left it at 0
    if result.overall_confidence == 0.0:
        confs = ([m.confidence for m in result.fields.medications if m.confidence > 0] +
                 [i.confidence for i in result.fields.investigations if i.confidence > 0])
        if confs:
            result.overall_confidence = round(sum(confs) / len(confs), 2)
        elif result.corrections:
            result.overall_confidence = round(
                sum(c.confidence for c in result.corrections) / len(result.corrections), 2)
        else:
            result.overall_confidence = 0.5

    # Flag ambiguous dates
    if result.fields.issue_date:
        iso_ok = _re.match(r"^\d{4}-\d{2}-\d{2}$", result.fields.issue_date)
        eu_ok = _re.match(r"^\d{2}[-/]\d{2}[-/]\d{2,4}$", result.fields.issue_date)
        if not iso_ok and not eu_ok:
            result.fields.issue_date = None
            if "Date format ambiguous" not in " ".join(result.review_reasons):
                result.review_reasons.append("Date format ambiguous ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â needs human review")

    # Re-evaluate needs_human_review
    low_conf = [m for m in result.fields.medications if m.confidence < 0.5]
    unnamed = [m for m in result.fields.medications if not m.generic and not m.brand]
    if result.overall_confidence < 0.7 or low_conf or unnamed:
        result.needs_human_review = True
        if result.overall_confidence < 0.7 and not any("Overall confidence" in r for r in result.review_reasons):
            result.review_reasons.append(
                f"Overall confidence {result.overall_confidence:.2f} below threshold")
        for m in low_conf:
            result.review_reasons.append(
                f"Low-confidence medication: {m.brand or m.generic or 'unknown'}")
        if unnamed:
            result.review_reasons.append(
                f"{len(unnamed)} medication(s) missing a name ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â needs manual entry")

    log.info("verifier ok: %d meds, %d complaints, overall=%.2f, review=%s",
             len(result.fields.medications), len(result.fields.complaints),
             result.overall_confidence, result.needs_human_review)
    return result.model_dump()


# ---------- Optional: focused medicine-only correction pass ----------

MEDICINE_PROMPT = """You are a clinical pharmacologist correcting OCR errors in medication names.

INPUT: Raw OCR text from a prescription.
TASK: For each medication line, produce:
- brand_raw: as OCR'd
- brand_corrected: spelling fixed
- generic: INN name (or null if unknown)
- drug_class: e.g. beta_blocker, benzodiazepine
- dose_value, dose_unit, frequency, duration
- suspicious_dose (boolean), suspicious_reason
- confidence 0-1

RULES:
1. Never invent a drug. If unrecognized, generic=null, confidence<=0.4.
2. Common mappings: Betaloc->Metoprolol, Oxprelol->Oxprenolol,
   Dorzolamidum->Dorzolamide, 201calm->Etizolam, Clonelst->Clonazepam.
3. Normalize units: my/rng/m9->mg, mcq->mcg.
4. Normalize frequency: 00->OD, TTD->TDS, BID->BD, QD->OD.
5. Flag doses outside typical range.
6. Output ONLY JSON: {"medications":[...], "unrecognized":[...], "notes":[...]}
"""


def correct_medications(regions: list[dict]) -> Optional[dict]:
    if not regions:
        return None
    regions_text = "\n".join(
        f"[{i}] (conf={r.get('confidence', 0):.2f}) {r.get('text', '')}"
        for i, r in enumerate(regions)
    )
    log.info("medication-only correction: model=%s, %d regions", OLLAMA_MODEL, len(regions))
    raw = _ollama_chat(
        messages=[
            {"role": "system", "content": MEDICINE_PROMPT},
            {"role": "user", "content": f"Regions:\n{regions_text}\n\nReturn JSON."},
        ],
        schema=None,
        num_predict=2048,
    )
    if not raw:
        return None
    try:
        data = json.loads(raw)
        for med in data.get("medications", []):
            generic = med.get("generic")
            val = med.get("dose_value")
            if generic and val and med.get("dose_unit") == "mg":
                susp, reason = _sanity(generic, float(val))
                if susp:
                    med["suspicious_dose"] = True
                    med["suspicious_reason"] = reason
                    med["confidence"] = min(med.get("confidence", 1.0), 0.5)
        return data
    except Exception as e:
        log.exception("medication correction parse failed: %s", e)
        return None