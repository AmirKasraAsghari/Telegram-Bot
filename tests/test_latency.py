import asyncio
from statistics import mean

from aiogram import Bot, types
from aiogram.test_utils import TestDispatcher

from hyperliquid_bot.bot.commands import setup_bot
from hyperliquid_bot.bot.middleware import ExecutionTimeMiddleware


def set_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("REDIS_URL", "redis://")


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
