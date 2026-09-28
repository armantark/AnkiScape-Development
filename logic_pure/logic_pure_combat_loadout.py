"""The pack and preset a combat burst readies for its target before anything
reads the player's gear. It lives apart from the burst's set-up module because
it needs the combat model and supplies, which share an import cycle with the
engine, and the set-up module stays outside that cycle."""

from typing import Mapping

from .logic_pure_combat_model import apply_combat_preset_pure, apply_combat_target_overrides_pure
from .logic_pure_combat_supplies import _combat_custom_layout_view


def _combat_prepare_target_loadout(data, target_id):
    """Restore an empty carried pack before applying the target's preset, so
    overrides see the same pack as an already active encounter."""
    carried = data.get("carried_inventory")
    current_view = carried.get(target_id) if isinstance(carried, Mapping) else None
    if not isinstance(current_view, Mapping) or not current_view:
        repacked = _combat_custom_layout_view(data, target_id)
        if repacked:
            carried = dict(carried) if isinstance(carried, Mapping) else {}
            carried[target_id] = repacked
            data["carried_inventory"] = carried
    return _combat_target_loadout(data, target_id)


def _combat_target_loadout(data, target_id):
    pinned_preset = (data.get("combat_target_presets", {}) or {}).get(target_id)
    if isinstance(pinned_preset, str):
        return apply_combat_preset_pure(data, pinned_preset, target_id)[0]
    return apply_combat_target_overrides_pure(data, target_id)
