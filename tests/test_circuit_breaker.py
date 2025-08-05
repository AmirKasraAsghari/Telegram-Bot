from hyperliquid_bot.bot import hyperliquid


def test_circuit_breaker_trips(monkeypatch):
    hyperliquid._error_times.clear()
    hyperliquid._paused_until = 0
    times = [0, 10, 20, 21]

    def fake_monotonic():
        return times.pop(0)

    monkeypatch.setattr(hyperliquid.time, "monotonic", fake_monotonic)
    for _ in range(3):
        hyperliquid.record_api_error()
    assert hyperliquid.is_paused()
