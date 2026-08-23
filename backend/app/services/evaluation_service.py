import random
from sqlalchemy.orm import Session
from app.services.deal_engine import find_best_offer


def run_evaluation(db: Session, scenarios: int = 500, seed: int = 42) -> dict:
    rng = random.Random(seed)
    baseline_revenue = 0.0
    baseline_profit = 0.0
    baseline_conversions = 0
    dg_revenue = 0.0
    dg_profit = 0.0
    dg_conversions = 0
    policy_violations = 0
    recovered = 0

    # Static baseline: Standard Gift Box at list price, no add-ons, no negotiation.
    baseline_unit_price = 649
    baseline_unit_cost = 470

    for _ in range(scenarios):
        quantity = rng.randint(10, 70)
        list_total = baseline_unit_price * quantity
        budget_factor = rng.uniform(0.78, 1.20)
        budget = round(list_total * budget_factor, 2)
        hard = ["corporate", "vegetarian"] if rng.random() < 0.55 else ["corporate"]
        soft = ["premium"] if rng.random() < 0.55 else []

        if list_total <= budget:
            baseline_conversions += 1
            baseline_revenue += list_total
            baseline_profit += (baseline_unit_price - baseline_unit_cost) * quantity

        candidate = find_best_offer(
            db,
            category="gift",
            quantity=quantity,
            buyer_budget=budget,
            hard_constraints=hard,
            soft_preferences=soft,
        )
        if candidate and rng.random() <= candidate["acceptance_probability"]:
            dg_conversions += 1
            dg_revenue += candidate["final_price"]
            dg_profit += candidate["profit"]
            if list_total > budget:
                recovered += 1
            if candidate["policy"]["status"] == "BLOCKED":
                policy_violations += 1

    def pct(value):
        return round(value * 100.0 / scenarios, 2)

    revenue_uplift = ((dg_revenue - baseline_revenue) / baseline_revenue * 100.0) if baseline_revenue else 0.0
    return {
        "scenarios": scenarios,
        "seed": seed,
        "baseline": {
            "conversions": baseline_conversions,
            "conversion_rate_pct": pct(baseline_conversions),
            "revenue": round(baseline_revenue, 2),
            "profit": round(baseline_profit, 2),
        },
        "dealguard": {
            "conversions": dg_conversions,
            "conversion_rate_pct": pct(dg_conversions),
            "revenue": round(dg_revenue, 2),
            "profit": round(dg_profit, 2),
            "recovered_deals": recovered,
            "policy_violations_executed": policy_violations,
        },
        "revenue_uplift_pct": round(revenue_uplift, 2),
        "conversion_uplift_points": round(pct(dg_conversions) - pct(baseline_conversions), 2),
        "methodology_note": "Synthetic seeded simulation. Results are demo evidence, not production claims.",
    }
