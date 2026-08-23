import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Deal, PaymentRecord
from app.services.audit_service import record_event
from app.services.razorpay_service import verify_webhook_signature

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    raw = await request.body()
    signature = request.headers.get("x-razorpay-signature", "")
    try:
        if not verify_webhook_signature(raw, signature):
            raise ValueError("signature mismatch")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    payload = json.loads(raw.decode("utf-8"))
    event = payload.get("event", "unknown")
    webhook_payload = payload.get("payload") or {}
    payment_entity = ((webhook_payload.get("payment") or {}).get("entity") or {})
    order_entity = ((webhook_payload.get("order") or {}).get("entity") or {})
    order_id = payment_entity.get("order_id") or order_entity.get("id")
    if order_id:
        payment = db.scalar(select(PaymentRecord).where(PaymentRecord.razorpay_order_id == order_id))
        if payment:
            if event in {"payment.captured", "order.paid"}:
                payment.status = "CAPTURED"
                payment.razorpay_payment_id = payment_entity.get("id") or payment.razorpay_payment_id
                deal = db.get(Deal, payment.deal_id)
                deal.status = "PAID"
                db.commit()
                record_event(db, deal.id, "WEBHOOK_PAYMENT_CAPTURED", "razorpay", {"event": event, "order_id": order_id})
            elif event == "payment.failed":
                payment.status = "FAILED"
                db.commit()
                record_event(db, payment.deal_id, "WEBHOOK_PAYMENT_FAILED", "razorpay", {
                    "event": event, "order_id": order_id, "recovery": "Deal retained; buyer may retry payment.",
                })
    return {"ok": True}
