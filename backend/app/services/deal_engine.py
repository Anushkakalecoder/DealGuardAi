import itertools
import math
import random
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Deal, MerchantPolicy, Product
from app.services.ai_service import ai_service
from app.services.audit_service import record_event
from app.services.deal_proof import generate_deal_proof
from app.services.policy_engine import verify_deal
from app.services.pricing_engine import calculate_deal


def _policy(db: Session) -> MerchantPolicy:
    policy = db.get(MerchantPolicy, 1)
    if not policy:
        policy = MerchantPolicy(id=1)
        db.add(policy)
        db.commit()
        db.refresh(policy)
    return policy


def _products(db: Session, category: str, quantity: int) -> list[Product]:
    return list(db.scalars(select(Product).where(Product.category == category, Product.is_addon.is_(False), Product.inventory >= quantity)).all())


def _addons(db: Session, product_sku: str, quantity: int) -> list[Product]:
    items = list(db.scalars(select(Product).where(Product.is_addon.is_(True), Product.inventory >= quantity)).all())
    return [item for item in items if product_sku in (item.compatible_with or [])]


def _constraint_product_ok(product: Product, hard_constraints: list[str]) -> bool:
    tags = {t.lower() for t in (product.tags or [])}
    for constraint in hard_constraints:
        c = constraint.lower()
        if c in {"corporate", "vegetarian", "premium"} and c not in tags:
            return False
    return True


def _preference_score(product: Product, addons: list[Product], soft_preferences: list[str]) -> float:
    if not soft_preferences:
        return 1.0
    tags = {t.lower() for t in (product.tags or [])}
    for addon in addons:
        tags.update(t.lower() for t in (addon.tags or []))
    hits = sum(1 for pref in soft_preferences if any(token in tags for token in pref.lower().replace("_", " ").split()))
    return hits / len(soft_preferences)


def estimate_acceptance_probability(offer_price: float, buyer_budget: float, preference_score: float,
                                    buyer_counteroffer: float | None = None) -> float:
    if offer_price > buyer_budget:
        return 0.0
    anchor = buyer_counteroffer if buyer_counteroffer and buyer_counteroffer > 0 else buyer_budget * 0.86
    if offer_price <= anchor:
        price_prob = 0.94
    else:
        span = max(buyer_budget - anchor, 1.0)
        price_prob = 0.94 - 0.58 * ((offer_price - anchor) / span)
    probability = price_prob * (0.88 + 0.12 * preference_score)
    return round(max(0.20, min(probability, 0.97)), 3)


def _candidate_payload(product: Product, addon_items: list[Product], quantity: int, discount_pct: float,
                       buyer_budget: float, policy: MerchantPolicy, soft_preferences: list[str],
                       buyer_counteroffer: float | None) -> dict | None:
    main = calculate_deal(product.price, product.cost, quantity, discount_pct)
    addon_revenue = sum(a.price * quantity for a in addon_items)
    addon_cost = sum(a.cost * quantity for a in addon_items)
    final_price = round(main["final_price"] + addon_revenue, 2)
    total_cost = round(main["total_cost"] + addon_cost, 2)
    profit = round(final_price - total_cost, 2)
    margin_pct = round((profit / final_price * 100.0) if final_price else 0.0, 2)
    policy_result = verify_deal(
        final_price=final_price,
        margin_pct=margin_pct,
        discount_pct=discount_pct,
        quantity=quantity,
        inventory=product.inventory,
        buyer_budget=buyer_budget,
        minimum_margin_pct=policy.minimum_margin_pct,
        maximum_discount_pct=policy.maximum_discount_pct,
        auto_approval_limit=policy.auto_approval_limit,
        max_order_value=policy.max_order_value,
    )
    if policy_result["status"] == "BLOCKED":
        return None
    pref_score = _preference_score(product, addon_items, soft_preferences)
    acceptance = estimate_acceptance_probability(final_price, buyer_budget, pref_score, buyer_counteroffer)
    expected_value = round(profit * acceptance, 2)
    return {
        "product": product,
        "addons": addon_items,
        "discount_pct": float(discount_pct),
        "gross_price": round(main["gross_revenue"] + addon_revenue, 2),
        "final_price": final_price,
        "total_cost": total_cost,
        "profit": profit,
        "margin_pct": margin_pct,
        "acceptance_probability": acceptance,
        "expected_merchant_value": expected_value,
        "preference_score": round(pref_score, 3),
        "policy": policy_result,
    }


