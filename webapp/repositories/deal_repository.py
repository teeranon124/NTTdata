import json
import os
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
MASTER_DEALS_FILE = os.path.join(DATA_DIR, 'master_deals.json')
RAW_2500_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dataset_2500.json')

class DealRepository:
    def __init__(self):
        self._deals_cache = None
        self._raw_cache = None

    def reload(self):
        self._deals_cache = None
        self._raw_cache = None
        return self.get_all_deals()

    def get_all_deals(self) -> Dict[str, dict]:
        if not self._deals_cache:
            if os.path.exists(MASTER_DEALS_FILE):
                with open(MASTER_DEALS_FILE, 'r', encoding='utf-8') as f:
                    self._deals_cache = json.load(f)
            else:
                self._deals_cache = {}
        return self._deals_cache

    def get_deal(self, deal_id: str) -> Optional[dict]:
        deals = self.get_all_deals()
        return deals.get(deal_id.lower())

    def get_statistics(self) -> dict:
        deals = self.get_all_deals()
        total_spend = sum(d.get('pre_spend', d.get('budget_total_thb', 0.0)) for d in deals.values())
        total_savings = sum(d.get('savings', d.get('total_savings_thb', 0.0)) for d in deals.values())
        total_prs = sum(d.get('prs_count', d.get('total_prs', 0)) for d in deals.values())
        total_qty = sum(d.get('qty', d.get('total_quantity', 0)) for d in deals.values())

        stages_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        stages_prs = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for d in deals.values():
            s = d.get('stage', 1)
            stages_count[s] = stages_count.get(s, 0) + 1
            stages_prs[s] = stages_prs.get(s, 0) + d.get('prs_count', d.get('total_prs', 0))

        return {
            'total_spend_thb': round(total_spend, 2),
            'total_savings_thb': round(total_savings, 2),
            'savings_pct': round((total_savings / total_spend) * 100, 1) if total_spend else 0.0,
            'total_prs': total_prs,
            'total_quantity': total_qty,
            'total_deals': len(deals),
            'stages_count': stages_count,
            'stages_prs': stages_prs
        }

    def get_raw_transactions(self, deal_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[dict]:
        if not self._raw_cache:
            if os.path.exists(RAW_2500_FILE):
                with open(RAW_2500_FILE, 'r', encoding='utf-8') as f:
                    self._raw_cache = json.load(f)
            else:
                self._raw_cache = []
        
        if not deal_id:
            return self._raw_cache[offset:offset+limit]

        did = deal_id.lower()
        exact = [r for r in self._raw_cache if r.get('deal_key', '').lower() == did]
        if exact:
            return exact[offset:offset+limit]
        filtered = [
            r for r in self._raw_cache
            if did in r.get('deal_key', '').lower()
            or did.upper() in r.get('code', '').upper()
            or did.upper() in r.get('deal', '').upper()
        ]
        return filtered[offset:offset+limit]

    def mark_deal_awarded(self, deal_id: str, vendor_id: str, agreed_price=None) -> bool:
        """Closed-loop award transition on the in-memory JSON deal (Stage 4)."""
        deals = self.get_all_deals()
        d = deals.get((deal_id or "").lower())
        if not d:
            return False
        d["stage"] = 4
        d["stage_label"] = "รอลงนาม PO"
        d["winning_vendor_id"] = vendor_id
        if agreed_price is not None:
            d["agreed_price"] = float(agreed_price)
        d.setdefault("po_status", "AWARDED")
        
        # Update in-memory vendor list statuses
        for v in d.get("vendors", []):
            vid = str(v.get("id", "")).lower()
            vname = str(v.get("name", "")).lower()
            target = str(vendor_id).lower()
            if vid == target or target in vid or target in vname or vid in target:
                v["status"] = "ชนะการประมูล (ออกใบ PO)"
                v["statusBadge"] = "badge-success text-white font-bold"
                if agreed_price is not None:
                    v["price"] = f"฿{float(agreed_price):,.2f}"
            else:
                if not v.get("price") or str(v.get("price")).strip() in ("-", ""):
                    v["status"] = "รอเสนอราคา"
                    v["statusBadge"] = "badge-ghost text-slate-400"
                else:
                    v["status"] = "ไม่ได้รับเลือก (Outbid)"
                    v["statusBadge"] = "badge-ghost text-slate-500"
        return True

    def create_po(self, deal_id: str, po_number: str) -> bool:
        deals = self.get_all_deals()
        d = deals.get((deal_id or "").lower())
        if not d:
            return False
        d["po_number"] = po_number
        d["po_status"] = "PO_CREATED"
        d["stage"] = 4
        return True

    def update_stage(self, deal_id: str, stage: int, stage_label: str = None) -> bool:
        deal = self.get_deal(deal_id)
        if not deal:
            return False
        deal["stage"] = stage
        if stage_label:
            deal["stage_label"] = stage_label
        return True

    def update_vendor_terms(self, deal_id: str, vendor_identifier: str, price: float = None, credit_days: int = None, lead_time_days: int = None, status: str = None) -> bool:
        deal = self.get_deal(deal_id)
        if not deal:
            return False
        if deal.get("stage", 1) < 3:
            deal["stage"] = 3
            deal["stage_label"] = "เจรจาต่อรอง"
        for v in deal.get("vendors", []):
            vid = str(v.get("id") or "").lower().replace('_', ' ').strip()
            vname = str(v.get("name") or "").lower().replace('_', ' ').strip()
            target = str(vendor_identifier).lower().replace('_', ' ').strip()
            if vid == target or target in vid or target in vname or vid in target or (vname and vname in target):
                if price is not None and price > 0:
                    v["price"] = f"฿{float(price):,.2f}"
                if credit_days is not None and credit_days > 0:
                    v["credit"] = f"{int(credit_days)} วัน"
                if lead_time_days is not None and lead_time_days > 0:
                    v["leadTime"] = f"{int(lead_time_days)} วันทำการ"
                if status:
                    v["status"] = status
                    v["statusBadge"] = "badge-primary text-white font-bold"
        return True

deal_repository = DealRepository()
