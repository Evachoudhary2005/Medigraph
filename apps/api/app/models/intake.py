from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class IntakeSession(Base):
    __tablename__ = "intake_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    questionnaire_id: Mapped[str] = mapped_column(String(32))
    language: Mapped[str] = mapped_column(String(8), default="en")
    status: Mapped[str] = mapped_column(String(16), default="in_progress")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    answers: Mapped[list["IntakeAnswer"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

class IntakeAnswer(Base):
    __tablename__ = "intake_answers"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_session_question"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("intake_sessions.id"), index=True)
    question_id: Mapped[str] = mapped_column(String(64))
    value_json: Mapped[str] = mapped_column(Text)          # JSON-encoded answer
    source: Mapped[str] = mapped_column(String(16), default="touch")   # touch | voice
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session: Mapped[IntakeSession] = relationship(back_populates="answers")