"""logic_pure_prayer.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from ..data.prayer_data import (
    COMBAT_PRAYERS_BY_ID,
    AUTO_PRAYER_TICKS_PER_ITEM,
    DEFAULT_PRAYER_TARGET,
    ECTOFUNTUS_MULTIPLIER,
    PRAYER_MATERIALS,
    PRAYER_UPTIME_POLICIES,
    SAP_SOURCE,
    LEECH_SOURCE,
    resolve_prayer_selection_pure,
)

from .logic_pure_construction import (  # noqa: F401  (re-export)
    _LECTERN_SLOTS,
    _construction_has_workbench,
    _construction_nail_stock,
    _consume_construction_nails,
    apply_construction_action_pure,
    construction_target_locked_reasons_pure,
    effective_gilded_altar_multiplier_pure,
    owned_gilded_altar_access_reasons_pure,
    owned_gilded_altar_burner_count_pure,
    owned_gilded_altar_effective_burners_pure,
    owned_gilded_altar_marrentill_required_pure,
    purchase_house_option_pure,
    purchase_house_pure,
)

from .logic_pure_state import (  # noqa: F401  (re-export)
    COMBAT_BANK_RUN_REVIEWS,
    COMBAT_GRAVE_RECOVERY_REVIEWS,
    _COMBAT_DRAGONFIRE_POTION_BY_DOSE,
    _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES,
    _COMBAT_STAT_POTION_BY_DOSE,
    _COMBAT_STAT_POTION_ITEM_NAMES,
    _build_combat_potion_dose_lookup,
    _combat_grave_items,
    _combat_stored_loadout,
    _copy_player_data_with_nested,
    _non_negative_float,
    _non_negative_int,
    _positive_int,
    _requirements_from_spec,
    _sanitize_combat_bank_run,
    _sanitize_combat_grave_state,
    _sanitize_combat_supply_loadout,
    _sanitize_death_office_state,
    _signed_int,
    default_combat_supply_loadout_pure,
    quest_completed_pure,
    quest_state_pure,
    sanitize_quest_combat_active_encounters_pure,
)

from .logic_pure_construction import (
    owned_gilded_altar_access_reasons_pure,
)

from .logic_pure_state import (
    _copy_player_data_with_nested,
    _non_negative_int,
    _positive_int,
    _requirements_from_spec,
)


def prayer_target_locked_reasons_pure(player_data, target_id, prayer_data):
    spec = prayer_data.get(target_id)
    if not isinstance(spec, Mapping):
        return ("Unknown Prayer target",)
    reasons = []
    level = _positive_int(player_data.get("prayer_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if level < required_level:
        reasons.append(f"Prayer level {required_level}")
    inventory = player_data.get("inventory", {}) or {}
    for item_name, amount in _requirements_from_spec(spec).items():
        if _non_negative_int(inventory.get(item_name, 0), 0) < amount:
            reasons.append(f"{item_name} x{amount}")
    return tuple(reasons)


def prayer_selection_locked_reasons_pure(player_data, material_id, ui_method_id, prayer_data):
    resolved = resolve_prayer_selection_pure(material_id, ui_method_id)
    if resolved is None:
        return ("unsupported material and method combination",)
    target_id, gilded_mode = resolved
    reasons = list(prayer_target_locked_reasons_pure(player_data, target_id, prayer_data))
    if gilded_mode == "owned":
        reasons.extend(owned_gilded_altar_access_reasons_pure(player_data, target_id))
    return tuple(dict.fromkeys(reasons))


def apply_prayer_selection_pure(player_data, material_id, ui_method_id, prayer_data):
    """Atomically apply a material/method pair while preserving composite IDs."""
    resolved = resolve_prayer_selection_pure(material_id, ui_method_id)
    if resolved is None:
        return player_data, False, ("unsupported material and method combination",)
    reasons = prayer_selection_locked_reasons_pure(player_data, material_id, ui_method_id, prayer_data)
    if reasons:
        return player_data, False, reasons

    target_id, gilded_mode = resolved
    data = _copy_player_data_with_nested(player_data)
    old_target = str(data.get("current_prayer", ""))
    old_mode = str(data.get("prayer_gilded_mode", "hosted"))
    data["current_prayer"] = target_id
    if gilded_mode is not None:
        data["prayer_gilded_mode"] = gilded_mode
    selection_changed = target_id != old_target or (
        gilded_mode is not None and gilded_mode != old_mode
    )
    if selection_changed:
        data["prayer_gilded_house_search"] = {}
        data["prayer_owned_altar_stint"] = {}
    return data, True, ()


_PRAYER_METHOD_MULTIPLIERS = {
    "bury": ("Bury", 1.0),
    "scatter": ("Scatter", 1.0),
    "ectofuntus": ("Ectofuntus", ECTOFUNTUS_MULTIPLIER),
}


def _prayer_requirements_hint(method: str, mode: str) -> str:
    if method == "gilded_altar" and mode == "owned":
        return "Check the materials and owned altar required for this method."
    return {
        "bury": "Check the bones required for Bury.",
        "scatter": "Check the ashes required for Scatter.",
        "ectofuntus": "Check the bonemeal and buckets of slime required for Ectofuntus.",
        "gilded_altar": "Check the bones required for the hosted gilded altar.",
    }[method]


def prayer_panel_view_pure(player_data, prayer_data):
    """The Prayer panel's method line and its gilded altar mode box.

    The box appears only for a gilded altar target: shown above plain Bury, its
    350% read as Bury's own rate.
    """
    target_id = str(player_data.get("current_prayer", DEFAULT_PRAYER_TARGET))
    spec = prayer_data.get(target_id) or prayer_data[DEFAULT_PRAYER_TARGET]
    material_id = str(spec["material_id"])
    gilded = spec["method"] == "gilded_altar"
    mode = "owned" if player_data.get("prayer_gilded_mode") == "owned" else "hosted"
    altar_target = f"gilded_altar_{material_id}"
    if gilded:
        method = f"Gilded altar ({mode})"
        multiplier = effective_gilded_altar_multiplier_pure(player_data, mode, altar_target)
    else:
        method, multiplier = _PRAYER_METHOD_MULTIPLIERS[spec["method"]]
    owned_multiplier = effective_gilded_altar_multiplier_pure(player_data, "owned", altar_target)
    owned_burners = owned_gilded_altar_effective_burners_pure(player_data, altar_target)
    return {
        "material_id": material_id,
        "requirements_hint": _prayer_requirements_hint(spec["method"], mode),
        "unavailable_warning": "The selected Prayer method is not ready. " + _prayer_requirements_hint(spec["method"], mode),
        "status": f"{method}: {spec['display_name']} · {multiplier:g}x XP",
        "show_gilded_mode": gilded,
        "gilded_mode": mode,
        "gilded_mode_options": (
            ("hosted", "Hosted - 350% XP",
             prayer_selection_locked_reasons_pure(player_data, material_id, "gilded_hosted", prayer_data)),
            ("owned", f"Owned - {owned_multiplier * 100:g}% XP ({owned_burners}/2 burners)",
             prayer_selection_locked_reasons_pure(player_data, material_id, "gilded_owned", prayer_data)),
        ),
    }


def apply_prayer_action_pure(target_id, inventory, prayer_data):
    """Apply one normal Prayer training action; pacing/friction stays runtime-side."""
    spec = prayer_data.get(target_id)
    if not isinstance(spec, Mapping):
        return inventory, 0.0, False, {}
    requirements = _requirements_from_spec(spec)
    if not all(_non_negative_int(inventory.get(name, 0), 0) >= amount for name, amount in requirements.items()):
        return inventory, 0.0, False, {}
    new_inventory = dict(inventory)
    for name, amount in requirements.items():
        new_inventory[name] = _non_negative_int(new_inventory.get(name, 0), 0) - amount
    outputs = {}
    for mapping_name in ("byproducts", "outputs"):
        raw_outputs = spec.get(mapping_name, {}) or {}
        if isinstance(raw_outputs, Mapping):
            for name, amount in raw_outputs.items():
                quantity = _non_negative_int(amount, 0)
                if isinstance(name, str) and quantity > 0:
                    new_inventory[name] = _non_negative_int(new_inventory.get(name, 0), 0) + quantity
                    outputs[name] = outputs.get(name, 0) + quantity
    return new_inventory, float(spec.get("exp", 0.0) or 0.0), True, outputs


def prayer_gilded_search_step_pure(player_data, target_id, rng):
    """Pay the once-per-stint 1..10 review house-search cost for hosted altars."""
    data = _copy_player_data_with_nested(player_data)
    state = data.get("prayer_gilded_house_search", {}) or {}
    if not isinstance(state, Mapping) or state.get("target_id") != target_id:
        try:
            roll = float(rng())
        except (TypeError, ValueError):
            roll = 0.0
        state = {"target_id": target_id, "reviews_remaining": min(10, max(1, int(roll * 10) + 1))}
    remaining = _positive_int(state.get("reviews_remaining", 1), 1) - 1
    data["prayer_gilded_house_search"] = (
        {"target_id": target_id, "reviews_remaining": remaining} if remaining > 0 else {"target_id": target_id, "reviews_remaining": 0}
    )
    return data, remaining <= 0, max(0, remaining)


def clear_prayer_gilded_stint_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    data["prayer_gilded_house_search"] = {}
    return data


def _highest_legal_prayer_candidate_pure(data, candidates, book):
    for prayer in sorted(candidates, key=lambda row: row.level, reverse=True):
        sanitized = sanitize_prayer_selection_pure(data, (prayer.id,), book)
        if sanitized:
            return sanitized[0]
    return None


def sanitize_prayer_selection_pure(player_data, selected, book=None):
    """Enforce level, book, quest, stat gates, and exact prayer conflicts."""
    active_book = book if book in ("standard", "curses") else str(player_data.get("combat_prayer_book", "standard"))
    level = _positive_int(player_data.get("prayer_level", 1), 1)
    defence_level = _positive_int(player_data.get("defense_level", 1), 1)
    quests = player_data.get("quests", {}) or {}
    knight_waves = bool((player_data.get("knight_waves") or {}).get("completed"))
    clean = []
    curse_offence_family = None
    for prayer_id in selected if isinstance(selected, Iterable) and not isinstance(selected, (str, bytes)) else ():
        prayer = COMBAT_PRAYERS_BY_ID.get(str(prayer_id))
        if prayer is None or prayer.book != active_book or prayer.level > level or prayer.defence_level > defence_level:
            continue
        if prayer.quest_gate == "the_temple_at_senntisten" and not bool((quests.get("the_temple_at_senntisten") or {}).get("completed")):
            continue
        if prayer.quest_gate == "knight_waves" and not knight_waves:
            continue

        candidate_family = None
        if prayer.book == "curses":
            if prayer.id.startswith("sap_"):
                candidate_family = "sap"
            elif prayer.id.startswith("leech_"):
                candidate_family = "leech"
            elif prayer.id == "turmoil":
                candidate_family = "turmoil"
            if candidate_family is not None and curse_offence_family not in (None, candidate_family):
                continue

        groups = set(prayer.groups)
        conflicts = set(prayer.conflicts)
        conflict_found = False
        for selected_id in clean:
            selected_prayer = COMBAT_PRAYERS_BY_ID[selected_id]
            selected_groups = set(selected_prayer.groups)
            if groups.intersection(selected_groups):
                conflict_found = True
                break
            if conflicts.intersection(selected_groups) or set(selected_prayer.conflicts).intersection(groups):
                conflict_found = True
                break
        if conflict_found:
            continue

        clean.append(prayer.id)
        if candidate_family is not None:
            curse_offence_family = candidate_family
    return tuple(clean)


def active_prayer_selection_pure(data, *, automatic_protection_prayer=None):
    enabled = bool(data.get("combat_prayers_enabled", True))
    selected = sanitize_prayer_selection_pure(data, data.get("combat_selected_prayers", ())) if enabled else ()
    automatic = automatic_protection_prayer_pure(data, automatic_protection_prayer)
    if not automatic:
        return selected
    ordinary = selected if PRAYER_UPTIME_POLICIES.get(str(data.get("combat_prayer_uptime", "off")), 0.0) > 0 else ()
    return sanitize_prayer_selection_pure(data, (automatic, *ordinary))


def prayer_uptime_fraction_pure(data):
    if not bool(data.get("combat_prayers_enabled", True)):
        return 0.0
    policy = str(data.get("combat_prayer_uptime", "off"))
    if _non_negative_int(data.get("combat_prayer_points", 0), 0) <= 0:
        return 0.0
    return float(PRAYER_UPTIME_POLICIES.get(policy, 0.0))


def automatic_protection_prayer_pure(data, prayer_id):
    if prayer_id is None:
        return None
    selected = sanitize_prayer_selection_pure(data, (prayer_id,))
    if selected and "protection_overhead" in COMBAT_PRAYERS_BY_ID[selected[0]].groups:
        return selected[0]
    return None


def _prayer_effect_uptimes(data, uptime_override, automatic):
    uptime = prayer_uptime_fraction_pure(data) if uptime_override is None else max(0.0, min(1.0, float(uptime_override)))
    if not automatic:
        return uptime, uptime
    ordinary = float(PRAYER_UPTIME_POLICIES.get(str(data.get("combat_prayer_uptime", "off")), 0.0)) if bool(data.get("combat_prayers_enabled", True)) else 0.0
    if ordinary:
        return uptime, min(1.0, uptime / ordinary)
    if uptime_override is None:
        uptime = 1.0 if _non_negative_int(data.get("combat_prayer_points", 0), 0) > 0 else 0.0
    return uptime, uptime


def prayer_effect_state_pure(data, uptime_override=None, *, automatic_protection_prayer=None):
    selected = active_prayer_selection_pure(data, automatic_protection_prayer=automatic_protection_prayer)
    automatic = automatic_protection_prayer_pure(data, automatic_protection_prayer)
    uptime, automatic_uptime = _prayer_effect_uptimes(data, uptime_override, automatic)
    effects = {}
    for prayer_id in selected:
        # Keep the ordinary scalar for live curse ramps; only this overhead is full-time.
        effect_uptime = automatic_uptime if prayer_id == automatic else uptime
        for effect, value in COMBAT_PRAYERS_BY_ID[prayer_id].effects:
            if effect in ("attack", "strength", "defence", "ranged", "ranged_attack", "ranged_strength", "magic"):
                effects[effect] = max(float(effects.get(effect, 1.0)), 1.0 + (float(value) - 1.0) * effect_uptime)
            else:
                effects[effect] = max(float(effects.get(effect, 0.0)), float(value) * effect_uptime)
    effects["uptime"] = uptime
    effects["selected"] = selected
    return effects


CASTLE_WARS_HALO_DRAIN_PRAYERS = frozenset(
    {
        "burst_of_strength",
        "superhuman_strength",
        "ultimate_strength",
        "sharp_eye",
        "hawk_eye",
        "eagle_eye",
        "mystic_will",
        "mystic_lore",
        "mystic_might",
        "chivalry",
        "piety",
        "augury",
        "rigour",
        "sap_warrior",
        "sap_ranger",
        "sap_mage",
        "sap_spirit",
        "leech_attack",
        "leech_ranged",
        "leech_magic",
        "leech_defence",
        "leech_strength",
        "leech_energy",
        "leech_special_attack",
        "turmoil",
    }
)


def _castle_wars_halo_drain_multipliers(data, selected):
    equipment = data.get("equipment")
    if not isinstance(equipment, Mapping) or str(equipment.get("head", "")) != "Saradomin halo":
        return {}
    return {prayer_id: 2.0 / 3.0 for prayer_id in selected if prayer_id in CASTLE_WARS_HALO_DRAIN_PRAYERS}


def prayer_drain_for_ticks_pure(
    points,
    counter,
    selected,
    prayer_bonus,
    ticks,
    uptime,
    drain_multipliers=None,
):
    """2011Scape Prayers.kt counter: sum drainEffect against 60+2*bonus."""
    current = max(0, int(points))
    progress = max(0.0, float(counter))
    resistance = max(1, 60 + 2 * int(prayer_bonus))
    # The emulator drain timer runs every two 0.6-second game ticks.
    multipliers = drain_multipliers if isinstance(drain_multipliers, Mapping) else {}
    rate = sum(
        float(COMBAT_PRAYERS_BY_ID[pid].drain)
        * max(0.0, float(multipliers.get(pid, 1.0)))
        for pid in selected
        if pid in COMBAT_PRAYERS_BY_ID
    ) / 2.0
    for _ in range(max(0, int(ticks))):
        progress += rate * max(0.0, min(1.0, float(uptime)))
        while current > 0 and progress >= resistance:
            current -= 1
            progress -= resistance
        if current <= 0:
            return 0, 0.0
    return current, progress


def prayer_drain_and_effective_uptime_pure(
    points,
    counter,
    selected,
    prayer_bonus,
    ticks,
    uptime,
    drain_multipliers=None,
):
    """Drain tick-by-tick and report the burst fraction for which Prayer remained active."""
    current = max(0, int(points))
    progress = max(0.0, float(counter))
    total_ticks = max(0, int(ticks))
    active_weight = 0.0
    requested = max(0.0, min(1.0, float(uptime)))
    for _ in range(total_ticks):
        if current <= 0 or requested <= 0:
            break
        active_weight += requested
        current, progress = prayer_drain_for_ticks_pure(
            current,
            progress,
            selected,
            prayer_bonus,
            1,
            requested,
            drain_multipliers,
        )
    return current, progress, (active_weight / total_ticks if total_ticks else 0.0)


def curse_expected_ramp_pure(attacks, kind):
    """Expected per-fight Sap/Leech ramp; each new enemy resets attack count."""
    chance = .25 if kind == "sap" else .20
    expected_stacks = min(5.0, max(0, int(attacks)) * chance)
    if kind == "sap":
        return {"enemy_drain": .10 + .02 * expected_stacks, "self_boost": 0.0, "source": SAP_SOURCE}
    return {"enemy_drain": .10 + .03 * expected_stacks, "self_boost": .05 + .01 * expected_stacks, "source": LEECH_SOURCE}
