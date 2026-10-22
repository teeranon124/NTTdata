"""
Repository factory.

Selects the storage backend at import time via the USE_DATABASE env flag:
  - USE_DATABASE unset/false -> legacy JSON-file repositories (default, zero-config)
  - USE_DATABASE=true        -> SQLAlchemy ORM repositories (SQLite/PostgreSQL)

Both backends expose an identical interface and produce byte-compatible API
output, so call sites never change.
"""
import os

from .deal_repository import DealRepository, deal_repository as _deal_repo_json
from .session_repository import SessionRepository, session_repository as _session_repo_json


def _use_database() -> bool:
    return os.environ.get("USE_DATABASE", "false").strip().lower() in ("1", "true", "yes")


if _use_database():
    from .deal_repository_db import deal_repository_db as deal_repository
    from .session_repository_db import session_repository_db as session_repository
    STORAGE_BACKEND = "database"
else:
    deal_repository = _deal_repo_json
    session_repository = _session_repo_json
    STORAGE_BACKEND = "json"

__all__ = [
    "deal_repository",
    "session_repository",
    "DealRepository",
    "SessionRepository",
    "STORAGE_BACKEND",
]
