from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Deal
from app.schemas.requests import ApprovalRequest
from app.services.audit_service import record_event
from app.services.deal_engine import serialize_deal

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("/{deal_id}")
def decide(deal_id: str, request: ApprovalRequest, db: Session = Depends(get_db)):
    deal = db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    decision = request.decision.upper()
    if decision not in {"APPROVED", "REJECTED"}:
        raise HTTPException(status_code=422, detail="Decision must be APPROVED or REJECTED")
    deal.approval_status = decision
    deal.status = "APPROVED" if decision == "APPROVED" else "REJECTED"
    db.commit()
    record_event(db, deal.id, f"HUMAN_{decision}", "merchant", {"decision": decision})
    return {"success": True, "deal": serialize_deal(deal)}
