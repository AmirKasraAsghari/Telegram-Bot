"""FastAPI service for leaderboard and sentiment endpoints.

This application exposes minimal REST endpoints for the Telegram bot and
related services. Additional routers (e.g. sentiment) are included here.
"""

from __future__ import annotations

import json
from urllib.request import urlopen

from fastapi import FastAPI, HTTPException, Request, Response

from ..bot.config import load_deny_countries
from ..sentiment.api import router as sentiment_router
from .metrics import render_metrics

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


@app.post("/approve/callback")
async def approve_callback(request: Request, ip: str | None = None) -> dict[str, str]:
    """Handle builder-fee approval callback with geofence check."""

    client_ip = request.headers.get("X-Forwarded-For", ip)
    country = ""
    if client_ip:
        try:
            with urlopen(f"https://ipapi.co/{client_ip}/json") as fh:  # nosec - test controlled
                data = json.loads(fh.read().decode("utf-8"))
                country = data.get("country", "")
        except Exception:
            country = ""
    deny = set(load_deny_countries())
    if country.upper() in deny:
        raise HTTPException(status_code=403, detail="Trading not available in your jurisdiction.")
    return {"status": "ok", "country": country}


@app.get("/metrics")
async def metrics() -> Response:
    """Expose Prometheus-style metrics."""

    return Response(render_metrics(), media_type="text/plain")
