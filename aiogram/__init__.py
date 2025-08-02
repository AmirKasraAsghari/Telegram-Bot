"""Minimal stub of the aiogram API for offline testing.

This stub implements only the interfaces used by the trading bot. It allows
imports of aiogram modules to succeed in environments where the real
``aiogram`` package is not installed. The stub does not provide actual
Telegram integration; it is solely for static analysis and unit tests.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, Optional


class Bot:
    """Simplified bot with token property."""
    def __init__(self, token: str, *args: Any, **kwargs: Any) -> None:
        self.token = token


class _MessageRegistry:
    """Helper class to simulate message handler registration."""
    def register(self, handler: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        # In a real implementation, handlers would be stored for dispatching.
        pass


class Dispatcher:
    """Minimal dispatcher that accepts handler registration and polling."""
    def __init__(self) -> None:
        self.message = _MessageRegistry()

    async def start_polling(self, bot: Bot) -> None:
        # Polling is no‑op in stub
        await asyncio.sleep(0)


class filters:  # type: ignore
    class CommandStart:
        """Placeholder for CommandStart filter."""
        pass


class types:  # type: ignore
    class Message:
        """Represents a Telegram message in the stub."""
        def __init__(self, text: str = "") -> None:
            self.text = text

        async def answer(self, text: str) -> None:
            # In tests we might capture answers; for now this is a no‑op.
            pass

    class CommandObject:
        """Placeholder for aiogram CommandObject."""
        pass