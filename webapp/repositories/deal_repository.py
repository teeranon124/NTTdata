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
        total_spend = sum(d['budget_total_thb'] for d in deals.values())
        total_savings = sum(d['total_savings_thb'] for d in deals.values())
        total_prs = sum(d['total_prs'] for d in deals.values())
        total_qty = sum(d['total_quantity'] for d in deals.values())

        stages_count = {1: 0, 2: 0, 3: 0, 4: 0}
        for d in deals.values():
            s = d.get('stage', 1)
            stages_count[s] = stages_count.get(s, 0) + 1

        return {
            'total_spend_thb': round(total_spend, 2),
            'total_savings_thb': round(total_savings, 2),
            'savings_pct': round((total_savings / total_spend) * 100, 1) if total_spend else 0.0,
            'total_prs': total_prs,
            'total_quantity': total_qty,
            'total_deals': len(deals),
            'stages_count': stages_count
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

        deal = self.get_deal(deal_id)
        if not deal:
            return []
        part_code = deal['part_code']
        filtered = [r for r in self._raw_cache if r.get('code') == part_code]
        return filtered[offset:offset+limit]

deal_repository = DealRepository()
