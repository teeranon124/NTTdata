"""
MarketBenchmarkTool — the facade the negotiation agents call.

Wraps one or more MarketBenchmarkProviders and adds the intelligence layer:
  - Price band resolution (low / median / high) with graceful heuristic fallback.
  - Volume-tier discount application for consolidated annual demand (LTA).
  - BATNA Leverage Score: how much bargaining power the buyer holds given where
    the supplier's/ budget price sits relative to the market band.

Designed to be dependency-injected into MarketIntelligenceAgent (the `benchmark_tool`
slot prepared in Phase B). Exposes get_market_band(part, target, budget) to match
that slot's expected interface, plus a richer assess() for direct use.
"""
import logging
from typing import List, Optional

from .catalog_provider import ThaiIndustrialCatalogProvider
from .provider import MarketBenchmarkProvider, MarketQuote

logger = logging.getLogger(__name__)


class MarketBenchmarkTool:
    def __init__(self, providers: Optional[List[MarketBenchmarkProvider]] = None):
        # Provider chain: first provider that returns a quote wins. Swap/extend
        # with SAP Ariba / EDI / B2B API providers without touching agents.
        self.providers: List[MarketBenchmarkProvider] = providers or [ThaiIndustrialCatalogProvider()]

    # -- Core resolution ---------------------------------------------------
    def _resolve_quote(self, part_code: str, part_name: str, category: Optional[str],
                       annual_quantity: int, target: float, budget: float) -> MarketQuote:
        for provider in self.providers:
            try:
                quote = provider.lookup(part_code, part_name, category, annual_quantity)
            except Exception as e:  # provider must not break the turn
                logger.info("Provider %s lookup error (%s) — trying next.", getattr(provider, "name", "?"), e)
                quote = None
            if quote:
                return quote

        # Heuristic fallback: derive a plausible band from the deal's own economics.
        # Center near the target price with a realistic ±spread; never raises.
        mid = float(target) if target else (float(budget) * 0.88 if budget else 100.0)
        return MarketQuote(
            part_code=part_code or "UNKNOWN",
            market_low=round(mid * 0.96, 2),
            market_median=round(mid, 2),
            market_high=round(mid * 1.08, 2),
            source="Heuristic Estimate (no catalog match)",
            confidence=0.35,
            matched=False,
            category=category,
            volume_tiers=[{"min_qty": 5000, "discount_pct": 5.0}],
        )

    def _volume_adjusted_target(self, quote: MarketQuote, annual_quantity: int) -> dict:
        """Best achievable price at this annual volume, per the discount ladder."""
        applicable = [t for t in (quote.volume_tiers or []) if annual_quantity >= t.get("min_qty", 0)]
        best = max((t["discount_pct"] for t in applicable), default=0.0)
        volume_price = round(quote.market_median * (1 - best / 100.0), 2)
        return {"volume_discount_pct": best, "volume_target_price": volume_price}

    @staticmethod
    def _batna_leverage(reference_price: float, quote: MarketQuote) -> dict:
        """
        BATNA Leverage Score (0-100): the buyer's bargaining power. The further the
        reference price (supplier offer or budget) sits ABOVE the market median,
        the more leverage the buyer has to push down (strong alternative suppliers).
        """
        median = quote.market_median or reference_price or 1.0
        gap_pct = ((reference_price - median) / median) * 100.0 if median else 0.0
        # Map 0%..+20% above median onto a 0..100 leverage score (capped).
        score = max(0.0, min(100.0, (gap_pct / 20.0) * 100.0))
        if score >= 66:
            stance = "แข็งแกร่ง (ราคาตลาดต่ำกว่ามาก — กดราคาได้สูง)"
        elif score >= 33:
            stance = "ปานกลาง (มีช่องต่อรองตามราคาตลาด)"
        else:
            stance = "จำกัด (ราคาใกล้เคียงตลาดแล้ว)"
        return {
            "batna_leverage_score": round(score, 1),
            "price_vs_median_pct": round(gap_pct, 1),
            "leverage_stance": stance,
        }

    # -- Public API for agents --------------------------------------------
    def assess(self, part_code: str, part_name: str = "", category: Optional[str] = None,
               annual_quantity: int = 0, target: float = 0.0, budget: float = 0.0,
               reference_price: Optional[float] = None) -> dict:
        """
        Full market assessment. `reference_price` defaults to the budget price
        (the buyer's walk-away ceiling) when computing leverage.
        """
        quote = self._resolve_quote(part_code, part_name, category, annual_quantity, target, budget)
        vol = self._volume_adjusted_target(quote, annual_quantity)
        ref = reference_price if reference_price is not None else (budget or quote.market_high)
        leverage = self._batna_leverage(ref, quote)

        out = quote.to_dict()
        out.update(vol)
        out.update(leverage)
        # Reservation price (buyer walk-away): the volume-adjusted market target.
        out["reservation_price"] = vol["volume_target_price"]
        return out

    def get_market_band(self, part_code: str, target: float, budget: float) -> dict:
        """
        Compatibility method for the MarketIntelligenceAgent slot (Phase B).
        Returns keys: market_low, market_high, market_mid, source (+ enrichment).
        """
        a = self.assess(part_code=part_code, target=target, budget=budget, reference_price=budget)
        return {
            "market_low": a["market_low"],
            "market_high": a["market_high"],
            "market_mid": a["market_median"],
            "source": a["source"],
            # Enrichment used by MarketIntelligenceAgent / StrategicNegotiator.
            "confidence": a["confidence"],
            "matched": a["matched"],
            "reservation_price": a["reservation_price"],
            "volume_discount_pct": a["volume_discount_pct"],
            "batna_leverage_score": a["batna_leverage_score"],
            "leverage_stance": a["leverage_stance"],
        }


# Shared singleton — injected into the orchestrator's MarketIntelligenceAgent.
market_benchmark_tool = MarketBenchmarkTool()
