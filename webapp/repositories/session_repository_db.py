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
                        latency_ms=a.get("latency_ms"),
                        input_tokens=a.get("input_tokens"),
                        output_tokens=a.get("output_tokens"),
                        tco_score=a.get("tco_score"),
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


session_repository_db = SessionRepositoryDB()
