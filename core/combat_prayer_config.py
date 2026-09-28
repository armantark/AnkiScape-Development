"""Save changes behind the Combat panel's Prayer and per-target preset controls."""

from ..logic_pure.logic_pure import sanitize_prayer_selection_pure


def _stored(value):
    return list(value) if isinstance(value, list) else value


def _pinned_target_presets(data, target_id, pinned):
    pins = dict(data.get("combat_target_presets", {}) or {})
    if pinned:
        pins[target_id] = str(data.get("combat_active_preset", "Default"))
    else:
        pins.pop(target_id, None)
    return pins


def _toggled_target_overrides(data, target_id, field, enabled):
    overrides = dict(data.get("combat_target_overrides", {}) or {})
    target_overrides = dict(overrides.get(target_id, {}) or {})
    if enabled:
        target_overrides[field] = _stored(data.get(field))
    else:
        target_overrides.pop(field, None)
    if target_overrides:
        overrides[target_id] = target_overrides
    else:
        overrides.pop(target_id, None)
    return overrides


def _set_prayer_field(data, target_id, key, value):
    data[key] = value
    if key == "combat_prayer_book" and value == "curses":
        temple = (data.get("quests", {}) or {}).get("the_temple_at_senntisten") or {}
        if not temple.get("completed"):
            data[key] = "standard"
    data["combat_selected_prayers"] = list(
        sanitize_prayer_selection_pure(data, data.get("combat_selected_prayers", ()))
    )
    # A field the current target overrides takes the player's new choice, so the
    # override does not silently put the old value back when it is next applied.
    overrides = data.get("combat_target_overrides", {}) or {}
    target_overrides = overrides.get(target_id)
    if isinstance(target_overrides, dict) and key in target_overrides:
        data["combat_target_overrides"] = {
            **overrides,
            target_id: {**target_overrides, key: _stored(data[key])},
        }


def apply_combat_prayer_config_pure(player_data, key, value):
    """Return the save after one Prayer, preset pin, or target override choice.

    Applying or saving a named preset is not handled here: those replace many
    fields at once and go through the Combat preset rules instead.
    """
    data = dict(player_data)
    target_id = str(data.get("current_combat_target", ""))
    if key == "pin_target_preset":
        data["combat_target_presets"] = _pinned_target_presets(data, target_id, bool(value))
    elif key == "target_override":
        field, enabled = value
        data["combat_target_overrides"] = _toggled_target_overrides(
            data, target_id, str(field), enabled
        )
    else:
        _set_prayer_field(data, target_id, key, value)
    return data
