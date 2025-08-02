"""Minimal stub of the aiogram API for offline testing.

This stub implements only the interfaces used by the trading bot. It allows
imports of aiogram modules to succeed in environments where the real
``aiogram`` package is not installed. The stub does not provide actual
Telegram integration; it is solely for static analysis and unit tests.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, Iterable


class Bot:
    """Simplified bot with token property."""
    def __init__(self, token: str, *args: Any, **kwargs: Any) -> None:
        self.token = token


class _MessageRegistry:
    """Helper class to simulate message handler registration."""

    def __init__(self) -> None:
        self._middlewares: list[Any] = []
        self._handlers: Dict[str, Callable[..., Any]] = {}

    def register(
        self, handler: Callable[..., Any], *args: Any, commands: Iterable[str] | None = None, **kwargs: Any
    ) -> None:
        """Register a handler for a set of commands."""
        if commands is None:
            return
        for cmd in commands:
            self._handlers[cmd] = handler

    def middleware(self, middleware: Any) -> None:
        """Register a middleware object (stored only for inspection)."""
        self._middlewares.append(middleware)


class Dispatcher:
    """Minimal dispatcher that accepts handler registration and polling."""
    def __init__(self) -> None:
        self.message = _MessageRegistry()

    async def start_polling(self, bot: Bot) -> None:
        # Polling is no‑op in stub
        await asyncio.sleep(0)


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
