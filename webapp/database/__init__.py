"""
Enterprise database layer for AutoProcure.AI.

Exposes the SQLAlchemy engine/session factory, the declarative Base, and the
ORM models. Supports zero-config SQLite (default) and PostgreSQL on AWS RDS,
selected at runtime via the DATABASE_URL environment variable.
"""
from .engine import (
    Base,
    DATABASE_URL,
    engine,
    get_session,
    init_db,
    session_scope,
)
from .models import (
    AuditTrail,
    Deal,
    MessageLog,
    NegotiationSession,
    PurchaseRequest,
    Vendor,
)

__all__ = [
    "Base",
    "DATABASE_URL",
    "engine",
    "get_session",
    "init_db",
    "session_scope",
    "Deal",
    "Vendor",
    "PurchaseRequest",
    "NegotiationSession",
    "MessageLog",
    "AuditTrail",
]
