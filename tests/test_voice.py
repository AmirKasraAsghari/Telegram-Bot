"""Tests for voice message stub."""

from hyperliquid_bot.bot.voice import voice_to_order
from hyperliquid_bot.bot.nl_parser import parse_order, BudgetGuard


def test_voice_stub(tmp_path):
    phrase = "Long BTC 0.1 at market"
    ogg = tmp_path / "sample.ogg"
    ogg.write_text(phrase)
    guard = BudgetGuard(1000)
    text_order = parse_order(phrase, budget=guard)
    voice_order = voice_to_order(str(ogg), budget=guard)
    assert voice_order == text_order
