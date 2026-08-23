from app.core.database import SessionLocal
from app.services.deal_engine import find_best_offer
from app.services.policy_engine import verify_deal
from app.services.pricing_engine import calculate_deal


def test_pricing_engine():
    r = calculate_deal(649, 470, 50, 8)
    assert r["final_price"] == 29854.0
    assert r["profit"] == 6354.0


def test_policy_blocks_excess_discount():
    p = verify_deal(final_price=25000, margin_pct=20, discount_pct=30, quantity=50, inventory=100,
                    buyer_budget=35000, minimum_margin_pct=18, maximum_discount_pct=10,
                    auto_approval_limit=10000, max_order_value=100000)
    assert p["status"] == "BLOCKED"
    assert any(c["rule"] == "MAX_DISCOUNT" and not c["passed"] for c in p["checks"])


def test_optimizer_returns_compliant_offer():
    with SessionLocal() as db:
        candidate = find_best_offer(db, category="gift", quantity=50, buyer_budget=35000,
                                    hard_constraints=["corporate", "vegetarian"], soft_preferences=["premium"])
        assert candidate is not None
        assert candidate["final_price"] <= 35000
        assert candidate["policy"]["status"] != "BLOCKED"
