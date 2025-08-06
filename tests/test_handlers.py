import asyncio
from hyperliquid_bot.bot.commands import (
    buy_sell_handler,
    cancel_handler,
    positions_handler,
    start_handler,
)
from hyperliquid_bot.bot.middleware import ExecutionTimeMiddleware
from aiogram import types
from hyperliquid_bot.bot import hyperliquid


class DummyMessage(types.Message):
    """Message object capturing answers for testing."""

    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self.replies = []

    async def answer(self, text: str) -> None:  # type: ignore[override]
        self.replies.append(text)


def test_positions_handler_outputs_placeholder():
    msg = DummyMessage("/positions")
    asyncio.run(positions_handler(msg))
    assert msg.replies[-1].startswith("You currently have")


def test_cancel_handler_all():
    msg = DummyMessage("/cancel")
    asyncio.run(cancel_handler(msg))
    assert "Cancelled all" in msg.replies[-1]


def test_execution_time_middleware_records_time():
    middleware = ExecutionTimeMiddleware()

    async def dummy_handler(event: str, data: dict) -> str:
        await asyncio.sleep(0)
        return "ok"

    data: dict = {}
    result = asyncio.run(middleware(dummy_handler, "event", data))
    assert result == "ok"
    assert data["execution_time"] >= 0


def set_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("REDIS_URL", "redis://")
    hyperliquid.reset_breaker()


def test_start_handler(monkeypatch):
    set_env(monkeypatch)
    msg = DummyMessage("/start")
    asyncio.run(start_handler(msg, types.CommandObject()))
    assert "Welcome" in msg.replies[-1]


def test_buy_sell_handler_usage(monkeypatch):
    set_env(monkeypatch)
    msg = DummyMessage("/buy")
    asyncio.run(buy_sell_handler(msg, "buy"))
    assert msg.replies[-1].startswith("Usage")


def test_buy_sell_handler_invalid_size(monkeypatch):
    set_env(monkeypatch)
    msg = DummyMessage("/buy ETH notanumber")
    asyncio.run(buy_sell_handler(msg, "buy"))
    assert "Invalid size" in msg.replies[-1]


def test_buy_sell_handler_invalid_price(monkeypatch):
    set_env(monkeypatch)
    msg = DummyMessage("/buy ETH 1 two")
    asyncio.run(buy_sell_handler(msg, "buy"))
    assert "Invalid price" in msg.replies[-1]


def test_buy_sell_handler_invalid_leverage(monkeypatch):
    set_env(monkeypatch)
    msg = DummyMessage("/buy ETH 1 100 notint")
    asyncio.run(buy_sell_handler(msg, "buy"))
    assert "Invalid leverage" in msg.replies[-1]


def test_buy_sell_handler_success(monkeypatch):
    set_env(monkeypatch)
    msg = DummyMessage("/buy ETH 1 2 3")
    asyncio.run(buy_sell_handler(msg, "buy"))
    assert "Order preview" in msg.replies[-1]


def test_buy_sell_handler_paused(monkeypatch):
    set_env(monkeypatch)
    for _ in range(3):
        hyperliquid.record_api_error()
    msg = DummyMessage("/buy ETH 1 2 3")
    asyncio.run(buy_sell_handler(msg, "buy"))
    assert "paused" in msg.replies[-1].lower()

