"""Main-menu cooking target and equipment-policy actions."""

from ..logic.cooking_gauntlets_logic import cooking_gauntlets_beneficial_pure


def set_cooking_target(addon, target_id: str) -> bool:
    if target_id not in addon.COOKING_DATA:
        return False

    def _change(current):
        updated = dict(current)
        updated["current_cooking"] = target_id
        updated = addon.reconcile_cooking_equipment_pure(
            updated,
            target_id,
            beneficial=cooking_gauntlets_beneficial_pure(
                updated, target_id, cadence_live_enabled=addon._cadence_kernel_enabled()
            ),
        )
        return updated, True

    committed = addon.commit_direct_action(_change)
    if committed:
        addon._refresh_skill_availability()
        try:
            addon.update_review_hud(addon._state.player_data, addon._state.current_skill)
        except Exception:
            pass
    return committed


def set_cooking_equipment_choice(addon, target_id: str, choice: str) -> bool:
    if target_id not in addon.COOKING_DATA:
        return False

    def _change(current):
        updated, ok = addon.set_cooking_equipment_choice_pure(
            current, target_id, choice
        )
        if ok and updated.get("current_cooking") == target_id:
            updated = addon.reconcile_cooking_equipment_pure(
                updated,
                target_id,
                beneficial=cooking_gauntlets_beneficial_pure(
                    updated, target_id, cadence_live_enabled=addon._cadence_kernel_enabled()
                ),
            )
        return updated, ok

    return addon.commit_direct_action(_change)
