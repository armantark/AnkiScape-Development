"""Main-menu gathering Keep/Drop and combat loot preferences."""


# Keep/Drop is a gathering choice (power-gather = drop the product for the
# fastest XP). Resolve it against the currently-selected gathering target.
_GATHERING_HANDLER_KEYS = {"mining", "woodcutting", "fishing", "hunter"}


def _current_gathering_target(addon):
    player_data = addon._state.player_data
    handler_key = addon.review_action_handler_key(addon._state.current_skill)
    if handler_key not in _GATHERING_HANDLER_KEYS:
        return None
    target_key = addon.runtime_actions._OVERLAY_TARGET_KEYS.get(handler_key)
    target_id = player_data.get(target_key) if target_key else None
    return str(target_id) if target_id else None


def current_gathering_keep_drop_state(addon):
    player_data = addon._state.player_data
    target_id = _current_gathering_target(addon)
    if target_id is None:
        return None
    return (player_data.get("carried_keep_drop") or {}).get(target_id, "keep")


def set_carried_keep_drop(addon, drop: bool):
    player_data = addon._state.player_data
    target_id = _current_gathering_target(addon)
    if target_id is None:
        return
    keep_drop = player_data.get("carried_keep_drop")
    if not isinstance(keep_drop, dict):
        keep_drop = {}
    if drop:
        keep_drop[target_id] = "drop"
    else:
        keep_drop.pop(target_id, None)
    player_data["carried_keep_drop"] = keep_drop
    addon.save_player_data()


def current_combat_loot_rows(addon):
    # Advanced per-drop loot control for the enemy currently selected. Each row
    # is {item, mode} where mode is auto/keep/leave from loot_overrides.
    player_data = addon._state.player_data
    if addon.review_action_handler_key(addon._state.current_skill) != "combat":
        return ()
    target_id = player_data.get("current_combat_target")
    overrides = player_data.get("loot_overrides") or {}
    rows = []
    for item_name in addon.combat_observed_drop_item_names_pure(player_data, target_id):
        rows.append({"item": item_name, "mode": overrides.get(item_name, "auto")})
    return tuple(rows)


def set_loot_override(addon, item_name: str, mode: str):
    player_data = addon._state.player_data
    overrides = player_data.get("loot_overrides")
    if not isinstance(overrides, dict):
        overrides = {}
    if mode in ("keep", "leave"):
        overrides[item_name] = mode
    else:
        overrides.pop(item_name, None)
    player_data["loot_overrides"] = overrides
    addon.save_player_data()
