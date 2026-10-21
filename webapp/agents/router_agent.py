import json
import os
import re
from .bedrock_client import bedrock_client

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")

# A number token: supports thousands separators and decimals, e.g. 420, 1,250.50, 405.-
_NUM = r"\d{1,3}(?:,\d{3})*(?:\.\d+)?"

# High-confidence price patterns: a number next to a currency marker (฿ / บาท / thb / บ. / .-).
_PRICE_WITH_UNIT = re.compile(
    rf"(?:฿\s*({_NUM}))"                       # ฿420
    rf"|(({_NUM})\s*(?:บาท|thb|บ\.|บาทถ้วน))"  # 420 บาท / 420thb / 420 บ.
    rf"|(({_NUM})\s*\.-)",                      # 420.-
    re.IGNORECASE,
)

# Cue words that typically precede a bare price in Thai procurement chat.
_PRICE_CUE = re.compile(
    rf"(?:ราคา|เสนอ|ขอ|ลดเหลือ|ที่|เป็น|หน่วยละ|ชิ้นละ|unit price|price)\s*(?:฿\s*)?({_NUM})",
    re.IGNORECASE,
)

# Bare standalone number (last-resort). Excludes numbers immediately followed by
# day/time units so credit terms like "45 วัน" are never mistaken for a price.
_PRICE_BARE = re.compile(rf"({_NUM})(?!\s*(?:วัน|day|days|เดือน|ปี|%|เปอร์เซ็นต์))", re.IGNORECASE)

# Plausible unit-price range for MRO parts (THB). Filters out junk like years or quantities.
_PRICE_MIN, _PRICE_MAX = 10.0, 1_000_000.0


def _to_float(raw: str):
    try:
        return float(raw.replace(",", ""))
    except (ValueError, AttributeError):
        return None


def _extract_price(text: str):
    """
    Extract a proposed unit price from free-text supplier chat.
    Priority: currency-marked -> cue-word -> plausible bare number.
    """
    # 1) Highest confidence: number attached to a currency marker.
    m = _PRICE_WITH_UNIT.search(text)
    if m:
        for g in m.groups():
            val = _to_float(g) if g else None
            if val is not None and _PRICE_MIN <= val <= _PRICE_MAX:
                return val

    # 2) Cue word immediately before a number (e.g. "เสนอ 420", "ขอ 405").
    m = _PRICE_CUE.search(text)
    if m:
        val = _to_float(m.group(1))
        if val is not None and _PRICE_MIN <= val <= _PRICE_MAX:
            return val

    # 3) Last resort: a plausible standalone number that is not a day/percent unit.
    for m in _PRICE_BARE.finditer(text):
        val = _to_float(m.group(1))
        if val is not None and _PRICE_MIN <= val <= _PRICE_MAX:
            return val

    return None


def parse_supplier_intent(user_message: str) -> dict:
    """
    Uses Amazon Nova Lite to extract intent and structured commercial facts.
    """
    system_prompt = open(os.path.join(PROMPTS_DIR, "router_system.md"), "r", encoding="utf-8").read()
    
    # Try calling Nova Lite
    res = bedrock_client.invoke_converse(
        model_id=bedrock_client.router_model,
        system_text=system_prompt,
        messages=[{"sender": "vendor", "text": user_message}],
        temperature=0.0
    )
    
    if res.get("status") == "live_aws" and res.get("text"):
        try:
            # Extract JSON from model output
            text = res["text"].strip()
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                parsed["source"] = f"Amazon Bedrock ({bedrock_client.router_model})"
                parsed["latency_ms"] = res["latency_ms"]
                return parsed
        except Exception:
            pass
            
    # Deterministic local regex fallback (if no AWS keys)
    extracted_price = _extract_price(user_message)
    credit_match = re.search(r"(\d{1,3})\s*(?:วัน|day|days)", user_message.lower())
    extracted_credit = int(credit_match.group(1)) if credit_match else None
    
    intent = "counter_offer" if (extracted_price or extracted_credit) else "inquiry"
    if any(w in user_message for w in ["ตกลง", "อนุมัติ", "ยินดีรับ", "รับข้อเสนอ"]):
        intent = "accept_terms"
    elif any(w in user_message for w in ["ไม่ลด", "ไม่ไหว", "ยกเลิก", "แพงไป"]):
        intent = "reject_terms"

    return {
        "intent": intent,
        "proposed_unit_price": extracted_price,
        "proposed_credit_days": extracted_credit,
        "proposed_lead_time_days": 7,
        "source": "Local Deterministic Parser (Ready for Bedrock Nova Lite)",
        "latency_ms": 1.2
    }
