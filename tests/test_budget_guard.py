from hyperliquid_bot.bot.nl_parser import BudgetGuard, parse_order


def test_budget_guard_logs(caplog):
    guard = BudgetGuard(monthly_budget=1)
    long_text = "Buy 1 BTC" + " really" * 100
    with caplog.at_level("WARNING"):
        parse_order(long_text, budget=guard)
    assert "Budget exceeded" in caplog.text
