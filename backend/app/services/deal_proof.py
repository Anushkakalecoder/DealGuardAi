import hashlib
import json
from datetime import datetime, timezone


def generate_deal_proof(deal_id: str, policy_result: dict, *, buyer_budget: float,
                        final_price: float, product_sku: str, quantity: int,
                        discount_pct: float, margin_pct: float) -> dict:
    proof = {
        "proof_version": "dealguard-proof/1.0",
        "deal_id": deal_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": policy_result["status"],
        "requires_approval": policy_result["requires_approval"],
        "facts": {
            "product_sku": product_sku,
            "quantity": quantity,
            "buyer_budget": buyer_budget,
            "final_price": final_price,
            "discount_pct": discount_pct,
            "margin_pct": margin_pct,
        },
        "checks": policy_result["checks"],
        "verdict": (
            "Blocked: one or more deterministic policy checks failed."
            if policy_result["status"] == "BLOCKED"
            else "Valid deal; explicit merchant approval is required before payment."
            if policy_result["status"] == "REQUIRES_APPROVAL"
            else "Valid deal and within the merchant's automatic-action threshold."
        ),
    }
    canonical = json.dumps(proof, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    proof["proof_hash_sha256"] = hashlib.sha256(canonical).hexdigest()
    return proof
