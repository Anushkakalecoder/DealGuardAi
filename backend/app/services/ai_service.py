import json
import re
from datetime import date, timedelta
from groq import Groq

from app.core.config import settings


INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string"},
        "quantity": {"type": "integer", "minimum": 1},
        "max_budget": {"type": "number", "exclusiveMinimum": 0},
        "hard_constraints": {"type": "array", "items": {"type": "string"}},
        "soft_preferences": {"type": "array", "items": {"type": "string"}},
        "buyer_summary": {"type": "string"},
    },
    "required": ["category", "quantity", "max_budget", "hard_constraints", "soft_preferences", "buyer_summary"],
    "additionalProperties": False,
}

STRATEGY_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["PROPOSE", "COUNTER", "ACCEPT", "REJECT"]},
        "reason": {"type": "string"},
        "buyer_facing_message": {"type": "string"},
    },
    "required": ["action", "reason", "buyer_facing_message"],
    "additionalProperties": False,
}


class AIService:
    def __init__(self):
        self.enabled = bool(settings.groq_api_key)
        self.client = Groq(api_key=settings.groq_api_key) if self.enabled else None

    def _structured(self, system: str, user: str, name: str, schema: dict) -> dict:
        if not self.enabled:
            raise RuntimeError("Groq is not configured")
        response = self.client.chat.completions.create(
            model=settings.groq_model,
            reasoning_effort=settings.groq_reasoning_effort,
            reasoning_format="hidden",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": name, "strict": True, "schema": schema},
            },
        )
        return json.loads(response.choices[0].message.content or "{}")

    def parse_intent(self, message: str) -> dict:
        if self.enabled:
            return self._structured(
                "You convert commerce requests into a strict buyer mandate. Never invent a larger budget or quantity. "
                "Use category 'gift' for corporate gift-box requests. Hard constraints are must-have requirements; "
                "soft preferences are negotiable. Dates may remain as concise natural-language constraints.",
                message,
                "buyer_intent",
                INTENT_SCHEMA,
            )
        return self._fallback_intent(message)

    def _fallback_intent(self, message: str) -> dict:
        lowered = message.lower()
        quantity_match = re.search(r"\b(\d+)\s+(?:corporate\s+)?(?:gift|box|boxes|gifts|units)", lowered)
        budget_match = re.search(r"(?:₹|rs\.?|inr|under|max(?:imum)?(?:\s+budget)?|budget(?:\s+is)?|below)\s*[:=]?\s*₹?\s*([0-9][0-9,]*)", lowered)
        if not budget_match:
            budget_match = re.search(r"₹\s*([0-9][0-9,]*)", message)
        quantity = int(quantity_match.group(1)) if quantity_match else 1
        budget = float(budget_match.group(1).replace(",", "")) if budget_match else 5000.0
        hard = []
        soft = []
        if "friday" in lowered or "delivery" in lowered:
            hard.append("delivery_by_friday" if "friday" in lowered else "delivery_required")
        if "vegetarian" in lowered:
            hard.append("vegetarian")
        if "premium" in lowered:
            soft.append("premium")
        if "corporate" in lowered:
            hard.append("corporate")
        return {
            "category": "gift" if "gift" in lowered or "box" in lowered else "gift",
            "quantity": quantity,
            "max_budget": budget,
            "hard_constraints": hard,
            "soft_preferences": soft,
            "buyer_summary": f"{quantity} units with a maximum budget of INR {budget:.0f}",
        }

    def explain_strategy(self, context: dict) -> dict:
        if not self.enabled:
            return {
                "action": context.get("suggested_action", "PROPOSE"),
                "reason": context.get("deterministic_reason", "Selected by the deterministic deal optimizer."),
                "buyer_facing_message": context.get("fallback_message", "I found a policy-compliant offer for you."),
            }
        return self._structured(
            "You are the merchant-side communication agent in DealGuard. Financial numbers are already verified by code. "
            "Do not change any price, discount, margin, product, quantity, or policy result supplied in the context. "
            "Explain the verified decision concisely and transparently.",
            json.dumps(context),
            "merchant_strategy",
            STRATEGY_SCHEMA,
        )


ai_service = AIService()
