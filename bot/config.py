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

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes
    ----------
    telegram_bot_token: str
        Token for the Telegram bot provided by BotFather.
    openai_api_key: str
        API key for OpenAI GPT access.
    database_url: str
        SQLAlchemy database URL (e.g., ``postgresql+asyncpg://user:pass@host/db``).
    redis_url: str
        URL for Redis/KeyDB instance (e.g., ``redis://localhost:6379/0``).
    builder_fee_default: int
        Default builder fee measured in tenths of a basis point. A value of
        ``5`` corresponds to 0.5 basis points (0.005 %).
    launch_zero_fee: bool
        Whether the bot is currently in zero‑fee launch mode. When ``True``
        all orders are sent with ``f=0`` regardless of user tier.
    deny_countries_path: str
        Path to the JSON file containing ISO country codes to geofence.
    """

    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    builder_fee_default: int = Field(5, env="BUILDER_FEE_DEFAULT")
    launch_zero_fee: bool = Field(False, env="LAUNCH_ZERO_FEE")
    deny_countries_path: str = Field("hyperliquid_bot/config/deny_countries.json", env="DENY_COUNTRIES_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


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