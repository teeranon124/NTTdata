"""
Database-backed DealRepository.

Drop-in replacement for the JSON DealRepository. Every method returns data in
the EXACT legacy shape (deal-keyed object for get_all_deals, string-formatted
vendor prices, same statistics keys) so the existing API/frontend is unchanged.
"""
from typing import Dict, List, Optional

from sqlalchemy import func

from ..database.engine import session_scope
from ..database.models import Deal, PurchaseRequest


class DealRepositoryDB:
    def get_all_deals(self) -> Dict[str, dict]:
        with session_scope() as s:
            deals = s.query(Deal).all()
            # dict keyed by deal_id — must match legacy /api/deals shape.
            return {d.id: d.to_api_dict() for d in deals}

    def get_deal(self, deal_id: str) -> Optional[dict]:
        with session_scope() as s:
            d = s.get(Deal, deal_id.lower())
            return d.to_api_dict() if d else None

    def get_statistics(self) -> dict:
        with session_scope() as s:
            deals = s.query(Deal).all()
            total_spend = sum((d.pre_spend or 0.0) for d in deals)
            total_savings = sum((d.savings or 0.0) for d in deals)
            total_prs = sum((d.prs_count or 0) for d in deals)
            total_qty = sum((d.qty or 0) for d in deals)

            stages_count = {1: 0, 2: 0, 3: 0, 4: 0}
            stages_prs = {1: 0, 2: 0, 3: 0, 4: 0}
            for d in deals:
                st = d.stage or 1
                stages_count[st] = stages_count.get(st, 0) + 1
                stages_prs[st] = stages_prs.get(st, 0) + (d.prs_count or 0)

            return {
                "total_spend_thb": round(total_spend, 2),
                "total_savings_thb": round(total_savings, 2),
                "savings_pct": round((total_savings / total_spend) * 100, 1) if total_spend else 0.0,
                "total_prs": total_prs,
                "total_quantity": total_qty,
                "total_deals": len(deals),
                "stages_count": stages_count,
                "stages_prs": stages_prs,
            }

    def get_raw_transactions(self, deal_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[dict]:
        with session_scope() as s:
            q = s.query(PurchaseRequest)
            if deal_id:
                did = deal_id.lower()
                # Match legacy filter semantics: deal_key / code / deal_code.
                like = f"%{did}%"
                code_like = f"%{deal_id.upper()}%"
                q = q.filter(
                    (func.lower(PurchaseRequest.deal_key) == did)
                    | (PurchaseRequest.deal_key.ilike(like))
                    | (PurchaseRequest.code.ilike(code_like))
                    | (PurchaseRequest.deal_code.ilike(code_like))
                )
            q = q.order_by(PurchaseRequest.pk).offset(offset).limit(limit)
            return [r.to_api_dict() for r in q.all()]


deal_repository_db = DealRepositoryDB()
