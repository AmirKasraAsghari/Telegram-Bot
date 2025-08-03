"""FastAPI service for leaderboard and sentiment endpoints.

This application exposes minimal REST endpoints for the Telegram bot and
related services. Additional routers (e.g. sentiment) are included here.
"""

from __future__ import annotations

from fastapi import FastAPI

from ..sentiment.api import router as sentiment_router

app = FastAPI(title="Hyperliquid Trading Companion API")


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/leaderboard")
async def leaderboard() -> list[dict[str, str]]:
    """Return a mock leaderboard.

    A real implementation would query the database for user volumes and
    referral points, sort users and return the top N. Here we return a
    placeholder list for demonstration and testing purposes.
    """
    return [
        {"user": "alice", "volume": "10000", "points": "100"},
        {"user": "bob", "volume": "7500", "points": "75"},
    ]


# Include sentiment router
app.include_router(sentiment_router)
