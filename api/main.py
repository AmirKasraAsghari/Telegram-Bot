"""FastAPI service for leaderboard and other REST endpoints.

The API exposes endpoints used by the Telegram bot and external clients.
These include leaderboards, referral management and health checks.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

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
    # Placeholder data
    return [
        {"user": "alice", "volume": "10000", "points": "100"},
        {"user": "bob", "volume": "7500", "points": "75"},
    ]