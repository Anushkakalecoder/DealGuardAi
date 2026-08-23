from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import MerchantPolicy
from app.schemas.requests import PolicyUpdateRequest

router = APIRouter(prefix="/merchant", tags=["Merchant"])


def as_dict(p: MerchantPolicy):
    return {
        "minimum_margin_pct": p.minimum_margin_pct,
        "maximum_discount_pct": p.maximum_discount_pct,
        "auto_approval_limit": p.auto_approval_limit,
        "max_order_value": p.max_order_value,
        "currency": p.currency,
    }


@router.get("/policy")
def get_policy(db: Session = Depends(get_db)):
    p = db.get(MerchantPolicy, 1)
    return as_dict(p)


@router.put("/policy")
def update_policy(request: PolicyUpdateRequest, db: Session = Depends(get_db)):
    p = db.get(MerchantPolicy, 1)
    for key, value in request.model_dump().items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return as_dict(p)
