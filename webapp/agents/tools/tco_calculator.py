"""
Deterministic TCO & Financial Savings Calculator Tool.
Calculates unit price variance, Net Present Value of extended credit terms,
and annual savings using corporate WACC (7% p.a.).
"""

def calculate_tco(budget_price: float, target_price: float, offered_price: float,
                  standard_credit: int, offered_credit: int, annual_quantity: int,
                  wacc_rate: float = 0.07) -> dict:
    
    price_gap = offered_price - target_price
    initial_budget_total = budget_price * annual_quantity
    offered_total = offered_price * annual_quantity
    
    # Financial credit gain formula: Price * (Delta Days / 365) * WACC
    delta_credit_days = offered_credit - standard_credit
    credit_benefit_per_unit = offered_price * (delta_credit_days / 365.0) * wacc_rate
    effective_tco_price = offered_price - credit_benefit_per_unit
    
    total_savings_thb = initial_budget_total - (effective_tco_price * annual_quantity)
    savings_pct = (total_savings_thb / initial_budget_total) * 100.0 if initial_budget_total else 0.0
    
    return {
        "budget_price": budget_price,
        "target_price": target_price,
        "offered_price": offered_price,
        "price_gap_per_unit": round(price_gap, 2),
        "standard_credit_days": standard_credit,
        "offered_credit_days": offered_credit,
        "delta_credit_days": delta_credit_days,
        "credit_benefit_per_unit": round(credit_benefit_per_unit, 2),
        "effective_tco_price": round(effective_tco_price, 2),
        "total_savings_thb": round(total_savings_thb, 2),
        "savings_pct": round(savings_pct, 1),
        "is_within_budget": offered_price <= budget_price,
        "is_target_met": price_gap <= 0
    }
