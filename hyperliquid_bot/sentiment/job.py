"""Sentiment aggregation job."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy.ext.asyncio import async_sessionmaker

from hyperliquid_bot.bot.db import get_engine, Base
from .models import PairSentiment

_positive = {"moon", "up", "bull", "bullish", "pump", "long"}
_negative = {"down", "bear", "bearish", "dump", "short"}


async def _fetch_texts(pair: str) -> list[str]:
    """Dummy fetcher returning placeholder lines."""
    return [f"{pair} to the moon", f"I am long {pair}"]


def _score(texts: list[str]) -> float:
    score = 0
    for t in texts:
        tl = t.lower()
        score += sum(word in tl for word in _positive)
        score -= sum(word in tl for word in _negative)
    return max(-1.0, min(1.0, score / max(len(texts), 1)))


async def run_sentiment_job(pairs: Iterable[str]) -> None:
    """Compute sentiment for ``pairs`` and store in the database."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        for pair in pairs:
            texts = await _fetch_texts(pair)
            score = _score(texts)
            summary = "Bullish" if score > 0 else "Bearish" if score < 0 else "Neutral"
            session.add(PairSentiment(pair=pair, score=score, summary=summary))
        await session.commit()
