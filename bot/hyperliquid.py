"""Helpers for interacting with Hyperliquid.

This module defines helpers to build order payloads and simulate interactions
with the Hyperliquid exchange. Actual network calls are abstracted so that
unit tests can exercise logic without hitting external services.

Notes
-----
* Builder codes allow builders to collect fees up to 0.1 % on perps once a user
  approves the builder fee【534398248561066†L141-L159】. The fee is specified in
  tenths of a basis point (1 bp = f=10).
* Users must approve the builder and the bot must maintain at least 100 USDC
  in perps account value【534398248561066†L141-L154】. Approval process is
  outside the scope of this helper and should be handled via commands.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .config import Settings


@dataclass
class Order:
    """Representation of a trade order for Hyperliquid.

    Attributes
    ----------
    symbol: str
        The ticker of the perpetual contract (e.g., ``ETH`` or ``BTC``).
    side: str
        "buy" or "sell".
    size: float
        The contract quantity to trade.
    price: Optional[float]
        Limit price. If ``None``, the order will be market.
    leverage: Optional[int]
        Desired leverage for the position.
    builder_fee: int
        Fee in tenths of basis points to pay to the builder. Setting ``0``
        disables fee collection (e.g., during launch promotion).
    """

    symbol: str
    side: str
    size: float
    price: Optional[float] = None
    leverage: Optional[int] = None
    builder_fee: int = 5

    def to_payload(self, builder_address: str) -> Dict[str, Any]:
        """Convert the order to a Hyperliquid API payload.

        Parameters
        ----------
        builder_address: str
            The address that will receive builder fees.

        Returns
        -------
        Dict[str, Any]
            JSON serializable payload for the exchange API.
        """
        payload: Dict[str, Any] = {
            "type": "order",
            "coin": self.symbol,
            "isBuy": True if self.side.lower() == "buy" else False,
            "sz": str(self.size),  # sizes are encoded as strings in API
            # builder code field
            "b": builder_address.lower(),
            "f": self.builder_fee,
        }
        # When builder fee is zero, indicate promotional mode
        if self.builder_fee == 0:
            payload["zeroFee"] = True
        # Determine order type and price fields
        if self.price is not None:
            payload.update({
                "limitPx": str(self.price),
            })
        # Leverage can be optionally specified
        if self.leverage is not None:
            payload.update({"leverage": self.leverage})
        return payload


def build_order_json(
    symbol: str,
    side: str,
    size: float,
    price: Optional[float] = None,
    leverage: Optional[int] = None,
    builder_fee: Optional[int] = None,
    *,
    settings: Optional[Settings] = None,
) -> Dict[str, Any]:
    """Utility wrapper to create order payloads with configured defaults.

    This function picks up the builder fee from settings unless explicitly
    overridden. It also honours zero‑fee launch periods.

    Parameters
    ----------
    symbol: str
        Contract symbol.
    side: str
        Either "buy" or "sell".
    size: float
        Quantity to trade.
    price: Optional[float]
        Limit price. ``None`` indicates a market order.
    leverage: Optional[int]
        Leverage value.
    builder_fee: Optional[int]
        Fee override in tenths of basis points.
    settings: Optional[Settings]
        Settings instance. If omitted, loaded automatically.

    Returns
    -------
    Dict[str, Any]
        Payload dictionary for the exchange.
    """
    s = settings or Settings()
    fee = builder_fee if builder_fee is not None else s.builder_fee_default
    # If launch_zero_fee is true, override to zero
    if s.launch_zero_fee:
        fee = 0
    order = Order(
        symbol=symbol,
        side=side,
        size=size,
        price=price,
        leverage=leverage,
        builder_fee=fee,
    )
    return order.to_payload(builder_address="0xbuilder")
