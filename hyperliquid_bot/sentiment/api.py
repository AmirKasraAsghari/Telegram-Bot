"""FastAPI router exposing sentiment data."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from hyperliquid_bot.bot.db import get_engine
from .models import PairSentiment

engine = get_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

router = APIRouter()


@router.get("/sentiment/{pair}")
async def get_sentiment(pair: str) -> dict:
    """Return latest sentiment for ``pair``."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(PairSentiment).where(PairSentiment.pair == pair).order_by(PairSentiment.ts.desc())
        )
        row = result.scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail="pair not found")
        return {"pair": row.pair, "score": row.score, "summary": row.summary}
