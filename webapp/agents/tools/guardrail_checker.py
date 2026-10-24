"""
Deterministic Security & Enterprise Procurement Guardrails.
Detects prompt injection attempts and validates budget boundaries.
"""
import re

INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior) instructions",
    r"disregard (all )?(rules|instructions)",
    r"you are now (in|a) ",
    r"system prompt",
    r"jailbreak",
    r"อนุมัติราคา 0",
    r"ลืมคำสั่งเดิม",
    r"ยกเลิกกฎทั้งหมด",
    r"เป็นอิสระ",
    r"hack",
    r"override (rules|budget)",
    # Social engineering / Authority spoofing defense (Mentor feedback)
    # Target explicit authority coercion forcing approval (e.g. ผู้บริหารสั่งมาให้เคาะ, หัวหน้าบอกให้อนุมัติ)
    # Avoid false-positives on benign corporate phrases like "ฝ่ายบริหารได้พิจารณา", "หวังว่าจะได้รับอนุมัติ", "ยินดีตกลง"
    r"(ผู้บริหาร|หัวหน้า|เจ้านาย|บอส|ผอ\.|ceo|cpo)(คุณ|ฝ่ายคุณ|ของคุณ)?\s*(สั่งมา|สั่งให้|สั่งว่า|บอกให้|สั่งการ).{0,25}?(อนุมัติ|เคาะ|ยอมรับ|ผ่าน)",
    r"(ตกลงกับ|คุยกับ).{0,20}?(ผู้บริหาร|หัวหน้า|เจ้านาย|บอส|ฝ่ายบริหาร|จัดซื้อ).{0,20}?(ไว้แล้ว).{0,20}?(ให้อนุมัติ|ให้ผ่าน|ให้ยอมรับ)",
    r"(สั่งให้|บังคับให้).{0,15}?(อนุมัติทันที|ปิดดีลทันที|เคาะเดี๋ยวนี้)",
]

def check_prompt_injection(user_text: str) -> dict:
    lower_text = user_text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower_text):
            return {
                "is_safe": False,
                "reason": "Security Alert: ตรวจพบความพยายามแก้ไขกฎระเบียบจัดซื้อ (Prompt Injection Detected)",
                "matched_pattern": pattern
            }
    return {"is_safe": True, "reason": None}

def verify_procurement_guardrail(proposed_price: float, budget_price: float, lead_time_days: int) -> dict:
    if proposed_price > budget_price * 1.05:
        return {
            "passed": False,
            "error_code": "BUDGET_CEILING_EXCEEDED",
            "message": f"ราคาที่เสนอ ฿{proposed_price:,.2f} เกินเพดานงบประมาณบริษัท ฿{budget_price:,.2f}"
        }
    if lead_time_days > 14:
        return {
            "passed": False,
            "error_code": "SLA_BREACH",
            "message": f"ระยะเวลาส่งมอบ {lead_time_days} วัน เกินเกณฑ์ความปลอดภัย SLA สูงสุด (14 วัน)"
        }
    return {"passed": True, "error_code": None}
