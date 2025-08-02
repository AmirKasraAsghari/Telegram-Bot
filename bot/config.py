"""Configuration loader for the trading bot.

This module loads environment variables and geofence lists. It provides
defaults for builder fee and other settings. The geofence list is stored in
JSON format under ``config/deny_countries.json``. Users from these ISO
country codes should be blocked from interacting with the bot.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings loaded from environment variables.

    This lightweight replacement for :class:`pydantic.BaseSettings` avoids a
    hard dependency on Pydantic which keeps the test environment minimal. Each
    field lazily pulls from ``os.environ`` when an instance is created.
    """

    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", ""))
    builder_fee_default: int = field(default_factory=lambda: int(os.getenv("BUILDER_FEE_DEFAULT", "5")))
    launch_zero_fee: bool = field(default_factory=lambda: os.getenv("LAUNCH_ZERO_FEE", "").lower() == "true")
    deny_countries_path: str = field(
        default_factory=lambda: os.getenv(
            "DENY_COUNTRIES_PATH", "hyperliquid_bot/config/deny_countries.json"
        )
    )


def load_deny_countries(path: Optional[str] = None) -> List[str]:
    """Load ISO country codes from the deny_countries JSON file.

    Parameters
    ----------
    path: Optional[str]
        Optional path to the JSON file. If ``None``, uses the path from
        Settings.deny_countries_path.

    Returns
    -------
    List[str]
        A list of ISO 3166-1 alpha-2 country codes that should be blocked.
    """
    settings = Settings()
    file_path = Path(path or settings.deny_countries_path)
    if not file_path.exists():
        return []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [c.upper() for c in data if isinstance(c, str)]
        raise ValueError("deny_countries.json must be a list of country codes")
    except Exception:
        return []
