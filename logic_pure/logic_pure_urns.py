"""logic_pure_urns.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from ..data.prayer_data import (
    COMBAT_PRAYERS_BY_ID,
    AUTO_PRAYER_TICKS_PER_ITEM,
    PRAYER_MATERIALS,
    PRAYER_UPTIME_POLICIES,
    SAP_SOURCE,
    LEECH_SOURCE,
    resolve_prayer_selection_pure,
)

from ..data.prayer_passive_data import (
    BONECRUSHER_ITEM_NAME,
    ECTOPLASMATOR_ITEM_NAME,
    ECTOPLASMATOR_XP_BY_ENEMY_ID,
)
from ..data.urn_data import (
    MAX_NONEMPTY_URNS_PER_SKILL,
    URN_CARRIED_TARGET_KEYS,
    URN_TIERS_BY_FULL_ITEM,
    URN_TIERS_BY_ID,
    URN_TIERS_BY_SKILL,
    materialize_urn_layout_pure,
    sanitize_urn_state_pure,
    urn_action_event_pure,
    urn_tier_accepts_event_pure,
)

from ..logic_pure.logic_pure_telemetry import (  # noqa: F401  (re-export)
    action_telemetry_key_pure,
    default_achievement_progress_pure,
    default_action_telemetry_pure,
    record_achievement_progress_pure,
    record_action_telemetry_pure,
    record_cadence_wait_telemetry_pure,
    sanitize_achievement_progress_pure,
    sanitize_action_telemetry_pure,
    summarize_action_telemetry_pure,
)

from ..logic_pure.logic_pure_state import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_telemetry import (
    record_action_telemetry_pure,
)

from ..logic_pure.logic_pure_state import (
    _copy_player_data_with_nested,
    _non_negative_float,
    _non_negative_int,
)


def active_urn_state_pure(player_data, skill_id):
    tier_id = player_data.get(f"active_urn_{skill_id}", "")
    tier = URN_TIERS_BY_ID.get(tier_id)
    if tier is None or tier.skill_id != skill_id:
        return None
    inventory = player_data.get("inventory", {}) or {}
    if _non_negative_int(inventory.get(tier.item_active, 0), 0) <= 0:
        return None
    progress = min(tier.capacity_base_xp, _non_negative_float(player_data.get(f"urn_progress_{skill_id}", 0.0), 0.0))
    return {"tier_id": tier.id, "progress": progress, "capacity": tier.capacity_base_xp, "item": tier.item_active}


def nonempty_urn_count_pure(player_data, skill_id):
    inventory = player_data.get("inventory", {}) or {}
    total = 0
    for tier in URN_TIERS_BY_SKILL.get(skill_id, ()):
        total += _non_negative_int(inventory.get(tier.item_active, 0), 0)
        total += _non_negative_int(inventory.get(tier.item_full, 0), 0)
    return total


def charge_training_urn_pure(
    player_data,
    skill_id,
    resource_id,
    resource_level,
    base_xp,
    carried_target_id=None,
):
    """Charge one skill family's urns from source base XP, preserving overflow.

    Physical urn transitions require the selected target's carried view. Banked
    urns and urns carried for another target remain untouched.
    """
    try:
        remaining = max(0.0, float(base_xp))
    except (TypeError, ValueError, OverflowError):
        remaining = 0.0
    info = {
        "charged": False,
        "base_xp_charged": 0.0,
        "overflow_base_xp": remaining,
        "activated": (),
        "filled": (),
    }
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_urn_state_pure(data))
    if remaining <= 0.0 or skill_id not in URN_TIERS_BY_SKILL or not isinstance(carried_target_id, str) or not carried_target_id:
        return data, info

    inventory = data.setdefault("inventory", {})
    carried_map = data.setdefault("carried_inventory", {})
    raw_carried = carried_map.get(carried_target_id, {})
    carried_items = dict(raw_carried) if isinstance(raw_carried, Mapping) else {}

    def available_count(item_name):
        return min(
            _non_negative_int(inventory.get(item_name, 0), 0),
            _non_negative_int(carried_items.get(item_name, 0), 0),
        )

    def adjust_item(item_name, delta):
        inventory[item_name] = max(0, _non_negative_int(inventory.get(item_name, 0), 0) + delta)
        new_count = max(0, _non_negative_int(carried_items.get(item_name, 0), 0) + delta)
        if new_count > 0:
            carried_items[item_name] = new_count
        else:
            carried_items.pop(item_name, None)

    active_key = f"active_urn_{skill_id}"
    progress_key = f"urn_progress_{skill_id}"
    activated = []
    filled = []
    charged = 0.0

    while remaining > 1e-9:
        active_id = str(data.get(active_key, "") or "")
        tier = URN_TIERS_BY_ID.get(active_id)
        if tier is not None and available_count(tier.item_active) <= 0:
            break
        if tier is not None and not urn_tier_accepts_event_pure(tier, str(resource_id), resource_level):
            break

        if tier is None:
            if nonempty_urn_count_pure(data, skill_id) >= MAX_NONEMPTY_URNS_PER_SKILL:
                break
            tier = next(
                (
                    candidate
                    for candidate in reversed(URN_TIERS_BY_SKILL[skill_id])
                    if available_count(candidate.item_r) > 0
                    and urn_tier_accepts_event_pure(candidate, str(resource_id), resource_level)
                ),
                None,
            )
            if tier is None:
                break
            adjust_item(tier.item_r, -1)
            adjust_item(tier.item_active, 1)
            data[active_key] = tier.id
            data[progress_key] = 0.0
            activated.append(tier.id)

        progress = min(tier.capacity_base_xp, _non_negative_float(data.get(progress_key, 0.0), 0.0))
        applied = min(remaining, max(0.0, tier.capacity_base_xp - progress))
        if applied <= 1e-9:
            applied = 0.0
        progress += applied
        remaining -= applied
        charged += applied
        data[progress_key] = progress

        if progress + 1e-9 < tier.capacity_base_xp:
            break
        adjust_item(tier.item_active, -1)
        adjust_item(tier.item_full, 1)
        data[active_key] = ""
        data[progress_key] = 0.0
        filled.append(tier.id)

    if carried_items:
        carried_map[carried_target_id] = carried_items
    else:
        carried_map.pop(carried_target_id, None)
    data["inventory"] = inventory
    info.update(
        {
            "charged": charged > 0.0,
            "base_xp_charged": charged,
            "overflow_base_xp": max(0.0, remaining),
            "activated": tuple(activated),
            "filled": tuple(filled),
        }
    )
    return data, info


def charge_training_urn_for_action_pure(
    player_data,
    skill_id,
    action_id,
    action_spec,
    base_xp,
    output_item=None,
    carried_target_id=None,
):
    event = urn_action_event_pure(skill_id, action_id, action_spec, float(base_xp or 0.0), output_item)
    if event is None:
        data = _copy_player_data_with_nested(player_data)
        data.update(sanitize_urn_state_pure(data))
        return data, {"charged": False, "base_xp_charged": 0.0, "overflow_base_xp": float(base_xp or 0.0), "activated": (), "filled": ()}
    resource_id, resource_level, source_base_xp = event
    return charge_training_urn_pure(
        player_data,
        skill_id,
        resource_id,
        resource_level,
        source_base_xp,
        carried_target_id,
    )


def full_urn_teleport_info_pure(player_data, item_name):
    """Describe whether one full urn can teleport from its current target pack."""
    tier = URN_TIERS_BY_FULL_ITEM.get(item_name)
    if tier is None:
        return None
    target_key = URN_CARRIED_TARGET_KEYS.get(tier.skill_id)
    target_id = str(player_data.get(target_key, "") or "") if target_key else ""
    inventory = player_data.get("inventory", {}) or {}
    carried = player_data.get("carried_inventory", {}) or {}
    view = carried.get(target_id, {}) if isinstance(carried, Mapping) and target_id else {}
    inventory_count = _non_negative_int(inventory.get(tier.item_full, 0), 0) if isinstance(inventory, Mapping) else 0
    carried_count = min(
        inventory_count,
        _non_negative_int(view.get(tier.item_full, 0), 0) if isinstance(view, Mapping) else 0,
    )
    return {
        "urn_id": tier.id,
        "item_name": tier.item_full,
        "skill_id": tier.skill_id,
        "target_id": target_id,
        "teleport_xp": tier.teleport_xp,
        "inventory_count": inventory_count,
        "carried_count": carried_count,
        "eligible": bool(target_id and carried_count > 0),
    }


def teleport_full_urn_pure(player_data, urn_id):
    tier = URN_TIERS_BY_ID.get(urn_id)
    if tier is None:
        return player_data, 0.0, False, ""
    info = full_urn_teleport_info_pure(player_data, tier.item_full)
    if not info or not info["eligible"]:
        return player_data, 0.0, False, tier.skill_id

    data = _copy_player_data_with_nested(player_data)
    inventory = data.setdefault("inventory", {})
    inventory[tier.item_full] = _non_negative_int(inventory.get(tier.item_full, 0), 0) - 1

    target_id = str(info["target_id"])
    carried = dict(data.get("carried_inventory", {}) or {})
    view = dict(carried.get(target_id, {}) or {})
    remaining_carried = _non_negative_int(info["carried_count"], 0) - 1
    if remaining_carried > 0:
        view[tier.item_full] = remaining_carried
    else:
        view.pop(tier.item_full, None)
    if view:
        carried[target_id] = view
    else:
        carried.pop(target_id, None)
    data["carried_inventory"] = carried

    record_action_telemetry_pure(
        data,
        tier.skill_id,
        f"teleport_{tier.id}",
        True,
        expected_success_chance=1.0,
    )
    if tier.skill_id == "prayer":
        data["prayer_urns_teleported"] = _non_negative_int(data.get("prayer_urns_teleported", 0), 0) + 1
        data["prayer_actions_completed"] = _non_negative_int(data.get("prayer_actions_completed", 0), 0) + 1
    return data, tier.teleport_xp, True, tier.skill_id


def carried_target_item_count_pure(player_data, target_id, item_name):
    if not isinstance(target_id, str) or not target_id:
        return 0
    inventory = player_data.get("inventory", {}) or {}
    carried = player_data.get("carried_inventory", {}) or {}
    view = carried.get(target_id, {}) if isinstance(carried, Mapping) else {}
    if not isinstance(inventory, Mapping) or not isinstance(view, Mapping):
        return 0
    return min(
        _non_negative_int(inventory.get(item_name, 0), 0),
        _non_negative_int(view.get(item_name, 0), 0),
    )


def intercept_bonecrusher_outputs_pure(player_data, carried_target_id, outputs):
    """Consume eligible bone outputs when Bonecrusher is in this target's pack."""
    data = _copy_player_data_with_nested(player_data)
    remaining = {
        str(item_name): _non_negative_int(amount, 0)
        for item_name, amount in (outputs or {}).items()
        if isinstance(item_name, str) and _non_negative_int(amount, 0) > 0
    }
    info = {"count": 0, "prayer_xp": 0.0, "consumed": {}}
    if carried_target_item_count_pure(data, carried_target_id, BONECRUSHER_ITEM_NAME) <= 0:
        return data, remaining, info
    for material in PRAYER_MATERIALS:
        if material.kind != "bone" or material.id == "ancient_bones":
            continue
        amount = remaining.pop(material.item_name, 0)
        if amount <= 0:
            continue
        info["count"] += amount
        info["prayer_xp"] += material.xp * amount
        info["consumed"][material.item_name] = amount
    if info["count"]:
        data["prayer_bonecrusher_triggers"] = _non_negative_int(data.get("prayer_bonecrusher_triggers", 0), 0) + info["count"]
        data["prayer_actions_completed"] = _non_negative_int(data.get("prayer_actions_completed", 0), 0) + info["count"]
    return data, remaining, info


