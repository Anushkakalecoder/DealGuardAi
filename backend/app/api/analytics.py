from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Deal
from app.schemas.requests import EvaluationRequest
from app.services.evaluation_service import run_evaluation

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("")
def analytics(db: Session = Depends(get_db)):
    deals = list(db.scalars(select(Deal)).all())
    paid = [d for d in deals if d.status == "PAID"]
    return {
        "total_deals": len(deals),
        "paid_deals": len(paid),
        "revenue": round(sum(d.final_price for d in paid), 2),
        "profit": round(sum(d.profit for d in paid), 2),
        "average_margin_pct": round(sum(d.margin_pct for d in paid) / len(paid), 2) if paid else 0.0,
        "approval_pending": sum(1 for d in deals if d.approval_status == "PENDING"),
    }


@router.post("/evaluate")
def evaluate(request: EvaluationRequest, db: Session = Depends(get_db)):
    return run_evaluation(db, request.scenarios, request.seed)
