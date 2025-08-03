"""Database utilities for storing user and referral information.

This module uses SQLAlchemy's asynchronous API to create a connection pool
and provides basic models. Tests and the bot may choose to mock out the
database layer if necessary. In production, a PostgreSQL database should be
used; for unit tests, SQLite with aiosqlite is sufficient.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import declarative_base

from .config import Settings


Base = declarative_base()


def get_engine(settings: Optional[Settings] = None) -> AsyncEngine:
    """Create an asynchronous SQLAlchemy engine.

    Parameters
    ----------
    settings: Optional[Settings]
        Optional settings instance. If omitted, loaded automatically.

    Returns
    -------
    AsyncEngine
        SQLAlchemy engine configured for asynchronous use.
    """
    s = settings or Settings()
    return create_async_engine(s.database_url, echo=False, future=True)
