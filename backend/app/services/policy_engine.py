def verify_deal(*, final_price: float, margin_pct: float, discount_pct: float, quantity: int,
                inventory: int, buyer_budget: float, minimum_margin_pct: float,
                maximum_discount_pct: float, auto_approval_limit: float,
                max_order_value: float) -> dict:
    checks = [
        {"rule": "BUYER_BUDGET", "actual": final_price, "limit": buyer_budget,
         "passed": final_price <= buyer_budget, "explanation": "Final price must not exceed the buyer mandate."},
        {"rule": "MIN_MARGIN", "actual": margin_pct, "limit": minimum_margin_pct,
         "passed": margin_pct >= minimum_margin_pct, "explanation": "Merchant minimum margin is protected."},
        {"rule": "MAX_DISCOUNT", "actual": discount_pct, "limit": maximum_discount_pct,
         "passed": discount_pct <= maximum_discount_pct, "explanation": "Discount cannot exceed merchant authority."},
        {"rule": "INVENTORY", "actual": quantity, "limit": inventory,
         "passed": quantity <= inventory, "explanation": "Merchant must have enough inventory."},
        {"rule": "MAX_ORDER_VALUE", "actual": final_price, "limit": max_order_value,
         "passed": final_price <= max_order_value, "explanation": "Order value must be within the merchant safety cap."},
    ]
    all_passed = all(c["passed"] for c in checks)
    if not all_passed:
        status = "BLOCKED"
        requires_approval = False
    elif final_price > auto_approval_limit:
        status = "REQUIRES_APPROVAL"
        requires_approval = True
    else:
        status = "APPROVED"
        requires_approval = False
    return {"status": status, "requires_approval": requires_approval, "checks": checks}
