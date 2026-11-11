from datetime import datetime
from typing import Any
from pydantic import BaseModel

class IntakeSessionCreate(BaseModel):
    language: str = "en"

class IntakeAnswerUpsert(BaseModel):
    value: Any
    source: str = "touch"
    confidence: float | None = None

class IntakeAnswerOut(BaseModel):
    question_id: str
    value: Any
    source: str
    confidence: float | None
    updated_at: datetime

class IntakeSessionOut(BaseModel):
    id: str
    patient_id: str
    questionnaire_id: str
    language: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    answers: list[IntakeAnswerOut] = []