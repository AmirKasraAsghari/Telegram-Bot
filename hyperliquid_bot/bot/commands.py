"""Telegram command handlers.

This module defines handlers for slash commands used by the Hyperliquid
trading companion. The implementation is lightweight and does not perform
network calls; instead, it builds JSON payloads and returns them for user
confirmation. Integration with actual order placement and wallet signing
would occur in production.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, CommandObject

from .config import load_deny_countries
from .hyperliquid import build_order_json
from .db import (
    Base,
    Trade,
    get_engine,
    get_or_create_user,
    get_sessionmaker,
)
from ..api.metrics import inc_orders


logger = logging.getLogger(__name__)


async def start_handler(message: types.Message, command: CommandObject) -> None:
    """Handle the /start command.

    Greets the user and checks geofence restrictions. If the user’s IP
    originates from a denied country, they are blocked from further use.
    """
    deny_countries = set(load_deny_countries())
    # In production, you would extract the user's country from an IP lookup.
    # During testing we mock this as always allowed.
    user_country_code: Optional[str] = None  # to be filled via webhook metadata
    if user_country_code and user_country_code.upper() in deny_countries:
        await message.answer("Sorry, our service is not available in your region.")
        return
    await message.answer(
        "Welcome to the Hyperliquid trading bot! Use /approve to set up builder fees or /help for more commands."
    )


async def approve_handler(message: types.Message) -> None:
    """Handle the /approve command.

    In practice, this would direct the user to sign a transaction approving
    the builder fee via their main Hyperliquid wallet. Here we provide a
    placeholder response.
    """
    await message.answer(
        "To start trading, you need to approve the bot as a builder. Please sign the builder fee approval in the Hyperliquid UI."
    )


async def buy_sell_handler(message: types.Message, side: str) -> None:
    """Handle /buy or /sell commands.

    Expects the command text to include the symbol and size. Optionally
    accepts a price and leverage. Example: ``/buy ETH 1.5 3000 5`` will
    build a limit order to buy 1.5 ETH at 3000 USDC with 5x leverage.
    """
    args = message.text.strip().split()
    # args[0] is the command, e.g., '/buy'
    if len(args) < 3:
        await message.answer("Usage: /{} SYMBOL SIZE [PRICE] [LEVERAGE]".format(side))
        return
    symbol = args[1].upper()
    try:
        size = float(args[2])
    except ValueError:
        await message.answer("Invalid size; please provide a number.")
        return
    price = None
    leverage = None
    if len(args) >= 4:
        try:
            price = float(args[3])
        except ValueError:
            await message.answer("Invalid price; please provide a number.")
            return
    if len(args) >= 5:
        try:
            leverage = int(args[4])
        except ValueError:
            await message.answer("Invalid leverage; please provide an integer.")
            return
    payload = build_order_json(
        symbol=symbol, side=side, size=size, price=price, leverage=leverage
    )
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Place", callback_data="confirm"),
                types.InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"),
            ]
        ]
    )
    await message.answer(
        f"Order preview:\n{json.dumps(payload)}", reply_markup=keyboard
    )


async def positions_handler(message: types.Message) -> None:
    """Handle the /positions command.

    For now this returns a placeholder response indicating that the user has no
    open positions. In production the bot would query Hyperliquid for the
    account's current positions.
    """
    await message.answer("You currently have no open positions.")


async def cancel_handler(message: types.Message) -> None:
    """Handle the /cancel command.

    The command optionally accepts an order identifier; the current
    implementation only echoes back a confirmation message and does not perform
    any API calls.
    """
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) > 1:
        await message.answer(f"Cancelled order {parts[1]}.")
    else:
        await message.answer("Cancelled all open orders.")


async def price_handler(message: types.Message) -> None:
    """Handle the /price command."""

    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer("Usage: /price SYMBOL")
        return
    symbol = parts[1].upper()
    await message.answer(f"{symbol} price is 0 (stub)")


async def order_callback_handler(callback: types.CallbackQuery) -> None:
    """Handle confirm/cancel buttons for orders."""

    if callback.data == "confirm":
        # Parse order payload from the message text
        payload = {}
        try:
            _, raw = callback.message.text.split("\n", 1)
            payload = json.loads(raw)
        except Exception:
            pass

        engine = get_engine()
        sessionmaker = get_sessionmaker()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with sessionmaker() as session:
            user = await get_or_create_user(session, callback.from_user.id)
            trade = Trade(
                user_id=user.id,
                symbol=payload.get("coin", ""),
                side="buy" if payload.get("isBuy") else "sell",
                size=float(payload.get("sz", "0")),
            )
            session.add(trade)
            await session.commit()
        inc_orders()
        await callback.message.edit_text("Order submitted!")
    else:
        await callback.message.edit_text("Order cancelled.")
    await callback.answer()


async def setup_bot(bot: Bot, dispatcher: Dispatcher) -> None:
    """Register handlers with the dispatcher.

    This helper wires up command handlers to the dispatcher. Should be
    called after bot and dispatcher are created in the main entrypoint.
    """
    # Start command
    dispatcher.message.register(start_handler, CommandStart())
    # Approve command
    dispatcher.message.register(approve_handler, commands={"approve"})
    # Buy and sell commands
    async def buy_wrapper(message: types.Message) -> None:
        await buy_sell_handler(message, "buy")
    async def sell_wrapper(message: types.Message) -> None:
        await buy_sell_handler(message, "sell")
    dispatcher.message.register(buy_wrapper, commands={"buy"})
    dispatcher.message.register(sell_wrapper, commands={"sell"})
    # Positions and cancel commands
    dispatcher.message.register(positions_handler, commands={"positions"})
    dispatcher.message.register(cancel_handler, commands={"cancel"})
    dispatcher.message.register(price_handler, commands={"price"})
    dispatcher.callback_query.register(order_callback_handler)
