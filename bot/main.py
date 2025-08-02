"""Entry point for the Telegram bot.

This script initializes the `aiogram` Bot and Dispatcher, registers command
handlers, and starts polling. It can be executed with `python -m bot.main`.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from .config import Settings
from .commands import setup_bot


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()
    await setup_bot(bot, dispatcher)
    # Start polling
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass