"""
Database engine & session management.

Selects the backend from DATABASE_URL:
  - unset            -> SQLite file at webapp/data/autoprocure.db (zero-config)
  - sqlite:///...    -> SQLite (file or :memory:)
  - postgresql+psycopg2://user:pass@host:5432/db  -> PostgreSQL (AWS RDS)

Normalizes the common 'postgres://' scheme (as emitted by some managed
providers) to the SQLAlchemy-compatible 'postgresql+psycopg2://'.
"""
import contextlib
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_DEFAULT_SQLITE_PATH = os.path.join(_DATA_DIR, "autoprocure.db")


def _resolve_database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        os.makedirs(_DATA_DIR, exist_ok=True)
        return f"sqlite:///{_DEFAULT_SQLITE_PATH}"
    # Managed providers (Heroku/RDS copy-paste) sometimes use the bare scheme.
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


DATABASE_URL = _resolve_database_url()


def _make_engine():
    kwargs = {"future": True, "pool_pre_ping": True}
    if DATABASE_URL.startswith("sqlite"):
        # Allow use across Flask's threaded dev server / SSE threads.
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # Sensible pool defaults for RDS; override via env if needed.
        kwargs["pool_size"] = int(os.environ.get("DB_POOL_SIZE", "5"))
        kwargs["max_overflow"] = int(os.environ.get("DB_MAX_OVERFLOW", "10"))
        kwargs["pool_recycle"] = int(os.environ.get("DB_POOL_RECYCLE", "1800"))
    return create_engine(DATABASE_URL, **kwargs)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def init_db():
    """Create all tables if they do not exist. Idempotent."""
    # Import models so they register on Base.metadata before create_all.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized at %s", _redacted_url())


def get_session():
    """Return a new session. Caller is responsible for closing it."""
    return SessionLocal()


@contextlib.contextmanager
def session_scope():
    """Transactional scope: commits on success, rolls back on error, always closes."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _redacted_url() -> str:
    """URL with any password masked, safe for logs."""
    url = DATABASE_URL
    if "@" in url and "://" in url:
        scheme, rest = url.split("://", 1)
        if "@" in rest:
            creds, host = rest.split("@", 1)
            user = creds.split(":", 1)[0]
            return f"{scheme}://{user}:***@{host}"
    return url
