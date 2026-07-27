"""Whitelisted derivations a diary ``derived_value`` condition may read.

Some period tasks are stated against a figure the save computes rather than
stores. Kudos is the example: it is a weighted sum over three append-only
records, and no leaf anywhere holds it. The ``counter`` kind coerces a leaf with
``int()``, so pointing it at such a figure reads zero forever and the row can
never complete.

This registry is the only way a condition may read a computed figure, and it
carries only derivations a shipped condition actually uses. The ceilings beside
it pin the maximum each derivation can currently reach, so a task threshold can
be tested for reachability against the content rather than against a constant
that might have drifted away from it.

It lives in its own module because ``data.achievement_diary_data`` validates the
catalog against it at import time, and ``logic.achievement_diary_logic`` imports
that data module.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ..data.varrock_museum_data import VARROCK_MUSEUM_IMPLEMENTED_MAX_KUDOS
from .varrock_museum_logic import varrock_museum_kudos_pure


DIARY_DERIVED_VALUES: dict[str, Callable[[Mapping[str, Any]], int]] = {
    "varrock_museum_kudos": varrock_museum_kudos_pure,
}

DIARY_DERIVED_VALUE_CEILINGS: dict[str, int] = {
    "varrock_museum_kudos": VARROCK_MUSEUM_IMPLEMENTED_MAX_KUDOS,
}
