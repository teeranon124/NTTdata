"""
MarketIntelligenceAgent — estimates the fair market price band for a part and
derives BATNA leverage the negotiator can use as a bargaining anchor.

In Phase B this uses a deterministic estimate derived from the deal's own target
price (stable, demo-safe). Phase C will plug a real MarketBenchmarkTool into the
`benchmark_tool` slot without changing this agent's interface.
"""
import logging

logger = logging.getLogger(__name__)


class MarketIntelligenceAgent:
    name = "Market Intelligence Agent"

    def __init__(self, benchmark_tool=None):
        # Pluggable provider — set in Phase C. When None, use the deterministic estimate.
        self.benchmark_tool = benchmark_tool

    def assess(self, deal_data: dict) -> dict:
        """
        Returns a market view:
          {
            "market_low": float, "market_high": float, "market_mid": float,
            "source": str, "batna_leverage_pct": float,
            "audit": {step dict}
          }
        """
        target = float(deal_data.get("target_unit_price") or deal_data.get("post_price") or 398.0)
        budget = float(deal_data.get("budget_unit_price") or deal_data.get("pre_price") or 450.0)
        part = deal_data.get("sku") or deal_data.get("part_code") or str(deal_data.get("id", "")).upper()

        if self.benchmark_tool is not None:
            band = self.benchmark_tool.get_market_band(part, target, budget)
        else:
            # Deterministic band: centered near target, ~±4% spread.
            mid = target
            band = {
                "market_low": round(mid * 0.98, 2),
                "market_high": round(mid * 1.06, 2),
                "market_mid": round(mid, 2),
                "source": "Deterministic Benchmark (Phase B seed)",
            }

        # BATNA leverage: how far the current budget sits above market mid (%).
        mid = band["market_mid"] or target or 1.0
        leverage = round(((budget - mid) / mid) * 100, 1) if mid else 0.0
        band["batna_leverage_pct"] = leverage

        band["audit"] = {
            "step": 2,
            "agent": self.name,
            "thought": (
                f"ราคากลางตลาด {part}: ฿{band['market_low']:,.2f}–฿{band['market_high']:,.2f} "
                f"(กลาง ฿{band['market_mid']:,.2f}) | BATNA Leverage {leverage:+.1f}% เหนือราคากลาง"
            ),
            "tool_call": f"market_benchmark('{part}') -> ฿{band['market_low']}-฿{band['market_high']}",
        }
        return band
