"""
Market Price Intelligence package.

Exposes a pluggable benchmark architecture:
  - MarketBenchmarkProvider : abstract provider interface (swap to SAP Ariba,
    EDI private catalog, external B2B API without touching business logic).
  - ThaiIndustrialCatalogProvider : default provider backed by a ground-truth
    Thai Industrial MRO price index.
  - MarketBenchmarkTool : facade computing price bands, volume-tier discounts,
    and BATNA leverage for the negotiation agents.
"""
from .benchmark_tool import MarketBenchmarkTool, market_benchmark_tool
from .catalog_provider import ThaiIndustrialCatalogProvider
from .provider import MarketBenchmarkProvider, MarketQuote

__all__ = [
    "MarketBenchmarkProvider",
    "MarketQuote",
    "ThaiIndustrialCatalogProvider",
    "MarketBenchmarkTool",
    "market_benchmark_tool",
]
