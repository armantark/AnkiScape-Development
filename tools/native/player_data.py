"""Build native-check player state without importing the add-on entry point."""

from copy import deepcopy
from difflib import get_close_matches

from ...core.constants import ITEM_DEFINITIONS, ORE_DATA
from ...core.storage_pure import default_player_data, migrate_loaded_data


def _merge(defaults: dict, overrides: dict) -> dict:
    merged = deepcopy(defaults)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def merge_player_data(overrides: dict) -> dict:
    """Merge known save keys recursively; nested keys may extend defaults."""
    if not isinstance(overrides, dict):
        raise ValueError("player data must be a JSON object")
    defaults = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for key in overrides:
        if key not in defaults:
            closest = get_close_matches(key, defaults, n=3, cutoff=0)
            raise ValueError(f"unknown player-data key {key!r}; closest valid names: {closest}")
    return _merge(defaults, overrides)


def migrated_player_data(overrides: dict) -> dict:
    return migrate_loaded_data(merge_player_data(overrides), ORE_DATA, ITEM_DEFINITIONS)
