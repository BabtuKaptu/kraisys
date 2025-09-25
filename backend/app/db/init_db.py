"""Utility helpers to create the v0.6 database schema."""

from __future__ import annotations

import logging
from contextlib import suppress

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import settings
from app.models import Base


logger = logging.getLogger(__name__)


def _create_engine() -> Engine:
    """Create a synchronous SQLAlchemy engine for DDL actions."""

    engine = create_engine(
        settings.DATABASE_URL,
        future=True,
    )
    return engine


def init_db() -> None:
    """Create all tables declared on the SQLAlchemy metadata.

    The call is idempotent thanks to ``checkfirst=True``.
    """

    engine = _create_engine()
    logger.info("Creating database schema if missing")
    Base.metadata.create_all(bind=engine, checkfirst=True)
    with suppress(Exception):
        # Warm up the connection pool; helpful to fail fast if the URL is wrong
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    logger.info("Database schema ensured")


def main() -> None:
    """Entry-point used by CLI/automation scripts."""

    logging.basicConfig(level=logging.INFO)
    try:
        init_db()
        logger.info("✅ Database initialisation completed")
    except Exception:  # pragma: no cover - CLI feedback only
        logger.exception("❌ Database initialisation failed")
        raise


if __name__ == "__main__":  # pragma: no cover - manual execution only
    main()
