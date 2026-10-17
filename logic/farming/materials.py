"""Bank material checks and debits for Farming transactions.

Bittercap keeps its ``Mushroom spore`` seed key, while Vinesweeper and the
Master Farmer grant ``Bittercap mushroom spore``. Both name item 5282 (Farming
oldid 6565110, Exchange oldid 6561263), so either stack plants the crop and
saves keep both keys untouched.
"""

from __future__ import annotations

import math
from typing import Any, Mapping

from ...data.farming_data import FARMING_CROPS_BY_ID

_MUSHROOM_SPORE = FARMING_CROPS_BY_ID["bittercap"].seed_item
_BITTERCAP_SPORE = "Bittercap mushroom spore"


def _int(value: Any, default: int = 0, minimum: int = 0) -> int:
    try:
        number = float(value)
        if not math.isfinite(number):
            return default
        return max(minimum, int(number))
    except (TypeError, ValueError, OverflowError):
        return default


def _resolve_requirements(inventory: Mapping[str, Any], requirements: Mapping[str, int]) -> Mapping[str, int]:
    # A sufficient Mushroom spore stack keeps the existing transaction. The
    # producers' stack stands in only when it alone covers the seed and any
    # separate demand on its own key, so one spore never pays twice and two
    # short stacks are never pooled.
    amount = requirements.get(_MUSHROOM_SPORE)
    if not amount or _int(inventory.get(_MUSHROOM_SPORE)) >= amount:
        return requirements
    total = amount + requirements.get(_BITTERCAP_SPORE, 0)
    if _int(inventory.get(_BITTERCAP_SPORE)) < total:
        return requirements
    resolved = {item: needed for item, needed in requirements.items() if item != _MUSHROOM_SPORE}
    resolved[_BITTERCAP_SPORE] = total
    return resolved


def _has_items(inventory: Mapping[str, Any], requirements: Mapping[str, int]) -> bool:
    resolved = _resolve_requirements(inventory, requirements)
    return all(_int(inventory.get(item)) >= amount for item, amount in resolved.items())


def _consume(inventory: dict[str, Any], requirements: Mapping[str, int]) -> None:
    for item, amount in _resolve_requirements(inventory, requirements).items():
        inventory[item] = _int(inventory.get(item)) - amount


def _missing_items_reason(inventory: Mapping[str, Any], requirements: Mapping[str, int]) -> str:
    missing = [
        f"{amount} {item} ({_int(inventory.get(item))} in Bank)"
        for item, amount in _resolve_requirements(inventory, requirements).items()
        if _int(inventory.get(item)) < amount
    ]
    return f"Needs {', '.join(missing)}." if missing else ""
