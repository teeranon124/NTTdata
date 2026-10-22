"""
ComplianceGuardrailAgent — the safety gate for every negotiation turn.

Defense-in-depth, aligned with AWS Bedrock prompt-injection guidance
(https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-injection.html):

  Layer 0. Input Validation — sanitize/bound the raw message before any model
           call (strip control chars, cap length, defang role-spoof markers).
  Layer 1. Deterministic prompt-injection detection (local regex) — never
           bypassable, works with zero AWS dependency.
  Layer 2. Deterministic procurement boundaries — hard ceiling price and minimum
           credit-term floor the AI can never cross, regardless of LLM output.
  Layer 3. Amazon Bedrock Guardrails (optional) — ApplyGuardrail API screens the
           input against managed policies (incl. the PROMPT_ATTACK content
           filter). Absence of AWS degrades gracefully to layers 0-2.

Returns a structured verdict so the orchestrator can short-circuit a turn before
any strategic/LLM work happens. Also exposes the sanitized message so downstream
agents operate on validated text.
"""
import logging
import os

from ..tools import check_prompt_injection, sanitize_user_input, verify_procurement_guardrail

logger = logging.getLogger(__name__)


class ComplianceGuardrailAgent:
    name = "Compliance & Guardrail Agent"

    def __init__(self):
        self.guardrail_id = os.environ.get("BEDROCK_GUARDRAIL_ID", "").strip()
        self.guardrail_version = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT").strip()

    # -- Layer 3: optional managed Bedrock Guardrails (ApplyGuardrail API) --
    def _bedrock_guardrail_check(self, text: str) -> dict:
        """
        Screen text with Amazon Bedrock Guardrails via the standalone
        ApplyGuardrail API (no model invocation). Input is tagged with a
        'guard_content' qualifier so only the user text is evaluated.

        Returns {available, blocked, reason, categories}. Never raises — any
        failure means "not available", falling back to the local layers.
        Reference: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html
        """
        if not self.guardrail_id:
            return {"available": False, "blocked": False, "reason": None, "categories": []}
        try:
            from ..bedrock_client import bedrock_client
            client = bedrock_client.client
            if client is None:
                return {"available": False, "blocked": False, "reason": None, "categories": []}

            resp = client.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.guardrail_version,
                source="INPUT",
                content=[{"text": {"text": text, "qualifiers": ["guard_content"]}}],
            )
            action = resp.get("action", "NONE")
            blocked = action == "GUARDRAIL_INTERVENED"

            # Surface which policies intervened (e.g. PROMPT_ATTACK) for the audit trail.
            categories = []
            for assessment in resp.get("assessments", []):
                cf = assessment.get("contentPolicy", {}).get("filters", [])
                for f in cf:
                    if f.get("action") == "BLOCKED":
                        categories.append(f.get("type"))
                tp = assessment.get("topicPolicy", {}).get("topics", [])
                for t in tp:
                    if t.get("action") == "BLOCKED":
                        categories.append(f"topic:{t.get('name')}")
                wp = assessment.get("wordPolicy", {})
                if wp.get("customWords") or wp.get("managedWordLists"):
                    categories.append("word_filter")

            reason = None
            if blocked:
                reason = "Amazon Bedrock Guardrail intervened"
                if categories:
                    reason += f" ({', '.join(c for c in categories if c)})"
            return {"available": True, "blocked": blocked, "reason": reason, "categories": categories}
        except Exception as e:  # pragma: no cover - network/permission dependent
            logger.info("Bedrock Guardrails not applied (%s) — using local guardrails.", e.__class__.__name__)
            return {"available": False, "blocked": False, "reason": None, "categories": []}

    # -- Public API --------------------------------------------------------
    def review(self, user_message: str, deal_data: dict, parsed_entities: dict) -> dict:
        """
        Returns:
          {
            "is_safe": bool,
            "block_reason": str | None,
            "block_reply": str | None,     # message to send the supplier if blocked
            "clean_message": str,          # sanitized input for downstream agents
            "audit": {step dict},
            "boundaries": {...}            # ceiling/floor applied (for downstream agents)
          }
        """
        # Layer 0: input validation / sanitization (before anything else).
        sanitized = sanitize_user_input(user_message)
        clean_message = sanitized["clean"]

        # Layer 1: deterministic prompt-injection detection (on the sanitized text).
        injection = check_prompt_injection(clean_message)
        # Layer 3: managed Bedrock Guardrails (optional).
        bedrock = self._bedrock_guardrail_check(clean_message)

        guard_mode = "Bedrock Guardrails" if bedrock["available"] else "Deterministic Local Guardrails"
        sanitize_note = f" | Input sanitized: {', '.join(sanitized['notes'])}" if sanitized["modified"] else ""

        if not injection["is_safe"] or bedrock["blocked"]:
            reason = injection.get("reason") or bedrock.get("reason") or "Security policy violation"
            matched = injection.get("matched_pattern") or ", ".join(bedrock.get("categories", [])) or "policy"
            return {
                "is_safe": False,
                "block_reason": reason,
                "block_reply": (
                    "ขออภัยครับ ระบบ AutoProcure.AI ไม่อนุญาตให้แก้ไขหรือแทรกแซงกฎระเบียบการจัดซื้อกลาง "
                    "หากท่านประสงค์จะเสนอราคาหรือเงื่อนไขทางการค้า กรุณาระบุรายละเอียดสินค้าและราคาตามขั้นตอนปกติครับ "
                    "[Procurement Security Compliance]"
                ),
                "clean_message": clean_message,
                "audit": {
                    "step": 1,
                    "agent": f"{self.name} ({guard_mode})",
                    "thought": (
                        f"ตรวจพบรูปแบบข้อความไม่พึงประสงค์ (Prompt Injection / Policy Violation) จึงระงับการต่อรอง{sanitize_note}"
                    ),
                    "tool_call": f"sanitize_user_input() | check_prompt_injection() -> BLOCKED [{matched}]",
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
            "clean_message": clean_message,
            "audit": {
                "step": 1,
                "agent": f"{self.name} ({guard_mode})",
                "thought": (
                    f"ผ่านการตรวจความปลอดภัย | เพดานราคา (Ceiling) ฿{boundaries['ceiling_price']:,.2f} | "
                    f"เครดิตขั้นต่ำ {min_credit} วัน | Boundary: "
                    f"{'ผ่าน' if boundary.get('passed') else boundary.get('error_code')}{sanitize_note}"
                ),
                "tool_call": "sanitize_user_input() | check_prompt_injection() -> SAFE | verify_procurement_guardrail()",
            },
            "boundaries": boundaries,
        }
