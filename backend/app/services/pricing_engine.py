def calculate_deal(unit_price: float, unit_cost: float, quantity: int, discount_pct: float = 0.0) -> dict:
    gross_revenue = unit_price * quantity
    discount_amount = gross_revenue * discount_pct / 100.0
    final_price = gross_revenue - discount_amount
    total_cost = unit_cost * quantity
    profit = final_price - total_cost
    margin_pct = (profit / final_price * 100.0) if final_price > 0 else 0.0
    return {
        "gross_revenue": round(gross_revenue, 2),
        "discount_amount": round(discount_amount, 2),
        "final_price": round(final_price, 2),
        "total_cost": round(total_cost, 2),
        "profit": round(profit, 2),
        "margin_pct": round(margin_pct, 2),
    }
