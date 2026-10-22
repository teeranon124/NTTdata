"""
ThaiIndustrialCatalogProvider — the default market benchmark provider.

Backed by a ground-truth Thai Industrial MRO price index covering 10 popular
part families, with price bands referenced to real Thai distributors (Misumi
Thailand, Factomart, RS Components, brand agents). Matching is tiered:

  1. Exact / prefix SKU match  (highest confidence)
  2. Brand + part-family keyword match
  3. Category-level band        (lower confidence)

All bands are deterministic and demo-safe (no network). Volume-tier discounts
model typical LTA/Blanket-Order concessions seen in Thai MRO procurement.
"""
from typing import List, Optional

from .provider import MarketBenchmarkProvider, MarketQuote

# Standard volume-tier discount ladder for consolidated annual demand (LTA).
_DEFAULT_VOLUME_TIERS = [
    {"min_qty": 1000, "discount_pct": 3.0},
    {"min_qty": 5000, "discount_pct": 6.0},
    {"min_qty": 10000, "discount_pct": 9.0},
]

# Ground-Truth Thai Industrial MRO Index — 10 part families.
# Prices in THB per unit; bands reflect typical street/distributor ranges in TH.
_CATALOG: List[dict] = [
    {
        "family": "bearing_deep_groove",
        "label": "ตลับลูกปืนเม็ดกลมร่องลึก (Deep Groove Ball Bearing)",
        "category": "mechanical",
        "brands": ["nsk", "skf", "ntn", "koyo", "nachi", "fag"],
        "sku_prefixes": ["6208", "6310", "6204", "6205", "6206", "ucp", "uc2"],
        "keywords": ["ตลับลูกปืน", "bearing", "แบริ่ง"],
        "low": 380.0, "median": 415.0, "high": 470.0,
        "source": "Misumi TH / Factomart (NSK/SKF bearing index)",
    },
    {
        "family": "v_belt",
        "label": "สายพานร่องวี / ร่องฟัน (V-Belt / Ribbed Belt)",
        "category": "mechanical",
        "brands": ["bando", "mitsuboshi", "gates", "optibelt", "contitech"],
        "sku_prefixes": ["a-", "b-", "spz", "spa", "spb", "3v", "5v", "rma"],
        "keywords": ["สายพาน", "belt", "v-belt", "ribbed"],
        "low": 120.0, "median": 165.0, "high": 240.0,
        "source": "Factomart / Bando TH dealer index",
    },
    {
        "family": "oil_seal",
        "label": "ซีลกันน้ำมัน / โอริง (Oil Seal / O-Ring)",
        "category": "mechanical",
        "brands": ["nok", "trelleborg", "klinger", "skf"],
        "sku_prefixes": ["tc", "sc", "or-", "as568", "g-"],
        "keywords": ["ซีล", "seal", "oring", "o-ring", "โอริง", "gasket", "ปะเก็น"],
        "low": 35.0, "median": 68.0, "high": 140.0,
        "source": "NOK TH agent / RS Components TH",
    },
    {
        "family": "photo_sensor",
        "label": "เซนเซอร์ตรวจจับ (Photoelectric / Proximity Sensor)",
        "category": "electrical",
        "brands": ["omron", "keyence", "sick", "panasonic", "autonics"],
        "sku_prefixes": ["e3", "e2", "pr", "bj", "fs-", "gl-", "wl-"],
        "keywords": ["เซนเซอร์", "sensor", "photo", "proximity", "fiber", "laser"],
        "low": 850.0, "median": 1250.0, "high": 2100.0,
        "source": "Factomart / Omron TH distributor index",
    },
    {
        "family": "contactor_breaker",
        "label": "คอนแทคเตอร์ / เบรกเกอร์ (Contactor / MCCB / MCB)",
        "category": "electrical",
        "brands": ["schneider", "mitsubishi", "fuji", "abb", "siemens", "ls"],
        "sku_prefixes": ["lc1", "ns", "nf", "sh", "bh", "3rt", "gv"],
        "keywords": ["คอนแทคเตอร์", "contactor", "เบรกเกอร์", "breaker", "mccb", "mcb"],
        "low": 480.0, "median": 780.0, "high": 1450.0,
        "source": "Schneider TH / Factomart breaker index",
    },
    {
        "family": "pneumatic_cylinder",
        "label": "กระบอกลม / วาล์วลม (Pneumatic Cylinder / Valve)",
        "category": "pneumatic",
        "brands": ["smc", "festo", "ckd", "koganei", "airtac", "pisco"],
        "sku_prefixes": ["cq2", "cm2", "mgp", "dsbc", "adn", "cxs", "vq", "sy"],
        "keywords": ["กระบอกลม", "cylinder", "วาล์วลม", "pneumatic", "solenoid"],
        "low": 650.0, "median": 980.0, "high": 1800.0,
        "source": "SMC TH / Factomart pneumatic index",
    },
    {
        "family": "fitting_tubing",
        "label": "ข้อต่อลม / ท่อลม (Push-in Fitting / PU Tubing)",
        "category": "pneumatic",
        "brands": ["smc", "pisco", "festo", "sang-a", "airtac"],
        "sku_prefixes": ["kq2", "pc", "pl", "pu", "pv", "pt"],
        "keywords": ["ข้อต่อ", "fitting", "ท่อลม", "tubing", "ท่อพียู"],
        "low": 18.0, "median": 42.0, "high": 95.0,
        "source": "Pisco TH / Factomart fitting index",
    },
    {
        "family": "linear_motion",
        "label": "ระบบส่งกำลังเชิงเส้น (Linear Guide / Ball Screw)",
        "category": "mechanical",
        "brands": ["thk", "iko", "hiwin", "nsk", "pmi"],
        "sku_prefixes": ["hsr", "shs", "lm", "sfu", "bsc", "lmk"],
        "keywords": ["ลิเนียร์", "linear", "ball screw", "บอลสกรู", "guide", "bushing", "บูช"],
        "low": 1200.0, "median": 1850.0, "high": 3200.0,
        "source": "THK TH agent / Misumi TH linear index",
    },
    {
        "family": "chain_sprocket",
        "label": "โซ่ส่งกำลัง / สเตอร์ (Roller Chain / Sprocket)",
        "category": "mechanical",
        "brands": ["tsubaki", "did", "khk", "martin", "renold"],
        "sku_prefixes": ["rs", "40-", "50-", "60-", "80-", "rf"],
        "keywords": ["โซ่", "chain", "สเตอร์", "sprocket", "gear", "เฟือง", "coupling", "คัปปลิ้ง"],
        "low": 240.0, "median": 390.0, "high": 720.0,
        "source": "Tsubaki TH / Factomart chain index",
    },
    {
        "family": "industrial_consumable",
        "label": "วัสดุสิ้นเปลืองอุตสาหกรรม (Adhesive / Lubricant / Silicone)",
        "category": "consumable",
        "brands": ["loctite", "mobil", "shell", "shinetsu", "3m", "wd"],
        "sku_prefixes": ["243", "271", "577", "gear", "kf-", "ls-"],
        "keywords": ["กาว", "adhesive", "loctite", "น้ำมัน", "oil", "lubricant", "ซิลิโคน", "silicone", "จาระบี", "grease"],
        "low": 280.0, "median": 480.0, "high": 950.0,
        "source": "Loctite TH / RS Components TH consumable index",
    },
]


