from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.deal_engine import find_best_offer

router = APIRouter(tags=["Protocol Bridge"])


class BuyerMandate(BaseModel):
    category: str = "gift"
    quantity: int = Field(gt=0)
    max_budget: float = Field(gt=0)
    hard_constraints: list[str] = Field(default_factory=list)
    soft_preferences: list[str] = Field(default_factory=list)
    confirmation_required_above: float | None = None


@router.get("/.well-known/dealguard.json")
def manifest():
    return {
        "name": "DealGuard AI Merchant Agent",
        "protocol_version": "dealguard-commerce/1.0",
        "capabilities": ["agent_readable_catalog", "quote", "negotiation", "cross_sell", "deal_proof", "approval_gate", "razorpay_test_checkout"],
        "commerce_objects": ["buyer_mandate", "offer", "deal_proof", "authorization"],
        "protocol_positioning": {
            "UAP_ACP": "Normalized intent/catalog/offer objects inspired by interoperable agent-commerce flows.",
            "AP2": "Explicit budget mandate and approval gates model delegated-payment authorization concepts.",
            "x402": "Not used as the payment rail in this build; Razorpay executes payments. The quote layer is rail-agnostic.",
        },
        "note": "This hackathon build is protocol-aware; it does not claim formal ACP/AP2/UAP/x402 certification or full compliance.",
    }


@router.post("/protocol/quote")
def protocol_quote(mandate: BuyerMandate, db: Session = Depends(get_db)):
    candidate = find_best_offer(db, category=mandate.category, quantity=mandate.quantity,
                                buyer_budget=mandate.max_budget, hard_constraints=mandate.hard_constraints,
                                soft_preferences=mandate.soft_preferences)
    if not candidate:
        raise HTTPException(status_code=422, detail="No compliant quote")
    return {
        "offer": {
            "product_sku": candidate["product"].sku,
            "quantity": mandate.quantity,
            "addons": [a.sku for a in candidate["addons"]],
            "amount": candidate["final_price"],
            "currency": "INR",
            "discount_pct": candidate["discount_pct"],
        },
        "merchant_economics": {"profit": candidate["profit"], "margin_pct": candidate["margin_pct"]},
        "authorization": {"status": candidate["policy"]["status"], "requires_approval": candidate["policy"]["requires_approval"]},
        "checks": candidate["policy"]["checks"],
    }
