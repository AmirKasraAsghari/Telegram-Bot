"""Simple in-memory metrics helpers for tests."""
from __future__ import annotations

from typing import Dict

_latency_buckets = [50, 100, 250, 500]
latency_ms_bucket: Dict[int, int] = {b: 0 for b in _latency_buckets}
_total_orders = 0


def observe_latency(ms: float) -> None:
    """Record a handler latency in milliseconds."""
    for b in _latency_buckets:
        if ms <= b:
            latency_ms_bucket[b] += 1
            break


def inc_orders() -> None:
    """Increment total order counter."""
    global _total_orders
    _total_orders += 1


def render_metrics() -> str:
    """Render metrics in Prometheus text format."""
    lines = [f'latency_ms_bucket{{le="{b}"}} {latency_ms_bucket[b]}' for b in _latency_buckets]
    lines.append(f'total_orders {_total_orders}')
    return "\n".join(lines) + "\n"