def find_best_offer(db: Session, *, category: str, quantity: int, buyer_budget: float,
                    hard_constraints: list[str], soft_preferences: list[str],
                    buyer_counteroffer: float | None = None) -> dict | None:
    policy = _policy(db)
    candidates: list[dict] = []
    for product in _products(db, category, quantity):
        if not _constraint_product_ok(product, hard_constraints):
            continue
        compatible = _addons(db, product.sku, quantity)
        addon_combos = [[]]
        for size in range(1, min(2, len(compatible)) + 1):
            addon_combos.extend([list(c) for c in itertools.combinations(compatible, size)])
        for discount in range(0, int(math.floor(policy.maximum_discount_pct)) + 1):
            for combo in addon_combos:
                candidate = _candidate_payload(product, combo, quantity, discount, buyer_budget, policy,
                                               soft_preferences, buyer_counteroffer)
                if candidate:
                    candidates.append(candidate)
    if not candidates:
        return None
    # Primary objective: expected merchant value. Ties favor profit, then preference satisfaction.
    return max(candidates, key=lambda x: (x["expected_merchant_value"], x["profit"], x["preference_score"]))


def _persist_offer(db: Session, intent: dict, buyer_message: str, candidate: dict, round_number: int,
                   deal_id: str | None = None) -> Deal:
    deal_id = deal_id or f"DLG-{uuid.uuid4().hex[:10].upper()}"
    proof = generate_deal_proof(
        deal_id,
        candidate["policy"],
        buyer_budget=intent["max_budget"],
        final_price=candidate["final_price"],
        product_sku=candidate["product"].sku,
        quantity=intent["quantity"],
        discount_pct=candidate["discount_pct"],
        margin_pct=candidate["margin_pct"],
    )
    approval_status = "PENDING" if proof["requires_approval"] else "AUTO_APPROVED"
    status = "REQUIRES_APPROVAL" if proof["requires_approval"] else "APPROVED"
    deal = db.get(Deal, deal_id)
    if not deal:
        deal = Deal(id=deal_id)
        db.add(deal)
    deal.status = status
    deal.buyer_message = buyer_message
    deal.category = intent["category"]
    deal.quantity = intent["quantity"]
    deal.buyer_budget = intent["max_budget"]
    deal.hard_constraints = intent["hard_constraints"]
    deal.soft_preferences = intent["soft_preferences"]
    deal.product_sku = candidate["product"].sku
    deal.addons = [{"sku": a.sku, "name": a.name, "unit_price": a.price, "quantity": intent["quantity"]} for a in candidate["addons"]]
    deal.discount_pct = candidate["discount_pct"]
    deal.gross_price = candidate["gross_price"]
    deal.final_price = candidate["final_price"]
    deal.total_cost = candidate["total_cost"]
    deal.profit = candidate["profit"]
    deal.margin_pct = candidate["margin_pct"]
    deal.acceptance_probability = candidate["acceptance_probability"]
    deal.expected_merchant_value = candidate["expected_merchant_value"]
    deal.requires_approval = proof["requires_approval"]
    deal.approval_status = approval_status
    deal.proof = proof
    deal.round_number = round_number
    db.commit()
    db.refresh(deal)
    return deal


def start_deal(db: Session, message: str) -> Deal:
    intent = ai_service.parse_intent(message)
    candidate = find_best_offer(db, category=intent["category"], quantity=intent["quantity"], buyer_budget=intent["max_budget"], hard_constraints=intent["hard_constraints"], soft_preferences=intent["soft_preferences"])
    if not candidate:
        raise ValueError("No policy-compliant deal can satisfy this buyer mandate.")
    deal = _persist_offer(db, intent, message, candidate, round_number=1)
    record_event(db, deal.id, "BUYER_INTENT_PARSED", "buyer_agent", intent)
    record_event(db, deal.id, "OFFER_OPTIMIZED", "deal_optimizer", {
        "product_sku": deal.product_sku, "addons": deal.addons, "final_price": deal.final_price,
        "profit": deal.profit, "margin_pct": deal.margin_pct,
        "expected_merchant_value": deal.expected_merchant_value,
    })
    record_event(db, deal.id, "DEAL_PROOF_GENERATED", "policy_engine", deal.proof)
    context = {
        "suggested_action": "PROPOSE",
        "deterministic_reason": "Highest expected merchant value among policy-compliant offers within the buyer mandate.",
        "fallback_message": f"I can offer {deal.quantity} × {deal.product_sku} for INR {deal.final_price:.0f}.",
        "verified_offer": serialize_deal(deal),
    }
    try:
        strategy = ai_service.explain_strategy(context)
        deal.ai_explanation = strategy["buyer_facing_message"]
        db.commit()
        record_event(db, deal.id, "AI_EXPLANATION_GENERATED", "merchant_agent", strategy)
    except Exception as exc:
        deal.ai_explanation = context["fallback_message"]
        db.commit()
        record_event(db, deal.id, "AI_FALLBACK_USED", "system", {"reason": str(exc)})
    return deal


