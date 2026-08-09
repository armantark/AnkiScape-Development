"""logic_pure_state.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from ..data.potion_data import POTION_FAMILIES, potion_dose_name, potion_flask_name

from ..data.combat_data import (
    COMBAT_ATTACK_STYLE_DATA,
    COMBAT_ANTIPOISON_POTION_DATA,
    COMBAT_BURST_TICKS,
    COMBAT_ENEMY_DATA,
    COMBAT_FOOD_DATA,
    CONSUMABLE_DATA,
    KEBAB_DRAINABLE_SKILLS,
    COMBAT_MAGIC_STAFF_DATA,
    COMBAT_MAGIC_SPELL_DATA,
    COMBAT_RANGED_AMMO_DATA,
    COMBAT_RANGED_WEAPON_DATA,
    DEFAULT_COMBAT_ATTACK_STYLE,
    DEFAULT_COMBAT_SPELL,
    DEFAULT_COMBAT_TARGET,
    MAGIC_FORMULA_SOURCE_PATH,
    MAGIC_STRATEGY_SOURCE_PATH,
    MELEE_FORMULA_SOURCE_PATH,
    MELEE_STRATEGY_SOURCE_PATH,
    POTION_TYPE_SOURCE_PATH,
    RANGED_FORMULA_SOURCE_PATH,
    RANGED_STRATEGY_SOURCE_PATH,
    WEAPON_TYPE_ATTACK_STYLES,
    WEAPON_TYPE_UNARMED_STYLES,
)


def _requirements_from_spec(spec):
    return spec.get("requirements") or spec.get("ore_required", {})


def _positive_int(value, default=1):
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _non_negative_int(value, default=0):
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0 else default


def _non_negative_float(value, default=0.0):
    if isinstance(value, bool):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0.0 else default


COMBAT_BANK_RUN_REVIEWS = 2


COMBAT_GRAVE_RECOVERY_REVIEWS = 5
# An AnkiScape safety abstraction, not a period mechanic: below this share of
# maximum lifepoints with nothing left to eat and nothing bankable to fetch, the
# next burst is refused and the player is asked whether to leave. The period had
# no such prompt; it also had a human watching the health bar in real time.
COMBAT_NEAR_DEATH_PERCENT = 20


# `sendPVPItemsOnDeath` keeps three items on an unskulled death. AnkiScape has no
# skull timer, so every player-versus-player death it models is unskulled.
COMBAT_PVP_DEATH_KEPT_ITEMS = 3


def default_combat_supply_loadout_pure():
    return {
        "food": {},
        "potions": {},
        "stat_potions": {},
        "ammo": {},
        "runes": {},
        "finishers": {},
        "hazards": {},
        "cannonballs": 0,
    }


def _sanitize_combat_supply_loadout(raw_loadout):
    loadout = default_combat_supply_loadout_pure()
    if not isinstance(raw_loadout, Mapping):
        return loadout
    raw_food = raw_loadout.get("food", {})
    if isinstance(raw_food, Mapping):
        loadout["food"] = {
            str(item_name): _non_negative_int(amount, 0)
            for item_name, amount in raw_food.items()
            if isinstance(item_name, str) and item_name in COMBAT_FOOD_DATA and _non_negative_int(amount, 0) > 0
        }
    raw_potions = raw_loadout.get("potions", {})
    if isinstance(raw_potions, Mapping):
        loadout["potions"] = {
            str(item_name): _non_negative_int(amount, 0)
            for item_name, amount in raw_potions.items()
            if isinstance(item_name, str)
            and (
                item_name in COMBAT_ANTIPOISON_POTION_DATA
                or item_name in _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES
            )
            and _non_negative_int(amount, 0) > 0
        }
    raw_stat_potions = raw_loadout.get("stat_potions", {})
    if isinstance(raw_stat_potions, Mapping):
        loadout["stat_potions"] = {
            str(item_name): _non_negative_int(amount, 0)
            for item_name, amount in raw_stat_potions.items()
            if isinstance(item_name, str)
            and item_name in _COMBAT_STAT_POTION_ITEM_NAMES
            and _non_negative_int(amount, 0) > 0
        }
    for key in ("ammo", "runes"):
        raw_mapping = raw_loadout.get(key, {})
        if isinstance(raw_mapping, Mapping):
            loadout[key] = {
                str(item_name): _non_negative_int(amount, 0)
                for item_name, amount in raw_mapping.items()
                if isinstance(item_name, str) and _non_negative_int(amount, 0) > 0
            }
    raw_finishers = raw_loadout.get("finishers", {})
    if isinstance(raw_finishers, Mapping):
        loadout["finishers"] = {
            str(item_name): _non_negative_int(amount, 0)
            for item_name, amount in raw_finishers.items()
            if isinstance(item_name, str) and _non_negative_int(amount, 0) > 0
        }
    raw_hazards = raw_loadout.get("hazards", {})
    if isinstance(raw_hazards, Mapping):
        loadout["hazards"] = {
            str(item_name): _non_negative_int(amount, 0)
            for item_name, amount in raw_hazards.items()
            if isinstance(item_name, str) and _non_negative_int(amount, 0) > 0
        }
    loadout["cannonballs"] = _non_negative_int(raw_loadout.get("cannonballs", 0), 0)
    return loadout


def _sanitize_combat_bank_run(raw_bank_run):
    if not isinstance(raw_bank_run, Mapping):
        return {}
    reviews_remaining = _non_negative_int(raw_bank_run.get("reviews_remaining", 0), 0)
    if reviews_remaining <= 0:
        return {}
    state = {"reviews_remaining": min(reviews_remaining, COMBAT_BANK_RUN_REVIEWS)}
    target_id = raw_bank_run.get("target_id")
    if isinstance(target_id, str) and target_id:
        state["target_id"] = target_id
    return state


def _combat_grave_items(raw_grave):
    if not isinstance(raw_grave, Mapping):
        return []
    raw_items = raw_grave.get("items", ()) or ()
    if not isinstance(raw_items, Iterable) or isinstance(raw_items, (str, bytes)):
        return []
    return [str(item_name) for item_name in raw_items if isinstance(item_name, str) and item_name]


def _combat_stored_loadout(raw_state):
    """The worn slot->item snapshot taken at death, used to auto-re-equip on
    reclaim. Absent/malformed entries just drop the piece back into the pack."""
    if not isinstance(raw_state, Mapping):
        return {}
    raw_loadout = raw_state.get("loadout", {}) or {}
    if not isinstance(raw_loadout, Mapping):
        return {}
    return {
        str(slot): str(name)
        for slot, name in raw_loadout.items()
        if isinstance(slot, str) and slot and isinstance(name, str) and name
    }


def _sanitize_combat_grave_state(raw_grave):
    if not isinstance(raw_grave, Mapping):
        return {}
    items = _combat_grave_items(raw_grave)
    if not items:
        return {}
    reviews_remaining = _positive_int(
        raw_grave.get("reviews_remaining", COMBAT_GRAVE_RECOVERY_REVIEWS),
        COMBAT_GRAVE_RECOVERY_REVIEWS,
    )
    source = raw_grave.get("source", "combat_death")
    state = {
        "items": items,
        "reviews_remaining": min(reviews_remaining, COMBAT_GRAVE_RECOVERY_REVIEWS),
        "source": source if isinstance(source, str) and source else "combat_death",
    }
    travel_reviews = _positive_int(raw_grave.get("travel_reviews", 0), 0)
    walk_reviews = _positive_int(raw_grave.get("walk_reviews_remaining", 0), 0)
    if travel_reviews:
        state["travel_reviews"] = travel_reviews
    if walk_reviews:
        state["walk_reviews_remaining"] = walk_reviews
    target_id = raw_grave.get("target_id")
    if isinstance(target_id, str) and target_id:
        state["target_id"] = target_id
    loadout = _combat_stored_loadout(raw_grave)
    if loadout:
        state["loadout"] = loadout
    return state


def _sanitize_death_office_state(raw_office):
    if not isinstance(raw_office, Mapping):
        return {}
    raw_items = raw_office.get("items", ()) or ()
    if not isinstance(raw_items, Iterable) or isinstance(raw_items, (str, bytes)):
        return {}
    items = [str(item_name) for item_name in raw_items if isinstance(item_name, str) and item_name]
    if not items:
        return {}
    state = {"items": items, "source": str(raw_office.get("source", "combat_death_office"))}
    stored_cost = _non_negative_int(raw_office.get("reclaim_cost", 0), 0)
    if stored_cost > 0:
        state["reclaim_cost"] = stored_cost
    loadout = _combat_stored_loadout(raw_office)
    if loadout:
        state["loadout"] = loadout
    return state


def _signed_int(value, default=0):
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _build_combat_potion_dose_lookup():
    """dose-item-name -> (base_name, skills, strategy, dose_int, is_flask) for every
    stat potion the combat loadout can auto-drink. Includes both the (1)-(4) vials
    and the (1)-(6) flasks — a flask holds more doses, so it lasts longer per slot."""
    lookup = {}
    for base_name, spec in POTION_FAMILIES.items():
        skills = tuple(spec["skills"])
        strategy = str(spec["strategy"])
        for dose in spec["doses"]:
            lookup[potion_dose_name(base_name, dose)] = (base_name, skills, strategy, int(dose), False)
        for dose in spec.get("flask_doses", {}):
            lookup[potion_flask_name(base_name, dose)] = (base_name, skills, strategy, int(dose), True)
    return lookup


_COMBAT_STAT_POTION_BY_DOSE = _build_combat_potion_dose_lookup()


_COMBAT_STAT_POTION_ITEM_NAMES = frozenset(
    item_name
    for item_name, entry in _COMBAT_STAT_POTION_BY_DOSE.items()
    if entry[1]
)


_COMBAT_DRAGONFIRE_POTION_BY_DOSE = {
    item_name: entry
    for item_name, entry in _COMBAT_STAT_POTION_BY_DOSE.items()
    if entry[2] in {"antifire", "super_antifire"}
}


_COMBAT_DRAGONFIRE_POTION_ITEM_NAMES = frozenset(
    _COMBAT_DRAGONFIRE_POTION_BY_DOSE
)


def _copy_player_data_with_nested(player_data):
    def _copy_quest_side_state(key):
        raw_collection = player_data.get(key, {}) or {}
        if not isinstance(raw_collection, Mapping):
            return {}
        copied_collection = {}
        for quest_id, raw_values in raw_collection.items():
            if isinstance(raw_values, Mapping):
                copied_collection[str(quest_id)] = dict(raw_values)
            elif isinstance(raw_values, (list, tuple, set)):
                copied_collection[str(quest_id)] = list(raw_values)
            else:
                copied_collection[str(quest_id)] = raw_values
        return copied_collection

    copied = dict(player_data)
    copied["inventory"] = dict(player_data.get("inventory", {}) or {})
    raw_carried_inventory = player_data.get("carried_inventory", {}) or {}
    copied["carried_inventory"] = {
        str(target_id): dict(items) if isinstance(items, Mapping) else {}
        for target_id, items in (raw_carried_inventory.items() if isinstance(raw_carried_inventory, Mapping) else ())
    }
    copied["equipment"] = dict(player_data.get("equipment", {}) or {})
    copied["quests"] = {
        str(quest_id): dict(state) if isinstance(state, Mapping) else {}
        for quest_id, state in (player_data.get("quests", {}) or {}).items()
    }
    copied["claims"] = {
        str(claim_id): dict(state) if isinstance(state, Mapping) else {}
        for claim_id, state in (player_data.get("claims", {}) or {}).items()
    }
    copied["wicked_hood"] = dict(player_data.get("wicked_hood", {}) or {})
    copied["runecrafting_pouches"] = {
        str(pouch_id): dict(state) if isinstance(state, Mapping) else {}
        for pouch_id, state in (player_data.get("runecrafting_pouches", {}) or {}).items()
    }
    copied["quest_combat_encounters"] = _copy_quest_side_state("quest_combat_encounters")
    copied["quest_combat_encounter_counts"] = _copy_quest_side_state("quest_combat_encounter_counts")
    copied["quest_combat_active_encounters"] = sanitize_quest_combat_active_encounters_pure(
        player_data.get("quest_combat_active_encounters")
    )
    copied["quest_stage_actions"] = _copy_quest_side_state("quest_stage_actions")
    copied["quest_route_states"] = _copy_quest_side_state("quest_route_states")
    copied["combat_encounter"] = dict(player_data.get("combat_encounter", {}) or {})
    copied["combat_kill_counts"] = dict(player_data.get("combat_kill_counts", {}) or {})
    copied["combat_last_result"] = dict(player_data.get("combat_last_result", {}) or {})
    copied["combat_grave"] = _sanitize_combat_grave_state(player_data.get("combat_grave", {}) or {})
    copied["death_office"] = _sanitize_death_office_state(player_data.get("death_office", {}) or {})
    copied["combat_auto_eat_food"] = list(player_data.get("combat_auto_eat_food", []) or [])
    copied["combat_supply_loadout"] = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    copied["combat_current_levels"] = dict(player_data.get("combat_current_levels", {}) or {})
    copied["skilling_current_levels"] = dict(
        player_data.get("skilling_current_levels", {}) or {}
    )
    copied["skilling_potion_targets"] = {
        str(skill_id): dict(targets) if isinstance(targets, Mapping) else {}
        for skill_id, targets in (
            (player_data.get("skilling_potion_targets", {}) or {}).items()
            if isinstance(player_data.get("skilling_potion_targets", {}), Mapping)
            else ()
        )
    }
    copied["cooking_equipment_choices"] = dict(
        player_data.get("cooking_equipment_choices", {}) or {}
    )
    copied["cooking_equipment_swap"] = dict(
        player_data.get("cooking_equipment_swap", {}) or {}
    )
    copied["combat_status_effects"] = dict(player_data.get("combat_status_effects", {}) or {})
    copied["combat_recovery_progress"] = dict(player_data.get("combat_recovery_progress", {}) or {})
    copied["combat_bank_run"] = _sanitize_combat_bank_run(player_data.get("combat_bank_run"))
    copied["item_charges"] = dict(player_data.get("item_charges", {}) or {})
    copied["unlocked_abilities"] = list(player_data.get("unlocked_abilities", []) or [])
    return copied


def quest_state_pure(player_data, quest_id):
    raw_quests = player_data.get("quests", {}) or {}
    state = raw_quests.get(quest_id, {}) if isinstance(raw_quests, Mapping) else {}
    if not isinstance(state, Mapping):
        state = {}
    return {
        "started": bool(state.get("started", False)),
        "completed": bool(state.get("completed", False)),
        "progress": max(0, _positive_int(state.get("progress", 0), 0)),
    }


def quest_completed_pure(player_data, quest_id):
    return bool(quest_state_pure(player_data, quest_id).get("completed", False))


def sanitize_quest_combat_active_encounters_pure(raw_state):
    if not isinstance(raw_state, Mapping):
        return {}
    clean = {}
    for quest_id, raw_encounters in raw_state.items():
        if not isinstance(quest_id, str) or not isinstance(raw_encounters, Mapping):
            continue
        clean_encounters = {}
        for encounter_id, raw_lifepoints in raw_encounters.items():
            if not isinstance(encounter_id, str):
                continue
            lifepoints = _non_negative_int(raw_lifepoints, 0)
            if lifepoints > 0:
                clean_encounters[encounter_id] = lifepoints
        if clean_encounters:
            clean[quest_id] = clean_encounters
    return clean
