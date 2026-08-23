import hashlib
import hmac
import json
import razorpay
from app.core.config import settings


def _client():
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise RuntimeError("Razorpay test credentials are not configured in .env")
    return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


def create_order(amount_rupees: float, deal_id: str) -> dict:
    amount_paise = int(round(amount_rupees * 100))
    return _client().order.create(data={
        "amount": amount_paise,
        "currency": "INR",
        "receipt": deal_id,
        "notes": {"deal_id": deal_id},
    })


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> None:
    _client().utility.verify_payment_signature({
        "razorpay_order_id": order_id,
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature,
    })


def verify_webhook_signature(raw_body: bytes, signature: str) -> bool:
    if not settings.razorpay_webhook_secret:
        raise RuntimeError("RAZORPAY_WEBHOOK_SECRET is not configured")
    expected = hmac.new(settings.razorpay_webhook_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
