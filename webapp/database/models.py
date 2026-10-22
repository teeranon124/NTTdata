"""
SQLAlchemy ORM models for AutoProcure.AI.

Design notes
------------
- Models are fully relational (Deal 1-*-Vendor, Deal 1-*-PurchaseRequest,
  Deal 1-*-NegotiationSession 1-*-MessageLog / AuditTrail).
- Each model exposes a `to_api_dict()` that reproduces the EXACT legacy JSON
  shape the existing frontend consumes (key names, string-formatted prices,
  deal-keyed object for /api/deals), guaranteeing backward compatibility.
- Vendor and PurchaseRequest preserve their original raw dict in a JSON column
  (`raw` / `extra`) so serialization is byte-compatible regardless of which
  optional fields a given record carried, while key business columns remain
  first-class and queryable.
"""
import time

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from .engine import Base

# Canonical field order for a deal object in the legacy API (keeps output stable).
_DEAL_FIELD_ORDER = [
    "id", "deal_code", "sku", "name", "category", "category_th",
    "stage", "stage_label", "stock_alert", "stock_type", "unit",
    "qty", "prs_count", "pre_price", "post_price", "pre_spend",
    "post_spend", "savings", "savings_pct", "supplier",
]

# Canonical vendor field order (optional fields included only if present in raw).
_VENDOR_FIELD_ORDER = [
    "id", "name", "price", "credit", "leadTime", "warranty",
    "cert", "status", "statusBadge", "outcome",
]


class Deal(Base):
    __tablename__ = "deals"

    # deal_id slug ("nsk", "skf", ...) is the natural primary key.
    id = Column(String(64), primary_key=True)
    deal_code = Column(String(128))
    sku = Column(String(128), index=True)
    name = Column(Text)
    category = Column(String(64), index=True)
    category_th = Column(String(128))
    stage = Column(Integer, index=True, default=1)
    stage_label = Column(String(128))
    stock_alert = Column(String(255))
    stock_type = Column(String(64))
    unit = Column(String(32))
    qty = Column(Integer, default=0)
    prs_count = Column(Integer, default=0)
    pre_price = Column(Float, default=0.0)
    post_price = Column(Float, default=0.0)
    pre_spend = Column(Float, default=0.0)
    post_spend = Column(Float, default=0.0)
    savings = Column(Float, default=0.0)
    savings_pct = Column(Float, default=0.0)
    supplier = Column(Text)

    vendors = relationship(
        "Vendor", back_populates="deal", cascade="all, delete-orphan",
        order_by="Vendor.position",
    )
    purchase_requests = relationship(
        "PurchaseRequest", back_populates="deal", cascade="all, delete-orphan",
    )
    sessions = relationship(
        "NegotiationSession", back_populates="deal", cascade="all, delete-orphan",
    )

    def to_api_dict(self) -> dict:
        """Reproduce the legacy master_deals.json deal object exactly."""
        out = {}
        for key in _DEAL_FIELD_ORDER:
            out[key] = getattr(self, key)
        out["vendors"] = [v.to_api_dict() for v in self.vendors]
        return out


