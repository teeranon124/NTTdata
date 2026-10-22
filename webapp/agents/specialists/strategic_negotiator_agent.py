"""
StrategicNegotiatorAgent — runs the TCO math + game-theory concession engine and
synthesizes the Thai negotiation reply via Claude 3.5 Sonnet (HEAVY tier), with a
high-fidelity deterministic fallback when AWS is unavailable.
"""
import logging
import os

from ..model_gateway import TaskComplexity, model_gateway
from ..tools import calculate_tco, evaluate_concessions

logger = logging.getLogger(__name__)

_PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


class StrategicNegotiatorAgent:
    name = "Strategic Negotiator Agent"

    def run(self, deal_data: dict, vendor_name: str, user_message: str, history: list,
            parsed_entities: dict, market: dict) -> dict:
        """
        Returns:
          {
            "reply": str, "tactic": str,
            "tco_data": dict, "concession": dict,
            "audit": [list of audit entries],
            "model_meta": {model_id, latency_ms, input_tokens, output_tokens, status}
          }
        """
        audit = []

        budget_price = float(deal_data.get("budget_unit_price") or deal_data.get("pre_price") or 450.0)
        target_price = float(deal_data.get("target_unit_price") or deal_data.get("post_price") or 398.0)
        annual_qty = int(deal_data.get("total_quantity") or deal_data.get("qty") or 1000)
        std_credit = int(deal_data.get("standard_credit_days") or 30)
        plants = deal_data.get("plants") or ["PLANT-CBI-02 (ชลบุรี)", "PLANT-RYG-03 (ระยอง)", "PLANT-AYU-01 (อยุธยา)"]

        offered_price = parsed_entities.get("proposed_unit_price") or budget_price
        offered_credit = parsed_entities.get("proposed_credit_days") or std_credit

        # --- TCO math ---
        tco_res = calculate_tco(
            budget_price=budget_price,
            target_price=target_price,
            offered_price=offered_price,
            standard_credit=std_credit,
            offered_credit=offered_credit,
            annual_quantity=annual_qty,
        )
        audit.append({
            "step": 3,
            "agent": "TCO Calculation Engine",
            "thought": (
                f"ส่วนต่างราคาต่อหน่วย: ฿{tco_res['price_gap_per_unit']:+,.2f} | "
                f"ผลประโยชน์เครดิต: ฿{tco_res['credit_benefit_per_unit']:,.2f} | "
                f"ประหยัดสุทธิ TCO: ฿{tco_res['total_savings_thb']:,.2f} ({tco_res['savings_pct']}%)"
            ),
            "tool_call": f"calculate_tco(price={offered_price}, credit={offered_credit}) -> Effective: ฿{tco_res['effective_tco_price']}",
        })

        # --- Game-theory concession ---
        concession = evaluate_concessions(
            price_gap=tco_res["price_gap_per_unit"],
            offered_price=offered_price,
            target_price=target_price,
            current_credit=offered_credit,
            annual_quantity=annual_qty,
        )
        audit.append({
            "step": 4,
            "agent": "Game Theory Concession Engine (Nash Bargaining)",
            "thought": f"เลือกยุทธวิธี: {concession['strategy']} | {concession['rationale']} | อ้างอิงราคากลางตลาด ฿{market.get('market_mid', target_price):,.2f}",
            "tool_call": f"evaluate_concessions(gap={tco_res['price_gap_per_unit']}) -> Strategy: {concession['strategy']}",
        })

        # --- LLM synthesis via Dynamic Model Gateway (HEAVY tier -> Claude 3.5 Sonnet) ---
        policy_prompt = open(os.path.join(_PROMPTS_DIR, "negotiator_policy.md"), "r", encoding="utf-8").read()
        deal_context = f"""
CURRENT NEGOTIATION CONTEXT:
- Part Name: {deal_data.get('name')} ({deal_data.get('part_code', deal_data.get('sku', 'NSK-STD'))})
- Category: {deal_data.get('category_th', deal_data.get('category', 'MRO'))}
- Annual Demand: {annual_qty:,} units (Consolidated across {len(plants)} plants)
- Budget Ceiling Price: ฿{budget_price:,.2f} / unit
- Target Price: ฿{target_price:,.2f} / unit
- Market Benchmark Band: ฿{market.get('market_low', target_price):,.2f} - ฿{market.get('market_high', budget_price):,.2f}
- Supplier Name: {vendor_name}
- Supplier Proposed Price: ฿{offered_price:,.2f} / unit
- Supplier Proposed Credit: {offered_credit} days
- TCO Gap: ฿{tco_res['price_gap_per_unit']:+,.2f} / unit
- Game Theory Recommended Strategy: {concession['strategy']} ({concession['rationale']})
"""
        system_text = policy_prompt + "\n" + deal_context

        res = model_gateway.invoke(
            task_type="negotiate",
            system_text=system_text,
            messages=history + [{"sender": "vendor", "text": user_message}],
            temperature=0.3,
            complexity=TaskComplexity.HEAVY,
        )

        model_meta = {
            "model_id": res.get("model_id"),
            "latency_ms": res.get("latency_ms"),
            "input_tokens": res.get("input_tokens", 0),
            "output_tokens": res.get("output_tokens", 0),
            "status": res.get("status"),
            "tier": res.get("tier"),
        }

        if res.get("status") == "live_aws" and res.get("text"):
            reply_text = res["text"].strip()
            audit.append({
                "step": 5,
                "agent": f"Strategic Synthesis ({res.get('model_id')})",
                "thought": f"สร้างข้อความโต้ตอบเชิงพาณิชย์ด้วยบริบทสัญญารายปี เครดิตเทอม และราคากลางตลาด (Latency: {res.get('latency_ms')}ms, Tier: {res.get('tier')})",
                "tool_call": f"model_gateway.invoke(negotiate) -> tokens={model_meta['input_tokens']}+{model_meta['output_tokens']} SUCCESS",
            })
        else:
            reply_text = self._fallback_reply(concession, vendor_name, offered_price, offered_credit, target_price, annual_qty)
            audit.append({
                "step": 5,
                "agent": "Autonomous Negotiation Engine (Ready for Claude 3.5 Sonnet)",
                "thought": f"สร้างข้อความโต้ตอบอัตโนมัติตามกลยุทธ์ {concession['strategy']} (โหมด Deterministic Fallback)",
                "tool_call": "generate_response() -> READY",
            })

        return {
            "reply": reply_text,
            "tactic": concession["tactic_label"],
            "tco_data": tco_res,
            "concession": concession,
            "audit": audit,
            "model_meta": model_meta,
        }

    @staticmethod
    def _fallback_reply(concession, vendor_name, offered_price, offered_credit, target_price, annual_qty) -> str:
        if concession["strategy"] == "AGREE_AND_AWARD":
            return (
                f"เรียน {vendor_name}\n\n"
                f"ฝ่ายจัดซื้อกลางขอขอบคุณสำหรับข้อเสนอที่ราคา ฿{offered_price:,.2f} ต่อหน่วย พร้อมเงื่อนไขการชำระเงิน {offered_credit} วัน "
                f"จากการประเมินโครงสร้างต้นทุนรวม (TCO) ข้อเสนอของท่านผ่านเกณฑ์เป้าหมายขององค์กรเรียบร้อยแล้ว\n\n"
                f"ในลำดับถัดไป ระบบ AutoProcure.AI ได้จัดทำร่างใบสั่งซื้อ (Draft PO) เพื่อเสนอผู้บริหารลงนามอนุมัติผ่านระบบ SAP S/4HANA "
                f"และขอเรียนเชิญท่านเป็นคู่สัญญาหลักภายใต้ข้อตกลงระยะยาว (LTA) ประจำปีนี้ครับ {concession['tactic_label']}"
            )
        if concession["strategy"] == "CREDIT_TERM_LEVER":
            return (
                f"เรียน {vendor_name}\n\n"
                f"ขอขอบคุณสำหรับข้อเสนอราคา ฿{offered_price:,.2f} ต่อหน่วย ฝ่ายจัดซื้อเข้าใจถึงข้อจำกัดด้านโครงสร้างต้นทุนของท่านเป็นอย่างดี\n\n"
                f"เพื่อให้เกิดจุดลงตัวที่เป็นประโยชน์ร่วมกันของทั้งสองฝ่าย ทางเราขอเรียนเสนอให้คงราคาดังกล่าว โดยขอปรับเงื่อนไขการชำระเงิน (Credit Terms) "
                f"เป็น {concession['target_credit']} วัน พร้อมเงื่อนไขการจัดส่งแบบ DDP โดยไม่มีค่าใช้จ่ายเพิ่มเติม ซึ่งจะช่วยให้โครงสร้างต้นทุนรวม (TCO) "
                f"ผ่านเกณฑ์การอนุมัติขององค์กรได้ครับ {concession['tactic_label']}"
            )
        return (
            f"เรียน {vendor_name}\n\n"
            f"ขอขอบคุณสำหรับข้อเสนอราคา ฿{offered_price:,.2f} ต่อหน่วย อย่างไรก็ดี ราคาดังกล่าวยังสูงกว่ากรอบราคาตลาดเป้าหมายขององค์กร\n\n"
            f"เพื่อประโยชน์สูงสุดร่วมกัน ฝ่ายจัดซื้อขอเรียนเสนอการจัดทำสัญญาซื้อขายระยะยาวแบบ Blanket Order 1 ปีเต็ม โดยการันตียอดสั่งซื้อรวม "
            f"{annual_qty:,} หน่วย แลกกับการปรับราคามาที่ ฿{target_price:,.2f} ต่อหน่วย และเงื่อนไขการชำระเงิน 45 วัน "
            f"หากท่านยืนยันเงื่อนไขนี้ ทางเราพร้อมล็อกสถานะคู่สัญญาหลักให้ท่านได้ทันทีครับ {concession['tactic_label']}"
        )
