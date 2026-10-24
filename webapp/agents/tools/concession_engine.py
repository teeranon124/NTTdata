"""
Game Theory & Multi-Attribute Concession Engine.
Implements Nash Bargaining, Anchoring Buffer, and Concession Ladders based on supplier proposal gap.
"""

def evaluate_concessions(price_gap: float, offered_price: float, target_price: float,
                         current_credit: int, annual_quantity: int,
                         wacc_rate: float = 0.07, round_num: int = 1) -> dict:
    
    # Working capital value of 45-day and 60-day credit extensions
    credit_gain_45d = offered_price * (15 / 365.0) * wacc_rate
    credit_gain_60d = offered_price * (30 / 365.0) * wacc_rate

    # If supplier proposal meets or beats target price (or within 0.5% tolerance) -> Award
    if price_gap <= 0 or (offered_price > 0 and (offered_price - target_price) <= (target_price * 0.005)):
        return {
            "strategy": "AGREE_AND_AWARD",
            "tactic_label": "[Award PO: บรรลุข้อตกลงสัญญารายปี LTA]",
            "counter_price": min(offered_price, target_price) if offered_price > 0 else target_price,
            "target_credit": max(current_credit, 45),
            "rationale": f"ข้อเสนอราคา ฿{offered_price:,.2f} สอดคล้องกับกรอบสัญญาจัดซื้อ พร้อมออกใบสั่งซื้อ PO ใน SAP"
        }
    
    # Anchor pricing: in early turns (Round 1), set anchor buffer ~7% below target price
    # e.g. for target 1,400 -> anchor is ~ 1,302 (rounded to 1,300)
    anchor_discount = 0.07
    anchor_price = round(target_price * (1.0 - anchor_discount), 2)

    # Round 1: Open with aggressive Anchor Price + 60-day credit term demand
    if round_num <= 1:
        return {
            "strategy": "VOLUME_LTA_CONCESSION",
            "tactic_label": "[Anchor Offer: ยื่นข้อเสนอราคาจัดซื้อเริ่มต้น พร้อมเครดิต 60 วัน]",
            "counter_price": anchor_price,
            "target_credit": 60,
            "anchor_price": anchor_price,
            "commitment_volume": annual_quantity,
            "rationale": f"เปิดการเจรจาด้วยราคา Anchor ฿{anchor_price:,.2f} เพื่อสร้างกรอบการต่อรอง พร้อมขอยืดเครดิตเป็น 60 วัน"
        }

    # If gap is moderate and can be offset by working capital (60-day credit)
    if price_gap <= credit_gain_60d:
        return {
            "strategy": "CREDIT_TERM_LEVER",
            "tactic_label": "[Working Capital Optimization: ยืดเครดิตเทอม 60 วัน]",
            "counter_price": offered_price,
            "target_credit": 60,
            "rationale": f"ยอมรับราคา ฿{offered_price:,.2f} โดยมีเงื่อนไขขอยืดเครดิตเทอมเป็น 60 วันเพื่อบริหารเงินทุนหมุนเวียน"
        }

    # Round 2+: Nash Bargaining concession step (Midpoint between anchor and target)
    # Allows gradual movement toward the target instead of abrupt jumping
    step_price = round((anchor_price + target_price) / 2.0, 2)
    if round_num == 2 and offered_price > target_price:
        counter_p = step_price
        target_c = 45
        rationale_text = f"ขยับข้อเสนอเข้าใกล้จุดดุลยภาพที่ ฿{counter_p:,.2f} แลกกับเครดิตเทอม 45 วัน"
    else:
        counter_p = target_price
        target_c = 45
        rationale_text = f"ยื่นข้อเสนอกรอบเป้าหมายสุดท้ายที่ ฿{counter_p:,.2f} ภายใต้สัญญา Blanket Order 1 ปีเต็ม"

    return {
        "strategy": "VOLUME_LTA_CONCESSION",
        "tactic_label": "[Volume Consolidation: แลกสัญญา Blanket Order 1 ปีเต็ม]",
        "counter_price": counter_p,
        "target_credit": target_c,
        "anchor_price": anchor_price,
        "commitment_volume": annual_quantity,
        "rationale": rationale_text
    }
