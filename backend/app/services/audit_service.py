from sqlalchemy.orm import Session
from app.models.entities import AuditEvent


def record_event(db: Session, deal_id: str, event_type: str, actor: str, details: dict) -> AuditEvent:
    event = AuditEvent(deal_id=deal_id, event_type=event_type, actor=actor, details=details)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def serialize_event(event: AuditEvent) -> dict:
    return {
        "id": event.id,
        "deal_id": event.deal_id,
        "event_type": event.event_type,
        "actor": event.actor,
        "details": event.details,
        "created_at": event.created_at.isoformat() + "Z",
    }
