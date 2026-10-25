"""
AgentOrchestrator — coordinates the specialized agents for a negotiation turn.

Pipeline:
  1. ComplianceGuardrailAgent  — safety gate (injection + hard boundaries).
  2. MarketIntelligenceAgent   — market band + BATNA leverage.
  3. StrategicNegotiatorAgent  — TCO math, Nash concession, Claude 3.5 Sonnet synthesis.
  4. CentralArbitratorAgent    — composite TCO score + BAFO rank signal.

Returns the SAME dict contract the legacy run_negotiation_turn() produced
(keys: reply, tactic, tco_data, concession, audit_trace) so downstream
services and the frontend are unaffected. Extra keys (arbitration, model_meta)
are additive and ignored by existing consumers.
"""
import logging

from .market import market_benchmark_tool
from .specialists import (
    CentralArbitratorAgent,
    ComplianceGuardrailAgent,
    MarketIntelligenceAgent,
    StrategicNegotiatorAgent,
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    def __init__(self, benchmark_tool=None):
        # Default to the Thai Industrial MRO benchmark tool (Phase C). Callers can
        # inject a different provider chain for enterprise deployments.
        tool = benchmark_tool if benchmark_tool is not None else market_benchmark_tool
        self.compliance = ComplianceGuardrailAgent()
        self.market = MarketIntelligenceAgent(benchmark_tool=tool)
        self.negotiator = StrategicNegotiatorAgent()
        self.arbitrator = CentralArbitratorAgent()

    def run_turn(self, deal_data: dict, vendor_name: str, user_message: str,
                 history: list, parsed_entities: dict) -> dict:
        audit_trace = []

        # 1) Compliance gate ------------------------------------------------
        verdict = self.compliance.review(user_message, deal_data, parsed_entities)
        if not verdict["is_safe"]:
            # Short-circuit: mirror the legacy blocked-turn return shape.
            return {
                "reply": verdict["block_reply"],
                "tactic": "[Security Alert: Prompt Injection Blocked]",
                "audit_trace": [verdict["audit"]],
            }
        audit_trace.append(verdict["audit"])

        # Downstream agents operate on the sanitized message (Input Validation layer).
        clean_message = verdict.get("clean_message", user_message)

        # Router/intent trace (kept for continuity with the prior audit layout).
        audit_trace.append({
            "step": 2,
            "agent": f"Router Agent ({parsed_entities.get('source', 'Nova Micro')})",
            "thought": (
                f"สกัดความประสงค์คู่ค้า: {parsed_entities.get('intent')} | "
                f"ราคาเสนอ: {parsed_entities.get('proposed_unit_price')} | "
                f"เครดิต: {parsed_entities.get('proposed_credit_days')} วัน"
            ),
            "tool_call": f"parse_supplier_intent() -> intent={parsed_entities.get('intent')}",
        })

        # 2) Market intelligence -------------------------------------------
        market = self.market.assess(deal_data)
        audit_trace.append(market["audit"])

        # 3) Strategic negotiation -----------------------------------------
        strat = self.negotiator.run(
            deal_data=deal_data,
            vendor_name=vendor_name,
            user_message=clean_message,
            history=history,
            parsed_entities=parsed_entities,
            market=market,
        )
        audit_trace.extend(strat["audit"])

        # 4) Central arbitration -------------------------------------------
        arb = self.arbitrator.arbitrate(deal_data, strat["tco_data"], strat["concession"], market)
        audit_trace.append(arb["audit"])

        return {
            # --- legacy contract (unchanged) ---
            "reply": strat["reply"],
            "tactic": strat["tactic"],
            "tco_data": strat["tco_data"],
            "concession": strat["concession"],
            "audit_trace": audit_trace,
            # --- additive enterprise metadata (safe to ignore) ---
            "arbitration": {
                "tco_score": arb["tco_score"],
                "rank_signal": arb["rank_signal"],
                "is_award_candidate": arb["is_award_candidate"],
            },
            "market": {k: v for k, v in market.items() if k != "audit"},
            "model_meta": strat["model_meta"],
        }


# Shared orchestrator instance (benchmark_tool wired in Phase C).
orchestrator = AgentOrchestrator()