def resolve_prayer_kill_effects_pure(player_data, enemy_id, kill_drops, combat_auto_prayer_training):
    """Resolve target-carried passives before retained drops and auto-training."""
    data = _copy_player_data_with_nested(player_data)
    remaining_drops = {
        str(item_name): _non_negative_int(amount, 0)
        for item_name, amount in (kill_drops or {}).items()
        if isinstance(item_name, str) and _non_negative_int(amount, 0) > 0
    }
    carried_target_id = str(enemy_id or "")
    prayer_xp = 0.0
    auto_ticks = 0
    info = {"bonecrusher": 0, "ectoplasmator": 0, "urn_ashes": 0, "auto_prayer": 0}

    ectoplasmator_xp = ECTOPLASMATOR_XP_BY_ENEMY_ID.get(str(enemy_id))
    if ectoplasmator_xp is not None and carried_target_item_count_pure(data, carried_target_id, ECTOPLASMATOR_ITEM_NAME) > 0:
        prayer_xp += float(ectoplasmator_xp)
        info["ectoplasmator"] = 1
        data["prayer_ectoplasmator_triggers"] = _non_negative_int(data.get("prayer_ectoplasmator_triggers", 0), 0) + 1
        data["prayer_actions_completed"] = _non_negative_int(data.get("prayer_actions_completed", 0), 0) + 1

    data, remaining_drops, bonecrusher_info = intercept_bonecrusher_outputs_pure(
        data,
        carried_target_id,
        remaining_drops,
    )
    prayer_xp += float(bonecrusher_info["prayer_xp"])
    info["bonecrusher"] = int(bonecrusher_info["count"])

    for material in PRAYER_MATERIALS:
        if material.kind != "ash":
            continue
        amount = remaining_drops.get(material.item_name, 0)
        if amount <= 0:
            continue
        retained = 0
        for _index in range(amount):
            charged_data, charge_info = charge_training_urn_pure(
                data,
                "prayer",
                material.item_name,
                None,
                material.xp,
                carried_target_id,
            )
            data = charged_data
            if charge_info.get("charged"):
                info["urn_ashes"] += 1
            else:
                retained += 1
        if retained > 0:
            remaining_drops[material.item_name] = retained
        else:
            remaining_drops.pop(material.item_name, None)
    if info["urn_ashes"]:
        data["prayer_urn_ashes_collected"] = _non_negative_int(data.get("prayer_urn_ashes_collected", 0), 0) + info["urn_ashes"]

    if combat_auto_prayer_training:
        for material in PRAYER_MATERIALS:
            amount = remaining_drops.pop(material.item_name, 0)
            if amount <= 0:
                continue
            prayer_xp += material.xp * amount
            info["auto_prayer"] += amount
            auto_ticks += amount * AUTO_PRAYER_TICKS_PER_ITEM
        if info["auto_prayer"]:
            data["prayer_actions_completed"] = _non_negative_int(data.get("prayer_actions_completed", 0), 0) + info["auto_prayer"]

    return data, remaining_drops, prayer_xp, auto_ticks, info
