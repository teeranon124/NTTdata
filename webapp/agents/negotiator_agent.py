import os
from .bedrock_client import bedrock_client
from .tools import calculate_tco, evaluate_concessions, check_prompt_injection, verify_procurement_guardrail

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")

def run_negotiation_turn(deal_data: dict, vendor_name: str, user_message: str, history: list, parsed_entities: dict) -> dict:
    """
    Main Enterprise Negotiator Agent Loop.
    Executes Guardrail -> TCO Calculation -> Concession Recommendation -> Nova Pro Synthesis.
    """
    audit_trace = []
    
    # Step 1: Security Guardrail Check (Anti-Injection)
    security = check_prompt_injection(user_message)
    if not security["is_safe"]:
        return {
            "reply": "ขออภัยครับ ระบบ AutoProcure.AI ไม่อนุญาตให้แก้ไขหรือแทรกแซงกฎระเบียบการจัดซื้อกลาง หากท่านประสงค์จะเสนอราคาหรือเงื่อนไขทางการค้า กรุณาระบุรายละเอียดสินค้าและราคาตามขั้นตอนปกติครับ [Procurement Security Compliance]",
            "tactic": "[Security Alert: Prompt Injection Blocked]",
            "audit_trace": [{
                "step": 1,
                "agent": "Security Guardrail Agent",
                "thought": "ตรวจพบรูปแบบข้อความไม่พึงประสงค์ (Prompt Injection) จึงระงับการต่อรอง",
                "tool_call": f"check_prompt_injection() -> BLOCKED"
            }]
        }

    # Step 2: Entity Routing Trace
    audit_trace.append({
        "step": 1,
        "agent": f"Router Agent ({parsed_entities.get('source', 'Nova Lite')})",
        "thought": f"สกัดความประสงค์คู่ค้า: {parsed_entities.get('intent')} | ราคาเสนอ: {parsed_entities.get('proposed_unit_price')} | เครดิต: {parsed_entities.get('proposed_credit_days')} วัน",
        "tool_call": f"parse_supplier_intent() -> intent={parsed_entities.get('intent')}"
    })

    # Step 3: TCO & Concession Math
    budget_price = deal_data["budget_unit_price"]
    target_price = deal_data["target_unit_price"]
    annual_qty = deal_data["total_quantity"]
    std_credit = deal_data["standard_credit_days"]
    
    offered_price = parsed_entities.get("proposed_unit_price") or budget_price
    offered_credit = parsed_entities.get("proposed_credit_days") or std_credit

    # Run TCO Tool
    tco_res = calculate_tco(
        budget_price=budget_price,
        target_price=target_price,
        offered_price=offered_price,
        standard_credit=std_credit,
        offered_credit=offered_credit,
        annual_quantity=annual_qty
    )
    
    audit_trace.append({
        "step": 2,
        "agent": "TCO Calculation Engine",
        "thought": f"ส่วนต่างราคาต่อหน่วย: ฿{tco_res['price_gap_per_unit']:+,.2f} | ผลประโยชน์เครดิต: ฿{tco_res['credit_benefit_per_unit']:,.2f} | ประหยัดสุทธิ TCO: ฿{tco_res['total_savings_thb']:,.2f} ({tco_res['savings_pct']}%)",
        "tool_call": f"calculate_tco(price={offered_price}, credit={offered_credit}) -> Effective: ฿{tco_res['effective_tco_price']}"
    })

    # Run Concession Engine Tool (Game Theory)
    concession = evaluate_concessions(
        price_gap=tco_res["price_gap_per_unit"],
        offered_price=offered_price,
        target_price=target_price,
        current_credit=offered_credit,
        annual_quantity=annual_qty
    )
    
    audit_trace.append({
        "step": 3,
        "agent": "Game Theory Concession Engine (Nash Bargaining)",
        "thought": f"เลือกยุทธวิธี: {concession['strategy']} | {concession['rationale']}",
        "tool_call": f"evaluate_concessions(gap={tco_res['price_gap_per_unit']}) -> Strategy: {concession['strategy']}"
    })

    # Step 4: Amazon Nova Pro Synthesis
    policy_prompt = open(os.path.join(PROMPTS_DIR, "negotiator_policy.md"), "r", encoding="utf-8").read()
    
    deal_context = f"""
CURRENT NEGOTIATION CONTEXT:
- Part Name: {deal_data['name']} ({deal_data['part_code']})
- Category: {deal_data['category']}
- Annual Demand: {annual_qty:,} units (Consolidated across {len(deal_data['plants'])} plants)
- Budget Ceiling Price: ฿{budget_price:,.2f} / unit
- Target Price: ฿{target_price:,.2f} / unit
- Supplier Name: {vendor_name}
- Supplier Proposed Price: ฿{offered_price:,.2f} / unit
- Supplier Proposed Credit: {offered_credit} days
- TCO Calculation Status: Gap is ฿{tco_res['price_gap_per_unit']:+,.2f} / unit
- Game Theory Recommended Strategy: {concession['strategy']} ({concession['rationale']})
"""

    system_text = policy_prompt + "\n" + deal_context
    
    res = bedrock_client.invoke_converse(
        model_id=bedrock_client.negotiator_model,
        system_text=system_text,
        messages=history + [{"sender": "vendor", "text": user_message}],
        temperature=0.3
    )
    
    if res.get("status") == "live_aws" and res.get("text"):
        reply_text = res["text"].strip()
        audit_trace.append({
            "step": 4,
            "agent": f"Strategic Synthesis ({bedrock_client.negotiator_model})",
            "thought": f"สร้างข้อความโต้ตอบทางธุรกิจโดยใช้บริบทสัญญารายปีและเครดิตเทอม (Latency: {res['latency_ms']}ms)",
            "tool_call": f"invoke_converse(tokens={res.get('input_tokens', 0)}+{res.get('output_tokens', 0)}) -> SUCCESS"
        })
    else:
        # High-fidelity deterministic fallback
        if concession["strategy"] == "AGREE_AND_AWARD":
            reply_text = f"ขอบคุณทาง {vendor_name} ครับ ข้อเสนอราคา ฿{offered_price:,.2f} เครดิต {offered_credit} วัน ผ่านเกณฑ์การประเมิน TCO ของกลุ่มโรงงานเรียบร้อยแล้ว ทางระบบ AutoProcure.AI ได้สร้าง Draft PO รอผู้บริหารลงนามอนุมัติในระบบ SAP เรียบร้อยครับ {concession['tactic_label']}"
        elif concession["strategy"] == "CREDIT_TERM_LEVER":
            reply_text = f"ทางเราเข้าใจเรื่องข้อจำกัดด้านต้นทุนของ {vendor_name} ครับ หากทางท่านจำเป็นต้องยืนราคาที่ ฿{offered_price:,.2f} ทางโรงงานขอเสนอจุดลงตัวแบบ Win-Win โดยขอยืดระยะเวลาเครดิตเทอมเป็น {concession['target_credit']} วัน พร้อมบริการจัดส่งฟรี DDP เพื่อให้โครงสร้างต้นทุนรวมผ่านเกณฑ์อนุมัติครับ {concession['tactic_label']}"
        else:
            reply_text = f"เรียน {vendor_name} เนื่องจากราคา ฿{offered_price:,.2f} ยังสูงกว่าราคาเป้าหมายในระบบ เพื่อให้เกิดประโยชน์สูงสุดร่วมกัน ทางเครือโรงงานขอเสนอทำสัญญา Blanket Order 1 ปีเต็ม การันตียอดสั่งซื้อรวม {annual_qty:,} ชิ้น แลกกับการปรับลดราคาลงมาที่ ฿{target_price:,.2f} และเครดิต 45 วันครับ หากท่านอนุมัติได้เราพร้อมล็อกให้ท่านเป็นคู่สัญญาหลักทันทีครับ {concession['tactic_label']}"
        
        audit_trace.append({
            "step": 4,
            "agent": "Autonomous Negotiation Engine (Ready for Nova Pro)",
            "thought": f"สร้างข้อความโต้ตอบอัตโนมัติตามกลยุทธ์ {concession['strategy']}",
            "tool_call": "generate_response() -> READY"
        })

    return {
        "reply": reply_text,
        "tactic": concession["tactic_label"],
        "tco_data": tco_res,
        "concession": concession,
        "audit_trace": audit_trace
    }