class Vendor(Base):
    __tablename__ = "vendors"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    deal_id = Column(String(64), ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    position = Column(Integer, default=0)  # preserves vendor ordering within a deal

    vendor_id = Column(String(64), index=True)   # "sp", "eb", "tk", ...
    name = Column(Text)
    price = Column(String(64))     # pre-formatted string e.g. "฿398.00"
    credit = Column(String(64))    # e.g. "45 วัน"
    lead_time = Column(String(64))
    warranty = Column(String(128))
    cert = Column(String(128), nullable=True)
    status = Column(Text)
    status_badge = Column(Text)
    outcome = Column(Text)

    # Raw original dict (minus messages) to guarantee byte-identical serialization.
    raw = Column(JSON, default=dict)
    # Seed messages embedded in the vendor profile (array of message dicts).
    seed_messages = Column(JSON, default=list)

    deal = relationship("Deal", back_populates="vendors")

    def to_api_dict(self) -> dict:
        """Reproduce the legacy vendor object (field order + optional fields)."""
        raw = self.raw or {}
        out = {}
        for key in _VENDOR_FIELD_ORDER:
            if key in raw:
                out[key] = raw[key]
        # Fall back to columns for any canonical field missing from raw.
        out.setdefault("id", self.vendor_id)
        out.setdefault("name", self.name)
        if self.seed_messages:
            out["messages"] = self.seed_messages
        return out


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    pr_id = Column(String(32), index=True)          # "PR-0001"
    deal_key = Column(String(64), index=True)        # slug used for filtering
    deal_id = Column(String(64), ForeignKey("deals.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_code = Column(String(128))                  # "DEAL-2026-..."
    pr = Column(String(32))                          # "PR-2025-0001"
    date = Column(String(16))
    plant = Column(Text)
    plant_code = Column(String(64), index=True)
    code = Column(String(128), index=True)           # part code
    name = Column(Text)
    cat = Column(String(128))
    cat_key = Column(String(64), index=True)
    qty = Column(Integer, default=0)
    unit = Column(String(32))
    mode = Column(String(64))
    sup_pre = Column(Text)
    pre_p = Column(Float, default=0.0)
    pre_tot = Column(Float, default=0.0)
    cred_pre = Column(Integer, default=0)
    sup_post = Column(Text)
    post_p = Column(Float, default=0.0)
    post_tot = Column(Float, default=0.0)
    cred_post = Column(Integer, default=0)
    vol_sav = Column(Float, default=0.0)
    batna_sav = Column(Float, default=0.0)
    cred_sav = Column(Float, default=0.0)
    tco_sav = Column(Float, default=0.0)
    tco_pct = Column(Float, default=0.0)
    rounds = Column(Integer, default=0)
    aws = Column(Float, default=0.0)

    # Full original record for byte-compatible transaction serialization.
    raw = Column(JSON, default=dict)

    deal = relationship("Deal", back_populates="purchase_requests")

    def to_api_dict(self) -> dict:
        return dict(self.raw) if self.raw else {}


class NegotiationSession(Base):
    __tablename__ = "negotiation_sessions"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    deal_key = Column(String(64), index=True)
    vendor_key = Column(String(255), index=True)     # normalized vendor id/name slug
    deal_id = Column(String(64), ForeignKey("deals.id", ondelete="SET NULL"), nullable=True)

    status = Column(String(32), default="in_progress")
    created_at = Column(Float, default=lambda: time.time())
    updated_at = Column(Float, default=lambda: time.time())

    # Ladder is a list of display dicts; stored as JSON to match legacy shape.
    concession_ladder = Column(JSON, default=list)

    # HITL (Human-in-the-Loop) executive sign-off governance.
    signoff_status = Column(String(32), default="pending")   # pending | approved | rejected
    approved_by = Column(String(128), nullable=True)
    approved_at = Column(Float, nullable=True)
    po_number = Column(String(64), nullable=True)
    signoff_note = Column(Text, nullable=True)

    messages = relationship(
        "MessageLog", back_populates="session", cascade="all, delete-orphan",
        order_by="MessageLog.seq",
    )
    audit_entries = relationship(
        "AuditTrail", back_populates="session", cascade="all, delete-orphan",
        order_by="AuditTrail.seq",
    )

    deal = relationship("Deal", back_populates="sessions")

    def to_api_dict(self) -> dict:
        """
        Reproduce the legacy session dict exactly (keys the frontend reads), plus
        an additive `signoff` block for HITL governance. Legacy consumers ignore it.
        """
        return {
            "deal_id": self.deal_key,
            "vendor_id": self.vendor_key,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "concession_ladder": self.concession_ladder or [],
            "audit_traces": [a.to_api_dict() for a in self.audit_entries],
            "messages": [m.to_api_dict() for m in self.messages],
            "signoff": {
                "status": self.signoff_status or "pending",
                "approved_by": self.approved_by,
                "approved_at": self.approved_at,
                "po_number": self.po_number,
                "note": self.signoff_note,
            },
        }


class MessageLog(Base):
    __tablename__ = "message_logs"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    session_pk = Column(Integer, ForeignKey("negotiation_sessions.pk", ondelete="CASCADE"), index=True)
    seq = Column(Integer, default=0)  # preserves message ordering

    sender = Column(String(32))       # "vendor" | "agent"
    name = Column(Text)
    time = Column(String(16))         # "HH:MM"
    text = Column(Text)
    tactic = Column(Text, nullable=True)

    # Production auditability metadata (Pillar 4).
    model_id = Column(String(128), nullable=True)
    latency_ms = Column(Float, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    tco_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("NegotiationSession", back_populates="messages")

    def to_api_dict(self) -> dict:
        """Legacy message shape: include 'tactic' only for agent messages that have it."""
        out = {
            "sender": self.sender,
            "name": self.name,
            "time": self.time,
            "text": self.text,
        }
        if self.sender == "agent":
            out["tactic"] = self.tactic
        elif self.tactic:
            out["tactic"] = self.tactic
        return out


class AuditTrail(Base):
    __tablename__ = "audit_trails"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    session_pk = Column(Integer, ForeignKey("negotiation_sessions.pk", ondelete="CASCADE"), index=True)
    seq = Column(Integer, default=0)

    timestamp = Column(Float, default=lambda: time.time())
    time = Column(String(16))
    # The step-by-step agent reasoning trace (list of {step, agent, thought, tool_call}).
    trace = Column(JSON, default=list)

    # Production auditability metadata (Pillar 4).
    model_id = Column(String(128), nullable=True)
    tier = Column(String(32), nullable=True)          # "light" | "heavy"
    status = Column(String(32), nullable=True)        # "live_aws" | "fallback"
    latency_ms = Column(Float, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    tco_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("NegotiationSession", back_populates="audit_entries")

    def to_api_dict(self) -> dict:
        """
        Legacy audit_traces entry shape, plus additive telemetry so governance
        dashboards can read model/cost metadata. Legacy consumers read only
        timestamp/time/trace and ignore the rest.
        """
        return {
            "timestamp": self.timestamp,
            "time": self.time,
            "trace": self.trace or [],
            "model_id": self.model_id,
            "tier": self.tier,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "tco_score": self.tco_score,
        }
