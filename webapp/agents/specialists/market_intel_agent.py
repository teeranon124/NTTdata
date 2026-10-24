import os
"""
MarketIntelligenceAgent — estimates the fair market price band for a part and
derives BATNA leverage the negotiator uses as an evidence-based bargaining anchor.

When a MarketBenchmarkTool is injected (Phase C), it sources a ground-truth Thai
Industrial MRO price band, volume-tier discounts, reservation price, and a BATNA
leverage score. Without a tool it falls back to a deterministic estimate, so the
agent never breaks.
"""
import logging

logger = logging.getLogger(__name__)


class MarketIntelligenceAgent:
    policy_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "market_intel_policy.md")
    name = "Market Intelligence Agent"

    def __init__(self, benchmark_tool=None):
        self.benchmark_tool = benchmark_tool

    def assess(self, deal_data: dict) -> dict:
        """
        Returns a market view (keys consumed downstream by StrategicNegotiator):
          market_low, market_high, market_mid, source, batna_leverage_pct,
          plus Phase C enrichment: reservation_price, batna_leverage_score,
          leverage_stance, volume_discount_pct, confidence, matched. Always
          includes an `audit` entry.
        """
        target = float(deal_data.get("target_unit_price") or deal_data.get("post_price") or round(budget * 0.85, 2))
        budget = float(deal_data.get("budget_unit_price") or deal_data.get("pre_price") or 450.0)
        annual_qty = int(deal_data.get("total_quantity") or deal_data.get("qty") or 0)
        part = deal_data.get("sku") or deal_data.get("part_code") or str(deal_data.get("id", "")).upper()
        part_name = deal_data.get("name") or ""
        category = deal_data.get("category") or None

        if self.benchmark_tool is not None:
            band = self.benchmark_tool.get_market_band(part, target, budget)
            # Pull volume-aware reservation + leverage directly from the tool.
            reservation = band.get("reservation_price")
            leverage_score = band.get("batna_leverage_score")
            stance = band.get("leverage_stance", "")
            vol_disc = band.get("volume_discount_pct", 0.0)
            confidence = band.get("confidence", 0.0)
            matched = band.get("matched", False)
            source = band.get("source", "Benchmark Tool")
        else:
            # Deterministic fallback band (no tool injected).
            band = {
                "market_low": round(target * 0.98, 2),
                "market_high": round(target * 1.06, 2),
                "market_mid": round(target, 2),
            }
            reservation = round(target, 2)
            leverage_score = None
            stance = ""
            vol_disc = 0.0
            confidence = 0.0
            matched = False
            source = "Deterministic Benchmark (no tool)"

        mid = band.get("market_mid") or target or 1.0
        leverage_pct = round(((budget - mid) / mid) * 100, 1) if mid else 0.0

        result = {
            "market_low": band["market_low"],
            "market_high": band["market_high"],
            "market_mid": band["market_mid"],
            "source": source,
            "batna_leverage_pct": leverage_pct,
            "reservation_price": reservation,
            "batna_leverage_score": leverage_score,
            "leverage_stance": stance,
            "volume_discount_pct": vol_disc,
            "confidence": confidence,
            "matched": matched,
        }

        score_txt = f" | BATNA Score {leverage_score}/100 ({stance})" if leverage_score is not None else ""
        match_txt = "พบในดัชนีราคา" if matched else "ประเมินแบบ Heuristic"
        result["audit"] = {
            "step": 2,
            "agent": self.name,
            "thought": (
                f"ราคากลางตลาด {part}: ฿{band['market_low']:,.2f}–฿{band['market_high']:,.2f} "
                f"(กลาง ฿{band['market_mid']:,.2f}, {match_txt}) | "
                f"Reservation ฿{reservation:,.2f} | BATNA Leverage {leverage_pct:+.1f}% เหนือราคากลาง{score_txt}"
            ),
            "tool_call": f"market_benchmark('{part}') -> ฿{band['market_low']}-฿{band['market_high']} [{source[:40]}]",
        }
        return result
