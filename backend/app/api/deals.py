from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import AuditEvent, Deal
from app.schemas.requests import CounterOfferRequest, StartDealRequest, UnsafeDiscountRequest
from app.services.audit_service import serialize_event
from app.services.deal_engine import counter_deal, demonstrate_block_and_repair, serialize_deal, start_deal

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.post("/start")
def start(request: StartDealRequest, db: Session = Depends(get_db)):
    try:
        deal = start_deal(db, request.message)
        return {"success": True, "deal": serialize_deal(deal)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/{deal_id}")
def get_deal(deal_id: str, db: Session = Depends(get_db)):
    deal = db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return serialize_deal(deal)


@router.post("/{deal_id}/counter")
def counter(deal_id: str, request: CounterOfferRequest, db: Session = Depends(get_db)):
    deal = db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    try:
        updated = counter_deal(db, deal, request.amount)
        return {"success": True, "deal": serialize_deal(updated)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/{deal_id}/demo-unsafe-discount")
def unsafe_discount(deal_id: str, request: UnsafeDiscountRequest, db: Session = Depends(get_db)):
    deal = db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return demonstrate_block_and_repair(db, deal, request.requested_discount_pct)


@router.get("/{deal_id}/audit")
def audit(deal_id: str, db: Session = Depends(get_db)):
    if not db.get(Deal, deal_id):
        raise HTTPException(status_code=404, detail="Deal not found")
    events = list(db.scalars(select(AuditEvent).where(AuditEvent.deal_id == deal_id).order_by(AuditEvent.id)).all())
    return {"deal_id": deal_id, "events": [serialize_event(e) for e in events]}
