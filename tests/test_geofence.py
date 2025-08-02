"""Tests for geofence list loading."""

from hyperliquid_bot.bot.config import load_deny_countries


def test_load_deny_countries_defaults(tmp_path, monkeypatch):
    """Ensure deny countries list is loaded correctly from default file."""
    # Copy test file to temporary directory
    deny_file = tmp_path / "deny.json"
    deny_file.write_text('["IR", "kp", "Sy"]')
    monkeypatch.setenv("DENY_COUNTRIES_PATH", str(deny_file))
    codes = load_deny_countries()
    assert set(codes) == {"IR", "KP", "SY"}


def test_load_deny_countries_missing(monkeypatch):
    """When file does not exist, empty list is returned."""
    monkeypatch.setenv("DENY_COUNTRIES_PATH", "/path/does/not/exist.json")
    codes = load_deny_countries()
    assert codes == []
