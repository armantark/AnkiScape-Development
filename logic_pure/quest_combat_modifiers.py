"""Quest-specific combat modifiers backed by period source evidence."""

from typing import Mapping

from .logic_pure_state import _non_negative_int


_COUNT_DRAYNOR_GARLIC_ENCOUNTER = (
    "vampyre_slayer",
    "vampyre_slayer_count_draynor_37",
)


def quest_combat_inventory_adjusted_stats_pure(
    quest_id, encounter_id, stats, player_data
):
    if (quest_id, encounter_id) != _COUNT_DRAYNOR_GARLIC_ENCOUNTER:
        return stats
    inventory = player_data.get("inventory", {}) if isinstance(player_data, Mapping) else {}
    if not isinstance(inventory, Mapping) or _non_negative_int(inventory.get("Garlic", 0), 0) <= 0:
        return stats
    # Quest items use the flat owned-supply store. Target-local carried views are
    # overlays on that store, and Count Draynor has no configurable target pack.
    adjusted = dict(stats)
    adjusted["strength"] = max(1, adjusted["strength"] - 5)
    adjusted["defence"] = max(1, adjusted["defence"] - 5)
    return adjusted
