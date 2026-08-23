from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Deal, PaymentRecord
from app.schemas.requests import VerifyPaymentRequest
from app.services.audit_service import record_event
from app.services.razorpay_service import create_order, verify_payment_signature

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/order/{deal_id}")
def create_payment_order(deal_id: str, db: Session = Depends(get_db)):
    deal = db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.status != "APPROVED" or deal.approval_status not in {"APPROVED", "AUTO_APPROVED"}:
        record_event(db, deal.id, "PAYMENT_CREATION_BLOCKED", "payment_gate", {
            "reason": "Deal is not approved", "deal_status": deal.status, "approval_status": deal.approval_status,
        })
        raise HTTPException(status_code=403, detail="Deal is not approved. Payment creation blocked.")
    existing = db.scalar(select(PaymentRecord).where(PaymentRecord.deal_id == deal_id))
    if existing and existing.razorpay_order_id:
        return {"success": True, "order": {
            "id": existing.razorpay_order_id, "amount": int(round(existing.amount * 100)),
            "currency": existing.currency, "receipt": deal_id, "status": existing.status,
        }}
    try:
        order = create_order(deal.final_price, deal.id)
    except Exception as exc:
        record_event(db, deal.id, "PAYMENT_PROVIDER_FAILURE", "razorpay", {"error": str(exc)})
        raise HTTPException(status_code=502, detail=f"Razorpay order creation failed: {exc}")
    payment = existing or PaymentRecord(deal_id=deal.id, amount=deal.final_price, currency="INR")
    payment.razorpay_order_id = order["id"]
    payment.status = order.get("status", "created").upper()
    db.add(payment)
    db.commit()
    record_event(db, deal.id, "RAZORPAY_ORDER_CREATED", "razorpay", {
        "order_id": order["id"], "amount_paise": order["amount"], "currency": order["currency"],
    })
    return {"success": True, "order": {
        "id": order["id"], "amount": order["amount"], "currency": order["currency"],
        "receipt": order.get("receipt"), "status": order.get("status"),
    }}


@router.post("/verify")
def verify_payment(request: VerifyPaymentRequest, db: Session = Depends(get_db)):
    payment = db.scalar(select(PaymentRecord).where(PaymentRecord.razorpay_order_id == request.razorpay_order_id))
    if not payment:
        raise HTTPException(status_code=404, detail="Unknown Razorpay order")
    try:
        verify_payment_signature(request.razorpay_order_id, request.razorpay_payment_id, request.razorpay_signature)
    except Exception:
        record_event(db, payment.deal_id, "PAYMENT_SIGNATURE_REJECTED", "payment_gate", {"order_id": request.razorpay_order_id})
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    payment.razorpay_payment_id = request.razorpay_payment_id
    payment.status = "VERIFIED"
    deal = db.get(Deal, payment.deal_id)
    deal.status = "PAID"
    db.commit()
    record_event(db, deal.id, "PAYMENT_VERIFIED", "payment_gate", {
        "order_id": request.razorpay_order_id, "payment_id": request.razorpay_payment_id,
    })
    return {"success": True, "verified": True, "deal_id": deal.id, "status": deal.status}
