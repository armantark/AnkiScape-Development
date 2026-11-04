"""Bank item conversions use the same recipes and direct-action undo as reviews."""

from .constants import UTILITY_ACTIVITY_DATA
from ..logic.flash_powder_factory_logic import convert_rogue_kit_pure
from ..logic_pure.logic_pure import apply_utility_activity_pure


_DYE_MIX_ACTIVITIES = ("mix_orange_dye", "mix_green_dye", "mix_purple_dye")


def dye_mix_options_pure(player_data: dict, item_name: str) -> tuple:
    inventory = player_data.get("inventory") or {}
    if inventory.get(item_name, 0) <= 0:
        return ()
    rows = []
    for activity_id in _DYE_MIX_ACTIVITIES:
        spec = UTILITY_ACTIVITY_DATA[activity_id]
        inputs = spec["requirements"]
        if item_name not in inputs:
            continue
        partner = next(item for item in inputs if item != item_name)
        if inventory.get(partner, 0) > 0:
            rows.append({
                "activity_id": activity_id,
                "partner": partner,
                "output_item": spec["output_item"],
            })
    return tuple(rows)


def mix_dye_pure(player_data: dict, activity_id: str) -> tuple:
    if activity_id not in _DYE_MIX_ACTIVITIES:
        return player_data, False
    inventory, _xp, ok, _count = apply_utility_activity_pure(
        activity_id, player_data.get("inventory") or {}, UTILITY_ACTIVITY_DATA
    )
    if not ok:
        return player_data, False
    return {**player_data, "inventory": inventory}, True


def mix_dye(addon, activity_id: str) -> bool:
    committed = addon.commit_direct_action(
        lambda current: mix_dye_pure(current, activity_id)
    )
    if committed:
        addon._refresh_skill_availability()
        addon.update_review_hud(addon._state.player_data, addon._state.current_skill)
    return committed


def convert_rogue_kit(addon, output_item):
    """Convert one Rogue kit into its chosen tool as an undoable Bank action."""
    info = {}

    def change(current):
        updated, ok, result = convert_rogue_kit_pure(current, str(output_item))
        info.update(result)
        return updated, ok

    if not addon.commit_direct_action(change):
        return None
    addon._refresh_skill_availability()
    try:
        addon.update_review_hud(addon._state.player_data, addon._state.current_skill)
    except AttributeError:
        pass
    return info
