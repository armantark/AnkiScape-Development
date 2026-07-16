"""Pure review-native run-energy and carried-weight transactions."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgilityTravelProfile:
    handler_key: str
    target_id: str
    base_reviews: float
    adjusted_reviews: float
    level_gain: float
    weight_gain: float
    carried_weight_kg: float
    effective_weight_kg: float
    route_label: str
    source_status: str


# Period-backed or emulator-convergent carried/equipped weights harvested in
# memory-bank/source-audits/agility-carried-weight-inputs-2026-07-15.md.
AGILITY_ITEM_WEIGHTS_KG = {
    "Rune essence": 0.0,
    "Pure essence": 0.0,
    "Small pouch": 1.0,
    "Medium pouch": 1.0,
    "Large pouch": 1.0,
    "Giant pouch": 1.0,
    "Nature tiara": 1.0,
    "Amulet of glory (4)": 0.0,
    "Dragon bones": 1.5,
    "Magic logs": 2.0,
    "Iron ore": 2.25,
    "Raw shark": 0.7,
    "Raw rocktail": 0.3,
    "Red chinchompa": 0.0,
    "Box trap": 0.2,
    "Adamant bar": 2.04,
    "Adamant platebody": 11.0,
    "Green dragon leather": 3.1,
    "Green d'hide body": 6.8,
    "Vial of water": 0.02,
    "Clean torstol": 0.0,
    "Agile top": -12.0,
    "Agile legs": -10.0,
    "Boots of lightness": -4.5,
    "Spotted cape": -2.2,
    "Spottier cape": -4.5,
}


_ROUTE_COSTS = {
    ("runecrafting", "craft_air_runes"): (19.8333333333, "Running to the Air altar", "period"),
    ("runecrafting", "craft_water_runes"): (36.5, "Running to the Water altar", "period"),
    ("runecrafting", "craft_earth_runes"): (24.0, "Running to the Earth altar", "period"),
    ("runecrafting", "craft_fire_runes"): (21.2222222222, "Running to the Fire altar", "period"),
    ("runecrafting", "craft_nature_runes"): (32.3333333333, "Running to the Nature altar", "period"),
    ("crafting", "silver_unstrung_symbol"): (6.75, "Running between the bank and furnace", "period"),
    ("crafting", "silver_unstrung_emblem"): (6.75, "Running between the bank and furnace", "period"),
    ("smithing", "forge_iron_platebody"): (60.0 / 13.0, "Running between the bank and anvil", "period"),
    ("smithing", "forge_adamant_platebody"): (2.8125, "Running between the bank and anvil", "period_candidate"),
}


_HANDLER_DEFAULTS = {
    "mining": (1.0, "weak", "Running to the bank", "ankiscape_trip_abstraction"),
    "woodcutting": (1.0, "weak", "Running to the bank", "ankiscape_trip_abstraction"),
    "fishing": (1.0, "weak", "Running to the bank", "ankiscape_trip_abstraction"),
    "cooking": (1.0, "marginal", "Running to the bank", "ankiscape_trip_abstraction"),
    "firemaking": (1.0, "marginal", "Running to the bank", "ankiscape_trip_abstraction"),
    "smithing": (1.0, "weak", "Running between the bank and workstation", "ankiscape_trip_abstraction"),
    "prayer": (2.678, "strong", "Running to the altar", "ankiscape_prayer_trip_abstraction"),
    "runecrafting": (24.0, "strong", "Running to the altar", "ankiscape_trip_abstraction"),
    "crafting": (0.0, "none", "Working at the bank", "period_route"),
    "hunter": (0.0, "none", "Working at the hunting ground", "period_route"),
    "fletching": (0.0, "none", "Working at the bank", "period_route"),
    "herblore": (0.0, "none", "Working at the bank", "period_route"),
    "thieving": (0.0, "none", "Working on site", "period_route"),
}

_TIER_CEILINGS = {"strong": 0.11, "weak": 0.07, "marginal": 0.03, "none": 0.0}


def _number(value: Any) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    return result if math.isfinite(result) else 0.0


def agility_carried_weight_pure(carried: Any, equipment: Any) -> tuple[float, float]:
    """Return positive pack weight and net run-energy weight, clamped at zero."""
    pack = carried if isinstance(carried, Mapping) else {}
    equipped = equipment if isinstance(equipment, Mapping) else {}
    carried_weight = sum(
        AGILITY_ITEM_WEIGHTS_KG.get(str(item), 0.0) * max(0, int(_number(quantity)))
        for item, quantity in pack.items()
    )
    equipment_weight = sum(
        AGILITY_ITEM_WEIGHTS_KG.get(str(item), 0.0)
        for item in equipped.values()
        if isinstance(item, str)
    )
    return max(0.0, carried_weight), max(0.0, carried_weight + equipment_weight)


def agility_travel_profile_pure(
    handler_key: str,
    target_id: str,
    agility_level: int,
    carried: Any,
    equipment: Any,
) -> AgilityTravelProfile:
    default = _HANDLER_DEFAULTS.get(handler_key, (0.0, "none", "Working on site", "not_applicable"))
    base_reviews, tier, route_label, source_status = default
    route = _ROUTE_COSTS.get((handler_key, target_id))
    if route is not None:
        base_reviews, route_label, source_status = route
        tier = "strong" if handler_key == "runecrafting" else "weak"
    level = max(1, min(99, int(_number(agility_level) or 1)))
    level_gain = _TIER_CEILINGS[tier] * ((level - 1) / 98.0)
    carried_weight, effective_weight = agility_carried_weight_pure(carried, equipment)
    # The harvested model puts Agile's 22 kg reduction on a 56 kg load at
    # roughly +2.8%. This bounded coefficient applies only to moving routes.
    weight_gain = 0.0 if base_reviews <= 0 else min(0.04, max(0.0, carried_weight - effective_weight) * (0.028 / 22.0))
    total_gain = min(0.15, level_gain + weight_gain)
    return AgilityTravelProfile(
        handler_key=handler_key,
        target_id=target_id,
        base_reviews=float(base_reviews),
        adjusted_reviews=max(0.0, float(base_reviews) * (1.0 - total_gain)),
        level_gain=level_gain,
        weight_gain=weight_gain,
        carried_weight_kg=carried_weight,
        effective_weight_kg=effective_weight,
        route_label=route_label,
        source_status=source_status,
    )


def scheduled_travel_reviews_pure(profile: AgilityTravelProfile, roll: float) -> int:
    """Stochastically schedule a fractional trip only when that trip is due."""
    whole = int(math.floor(profile.adjusted_reviews))
    fraction = profile.adjusted_reviews - whole
    return whole + int(max(0.0, min(_number(roll), 1.0)) < fraction)

