"""
Database-backed SessionRepository.

Drop-in replacement for the JSON SessionRepository. Reproduces the legacy
session dict shape exactly (deal_id, vendor_id, status, created_at, updated_at,
concession_ladder, audit_traces, messages) and the same id-normalization so the
API/frontend behaves identically.
"""
import time
from typing import Optional

from ..database.engine import session_scope
from ..database.models import AuditTrail, MessageLog, NegotiationSession


def _normalize(deal_id: str, vendor_id: str):
    clean_deal = (deal_id or "").lower().replace("/", "_")
    clean_vendor = (vendor_id or "").lower().replace("/", "_").replace(" ", "_")
    return clean_deal, clean_vendor


def _default_session_dict(deal_key: str, vendor_key: str) -> dict:
    now = time.time()
    return {
        "deal_id": deal_key,
        "vendor_id": vendor_key,
        "status": "in_progress",
        "created_at": now,
        "updated_at": now,
        "concession_ladder": [],
        "audit_traces": [],
        "messages": [],
    }


class SessionRepositoryDB:
    def _get_row(self, s, deal_key: str, vendor_key: str) -> Optional[NegotiationSession]:
        return (
            s.query(NegotiationSession)
            .filter(NegotiationSession.deal_key == deal_key,
                    NegotiationSession.vendor_key == vendor_key)
            .one_or_none()
        )

    def load_session(self, deal_id: str, vendor_id: str) -> dict:
        deal_key, vendor_key = _normalize(deal_id, vendor_id)
        with session_scope() as s:
            row = self._get_row(s, deal_key, vendor_key)
            if row:
                return row.to_api_dict()
            # Legacy behavior: a missing session yields a fresh default dict
            # (not persisted until save_session is called).
            return _default_session_dict(deal_key, vendor_key)

    def save_session(self, deal_id: str, vendor_id: str, session_data: dict) -> bool:
        deal_key, vendor_key = _normalize(deal_id, vendor_id)
        session_data["updated_at"] = time.time()
        try:
            with session_scope() as s:
                row = self._get_row(s, deal_key, vendor_key)
                if not row:
                    row = NegotiationSession(
                        deal_key=deal_key,
                        vendor_key=vendor_key,
                        deal_id=deal_key,
                        created_at=session_data.get("created_at", time.time()),
                    )
                    s.add(row)
                    s.flush()

                row.status = session_data.get("status", "in_progress")
                row.updated_at = session_data["updated_at"]
                row.concession_ladder = session_data.get("concession_ladder", [])

                # Preserve any existing sign-off state carried in the dict.
                signoff = session_data.get("signoff") or {}
                if signoff:
                    row.signoff_status = signoff.get("status", row.signoff_status or "pending")
                    row.approved_by = signoff.get("approved_by", row.approved_by)
                    row.approved_at = signoff.get("approved_at", row.approved_at)
                    row.po_number = signoff.get("po_number", row.po_number)
                    row.signoff_note = signoff.get("note", row.signoff_note)

                # Replace messages + audit traces wholesale to mirror the
                # file-based "write the whole document" semantics.
                row.messages.clear()
                for i, m in enumerate(session_data.get("messages", [])):
                    row.messages.append(MessageLog(
                        seq=i,
                        sender=m.get("sender"),
                        name=m.get("name"),
                        time=m.get("time"),
                        text=m.get("text"),
                        tactic=m.get("tactic"),
                        model_id=m.get("model_id"),
                        latency_ms=m.get("latency_ms"),
                        input_tokens=m.get("input_tokens"),
                        output_tokens=m.get("output_tokens"),
                        tco_score=m.get("tco_score"),
                    ))

                row.audit_entries.clear()
                for i, a in enumerate(session_data.get("audit_traces", [])):
                    row.audit_entries.append(AuditTrail(
                        seq=i,
                        timestamp=a.get("timestamp", time.time()),
                        time=a.get("time"),
                        trace=a.get("trace", []),
                        model_id=a.get("model_id"),
                        tier=a.get("tier"),
                        status=a.get("status"),
                        latency_ms=a.get("latency_ms"),
                        input_tokens=a.get("input_tokens"),
                        output_tokens=a.get("output_tokens"),
                        tco_score=a.get("tco_score"),
                        offered_price=a.get("offered_price"),
                        offered_credit=a.get("offered_credit"),
                    ))
            return True
        except Exception as e:
            print(f"Error saving session {deal_key}/{vendor_key}: {e}")
            return False

    def append_message(self, deal_id: str, vendor_id: str, sender: str, name: str,
                       text: str, tactic: Optional[str] = None) -> dict:
        session = self.load_session(deal_id, vendor_id)
        msg = {
            "sender": sender,
            "name": name,
            "time": time.strftime("%H:%M"),
            "text": text,
            "tactic": tactic,
        }
        session["messages"].append(msg)
        self.save_session(deal_id, vendor_id, session)
        return msg

    # -- HITL governance / auditability (Phase D) --------------------------
    def list_sessions(self) -> list:
        """Lightweight index of all persisted sessions for the governance view."""
        with session_scope() as s:
            rows = s.query(NegotiationSession).order_by(NegotiationSession.updated_at.desc()).all()
            out = []
            for r in rows:
                msg_count = len(r.messages)
                audit_count = len(r.audit_entries)
                out.append({
                    "deal_id": r.deal_key,
                    "vendor_id": r.vendor_key,
                    "status": r.status,
                    "updated_at": r.updated_at,
                    "messages": msg_count,
                    "audit_entries": audit_count,
                    "deal_key": r.deal_key,
                    "vendor_name": r.vendor_key,
                    "signoff_status": r.signoff_status or "pending",
                    "decision": r.signoff_status or "pending",
                    "signed_off": (r.signoff_status or "pending") in ("approved", "rejected"),
                    "po_number": r.po_number,
                })
            return out

    def get_audit_trail(self, deal_id: str, vendor_id: str) -> dict:
        """
        Return the full audit trail for a session plus a cost/latency rollup
        across all model invocations (for the Cloud Cost comparison table).
        """
        deal_key, vendor_key = _normalize(deal_id, vendor_id)
        with session_scope() as s:
            row = self._get_row(s, deal_key, vendor_key)
            if not row:
                return {
                    "deal_id": deal_key, "vendor_id": vendor_key,
                    "found": False, "audit_traces": [], "rollup": {},
                }
            traces = [a.to_api_dict() for a in row.audit_entries]
            total_in = sum((a.input_tokens or 0) for a in row.audit_entries)
            total_out = sum((a.output_tokens or 0) for a in row.audit_entries)
            latencies = [a.latency_ms for a in row.audit_entries if a.latency_ms is not None]
            tco_scores = [a.tco_score for a in row.audit_entries if a.tco_score is not None]
            models = sorted({a.model_id for a in row.audit_entries if a.model_id})
            rollup = {
                "turns": len(traces),
                "total_input_tokens": total_in,
                "total_output_tokens": total_out,
                "total_tokens": total_in + total_out,
                "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else None,
                "latest_tco_score": tco_scores[-1] if tco_scores else None,
                "models_used": models,
            }
            return {
                "deal_id": deal_key, "vendor_id": vendor_key, "found": True,
                "signoff": row.to_api_dict()["signoff"],
                "audit_traces": traces, "rollup": rollup,
            }

    def sign_off(self, deal_id: str, vendor_id: str, approved_by: str,
                 decision: str = "approved", po_number: Optional[str] = None,
                 note: Optional[str] = None) -> dict:
        """Record an executive HITL sign-off decision on a negotiation session."""
        deal_key, vendor_key = _normalize(deal_id, vendor_id)
        decision = (decision or "approved").lower()
        if decision not in ("approved", "rejected"):
            decision = "approved"
        with session_scope() as s:
            row = self._get_row(s, deal_key, vendor_key)
            if not row:
                row = NegotiationSession(deal_key=deal_key, vendor_key=vendor_key, deal_id=deal_key)
                s.add(row)
                s.flush()
            row.signoff_status = decision
            row.approved_by = approved_by
            row.approved_at = time.time()
            row.po_number = po_number
            row.signoff_note = note
            row.updated_at = time.time()
            result = row.to_api_dict()["signoff"]
        return {"deal_id": deal_key, "vendor_id": vendor_key, "signed_off": True, "decision": decision, **result}

    # -- Data hygiene: separate transient sessions from permanent seed data ---
    def delete_session(self, deal_id: str, vendor_id: str) -> bool:
        """Delete one negotiation session (messages/audit cascade)."""
        deal_key, vendor_key = _normalize(deal_id, vendor_id)
        with session_scope() as s:
            n = (s.query(NegotiationSession)
                 .filter(NegotiationSession.deal_key == deal_key,
                         NegotiationSession.vendor_key == vendor_key)
                 .delete())
        return bool(n)

    def clear_all_sessions(self) -> int:
        """
        Delete ALL negotiation sessions (messages + audit trails cascade) while
        leaving the seed catalog (deals / vendors / purchase_requests) intact.
        Gives a clean slate before a demo without destroying the 60 deals / 2,500 PRs.
        """
        from sqlalchemy import text
        with session_scope() as s:
            s.execute(text("DELETE FROM audit_trails"))
            s.execute(text("DELETE FROM message_logs"))
            count = s.execute(text("DELETE FROM negotiation_sessions")).rowcount
        return count


session_repository_db = SessionRepositoryDB()