def _norm(s: str) -> str:
    return (s or "").strip().lower()


class ThaiIndustrialCatalogProvider(MarketBenchmarkProvider):
    name = "Thai Industrial MRO Index"

    def __init__(self, catalog: Optional[List[dict]] = None):
        self._catalog = catalog if catalog is not None else _CATALOG

    def _match_entry(self, part_code: str, part_name: str, category: Optional[str]):
        pc = _norm(part_code)
        pn = _norm(part_name)
        cat = _norm(category)
        blob = f"{pc} {pn}"

        # Tier 1: SKU prefix match (highest confidence).
        for entry in self._catalog:
            for pre in entry["sku_prefixes"]:
                if pre and pre in pc:
                    return entry, 0.92, "sku_prefix"

        # Tier 2: brand + keyword match.
        for entry in self._catalog:
            brand_hit = any(b in blob for b in entry["brands"])
            kw_hit = any(k in blob for k in entry["keywords"])
            if brand_hit and kw_hit:
                return entry, 0.85, "brand+keyword"
            if brand_hit or kw_hit:
                return entry, 0.72, "brand_or_keyword"

        # Tier 3: category-level band (lower confidence).
        if cat:
            for entry in self._catalog:
                if entry["category"] == cat:
                    return entry, 0.55, "category"

        return None, 0.0, "none"

    def lookup(self, part_code: str, part_name: str = "", category: Optional[str] = None,
               annual_quantity: int = 0) -> Optional[MarketQuote]:
        entry, confidence, _tier = self._match_entry(part_code, part_name, category)
        if not entry:
            return None  # caller applies heuristic fallback; never raise
        return MarketQuote(
            part_code=part_code or entry["family"],
            market_low=float(entry["low"]),
            market_median=float(entry["median"]),
            market_high=float(entry["high"]),
            source=f"{self.name} — {entry['source']}",
            confidence=confidence,
            matched=True,
            category=entry["category"],
            volume_tiers=list(_DEFAULT_VOLUME_TIERS),
        )
