"""
ComplianceGuardrailAgent — the safety gate for every negotiation turn.

Three layers of defense, applied in order:
  1. Deterministic prompt-injection detection (local regex) — never bypassable.
  2. Deterministic procurement boundaries — hard ceiling price and minimum
     credit-term floor that the AI can never cross, regardless of LLM output.
  3. (Optional) Amazon Bedrock Guardrails — if BEDROCK_GUARDRAIL_ID is set and
     AWS is available, the content is additionally screened via boto3
     apply_guardrail. Absence of AWS degrades gracefully to layers 1-2.

This agent returns a structured verdict so the orchestrator can short-circuit
a turn before any strategic/LLM work happens.
"""
import logging
import os

from ..tools import check_prompt_injection, verify_procurement_guardrail

logger = logging.getLogger(__name__)


class ComplianceGuardrailAgent:
    name = "Compliance & Guardrail Agent"

    def __init__(self):
        self.guardrail_id = os.environ.get("BEDROCK_GUARDRAIL_ID", "").strip()
        self.guardrail_version = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT").strip()

    # -- Layer 3: optional managed Bedrock Guardrails ----------------------
    def _bedrock_guardrail_check(self, text: str) -> dict:
        """
        Screen text with Amazon Bedrock Guardrails when configured.
        Returns {"available": bool, "blocked": bool, "reason": str|None}.
        Never raises — any failure means "not available", falling back to local layers.
        """
        if not self.guardrail_id:
            return {"available": False, "blocked": False, "reason": None}
        try:
            from ..bedrock_client import bedrock_client
            client = bedrock_client.client
            if client is None:
                return {"available": False, "blocked": False, "reason": None}
            # bedrock-runtime exposes apply_guardrail in recent boto3.
            resp = client.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.guardrail_version,
                source="INPUT",
                content=[{"text": {"text": text}}],
            )
            action = resp.get("action", "NONE")
            blocked = action == "GUARDRAIL_INTERVENED"
            return {"available": True, "blocked": blocked, "reason": "Bedrock Guardrail intervened" if blocked else None}
        except Exception as e:  # pragma: no cover - network/permission dependent
            logger.info("Bedrock Guardrails not applied (%s) — using local guardrails.", e.__class__.__name__)
            return {"available": False, "blocked": False, "reason": None}

    # -- Public API --------------------------------------------------------
    def review(self, user_message: str, deal_data: dict, parsed_entities: dict) -> dict:
        """
        Returns:
          {
            "is_safe": bool,
            "block_reason": str | None,
            "block_reply": str | None,     # the message to send the supplier if blocked
            "audit": {step dict},          # audit trace entry
            "boundaries": {...}            # ceiling/floor applied (for downstream agents)
          }
        """
        # Layer 1: prompt injection
        injection = check_prompt_injection(user_message)
        bedrock = self._bedrock_guardrail_check(user_message)

        guard_mode = "Bedrock Guardrails" if bedrock["available"] else "Deterministic Local Guardrails"

        if not injection["is_safe"] or bedrock["blocked"]:
            reason = injection.get("reason") or bedrock.get("reason") or "Security policy violation"
            return {
                "is_safe": False,
                "block_reason": reason,
                "block_reply": (
                    "ขออภัยครับ ระบบ AutoProcure.AI ไม่อนุญาตให้แก้ไขหรือแทรกแซงกฎระเบียบการจัดซื้อกลาง "
                    "หากท่านประสงค์จะเสนอราคาหรือเงื่อนไขทางการค้า กรุณาระบุรายละเอียดสินค้าและราคาตามขั้นตอนปกติครับ "
                    "[Procurement Security Compliance]"
                ),
                "audit": {
                    "step": 1,
                    "agent": f"{self.name} ({guard_mode})",
                    "thought": "ตรวจพบรูปแบบข้อความไม่พึงประสงค์ (Prompt Injection / Policy Violation) จึงระงับการต่อรอง",
                    "tool_call": "check_prompt_injection() -> BLOCKED",
                },
                "boundaries": {},
            }

        # Layer 2: deterministic procurement boundaries (hard ceiling / credit floor).
        budget_price = float(
            deal_data.get("budget_unit_price") or deal_data.get("pre_price") or 450.0
        )
        min_credit = int(deal_data.get("standard_credit_days") or 30)
        offered_price = parsed_entities.get("proposed_unit_price") or budget_price
        offered_lead = parsed_entities.get("proposed_lead_time_days") or 7

        boundary = verify_procurement_guardrail(
            proposed_price=offered_price,
            budget_price=budget_price,
            lead_time_days=offered_lead,
        )

        boundaries = {
            "ceiling_price": round(budget_price * 1.05, 2),
            "min_credit_days": min_credit,
            "budget_price": budget_price,
            "boundary_check": boundary,
            "guard_mode": guard_mode,
        }

        return {
            "is_safe": True,
            "block_reason": None,
            "block_reply": None,
            "audit": {
                "step": 1,
                "agent": f"{self.name} ({guard_mode})",
                "thought": (
                    f"ผ่านการตรวจความปลอดภัย | เพดานราคา (Ceiling) ฿{boundaries['ceiling_price']:,.2f} | "
                    f"เครดิตขั้นต่ำ {min_credit} วัน | Boundary: "
                    f"{'ผ่าน' if boundary.get('passed') else boundary.get('error_code')}"
                ),
                "tool_call": "check_prompt_injection() -> SAFE | verify_procurement_guardrail()",
            },
            "boundaries": boundaries,
        }
