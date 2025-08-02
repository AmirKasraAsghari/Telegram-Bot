"""Tests for order JSON generation.

This module verifies that `build_order_json` correctly constructs payloads
according to provided parameters and respects zero‑fee launch mode.
"""

import pytest

from hyperliquid_bot.bot.hyperliquid import build_order_json
from hyperliquid_bot.bot.config import Settings


def test_build_market_order_default_fee(monkeypatch):
    """Market order should include default builder fee."""
    # Use test settings
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    # Set default builder fee to 5
    monkeypatch.setenv("BUILDER_FEE_DEFAULT", "5")
    settings = Settings()
    payload = build_order_json("ETH", "buy", 1.5, settings=settings)
    assert payload["type"] == "order"
    assert payload["coin"] == "ETH"
    assert payload["isBuy"] is True
    assert payload["sz"] == "1.5"
    assert payload["b"] == "0xbuilder"
    assert payload["f"] == 5


def test_build_limit_order_override_fee(monkeypatch):
    """Limit order with explicit builder fee should override default."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    settings = Settings()
    payload = build_order_json("BTC", "sell", 0.25, price=30000, leverage=3, builder_fee=8, settings=settings)
    assert payload["isBuy"] is False
    assert payload["limitPx"] == "30000"
    assert payload.get("leverage") == 3
    assert payload["f"] == 8


def test_zero_fee_launch(monkeypatch):
    """When LAUNCH_ZERO_FEE is enabled, builder fee should be zero."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("LAUNCH_ZERO_FEE", "true")
    settings = Settings()
    payload = build_order_json("DOGE", "buy", 10, builder_fee=7, settings=settings)
    assert payload["f"] == 0