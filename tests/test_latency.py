import asyncio
from statistics import mean

from aiogram import Bot, types
from aiogram.test_utils import TestDispatcher

from hyperliquid_bot.bot.commands import setup_bot
from hyperliquid_bot.bot.middleware import ExecutionTimeMiddleware
from fastapi.testclient import TestClient
from hyperliquid_bot.api.main import app


def set_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("REDIS_URL", "redis://")
    monkeypatch.setenv("BUILDER_FEE_TENTH_BPS", "5")
    monkeypatch.setenv("TOKEN_BUDGET_MONTHLY", "200")
    monkeypatch.setenv("VOICE_ENABLED", "false")
    monkeypatch.setenv("DENY_COUNTRIES_URL", "")


def test_latency(monkeypatch):
    set_env(monkeypatch)

    async def run() -> list[float]:
        bot = Bot("t")
        dp = TestDispatcher()
        await setup_bot(bot, dp)
        dp.message.middleware(ExecutionTimeMiddleware())
        timings: list[float] = []
        for _ in range(20):
            msg = types.Message("/buy BTC-PERP 0.01")
            data = await dp.feed_update(msg)
            timings.append(data["execution_time"])
        return timings

    timings = asyncio.run(run())
    avg = mean(timings)
    p95 = sorted(timings)[int(len(timings) * 0.95) - 1]
    print(f"Average latency: {avg*1000:.2f} ms; p95 latency: {p95*1000:.2f} ms")
    assert p95 < 0.4


def test_metrics_endpoint_200():
    client = TestClient(app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "total_orders" in resp.text
    assert "latency_ms_bucket" in resp.text
