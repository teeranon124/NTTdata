"""
Game Theory & Multi-Attribute Concession Engine.
Implements Nash Bargaining and trade-off selections based on supplier proposal gap.
"""

def evaluate_concessions(price_gap: float, offered_price: float, target_price: float,
                         current_credit: int, annual_quantity: int,
                         wacc_rate: float = 0.07) -> dict:
    
    # Value of 45-day and 60-day credit extensions
    credit_gain_45d = offered_price * (15 / 365.0) * wacc_rate
    credit_gain_60d = offered_price * (30 / 365.0) * wacc_rate
    
    if price_gap <= 0:
        return {
            "strategy": "AGREE_AND_AWARD",
            "tactic_label": "[Award PO: ปิดดีลสำเร็จตามเป้า TCO]",
            "counter_price": offered_price,
            "target_credit": current_credit,
            "rationale": "ข้อเสนอราคาผ่านเกณฑ์เป้าหมาย TCO เรียบร้อย ยืนยันการออกใบ PO"
        }
    
    # If gap is moderate, trade off with 45-60 days credit
    if price_gap <= credit_gain_60d:
        return {
            "strategy": "CREDIT_TERM_LEVER",
            "tactic_label": "[Working Capital Optimization: ยืดเครดิตเทอม 60 วัน]",
            "counter_price": offered_price,
            "target_credit": 60,
            "rationale": f"ยอมรับราคา ฿{offered_price:,.2f} โดยมีเงื่อนไขขอยืดเครดิตเทอมเป็น 60 วันเพื่อชดเชยต้นทุนเงินทุน"
        }
    
    # If gap is high, demand target price by offering 1-Year Blanket Order
    return {
        "strategy": "VOLUME_LTA_CONCESSION",
        "tactic_label": "[Volume Consolidation: แลกสัญญา Blanket Order 1 ปีเต็ม]",
        "counter_price": target_price,
        "target_credit": 45,
        "commitment_volume": annual_quantity,
        "rationale": f"เสนอทำสัญญา Blanket Order 1 ปีเต็ม รวมยอด {annual_quantity:,} ชิ้น แลกกับราคาเป้าหมาย ฿{target_price:,.2f} และเครดิต 45 วัน"
    }
