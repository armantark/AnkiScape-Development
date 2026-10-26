"""logic_pure_quest.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from ..logic.cold_war_greeting_logic import ensure_cold_war_greeting_pure, cold_war_journal_lines_pure
from .quest.oronwen import apply_oronwen_review_pure, oronwen_requirement_pure, oronwen_review_ready_pure
from ..data.equipment_data import EQUIPMENT_BONUS_FIELDS, EquipmentBonuses
from ..data.soul_wars_data import SOUL_WARS_ZEAL_CAP
from ..core.skill_registry import get_skill, trainable_skill_definitions
from ..core.tool_belt import tool_on_belt

from ..logic.treasure_trails_logic import clue_refusal_reason_pure, filter_clue_scroll_outputs_pure

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

from .logic_pure_combat_engine import (  # noqa: F401  (re-export)
    _COMBAT_EXP_KEY_DISPLAY,
    _COMBAT_STYLE_XP_KEYS,
    _combat_roll_damage_lifepoints,
    apply_combat_burst_pure,
    apply_safe_combat_recovery_pure,
    bank_gear_rows_pure,
    combat_attack_style_trained_skills_pure,
    combat_death_office_items_pure,
    combat_death_office_reclaim_cost_pure,
    combat_death_office_summary_pure,
    combat_enemy_pressure_attack_pure,
    combat_has_active_encounter_pure,
    combat_hud_state_pure,
    combat_supply_loadout_summary_pure,
    combat_target_preview_pure,
    combat_weapon_style_options_pure,
    player_combat_level_pure,
    reclaim_death_office_items_pure,
    refill_combat_supply_loadout_pure,
    set_combat_auto_eat_food_pure,
    set_combat_auto_eat_threshold_pure,
    set_combat_pack_mode_pure,
    unload_combat_supply_loadout_pure,
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

from .quest_action_proofs import quest_action_proof_completed_pure, record_quest_stage_action_proofs_pure
from .quest.progress_state import (
    _quest_combat_completed_count,
    _quest_combat_remaining_count,
    _quest_combat_total_quantity,
    _quest_flag_completed,
    quest_combat_prerequisites_completed_pure,
)
from .quest_runtime_rules import (  # noqa: F401  (re-export)
    _requirements_for_unlock_rule,
    _target_ids_for_unlock_rule,
    ability_unlocked_pure,
    quest_combat_inventory_adjusted_stats_pure,
    quest_unlock_locked_reasons_pure,
    target_unlock_locked_reasons_pure,
)

def _trainable_exp_keys():
    return {skill.exp_key for skill in trainable_skill_definitions()}

def _skill_requirement_reason(player_data, requirement):
    if not isinstance(requirement, Mapping):
        return None
    skill_id = requirement.get("skill_id")
    display_name = requirement.get("display_name")
    if not isinstance(skill_id, str):
        return None
    skill = get_skill(skill_id)
    label = str(display_name or (skill.display_name if skill is not None else skill_id.replace("_", " ").title()))
    level_required = _positive_int(requirement.get("level", 1), 1)
    if skill_id == "combat":
        return None if player_combat_level_pure(player_data) >= level_required else f"{label} {level_required}"
    if skill is None or not skill.trainable:
        return f"{label} {level_required} (not implemented)"
    level_key = skill.level_key
    if level_key not in player_data:
        return f"{label} {level_required} (not implemented)"
    if _positive_int(player_data.get(level_key, 1), 1) < level_required:
        return f"{label} {level_required}"
    return None

def quest_locked_reasons_pure(player_data, quest_id, quest_data):
    quest = quest_data.get(quest_id)
    if not quest:
        return ("unknown quest",)
    state = quest_state_pure(player_data, quest_id)
    if state["completed"]:
        return ("completed",)
    if state["started"]:
        return tuple()

    reasons = []
    for requirement in quest.get("required_quests", ()) or ():
        if not isinstance(requirement, Mapping):
            continue
        required_id = requirement.get("quest_id")
        display_name = requirement.get("display_name")
        if not isinstance(required_id, str):
            continue
        if not isinstance(quest_data.get(required_id), Mapping):
            reasons.append(f"{display_name or required_id.replace('_', ' ').title()} (not implemented)")
        elif not quest_completed_pure(player_data, required_id):
            reasons.append(str(display_name or required_id.replace("_", " ").title()))

    for requirement in quest.get("required_skills", ()) or ():
        reason = _skill_requirement_reason(player_data, requirement)
        if reason:
            reasons.append(reason)

    required_quest_points = _positive_int(quest.get("required_quest_points", 0), 0)
    if required_quest_points and _positive_int(player_data.get("quest_points", 0), 0) < required_quest_points:
        reasons.append(f"{required_quest_points} quest points")

    inventory = player_data.get("inventory", {}) or {}
    required_items = quest.get("required_items", {}) or {}
    for item_name, amount in required_items.items():
        if inventory.get(item_name, 0) < amount:
            reasons.append(f"{item_name} x{amount}")
    return tuple(dict.fromkeys(reasons))

def quest_current_stage_pure(player_data, quest_id, quest_data):
    quest = quest_data.get(quest_id)
    if not quest:
        return 0
    state = quest_state_pure(player_data, quest_id)
    if not state["started"]:
        return 0
    total_stages = _positive_int(quest.get("stages", 1), 1)
    if state["completed"]:
        return total_stages
    return min(total_stages, max(1, state["progress"]))

def _quest_stage_item_pairs(requirement, key):
    raw_items = requirement.get(key, {}) if isinstance(requirement, Mapping) else {}
    if isinstance(raw_items, Mapping):
        return tuple((str(name), _positive_int(amount, 1)) for name, amount in raw_items.items())
    if isinstance(raw_items, Iterable) and not isinstance(raw_items, str):
        pairs = []
        for item in raw_items:
            if isinstance(item, Mapping):
                name = item.get("item_name") or item.get("display_name")
                amount = item.get("quantity", item.get("amount", 1))
            elif isinstance(item, (tuple, list)) and len(item) >= 2:
                name, amount = item[0], item[1]
            else:
                continue
            if isinstance(name, str):
                pairs.append((name, _positive_int(amount, 1)))
        return tuple(pairs)
    return tuple()

def _quest_stage_item_option_groups(requirement, key):
    raw_groups = requirement.get(key, ()) if isinstance(requirement, Mapping) else ()
    if isinstance(raw_groups, Mapping):
        return (_quest_stage_item_pairs({key: raw_groups}, key),)
    if not isinstance(raw_groups, Iterable) or isinstance(raw_groups, str):
        return tuple()
    raw_groups = tuple(raw_groups)
    if raw_groups and all(isinstance(raw_group, Mapping) for raw_group in raw_groups):
        pairs = tuple(
            (str(name), _positive_int(amount, 1))
            for raw_group in raw_groups
            for name, amount in raw_group.items()
        )
        return (pairs,) if pairs else tuple()
    groups = []
    for raw_group in raw_groups:
        if isinstance(raw_group, Mapping):
            pairs = tuple((str(name), _positive_int(amount, 1)) for name, amount in raw_group.items())
        elif isinstance(raw_group, Iterable) and not isinstance(raw_group, str):
            pairs = []
            for option in raw_group:
                if isinstance(option, Mapping):
                    pairs.extend((str(name), _positive_int(amount, 1)) for name, amount in option.items())
                elif isinstance(option, (tuple, list)) and len(option) >= 2:
                    pairs.append((str(option[0]), _positive_int(option[1], 1)))
            pairs = tuple(pairs)
        else:
            pairs = tuple()
        if pairs:
            groups.append(pairs)
    return tuple(groups)

def _quest_item_requirement_text(item_name, amount):
    quantity = f" x{amount}" if amount > 1 else " x1"
    return f"{item_name}{quantity}"

def _quest_item_option_reason(options):
    return "Needs " + " or ".join(_quest_item_requirement_text(item_name, amount) for item_name, amount in options)

def _quest_stage_strings(requirement, key):
    raw_values = requirement.get(key, ()) if isinstance(requirement, Mapping) else ()
    if isinstance(raw_values, str):
        return (raw_values,)
    if isinstance(raw_values, Iterable):
        return tuple(str(value) for value in raw_values if str(value))
    return tuple()


_QUEST_ROUTE_INHERITANCE = {
    ("heroes_quest", "Join the Phoenix Gang"): ("shield_of_arrav",),
    ("heroes_quest", "Join the Black Arm Gang"): ("shield_of_arrav",),
}

def _quest_route_completed(player_data, quest_id, route_id):
    if _quest_flag_completed(player_data, "quest_route_states", quest_id, route_id):
        return True
    for source_quest_id in _QUEST_ROUTE_INHERITANCE.get((quest_id, route_id), ()):
        if _quest_flag_completed(player_data, "quest_route_states", source_quest_id, route_id):
            return True
    return False

def _quest_choice_stage(choice):
    return _positive_int(choice.get("stage", 0), 0) if isinstance(choice, Mapping) else 0

def _quest_choice_options(choice):
    if not isinstance(choice, Mapping):
        return tuple()
    rows = []
    for option in choice.get("options", ()) or ():
        if not isinstance(option, Mapping):
            continue
        route_id = str(option.get("route_id") or "").strip()
        label = str(option.get("label") or route_id).strip()
        if not route_id or not label:
            continue
        rows.append(
            {
                "label": label,
                "route_id": route_id,
                "description": str(option.get("description") or ""),
            }
        )
    return tuple(rows)

def _quest_choice_current_stage(player_data, quest_id, quest_data):
    state = quest_state_pure(player_data, quest_id)
    if state["completed"]:
        return 0
    if state["started"]:
        return quest_current_stage_pure(player_data, quest_id, quest_data)
    return 0

def _quest_choice_selected(player_data, quest_id, options):
    return tuple(
        option for option in options
        if _quest_route_completed(player_data, quest_id, option["route_id"])
    )

def _quest_choices_for_stage(player_data, quest_id, quest_data, stage):
    quest = quest_data.get(quest_id)
    if not isinstance(quest, Mapping):
        return tuple()
    rows = []
    for choice in quest.get("choices", ()) or ():
        if not isinstance(choice, Mapping) or _quest_choice_stage(choice) != stage:
            continue
        options = _quest_choice_options(choice)
        if not options:
            continue
        rows.append(
            {
                "stage": stage,
                "prompt": str(choice.get("prompt") or "Choose path"),
                "options": options,
                "source": str(choice.get("source") or ""),
                "selected_options": _quest_choice_selected(player_data, quest_id, options),
            }
        )
    return tuple(rows)

def quest_current_stage_choices_pure(player_data, quest_id, quest_data):
    """Return unresolved player choices for the visible quest stage."""
    stage = _quest_choice_current_stage(player_data, quest_id, quest_data)
    if stage <= 0:
        return tuple()
    choices = _quest_choices_for_stage(player_data, quest_id, quest_data, stage)
    return tuple(choice for choice in choices if not choice["selected_options"])


def _quest_current_stage_choice_blockers(player_data, quest_id, quest_data):
    blockers = []
    for choice in quest_current_stage_choices_pure(player_data, quest_id, quest_data):
        labels = tuple(option["label"] for option in choice["options"])
        reason = "Choose path: " + " or ".join(labels)
        blockers.append(
            _quest_blocker(
                choice["stage"],
                "quest_choice",
                reason,
                choice["source"],
                prompt=choice["prompt"],
                options=choice["options"],
            )
        )
    return tuple(blockers)


def apply_quest_route_choice_pure(player_data, quest_id, quest_data, route_id):
    route_id = str(route_id or "").strip()
    if not route_id or quest_id not in quest_data:
        return player_data, False
    state = quest_state_pure(player_data, quest_id)
    if (state["started"], state["completed"]) != (True, False):
        return player_data, False
    stage = _quest_choice_current_stage(player_data, quest_id, quest_data)
    valid_choices = _quest_choices_for_stage(player_data, quest_id, quest_data, stage)
    matching_choice = None
    for choice in valid_choices:
        if any(option["route_id"] == route_id for option in choice["options"]):
            matching_choice = choice
            break
    if matching_choice is None:
        return player_data, False
    selected = matching_choice["selected_options"]
    if selected:
        return (player_data, True) if any(option["route_id"] == route_id for option in selected) else (player_data, False)

    data = _copy_player_data_with_nested(player_data)
    raw_routes = data.setdefault("quest_route_states", {}).setdefault(quest_id, [])
    if isinstance(raw_routes, str):
        routes = [raw_routes]
    elif isinstance(raw_routes, Mapping):
        routes = [flag for flag, enabled in raw_routes.items() if isinstance(flag, str) and bool(enabled)]
    elif isinstance(raw_routes, Iterable):
        routes = [flag for flag in raw_routes if isinstance(flag, str)]
    else:
        routes = []
    if route_id not in routes:
        routes.append(route_id)
    data["quest_route_states"][quest_id] = routes
    return data, True


_GENERIC_TOOL_SUFFIXES = {"pickaxe": ("pickaxe",), "hatchet": ("hatchet", " axe"), "axe": ("hatchet", " axe")}


def _has_quest_tool(player_data, tool_name, amount):
    inventory = player_data.get("inventory", {}) or {}
    # The belt holds one of each tool; a stage asking for several wants stock.
    if inventory.get(tool_name, 0) >= amount or (amount == 1 and tool_on_belt(player_data, tool_name)):
        return True
    equipment = player_data.get("equipment", {}) or {}
    if isinstance(equipment, Mapping) and tool_name in {str(item_name) for item_name in equipment.values()}:
        return True
    suffixes = _GENERIC_TOOL_SUFFIXES.get(tool_name.lower())
    return bool(suffixes) and any(
        str(name).lower().endswith(suffixes) and count >= amount for name, count in inventory.items()
    )


def _quest_blocker(stage, kind, reason, source="", **extra):
    row = {"stage": stage, "kind": kind, "reason": reason, "source": source}
    row.update(extra)
    return row


def _quest_combat_stats(encounter):
    stats = encounter.get("npc_stats", {}) if isinstance(encounter, Mapping) else {}
    return stats if isinstance(stats, Mapping) else {}


def _quest_combat_configs(encounter):
    configs = encounter.get("npc_configs", {}) if isinstance(encounter, Mapping) else {}
    return configs if isinstance(configs, Mapping) else {}


def _quest_combat_bonuses(encounter):
    bonuses = encounter.get("npc_bonuses", {}) if isinstance(encounter, Mapping) else {}
    return bonuses if isinstance(bonuses, Mapping) else {}


def _quest_combat_attack_style(encounter):
    attack_style = str(_quest_combat_configs(encounter).get("attack_style", "")).lower()
    if attack_style in {"range", "ranged"}:
        return "ranged"
    if attack_style == "magic":
        return "magic"
    if attack_style == "melee":
        return "melee"
    return ""


def _quest_combat_required_stat_keys(encounter):
    style = _quest_combat_attack_style(encounter)
    if style == "magic":
        return ("hitpoints", "defence", "magic")
    if style == "ranged":
        return ("hitpoints", "defence", "ranged")
    return ("hitpoints", "attack", "strength", "defence")


def quest_combat_encounter_has_stats_pure(encounter):
    stats = _quest_combat_stats(encounter)
    required_keys = _quest_combat_required_stat_keys(encounter)
    if all(_positive_int(stats.get(key, 0), 0) > 0 for key in required_keys):
        return True
    # Some source combatdefs explicitly use zero combat levels and drive damage
    # through maxHit. Missing stat keys remain unresolved rather than becoming zero.
    if (
        all(key in stats for key in required_keys)
        and _positive_int(stats.get("hitpoints", 0), 0) > 0
        and all(_non_negative_int(stats[key], -1) == 0 for key in required_keys if key != "hitpoints")
        and _positive_int(_quest_combat_configs(encounter).get("max_hit", 0), 0) > 0
    ):
        return True
    if _quest_combat_attack_style(encounter):
        melee_fallback = ("hitpoints", "attack", "strength", "defence")
        return all(_positive_int(stats.get(key, 0), 0) > 0 for key in melee_fallback)
    return False


def _quest_combat_display(encounter, source=""):
    display_name = str(encounter.get("display_name") or encounter.get("encounter_id") or "combat encounter")
    level = _positive_int(encounter.get("level", 0), 0)
    quantity = _positive_int(encounter.get("quantity", 1), 1)
    level_text = f" level {level}" if level > 0 else ""
    quantity_text = f" x{quantity}" if quantity > 1 else ""
    return display_name, level, quantity, level_text, quantity_text, str(encounter.get("source") or source)


_QUEST_COMBAT_BONUS_ALIASES = {
    "attackStab": "attack_stab",
    "attackSlash": "attack_slash",
    "attackCrush": "attack_crush",
    "attackMagic": "attack_magic",
    "attackRanged": "attack_ranged",
    "defenceStab": "defence_stab",
    "defenceSlash": "defence_slash",
    "defenceCrush": "defence_crush",
    "defenceMagic": "defence_magic",
    "defenceRanged": "defence_ranged",
    "stab_att": "attack_stab",
    "slash_att": "attack_slash",
    "crush_att": "attack_crush",
    "magic_att": "attack_magic",
    "range_att": "attack_ranged",
    "stab_def": "defence_stab",
    "slash_def": "defence_slash",
    "crush_def": "defence_crush",
    "magic_def": "defence_magic",
    "range_def": "defence_ranged",
    "strength": "melee_strength",
    "ranged_strength": "ranged_strength",
    "magic_damage": "magic_damage",
}


def default_quest_combat_active_encounters_pure():
    return {}


def _quest_combat_target_id(quest_id, encounter_id):
    return f"quest:{quest_id}:{encounter_id}"


QUEST_COMBAT_DEFAULT_BURST_TICKS = COMBAT_BURST_TICKS * 10


def _quest_combat_normalized_bonuses(encounter):
    normalized = {}
    for raw_key, raw_value in _quest_combat_bonuses(encounter).items():
        if not isinstance(raw_key, str):
            continue
        key = raw_key if raw_key in EQUIPMENT_BONUS_FIELDS else _QUEST_COMBAT_BONUS_ALIASES.get(raw_key)
        if key in EQUIPMENT_BONUS_FIELDS:
            normalized[key] = _signed_int(raw_value, 0)
    return normalized


def _quest_combat_enemy_spec(quest_id, encounter_id, encounter, player_data=None):
    stats = {
        str(key): _non_negative_int(value, 0)
        for key, value in _quest_combat_stats(encounter).items()
        if isinstance(key, str)
    }
    configs = _quest_combat_configs(encounter)
    attack_style = _quest_combat_attack_style(encounter)
    if attack_style == "magic":
        magic_level = _positive_int(stats.get("magic", 0), 1)
        stats["attack"] = max(_positive_int(stats.get("attack", 0), 0), magic_level)
        stats["strength"] = max(_positive_int(stats.get("strength", 0), 0), magic_level)
    elif attack_style == "ranged":
        ranged_level = _positive_int(stats.get("ranged", 0), 1)
        stats["attack"] = max(_positive_int(stats.get("attack", 0), 0), ranged_level)
        stats["strength"] = max(_positive_int(stats.get("strength", 0), 0), ranged_level)
    stats["hitpoints"] = _positive_int(stats.get("hitpoints", 0), 1)
    stats["attack"] = _positive_int(stats.get("attack", 0), 1)
    stats["strength"] = _positive_int(stats.get("strength", 0), 1)
    stats["defence"] = _positive_int(stats.get("defence", 0), 1)
    stats = quest_combat_inventory_adjusted_stats_pure(
        quest_id, encounter_id, stats, player_data
    )
    display_name, level, _quantity, _level_text, _quantity_text, source = _quest_combat_display(encounter)
    enemy = {
        "display_name": display_name,
        "level": level,
        "stats": stats,
        "bonuses": _quest_combat_normalized_bonuses(encounter),
        "drops": {
            "guaranteed": tuple(
                (item_name, _positive_int(quantity, 1))
                for item_name, quantity in (encounter.get("guaranteed_drops", {}) or {}).items()
                if isinstance(item_name, str)
            ),
            "tables": (),
        },
        "source": source,
        "quest_id": quest_id,
        "quest_encounter_id": encounter_id,
        "attack_style": attack_style or "melee",
        "attack_speed": _positive_int(configs.get("attack_speed", 4), 4),
    }
    max_hit = _positive_int(configs.get("max_hit", 0), 0)
    if max_hit > 0:
        enemy["max_hit"] = max_hit
    if configs.get("poison_immune"):
        enemy["poison_immune"] = True
    return enemy


def _quest_combat_default_rng():
    return lambda: 0.5


def quest_combat_encounter_ready_pure(player_data, encounter):
    if not quest_combat_encounter_has_stats_pure(encounter):
        return False, "combat_missing_stats"
    minimum_player_combat = _positive_int(
        _quest_combat_configs(encounter).get("minimum_player_combat", 0), 0
    )
    player_level = player_combat_level_pure(player_data)
    if minimum_player_combat > 0 and player_level < minimum_player_combat:
        return False, "combat_underpowered"
    return True, "combat_ready"


def _quest_stage_requirement_variant(requirement):
    if not isinstance(requirement, Mapping):
        return ""
    return str(requirement.get("variant") or "").strip()


def _quest_current_stage_rows(quest, current_stage):
    rows = []
    for requirement in quest.get("stage_requirements", ()) or ():
        if not isinstance(requirement, Mapping):
            continue
        if _positive_int(requirement.get("stage", 0), 0) == current_stage:
            rows.append(requirement)
    return tuple(rows)


def _dedupe_quest_blockers(blockers):
    seen = set()
    rows = []
    for blocker in blockers:
        key = (
            blocker.get("stage"),
            blocker.get("kind"),
            blocker.get("reason"),
            blocker.get("source"),
            blocker.get("route_id"),
            blocker.get("action_id"),
            blocker.get("encounter_id"),
            blocker.get("item_name"),
            blocker.get("tool_name"),
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(blocker)
    return tuple(rows)


def _quest_stage_skill_blockers(player_data, stage, source, requirements):
    blockers = []
    for requirement in requirements or ():
        reason = _skill_requirement_reason(player_data, requirement)
        if not reason:
            continue
        blockers.append(
            _quest_blocker(
                stage,
                "missing_skill",
                reason,
                source,
                skill_id=requirement.get("skill_id"),
                level=_positive_int(requirement.get("level", 1), 1),
            )
        )
    return tuple(blockers)


def _quest_combat_weapon_blockers(player_data, quest_id, stage, source, requirement):
    # Darkan's DelrithBoss zeroes every hit not dealt with a wielded Silverlight,
    # so such a fight cannot start or go on with any other weapon.
    wielded = (player_data.get("equipment", {}) or {}).get("weapon")
    return tuple(
        _quest_blocker(stage, "missing_weapon", f"Wield {weapon} to damage {encounter.get('display_name')}", source)
        for encounter in requirement.get("combat_encounters", ()) or ()
        if (weapon := _quest_combat_configs(encounter).get("required_weapon"))
        and weapon != wielded
        and _quest_combat_remaining_count(player_data, quest_id, encounter.get("encounter_id"), encounter) > 0
    )


def _quest_requirement_blockers(player_data, quest_id, requirement):
    requirement = oronwen_requirement_pure(player_data, quest_id, requirement)
    stage = _positive_int(requirement.get("stage", 0), 0)
    source = str(requirement.get("source", ""))
    inventory = player_data.get("inventory", {}) or {}
    blockers = []
    repeatable_consumed_items = {
        item_name
        for item_name, _amount in _quest_stage_item_pairs(
            requirement, "consumed_inventory"
        )
    } if bool(requirement.get("repeatable_until_consumed")) else set()

    required_items = {}
    for item_name, amount in (
        _quest_stage_item_pairs(requirement, "required_inventory")
        + _quest_stage_item_pairs(requirement, "consumed_inventory")
    ):
        required_items[item_name] = max(required_items.get(item_name, 0), amount)
    for item_name, amount in required_items.items():
        owned = _positive_int(inventory.get(item_name, 0), 0)
        if owned < amount:
            if item_name in repeatable_consumed_items:
                continue
            blockers.append(
                _quest_blocker(
                    stage,
                    "missing_item",
                    f"Needs {item_name} x{amount}",
                    source,
                    item_name=item_name,
                    quantity=amount,
                    owned=owned,
                )
            )

    seen_option_blockers = set()
    for option_key in ("required_inventory_options", "consumed_inventory_options"):
        for options in _quest_stage_item_option_groups(requirement, option_key):
            if option_key == "required_inventory_options":
                option_met = any(_has_quest_tool(player_data, item_name, amount) for item_name, amount in options)
            else:
                option_met = any(
                    _positive_int(inventory.get(item_name, 0), 0) >= amount for item_name, amount in options
                )
            if option_met:
                continue
            option_signature = tuple(options)
            if option_signature in seen_option_blockers:
                continue
            seen_option_blockers.add(option_signature)
            blockers.append(
                _quest_blocker(
                    stage,
                    "missing_item_option",
                    _quest_item_option_reason(options),
                    source,
                    options=tuple({"item_name": item_name, "quantity": amount} for item_name, amount in options),
                )
            )

    blockers.extend(
        _quest_stage_skill_blockers(
            player_data,
            stage,
            source,
            requirement.get("required_skills"),
        )
    )

    for tool_name, amount in _quest_stage_item_pairs(requirement, "required_tools"):
        if not _has_quest_tool(player_data, tool_name, amount):
            quantity = f" x{amount}" if amount > 1 else ""
            blockers.append(
                _quest_blocker(
                    stage,
                    "missing_tool",
                    f"Needs {tool_name}{quantity}",
                    source,
                    tool_name=tool_name,
                    quantity=amount,
                )
            )

    for action_id in _quest_stage_strings(requirement, "required_actions"):
        if not quest_action_proof_completed_pure(player_data, action_id):
            blockers.append(
                _quest_blocker(
                    stage,
                    "required_action",
                    f"Action required: {action_id}",
                    source,
                    action_id=action_id,
                )
            )

    for route_id in _quest_stage_strings(requirement, "required_routes"):
        if not _quest_route_completed(player_data, quest_id, route_id):
            blockers.append(
                _quest_blocker(
                    stage,
                    "unmet_route",
                    f"Route required: {route_id}",
                    source,
                    route_id=route_id,
                )
            )

    blockers.extend(_quest_combat_weapon_blockers(player_data, quest_id, stage, source, requirement))
    for encounter in requirement.get("combat_encounters", ()) or ():
        if not isinstance(encounter, Mapping):
            continue
        encounter_id = encounter.get("encounter_id")
        if not isinstance(encounter_id, str):
            continue
        display_name, level, quantity, level_text, _, encounter_source = _quest_combat_display(encounter, source)
        completed_quantity = _quest_combat_completed_count(player_data, quest_id, encounter_id, encounter)
        remaining_quantity = _quest_combat_remaining_count(player_data, quest_id, encounter_id, encounter)
        if remaining_quantity <= 0:
            continue
        remaining_quantity_text = f" x{remaining_quantity}" if remaining_quantity > 1 else ""
        label = f"{display_name}{level_text}{remaining_quantity_text}"
        fight = dict(
            encounter_id=encounter_id,
            display_name=display_name,
            level=level,
            quantity=remaining_quantity,
            total_quantity=quantity,
            completed_quantity=completed_quantity,
            remaining_quantity=remaining_quantity,
        )
        if not quest_combat_encounter_has_stats_pure(encounter):
            reason = f"This fight is not modelled yet (combat stats missing): {label}"
            blockers.append(_quest_blocker(stage, "combat_missing_stats", reason, encounter_source, **fight))
            continue
        player_level = player_combat_level_pure(player_data)
        minimum_player_combat = _positive_int(
            _quest_combat_configs(encounter).get("minimum_player_combat", 0), 0
        )
        fight["minimum_player_combat"] = minimum_player_combat
        if minimum_player_combat > 0 and player_level < minimum_player_combat:
            reason = f"Requires combat level {minimum_player_combat} for battle: {label}"
            blockers.append(
                _quest_blocker(
                    stage, "combat_underpowered", reason, encounter_source, player_combat_level=player_level, **fight
                )
            )
            continue
        reason = f"Battle required: {label}"
        blockers.append(_quest_blocker(stage, "combat_encounter", reason, encounter_source, **fight))
    return tuple(blockers)


def _quest_current_stage_selected_requirements(player_data, quest_id, quest_data):
    quest = quest_data.get(quest_id)
    if not isinstance(quest, Mapping):
        return tuple(), tuple()
    current_stage = quest_current_stage_pure(player_data, quest_id, quest_data)
    mandatory_rows = []
    variant_rows_by_id = {}
    for requirement in _quest_current_stage_rows(quest, current_stage):
        variant = _quest_stage_requirement_variant(requirement)
        if variant:
            variant_rows_by_id.setdefault(variant, []).append(requirement)
        else:
            mandatory_rows.append(requirement)

    mandatory_blockers = [
        blocker
        for requirement in mandatory_rows
        for blocker in _quest_requirement_blockers(player_data, quest_id, requirement)
    ]
    if not variant_rows_by_id:
        return tuple(mandatory_rows), _dedupe_quest_blockers(mandatory_blockers)

    variant_results = []
    for variant, variant_rows in variant_rows_by_id.items():
        blockers = [
            blocker
            for requirement in variant_rows
            for blocker in _quest_requirement_blockers(player_data, quest_id, requirement)
        ]
        route_blockers = tuple(blocker for blocker in blockers if blocker.get("kind") == "unmet_route")
        variant_results.append((len(route_blockers), len(blockers), variant, tuple(variant_rows), tuple(blockers), route_blockers))

    route_matched = [result for result in variant_results if result[0] == 0]
    if route_matched:
        _, _, _, selected_rows, selected_blockers, _ = min(route_matched, key=lambda row: (row[1], row[2]))
        return (
            tuple(mandatory_rows) + selected_rows,
            _dedupe_quest_blockers((*mandatory_blockers, *selected_blockers)),
        )

    route_blockers = tuple(blocker for result in variant_results for blocker in result[5])
    if route_blockers:
        return tuple(mandatory_rows), _dedupe_quest_blockers((*mandatory_blockers, *route_blockers))

    _, _, _, _, selected_blockers, _ = min(variant_results, key=lambda row: (row[1], row[2]))
    return tuple(mandatory_rows), _dedupe_quest_blockers((*mandatory_blockers, *selected_blockers))


def quest_current_stage_blockers_pure(player_data, quest_id, quest_data):
    quest = quest_data.get(quest_id)
    if not quest:
        return (_quest_blocker(0, "unknown", "Unknown quest"),)
    state = quest_state_pure(player_data, quest_id)
    if not state["started"] or state["completed"]:
        return tuple()
    choice_blockers = _quest_current_stage_choice_blockers(player_data, quest_id, quest_data)
    if choice_blockers:
        return choice_blockers
    _, blockers = _quest_current_stage_selected_requirements(player_data, quest_id, quest_data)
    return blockers


def quest_current_stage_blocker_reasons_pure(player_data, quest_id, quest_data):
    return tuple(str(blocker.get("reason")) for blocker in quest_current_stage_blockers_pure(player_data, quest_id, quest_data))


_QUEST_NONCOMBAT_STAGE_BLOCKER_KINDS = {
    "missing_item",
    "missing_item_option",
    "missing_skill",
    "missing_tool",
    "required_action",
    "unmet_route",
    "quest_choice",
}


_QUEST_COMBAT_PREREQUISITE_BLOCKER_KINDS = {
    "missing_item",
    "missing_item_option",
    "missing_skill",
    "missing_tool",
    "missing_weapon",
    "unmet_route",
    "quest_choice",
}


def quest_current_stage_resolvable_combat_blockers_pure(player_data, quest_id, quest_data):
    blockers = quest_current_stage_blockers_pure(player_data, quest_id, quest_data)
    if any(blocker.get("kind") in _QUEST_COMBAT_PREREQUISITE_BLOCKER_KINDS for blocker in blockers):
        return tuple()
    return tuple(
        blocker
        for blocker in blockers
        if blocker.get("kind") == "combat_encounter"
        and "reason" not in _quest_current_stage_combat_admission_pure(
            player_data, quest_id, quest_data, blocker["encounter_id"],
        )
    )


def quest_availability_state_pure(player_data, quest_id, quest_data):
    """Classify quest list state while preserving start locks vs stage blockers."""
    if not quest_data.get(quest_id):
        return "unknown"
    state = quest_state_pure(player_data, quest_id)
    if state["completed"]:
        return "completed"
    if state["started"]:
        if quest_current_stage_blockers_pure(player_data, quest_id, quest_data):
            return "blocked_at_stage"
        return "in_progress"
    if quest_locked_reasons_pure(player_data, quest_id, quest_data):
        return "locked"
    return "can_start"


QUEST_SECTION_QUESTS = "Quests"
QUEST_SECTION_MINIQUESTS = "Miniquests"


def quest_catalog_sections_pure(rows):
    """Split already-sorted ``(quest_id, quest)`` rows into catalog sections.

    Miniquests share the ledger but read as their own list, so they always come
    last. A lone section carries an empty title: a heading over the only group
    on screen is noise, and the tab shows nothing where the title is empty.
    """
    sections = []
    for title, wanted in ((QUEST_SECTION_QUESTS, False), (QUEST_SECTION_MINIQUESTS, True)):
        matched = tuple(row for row in rows if bool(row[1].get("miniquest", False)) == wanted)
        if matched:
            sections.append({"title": title, "rows": matched})
    if len(sections) == 1:
        sections[0]["title"] = ""
    return tuple(sections)


def normalize_xp_rewards_pure(action_spec, default_skill_id="", default_amount=None):
    raw_rewards = action_spec.get("xp_rewards", ()) if isinstance(action_spec, Mapping) else ()
    normalized = []
    if isinstance(raw_rewards, Mapping):
        raw_iter = (raw_rewards,)
    elif isinstance(raw_rewards, Iterable) and not isinstance(raw_rewards, str):
        raw_iter = raw_rewards
    else:
        raw_iter = ()

    for reward in raw_iter:
        if isinstance(reward, Mapping):
            skill_id = reward.get("skill_id")
            amount = reward.get("amount", 0)
        elif isinstance(reward, (tuple, list)) and len(reward) >= 2:
            skill_id, amount = reward[0], reward[1]
        else:
            continue
        if not isinstance(skill_id, str) or not skill_id:
            continue
        try:
            amount_float = float(amount)
        except (TypeError, ValueError):
            continue
        if amount_float <= 0:
            continue
        normalized.append((skill_id, amount_float))

    if not normalized and default_skill_id:
        try:
            amount_float = float(default_amount if default_amount is not None else 0)
        except (TypeError, ValueError):
            amount_float = 0.0
        if amount_float > 0:
            normalized.append((default_skill_id, amount_float))

    ordered_skill_ids = []
    totals = {}
    for skill_id, amount in normalized:
        if skill_id not in totals:
            ordered_skill_ids.append(skill_id)
            totals[skill_id] = 0.0
        totals[skill_id] += amount
    return tuple({"skill_id": skill_id, "amount": totals[skill_id]} for skill_id in ordered_skill_ids)


def primary_xp_reward_amount_pure(xp_rewards, owner_skill_id):
    normalized = normalize_xp_rewards_pure({"xp_rewards": xp_rewards})
    if not normalized:
        return 0.0
    for reward in normalized:
        if reward.get("skill_id") == owner_skill_id:
            return float(reward.get("amount", 0.0) or 0.0)
    return float(normalized[0].get("amount", 0.0) or 0.0)


def can_start_quest_pure(player_data, quest_id, quest_data):
    quest = quest_data.get(quest_id)
    if not quest:
        return False
    state = quest_state_pure(player_data, quest_id)
    if state["completed"]:
        return False
    if state["started"]:
        return True
    return not quest_locked_reasons_pure(player_data, quest_id, quest_data)


def can_progress_quest_pure(player_data, quest_id, quest_data):
    quest = quest_data.get(quest_id)
    if not quest:
        return False
    state = quest_state_pure(player_data, quest_id)
    if state["completed"]:
        return False
    if not state["started"]:
        return can_start_quest_pure(player_data, quest_id, quest_data)
    return not quest_current_stage_blockers_pure(player_data, quest_id, quest_data)


def can_attempt_quest_review_pure(player_data, quest_id, quest_data):
    if can_progress_quest_pure(player_data, quest_id, quest_data):
        return True
    blockers = quest_current_stage_blockers_pure(player_data, quest_id, quest_data)
    return oronwen_review_ready_pure(player_data, quest_id, blockers) or bool(quest_current_stage_resolvable_combat_blockers_pure(player_data, quest_id, quest_data))


def start_quest_pure(player_data, quest_id, quest_data, *, assign_greeting=True):
    if not can_start_quest_pure(player_data, quest_id, quest_data):
        return player_data, False
    data = _copy_player_data_with_nested(player_data)
    quest = quest_data[quest_id]
    state = quest_state_pure(data, quest_id)
    if not state["started"]:
        inventory = data["inventory"]
        for item_name, amount in (quest.get("required_items", {}) or {}).items():
            inventory[item_name] = inventory.get(item_name, 0) - amount
        for item_name, amount in (quest.get("start_inventory", {}) or {}).items():
            inventory[item_name] = inventory.get(item_name, 0) + _positive_int(amount, 1)
        state["started"] = True
        state["progress"] = 0
        state["completed"] = False
    data.setdefault("quests", {})[quest_id] = state
    if quest_id == "cold_war" and assign_greeting:
        data["cold_war_greeting"] = ensure_cold_war_greeting_pure(data)
    data["current_quest"] = quest_id
    return data, True


def _produce_repeatable_quest_stage_items(data, quest_id, quest):
    inventory = data["inventory"]
    requirements, blockers = _quest_current_stage_selected_requirements(
        data, quest_id, {quest_id: quest}
    )
    if blockers:
        return False
    produced = False
    for requirement in requirements:
        if not bool(requirement.get("repeatable_until_consumed")):
            continue
        consumed_items = _quest_stage_item_pairs(requirement, "consumed_inventory")
        if not consumed_items or all(
            _positive_int(inventory.get(item_name, 0), 0) >= amount
            for item_name, amount in consumed_items
        ):
            continue
        for item_name, amount in _quest_stage_item_pairs(
            requirement, "produced_inventory"
        ):
            inventory[item_name] = (
                _positive_int(inventory.get(item_name, 0), 0) + amount
            )
            produced = True
    return produced


def _consume_quest_current_stage_items(data, quest_id, quest):
    inventory = data["inventory"]
    requirements, blockers = _quest_current_stage_selected_requirements(data, quest_id, {quest_id: quest})
    if blockers:
        return
    for requirement in requirements:
        record_quest_stage_action_proofs_pure(data, quest_id, _quest_stage_strings(requirement, "auto_actions"))
        for item_name, amount in _quest_stage_item_pairs(requirement, "consumed_inventory"):
            inventory[item_name] = max(0, _positive_int(inventory.get(item_name, 0), 0) - amount)
        for options in _quest_stage_item_option_groups(requirement, "consumed_inventory_options"):
            for item_name, amount in options:
                if _positive_int(inventory.get(item_name, 0), 0) >= amount:
                    inventory[item_name] = max(0, _positive_int(inventory.get(item_name, 0), 0) - amount)
                    break
        if bool(requirement.get("repeatable_until_consumed")):
            continue
        for item_name, amount in _quest_stage_item_pairs(requirement, "produced_inventory"):
            inventory[item_name] = _positive_int(inventory.get(item_name, 0), 0) + amount


def _quest_current_stage_encounter_by_id(player_data, quest_id, quest_data, encounter_id):
    quest = quest_data.get(quest_id)
    if not isinstance(quest, Mapping):
        return None
    requirements, _ = _quest_current_stage_selected_requirements(player_data, quest_id, quest_data)
    for requirement in requirements:
        for encounter in requirement.get("combat_encounters", ()) or ():
            if isinstance(encounter, Mapping) and encounter.get("encounter_id") == encounter_id:
                return encounter
    return None


def _quest_current_stage_combat_admission_pure(player_data, quest_id, quest_data, encounter_id):
    encounter = _quest_current_stage_encounter_by_id(player_data, quest_id, quest_data, encounter_id)
    if encounter is None:
        return {"reason": "encounter_not_current_stage"}
    if not quest_combat_prerequisites_completed_pure(player_data, quest_id, quest_data, encounter):
        return {"reason": "combat_prerequisites_unmet"}
    ready, reason = quest_combat_encounter_ready_pure(player_data, encounter)
    if not ready:
        return {"reason": reason}
    quantity = _quest_combat_total_quantity(encounter)
    completed_quantity = _quest_combat_completed_count(player_data, quest_id, encounter_id, encounter)
    if completed_quantity >= quantity:
        return {"reason": "combat_already_resolved"}
    return {
        "encounter": encounter,
        "quantity": quantity,
        "completed_quantity": completed_quantity,
    }


def _quest_combat_resumed_encounter(player_data, target_id, saved_lifepoints):
    """A quest fight resumes the encounter its last review carried, so in live
    pacing the attack clocks and spell effects run on as in an ordinary fight."""
    if saved_lifepoints <= 0:
        return {}
    carried = player_data.get("quest_combat_encounter")
    if not isinstance(carried, Mapping) or carried.get("target_id") != target_id:
        carried = {"target_id": target_id}
    return {**carried, "enemy_lifepoints": saved_lifepoints}


def apply_quest_combat_encounter_pure(
    player_data,
    quest_id,
    quest_data,
    encounter_id=None,
    ticks=None,
    rng=None,
    equipment_data=None,
    *,
    stop_after_first_kill=False,
    live_cadence=False,
):
    state = quest_state_pure(player_data, quest_id)
    if not state["started"] or state["completed"]:
        return player_data, False, {"reason": "quest_not_in_progress"}
    stage_blockers = quest_current_stage_blockers_pure(player_data, quest_id, quest_data)
    if any(blocker.get("kind") in _QUEST_COMBAT_PREREQUISITE_BLOCKER_KINDS for blocker in stage_blockers):
        return player_data, False, {"reason": "stage_requirements_unmet"}
    blockers = quest_current_stage_resolvable_combat_blockers_pure(player_data, quest_id, quest_data)
    if encounter_id is None and blockers:
        encounter_id = blockers[0].get("encounter_id")
    if not isinstance(encounter_id, str):
        return player_data, False, {"reason": "no_resolvable_combat"}
    admission = _quest_current_stage_combat_admission_pure(player_data, quest_id, quest_data, encounter_id)
    if "reason" in admission:
        return player_data, False, admission
    encounter = admission["encounter"]
    quantity = admission["quantity"]
    completed_quantity = admission["completed_quantity"]

    quest_target_id = _quest_combat_target_id(quest_id, encounter_id)
    quest_enemy_data = {
        quest_target_id: _quest_combat_enemy_spec(
            quest_id, encounter_id, encounter, player_data
        )
    }
    original_combat_target = player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    original_combat_encounter = dict(player_data.get("combat_encounter", {}) or {})
    quest_active_encounters = sanitize_quest_combat_active_encounters_pure(
        player_data.get("quest_combat_active_encounters")
    )
    saved_lifepoints = _non_negative_int(
        (quest_active_encounters.get(quest_id, {}) or {}).get(encounter_id, 0),
        0,
    )

    combat_player_data = _copy_player_data_with_nested(player_data)
    combat_player_data["current_combat_target"] = quest_target_id
    # Quest battles must resolve to a kill or death, because auto-flee would
    # soft-lock quest progress. Keep the override local to this battle.
    combat_player_data["combat_auto_flee"] = False
    combat_player_data["combat_encounter"] = _quest_combat_resumed_encounter(
        player_data, quest_target_id, saved_lifepoints
    )
    combat_rng = rng if rng is not None else _quest_combat_default_rng()
    combat_ticks = ticks if ticks is not None else QUEST_COMBAT_DEFAULT_BURST_TICKS
    data, combat_ok, combat_result = apply_combat_burst_pure(
        combat_player_data,
        quest_enemy_data,
        equipment_data or {},
        ticks=combat_ticks,
        rng=combat_rng,
        stop_after_first_kill=stop_after_first_kill,
        live_cadence=live_cadence,
    )
    if not combat_ok:
        return player_data, False, combat_result

    quest_encounter = data.get("combat_encounter", {})
    data["current_combat_target"] = original_combat_target
    data["combat_encounter"] = {} if combat_result.get("died") else original_combat_encounter
    data["combat_auto_flee"] = player_data.get("combat_auto_flee", True)
    if combat_result.get("killed"):
        kill_counts = dict(data.get("combat_kill_counts", {}) or {})
        kill_counts.pop(quest_target_id, None)
        data["combat_kill_counts"] = kill_counts
    quest_active_encounters = sanitize_quest_combat_active_encounters_pure(
        data.get("quest_combat_active_encounters")
    )
    quest_active = dict(quest_active_encounters.get(quest_id, {}) or {})

    display_name, level, quantity, _, _, source = _quest_combat_display(encounter)
    quest_result = dict(combat_result)
    quest_result.update(
        {
            "reason": "quest_combat_bank_run"
            if combat_result.get("reason") == "combat_bank_run"
            else "quest_combat_burst",
            "encounter_id": encounter_id,
            "quest_id": quest_id,
            "display_name": display_name,
            "level": level,
            "quantity": 1,
            "quantity_text": "",
            "total_quantity": quantity,
            "completed_quantity": completed_quantity,
            "remaining_quantity": max(0, quantity - completed_quantity),
            "player_combat_level": player_combat_level_pure(player_data),
            "source": source,
        }
    )

    if combat_result.get("reason") == "combat_bank_run":
        if quest_active:
            quest_active_encounters[quest_id] = quest_active
        else:
            quest_active_encounters.pop(quest_id, None)
        data["quest_combat_active_encounters"] = quest_active_encounters
        data["combat_last_result"] = quest_result
        return data, True, quest_result

    data["quest_combat_encounter"] = {}
    if combat_result.get("killed"):
        quest_active.pop(encounter_id, None)
    elif combat_result.get("died"):
        quest_active.pop(encounter_id, None)
    else:
        enemy_lifepoints = _non_negative_int(combat_result.get("enemy_lifepoints", 0), 0)
        if enemy_lifepoints > 0:
            quest_active[encounter_id] = enemy_lifepoints
            data["quest_combat_encounter"] = quest_encounter

    if quest_active:
        quest_active_encounters[quest_id] = quest_active
    else:
        quest_active_encounters.pop(quest_id, None)
    data["quest_combat_active_encounters"] = quest_active_encounters

    if not combat_result.get("killed"):
        data["combat_last_result"] = quest_result
        return data, True, quest_result

    quest_result["reason"] = "combat_resolved"

    quest_counts = data.setdefault("quest_combat_encounter_counts", {}).setdefault(quest_id, {})
    if not isinstance(quest_counts, Mapping):
        quest_counts = {}
    completed_quantity = min(quantity, completed_quantity + 1)
    quest_counts[encounter_id] = completed_quantity
    data["quest_combat_encounter_counts"][quest_id] = dict(quest_counts)

    quest_flags = data.setdefault("quest_combat_encounters", {}).setdefault(quest_id, [])
    if isinstance(quest_flags, str):
        quest_flags = [quest_flags]
    elif isinstance(quest_flags, Mapping):
        quest_flags = [flag for flag, enabled in quest_flags.items() if isinstance(flag, str) and bool(enabled)]
    elif isinstance(quest_flags, Iterable):
        quest_flags = [flag for flag in quest_flags if isinstance(flag, str)]
    else:
        quest_flags = []
    remaining_quantity = max(0, quantity - completed_quantity)
    if remaining_quantity <= 0 and encounter_id not in quest_flags:
        quest_flags.append(encounter_id)
    if quest_flags:
        data["quest_combat_encounters"][quest_id] = sorted(set(quest_flags))
    else:
        data["quest_combat_encounters"].pop(quest_id, None)
    quest_result.update(
        {
            "completed_quantity": completed_quantity,
            "remaining_quantity": remaining_quantity,
            "quest_combat_completed": remaining_quantity <= 0,
        }
    )
    data["combat_last_result"] = quest_result
    return data, True, quest_result


def apply_quest_progress_pure(
    player_data, quest_id, quest_data, *, include_clue_refusal=False
):
    empty_refusal = ("",) if include_clue_refusal else ()
    data, ok = start_quest_pure(player_data, quest_id, quest_data, assign_greeting=False)
    state = quest_state_pure(data, quest_id)
    if not ok or state["completed"]:
        return (data, False, False, *empty_refusal)
    blockers = quest_current_stage_blockers_pure(data, quest_id, quest_data)
    data, repair_result = apply_oronwen_review_pure(data, quest_id, blockers)
    if repair_result == "handed_in":
        return (data, True, False, *empty_refusal)
    if repair_result == "collected":
        blockers = quest_current_stage_blockers_pure(data, quest_id, quest_data)
    if blockers:
        return (player_data, False, False, *empty_refusal)
    quest = quest_data[quest_id]
    if quest_id == "cold_war":
        data["cold_war_greeting"] = ensure_cold_war_greeting_pure(data)
    current_stage = quest_current_stage_pure(data, quest_id, quest_data)
    if _produce_repeatable_quest_stage_items(data, quest_id, quest):
        state["progress"] = current_stage
        data.setdefault("quests", {})[quest_id] = state
        return (data, True, False, *empty_refusal)
    _consume_quest_current_stage_items(data, quest_id, quest)
    total_stages = _positive_int(quest.get("stages", 1), 1)
    state["progress"] = min(total_stages, current_stage + 1)
    completed_now = state["progress"] >= total_stages
    clue_reward_refusal_reason = ""
    if completed_now:
        state["completed"] = True
        data["quest_points"] = max(0, _positive_int(data.get("quest_points", 0), 0)) + _positive_int(quest.get("point_reward", 0), 0)
        inventory = data["inventory"]
        offered_rewards = quest.get("rewards", {}) or {}
        rewards = filter_clue_scroll_outputs_pure(data, offered_rewards)
        clue_reward_refusal_reason = clue_refusal_reason_pure(
            player_data, offered_rewards, rewards
        )
        for item_name, amount in rewards.items():
            inventory[item_name] = inventory.get(item_name, 0) + _positive_int(amount, 1)
        if quest_id == "family_crest":
            data["family_gauntlet_enchantment"] = "family"
        if quest_id == "nomads_requiem":
            # Nomad's Requiem pays 70 Zeal points, a Soul Wars currency, not an
            # inventory item (RuneScape Wiki Nomad's Requiem oldid=6386610).
            data["soul_wars_zeal"] = min(
                SOUL_WARS_ZEAL_CAP,
                max(0, int(data.get("soul_wars_zeal") or 0)) + 70,
            )
        _apply_quest_xp_rewards(data, quest)
    data.setdefault("quests", {})[quest_id] = state
    if include_clue_refusal:
        return data, True, completed_now, clue_reward_refusal_reason
    return data, True, completed_now


def _apply_quest_xp_rewards(data, quest):
    trainable_exp_keys = _trainable_exp_keys()
    pending = data.get("pending_skill_exp_rewards", {})
    if not isinstance(pending, Mapping):
        pending = {}
    clean_pending = dict(pending)
    for reward in quest.get("xp_rewards", ()) or ():
        if not isinstance(reward, Mapping):
            continue
        skill_id = reward.get("skill_id")
        if not isinstance(skill_id, str):
            continue
        skill = get_skill(skill_id)
        exp_key = skill.exp_key if skill is not None else f"{skill_id}_exp"
        try:
            amount = float(reward.get("amount", 0))
        except (TypeError, ValueError):
            amount = 0.0
        if amount <= 0:
            continue
        if exp_key in trainable_exp_keys and skill is not None and skill.trainable:
            data[exp_key] = data.get(exp_key, 0) + amount
        else:
            clean_pending[exp_key] = float(clean_pending.get(exp_key, 0) or 0) + amount
    data["pending_skill_exp_rewards"] = {
        key: value for key, value in clean_pending.items() if value > 0
    }


def _apply_skill_xp_reward(data, skill_id, amount):
    skill = get_skill(skill_id)
    exp_key = skill.exp_key if skill is not None else f"{skill_id}_exp"
    trainable_exp_keys = _trainable_exp_keys()
    if exp_key in trainable_exp_keys and skill is not None and skill.trainable:
        data[exp_key] = data.get(exp_key, 0) + amount
        return
    pending = data.get("pending_skill_exp_rewards", {})
    if not isinstance(pending, Mapping):
        pending = {}
    clean_pending = dict(pending)
    clean_pending[exp_key] = float(clean_pending.get(exp_key, 0) or 0) + amount
    data["pending_skill_exp_rewards"] = {
        key: value for key, value in clean_pending.items() if value > 0
    }


def quest_journal_rows_pure(player_data, quest_id, quest_data):
    quest = quest_data.get(quest_id)
    if not quest:
        return tuple()
    state = quest_state_pure(player_data, quest_id)
    progress = state["progress"]
    if state["started"] and progress <= 0:
        progress = 1
    if state["completed"]:
        progress = _positive_int(quest.get("stages", progress), progress)
    journal_stages = quest.get("journal_stages", {}) or {}
    rows = []
    for stage in sorted(journal_stages):
        if stage > progress:
            continue
        rows.append(
            {
                "stage": stage,
                "lines": cold_war_journal_lines_pure(player_data, quest_id, stage, journal_stages.get(stage, ())),
                "completed": state["completed"] or stage < progress,
                "current": (not state["completed"] and stage == progress),
            }
        )
    return tuple(rows)
