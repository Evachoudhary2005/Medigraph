"""Append-only audit log."""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditLog

log = logging.getLogger("medigraph.audit")


def record(
    db: Session,
    action: str,
    actor: str = "system",
    patient_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    entry = AuditLog(
        id=str(uuid.uuid4()),
        actor=actor,
        action=action,
        patient_id=patient_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details_json=json.dumps(details or {}, ensure_ascii=False),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    log.info("audit: %s %s patient=%s res=%s/%s",
             actor, action, patient_id, resource_type, resource_id)
    return entry