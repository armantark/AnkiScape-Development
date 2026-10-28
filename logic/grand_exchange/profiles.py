"""Stable market profiles shared with demand accounting."""

import hashlib
import math
from typing import Any, Mapping

GE_MARKET_DAY_CARDS = 240


def _clean_int(value: object, default: int = 0, *, minimum: int = 0) -> int:
    try:
        cleaned = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return max(minimum, cleaned)


def _stable_unit_interval(*parts: object) -> float:
    payload = "\x1f".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def _move_toward_zero(value: int, amount: int) -> int:
    if value > 0:
        return max(0, value - amount)
    if value < 0:
        return min(0, value + amount)
    return 0


def _market_liquidity_pure(
    *,
    anchor_price: int,
    item_seed: int,
    market_tick: int,
    item_spec: Mapping[str, Any],
) -> float:
    base = 1.0 - math.log(max(1, anchor_price)) / math.log(2_000_000_000)
    base = min(1.0, max(0.18, base))
    category_factor = {
        "ore": 1.08,
        "log": 1.08,
        "fish": 1.05,
        "runecrafting": 1.05,
        "gem": 0.82,
        "equipment": 0.80,
        "hunter": 0.85,
    }.get(str(item_spec.get("category", "")), 1.0)
    role_factor = {
        "raw_material": 1.08,
        "processed_good": 0.92,
        "rare_or_dependency": 0.80,
    }.get(str(item_spec.get("source_role", "")), 1.0)
    required_level = _clean_int(item_spec.get("required_level"), 1, minimum=1)
    level_factor = 1.0 - min(0.30, (required_level - 1) / 326.0)
    day_index = market_tick // GE_MARKET_DAY_CARDS
    day_phase = (market_tick % GE_MARKET_DAY_CARDS) / GE_MARKET_DAY_CARDS
    day_envelope = 1.0 - 0.25 * math.cos(2.0 * math.pi * day_phase)
    weekend = 1.10 if day_index % 7 in {5, 6} else 1.0
    item_jitter = 0.95 + 0.10 * _stable_unit_interval(item_seed, "item_liquidity")
    day_jitter = 0.90 + 0.20 * _stable_unit_interval(
        item_seed,
        day_index,
        "day_liquidity",
    )
    return min(
        1.5,
        max(
            0.10,
            base
            * category_factor
            * role_factor
            * level_factor
            * day_envelope
            * weekend
            * item_jitter
            * day_jitter,
        ),
    )
