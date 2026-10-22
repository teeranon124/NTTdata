"""
CentralArbitratorAgent — computes a composite TCO score for the current offer
and assigns a BAFO rank signal. Deterministic and demo-safe.

The TCO score (0-100) blends price competitiveness vs the target, credit-term
value, and market positioning, so the dashboard/CPO can see a single comparable
number per vendor turn.
"""
import logging

logger = logging.getLogger(__name__)


class CentralArbitratorAgent:
    name = "Central Arbitrator Agent"

    def arbitrate(self, deal_data: dict, tco_data: dict, concession: dict, market: dict) -> dict:
        """
        Returns:
          {
            "tco_score": float (0-100),
            "rank_signal": str,          # e.g. "BAFO Rank #1 (ผู้นำ TCO)"
            "is_award_candidate": bool,
            "audit": {step dict}
          }
        """
        target_price = float(deal_data.get("target_unit_price") or deal_data.get("post_price") or 398.0)
        budget_price = float(deal_data.get("budget_unit_price") or deal_data.get("pre_price") or 450.0)
        effective = float(tco_data.get("effective_tco_price") or tco_data.get("offered_price") or budget_price)

        # Price competitiveness: 100 at/below target, 0 at/above budget ceiling.
        span = max(budget_price - target_price, 1e-6)
        price_score = max(0.0, min(100.0, (budget_price - effective) / span * 100.0))

        # Credit value contribution (small positive nudge, capped).
        credit_benefit = float(tco_data.get("credit_benefit_per_unit") or 0.0)
        credit_score = max(0.0, min(100.0, (credit_benefit / max(target_price, 1.0)) * 100.0 * 20))

        # Market positioning: reward offers at or below market mid.
        market_mid = float(market.get("market_mid") or target_price)
        market_score = max(0.0, min(100.0, (market.get("market_high", budget_price) - effective)
                                     / max(market.get("market_high", budget_price) - market.get("market_low", target_price), 1e-6) * 100.0))

        tco_score = round(0.6 * price_score + 0.15 * credit_score + 0.25 * market_score, 1)
        tco_score = max(0.0, min(100.0, tco_score))

        is_award = concession.get("strategy") == "AGREE_AND_AWARD" or tco_data.get("is_target_met", False)
        if is_award or tco_score >= 90:
            rank_signal = "BAFO Rank #1 (ผู้นำ TCO — พร้อมออกใบ PO)"
        elif tco_score >= 75:
            rank_signal = "BAFO Rank #2 (แข่งขันได้ — ตามหลังผู้นำ)"
        else:
            rank_signal = "อยู่ระหว่างเจรจา (ยังไม่ผ่านเกณฑ์ TCO)"

        return {
            "tco_score": tco_score,
            "rank_signal": rank_signal,
            "is_award_candidate": bool(is_award),
            "audit": {
                "step": 6,
                "agent": self.name,
                "thought": (
                    f"คำนวณ TCO Score รวม = {tco_score}/100 "
                    f"(ราคา {price_score:.0f} · เครดิต {credit_score:.0f} · ตลาด {market_score:.0f}) "
                    f"→ {rank_signal}"
                ),
                "tool_call": f"arbitrate() -> tco_score={tco_score}, award={is_award}",
            },
        }
