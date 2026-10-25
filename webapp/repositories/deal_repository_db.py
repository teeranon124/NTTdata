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

            stages_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            stages_prs = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
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
                # Check for exact deal_key match first to avoid partial collision (e.g. festo_cyl vs festo_cylinder)
                exact_count = s.query(PurchaseRequest).filter(func.lower(PurchaseRequest.deal_key) == did).count()
                if exact_count > 0:
                    q = s.query(PurchaseRequest).filter(func.lower(PurchaseRequest.deal_key) == did)
                else:
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

    def mark_deal_awarded(self, deal_id: str, vendor_id: str, agreed_price=None) -> bool:
        """
        Closed-loop transition: a negotiation was agreed -> move the deal to
        Stage 4 (รออนุมัติ PO) and record the winning vendor + agreed price.
        Idempotent; returns True if the deal exists.
        """
        with session_scope() as s:
            d = s.get(Deal, (deal_id or "").lower())
            if not d:
                return False
            d.stage = 4
            d.stage_label = "รอลงนาม PO"
            d.winning_vendor_id = vendor_id
            if agreed_price is not None:
                d.agreed_price = float(agreed_price)
            if d.po_status not in ("PO_CREATED",):
                d.po_status = "AWARDED"
            for v in getattr(d, 'vendors', []):
                vid = str(getattr(v, 'vendor_id', '') or '').lower()
                vname = str(getattr(v, 'name', '') or '').lower()
                target = str(vendor_id).lower()
                if vid == target or target in vid or target in vname or vid in target:
                    v.status = "ชนะการประมูล (ออกใบ PO)"
                    v.status_badge = "badge-success text-white font-bold"
                    if agreed_price is not None:
                        v.price = f"฿{float(agreed_price):,.2f}"
                else:
                    if not v.price or str(v.price).strip() in ("-", ""):
                        v.status = "รอเสนอราคา"
                        v.status_badge = "badge-ghost text-slate-400"
                    else:
                        v.status = "ไม่ได้รับเลือก (Outbid)"
                        v.status_badge = "badge-ghost text-slate-500"
            return True

    def create_po(self, deal_id: str, po_number: str) -> bool:
        """Record SAP PO creation on the deal (stage stays 4, po_status=PO_CREATED)."""
        with session_scope() as s:
            d = s.get(Deal, (deal_id or "").lower())
            if not d:
                return False
            d.po_number = po_number
            d.po_status = "PO_CREATED"
            d.stage = 5
            d.stage_label = "ออก PO สำเร็จ"
            return True


    def update_stage(self, deal_id: str, stage: int, stage_label: str = None) -> bool:
        with session_scope() as s:
            d = s.get(Deal, (deal_id or "").lower())
            if not d:
                return False
            d.stage = stage
            if stage_label:
                d.stage_label = stage_label
            elif stage == 1:
                d.stage_label = "รวมความต้องการ"
            elif stage == 2:
                d.stage_label = "ออกเทียบราคา"
            elif stage == 3:
                d.stage_label = "เจรจาต่อรอง"
            elif stage == 4:
                d.stage_label = "รอลงนาม PO"
            return True

    def update_vendor_terms(self, deal_id: str, vendor_identifier: str, price: float = None, credit_days: int = None, lead_time_days: int = None, status: str = None) -> bool:
        with session_scope() as s:
            d = s.get(Deal, (deal_id or "").lower())
            if not d:
                return False
            if d.stage < 3:
                d.stage = 3
                d.stage_label = "เจรจาต่อรอง"
            for v in getattr(d, 'vendors', []):
                vid = str(getattr(v, 'vendor_id', '') or '').lower().replace('_', ' ').strip()
                vname = str(getattr(v, 'name', '') or '').lower().replace('_', ' ').strip()
                target = str(vendor_identifier).lower().replace('_', ' ').strip()
                if vid == target or target in vid or target in vname or vid in target or (vname and vname in target):
                    if price is not None and price > 0:
                        v.price = f"฿{float(price):,.2f}"
                    if credit_days is not None and credit_days > 0:
                        v.credit = f"{int(credit_days)} วัน"
                    if lead_time_days is not None and lead_time_days > 0:
                        v.lead_time = f"{int(lead_time_days)} วันทำการ"
                    if status:
                        v.status = status
                        v.status_badge = "badge-primary text-white font-bold"
            return True

deal_repository_db = DealRepositoryDB()
