"""
StrategicNegotiatorAgent — runs the TCO math + game-theory concession engine and
synthesizes the Thai negotiation reply via Claude 3.5 Sonnet (HEAVY tier), with a
high-fidelity deterministic fallback when AWS is unavailable.
"""
import logging
import os
import re

from ..model_gateway import TaskComplexity, model_gateway
from ..tools import calculate_tco, evaluate_concessions

logger = logging.getLogger(__name__)

_PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


class StrategicNegotiatorAgent:
    name = "Strategic Negotiator Agent"
    policy_file = os.path.join(_PROMPTS_DIR, "strategic_negotiator_policy.md")

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
        target_price = float(deal_data.get("target_unit_price") or deal_data.get("post_price") or round(budget_price * 0.85, 2))
        annual_qty = int(deal_data.get("total_quantity") or deal_data.get("qty") or 1000)
        std_credit = int(deal_data.get("standard_credit_days") or 30)
        plants = deal_data.get("plants") or ["PLANT-CBI-02 (ชลบุรี)", "PLANT-RYG-03 (ระยอง)", "PLANT-AYU-01 (อยุธยา)"]

        offered_price = parsed_entities.get("proposed_unit_price") or budget_price
        offered_credit = parsed_entities.get("proposed_credit_days") or std_credit

        # Round number: each prior round added a vendor+agent message pair to history.
        has_agent_msg = any(m.get("sender") in ("agent", "ai") for m in (history or []))
        vendor_msg_count = len([m for m in (history or []) if m.get("sender") == "vendor"])
        # If an opening message already exists from the buyer agent, this supplier reply is Turn 2!
        round_num = (vendor_msg_count + 2) if has_agent_msg else (vendor_msg_count + 1)

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
                f"เทียบเป้าหมาย Target: {'ชนราคาเป้าหมายแล้ว (Target Met)' if tco_res['price_gap_per_unit'] <= 0 else f'สูงกว่าเป้า ฿{tco_res["price_gap_per_unit"]:,.2f}'} | ลดจากงบตั้งต้น: ฿{budget_price - offered_price:,.2f}/หน่วย | "
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
            round_num=round_num,
            intent=parsed_entities.get("intent", ""),
        )
        from ..skills import skill_registry
        skill_name = "anchoring_concession_ladder.md" if round_num <= 1 else "nash_bargaining_equilibrium.md"
        skill_content = skill_registry.read_skill(skill_name)

        audit.append({
            "step": 4,
            "agent": f"Game Theory Engine (Skill: {skill_name})",
            "thought": f"เปิดอ่านทฤษฎี [{skill_name}] | เลือกยุทธวิธี: {concession['strategy']} | {concession['rationale']} | อ้างอิงราคากลาง ฿{market.get('market_mid', target_price):,.2f}",
            "tool_call": f"skill_registry.read_skill('{skill_name}') -> evaluate_concessions(round={round_num}) -> {concession['strategy']}",
        })

        # --- LLM synthesis via Dynamic Model Gateway (HEAVY tier) ---
        prompt_path = os.path.join(_PROMPTS_DIR, "strategic_negotiator_policy.md")
        if not os.path.exists(prompt_path):
            prompt_path = os.path.join(_PROMPTS_DIR, "negotiator_policy.md")
        policy_prompt = open(prompt_path, "r", encoding="utf-8").read()
        directive = self._strategy_directive(concession, target_price, annual_qty, round_num, offered_price, offered_credit)
        deal_context = f"""
CURRENT NEGOTIATION CONTEXT:
- Part: {deal_data.get('name')} ({deal_data.get('part_code', deal_data.get('sku', 'NSK-STD'))})
- Annual Demand: {annual_qty:,} units across {len(plants)} plants
- Budget Ceiling: ฿{budget_price:,.2f} | Target: ฿{target_price:,.2f} / unit
- Market Band: ฿{market.get('market_low', target_price):,.2f}-฿{market.get('market_high', budget_price):,.2f} (median ฿{market.get('market_mid', target_price):,.2f})
- BATNA Leverage: {market.get('batna_leverage_score', 'n/a')}/100 ({market.get('leverage_stance', 'n/a')})
- Supplier: {vendor_name} proposed ฿{offered_price:,.2f} / {offered_credit} days
- TCO Gap vs target: ฿{tco_res['price_gap_per_unit']:+,.2f} / unit
- Decided Strategy: {concession['strategy']}

REQUIRED ACTION FOR THIS TURN:
{directive}

STYLE: Reply in professional Thai procurement language. Be concise and decisive
— no more than ~5 short sentences or a short numbered list. Do NOT pad or repeat.
When countering a high price, cite the market band (not the secret target) as the
anchor. Do NOT append internal tactic tags or brackets to the message.
"""
        active_skill_block = (
            f"\n\n=======================================================\n"
            f"ACTIVELY RETRIEVED NEGOTIATION THEORY SKILL: {skill_name}\n"
            f"=======================================================\n"
            f"{skill_content}\n"
            f"=======================================================\n"
        )
        system_text = policy_prompt + active_skill_block + "\n" + deal_context

        res = model_gateway.invoke(
            task_type="negotiate",
            system_text=system_text,
            messages=history + [{"sender": "vendor", "text": user_message}],
            temperature=0.3,
            complexity=TaskComplexity.HEAVY,
            # A concise procurement reply fits well under 512 tokens; this roughly
            # halves generation latency vs 1024 for the Nova Pro negotiator turn.
            max_tokens=512,
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
            reply_text = re.sub(r"\s*\[[^\]]+\]\s*$", "", reply_text).strip()
            reply_text = re.sub(r"(สุภาพ\s*หนักแน่น\s*รัดกุม\s*ชัดเจน\s*)", "", reply_text).strip()
            audit.append({
                "step": 5,
                "agent": f"Strategic Synthesis ({res.get('model_id')})",
                "thought": f"สร้างข้อความโต้ตอบเชิงพาณิชย์ด้วยบริบทสัญญารายปี เครดิตเทอม และราคากลางตลาด (Latency: {res.get('latency_ms')}ms, Tier: {res.get('tier')})",
                "tool_call": f"model_gateway.invoke(negotiate) -> tokens={model_meta['input_tokens']}+{model_meta['output_tokens']} SUCCESS",
            })
        else:
            reply_text = self._fallback_reply(concession, vendor_name, offered_price, offered_credit, target_price, annual_qty, market, deal_data=deal_data, parsed_entities=parsed_entities, user_message=user_message, budget_price=budget_price)
            audit.append({
                "step": 5,
                "agent": "Strategic Synthesis (Amazon Nova Pro Engine)",
                "thought": f"สร้างข้อความเจรจาภาษาไทยเชิงกลยุทธ์ อ้างอิงสัญญา Blanket LTA และกรอบ TCO ตามกลยุทธ์ {concession['strategy']} (โหมด Deterministic Fallback)",
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
    def _strategy_directive(concession, target_price, annual_qty, round_num=1, offered_price=0.0, offered_credit=30) -> str:
        """
        Turn the game-theory decision into an explicit, unambiguous instruction so
        the LLM's message matches the computed strategy (prevents the model from
        counter-offering on a deal it should close). Round-aware: later rounds push
        toward convergence instead of repeating the same opening counter.
        """
        strategy = concession.get("strategy")
        round_note = (
            f"This is negotiation ROUND {round_num}. " +
            ("This is an opening round — set the anchor clearly." if round_num <= 1
             else "This is a follow-up round — acknowledge the supplier has already moved, "
                  "avoid repeating the identical counter verbatim, and push toward convergence.")
        )

        if strategy == "AGREE_AND_AWARD":
            return (
                round_note + " ACCEPT and CLOSE the deal now. Thank the supplier, confirm their "
                "price and credit terms are APPROVED, and state that a Draft PO will be issued "
                "in SAP for executive sign-off. Do NOT ask for any further concession "
                "(no extra credit days, no DDP, no price cut) — the terms already meet target."
            )
        if strategy == "CREDIT_TERM_LEVER":
            return (
                round_note + f" ACCEPT the price (฿{offered_price:,.2f}) but request ONE concession "
                f"only: extend credit terms to {concession.get('target_credit', 60)} days "
                "(optionally free DDP delivery). Do not ask for a price reduction. Frame it as a "
                "win-win on working capital."
            )
        if strategy == "COUNTER_OFFER_CONVERGENCE":
            counter_p = concession.get("counter_price", target_price)
            target_c = concession.get("target_credit", 45)
            return (
                f"{round_note} ACTIVE COUNTER-OFFER: The supplier has proposed ฿{offered_price:,.2f} with {offered_credit} days credit. "
                "1. Express polite appreciation for their proposal and specifically acknowledge any value-added services (such as safety stock buffer 10% or SLA claim guarantees) they offered. "
                f"2. Clearly state that while their service commitment is valued, ฿{offered_price:,.2f} remains above the corporate budget ceiling for an annual blanket order of {annual_qty:,} units across 3 plants. "
                f"3. Put forward our official compromise counter-offer: ฿{counter_p:,.2f} / unit with {target_c}-day credit terms under a guaranteed 1-Year Blanket Order. "
                f"4. Invite them to accept ฿{counter_p:,.2f} so we can finalize the contract and issue the formal PO in SAP. Write in professional, persuasive Thai procurement language."
            )
        counter_price = concession.get("counter_price", target_price)
        target_credit = concession.get("target_credit", 45)
        # VOLUME_LTA_CONCESSION (or default)
        return (
            round_note + f" COUNTER the offer: propose a 1-year Blanket Order (LTA) guaranteeing "
            f"{annual_qty:,} units in exchange for the counter price of ฿{counter_price:,.2f} "
            f"and {target_credit}-day credit. Do NOT cite the secret target (฿{target_price:,.2f}) or budget ceiling. "
            "Justify using the market band and volume consolidation across all plants. "
            "If the supplier has already conceded close to target, move toward convergence."
        )

    @staticmethod
    def _fallback_reply(concession, vendor_name, offered_price, offered_credit, target_price, annual_qty, market=None, deal_data=None, parsed_entities=None, user_message="", budget_price=0.0) -> str:
        deal_data = deal_data or {}
        parsed_entities = parsed_entities or {}
        budget_price = budget_price or float(deal_data.get("budget_unit_price") or deal_data.get("pre_price") or target_price)
        market = market or {}
        m_low = market.get("market_low")
        m_high = market.get("market_high")
        m_mid = market.get("market_mid")
        # Evidence sentence citing the market band (BATNA anchor) — never the secret target.
        market_evidence = ""
        if m_low and m_high:
            market_evidence = (
                f" ทั้งนี้ จากการอ้างอิงดัชนีราคากลางตลาดอุตสาหกรรม ({market.get('source', 'Market Index')}) "
                f"ราคากลางของสินค้าประเภทนี้อยู่ในช่วง ฿{m_low:,.2f}–฿{m_high:,.2f} ต่อหน่วย (ค่ากลาง ฿{m_mid:,.2f})"
            )
        if concession["strategy"] == "AGREE_AND_AWARD":
            return (
                f"เรียน {vendor_name}\n\n"
                f"ฝ่ายจัดซื้อกลางขอขอบคุณสำหรับความร่วมมือและข้อเสนอราคา ฿{offered_price:,.2f} ต่อหน่วย พร้อมเงื่อนไขการชำระเงิน {offered_credit} วัน "
                f"ซึ่งสอดคล้องกับกรอบสัญญาจัดซื้อและข้อตกลงระยะยาว (LTA) ประจำปีขององค์กรเรียบร้อยแล้ว\n\n"
                f"ในลำดับถัดไป ระบบได้จัดทำร่างใบสั่งซื้อ (Draft PO) เพื่อเสนอผู้บริหารลงนามอนุมัติตามขั้นตอนกำกับดูแลผ่านระบบ SAP S/4HANA "
                f"และขอต้อนรับท่านเป็นคู่สัญญาหลักสำหรับเครือข่ายโรงงานทั้ง 3 แห่งอย่างเป็นทางการครับ"
            )
        if concession["strategy"] == "CREDIT_TERM_LEVER":
            return (
                f"เรียน {vendor_name}\n\n"
                f"ขอขอบคุณสำหรับข้อเสนอราคา ฿{offered_price:,.2f} ต่อหน่วย ฝ่ายจัดซื้อเข้าใจถึงโครงสร้างต้นทุนของท่านเป็นอย่างดี\n\n"
                f"เพื่อให้เกิดจุดลงตัวร่วมกันของทั้งสองฝ่าย ทางฝ่ายจัดซื้อขอเรียนเสนอให้คงราคาดังกล่าว โดยขอปรับเงื่อนไขการชำระเงิน (Credit Terms) "
                f"เป็น {concession['target_credit']} วัน พร้อมเงื่อนไขการจัดส่งแบบ DDP ถึงโรงงานทั้ง 3 นิคมฯ โดยไม่มีค่าใช้จ่ายเพิ่มเติม เพื่อให้สอดคล้องกับเกณฑ์การอนุมัติสัญญาขององค์กรครับ"
            )
        deal_name = deal_data.get("name") or deal_data.get("sku") or "สินค้า"
        unit_name = deal_data.get("unit") or "หน่วย"

        counter_p = concession.get("counter_price", target_price)
        target_c = concession.get("target_credit", 45)

        # If user did not offer a price (e.g. asked an inquiry, questioned 0.00 or terms)
        if not parsed_entities.get("proposed_unit_price") or str(user_message).strip() == "" or "ฟรี" in str(user_message) or "0.00" in str(user_message):
            return (
                f"เรียน {vendor_name}\n\n"
                f"ฝ่ายจัดซื้อกลางขอเรียนชี้แจงเพิ่มเติมครับ สำหรับรายการ {deal_name} ทางกลุ่มโรงงานขอเรียนเสนอเปิดเงื่อนไขการจัดซื้อที่ "
                f"฿{counter_p:,.2f} ต่อ{unit_name} พร้อมเงื่อนไขการชำระเงิน {target_c} วัน "
                f"เพื่อแลกกับการผูกสัญญาซื้อขายระยะยาวแบบ Blanket Order 1 ปีเต็ม การันตียอดสั่งซื้อรวม {annual_qty:,} {unit_name}{market_evidence}\n\n"
                f"ทางท่านเห็นสมควรหรือต้องการเสนอเงื่อนไขราคาและเครดิตเทอมโต้ตอบอย่างไร สามารถแจ้งข้อเสนอเข้ามาได้เลยครับ"
            )

        return (
            f"เรียน {vendor_name}\n\n"
            f"ขอขอบคุณสำหรับข้อเสนอราคา ฿{offered_price:,.2f} ต่อ{unit_name} อย่างไรก็ดี ราคาดังกล่าวยังสูงกว่ากรอบราคากลางอุตสาหกรรม"
            f"{market_evidence}\n\n"
            f"เพื่อประโยชน์สูงสุดร่วมกัน ฝ่ายจัดซื้อขอเรียนเสนอการจัดทำสัญญาซื้อขายระยะยาวแบบ Blanket Order 1 ปีเต็ม โดยการันตียอดสั่งซื้อรวม "
            f"{annual_qty:,} {unit_name} ให้กับท่าน แลกกับการปรับเงื่อนไขราคามาที่ ฿{counter_p:,.2f} ต่อ{unit_name} "
            f"และเงื่อนไขการชำระเงิน {target_c} วัน หากท่านสามารถยืนยันเงื่อนไขนี้ได้ ทางเราพร้อมล็อกสถานะคู่สัญญาหลักให้ท่านทันทีครับ"
        )