def counter_deal(db: Session, deal: Deal, buyer_counteroffer: float) -> Deal:
    if buyer_counteroffer <= 0 or buyer_counteroffer > deal.buyer_budget:
        raise ValueError("Counteroffer must be greater than zero and no higher than the buyer's declared maximum budget.")
    intent = {
        "category": deal.category,
        "quantity": deal.quantity,
        "max_budget": deal.buyer_budget,
        "hard_constraints": deal.hard_constraints,
        "soft_preferences": deal.soft_preferences,
    }
    record_event(db, deal.id, "BUYER_COUNTEROFFER", "buyer_agent", {"amount": buyer_counteroffer})
    candidate = find_best_offer(db, category=deal.category, quantity=deal.quantity, buyer_budget=deal.buyer_budget,
                                hard_constraints=deal.hard_constraints, soft_preferences=deal.soft_preferences,
                                buyer_counteroffer=buyer_counteroffer)
    if not candidate:
        record_event(db, deal.id, "COUNTEROFFER_REJECTED", "policy_engine", {"reason": "No compliant alternative exists."})
        raise ValueError("No policy-compliant counteroffer is possible.")
    deal = _persist_offer(db, intent, deal.buyer_message, candidate, round_number=deal.round_number + 1, deal_id=deal.id)
    action = "ACCEPT" if deal.final_price <= buyer_counteroffer else "COUNTER"
    context = {
        "suggested_action": action,
        "deterministic_reason": "The optimizer selected the compliant offer with the highest expected merchant value.",
        "fallback_message": (
            f"I can accept at INR {deal.final_price:.0f}." if action == "ACCEPT"
            else f"I cannot accept INR {buyer_counteroffer:.0f}, but I can offer INR {deal.final_price:.0f}."
        ),
        "buyer_counteroffer": buyer_counteroffer,
        "verified_offer": serialize_deal(deal),
    }
    try:
        strategy = ai_service.explain_strategy(context)
        deal.ai_explanation = strategy["buyer_facing_message"]
        db.commit()
        record_event(db, deal.id, "AI_NEGOTIATION_MESSAGE", "merchant_agent", strategy)
    except Exception as exc:
        deal.ai_explanation = context["fallback_message"]
        db.commit()
        record_event(db, deal.id, "AI_FALLBACK_USED", "system", {"reason": str(exc)})
    record_event(db, deal.id, "DEAL_PROOF_GENERATED", "policy_engine", deal.proof)
    return deal


def demonstrate_block_and_repair(db: Session, deal: Deal, requested_discount_pct: float) -> dict:
    policy = _policy(db)
    if requested_discount_pct <= policy.maximum_discount_pct:
        return {"blocked": False, "message": "Requested discount is within policy."}
    blocked = {
        "rule": "MAX_DISCOUNT",
        "requested_discount_pct": requested_discount_pct,
        "maximum_discount_pct": policy.maximum_discount_pct,
        "action": "BLOCKED",
        "money_action_executed": False,
    }
    record_event(db, deal.id, "UNSAFE_ACTION_BLOCKED", "policy_engine", blocked)
    repaired = counter_deal(db, deal, max(1.0, deal.buyer_budget * 0.86))
    repair = {
        "deal_id": repaired.id,
        "final_price": repaired.final_price,
        "discount_pct": repaired.discount_pct,
        "margin_pct": repaired.margin_pct,
        "status": repaired.status,
    }
    record_event(db, deal.id, "SAFE_ALTERNATIVE_GENERATED", "deal_optimizer", repair)
    return {"blocked": True, "blocked_action": blocked, "repaired_offer": repair}


def serialize_deal(deal: Deal) -> dict:
    return {
        "id": deal.id,
        "status": deal.status,
        "buyer_message": deal.buyer_message,
        "category": deal.category,
        "quantity": deal.quantity,
        "buyer_budget": deal.buyer_budget,
        "hard_constraints": deal.hard_constraints,
        "soft_preferences": deal.soft_preferences,
        "product_sku": deal.product_sku,
        "addons": deal.addons,
        "discount_pct": deal.discount_pct,
        "gross_price": deal.gross_price,
        "final_price": deal.final_price,
        "total_cost": deal.total_cost,
        "profit": deal.profit,
        "margin_pct": deal.margin_pct,
        "acceptance_probability": deal.acceptance_probability,
        "expected_merchant_value": deal.expected_merchant_value,
        "requires_approval": deal.requires_approval,
        "approval_status": deal.approval_status,
        "proof": deal.proof,
        "ai_explanation": deal.ai_explanation,
        "round_number": deal.round_number,
        "created_at": deal.created_at.isoformat() + "Z" if deal.created_at else None,
        "updated_at": deal.updated_at.isoformat() + "Z" if deal.updated_at else None,
    }
