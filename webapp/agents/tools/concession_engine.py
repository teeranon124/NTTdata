"""
Game Theory & Multi-Attribute Concession Engine.
Implements Nash Bargaining, Anchoring Buffer, and Concession Ladders based on supplier proposal gap.
"""

def evaluate_concessions(price_gap: float, offered_price: float, target_price: float,
                         current_credit: int, annual_quantity: int,
                         wacc_rate: float = 0.07, round_num: int = 1,
                         intent: str = "") -> dict:
    
    # Working capital value of credit extensions
    credit_gain_45d = offered_price * (15 / 365.0) * wacc_rate
    credit_gain_60d = offered_price * (30 / 365.0) * wacc_rate

    # If supplier proposal meets or beats target price (or within 0.5% tolerance) -> Award
    if intent in ("accept_terms", "agree") or price_gap <= 0 or (offered_price > 0 and (offered_price - target_price) <= (target_price * 0.005)):
        return {
            "strategy": "AGREE_AND_AWARD",
            "tactic_label": "[Award PO: บรรลุข้อตกลงสัญญารายปี LTA]",
            "counter_price": min(offered_price, target_price) if offered_price > 0 else target_price,
            "target_credit": max(current_credit, 45),
            "rationale": f"ข้อเสนอราคา ฿{offered_price:,.2f} สอดคล้องกับกรอบสัญญาจัดซื้อ พร้อมออกใบสั่งซื้อ PO ใน SAP"
        }
    
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

    # Round 2+: Nash Equilibrium Concession
    # Move gradually from target towards offered price (giving ~25-35% concession toward vendor)
    if offered_price > target_price:
        step_delta = (offered_price - target_price) * 0.30
        counter_p = round(target_price + step_delta, 2)
        target_c = 45 if current_credit <= 30 else current_credit
        rationale_text = f"พิจารณาข้อเสนอ ฿{offered_price:,.2f} โดยปรับราคาผ่อนปรนเป็น ฿{counter_p:,.2f} เครดิต {target_c} วัน ตามโมเดล Nash Bargaining"
    else:
        counter_p = target_price
        target_c = max(current_credit, 45)
        rationale_text = f"ยื่นข้อเสนอกรอบเป้าหมายสุดท้ายที่ ฿{counter_p:,.2f} ภายใต้สัญญา Blanket Order 1 ปีเต็ม"

    return {
        "strategy": "COUNTER_OFFER_CONVERGENCE",
        "tactic_label": f"[Strategic Counter-Offer: ยื่นราคาปรับปรุง ฿{counter_p:,.2f} เครดิต {target_c} วัน]",
        "counter_price": counter_p,
        "target_credit": target_c,
        "anchor_price": anchor_price,
        "commitment_volume": annual_quantity,
        "rationale": rationale_text
    }
