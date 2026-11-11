"""Typed state for the MediGraph clinical pipeline.

This is passed between nodes in the state graph. Every node returns a partial
update; LangGraph merges it into the running state.
"""
from __future__ import annotations

from typing import Any, TypedDict


class PipelineState(TypedDict, total=False):
    # --- inputs ---
    patient_id: str
    document_id: str | None
    actor: str

    # --- intermediate results ---
    ocr_regions: list[dict]
    ocr_text: str
    document_type: str
    verified: dict | None           # AI verification JSON
    facts: list[dict]               # extracted clinical facts
    timeline_count: int
    summary: dict | None            # built draft
    narrative: str | None           # AI-generated clinical narrative
    draft_id: str | None
    draft_version: int | None
    alerts: list[dict]
    bundle: dict | None             # FHIR bundle
    validation: dict | None         # FHIR validation report

    # --- control flow ---
    confidence: float
    needs_review: bool
    human_approved: bool
    retries: int
    stage: str                      # last completed stage
    errors: list[str]
    log: list[str]