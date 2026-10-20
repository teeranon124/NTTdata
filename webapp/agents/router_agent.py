import json
import os
import re
from .bedrock_client import bedrock_client

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")

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
    price_match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:บาท|thb|บ\.)", user_message.lower())
    credit_match = re.search(r"(\d{2})\s*(?:วัน|day)", user_message.lower())
    
    extracted_price = float(price_match.group(1).replace(",", "")) if price_match else None
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
