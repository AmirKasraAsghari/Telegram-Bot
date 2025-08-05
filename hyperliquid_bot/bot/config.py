"""Configuration loader for the trading bot.

Environment variables are used for all runtime configuration.  The most
important ones are ``BUILDER_FEE_TENTH_BPS`` (fee in tenths of a basis point),
``ZERO_FEE_UNTIL`` (ISO timestamp for launch promotions) and
``DENY_COUNTRIES_URL`` pointing to a JSON/CSV deny‑list for geofencing.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Optional
from urllib.request import urlopen

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
    builder_fee_tenth_bps: int = field(
        default_factory=lambda: int(os.getenv("BUILDER_FEE_TENTH_BPS", "1"))
    )
    zero_fee_until: Optional[datetime] = field(
        default_factory=lambda: (
            datetime.fromisoformat(os.getenv("ZERO_FEE_UNTIL", ""))
            if os.getenv("ZERO_FEE_UNTIL")
            else None
        )
    )
    token_budget_monthly: int = field(
        default_factory=lambda: int(os.getenv("TOKEN_BUDGET_MONTHLY", "200"))
    )
    voice_enabled: bool = field(
        default_factory=lambda: os.getenv("VOICE_ENABLED", "").lower() == "true"
    )
    deny_countries_url: str = field(
        default_factory=lambda: os.getenv("DENY_COUNTRIES_URL", "")
    )


def load_deny_countries(url: Optional[str] = None) -> List[str]:
    """Fetch ISO country codes from a JSON or CSV deny‑list URL.

    The helper supports HTTP(S) and ``file://`` URLs so tests can provide a
    temporary file.  CSV files are expected to contain comma‑separated country
    codes.  Invalid or unreachable URLs simply result in an empty list.
    """

    settings = Settings()
    source = url or settings.deny_countries_url
    if not source:
        return []
    try:
        with urlopen(source) as fh:  # nosec - controlled input in tests
            raw = fh.read().decode("utf-8")
    except Exception:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [c.upper() for c in data if isinstance(c, str)]
    except Exception:
        pass
    # Fallback to CSV parsing
    return [c.strip().upper() for c in raw.split(",") if c.strip()]
