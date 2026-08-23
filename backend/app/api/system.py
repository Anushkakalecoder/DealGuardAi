from fastapi import APIRouter
from app.core.config import settings
from app.services.ai_service import ai_service

router = APIRouter(tags=["System"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "dealguard-backend", "ai_mode": "groq" if ai_service.enabled else "deterministic-fallback"}


@router.get("/config/public")
def public_config():
    return {
        "razorpay_key_id": settings.razorpay_key_id,
        "groq_model": settings.groq_model,
        "ai_enabled": ai_service.enabled,
        "environment": settings.app_env,
    }
