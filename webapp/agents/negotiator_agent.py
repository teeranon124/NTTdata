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
    budget_price = float(deal_data.get("budget_unit_price") or deal_data.get("pre_price") or 450.0)
    target_price = float(deal_data.get("target_unit_price") or deal_data.get("post_price") or 398.0)
    annual_qty = int(deal_data.get("total_quantity") or deal_data.get("qty") or 1000)
    std_credit = int(deal_data.get("standard_credit_days") or 30)
    plants = deal_data.get("plants") or ["PLANT-CBI-02 (ชลบุรี)", "PLANT-RYG-03 (ระยอง)", "PLANT-AYU-01 (อยุธยา)"]
    part_code = deal_data.get("part_code") or deal_data.get("sku") or str(deal_data.get("id", "")).upper()
    part_name = deal_data.get("name") or f"อะไหล่ MRO {part_code}"
    category_name = deal_data.get("category_th") or deal_data.get("category") or "เครื่องกล & ส่งกำลัง" 
    
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
- Part Name: {deal_data['name']} ({deal_data.get('part_code', deal_data.get('sku', 'NSK-STD'))})
- Category: {deal_data.get('category_th', deal_data.get('category', 'MRO'))}
- Annual Demand: {annual_qty:,} units (Consolidated across {len(deal_data.get('plants', ['ชลบุรี', 'ระยอง', 'อยุธยา']))} plants)
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
            reply_text = (
                f"เรียน {vendor_name}\n\n"
                f"ฝ่ายจัดซื้อกลางขอขอบคุณสำหรับข้อเสนอที่ราคา ฿{offered_price:,.2f} ต่อหน่วย พร้อมเงื่อนไขการชำระเงิน {offered_credit} วัน "
                f"จากการประเมินโครงสร้างต้นทุนรวม (TCO) ของกลุ่มโรงงานทั้ง {len(plants)} แห่ง ข้อเสนอของท่านผ่านเกณฑ์เป้าหมายขององค์กรเรียบร้อยแล้ว\n\n"
                f"ในลำดับถัดไป ระบบ AutoProcure.AI ได้จัดทำร่างใบสั่งซื้อ (Draft PO) เพื่อเสนอผู้บริหารลงนามอนุมัติผ่านระบบ SAP S/4HANA "
                f"และขอเรียนเชิญท่านเป็นคู่สัญญาหลักภายใต้ข้อตกลงระยะยาว (LTA) ประจำปีนี้ครับ {concession['tactic_label']}"
            )
        elif concession["strategy"] == "CREDIT_TERM_LEVER":
            reply_text = (
                f"เรียน {vendor_name}\n\n"
                f"ขอขอบคุณสำหรับข้อเสนอราคา ฿{offered_price:,.2f} ต่อหน่วย ฝ่ายจัดซื้อเข้าใจถึงข้อจำกัดด้านโครงสร้างต้นทุนของท่านเป็นอย่างดี\n\n"
                f"เพื่อให้เกิดจุดลงตัวที่เป็นประโยชน์ร่วมกันของทั้งสองฝ่าย ทางเราขอเรียนเสนอให้คงราคาดังกล่าว โดยขอปรับเงื่อนไขการชำระเงิน (Credit Terms) "
                f"เป็น {concession['target_credit']} วัน พร้อมเงื่อนไขการจัดส่งแบบ DDP โดยไม่มีค่าใช้จ่ายเพิ่มเติม ซึ่งจะช่วยให้โครงสร้างต้นทุนรวม (TCO) "
                f"ผ่านเกณฑ์การอนุมัติขององค์กรได้ครับ {concession['tactic_label']}"
            )
        else:
            reply_text = (
                f"เรียน {vendor_name}\n\n"
                f"ขอขอบคุณสำหรับข้อเสนอราคา ฿{offered_price:,.2f} ต่อหน่วย อย่างไรก็ดี ราคาดังกล่าวยังสูงกว่ากรอบราคาตลาดเป้าหมายขององค์กร\n\n"
                f"เพื่อประโยชน์สูงสุดร่วมกัน ฝ่ายจัดซื้อขอเรียนเสนอการจัดทำสัญญาซื้อขายระยะยาวแบบ Blanket Order 1 ปีเต็ม โดยการันตียอดสั่งซื้อรวม "
                f"{annual_qty:,} หน่วย แลกกับการปรับราคามาที่ ฿{target_price:,.2f} ต่อหน่วย และเงื่อนไขการชำระเงิน 45 วัน "
                f"หากท่านยืนยันเงื่อนไขนี้ ทางเราพร้อมล็อกสถานะคู่สัญญาหลักให้ท่านได้ทันทีครับ {concession['tactic_label']}"
            )
        
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
