"""Tests for geofence list loading."""

from hyperliquid_bot.bot.config import load_deny_countries
from fastapi.testclient import TestClient
import hyperliquid_bot.api.main as api_main


def test_load_deny_countries_defaults(tmp_path, monkeypatch):
    """Ensure deny countries list is loaded correctly from default file."""
    # Copy test file to temporary directory
    deny_file = tmp_path / "deny.json"
    deny_file.write_text('["IR", "kp", "Sy"]')
    monkeypatch.setenv("DENY_COUNTRIES_URL", deny_file.as_uri())
    codes = load_deny_countries()
    assert set(codes) == {"IR", "KP", "SY"}


def test_load_deny_countries_missing(tmp_path, monkeypatch):
    """When file does not exist, empty list is returned."""
    missing = tmp_path / "missing.json"
    monkeypatch.setenv("DENY_COUNTRIES_URL", missing.as_uri())
    codes = load_deny_countries()
    assert codes == []


def test_approve_callback_blocks(monkeypatch, tmp_path):
    """Approval callback should block users from denied countries."""
    deny_file = tmp_path / "deny.json"
    deny_file.write_text('["IR", "KP"]')
    monkeypatch.setenv("DENY_COUNTRIES_URL", deny_file.as_uri())

    def fake_urlopen(url: str):
        class Resp:
            def read(self) -> bytes:
                return b'{"country":"IR"}'

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        return Resp()

    monkeypatch.setattr(api_main, "urlopen", fake_urlopen)
    client = TestClient(api_main.app)
    resp = client.post("/approve/callback", headers={"X-Forwarded-For": "1.2.3.4"})
    assert resp.status_code == 403
