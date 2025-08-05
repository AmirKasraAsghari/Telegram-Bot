import asyncio
from hyperliquid_bot.bot.commands import (
    buy_sell_handler,
    cancel_handler,
    positions_handler,
    price_handler,
    start_handler,
    order_callback_handler,
)
from hyperliquid_bot.bot.middleware import ExecutionTimeMiddleware
from aiogram import types
from hyperliquid_bot.bot.db import get_engine, get_sessionmaker, Trade
from sqlalchemy import select


class DummyMessage(types.Message):
    """Message object capturing answers for testing."""

    def __init__(self, text: str = "", from_user: types.User | None = None) -> None:
        super().__init__(text, from_user)
        self.replies: list[str] = []
        self.markups = []

    async def answer(self, text: str, reply_markup=None) -> None:  # type: ignore[override]
        self.replies.append(text)
        self.markups.append(reply_markup)
        self.text = text

    async def edit_text(self, text: str) -> None:  # type: ignore[override]
        self.replies.append(text)
        self.text = text


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
    monkeypatch.setenv("BUILDER_FEE_TENTH_BPS", "5")
    monkeypatch.setenv("TOKEN_BUDGET_MONTHLY", "200")
    monkeypatch.setenv("VOICE_ENABLED", "false")
    monkeypatch.setenv("DENY_COUNTRIES_URL", "")


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
    assert msg.markups[-1] is not None


def test_price_handler(monkeypatch):
    set_env(monkeypatch)
    msg = DummyMessage("/price ETH")
    asyncio.run(price_handler(msg))
    assert "ETH price" in msg.replies[-1]


def test_trade_row_created_after_buy(monkeypatch, tmp_path):
    set_env(monkeypatch)
    db_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    monkeypatch.setenv("DATABASE_URL", db_url)
    user = types.User(7)
    msg = DummyMessage("/buy ETH 1", from_user=user)
    asyncio.run(buy_sell_handler(msg, "buy"))
    cb = types.CallbackQuery("confirm", msg, from_user=user)
    asyncio.run(order_callback_handler(cb))
    get_engine()
    sessionmaker = get_sessionmaker()
    async def fetch_symbol() -> str:
        async with sessionmaker() as session:
            result = await session.execute(select(Trade))
            return result.scalar_one().symbol
    symbol = asyncio.run(fetch_symbol())
    assert symbol == "ETH"

