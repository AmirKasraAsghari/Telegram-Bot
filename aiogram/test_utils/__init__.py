"""Test utilities for the aiogram stub."""
from __future__ import annotations

from functools import partial
from typing import Any, Awaitable, Callable, Dict

from .. import Dispatcher, types


class TestDispatcher(Dispatcher):
    """Dispatcher with a helper to feed messages through middleware."""
    __test__ = False

    async def feed_update(self, message: types.Message) -> Dict[str, Any]:
        """Process a message and return context data."""
        command = message.text.split()[0].lstrip("/") if message.text else ""
        handler = self.message._handlers.get(command)
        if handler is None:
            raise ValueError(f"No handler for command {command}")

        async def base(event: types.Message, data: Dict[str, Any]) -> Any:
            return await handler(event)

        call: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]] = base
        for mw in reversed(self.message._middlewares):
            call = partial(mw, call)

        data: Dict[str, Any] = {}
        await call(message, data)
        return data
