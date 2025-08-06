from hyperliquid_bot.bot import hyperliquid


def test_record_api_error_alert():
    hyperliquid.reset_breaker()
    alerts = []

    def cb(msg: str) -> None:
        alerts.append(msg)

    hyperliquid.set_alert_callback(cb)
    for _ in range(3):
        hyperliquid.record_api_error()
    assert hyperliquid.is_paused() is True
    assert alerts and "error threshold" in alerts[0].lower()
