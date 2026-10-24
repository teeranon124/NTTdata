"""
Seed Data Loader — migrates the legacy JSON datasets into the ORM database.

Sources:
  - webapp/data/master_deals.json  -> Deal + Vendor rows (60 deals)
  - dataset_2500.json (repo root)  -> PurchaseRequest rows (2,500 PRs)

Idempotent: by default it only seeds an empty database. Use --force to wipe and
reload. Run as a module:  python -m webapp.database.seed_loader [--force]
"""
import argparse
import json
import logging
import os

from .engine import init_db, seed_lock, session_scope
from .models import Deal, PurchaseRequest, Vendor

logger = logging.getLogger(__name__)

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_MASTER_DEALS = os.path.join(_DATA_DIR, "master_deals.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_DATASET_2500 = os.path.join(_ROOT, "dataset_2500.json")

_DEAL_SCALAR_FIELDS = [
    "deal_code", "sku", "name", "category", "category_th", "stage",
    "stage_label", "stock_alert", "stock_type", "unit", "qty", "prs_count",
    "pre_price", "post_price", "pre_spend", "post_spend", "savings",
    "savings_pct", "supplier", "po_number", "po_status",
]

_PR_SCALAR_FIELDS = [
    "deal_key", "date", "plant", "plant_code", "code", "name", "cat",
    "cat_key", "qty", "unit", "mode", "sup_pre", "pre_p", "pre_tot",
    "cred_pre", "sup_post", "post_p", "post_tot", "cred_post", "vol_sav",
    "batna_sav", "cred_sav", "tco_sav", "tco_pct", "rounds", "aws",
]


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_deal(deal_id: str, data: dict) -> Deal:
    deal = Deal(id=deal_id)
    for field in _DEAL_SCALAR_FIELDS:
        if field in data:
            setattr(deal, field, data[field])

    for pos, v in enumerate(data.get("vendors", [])):
        # Separate embedded seed messages from the byte-compatible raw vendor dict.
        raw = {k: val for k, val in v.items() if k != "messages"}
        vendor = Vendor(
            position=pos,
            vendor_id=v.get("id"),
            name=v.get("name"),
            email=v.get("email"),
            price=v.get("price"),
            credit=v.get("credit"),
            lead_time=v.get("leadTime"),
            warranty=v.get("warranty"),
            cert=v.get("cert"),
            status=v.get("status"),
            status_badge=v.get("statusBadge"),
            outcome=v.get("outcome"),
            raw=raw,
            seed_messages=v.get("messages", []),
        )
        deal.vendors.append(vendor)
    return deal


def _build_pr(rec: dict, valid_deal_ids: set) -> PurchaseRequest:
    pr = PurchaseRequest(
        pr_id=rec.get("id"),
        deal_code=rec.get("deal"),
        pr=rec.get("pr"),
        raw=rec,
    )
    for field in _PR_SCALAR_FIELDS:
        if field in rec:
            setattr(pr, field, rec[field])
    dk = (rec.get("deal_key") or "").lower()
    if dk in valid_deal_ids:
        pr.deal_id = dk
    return pr


def seed(force: bool = False) -> dict:
    """
    Load deals + PRs into the database.
    Returns a summary dict: {deals, vendors, prs, skipped}.
    """
    init_db()

    # Serialize across workers so only one process seeds an empty DB.
    with seed_lock(), session_scope() as s:
        existing_deals = s.query(Deal).count()
        if existing_deals and not force:
            logger.info("Database already seeded (%d deals) — skipping. Use force=True to reload.", existing_deals)
            return {"deals": existing_deals, "skipped": True}

        if force:
            # Order matters only loosely thanks to cascades, but clear children first.
            s.query(PurchaseRequest).delete()
            s.query(Vendor).delete()
            s.query(Deal).delete()
            s.flush()

        deals_data = _load_json(_MASTER_DEALS)
        valid_ids = {k.lower() for k in deals_data.keys()}

        vendor_count = 0
        for deal_id, data in deals_data.items():
            deal = _build_deal(deal_id.lower(), data)
            vendor_count += len(deal.vendors)
            s.add(deal)
        s.flush()

        pr_data = _load_json(_DATASET_2500) if os.path.exists(_DATASET_2500) else []
        for rec in pr_data:
            s.add(_build_pr(rec, valid_ids))

        summary = {
            "deals": len(deals_data),
            "vendors": vendor_count,
            "prs": len(pr_data),
            "skipped": False,
        }

    logger.info("Seed complete: %s", summary)
    return summary


def reset_sessions() -> int:
    """
    Clear all transient negotiation sessions (messages + audit trails) while
    keeping the seed catalog intact. Returns the number of sessions removed.
    Clean-slate helper for demo preparation.
    """
    init_db()
    from .models import NegotiationSession

    with session_scope() as s:
        count = s.query(NegotiationSession).count()
        s.query(NegotiationSession).delete()
    logger.info("Cleared %d negotiation sessions (seed catalog kept).", count)
    return count


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Seed / maintain the AutoProcure.AI database.")
    parser.add_argument("--force", action="store_true", help="Wipe and reload all data (deals + PRs).")
    parser.add_argument("--reset-sessions", action="store_true",
                        help="Clear all negotiation sessions but KEEP seed data (demo clean slate).")
    args = parser.parse_args()

    if args.reset_sessions:
        n = reset_sessions()
        print(f"Sessions cleared: {n} (seed catalog kept)")
        return

    result = seed(force=args.force)
    print(f"Seed result: {result}")


if __name__ == "__main__":
    main()
