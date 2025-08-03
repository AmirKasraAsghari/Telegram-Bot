"""Natural language order parser with budget guard.

This module parses free-form trading instructions into structured order
payloads. It uses a very small heuristic parser for unit tests but exposes
interfaces that could call GPT models in production. A ``BudgetGuard``
monitors estimated token spend and falls back to a lightweight parser when
the monthly budget is exceeded.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import os
import re
from typing import Optional

from .hyperliquid import build_order_json

logger = logging.getLogger(__name__)


@dataclass
class BudgetGuard:
    """Simple token budget tracker.

    Attributes
    ----------
    monthly_budget: float
        Maximum spend allowed for the current month.
    spent: float
        Accumulated spend for the current month.
    """

    monthly_budget: float = float(os.getenv("TOKEN_BUDGET_MONTHLY", 200))
    spent: float = 0.0

    def can_spend(self, cost: float) -> bool:
        """Return ``True`` if ``cost`` may be spent, else log fallback."""
        if self.spent + cost > self.monthly_budget:
            logger.warning("Budget exceeded; using fallback parser")
            return False
        self.spent += cost
        return True


def _heuristic_parse(text: str) -> tuple[str, str, float, Optional[float], Optional[int]]:
    """Parse order parameters using simple heuristics.

    Returns ``(symbol, side, size, price, leverage)``.
    """
    original = text
    text = text.replace("@", " @ ")
    tokens = text.lower().split()
    side = "buy"
    if "sell" in tokens or "short" in tokens:
        side = "sell"
    if "long" in tokens or "buy" in tokens:
        side = "buy" if "sell" not in tokens and "short" not in tokens else "sell"

    symbol = None
    size: Optional[float] = None
    price: Optional[float] = None
    leverage: Optional[int] = None

    exclude = {"with", "at", "market", "leverage", "long", "short", "buy", "sell"}
    for tok in tokens:
        if re.fullmatch(r"[a-z]+(?:-perp)?", tok) and tok not in exclude:
            symbol = tok.upper()
            break
    for tok in tokens:
        if re.fullmatch(r"\d+(?:\.\d+)?", tok):
            if size is None:
                size = float(tok)
            elif price is None:
                price = float(tok)
    for i, tok in enumerate(tokens):
        if tok in {"@", "at"} and i + 1 < len(tokens):
            nxt = tokens[i + 1]
            if nxt != "market" and re.fullmatch(r"\d+(?:\.\d+)?", nxt):
                price = float(nxt)
    for tok in tokens:
        m = re.fullmatch(r"(\d+)x", tok)
        if m:
            leverage = int(m.group(1))
    if symbol is None or size is None:
        raise ValueError(f"Could not parse order from '{original}'")
    return symbol, side, size, price, leverage


def parse_order(text: str, *, budget: Optional[BudgetGuard] = None) -> dict:
    """Parse ``text`` into an order JSON payload.

    In a real deployment this would call the OpenAI API. For the test suite we
    use the heuristic parser above. ``BudgetGuard`` determines whether the
    model may be called; when the budget is exceeded the same heuristic parser
    acts as a lightweight fallback.
    """
    budget = budget or BudgetGuard()
    # Estimate cost by token count (very rough)
    estimated_cost = len(text.split())
    if budget.can_spend(estimated_cost):
        # Placeholder for GPT call; use heuristic for the tests
        logger.debug("Parsing with GPT stub")
        symbol, side, size, price, leverage = _heuristic_parse(text)
    else:
        logger.debug("Using logistic regression fallback parser")
        symbol, side, size, price, leverage = _heuristic_parse(text)
    payload = build_order_json(symbol, side, size, price=price, leverage=leverage)
    return payload


def order_preview(text: str, *, budget: Optional[BudgetGuard] = None) -> tuple[str, dict]:
    """Return a human-readable preview and the payload awaiting confirmation."""
    payload = parse_order(text, budget=budget)
    preview = f"Order preview:\n{payload}\n\nConfirm?"
    return preview, payload


def confirm_order(payload: dict) -> dict:
    """Placeholder confirmation step.

    In production this would be triggered by a callback button. For tests it
    simply returns the provided payload.
    """
    return payload
