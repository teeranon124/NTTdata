"""
Unit tests for the Market Price Intelligence layer (Phase C).

Run: python -m pytest tests/test_market_benchmark.py
  or: python tests/test_market_benchmark.py   (self-running without pytest)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.agents.market import (  # noqa: E402
    MarketBenchmarkTool,
    ThaiIndustrialCatalogProvider,
    MarketBenchmarkProvider,
    MarketQuote,
)


def test_catalog_matches_bearing_by_sku_prefix():
    tool = MarketBenchmarkTool()
    a = tool.assess(part_code="NSK-6208-2RS1", part_name="ตลับลูกปืน", category="mechanical",
                    annual_quantity=16710, target=398.0, budget=450.0)
    assert a["matched"] is True
    assert a["confidence"] >= 0.9                      # SKU-prefix tier
    assert a["market_low"] <= a["market_median"] <= a["market_high"]
    assert 380.0 <= a["market_median"] <= 470.0        # bearing band
    # Volume >= 10000 -> top discount tier applied.
    assert a["volume_discount_pct"] == 9.0
    assert a["reservation_price"] < a["market_median"]


def test_catalog_matches_belt_by_keyword():
    tool = MarketBenchmarkTool()
    a = tool.assess(part_code="RMA-A50", part_name="สายพานร่องวี Bando", category="mechanical",
                    annual_quantity=2000, target=150.0, budget=200.0)
    assert a["matched"] is True
    assert 120.0 <= a["market_median"] <= 240.0


def test_sensor_band():
    tool = MarketBenchmarkTool()
    a = tool.assess(part_code="E3Z-D61", part_name="เซนเซอร์ Omron photo", category="electrical",
                    annual_quantity=500, target=1250.0, budget=1500.0)
    assert a["matched"] is True
    assert 850.0 <= a["market_median"] <= 2100.0


def test_graceful_fallback_on_unknown_sku():
    tool = MarketBenchmarkTool()
    a = tool.assess(part_code="ZZZ-UNKNOWN-999", part_name="ของแปลกไม่มีในตลาด", category=None,
                    annual_quantity=100, target=500.0, budget=560.0)
    # Must not raise; returns a heuristic band centered near target.
    assert a["matched"] is False
    assert a["confidence"] < 0.5
    assert a["market_low"] <= a["market_median"] <= a["market_high"]
    assert abs(a["market_median"] - 500.0) < 1e-6


def test_batna_leverage_scales_with_price_gap():
    tool = MarketBenchmarkTool()
    # Budget far above market median -> high leverage.
    high = tool.assess(part_code="NSK-6208", target=415.0, budget=520.0, reference_price=520.0,
                       category="mechanical", annual_quantity=1000)
    # Budget near market median -> low leverage.
    low = tool.assess(part_code="NSK-6208", target=415.0, budget=420.0, reference_price=420.0,
                      category="mechanical", annual_quantity=1000)
    assert high["batna_leverage_score"] > low["batna_leverage_score"]
    assert 0.0 <= low["batna_leverage_score"] <= 100.0
    assert 0.0 <= high["batna_leverage_score"] <= 100.0


def test_get_market_band_slot_contract():
    """MarketIntelligenceAgent expects these exact keys from the tool slot."""
    tool = MarketBenchmarkTool()
    band = tool.get_market_band("NSK-6208-2RS1", target=398.0, budget=450.0)
    for key in ("market_low", "market_high", "market_mid", "source"):
        assert key in band, f"missing slot key {key}"
    assert band["market_low"] <= band["market_mid"] <= band["market_high"]


def test_pluggable_custom_provider_overrides_catalog():
    class FakeProvider(MarketBenchmarkProvider):
        name = "FakeAriba"

        def lookup(self, part_code, part_name="", category=None, annual_quantity=0):
            return MarketQuote(part_code=part_code, market_low=10, market_median=20,
                               market_high=30, source="FakeAriba", confidence=1.0, matched=True)

    tool = MarketBenchmarkTool(providers=[FakeProvider()])
    a = tool.assess(part_code="NSK-6208", target=398.0, budget=450.0)
    assert a["source"] == "FakeAriba"
    assert a["market_median"] == 20       # proves provider swap without logic change


def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        t()
        print(f"[PASS] {t.__name__}")
        passed += 1
    print(f"\n{passed}/{len(tests)} market benchmark tests passed")


if __name__ == "__main__":
    _run_all()
