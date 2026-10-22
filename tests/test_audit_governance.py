"""
Unit tests for Phase D — audit metadata persistence + HITL governance.

Runs against BOTH backends (SQLite ORM and JSON file) to prove parity.
Run: python tests/test_audit_governance.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _reload_backend(use_db: bool):
    os.environ["USE_DATABASE"] = "true" if use_db else "false"
    for mod in list(sys.modules):
        if mod.startswith("webapp"):
            del sys.modules[mod]
    if use_db:
        from webapp.database.seed_loader import seed
        seed(force=False)
    import webapp.repositories as repos
    from webapp.services.negotiation_service import negotiation_service
    return repos.session_repository, repos.STORAGE_BACKEND, negotiation_service


def _exercise(session_repository, backend, negotiation_service):
    deal, vendor = "nsk", f"utest {backend}"

    # Negotiate -> persists messages + audit with telemetry metadata.
    res = negotiation_service.negotiate(deal_key=deal, vendor_name=vendor,
                                        latest_user_message="เสนอ 440 เครดิต 30 วัน")
    assert res["status"] == "success"
    assert {"reply", "tactic", "tco_data", "concession", "audit_trace", "messages", "ladder"}.issubset(res.keys())
    assert "arbitration" in res and "model_meta" in res

    # Agent message carries additive telemetry keys.
    agent_msgs = [m for m in res["messages"] if m.get("sender") == "agent"]
    assert agent_msgs, "expected an agent message"
    last = agent_msgs[-1]
    for k in ("model_id", "latency_ms", "input_tokens", "output_tokens", "tco_score"):
        assert k in last, f"agent message missing telemetry key {k}"

    # Audit trail + rollup.
    at = session_repository.get_audit_trail(deal, vendor)
    assert at["found"] is True
    assert at["rollup"]["turns"] >= 1
    assert at["rollup"]["models_used"], "expected at least one model recorded"
    assert "total_tokens" in at["rollup"]

    # Sign-off persists.
    so = session_repository.sign_off(deal, vendor, approved_by="CPO Test",
                                     decision="approved", po_number="PO-UTEST-01",
                                     note="Unit test sign-off")
    assert so["signed_off"] is True
    assert so["decision"] == "approved"
    assert so["po_number"] == "PO-UTEST-01"

    # Reflected in session index.
    sess_list = session_repository.list_sessions()
    vslug = vendor.lower().replace("/", "_").replace(" ", "_")
    matching = [s for s in sess_list if (s.get("deal_id") == deal or s.get("deal_key") == deal) and (s.get("vendor_id") == vslug or s.get("vendor_name") in (vendor, vslug))]
    assert matching, "expected session in list_sessions"
    assert matching[0]["signed_off"] is True
    assert matching[0]["decision"] == "approved"

    # Re-query audit trail reflects sign-off state.
    at2 = session_repository.get_audit_trail(deal, vendor)
    assert at2["signoff"]["signed_off"] is True
    assert at2["signoff"]["approved_by"] == "CPO Test"

    return deal, vendor


def _cleanup(backend, use_db, deal, vendor):
    if use_db:
        from webapp.database.engine import session_scope
        from webapp.database.models import NegotiationSession as N
        vkey = vendor.lower().replace("/", "_").replace(" ", "_")
        with session_scope() as s:
            s.query(N).filter(N.deal_key == deal, N.vendor_key == vkey).delete()
    else:
        vkey = vendor.lower().replace("/", "_").replace(" ", "_")
        p = os.path.join(ROOT, "webapp", "data", "sessions", f"{deal}_{vkey}.json")
        if os.path.exists(p):
            os.remove(p)


def test_database_backend():
    sr, backend, svc = _reload_backend(use_db=True)
    assert backend == "database"
    deal, vendor = _exercise(sr, backend, svc)
    _cleanup(backend, True, deal, vendor)


def test_json_backend():
    sr, backend, svc = _reload_backend(use_db=False)
    assert backend == "json"
    deal, vendor = _exercise(sr, backend, svc)
    _cleanup(backend, False, deal, vendor)


def _run_all():
    for name in ["test_database_backend", "test_json_backend"]:
        globals()[name]()
        print(f"[PASS] {name}")
    print("\n2/2 audit & governance tests passed (both backends)")


if __name__ == "__main__":
    _run_all()
