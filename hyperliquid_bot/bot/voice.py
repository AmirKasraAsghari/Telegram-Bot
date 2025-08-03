"""Voice message handling stub.

The real implementation would invoke Whisper to transcribe `.ogg` files. For
unit tests and offline environments this module provides a minimal stub that
reads the input file as UTF‑8 text and feeds the result into the natural-
language parser.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .nl_parser import parse_order, BudgetGuard


def transcribe(path: str) -> str:
    """Return the text representation of an `.ogg` file.

    The stub simply reads the file contents as text. Test fixtures write the
    desired phrase directly to the file.
    """
    return Path(path).read_text(encoding="utf-8").strip()


def voice_to_order(path: str, *, budget: Optional[BudgetGuard] = None) -> dict:
    """Convert a voice message to an order payload."""
    text = transcribe(path)
    return parse_order(text, budget=budget)
