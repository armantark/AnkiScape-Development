"""Frozen modern volume evidence and delegated AnkiScape daily balance.

The rounded maxima describe the displayed six-month window, not all-time
records, historical sell demand, or pre-Evolution-of-Combat market behavior.
"""

import json
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType

REFERENCE_URL = "https://secure.runescape.com/m=itemdb_rs/top100?list=0&scale=3"
REFERENCE_TITLE = "Most Traded Items"
REFERENCE_RETRIEVED = "2026-10-24"
REFERENCE_SELECTION = "Last 6 Months, Max column"
REFERENCE_EXTRACT_SHA256 = "6510fa6b7a05e432692e03efe8a01b8287dac95a1c9bdec14686e7337fcea74e"
REFERENCE_CLASSIFICATION = "rounded modern statistics for the displayed six-month window"
PUBLISHER_REVISION_ID = "not provided"
INDIVIDUAL_MAXIMUM_DATES = "not provided"
OWNER_ANSWERS = (
    "There should be a roughly approximated daily trade volume each game-day, "
    "we can model this off the historical trading volume heights of RS3.",
    "Sell a smaller share scaled to one player; give a rough daily Yew-log allowance in the note.",
    "Buyers recover gradually up to one day's capacity; "
    "I'm not going to give you a yew log quantity. Do it yourself",
)
PLAYER_VOLUME_DIVISOR = 1_000
BALANCE_CLASSIFICATION = (
    "Author-selected AnkiScape balance under the owner's delegation: divisor 1,000 "
    "and scaled-buy-limit/minimum fallbacks are estimates, not observed volumes, "
    "emulator-derived algorithms or period-authentic constants. Missing reference "
    "data does not imply zero historical trading."
)
RS3_VOLUME_HIGHS = MappingProxyType(json.loads(
    Path(__file__).with_name("rs3_volume_highs.json").read_text(encoding="utf-8")
))


def daily_sell_demand_capacity_pure(item_name, buy_limit):
    displayed = RS3_VOLUME_HIGHS.get(item_name)
    if displayed is not None:
        return int(Decimal(displayed[:-1]) * 1_000_000) // PLAYER_VOLUME_DIVISOR
    if isinstance(buy_limit, int) and not isinstance(buy_limit, bool) and buy_limit > 0:
        return max(1, buy_limit * 2200 // 25000)
    return 1
