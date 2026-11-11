from datetime import datetime
from pydantic import BaseModel

class ConsentCreate(BaseModel):
    purpose: str
    granted: bool = True
    notes: str | None = None

class PatientCreate(BaseModel):
    synthetic_id: str
    preferred_language: str = "en"

class PatientOut(BaseModel):
    id: str
    synthetic_id: str
    preferred_language: str
    created_at: datetime
    class Config:
        from_attributes = True