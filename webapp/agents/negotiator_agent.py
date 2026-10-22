"""
Negotiator Agent — public entry point for a single negotiation turn.

This now delegates to the multi-agent AgentOrchestrator (Compliance -> Market
Intelligence -> Strategic Negotiator -> Central Arbitrator) while preserving the
exact return contract the negotiation_service depends on:
    {reply, tactic, tco_data, concession, audit_trace}
(plus additive keys: arbitration, market, model_meta — ignored by legacy callers).
"""
from .orchestrator import orchestrator


def run_negotiation_turn(deal_data: dict, vendor_name: str, user_message: str,
                         history: list, parsed_entities: dict) -> dict:
    """Run one orchestrated negotiation turn. Contract-compatible with the prior implementation."""
    return orchestrator.run_turn(
        deal_data=deal_data,
        vendor_name=vendor_name,
        user_message=user_message,
        history=history,
        parsed_entities=parsed_entities,
    )
