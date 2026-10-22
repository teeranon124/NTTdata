"""
Pluggable Market Benchmark Provider interface.

A provider answers a single question: "What is the fair market price band for
this part (optionally at this annual volume)?" Concrete providers can source
that answer from a static catalog, SAP Ariba, an EDI private catalog, or an
external B2B pricing API — the negotiation agents depend only on this interface,
never on a concrete provider.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MarketQuote:
    """Normalized market pricing view returned by any provider."""
    part_code: str
    market_low: float
    market_median: float
    market_high: float
    currency: str = "THB"
    unit: str = "ชิ้น"
    source: str = "unknown"
    confidence: float = 0.0            # 0.0-1.0; how reliable this quote is
    matched: bool = False              # True if a real catalog entry matched
    category: Optional[str] = None
    # Volume-tier discounts: list of {min_qty, discount_pct} applied off median.
    volume_tiers: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "part_code": self.part_code,
            "market_low": round(self.market_low, 2),
            "market_median": round(self.market_median, 2),
            "market_high": round(self.market_high, 2),
            "currency": self.currency,
            "unit": self.unit,
            "source": self.source,
            "confidence": round(self.confidence, 2),
            "matched": self.matched,
            "category": self.category,
            "volume_tiers": self.volume_tiers,
        }


class MarketBenchmarkProvider(ABC):
    """Abstract base for all market benchmark data providers."""

    #: Human-readable provider name (shown in audit trails).
    name: str = "AbstractProvider"

    @abstractmethod
    def lookup(
        self,
        part_code: str,
        part_name: str = "",
        category: Optional[str] = None,
        annual_quantity: int = 0,
    ) -> Optional[MarketQuote]:
        """
        Return a MarketQuote for the part, or None if the provider has no data
        (the caller is responsible for applying a heuristic fallback). Providers
        MUST NOT raise on a miss — return None instead.
        """
        raise NotImplementedError
