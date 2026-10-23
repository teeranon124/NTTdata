import json
import os
import re
from .model_gateway import TaskComplexity, model_gateway

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

    # Route to the FAST tier (Nova Lite) via the Dynamic Model Gateway — this is a
    # LIGHT classification/extraction task, so we deliberately avoid the costly model.
    res = model_gateway.invoke(
        task_type="intent",
        system_text=system_prompt,
        messages=[{"sender": "vendor", "text": user_message}],
        temperature=0.0,
        complexity=TaskComplexity.LIGHT,
    )

    if res.get("status") == "live_aws" and res.get("text"):
        try:
            # Extract JSON from model output
            text = res["text"].strip()
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                parsed["source"] = f"Amazon Bedrock ({res.get('model_id')})"
                parsed["latency_ms"] = res["latency_ms"]
                # DEFENSE-IN-DEPTH: the LLM sometimes drops a field (e.g. misses a
                # bare price/credit). Backfill any missing commercial fact from the
                # deterministic regex parser so a single LLM miss never derails the
                # whole pipeline (price=None -> wrong strategy). Regex only FILLS
                # gaps; it never overrides a value the LLM extracted.
                local = _regex_parse(user_message)
                if parsed.get("proposed_unit_price") in (None, "", 0):
                    parsed["proposed_unit_price"] = local["proposed_unit_price"]
                if parsed.get("proposed_credit_days") in (None, "", 0):
                    parsed["proposed_credit_days"] = local["proposed_credit_days"]
                if not parsed.get("intent"):
                    parsed["intent"] = local["intent"]
                # Backfill the richer commercial-terms fields the LLM may omit.
                for k in ("proposed_lead_time_days", "proposed_warranty_months",
                          "proposed_sla_buffer", "proposed_compliance_cert"):
                    if parsed.get(k) in (None, "", 0):
                        parsed[k] = local.get(k)
                if parsed.get("proposed_unit_price") is not None or parsed.get("proposed_credit_days") is not None:
                    parsed["source"] = f"Amazon Bedrock ({res.get('model_id')}) + regex backfill"
                return parsed
        except Exception:
            pass

    # Deterministic local regex fallback (no AWS / LLM failure)
    return _regex_parse(user_message)


def _regex_parse(user_message: str) -> dict:
    """Deterministic extraction of price / credit / intent from Thai+EN chat."""
    extracted_price = _extract_price(user_message)
    _lc = user_message.lower()
    # Prefer "<n> วัน/day"; else accept a number right after the credit keyword
    # (e.g. "เครดิต 45 ตกลง" — no trailing 'วัน'). Day range bounded to 1-180.
    credit_match = re.search(r"(\d{1,3})\s*(?:วัน|day|days)", _lc)
    if not credit_match:
        credit_match = re.search(r"(?:เครดิต|เครดิตเทอม|credit)\s*(?:เทอม\s*)?(\d{1,3})", _lc)
    extracted_credit = None
    if credit_match:
        c = int(credit_match.group(1))
        if 1 <= c <= 180:
            extracted_credit = c

    # Lead time: "ส่ง 7 วัน", "lead time 10 วันทำการ", "จัดส่ง 5 วัน"
    lead_match = re.search(r"(?:ส่ง|จัดส่ง|lead\s*time|ส่งมอบ)\D{0,8}(\d{1,3})\s*(?:วัน|day)", _lc)
    lead_time = int(lead_match.group(1)) if lead_match else None

    # Warranty: "รับประกัน 24 เดือน", "warranty 18 months", "ประกัน 2 ปี"
    warranty_months = None
    wmatch = re.search(r"(?:รับประกัน|ประกัน|warranty)\D{0,6}(\d{1,3})\s*(?:เดือน|month)", _lc)
    if wmatch:
        warranty_months = int(wmatch.group(1))
    else:
        wyear = re.search(r"(?:รับประกัน|ประกัน|warranty)\D{0,6}(\d)\s*(?:ปี|year)", _lc)
        if wyear:
            warranty_months = int(wyear.group(1)) * 12

    # SLA buffer / safety stock: "สำรอง 10%", "buffer stock 15%"
    sla_match = re.search(r"(?:สำรอง|buffer|safety\s*stock)\D{0,8}(\d{1,2})\s*%?", _lc)
    sla_buffer = f"{sla_match.group(1)}%" if sla_match else None

    # Compliance cert mentions (common industrial standards).
    cert_hit = None
    for cert in ["iso 15552", "iso 492", "jis b 1514", "ce/rohs", "rohs", "ce ", "iso 9001", "din"]:
        if cert in _lc:
            cert_hit = cert.upper().strip()
            break

    intent = "counter_offer" if (extracted_price or extracted_credit) else "inquiry"
    if any(w in user_message for w in ["ตกลง", "อนุมัติ", "ยินดีรับ", "รับข้อเสนอ"]):
        intent = "accept_terms"
    elif any(w in user_message for w in ["ไม่ลด", "ไม่ไหว", "ยกเลิก", "แพงไป"]):
        intent = "reject_terms"

    return {
        "intent": intent,
        "proposed_unit_price": extracted_price,
        "proposed_credit_days": extracted_credit,
        "proposed_lead_time_days": lead_time if lead_time is not None else 7,
        "proposed_warranty_months": warranty_months,
        "proposed_sla_buffer": sla_buffer,
        "proposed_compliance_cert": cert_hit,
        "source": "Local Deterministic Parser (Ready for Bedrock Nova Lite)",
        "latency_ms": 1.2
    }
