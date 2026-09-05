"""
Database connection module.
Uses SQLAlchemy with PostgreSQL (production) or SQLite (local dev fallback).
Reads DATABASE_URL from environment.
"""

import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to SQLite for local development if no PostgreSQL URL is set
if not DATABASE_URL:
    _db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "sportslot.db")
    _db_path = os.path.abspath(_db_path)
    DATABASE_URL = f"sqlite:///{_db_path}"
    logger.warning(f"DATABASE_URL not set — using SQLite fallback: {DATABASE_URL}")

# SQLite-specific adjustments
_is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "pool_pre_ping": True,
}
if not _is_sqlite:
    engine_kwargs.update({"pool_size": 10, "max_overflow": 20})

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Enable WAL mode and foreign keys for SQLite
if _is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
