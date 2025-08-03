"""Tests for sentiment endpoint."""

import asyncio
from fastapi.testclient import TestClient


def test_sentiment_endpoint(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./sentiment.db")
    monkeypatch.setenv("REDIS_URL", "redis://")
    from hyperliquid_bot.sentiment.job import run_sentiment_job
    from hyperliquid_bot.api.main import app

    asyncio.run(run_sentiment_job(["BTC-PERP"]))
    client = TestClient(app)
    resp = client.get("/sentiment/BTC-PERP")
    assert resp.status_code == 200
    data = resp.json()
    assert data["pair"] == "BTC-PERP"
    assert "score" in data and "summary" in data
