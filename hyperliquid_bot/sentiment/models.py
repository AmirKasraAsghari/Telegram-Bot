"""Database model for sentiment scores."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Float, Integer, String

from hyperliquid_bot.bot.db import Base


class PairSentiment(Base):
    """Stored sentiment score for a trading pair."""

    __tablename__ = "pair_sentiment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pair: Mapped[str] = mapped_column(String, index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    score: Mapped[float] = mapped_column(Float)
    summary: Mapped[str] = mapped_column(String(120))
