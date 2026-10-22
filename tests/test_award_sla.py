"""
Tests for multi-vendor Award Board, SLA/anti-stall monitor, and router
LLM+regex merge (deterministic, no AWS required).

Run: python tests/test_award_sla.py
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Force fallback mode (no AWS) so router uses the deterministic regex path.
os.environ.pop("AWS_ACCESS_KEY_ID", None)
os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
os.environ.pop("AWS_SESSION_TOKEN", None)
os.environ["USE_DATABASE"] = "true"

from webapp.agents.router_agent import parse_supplier_intent, _regex_parse  # noqa: E402
from webapp.services.negotiation_service import negotiation_service as svc  # noqa: E402
from webapp.repositories import session_repository as sr  # noqa: E402

DEAL = "nsk"


def _clean():
    if hasattr(sr, "clear_all_sessions"):
        sr.clear_all_sessions()


# ---- Router merge / credit regex ----
def test_credit_without_day_word():
    r = _regex_parse("เอา 398 เครดิต 45 ตกลงครับ")
    assert r["proposed_unit_price"] == 398.0
    assert r["proposed_credit_days"] == 45          # parsed even without "วัน"
    assert r["intent"] == "accept_terms"


def test_credit_with_day_word_still_works():
    r = _regex_parse("ขอเสนอ 420 เครดิต 60 วัน")
    assert r["proposed_unit_price"] == 420.0
    assert r["proposed_credit_days"] == 60


def test_credit_out_of_range_ignored():
    r = _regex_parse("เครดิต 999")
    assert r["proposed_credit_days"] is None        # 999 > 180 bound


# ---- Award board ----
def test_award_board_ranks_and_picks_winner():
    _clean()
    svc.negotiate(deal_key=DEAL, vendor_name="เจ้า เอ", latest_user_message="เสนอ 398 เครดิต 45 ตกลง")
    svc.negotiate(deal_key=DEAL, vendor_name="เจ้า บี", latest_user_message="ขอเสนอ 460 เครดิต 30")
    board = svc.get_award_board(DEAL)
    assert board["evaluated"] == 2
    # Ranked best-first; ranks are 1..n contiguous.
    assert [v["rank"] for v in board["vendors"]] == [1, 2]
    assert board["vendors"][0]["is_winner"] is True
    assert board["vendors"][0]["latest_tco_score"] >= board["vendors"][1]["latest_tco_score"]
    _clean()


def test_award_board_empty_deal():
    _clean()
    board = svc.get_award_board("zzz_no_such_deal")
    assert board["evaluated"] == 0 and board["winner"] is None


def test_consistency_guard_lower_price_not_ranked_below():
    """A cheaper offer with >= credit must never rank below a pricier one."""
    _clean()
    # Cheap vendor: ฿398 / 45 days ; Pricey vendor: ฿460 / 30 days.
    svc.negotiate(deal_key=DEAL, vendor_name="เจ้า ถูก", latest_user_message="เสนอ 398 เครดิต 45 ตกลง")
    svc.negotiate(deal_key=DEAL, vendor_name="เจ้า แพง", latest_user_message="เสนอ 460 เครดิต 30")

    # Simulate the LLM-scoring anomaly: force the pricey vendor's audit score ABOVE
    # the cheap vendor's, then confirm the guard corrects the final ranking.
    from webapp.database.engine import session_scope
    from webapp.database.models import NegotiationSession as N, AuditTrail as A
    with session_scope() as s:
        for row in s.query(N).filter(N.deal_key == DEAL).all():
            for a in row.audit_entries:
                if row.vendor_key.startswith("เจ้า_แพง") or "แพง" in row.vendor_key:
                    a.tco_score = 99.0
                    a.offered_price = 460.0
                    a.offered_credit = 30
                else:
                    a.tco_score = 50.0
                    a.offered_price = 398.0
                    a.offered_credit = 45

    board = svc.get_award_board(DEAL)
    by_vendor = {v["vendor_id"]: v for v in board["vendors"]}
    cheap = next(v for k, v in by_vendor.items() if "ถูก" in k)
    pricey = next(v for k, v in by_vendor.items() if "แพง" in k)
    # Guard must lift the cheaper (better) offer to at least the pricier score.
    assert cheap["latest_tco_score"] >= pricey["latest_tco_score"], (cheap, pricey)
    assert cheap["rank"] <= pricey["rank"]
    _clean()


# ---- SLA monitor ----
def test_sla_flags_stalled_session():
    _clean()
    svc.negotiate(deal_key=DEAL, vendor_name="เจ้า ช้า", latest_user_message="เสนอ 440 เครดิต 30")
    # Simulate a stall by pushing updated_at 72h into the past directly on the
    # persisted row (save_session always re-stamps updated_at, so we bypass it).
    old = time.time() - 72 * 3600
    from webapp.database.engine import session_scope
    from webapp.database.models import NegotiationSession as N
    with session_scope() as s:
        for row in s.query(N).filter(N.deal_key == DEAL).all():
            row.updated_at = old

    sla = svc.get_sla_status(DEAL)
    stalled = [s for s in sla["sessions"] if s["status"] == "stalled"]
    assert stalled, "expected at least one stalled session"
    assert stalled[0]["needs_followup"] is True
    assert stalled[0]["hours_idle"] >= 48
    _clean()


def test_sla_active_session_not_flagged():
    _clean()
    svc.negotiate(deal_key=DEAL, vendor_name="เจ้า สด", latest_user_message="เสนอ 440 เครดิต 30")
    sla = svc.get_sla_status(DEAL)
    assert sla["stalled_count"] == 0
    assert all(not s["needs_followup"] for s in sla["sessions"])
    _clean()


def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print(f"[PASS] {t.__name__}")
    print(f"\n{len(tests)}/{len(tests)} award/sla/router tests passed")


if __name__ == "__main__":
    try:
        _run_all()
    finally:
        _clean()
