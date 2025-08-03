"""Accuracy tests for the natural language parser."""

import math

from hyperliquid_bot.bot.nl_parser import (
    BudgetGuard,
    confirm_order,
    order_preview,
    parse_order,
)
from hyperliquid_bot.bot.hyperliquid import build_order_json

cases = [
    ("Long BTC 0.1 at market", ("BTC", "buy", 0.1, None, None)),
    ("Short ETH 2 at 3500", ("ETH", "sell", 2.0, 3500.0, None)),
    ("Buy 5 SOL @ 40", ("SOL", "buy", 5.0, 40.0, None)),
    ("Sell 10 XRP at market", ("XRP", "sell", 10.0, None, None)),
    ("Long DOG-PERP 3 with 5x leverage", ("DOG-PERP", "buy", 3.0, None, 5)),
    ("Sell 50 DOG-PERP with 10x leverage", ("DOG-PERP", "sell", 50.0, None, 10)),
    ("Buy 0.5 BTC @30000 3x", ("BTC", "buy", 0.5, 30000.0, 3)),
    ("Short 2 ETH at 2000", ("ETH", "sell", 2.0, 2000.0, None)),
    ("Long 1 BTC with 2x", ("BTC", "buy", 1.0, None, 2)),
    ("Sell 7 ADA at 0.3", ("ADA", "sell", 7.0, 0.3, None)),
    ("Buy 1.2 LTC @100", ("LTC", "buy", 1.2, 100.0, None)),
    ("Long BNB 4", ("BNB", "buy", 4.0, None, None)),
    ("Short DOGE 1000 at 0.07", ("DOGE", "sell", 1000.0, 0.07, None)),
    ("Buy 3 LINK @ 7 with 4x leverage", ("LINK", "buy", 3.0, 7.0, 4)),
    ("Sell 0.25 BTC", ("BTC", "sell", 0.25, None, None)),
    ("Long SOL 2 at 35 with 3x", ("SOL", "buy", 2.0, 35.0, 3)),
    ("Short XRP 5 at market", ("XRP", "sell", 5.0, None, None)),
    ("Buy 10 DOG-PERP", ("DOG-PERP", "buy", 10.0, None, None)),
    ("Sell 0.1 ETH @ 1800", ("ETH", "sell", 0.1, 1800.0, None)),
    ("Long BTC 1 @ 28000", ("BTC", "buy", 1.0, 28000.0, None)),
    ("Short 5 BNB with 2x leverage", ("BNB", "sell", 5.0, None, 2)),
    ("Buy ADA 1000 @0.25", ("ADA", "buy", 1000.0, 0.25, None)),
    ("Sell 2 LTC at market", ("LTC", "sell", 2.0, None, None)),
    ("Long 0.3 BTC with 3x leverage", ("BTC", "buy", 0.3, None, 3)),
    ("Short 1 DOGE @0.06", ("DOGE", "sell", 1.0, 0.06, None)),
    ("Buy 4 SOL at 32", ("SOL", "buy", 4.0, 32.0, None)),
    ("Sell 0.5 XRP with 5x", ("XRP", "sell", 0.5, None, 5)),
    ("Long ETH 0.8 at 2500", ("ETH", "buy", 0.8, 2500.0, None)),
    ("Short BTC 0.2", ("BTC", "sell", 0.2, None, None)),
    ("Buy 6 BNB @ 240", ("BNB", "buy", 6.0, 240.0, None)),
]


def test_nl_phrase_accuracy(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("REDIS_URL", "redis://")
    guard = BudgetGuard(10000)
    correct = 0
    for phrase, params in cases:
        expected = build_order_json(*params[:3], price=params[3], leverage=params[4])
        payload = parse_order(phrase, budget=guard)
        if payload == expected:
            correct += 1
    assert len(cases) == 30
    required = math.ceil(0.95 * len(cases))
    assert correct >= required, f"Only {correct}/{len(cases)} phrases parsed correctly"


def test_confirm_flow():
    preview, payload = order_preview("Long BTC 0.1 at market")
    assert "Confirm?" in preview
    confirmed = confirm_order(payload)
    assert confirmed["coin"] == "BTC"
