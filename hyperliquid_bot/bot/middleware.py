"""Custom middleware utilities for the Telegram bot.

This module currently provides :class:`ExecutionTimeMiddleware` which measures
how long a handler takes to run. The timing is stored in the context ``data``
for further inspection and logged using the standard :mod:`logging` module.
The implementation is intentionally lightweight for the test environment.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Awaitable, Callable, Dict


from ..api.metrics import observe_latency

logger = logging.getLogger(__name__)


class ExecutionTimeMiddleware:
    """Measure and log execution time of handlers.

    The middleware follows the aiogram v3 protocol where middleware instances
    are callable with ``handler``, ``event`` and a mutable ``data`` mapping. The
    elapsed time in seconds is stored under ``execution_time`` in ``data`` and
    logged at INFO level.
    """

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        start = time.perf_counter()
        result = await handler(event, data)
        duration = time.perf_counter() - start
        data["execution_time"] = duration
        logger.info("%s handled in %.4f seconds", getattr(handler, "__name__", str(handler)), duration)
        observe_latency(duration * 1000)
        return result
