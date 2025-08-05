"""Database utilities for storing user and referral information.

This module uses SQLAlchemy's asynchronous API to create a connection pool
and provides basic models. Tests and the bot may choose to mock out the
database layer if necessary. In production, a PostgreSQL database should be
used; for unit tests, SQLite with aiosqlite is sufficient.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, Float, ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, relationship

from .config import Settings


Base = declarative_base()


class User(Base):
    """Database model representing a Telegram user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    country = Column(String, nullable=True)
    trades = relationship("Trade", back_populates="user")


class Trade(Base):
    """Model representing a confirmed trade."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String)
    side = Column(String)
    size = Column(Float)
    user = relationship("User", back_populates="trades")


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


def get_sessionmaker(settings: Optional[Settings] = None) -> async_sessionmaker[AsyncSession]:
    """Return an async session factory bound to the engine."""

    engine = get_engine(settings)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_or_create_user(session: AsyncSession, telegram_id: int) -> User:
    """Fetch a user by Telegram ID, creating one if missing."""

    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.flush()
    return user
