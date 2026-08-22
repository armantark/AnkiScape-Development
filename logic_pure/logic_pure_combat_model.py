"""logic_pure_combat_model.py - split out of logic_pure.py; see that module's header."""

from math import comb, floor, sqrt

from typing import Iterable, Mapping, Optional

from ..data.equipment_data import EQUIPMENT_BONUS_FIELDS, EquipmentBonuses

from ..logic.equipment_instance_logic import (
    advance_equipped_condition_pure,
    discharge_equipped_on_unsafe_death_pure,
    sanitize_equipment_instance_state_pure,
)
from ..data.equipment_condition_data import EQUIPMENT_CONDITION_DATA

from ..logic.inventory_pure import CARRIED_CAPACITY, apply_carried_layout_pure, carried_slots_used, clamp_carried_view_to_bank

from ..logic.court_cases_logic import filter_court_summons_outputs_pure
from ..logic.treasure_trails_logic import (
    clue_refusal_reason_pure,
    filter_clue_scroll_outputs_pure,
)

try:
    from ..data.item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES
except ImportError:  # values not generated in this checkout
    ITEM_VALUES = {}
    STACKABLE_ITEM_NAMES = frozenset()

from ..logic.warriors_guild_logic import (
    warriors_guild_cyclops_damage_multiplier_pure,
    warriors_guild_cyclops_locked_reasons_pure,
)

from ..data.prayer_data import (
    COMBAT_PRAYERS_BY_ID,
    AUTO_PRAYER_TICKS_PER_ITEM,
    PRAYER_MATERIALS,
    PRAYER_UPTIME_POLICIES,
    SAP_SOURCE,
    LEECH_SOURCE,
    resolve_prayer_selection_pure,
)

from ..data.magic_data import CASUAL_MAGIC_DIAL, DREAM_COST, SPELLBOOK_SWAP_COST, VENGEANCE_COST

from ..data.livid_farm_data import BORROWED_POWER_COMBAT_SPELLS

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

from .logic_pure_urns import (  # noqa: F401  (re-export)
    active_urn_state_pure,
    carried_target_item_count_pure,
    charge_training_urn_for_action_pure,
    charge_training_urn_pure,
    full_urn_teleport_info_pure,
    intercept_bonecrusher_outputs_pure,
    nonempty_urn_count_pure,
    resolve_prayer_kill_effects_pure,
    teleport_full_urn_pure,
)

from .logic_pure_prayer import (  # noqa: F401  (re-export)
    CASTLE_WARS_HALO_DRAIN_PRAYERS,
    _highest_legal_prayer_candidate_pure,
    active_prayer_selection_pure,
    apply_prayer_action_pure,
    apply_prayer_selection_pure,
    clear_prayer_gilded_stint_pure,
    curse_expected_ramp_pure,
    prayer_drain_and_effective_uptime_pure,
    prayer_drain_for_ticks_pure,
    prayer_effect_state_pure,
    prayer_gilded_search_step_pure,
    prayer_selection_locked_reasons_pure,
    prayer_target_locked_reasons_pure,
    prayer_uptime_fraction_pure,
    sanitize_prayer_selection_pure,
)

from .logic_pure_magic import (  # noqa: F401  (re-export)
    MAGIC_CHARGE_DURATION_TICKS,
    TEMPORARY_EFFECT_TICKS_PER_ACTION,
    _HUMIDIFY_OUTPUTS,
    _LEATHER_OUTPUTS,
    _PIE_OUTPUTS,
    _STRINGABLE_AMULETS,
    _apply_farming_spell_pure,
    _apply_remote_farm_pure,
    _farming_spell_locked_reasons_pure,
    _livid_spell_locked_reasons_pure,
    _magic_dynamic_requirements_pure,
    _magic_quest_gate_complete_pure,
    advance_temporary_effects_pure,
    apply_magic_action_pure,
    effective_magic_rune_cost_pure,
    magic_target_locked_reasons_pure,
)

from .logic_pure_equipment import (  # noqa: F401  (re-export)
    _combat_level_key,
    _combat_skill_label,
    _equipment_bonus_value,
    _equipment_bonuses,
    _equipment_skill_requirements,
    _equipment_value,
    _mage_arena_god_for_item,
    _normalized_equipment_slot,
    _toolbelt_ids,
    best_mining_pickaxe_pure,
    best_woodcutting_axe_pure,
    can_equip_item_pure,
    equip_item_pure,
    equipment_bonus_state_pure,
    equipment_stat_totals_pure,
    unequip_item_pure,
)

from .logic_pure_landmarks import (  # noqa: F401  (re-export)
    KNIGHT_WAVES_TOTAL_STEPS,
    KNIGHT_WAVES_XP_REWARD,
    MAGE_ARENA_GOD_CAPES,
    MAGE_ARENA_GOD_DATA,
    MAGE_ARENA_GOD_STAVES,
    MAGE_ARENA_SPELL_TO_GOD,
    MAGE_ARENA_STEP_NAMES,
    MAGE_ARENA_TOTAL_STEPS,
    STRONGHOLD_BOOT_CHOICES,
    STRONGHOLD_REWARD_COINS,
    STRONGHOLD_STEP_NAMES,
    STRONGHOLD_TOTAL_STEPS,
    _owns_or_equips_pure,
    apply_knight_waves_step_pure,
    apply_mage_arena_cape_action_pure,
    apply_mage_arena_step_pure,
    apply_stronghold_step_pure,
    attune_mage_arena_spell_pure,
    default_knight_waves_state_pure,
    default_mage_arena_state_pure,
    default_stronghold_state_pure,
    grant_stronghold_reward_pure,
    knight_waves_locked_reasons_pure,
    mage_arena_locked_reasons_pure,
    sanitize_knight_waves_state_pure,
    sanitize_mage_arena_state_pure,
    sanitize_stronghold_state_pure,
    set_mage_arena_alignment_pure,
)

from .logic_pure_state import (  # noqa: F401  (re-export)
    COMBAT_BANK_RUN_REVIEWS,
    COMBAT_GRAVE_RECOVERY_REVIEWS,
    COMBAT_PVP_DEATH_KEPT_ITEMS,
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

from .logic_pure_urns import (
    resolve_prayer_kill_effects_pure,
)

from .logic_pure_prayer import (
    _highest_legal_prayer_candidate_pure,
    prayer_effect_state_pure,
    sanitize_prayer_selection_pure,
)

from .logic_pure_magic import (
    _magic_quest_gate_complete_pure,
)

from .logic_pure_equipment import (
    _combat_skill_label,
    _equipment_bonus_value,
    _equipment_skill_requirements,
    _equipment_value,
)

from .logic_pure_landmarks import (
    MAGE_ARENA_GOD_DATA,
    MAGE_ARENA_SPELL_TO_GOD,
    sanitize_knight_waves_state_pure,
    sanitize_mage_arena_state_pure,
)

from .logic_pure_state import (
    COMBAT_GRAVE_RECOVERY_REVIEWS,
    _combat_grave_items,
    _combat_stored_loadout,
    _copy_player_data_with_nested,
    _non_negative_float,
    _non_negative_int,
    _positive_int,
    _sanitize_combat_bank_run,
    _sanitize_combat_grave_state,
    _sanitize_combat_supply_loadout,
    _sanitize_death_office_state,
    _signed_int,
    default_combat_supply_loadout_pure,
    quest_completed_pure,
)


_DEFAULT_COMBAT_AUTO_EAT_FOOD = (
    "Shark",
    "Monkfish",
    "Swordfish",
    "Bass",
    "Lobster",
    "Tuna",
    "Salmon",
    "Pike",
    "Trout",
    "Cod",
    "Mackerel",
    "Herring",
    "Cooked meat",
    "Cooked chicken",
    "Sardine",
    "Shrimps",
    "Crayfish",
)


# RS-classic natural regeneration is ~1 hitpoint per game-minute; a lifepoint is
# 1/10th of a hitpoint, and a safe (non-combat) review models one burst window
# (COMBAT_BURST_TICKS * 0.6s ~= 30s ~= half a game-minute), so a rested-out review
# regenerates ~5 LP. This is the slow baseline; leaving combat grants an
# accelerated "rest" that reaches full LP over COMBAT_REST_FULL_HEAL_REVIEWS.
NATURAL_COMBAT_RECOVERY_LIFEPOINTS = 5


COMBAT_REST_FULL_HEAL_REVIEWS = 3


# Overheal (LP above max, from potions/brews) still bleeds off at the old faster
# rate — natural regen only ever climbs toward the cap, never away from it.
SAFE_COMBAT_RECOVERY_LIFEPOINTS = 100


SAFE_COMBAT_RECOVERY_TICKS = COMBAT_BURST_TICKS


COMBAT_SPECIAL_ATTACK_MAX_ENERGY = 100


COMBAT_SPECIAL_ATTACK_REGEN_PER_50_TICKS = 10


COMBAT_OBSERVED_DROP_TARGET_LIMIT = 1024
COMBAT_OBSERVED_DROP_ITEM_LIMIT = 256
COMBAT_OBSERVED_DROP_COUNT_LIMIT = 2_147_483_647


COMBAT_STAT_DRAIN_RECOVERY_TICKS = 100


COMBAT_POISON_TICK_DELAY = 30


COMBAT_POISON_NPC_ATTACK_CHANCE = 0.4


COMBAT_POISON_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/mechanics/poison/Poison.kt"
)


COMBAT_POISON_TIMER_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/mechanics/poison/poison_plugin.plugin.kts"
)


COMBAT_FOOD_LOADOUT_CAPACITY = 28


# Combat packing mode allocates the single 28-slot inventory across three axes:
# food (survival), stat-potion flasks (damage), and the slots left empty for
# loot (fewer bank interruptions). Potions are capped as a small flask count
# (each flask is 4 doses, so a couple last a whole trip and refill every bank
# run — carrying 20 would be absurd). Max-safety leans food; max-output carries
# little food + more damage potions and leaves the most room for loot (confident
# out-gearing); balanced is a mix. All caps are tunable AnkiScape balance knobs.
_COMBAT_DEFAULT_PACK_MODE = "balanced"


_COMBAT_VALID_PACK_MODES = ("balanced", "max_output", "max_safety")


_COMBAT_FOOD_CAP_BY_MODE = {"max_safety": 20, "balanced": 14, "max_output": 8}


_COMBAT_POTION_FLASK_CAP_BY_MODE = {"max_safety": 2, "balanced": 4, "max_output": 6}


# One dose cures poison; two cover a trip and refill at every bank run. Mode does
# not scale this — antipoison is a cure, not a food/damage tradeoff.
_COMBAT_ANTIPOISON_SLOT_CAP = 2


_COMBAT_DRAGONFIRE_POTION_SLOT_CAP = 1


def _combat_coerce_pack_mode(mode):
    return mode if mode in _COMBAT_VALID_PACK_MODES else _COMBAT_DEFAULT_PACK_MODE


def _combat_food_slot_cap(data):
    mode = _combat_coerce_pack_mode(data.get("combat_pack_mode", _COMBAT_DEFAULT_PACK_MODE))
    return min(COMBAT_FOOD_LOADOUT_CAPACITY, _COMBAT_FOOD_CAP_BY_MODE.get(mode, 14))


def _combat_potion_flask_cap(data):
    mode = _combat_coerce_pack_mode(data.get("combat_pack_mode", _COMBAT_DEFAULT_PACK_MODE))
    return _COMBAT_POTION_FLASK_CAP_BY_MODE.get(mode, 4)


COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS = 1000


COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM = 100


# Skills whose *current* level can differ from base via drains/boosts
# (engine setCurrentLevel model). Kebab can also drop a random non-combat
# skill, so the substrate accepts any skill id; this tuple is the combat
# set that feeds accuracy/max-hit.
_COMBAT_AFFECTABLE_SKILLS = ("attack", "strength", "defense", "ranged", "magic", "prayer")


_COMBAT_DRAINABLE_SKILLS = _COMBAT_AFFECTABLE_SKILLS  # back-compat alias


_COMBAT_MELEE_STYLE_IDS = ("accurate", "aggressive", "defensive", "controlled")


_COMBAT_RANGED_STYLE_IDS = ("ranged_accurate", "ranged_rapid", "ranged_longrange")


_COMBAT_MAGIC_EQUIPMENT_TYPES = {"staff", "elemental_staff", "battlestaff"}


# "auto" lets the resolver pick the first slot for the chosen weapon_style;
# stab/slash/crush force a specific melee attack type (D1 parity).
_COMBAT_MELEE_STYLE_TYPES = ("auto", "stab", "slash", "crush")


# AttackStyleData xp_mode -> the _combat_apply_xp style id that trains the same
# skill(s). "shared" trains attack/strength/defence three ways like "controlled",
# which is how the two-handed-sword aggressive/crush/SHARED anomaly is trained.
_COMBAT_XP_MODE_TO_STYLE_ID = {
    "attack": "accurate",
    "strength": "aggressive",
    "defense": "defensive",
    "shared": "controlled",
}


def combat_max_lifepoints_pure(player_data):
    return max(10, _positive_int(player_data.get("constitution_level", 10), 10) * 10)


COMBAT_PRESET_FIELDS = (
    "combat_pack_mode", "combat_auto_eat_threshold_percent", "combat_auto_eat_food",
    "combat_auto_flee", "combat_selected_prayers",
    "combat_prayer_uptime", "combat_auto_prayer_training", "current_combat_spell",
    "combat_prayers_enabled", "combat_vengeance", "combat_dream_thrift",
    "combat_spellbook_swap",
)


def combat_dream_thrift_locked_reasons_pure(player_data):
    """Return the source-backed requirements that prevent automatic Dream use."""
    if (
        _positive_int(player_data.get("magic_level", 1), 1) < 79
        or not quest_completed_pure(player_data, "dream_mentor")
    ):
        return ("79 Magic and Dream Mentor",)
    return ()


def combat_magic_preset_locked_reasons_pure(player_data):
    """Enforce implicit spellbooks and the one explicit Lunar swap exception."""
    spell_id = str(player_data.get("current_combat_spell", DEFAULT_COMBAT_SPELL))
    spell = COMBAT_MAGIC_SPELL_DATA.get(spell_id, {})
    equipment = player_data.get("equipment", {}) or {}
    wielded = str(equipment.get("weapon", "") or "")
    effects = []
    if wielded in COMBAT_MAGIC_STAFF_DATA:
        effects.append((spell_id, str(spell.get("spellbook", "standard"))))
    if bool(player_data.get("combat_vengeance", False)):
        if _positive_int(player_data.get("magic_level", 1), 1) < 94 or not quest_completed_pure(player_data, "lunar_diplomacy"):
            return ("Vengeance requires 94 Magic and Lunar Diplomacy",)
        effects.append(("vengeance", "lunar"))
    if bool(player_data.get("combat_dream_thrift", False)):
        dream_reasons = combat_dream_thrift_locked_reasons_pure(player_data)
        if dream_reasons:
            return (f"Dream requires {dream_reasons[0]}",)
        effects.append(("dream", "lunar"))
    books = {book for _effect, book in effects}
    swap_spell = str(player_data.get("combat_spellbook_swap", "") or "")
    if swap_spell and swap_spell not in {effect for effect, _book in effects}:
        return ("Spellbook Swap must name one selected magic effect",)
    if len(books) > 1:
        if not swap_spell or swap_spell not in {effect for effect, _book in effects}:
            return ("Preset mixes spellbooks",)
        remaining_books = {book for effect, book in effects if effect != swap_spell}
        swapped_books = {book for effect, book in effects if effect == swap_spell}
        if len(remaining_books) != 1 or len(swapped_books) != 1 or remaining_books == swapped_books:
            return ("Spellbook Swap allows exactly one off-book spell",)
        if _positive_int(player_data.get("magic_level", 1), 1) < 96 or not quest_completed_pure(player_data, "lunar_diplomacy"):
            return ("Spellbook Swap requires 96 Magic and Lunar Diplomacy",)
    target_id = str(player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET))
    for label, cost, _xp in _combat_pending_supplemental_magic_costs_pure(player_data):
        if label != "spellbook_swap":
            continue
        for rune, amount in cost.items():
            if _combat_magic_rune_count(player_data, rune, target_id) < amount:
                return (f"Spellbook Swap needs {rune} x{amount}",)
    return ()


def derive_casual_combat_magic_pure(player_data):
    """Data-driven three-position dial layer atop the advanced preset fields."""
    data = _copy_player_data_with_nested(player_data)
    mode = _combat_coerce_pack_mode(data.get("combat_pack_mode", "balanced"))
    rule = CASUAL_MAGIC_DIAL.get(mode, CASUAL_MAGIC_DIAL["balanced"])
    if bool(data.get("combat_prayers_enabled", True)):
        data["combat_prayer_uptime"] = rule["prayer_uptime"]
        prayer_level = _positive_int(data.get("prayer_level", 1), 1)
        book = str(data.get("combat_prayer_book", "standard"))
        target = COMBAT_ENEMY_DATA.get(str(data.get("current_combat_target", "")), {})
        if mode == "max_safety":
            configured_style = COMBAT_ATTACK_STYLE_DATA.get(
                str(data.get("combat_attack_style", DEFAULT_COMBAT_ATTACK_STYLE)),
                COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE],
            )
            protection_class = (
                _combat_enemy_protection_class(
                    target,
                    str(configured_style.get("combat_class", "melee")),
                )
                if target
                else "melee"
            )
            protection_effect = {
                "magic": "protect_magic",
                "ranged": "protect_ranged",
            }.get(protection_class, "protect_melee")
            candidates = [
                prayer for prayer in COMBAT_PRAYERS_BY_ID.values()
                if prayer.book == book and prayer.level <= prayer_level
                and any(effect == protection_effect for effect, _value in prayer.effects)
            ]
            candidate = _highest_legal_prayer_candidate_pure(data, candidates, book)
            selected = [candidate] if candidate else []
        else:
            equipment = data.get("equipment", {}) or {}
            weapon = str(equipment.get("weapon", "") or "")
            if weapon in COMBAT_MAGIC_STAFF_DATA:
                wanted = ("magic_combat", "leech_magic", "sap_mage")
            elif weapon in COMBAT_RANGED_WEAPON_DATA:
                wanted = ("ranged_combat", "leech_ranged", "sap_ranger")
            else:
                wanted = ("melee_combat", "turmoil")
            candidates = [
                prayer for prayer in COMBAT_PRAYERS_BY_ID.values()
                if prayer.book == book and prayer.level <= prayer_level
                and set(prayer.groups).intersection(wanted)
            ]
            candidate = _highest_legal_prayer_candidate_pure(data, candidates, book)
            selected = [candidate] if candidate else []
            if not selected and book == "standard":
                for group in ("attack", "strength", "defence"):
                    group_rows = [
                        prayer for prayer in COMBAT_PRAYERS_BY_ID.values()
                        if prayer.book == book and prayer.level <= prayer_level and group in prayer.groups
                    ]
                    candidate = _highest_legal_prayer_candidate_pure(data, group_rows, book)
                    if candidate:
                        selected.append(candidate)
        data["combat_selected_prayers"] = list(sanitize_prayer_selection_pure(data, selected, book))
    data["combat_vengeance"] = bool(rule["vengeance"] and _positive_int(data.get("magic_level", 1), 1) >= 94 and quest_completed_pure(data, "lunar_diplomacy"))
    data["combat_dream_thrift"] = bool(
        (data.get("combat_dream_thrift") or rule["dream"])
        and not combat_dream_thrift_locked_reasons_pure(data)
    )
    return data


def _combat_preset_snapshot(data):
    snapshot = {}
    for key in COMBAT_PRESET_FIELDS:
        value = data.get(key)
        if isinstance(value, Mapping):
            snapshot[key] = dict(value)
        elif isinstance(value, list):
            snapshot[key] = list(value)
        else:
            snapshot[key] = value
    return snapshot


def save_combat_preset_pure(player_data, name):
    data = _copy_player_data_with_nested(player_data)
    clean_name = str(name).strip()
    if not clean_name:
        return data, False
    presets = dict(data.get("combat_presets", {}) or {})
    presets[clean_name] = _combat_preset_snapshot(data)
    data["combat_presets"] = presets
    data["combat_active_preset"] = clean_name
    return data, True


def apply_combat_target_overrides_pure(player_data, target_id):
    data = _copy_player_data_with_nested(player_data)
    overrides = (data.get("combat_target_overrides", {}) or {}).get(target_id, {}) if target_id else {}
    if isinstance(overrides, Mapping):
        for key, value in overrides.items():
            if key in COMBAT_PRESET_FIELDS:
                data[key] = dict(value) if isinstance(value, Mapping) else list(value) if isinstance(value, list) else value
    data["combat_selected_prayers"] = list(sanitize_prayer_selection_pure(data, data.get("combat_selected_prayers", ())))
    return data


def apply_combat_preset_pure(player_data, name, target_id=None):
    data = _copy_player_data_with_nested(player_data)
    presets = data.get("combat_presets", {}) or {}
    preset = presets.get(name) if isinstance(presets, Mapping) else None
    if not isinstance(preset, Mapping):
        return data, False
    for key in COMBAT_PRESET_FIELDS:
        if key in preset:
            value = preset[key]
            data[key] = dict(value) if isinstance(value, Mapping) else list(value) if isinstance(value, list) else value
    data = apply_combat_target_overrides_pure(data, target_id)
    data["combat_active_preset"] = str(name)
    return data, True


def default_combat_state_pure():
    state = {
        "current_combat_target": DEFAULT_COMBAT_TARGET,
        "combat_action": "attack",
        "combat_attack_style": DEFAULT_COMBAT_ATTACK_STYLE,
        "combat_attack_style_type": "auto",
        "current_combat_spell": DEFAULT_COMBAT_SPELL,
        "combat_borrowed_power_spell": "",
        "combat_lifepoints": 100,
        "combat_auto_eat_threshold_percent": 40,
        "combat_auto_flee": True,
        "combat_rest_reviews": 0,
        "combat_auto_eat_food": list(_DEFAULT_COMBAT_AUTO_EAT_FOOD),
        "combat_supply_loadout": default_combat_supply_loadout_pure(),
        "combat_pack_mode": _COMBAT_DEFAULT_PACK_MODE,
        "combat_special_attack_energy": COMBAT_SPECIAL_ATTACK_MAX_ENERGY,
        "combat_current_levels": {},
        "combat_status_effects": {},
        "combat_antifire_ticks_remaining": 0,
        "combat_super_antifire_ticks_remaining": 0,
        "combat_recovery_progress": {},
        "combat_bank_run": {},
        "combat_encounter": {},
        "combat_kill_counts": {},
        "combat_observed_drops": {},
        "combat_examined_monsters": [],
        "combat_last_result": {},
        "combat_grave": {},
        "death_office": {},
        "combat_prayer_book": "standard",
        "combat_selected_prayers": [],
        "combat_prayer_uptime": "off",
        "combat_prayer_points": 10,
        "combat_prayer_drain_counter": 0.0,
        "combat_auto_prayer_training": False,
        "combat_prayers_enabled": True,
        "combat_vengeance": False,
        "combat_dream_thrift": False,
        "combat_spellbook_swap": "",
        "combat_active_preset": "Default",
        "combat_target_presets": {},
        "combat_target_overrides": {},
        "knight_waves": {"step": 0, "completed": False},
    }
    state["combat_presets"] = {"Default": _combat_preset_snapshot(state)}
    return state


def _sanitize_combat_current_levels(raw_levels):
    """Absolute current skill levels that differ from base (engine
    setCurrentLevel model). Absence of a skill means "at base". Values are
    signed to represent both drains (current < base) and boosts
    (current > base); any skill id is accepted since kebab can drop a random
    non-combat skill."""
    if not isinstance(raw_levels, Mapping):
        return {}
    cleaned = {}
    for skill_id, level in raw_levels.items():
        if not isinstance(skill_id, str):
            continue
        cleaned[skill_id] = max(1, _signed_int(level, 1))
    return cleaned


def _sanitize_combat_status_effects(raw_effects):
    if not isinstance(raw_effects, Mapping):
        return {}
    effects = {}
    raw_poison = raw_effects.get("poison")
    if isinstance(raw_poison, Mapping):
        ticks_left = _non_negative_int(raw_poison.get("ticks_left", 0), 0)
        tick_progress = _non_negative_int(raw_poison.get("tick_progress", 0), 0)
        source = raw_poison.get("source", COMBAT_POISON_SOURCE_PATH)
        if ticks_left > 0:
            effects["poison"] = {
                "ticks_left": ticks_left,
                "tick_progress": min(tick_progress, COMBAT_POISON_TICK_DELAY - 1),
                "source": source if isinstance(source, str) and source else COMBAT_POISON_SOURCE_PATH,
            }
    raw_immunity = raw_effects.get("poison_immunity")
    if isinstance(raw_immunity, Mapping):
        ticks_left = _non_negative_int(raw_immunity.get("ticks_left", 0), 0)
        source = raw_immunity.get("source", POTION_TYPE_SOURCE_PATH)
        if ticks_left > 0:
            effects["poison_immunity"] = {
                "ticks_left": ticks_left,
                "source": source if isinstance(source, str) and source else POTION_TYPE_SOURCE_PATH,
            }
    return effects


def _sanitize_combat_recovery_progress(raw_progress):
    if not isinstance(raw_progress, Mapping):
        return {}
    stat_drain_ticks = _non_negative_int(raw_progress.get("stat_drain_ticks", 0), 0)
    return {"stat_drain_ticks": stat_drain_ticks} if stat_drain_ticks > 0 else {}


def _combat_reclaim_items_to_player(data, items, loadout):
    """Return reclaimed gear to the player: re-equip the worn loadout into any
    still-empty slot, then drop everything else back into the inventory. A slot
    the player has re-filled since dying keeps its newer item, so the graved piece
    falls to the inventory instead of clobbering it."""
    remaining = [str(item_name) for item_name in items if isinstance(item_name, str) and item_name]
    if isinstance(loadout, Mapping) and loadout:
        equipment = dict(data.get("equipment", {}) or {})
        for slot, item_name in loadout.items():
            if not isinstance(slot, str) or not isinstance(item_name, str) or not item_name:
                continue
            if equipment.get(slot):
                continue
            if item_name in remaining:
                remaining.remove(item_name)
                equipment[slot] = item_name
        data["equipment"] = equipment
    inventory = dict(data.get("inventory", {}) or {})
    for item_name in remaining:
        inventory[item_name] = inventory.get(item_name, 0) + 1
    data["inventory"] = inventory


def _combat_death_office_items(raw_office):
    office = _sanitize_death_office_state(raw_office)
    return list(office.get("items", ()) or ())


def _set_combat_death_office_items(data, items, source="combat_death_office", loadout=None):
    clean_items = [str(item_name) for item_name in items if isinstance(item_name, str) and item_name]
    if clean_items:
        office = {
            "items": clean_items,
            "source": source,
            "reclaim_cost": len(clean_items) * COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM,
        }
        if isinstance(loadout, Mapping) and loadout:
            office["loadout"] = dict(loadout)
        data["death_office"] = office
    else:
        data["death_office"] = {}


def _carried_inventory_grave_counts(data, target_id=None):
    """What is actually in hand at death ({item: count}) — the carried view of the
    active target, i.e. the items from this trip. Combat defaults to its current
    enemy; other dangerous skills pass their own target explicitly.

    NOT the union of every target's view. `carried_inventory` keeps a saved pack per
    target, so a player who has trained Firemaking, Cooking, and Smithing has a
    dormant ~28-item pack sitting under each of those target ids. Draining all of
    them on a combat death both dropped materials from skills the player was not
    doing and staged more than 28 slots of items — more than one inventory can hold.
    A dormant pack is a loadout resting in the bank, not something you are carrying.
    """
    carried = data.get("carried_inventory")
    if not isinstance(carried, Mapping):
        return {}
    if target_id is None:
        target_id = data.get("current_combat_target")
    view = carried.get(target_id) if isinstance(target_id, str) else None
    if not isinstance(view, Mapping):
        return {}
    # Clamp to what the bank still holds. The view can outlive its items (discard,
    # shop sale, eating looted food), and graving more than existed would mint the
    # difference when the grave is reclaimed.
    return clamp_carried_view_to_bank(view, data.get("inventory"))


def _combat_apply_follower_death(data):
    from ..logic.summoning_logic import apply_follower_player_death_pure

    follower_updated, _follower_death = apply_follower_player_death_pure(
        data,
        protected_carried_pet_id=data.get("combat_protected_pet_instance_id"),
    )
    data.clear()
    data.update(follower_updated)


def _combat_apply_pvm_death(
    data,
    max_player_lifepoints,
    grave_source="combat_death",
    carried_target_id=None,
    no_grave=False,
):
    _combat_apply_follower_death(data)
    original_equipment = dict(data.get("equipment", {}) or {})
    carried_counts = _carried_inventory_grave_counts(data, carried_target_id)
    protected_slots: set[str] = set()
    protected_carried: dict[str, int] = {}
    protect_item = prayer_effect_state_pure(data).get("protect_item")
    if no_grave:
        # The gravestone-free death is the player-versus-player one, where
        # `sendPVPItemsOnDeath` hands the rest to the killer. It keeps three
        # items unskulled, and one more while Protect Item is active. Which three
        # is the player's choice in the period; AnkiScape has no inventory
        # arrangement to express it, so it keeps the most valuable ones.
        keep = COMBAT_PVP_DEATH_KEPT_ITEMS + (1 if protect_item else 0)
        candidates = [
            (
                _non_negative_int(ITEM_VALUES.get(item_name, 0), 0),
                str(item_name),
                "equipment",
                str(slot),
            )
            for slot, item_name in original_equipment.items()
            if isinstance(item_name, str)
        ]
        # Carried units are counted one at a time so the kept total is a count of
        # items rather than of stacks.
        candidates.extend(
            (
                _non_negative_int(ITEM_VALUES.get(item_name, 0), 0),
                str(item_name),
                "carried",
                str(item_name),
            )
            for item_name, count in carried_counts.items()
            for _unit in range(max(0, count))
        )
        for _value, _item_name, location, key in sorted(candidates, reverse=True)[:keep]:
            if location == "equipment":
                protected_slots.add(key)
            else:
                protected_carried[key] = protected_carried.get(key, 0) + 1
    elif protect_item and original_equipment:
        protected_slots = {
            max(
                original_equipment,
                key=lambda slot: (_non_negative_int(ITEM_VALUES.get(original_equipment[slot], 0), 0), str(original_equipment[slot]), str(slot)),
            )
        }
    discharged, _condition_events = discharge_equipped_on_unsafe_death_pure(
        data, EQUIPMENT_CONDITION_DATA
    )
    data.clear()
    data.update(discharged)
    discharged_equipment = dict(data.get("equipment", {}) or {})
    protected_equipment = {
        slot: item_name
        for slot, item_name in discharged_equipment.items()
        if slot in protected_slots
    }
    equipment = {
        slot: item_name
        for slot, item_name in discharged_equipment.items()
        if slot not in protected_slots
    }
    grave_items = [item_name for item_name in equipment.values() if isinstance(item_name, str)]
    # Carried items are a view over the flat store: remove them from the bank and
    # drop them into the grave, expanded one grave entry per unit. Only the view of
    # the target being fought is at risk — other targets' saved packs are loadouts
    # resting in the bank, not carried, so they must survive the death.
    if carried_counts:
        inventory = dict(data.get("inventory", {}) or {})
        for item_name, count in carried_counts.items():
            lost = count - protected_carried.get(item_name, 0)
            if lost <= 0:
                continue
            inventory[item_name] = max(0, _non_negative_int(inventory.get(item_name, 0), 0) - lost)
            if not no_grave:
                grave_items.extend([item_name] * lost)
        data["inventory"] = inventory
    active_target = (
        carried_target_id
        if isinstance(carried_target_id, str)
        else data.get("current_combat_target")
    )
    if isinstance(active_target, str):
        for map_key in ("carried_inventory", "carried_churn"):
            container = data.get(map_key)
            if isinstance(container, Mapping) and active_target in container:
                container = dict(container)
                container.pop(active_target, None)
                data[map_key] = container
    if not no_grave:
        existing_grave = data.get("combat_grave", {}) or {}
        existing_grave_items = _combat_grave_items(existing_grave)
        if existing_grave_items:
            existing_office = data.get("death_office", {}) or {}
            existing_office_items = _combat_death_office_items(existing_office)
            # A second death before the first grave is reclaimed pushes the old grave
            # to Death's Office; carry both loadouts so either set still re-equips.
            stacked_loadout = {
                **_combat_stored_loadout(existing_grave),
                **_combat_stored_loadout(existing_office),
            }
            _set_combat_death_office_items(
                data,
                existing_office_items + existing_grave_items,
                "combat_stacked_grave",
                stacked_loadout,
            )
    data["equipment"] = protected_equipment
    if not no_grave:
        data["combat_grave"] = {
            "items": grave_items,
            "reviews_remaining": COMBAT_GRAVE_RECOVERY_REVIEWS,
            "source": grave_source,
            "loadout": equipment,
        } if grave_items else {}
    data["combat_encounter"] = {}
    data["combat_status_effects"] = {}
    data["combat_lifepoints"] = max_player_lifepoints
    synced = sanitize_equipment_instance_state_pure(
        data, EQUIPMENT_CONDITION_DATA
    )
    data.clear()
    data.update(synced)
    return max_player_lifepoints


def combat_wilderness_equipment_risk_pure(player_data, enemy):
    risk = enemy.get("wilderness_risk") if isinstance(enemy, Mapping) else None
    if not isinstance(risk, Mapping):
        return {}
    equipment = dict(player_data.get("equipment", {}) or {})
    ranked = sorted(
        (
            (str(slot), str(item_name))
            for slot, item_name in equipment.items()
            if isinstance(slot, str)
            and slot
            and isinstance(item_name, str)
            and item_name
        ),
        key=lambda row: (
            _non_negative_int(ITEM_VALUES.get(row[1], 0), 0),
            row[1],
            row[0],
        ),
        reverse=True,
    )
    skulled = bool(player_data.get("combat_wilderness_skulled", False))
    keep_count = (
        0
        if skulled
        else _non_negative_int(risk.get("unskulled_items_kept", 3), 3)
    )
    protect_item = bool(prayer_effect_state_pure(player_data).get("protect_item"))
    if protect_item:
        keep_count += 1
    kept = ranked[:keep_count]
    lost = ranked[keep_count:]
    return {
        "skulled": skulled,
        "protect_item": protect_item,
        "kept_items": tuple(item_name for _slot, item_name in kept),
        "lost_items": tuple(item_name for _slot, item_name in lost),
        "kept_slots": dict(kept),
        "lost_slots": dict(lost),
    }


def _combat_apply_wilderness_death(
    data,
    enemy,
    max_player_lifepoints,
    confirmed_equipment_risk=None,
):
    loss = (
        dict(confirmed_equipment_risk)
        if isinstance(confirmed_equipment_risk, Mapping)
        else combat_wilderness_equipment_risk_pure(data, enemy)
    )
    discharged, _condition_events = discharge_equipped_on_unsafe_death_pure(
        data, EQUIPMENT_CONDITION_DATA
    )
    data.clear()
    data.update(discharged)
    discharged_equipment = data.get("equipment", {}) or {}
    kept_slots = {
        slot: discharged_equipment.get(slot, item_name)
        for slot, item_name in dict(loss.get("kept_slots", {}) or {}).items()
    }
    loss["kept_slots"] = kept_slots
    loss["kept_items"] = tuple(kept_slots.values())
    _combat_apply_follower_death(data)
    data["equipment"] = kept_slots
    data["combat_encounter"] = {}
    data["combat_status_effects"] = {}
    data["combat_lifepoints"] = max_player_lifepoints
    synced = sanitize_equipment_instance_state_pure(
        data, EQUIPMENT_CONDITION_DATA
    )
    data.clear()
    data.update(synced)
    return loss


def _combat_apply_wilderness_ambush(
    data,
    enemy,
    current_lifepoints,
    max_player_lifepoints,
    rng,
    confirmed_equipment_risk=None,
):
    risk = enemy.get("wilderness_risk") if isinstance(enemy, Mapping) else None
    if not isinstance(risk, Mapping):
        return None
    chance = max(0.0, min(1.0, float(risk.get("ambush_chance", 0.0) or 0.0)))
    try:
        triggered = float(rng()) < chance
    except (TypeError, ValueError):
        triggered = False
    max_hit = _positive_int(risk.get("max_hit", 1), 1)
    if not triggered:
        return {"triggered": False, "chance": chance, "max_hit": max_hit}
    try:
        damage_roll = max(0.0, min(float(rng()), 0.999999999))
    except (TypeError, ValueError):
        damage_roll = 0.0
    damage = 1 + int(damage_roll * max(1, max_hit - 1))
    lifepoints_before = max(0, int(current_lifepoints))
    lifepoints_after = max(0, lifepoints_before - damage)
    food_event = None
    died = lifepoints_after <= 0
    loss = {}
    if died:
        loss = _combat_apply_wilderness_death(
            data,
            enemy,
            max_player_lifepoints,
            confirmed_equipment_risk,
        )
    else:
        lifepoints_after, food_event = _combat_consume_auto_food(
            data,
            lifepoints_after,
            max_player_lifepoints,
            rng,
        )
        data["combat_lifepoints"] = lifepoints_after
        data["combat_encounter"] = {}
    return {
        "triggered": True,
        "chance": chance,
        "max_hit": max_hit,
        "damage": damage,
        "lifepoints_before": lifepoints_before,
        "lifepoints_after": 0 if died else lifepoints_after,
        "died": died,
        "food_used": food_event,
        "kept_items": tuple(loss.get("kept_items", ()) or ()),
        "lost_items": tuple(loss.get("lost_items", ()) or ()),
    }


def _sanitize_combat_observed_drops(raw_log):
    if not isinstance(raw_log, Mapping):
        return {}
    cleaned = {}
    for target_id, raw_items in raw_log.items():
        if len(cleaned) >= COMBAT_OBSERVED_DROP_TARGET_LIMIT:
            break
        if not isinstance(target_id, str) or not target_id or not isinstance(raw_items, Mapping):
            continue
        items = {}
        for item_name, raw_observation in raw_items.items():
            if len(items) >= COMBAT_OBSERVED_DROP_ITEM_LIMIT:
                break
            if not isinstance(item_name, str) or not item_name or not isinstance(raw_observation, Mapping):
                continue
            times_seen = min(
                COMBAT_OBSERVED_DROP_COUNT_LIMIT,
                _non_negative_int(raw_observation.get("times_seen", 0), 0),
            )
            quantity_seen = min(
                COMBAT_OBSERVED_DROP_COUNT_LIMIT,
                _non_negative_int(raw_observation.get("quantity_seen", 0), 0),
            )
            if times_seen > 0 and quantity_seen > 0:
                items[item_name] = {
                    "times_seen": times_seen,
                    "quantity_seen": quantity_seen,
                }
        if items:
            cleaned[target_id] = items
    return cleaned


def _sanitize_combat_examined_monsters(raw_targets, enemy_data):
    if not isinstance(raw_targets, (list, tuple)):
        return []
    cleaned = []
    for target_id in raw_targets:
        if (
            isinstance(target_id, str)
            and target_id in enemy_data
            and target_id not in cleaned
        ):
            cleaned.append(target_id)
    return cleaned


def _record_combat_observed_drops_pure(data, target_id, drops):
    if not isinstance(target_id, str) or not target_id or not isinstance(drops, Mapping):
        return
    observed = _sanitize_combat_observed_drops(data.get("combat_observed_drops"))
    target_drops = dict(observed.get(target_id, {}) or {})
    for item_name, raw_quantity in drops.items():
        if not isinstance(item_name, str) or not item_name:
            continue
        quantity = _non_negative_int(raw_quantity, 0)
        if quantity <= 0:
            continue
        if item_name not in target_drops and len(target_drops) >= COMBAT_OBSERVED_DROP_ITEM_LIMIT:
            continue
        previous = target_drops.get(item_name, {}) or {}
        target_drops[item_name] = {
            "times_seen": min(
                COMBAT_OBSERVED_DROP_COUNT_LIMIT,
                _non_negative_int(previous.get("times_seen", 0), 0) + 1,
            ),
            "quantity_seen": min(
                COMBAT_OBSERVED_DROP_COUNT_LIMIT,
                _non_negative_int(previous.get("quantity_seen", 0), 0) + quantity,
            ),
        }
    if target_drops and (target_id in observed or len(observed) < COMBAT_OBSERVED_DROP_TARGET_LIMIT):
        observed[target_id] = target_drops
    data["combat_observed_drops"] = observed


def sanitize_combat_state_pure(player_data, enemy_data=None, style_data=None):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    style_data = style_data or COMBAT_ATTACK_STYLE_DATA
    defaults = default_combat_state_pure()
    target = player_data.get("current_combat_target", defaults["current_combat_target"])
    if target not in enemy_data:
        target = defaults["current_combat_target"]
    if target not in enemy_data and enemy_data:
        target = next(iter(enemy_data))
    style = player_data.get("combat_attack_style", defaults["combat_attack_style"])
    if style not in style_data:
        style = defaults["combat_attack_style"]
    style_type = player_data.get("combat_attack_style_type", defaults["combat_attack_style_type"])
    if style_type not in _COMBAT_MELEE_STYLE_TYPES:
        style_type = defaults["combat_attack_style_type"]
    spell = player_data.get("current_combat_spell", defaults["current_combat_spell"])
    if spell not in COMBAT_MAGIC_SPELL_DATA:
        spell = defaults["current_combat_spell"]
    borrowed_spell = str(player_data.get("combat_borrowed_power_spell", "") or "")
    if borrowed_spell not in BORROWED_POWER_COMBAT_SPELLS:
        borrowed_spell = ""
    max_lp = combat_max_lifepoints_pure(player_data)
    current_lp = _non_negative_int(player_data.get("combat_lifepoints", max_lp), max_lp)
    auto_food_raw = player_data.get("combat_auto_eat_food", defaults["combat_auto_eat_food"])
    if isinstance(auto_food_raw, str):
        auto_food = [auto_food_raw]
    elif isinstance(auto_food_raw, Iterable):
        auto_food = [str(item) for item in auto_food_raw if isinstance(item, str) and item in COMBAT_FOOD_DATA]
    else:
        auto_food = []
    if not auto_food:
        auto_food = list(defaults["combat_auto_eat_food"])
    encounter = player_data.get("combat_encounter", {}) or {}
    if not isinstance(encounter, Mapping):
        encounter = {}
    dream_thrift = bool(player_data.get("combat_dream_thrift", False))
    dream_locked = bool(combat_dream_thrift_locked_reasons_pure(player_data))
    if dream_thrift and dream_locked:
        # The old casual dial could latch Dream on an ineligible save. Combat then
        # rejected every review before resolving the live encounter, leaving both
        # the invalid toggle and half-finished fight stuck across launches.
        dream_thrift = False
        encounter = {}
    kill_counts = player_data.get("combat_kill_counts", {}) or {}
    if not isinstance(kill_counts, Mapping):
        kill_counts = {}
    special_energy = _non_negative_int(
        player_data.get("combat_special_attack_energy", defaults["combat_special_attack_energy"]),
        defaults["combat_special_attack_energy"],
    )
    prayer_book = player_data.get("combat_prayer_book", "standard")
    if prayer_book not in ("standard", "curses"):
        prayer_book = "standard"
    temple_state = ((player_data.get("quests", {}) or {}).get("the_temple_at_senntisten") or {})
    if prayer_book == "curses" and not bool(temple_state.get("completed")):
        prayer_book = "standard"
    selected_prayers = list(sanitize_prayer_selection_pure(player_data, player_data.get("combat_selected_prayers", ()), prayer_book))
    uptime_policy = str(player_data.get("combat_prayer_uptime", "off"))
    if uptime_policy not in PRAYER_UPTIME_POLICIES:
        uptime_policy = "off"
    prayer_max = _positive_int(player_data.get("prayer_level", 1), 1) * 10
    presets = player_data.get("combat_presets")
    if not isinstance(presets, Mapping) or not presets:
        presets = {"Default": _combat_preset_snapshot({**defaults, **player_data})}
    else:
        presets = {str(name): dict(value) for name, value in presets.items() if isinstance(name, str) and isinstance(value, Mapping)}
    if not presets:
        presets = {"Default": _combat_preset_snapshot({**defaults, **player_data})}
    if dream_locked:
        for preset in presets.values():
            if bool(preset.get("combat_dream_thrift", False)):
                preset["combat_dream_thrift"] = False
    active_preset = str(player_data.get("combat_active_preset", "Default"))
    if active_preset not in presets:
        active_preset = next(iter(presets))
    target_overrides = {
        str(target_id): dict(values)
        for target_id, values in (player_data.get("combat_target_overrides", {}) or {}).items()
        if isinstance(target_id, str) and isinstance(values, Mapping)
    }
    if dream_locked:
        for values in target_overrides.values():
            if bool(values.get("combat_dream_thrift", False)):
                values["combat_dream_thrift"] = False
    return {
        "current_combat_target": target,
        "combat_action": (
            "finisher"
            if player_data.get("combat_action") == "finisher"
            else "attack"
        ),
        "combat_attack_style": style,
        "combat_attack_style_type": style_type,
        "current_combat_spell": spell,
        "combat_borrowed_power_spell": borrowed_spell,
        "combat_lifepoints": max(0, min(current_lp, max_lp + COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS)),
        "combat_auto_eat_threshold_percent": max(
            1,
            min(_positive_int(player_data.get("combat_auto_eat_threshold_percent", 40), 40), 99),
        ),
        "combat_auto_flee": bool(player_data.get("combat_auto_flee", True)),
        "combat_rest_reviews": _non_negative_int(player_data.get("combat_rest_reviews", 0), 0),
        "combat_auto_eat_food": auto_food,
        "combat_supply_loadout": _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout")),
        "combat_pack_mode": _combat_coerce_pack_mode(player_data.get("combat_pack_mode", _COMBAT_DEFAULT_PACK_MODE)),
        "combat_special_attack_energy": min(COMBAT_SPECIAL_ATTACK_MAX_ENERGY, special_energy),
        "combat_current_levels": _sanitize_combat_current_levels(player_data.get("combat_current_levels")),
        "combat_status_effects": _sanitize_combat_status_effects(player_data.get("combat_status_effects")),
        "combat_antifire_ticks_remaining": _non_negative_int(
            player_data.get("combat_antifire_ticks_remaining", 0),
            0,
        ),
        "combat_super_antifire_ticks_remaining": _non_negative_int(
            player_data.get("combat_super_antifire_ticks_remaining", 0),
            0,
        ),
        "combat_recovery_progress": _sanitize_combat_recovery_progress(player_data.get("combat_recovery_progress")),
        "combat_bank_run": _sanitize_combat_bank_run(player_data.get("combat_bank_run")),
        "combat_encounter": dict(encounter),
        "combat_kill_counts": {
            str(target_id): _positive_int(count, 0)
            for target_id, count in kill_counts.items()
            if isinstance(target_id, str)
        },
        "combat_observed_drops": _sanitize_combat_observed_drops(
            player_data.get("combat_observed_drops")
        ),
        "combat_examined_monsters": _sanitize_combat_examined_monsters(
            player_data.get("combat_examined_monsters"), enemy_data
        ),
        "combat_last_result": dict(player_data.get("combat_last_result", {}) or {}),
        "combat_grave": _sanitize_combat_grave_state(player_data.get("combat_grave", {}) or {}),
        "death_office": _sanitize_death_office_state(player_data.get("death_office", {}) or {}),
        "combat_prayer_book": prayer_book,
        "combat_selected_prayers": selected_prayers,
        "combat_prayer_uptime": uptime_policy,
        "combat_prayer_points": min(prayer_max, _non_negative_int(player_data.get("combat_prayer_points", prayer_max), prayer_max)),
        "combat_prayer_drain_counter": max(0.0, float(player_data.get("combat_prayer_drain_counter", 0.0) or 0.0)),
        "combat_auto_prayer_training": bool(player_data.get("combat_auto_prayer_training", False)),
        "combat_prayers_enabled": bool(player_data.get("combat_prayers_enabled", True)),
        "combat_vengeance": bool(player_data.get("combat_vengeance", False)),
        "combat_dream_thrift": dream_thrift,
        "combat_spellbook_swap": str(player_data.get("combat_spellbook_swap", "") or ""),
        "combat_presets": presets,
        "combat_active_preset": active_preset,
        "combat_target_presets": dict(player_data.get("combat_target_presets", {}) or {}),
        "combat_target_overrides": target_overrides,
        "knight_waves": sanitize_knight_waves_state_pure(player_data.get("knight_waves")),
    }


def combat_enemy_current_lifepoints_pure(player_data, target_id, enemy_data=None):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    enemy = enemy_data.get(target_id)
    if enemy is None:
        return 0
    encounter = player_data.get("combat_encounter", {}) or {}
    if isinstance(encounter, Mapping) and encounter.get("target_id") == target_id:
        return max(0, min(_positive_int(encounter.get("enemy_lifepoints", 0), 0), _positive_int(enemy.get("stats", {}).get("hitpoints", 0), 0)))
    return _positive_int(enemy.get("stats", {}).get("hitpoints", 0), 0)


def _combat_restricted_weapon_locked_reasons(
    player_data,
    target_id,
    enemy,
    combat_class,
    equipment_data,
):
    restriction = enemy.get("restricted_weapon")
    if not isinstance(restriction, Mapping):
        return tuple()
    target_name = str(enemy.get("display_name", target_id) or target_id)
    if combat_class == "melee":
        equipment = player_data.get("equipment", {}) or {}
        weapon_name = (
            equipment.get("weapon")
            if isinstance(equipment, Mapping)
            else None
        )
        allowed = tuple(restriction.get("melee_weapons", ()) or ())
        if allowed and weapon_name not in allowed:
            return (f"{target_name} weapon: " + " or ".join(allowed),)
    elif combat_class == "ranged":
        _weapon_name, _equipment_spec, weapon_spec = _combat_ranged_weapon_spec(
            player_data,
            equipment_data,
        )
        ammo_name = _combat_selected_ranged_ammo(
            player_data,
            weapon_spec,
            target_id,
        )
        allowed = tuple(restriction.get("ranged_ammunition", ()) or ())
        if allowed and ammo_name not in allowed:
            return (f"{target_name} ammunition: " + " or ".join(allowed),)
    elif combat_class == "magic":
        spell_id, _spell_spec = _combat_selected_magic_spell(player_data)
        allowed = tuple(restriction.get("magic_spells", ()) or ())
        if allowed and spell_id not in allowed:
            spell_names = tuple(
                str(COMBAT_MAGIC_SPELL_DATA.get(value, {}).get("display_name", value))
                for value in allowed
            )
            return (f"{target_name} spell: " + " or ".join(spell_names),)
    return tuple()


def combat_target_locked_reasons_pure(player_data, target_id, enemy_data=None, style_data=None, equipment_data=None):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    style_data = style_data or COMBAT_ATTACK_STYLE_DATA
    enemy = enemy_data.get(target_id)
    if enemy is None:
        return ("unknown enemy",)
    encounter = player_data.get("combat_encounter", {}) or {}
    if enemy.get("encounter_only") and not (
        isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
    ):
        return ("encounter only",)
    stats = enemy.get("stats", {})
    if not isinstance(stats, Mapping) or _positive_int(stats.get("hitpoints", 0), 0) <= 0:
        return ("missing source combat stats",)
    drops = enemy.get("drops")
    if not isinstance(drops, Mapping):
        return ("missing source drop behavior",)
    required_slayer_level = _positive_int(
        enemy.get("required_slayer_level", 0), 0
    )
    if (
        required_slayer_level > 0
        and _positive_int(player_data.get("slayer_level", 1), 1)
        < required_slayer_level
    ):
        return (f"Slayer level {required_slayer_level}",)
    skill_requirements = enemy.get("skill_requirements", {}) or {}
    if isinstance(skill_requirements, Mapping):
        missing_skill_requirements = tuple(
            f"{str(skill_id).replace('_', ' ').title()} level {required_level}"
            for skill_id, raw_required_level in skill_requirements.items()
            if (required_level := _positive_int(raw_required_level, 0)) > 0
            and _positive_int(player_data.get(f"{skill_id}_level", 1), 1)
            < required_level
        )
        if missing_skill_requirements:
            return missing_skill_requirements
    quest_gate = str(enemy.get("quest_gate", enemy.get("required_quest", "")) or "")
    if quest_gate:
        quests = player_data.get("quests", {}) or {}
        quest_state = quests.get(quest_gate, {}) if isinstance(quests, Mapping) else {}
        gate_state = str(enemy.get("quest_gate_state", "completed") or "completed")
        if isinstance(quest_state, Mapping):
            quest_accessible = bool(quest_state.get("completed"))
            if gate_state == "started":
                quest_accessible = quest_accessible or bool(quest_state.get("started"))
        else:
            quest_accessible = bool(quest_state)
        if not quest_accessible:
            verb = "Start" if gate_state == "started" else "Complete"
            return (
                str(
                    enemy.get(
                        "quest_gate_label",
                        f"{verb} {quest_gate.replace('_', ' ').title()}",
                    )
                ),
            )
    required_items = enemy.get("required_items", {}) or {}
    if isinstance(required_items, Mapping):
        inventory = player_data.get("inventory", {}) or {}
        inventory = inventory if isinstance(inventory, Mapping) else {}
        missing_required_items = [
            str(item_name)
            for item_name, raw_amount in required_items.items()
            if isinstance(item_name, str)
            and _non_negative_int(inventory.get(item_name, 0), 0)
            < max(1, _positive_int(raw_amount, 1))
        ]
        if missing_required_items:
            label = enemy.get("required_items_label")
            if isinstance(label, str) and label:
                return (label,)
            return tuple(f"{item_name} x1" for item_name in missing_required_items)
    required_item_options = enemy.get("required_item_options", ()) or ()
    if isinstance(required_item_options, (tuple, list)):
        inventory = player_data.get("inventory", {}) or {}
        inventory = inventory if isinstance(inventory, Mapping) else {}
        equipment = player_data.get("equipment", {}) or {}
        equipped_items = (
            {item_name for item_name in equipment.values() if isinstance(item_name, str)}
            if isinstance(equipment, Mapping)
            else set()
        )
        for option_group in required_item_options:
            if not isinstance(option_group, (tuple, list)):
                continue
            if not any(
                isinstance(item_name, str)
                and (
                    _non_negative_int(inventory.get(item_name, 0), 0) > 0
                    or item_name in equipped_items
                )
                for item_name in option_group
            ):
                label = enemy.get("required_item_options_label")
                if isinstance(label, str) and label:
                    return (label,)
                return ("Required item option missing",)
    start_equipment, start_equipment_active = _combat_start_equipment_state(
        player_data, enemy
    )
    active_encounter = (
        isinstance(encounter, Mapping)
        and encounter.get("target_id") == target_id
    )
    if (
        isinstance(start_equipment, Mapping)
        and not start_equipment_active
        and (
            not active_encounter
            or bool(start_equipment.get("persistent"))
        )
    ):
        return (
            str(
                start_equipment.get(
                    "warning",
                    "Required equipment must be worn to start this fight",
                )
            ),
        )
    hazard = _combat_environmental_hazard_spec(enemy)
    finisher = _combat_finisher_spec(enemy)
    encounter = player_data.get("combat_encounter", {}) or {}
    finisher_review_ready = bool(
        player_data.get("combat_action") == "finisher"
        and isinstance(encounter, Mapping)
        and encounter.get("target_id") == target_id
        and finisher is not None
        and 0
        < _positive_int(encounter.get("enemy_lifepoints", 0), 0)
        <= _positive_int(finisher.get("threshold_lifepoints", 0), 0)
    )
    if (
        hazard is not None
        and not finisher_review_ready
        and _combat_loaded_hazard_count(player_data, hazard) <= 0
        and _combat_banked_hazard_count(player_data, hazard) <= 0
    ):
        return (
            f"{hazard.get('display_name', 'Environmental hazard')}: "
            "filled Waterskin",
        )
    if enemy.get("warriors_guild_gate"):
        guild_locked = warriors_guild_cyclops_locked_reasons_pure(
            player_data,
            str(enemy.get("warriors_guild_target", target_id)),
        )
        if guild_locked:
            return guild_locked
    style_id = combat_attack_style_for_equipment_pure(player_data, equipment_data)
    style = style_data.get(style_id)
    if not isinstance(style, Mapping):
        return ("invalid attack style",)
    combat_class = style.get("combat_class")
    allowed_classes = tuple(enemy.get("allowed_combat_classes", ()) or ())
    if allowed_classes and combat_class not in allowed_classes:
        return (
            "Melee only inside the Warriors' Guild Cyclops room",
        )
    if combat_class == "melee":
        return _combat_restricted_weapon_locked_reasons(
            player_data,
            target_id,
            enemy,
            combat_class,
            equipment_data or {},
        )
    if combat_class == "ranged":
        restricted_reasons = _combat_restricted_weapon_locked_reasons(
            player_data,
            target_id,
            enemy,
            combat_class,
            equipment_data or {},
        )
        if restricted_reasons:
            return restricted_reasons
        locked_reasons = _combat_ranged_locked_reasons(
            player_data,
            target_id,
            equipment_data or {},
        )
        if locked_reasons:
            return locked_reasons
        return tuple()
    if combat_class == "magic":
        locked_reasons = _combat_magic_locked_reasons(
            player_data,
            target_id,
            equipment_data or {},
        )
        if locked_reasons:
            return locked_reasons
        return _combat_restricted_weapon_locked_reasons(
            player_data,
            target_id,
            enemy,
            combat_class,
            equipment_data or {},
        )
    return ("unsupported combat class",)


def _combat_attack_bonus_from_totals(totals, combat_class="melee", style_type=None):
    if combat_class == "magic":
        return _equipment_bonus_value(totals, "attack_magic")
    if combat_class == "ranged":
        return _equipment_bonus_value(totals, "attack_ranged")
    # D1 parity: the player's chosen attack type picks the specific bonus rather
    # than the old best-of-three max(). max() only survives when no concrete type
    # is resolved (e.g. enemy-side attacks, which carry no melee sub-type).
    if style_type in ("stab", "slash", "crush"):
        return _equipment_bonus_value(totals, f"attack_{style_type}")
    return max(
        _equipment_bonus_value(totals, "attack_stab"),
        _equipment_bonus_value(totals, "attack_slash"),
        _equipment_bonus_value(totals, "attack_crush"),
    )


def _combat_defence_bonus_from_totals(totals, combat_class="melee", style_type=None):
    if combat_class == "magic":
        return _equipment_bonus_value(totals, "defence_magic")
    if combat_class == "ranged":
        return _equipment_bonus_value(totals, "defence_ranged")
    # D1 parity: the enemy resists the exact attack type the player is throwing.
    if style_type in ("stab", "slash", "crush"):
        return _equipment_bonus_value(totals, f"defence_{style_type}")
    return max(
        _equipment_bonus_value(totals, "defence_stab"),
        _equipment_bonus_value(totals, "defence_slash"),
        _equipment_bonus_value(totals, "defence_crush"),
    )


def _combat_enemy_bonuses(enemy):
    bonuses = enemy.get("bonuses", {}) if isinstance(enemy, Mapping) else {}
    if not isinstance(bonuses, Mapping):
        bonuses = {}
    return EquipmentBonuses(**{field: _signed_int(bonuses.get(field, 0), 0) for field in EQUIPMENT_BONUS_FIELDS})


def _combat_effective_player_attack_level(player_data, style_id):
    level = _combat_effective_skill_level(player_data, "attack", 1)
    style_bonus = 3 if style_id == "accurate" else 1 if style_id == "controlled" else 0
    return floor(level) + style_bonus + 8


def _combat_effective_player_strength_level(player_data, style_id):
    level = _combat_effective_skill_level(player_data, "strength", 1)
    style_bonus = 3 if style_id == "aggressive" else 1
    return floor(level) + style_bonus + 8


def _combat_effective_player_defence_level(player_data, style_id):
    level = _combat_effective_skill_level(player_data, "defense", 1)
    style_bonus = (
        3
        if style_id in {"defensive", "ranged_longrange"}
        else 1
        if style_id == "controlled"
        else 0
    )
    return floor(level) + style_bonus + 8


def _combat_effective_player_ranged_level(player_data, style_id):
    level = _combat_effective_skill_level(player_data, "ranged", 1)
    style_bonus = 3 if style_id == "ranged_accurate" else 0
    return floor(level) + style_bonus + 8


def _combat_effective_player_magic_level(player_data):
    return floor(_combat_effective_skill_level(player_data, "magic", 1)) + 8


def _combat_base_skill_level(player_data, skill_id, default=1):
    return _positive_int(player_data.get(f"{skill_id}_level", default), default)


def _combat_effective_skill_level(player_data, skill_id, default):
    base_level = _combat_base_skill_level(player_data, skill_id, default)
    currents = player_data.get("combat_current_levels", {}) or {}
    if isinstance(currents, Mapping) and skill_id in currents:
        return max(1, _signed_int(currents.get(skill_id), base_level))
    return base_level


def _combat_accuracy(attacker_roll, defender_roll):
    attacker_roll = max(0, float(attacker_roll))
    defender_roll = max(0, float(defender_roll))
    if attacker_roll > defender_roll:
        return max(0.0, min(1.0, 1.0 - (defender_roll + 2.0) / (2.0 * (attacker_roll + 1.0))))
    return max(0.0, min(1.0, attacker_roll / (2.0 * (defender_roll + 1.0))))


def _combat_melee_max_hit_old_hp(effective_strength, strength_bonus):
    return max(0.0, 0.5 + float(effective_strength) * (float(strength_bonus) + 64.0) / 640.0)


COMBAT_ENEMY_ATTACK_STYLES = ("melee", "ranged", "magic", "magic_melee")


def _combat_enemy_attack_style(enemy, player_combat_class=None):
    if not isinstance(enemy, Mapping):
        return "melee"
    by_player_class = enemy.get("attack_style_by_player_class")
    if isinstance(by_player_class, Mapping):
        resolved = by_player_class.get(player_combat_class)
        if resolved in COMBAT_ENEMY_ATTACK_STYLES:
            return resolved
    style = enemy.get("attack_style", "melee")
    return style if style in COMBAT_ENEMY_ATTACK_STYLES else "melee"


def _combat_enemy_attack_class(enemy, player_combat_class=None):
    """The style the ENEMY attacks with. Determines which of its attack bonuses
    drives its accuracy and which of the player's defence bonuses resists it.
    Magic-based melee rolls against Magic defence while retaining melee damage
    and protection-prayer semantics. Unknown values fall back to melee."""
    style = _combat_enemy_attack_style(enemy, player_combat_class)
    if style == "magic_melee":
        return "magic"
    return style


def _combat_enemy_protection_class(enemy, player_combat_class=None):
    if _combat_enemy_attack_style(enemy, player_combat_class) == "magic_melee":
        return "melee"
    return _combat_enemy_attack_class(enemy, player_combat_class)


def _combat_select_enemy_attack_pure(enemy, rng):
    """Select one generic weighted enemy attack row, or its ordinary attack."""
    table = enemy.get("attack_table") if isinstance(enemy, Mapping) else None
    if not isinstance(table, (list, tuple)):
        return {"kind": "attack"}
    rows = [
        dict(row)
        for row in table
        if isinstance(row, Mapping) and _positive_int(row.get("weight", 0), 0) > 0
    ]
    total = sum(_positive_int(row.get("weight", 0), 0) for row in rows)
    if not rows or total <= 0:
        return {"kind": "attack"}
    try:
        cursor = max(0.0, min(float(rng()), 0.999999999999)) * total
    except (TypeError, ValueError, OverflowError):
        cursor = 0.0
    for row in rows:
        cursor -= _positive_int(row.get("weight", 0), 0)
        if cursor < 0:
            return row
    return rows[-1]


def _combat_enemy_max_hit_old_hp(enemy, effective_strength, strength_bonus, enemy_totals=None):
    configured_lp_hit = _positive_int(enemy.get("max_hit", 0), 0) if isinstance(enemy, Mapping) else 0
    if configured_lp_hit > 0:
        return configured_lp_hit / 10.0
    configured_old_hit = _positive_int(enemy.get("max_hit_old_hp", 0), 0) if isinstance(enemy, Mapping) else 0
    if configured_old_hit > 0:
        return float(configured_old_hit)
    # A ranged attacker's hit scales off its ranged level + ranged strength, not
    # melee strength. A magic attacker's hit is spell-defined in the source, so it
    # must declare max_hit; without one we fall back to the melee derivation rather
    # than silently dealing zero (the roster test forbids that data gap).
    if enemy_totals is not None and _combat_enemy_attack_class(enemy) == "ranged":
        return _combat_ranged_max_hit_old_hp(
            _positive_int(enemy.get("stats", {}).get("ranged", 1), 1) + 8,
            _equipment_bonus_value(enemy_totals, "ranged_strength"),
        )
    return _combat_melee_max_hit_old_hp(effective_strength, strength_bonus)


def _combat_protective_equipment_state(
    player_data, enemy, player_combat_class=None
):
    protection = enemy.get("protective_equipment") if isinstance(enemy, Mapping) else None
    if not isinstance(protection, Mapping):
        return None, True
    protected_classes = tuple(
        value
        for value in (protection.get("applies_to_player_classes", ()) or ())
        if isinstance(value, str)
    )
    if protected_classes and player_combat_class not in protected_classes:
        return protection, True
    equipment = player_data.get("equipment", {}) or {}
    if not isinstance(equipment, Mapping):
        equipment = {}
    alternatives = protection.get("alternatives", ()) or ()
    if alternatives:
        return protection, any(
            isinstance(alternative, Mapping)
            and isinstance(alternative.get("slot"), str)
            and equipment.get(alternative["slot"])
            in (alternative.get("items", ()) or ())
            for alternative in alternatives
        )
    slot = protection.get("slot")
    required_items = protection.get("items", ()) or ()
    equipped_item = equipment.get(slot) if isinstance(slot, str) else None
    return protection, equipped_item in required_items


def _combat_weakening_equipment_state(player_data, enemy):
    weakness = enemy.get("weakening_equipment") if isinstance(enemy, Mapping) else None
    if not isinstance(weakness, Mapping):
        return None, False
    equipment = player_data.get("equipment", {}) or {}
    if not isinstance(equipment, Mapping):
        equipment = {}
    slot = weakness.get("slot")
    weakening_items = weakness.get("items", ()) or ()
    equipped_item = equipment.get(slot) if isinstance(slot, str) else None
    return weakness, equipped_item in weakening_items


def _combat_start_equipment_state(player_data, enemy):
    requirement = (
        enemy.get("start_equipment") if isinstance(enemy, Mapping) else None
    )
    if not isinstance(requirement, Mapping):
        return None, True
    equipment = player_data.get("equipment", {}) or {}
    if not isinstance(equipment, Mapping):
        equipment = {}
    slot = requirement.get("slot")
    required_items = requirement.get("items", ()) or ()
    equipped_item = equipment.get(slot) if isinstance(slot, str) else None
    return requirement, equipped_item in required_items


def _combat_unprotected_damage_lifepoints(effect, max_lifepoints, rng=None):
    damage = effect.get("damage") if isinstance(effect, Mapping) else None
    if not isinstance(damage, Mapping):
        return 0
    if damage.get("kind") == "fixed":
        return _non_negative_int(damage.get("amount", 0), 0)
    if damage.get("kind") == "uniform_max":
        maximum = _non_negative_int(damage.get("max", 0), 0)
        if not callable(rng):
            return maximum
        try:
            roll = max(0.0, min(float(rng()), 0.999999999999))
        except (TypeError, ValueError):
            roll = 0.0
        return int(roll * (maximum + 1))
    if damage.get("kind") != "max_lifepoints_fraction_capped":
        return 0
    numerator = _positive_int(damage.get("numerator", 1), 1)
    denominator = _positive_int(damage.get("denominator", 1), 1)
    amount = max(1, _positive_int(max_lifepoints, 1) * numerator // denominator)
    cap = _positive_int(damage.get("cap", amount), amount)
    return min(amount, cap)


def _combat_apply_unprotected_stat_drains(data, effect, rng=None):
    drain = effect.get("stat_drain") if isinstance(effect, Mapping) else None
    if not isinstance(drain, Mapping):
        return {}
    kind = drain.get("kind")
    if kind not in ("base_fraction_to_floor", "flat_to_floor"):
        return {}
    if kind == "base_fraction_to_floor":
        numerator = _positive_int(drain.get("numerator", 1), 1)
        denominator = _positive_int(drain.get("denominator", 1), 1)
        floor_numerator = _positive_int(drain.get("floor_numerator", 1), 1)
        floor_denominator = _positive_int(drain.get("floor_denominator", 1), 1)
    else:
        flat_amount = _positive_int(drain.get("amount", 1), 1)
        flat_floor = _positive_int(drain.get("floor", 1), 1)
    skills = tuple(
        skill_id
        for skill_id in (drain.get("skills", ()) or ())
        if isinstance(skill_id, str)
    )
    if drain.get("selection") == "random_one" and skills:
        try:
            roll = float(rng()) if callable(rng) else 0.0
        except (TypeError, ValueError):
            roll = 0.0
        index = min(
            len(skills) - 1,
            int(max(0.0, min(roll, 0.999999999)) * len(skills)),
        )
        skills = (skills[index],)
    applied = {}
    for skill_id in skills:
        base = _combat_base_skill_level(data, skill_id, 1)
        current = _combat_effective_skill_level(data, skill_id, base)
        if kind == "base_fraction_to_floor":
            floor_level = max(1, base * floor_numerator // floor_denominator)
            amount = max(1, base * numerator // denominator)
        else:
            floor_level = flat_floor
            amount = flat_amount
        updated = max(floor_level, current - amount)
        if updated < current:
            apply_combat_stat_delta_pure(data, skill_id, updated - current)
            applied[skill_id] = current - updated
    return applied


def _combat_finisher_spec(enemy):
    finisher = enemy.get("finisher") if isinstance(enemy, Mapping) else None
    return finisher if isinstance(finisher, Mapping) else None


def _combat_finisher_charge_items(finisher):
    if not isinstance(finisher, Mapping):
        return ()
    rows = []
    for row in finisher.get("charge_items", ()) or ():
        if not isinstance(row, (tuple, list)) or len(row) < 2:
            continue
        item_name = row[0]
        charges = _positive_int(row[1], 0)
        if isinstance(item_name, str) and item_name and charges > 0:
            rows.append((item_name, charges))
    return tuple(rows)


def _combat_loaded_finisher_charge_state(data, finisher):
    charge_items = _combat_finisher_charge_items(finisher)
    if not charge_items:
        return 0, 0, 0
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    finishers = loadout.get("finishers", {}) or {}
    empty_item = str(finisher.get("empty_item", "") or "")
    reload_item = str(finisher.get("reload_item", "") or "")
    tool_count = sum(
        _non_negative_int(finishers.get(item_name, 0), 0)
        for item_name, _charges in charge_items
    )
    if empty_item:
        tool_count += _non_negative_int(finishers.get(empty_item, 0), 0)
    charges = sum(
        _non_negative_int(finishers.get(item_name, 0), 0) * charge_count
        for item_name, charge_count in charge_items
    )
    reloads = (
        _non_negative_int(finishers.get(reload_item, 0), 0)
        if reload_item and tool_count > 0
        else 0
    )
    reload_charges = _positive_int(finisher.get("reload_charges", 0), 0)
    return charges, reloads, charges + reloads * reload_charges


def _combat_environmental_hazard_spec(enemy):
    hazard = (
        enemy.get("environmental_hazard")
        if isinstance(enemy, Mapping)
        else None
    )
    return hazard if isinstance(hazard, Mapping) else None


def _combat_hazard_dose_items(hazard):
    if not isinstance(hazard, Mapping):
        return ()
    return tuple(
        item_name
        for item_name in hazard.get("dose_items", ()) or ()
        if isinstance(item_name, str) and item_name
    )


def _combat_loaded_hazard_count(data, hazard):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    supplies = loadout.get("hazards", {}) or {}
    return sum(
        _non_negative_int(supplies.get(item_name, 0), 0)
        for item_name in _combat_hazard_dose_items(hazard)
    )


def _combat_banked_hazard_count(data, hazard):
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return 0
    return sum(
        _non_negative_int(inventory.get(item_name, 0), 0)
        for item_name in _combat_hazard_dose_items(hazard)
    )


def _combat_consume_hazard_dose(data, hazard):
    dose_items = _combat_hazard_dose_items(hazard)
    if not dose_items:
        return None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    supplies = dict(loadout.get("hazards", {}) or {})
    for index, item_name in enumerate(dose_items):
        current = _non_negative_int(supplies.get(item_name, 0), 0)
        if current <= 0:
            continue
        if current == 1:
            supplies.pop(item_name, None)
        else:
            supplies[item_name] = current - 1
        replacement = (
            dose_items[index + 1]
            if index + 1 < len(dose_items)
            else str(hazard.get("empty_item", "") or "")
        )
        if replacement:
            supplies[replacement] = (
                _non_negative_int(supplies.get(replacement, 0), 0) + 1
            )
        loadout["hazards"] = supplies
        data["combat_supply_loadout"] = loadout
        return {"item": item_name, "replacement": replacement}
    return None


def _combat_equipped_item_count(player_data, item_name):
    equipment = player_data.get("equipment", {}) or {}
    if not isinstance(equipment, Mapping):
        return 0
    return sum(1 for equipped in equipment.values() if equipped == item_name)


def _combat_loaded_finisher_count(player_data, item_name, finisher=None):
    if not isinstance(item_name, str) or not item_name:
        return 0
    if isinstance(finisher, Mapping) and finisher.get("must_be_worn"):
        return _combat_equipped_item_count(player_data, item_name)
    if _combat_finisher_charge_items(finisher):
        _charges, _reloads, total_uses = _combat_loaded_finisher_charge_state(
            player_data, finisher
        )
        return total_uses
    loadout = _sanitize_combat_supply_loadout(
        player_data.get("combat_supply_loadout")
    )
    return _non_negative_int(
        (loadout.get("finishers", {}) or {}).get(item_name, 0), 0
    )


def combat_finisher_state_pure(player_data, target_id=None, enemy_data=None):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    target_id = (
        target_id
        if isinstance(target_id, str)
        else player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    )
    enemy = enemy_data.get(target_id) if isinstance(enemy_data, Mapping) else None
    finisher = _combat_finisher_spec(enemy)
    if finisher is None:
        return {
            "required": False,
            "ready": False,
            "available": False,
            "automatic": False,
            "item": "",
            "item_count": 0,
            "threshold_lifepoints": 0,
            "action_label": "",
            "consumable": False,
            "charged": False,
            "charges": 0,
            "reloads": 0,
        }
    item_name = str(finisher.get("item", "") or "")
    display_item = str(finisher.get("display_item", item_name) or item_name)
    threshold = _positive_int(finisher.get("threshold_lifepoints", 0), 0)
    encounter = player_data.get("combat_encounter", {}) or {}
    enemy_lifepoints = (
        _positive_int(encounter.get("enemy_lifepoints", 0), 0)
        if isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
        else 0
    )
    ready = 0 < enemy_lifepoints <= threshold
    item_count = _combat_loaded_finisher_count(player_data, item_name, finisher)
    charge_items = _combat_finisher_charge_items(finisher)
    charges, reloads, _total_uses = _combat_loaded_finisher_charge_state(
        player_data, finisher
    )
    quick_unlock_key = str(finisher.get("quick_unlock_key", "") or "")
    return {
        "required": True,
        "ready": ready,
        "available": ready and item_count > 0,
        "automatic": bool(
            quick_unlock_key and player_data.get(quick_unlock_key, False)
        ),
        "item": display_item,
        "item_count": item_count,
        "threshold_lifepoints": threshold,
        "action_label": str(
            finisher.get("action_label", f"Use {item_name}") or f"Use {item_name}"
        ),
        "consumable": bool(finisher.get("consume", False)),
        "charged": bool(charge_items),
        "charges": charges,
        "reloads": reloads,
        "enemy_lifepoints": enemy_lifepoints,
    }


def _combat_consume_loaded_finisher(data, finisher):
    item_name = str(finisher.get("item", "") or "")
    if finisher.get("must_be_worn"):
        return _combat_equipped_item_count(data, item_name) > 0
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    finishers = dict(loadout.get("finishers", {}) or {})
    charge_items = _combat_finisher_charge_items(finisher)
    if charge_items:
        for index, (charged_item, _charges) in enumerate(charge_items):
            current = _non_negative_int(finishers.get(charged_item, 0), 0)
            if current <= 0:
                continue
            if current == 1:
                finishers.pop(charged_item, None)
            else:
                finishers[charged_item] = current - 1
            replacement = (
                charge_items[index + 1][0]
                if index + 1 < len(charge_items)
                else str(finisher.get("empty_item", "") or "")
            )
            if replacement:
                finishers[replacement] = (
                    _non_negative_int(finishers.get(replacement, 0), 0) + 1
                )
            loadout["finishers"] = finishers
            data["combat_supply_loadout"] = loadout
            return True

        empty_item = str(finisher.get("empty_item", "") or "")
        reload_item = str(finisher.get("reload_item", "") or "")
        empty_count = _non_negative_int(finishers.get(empty_item, 0), 0)
        reload_count = _non_negative_int(finishers.get(reload_item, 0), 0)
        if empty_count <= 0 or reload_count <= 0:
            return False
        if empty_count == 1:
            finishers.pop(empty_item, None)
        else:
            finishers[empty_item] = empty_count - 1
        if reload_count == 1:
            finishers.pop(reload_item, None)
        else:
            finishers[reload_item] = reload_count - 1
        replacement_charges = max(
            0, _positive_int(finisher.get("reload_charges", 0), 0) - 1
        )
        replacement = next(
            (
                charged_item
                for charged_item, charges in charge_items
                if charges == replacement_charges
            ),
            empty_item,
        )
        if replacement:
            finishers[replacement] = (
                _non_negative_int(finishers.get(replacement, 0), 0) + 1
            )
        loadout["finishers"] = finishers
        data["combat_supply_loadout"] = loadout
        return True

    current = _non_negative_int(finishers.get(item_name, 0), 0)
    if current <= 0:
        return False
    if bool(finisher.get("consume", False)):
        current -= 1
        if current > 0:
            finishers[item_name] = current
        else:
            finishers.pop(item_name, None)
        loadout["finishers"] = finishers
        data["combat_supply_loadout"] = loadout
    return True


def _combat_cap_damage_for_finisher(
    data, finisher, enemy_lifepoints, damage, *, allow_automatic=True
):
    enemy_lifepoints = _non_negative_int(enemy_lifepoints, 0)
    if enemy_lifepoints <= 0:
        return 0, False
    damage = min(
        enemy_lifepoints,
        _non_negative_int(damage, 0),
    )
    if finisher is None or damage < enemy_lifepoints:
        return damage, False
    quick_unlock_key = str(finisher.get("quick_unlock_key", "") or "")
    if (
        allow_automatic
        and (
            bool(finisher.get("must_be_worn"))
            or (quick_unlock_key and bool(data.get(quick_unlock_key, False)))
        )
        and _combat_consume_loaded_finisher(data, finisher)
    ):
        return damage, True
    return enemy_lifepoints - 1, False


def _combat_ranged_max_hit_old_hp(effective_ranged, ranged_strength_bonus):
    return max(0.0, 0.5 + float(effective_ranged) * (float(ranged_strength_bonus) + 64.0) / 640.0)


def charged_god_spell_max_hit_bonus_pure(player_data, spell_id):
    god_id = MAGE_ARENA_SPELL_TO_GOD.get(str(spell_id))
    if not god_id:
        return 0
    if not bool(player_data.get("magic_charge_active", False)):
        return 0
    if _non_negative_int(player_data.get("magic_charge_ticks_remaining", 0), 0) <= 0:
        return 0
    row = MAGE_ARENA_GOD_DATA[god_id]
    equipment = player_data.get("equipment", {}) or {}
    if (
        equipment.get("cape") != row["cape"]
        or equipment.get("weapon") != row["staff"]
    ):
        return 0
    state = sanitize_mage_arena_state_pure(player_data.get("mage_arena"))
    return 10 if row["spell_id"] in state["attuned_spells"] else 0


def _combat_magic_max_hit_old_hp(
    spell_spec,
    player_totals,
    player_data=None,
    spell_id=None,
):
    if not isinstance(spell_spec, Mapping):
        return 0.0
    base_hit = _positive_int(spell_spec.get("max_hit_old_hp", 0), 0)
    if isinstance(player_data, Mapping):
        base_hit += charged_god_spell_max_hit_bonus_pure(
            player_data,
            spell_id or spell_spec.get("id", ""),
        )
    multiplier = 1.0 + (_equipment_bonus_value(player_totals, "magic_damage") / 100.0)
    return max(0.0, floor(float(base_hit) * multiplier))


def _combat_equipped_weapon_name(player_data):
    equipment = player_data.get("equipment", {}) or {}
    if not isinstance(equipment, Mapping):
        return None
    weapon_name = equipment.get("weapon")
    return weapon_name if isinstance(weapon_name, str) else None


def _combat_ranged_weapon_spec(player_data, equipment_data):
    weapon_name = _combat_equipped_weapon_name(player_data)
    if not isinstance(weapon_name, str):
        return weapon_name, None, None
    equipment_spec = equipment_data.get(weapon_name) if isinstance(equipment_data, Mapping) else None
    equipment_type = _equipment_value(equipment_spec, "equipment_type", None)
    weapon_spec = COMBAT_RANGED_WEAPON_DATA.get(weapon_name)
    if weapon_spec is None and isinstance(equipment_type, str):
        for candidate in COMBAT_RANGED_WEAPON_DATA.values():
            if candidate.get("equipment_type") == equipment_type:
                weapon_spec = candidate
                break
    return weapon_name, equipment_spec, weapon_spec


def _combat_weapon_equipment_type(player_data, equipment_data=None):
    weapon_name = _combat_equipped_weapon_name(player_data)
    if not isinstance(weapon_name, str):
        return weapon_name, None, None
    equipment_spec = equipment_data.get(weapon_name) if isinstance(equipment_data, Mapping) else None
    return weapon_name, equipment_spec, _equipment_value(equipment_spec, "equipment_type", None)


def _combat_weapon_is_ranged(player_data, equipment_data=None):
    weapon_name, _equipment_spec, equipment_type = _combat_weapon_equipment_type(player_data, equipment_data)
    if not isinstance(weapon_name, str):
        return False
    if weapon_name in COMBAT_RANGED_WEAPON_DATA:
        return True
    if isinstance(equipment_type, str):
        return any(spec.get("equipment_type") == equipment_type for spec in COMBAT_RANGED_WEAPON_DATA.values())
    return False


def _combat_weapon_is_magic(player_data, equipment_data=None):
    weapon_name, _equipment_spec, equipment_type = _combat_weapon_equipment_type(player_data, equipment_data)
    if not isinstance(weapon_name, str):
        return False
    return weapon_name in COMBAT_MAGIC_STAFF_DATA or equipment_type in _COMBAT_MAGIC_EQUIPMENT_TYPES


def _combat_weapon_type_id(player_data, equipment_data=None):
    """The equipped weapon's items.yml ``weapon_type`` id, or -1 for bare fists /
    typeless weapons (which fall back to the UNARMED table, D3)."""
    weapon_name = _combat_equipped_weapon_name(player_data)
    if not isinstance(weapon_name, str):
        return -1
    equipment_spec = equipment_data.get(weapon_name) if isinstance(equipment_data, Mapping) else None
    return _signed_int(_equipment_value(equipment_spec, "weapon_type", -1), -1)


def combat_weapon_attack_style_slots_pure(player_data, equipment_data=None):
    """Ordered melee attack-style slots (weapon_style/style_type/xp_mode) the
    equipped weapon offers, transcribed from AttackStyleData.kt. Typeless weapons
    and bare fists fall back to the UNARMED table (all crush, D3). Drives the D2
    per-weapon style selector."""
    weapon_type = _combat_weapon_type_id(player_data, equipment_data)
    return WEAPON_TYPE_ATTACK_STYLES.get(weapon_type, WEAPON_TYPE_UNARMED_STYLES)


def _combat_resolve_melee_slot(player_data, equipment_data=None):
    """The AttackStyleData slot the player actually swings with: the stored
    combat_attack_style (weapon_style) narrowed to a slot the equipped weapon
    offers, then narrowed again by the orthogonal combat_attack_style_type
    preference. Guarantees weapon_style, style_type and xp_mode stay mutually
    consistent even after a weapon swap leaves a now-unavailable style stored."""
    slots = combat_weapon_attack_style_slots_pure(player_data, equipment_data)
    stored_style = str(player_data.get("combat_attack_style", DEFAULT_COMBAT_ATTACK_STYLE))
    chosen_type = str(player_data.get("combat_attack_style_type", "auto"))
    matching = [slot for slot in slots if slot["weapon_style"] == stored_style]
    if not matching:
        return slots[0]
    if chosen_type in ("stab", "slash", "crush"):
        for slot in matching:
            if slot["style_type"] == chosen_type:
                return slot
    return matching[0]


def combat_attack_style_for_equipment_pure(player_data, equipment_data=None):
    stored_style = str(player_data.get("combat_attack_style", DEFAULT_COMBAT_ATTACK_STYLE))
    if _combat_weapon_is_ranged(player_data, equipment_data):
        return stored_style if stored_style in _COMBAT_RANGED_STYLE_IDS else "ranged_accurate"
    if _combat_weapon_is_magic(player_data, equipment_data):
        return "magic_standard"
    return _combat_resolve_melee_slot(player_data, equipment_data)["weapon_style"]


def combat_melee_attack_type_pure(player_data, equipment_data=None):
    """(style_type, xp_style_id) for the equipped melee weapon. style_type
    ("stab"/"slash"/"crush") drives the D1 attack/defence-type parity; xp_style_id
    feeds _combat_apply_xp and captures the two-handed-sword aggressive/crush/SHARED
    anomaly. Returns (None, resolved-style-id) for ranged/magic, where the existing
    max()/xp paths already apply."""
    if _combat_weapon_is_ranged(player_data, equipment_data) or _combat_weapon_is_magic(player_data, equipment_data):
        return None, combat_attack_style_for_equipment_pure(player_data, equipment_data)
    slot = _combat_resolve_melee_slot(player_data, equipment_data)
    return slot["style_type"], _COMBAT_XP_MODE_TO_STYLE_ID[slot["xp_mode"]]


def _combat_ranged_ammo_count(player_data, ammo_name, target_id):
    loadout = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    loaded = _non_negative_int((loadout.get("ammo", {}) or {}).get(ammo_name, 0), 0)
    encounter = player_data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
    if active_encounter:
        return loaded
    inventory = player_data.get("inventory", {}) or {}
    banked = _non_negative_int(inventory.get(ammo_name, 0), 0) if isinstance(inventory, Mapping) else 0
    return loaded + banked


def _combat_selected_ranged_ammo(
    player_data,
    weapon_spec,
    target_id,
    allowed_ammo=None,
):
    if not isinstance(weapon_spec, Mapping):
        return None
    compatible_ammo = tuple(weapon_spec.get("compatible_ammo", ()) or ())
    if allowed_ammo is None:
        enemy = COMBAT_ENEMY_DATA.get(target_id, {})
        restriction = (
            enemy.get("restricted_weapon")
            if isinstance(enemy, Mapping)
            else None
        )
        if isinstance(restriction, Mapping):
            allowed_ammo = restriction.get("ranged_ammunition")
    if allowed_ammo:
        allowed = set(allowed_ammo)
        compatible_ammo = tuple(
            ammo_name for ammo_name in compatible_ammo if ammo_name in allowed
        )
    loadout = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    loaded_ammo = loadout.get("ammo", {}) or {}
    for ammo_name in compatible_ammo:
        if isinstance(ammo_name, str) and _non_negative_int(loaded_ammo.get(ammo_name, 0), 0) > 0:
            return ammo_name
    for ammo_name in compatible_ammo:
        if isinstance(ammo_name, str) and _combat_ranged_ammo_count(player_data, ammo_name, target_id) > 0:
            return ammo_name
    return None


def _combat_ranged_locked_reasons(player_data, target_id, equipment_data):
    weapon_name, equipment_spec, weapon_spec = _combat_ranged_weapon_spec(player_data, equipment_data)
    if not isinstance(weapon_name, str):
        return ("ranged weapon",)
    if equipment_spec is None or _equipment_value(equipment_spec, "combat_skill", None) != "ranged":
        return ("ranged weapon",)
    if not isinstance(weapon_spec, Mapping):
        return ("supported ranged weapon",)
    ammo_name = _combat_selected_ranged_ammo(player_data, weapon_spec, target_id)
    if ammo_name is None:
        return ("compatible ammunition",)
    ammo_spec = equipment_data.get(ammo_name)
    for combat_skill, required_level, level_key in _equipment_skill_requirements(
        ammo_spec
    ):
        current_level = _positive_int(player_data.get(level_key, 1), 1)
        if current_level < required_level:
            return (f"{_combat_skill_label(combat_skill)} level {required_level}",)
    return tuple()


def _combat_selected_magic_spell(player_data):
    borrowed_spell_id = str(
        player_data.get("combat_borrowed_power_spell", "") or ""
    )
    if borrowed_spell_id in BORROWED_POWER_COMBAT_SPELLS:
        borrowed_spec = COMBAT_MAGIC_SPELL_DATA.get(borrowed_spell_id)
        if isinstance(borrowed_spec, Mapping):
            manual_spec = dict(borrowed_spec)
            manual_spec["display_name"] = (
                "Borrowed Power — "
                + str(borrowed_spec.get("display_name", borrowed_spell_id))
            )
            manual_spec["rune_cost"] = {"Astral rune": 3}
            manual_spec["borrowed_spell_id"] = borrowed_spell_id
            return borrowed_spell_id, manual_spec
    spell_id = str(player_data.get("current_combat_spell", DEFAULT_COMBAT_SPELL))
    spell_spec = COMBAT_MAGIC_SPELL_DATA.get(spell_id)
    if isinstance(spell_spec, Mapping):
        return spell_id, spell_spec
    return DEFAULT_COMBAT_SPELL, COMBAT_MAGIC_SPELL_DATA.get(DEFAULT_COMBAT_SPELL, {})


def combat_staff_covered_runes_pure(player_data, equipment_data=None):
    equipment = player_data.get("equipment", {}) or {}
    if not isinstance(equipment, Mapping):
        return {}
    weapon_name = equipment.get("weapon")
    if not isinstance(weapon_name, str):
        return {}
    staff_spec = COMBAT_MAGIC_STAFF_DATA.get(weapon_name)
    if not isinstance(staff_spec, Mapping):
        return {}
    if isinstance(equipment_data, Mapping) and equipment_data:
        equipment_spec = equipment_data.get(weapon_name)
        if equipment_spec is None or _equipment_value(equipment_spec, "slot", "") != "weapon":
            return {}
    covered_runes = staff_spec.get("covered_runes", ())
    if isinstance(covered_runes, str):
        covered_runes = (covered_runes,)
    if not isinstance(covered_runes, Iterable):
        return {}
    return {rune_name: weapon_name for rune_name in covered_runes if isinstance(rune_name, str)}


def _combat_effective_rune_cost_pure(player_data, rune_cost, equipment_data=None):
    covered_runes = combat_staff_covered_runes_pure(player_data, equipment_data)
    return {
        str(rune_name): _positive_int(amount, 0)
        for rune_name, amount in (rune_cost or {}).items()
        if isinstance(rune_name, str)
        and rune_name not in covered_runes
        and _positive_int(amount, 0) > 0
    }


def _combat_spellbook_swap_applies_pure(player_data):
    spell_id = str(player_data.get("current_combat_spell", DEFAULT_COMBAT_SPELL))
    spell = COMBAT_MAGIC_SPELL_DATA.get(spell_id, {})
    equipment = player_data.get("equipment", {}) or {}
    effects = []
    if str(equipment.get("weapon", "") or "") in COMBAT_MAGIC_STAFF_DATA:
        effects.append((spell_id, str(spell.get("spellbook", "standard"))))
    if bool(player_data.get("combat_vengeance", False)):
        effects.append(("vengeance", "lunar"))
    if bool(player_data.get("combat_dream_thrift", False)):
        effects.append(("dream", "lunar"))
    swap_spell = str(player_data.get("combat_spellbook_swap", "") or "")
    return bool(swap_spell and len({book for _effect, book in effects}) > 1)


def _combat_pending_supplemental_magic_costs_pure(player_data, equipment_data=None):
    target_id = str(player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET))
    encounter = player_data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
    swap_paid = bool(active_encounter and encounter.get("spellbook_swap_paid", False))
    vengeance_pending = bool(active_encounter and encounter.get("vengeance_pending", False))
    costs = []
    if _combat_spellbook_swap_applies_pure(player_data) and not swap_paid:
        costs.append(("spellbook_swap", SPELLBOOK_SWAP_COST, 130.0))
    if bool(player_data.get("combat_vengeance", False)) and not vengeance_pending:
        costs.append(("vengeance", VENGEANCE_COST, 112.0))
    return tuple(
        (label, _combat_effective_rune_cost_pure(player_data, raw_cost, equipment_data), xp)
        for label, raw_cost, xp in costs
    )


def _combat_supplemental_rune_cost_pure(player_data, equipment_data=None):
    combined = {}
    for _label, cost, _xp in _combat_pending_supplemental_magic_costs_pure(player_data, equipment_data):
        for rune_name, amount in cost.items():
            combined[rune_name] = _non_negative_int(combined.get(rune_name, 0), 0) + amount
    return combined


def _combat_required_rune_cost_pure(player_data, combat_class, spell_spec, equipment_data=None):
    combined = {}
    if combat_class == "magic" and isinstance(spell_spec, Mapping):
        for rune_name, amount in _combat_effective_rune_cost_pure(
            player_data,
            spell_spec.get("rune_cost", {}),
            equipment_data,
        ).items():
            combined[rune_name] = _non_negative_int(combined.get(rune_name, 0), 0) + amount
    for rune_name, amount in _combat_supplemental_rune_cost_pure(player_data, equipment_data).items():
        combined[rune_name] = _non_negative_int(combined.get(rune_name, 0), 0) + amount
    return combined


def _combat_magic_rune_count(player_data, rune_name, target_id):
    loadout = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    loaded = _non_negative_int((loadout.get("runes", {}) or {}).get(rune_name, 0), 0)
    encounter = player_data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
    if active_encounter:
        return loaded
    inventory = player_data.get("inventory", {}) or {}
    banked = _non_negative_int(inventory.get(rune_name, 0), 0) if isinstance(inventory, Mapping) else 0
    return loaded + banked


def _combat_magic_missing_runes(player_data, spell_spec, target_id, equipment_data=None):
    rune_cost = spell_spec.get("rune_cost", {}) if isinstance(spell_spec, Mapping) else {}
    if not isinstance(rune_cost, Mapping) or not rune_cost:
        return tuple()
    missing = []
    covered_runes = combat_staff_covered_runes_pure(player_data, equipment_data)
    for rune_name, amount in rune_cost.items():
        if not isinstance(rune_name, str):
            continue
        if rune_name in covered_runes:
            continue
        required = _positive_int(amount, 0)
        if required > 0 and _combat_magic_rune_count(player_data, rune_name, target_id) < required:
            missing.append(f"{rune_name} x{required}")
    return tuple(missing)


def _combat_magic_locked_reasons(player_data, target_id, equipment_data=None):
    spell_id, spell_spec = _combat_selected_magic_spell(player_data)
    if not isinstance(spell_spec, Mapping) or not spell_spec:
        return ("source-backed combat spell",)
    required_level = _positive_int(spell_spec.get("required_magic_level", 1), 1)
    if _combat_effective_skill_level(player_data, "magic", 1) < required_level:
        return (f"Magic level {required_level}",)
    gate = spell_spec.get("quest_gate")
    if gate and not _magic_quest_gate_complete_pure(player_data, gate):
        return (str(gate).replace("_", " ").title(),)
    god_id = MAGE_ARENA_SPELL_TO_GOD.get(spell_id)
    if god_id:
        state = sanitize_mage_arena_state_pure(player_data.get("mage_arena"))
        if spell_id not in state["attuned_spells"]:
            return (
                f"Attune {MAGE_ARENA_GOD_DATA[god_id]['spell_name']} in the Mage Arena",
            )
    required_weapon = spell_spec.get("required_weapon")
    if required_weapon and (player_data.get("equipment", {}) or {}).get("weapon") != required_weapon:
        return (str(required_weapon),)
    if spell_spec.get("effect") == "undead_only":
        enemy_name = str(COMBAT_ENEMY_DATA.get(target_id, {}).get("display_name", target_id)).lower()
        if not any(token in enemy_name for token in ("skeleton", "zombie", "ghost", "shade", "undead")):
            return ("Undead target",)
    borrowed_spell_id = spell_spec.get("borrowed_spell_id")
    if borrowed_spell_id:
        from ..logic.livid_farm_logic import borrowed_power_locked_reasons_pure
        borrowed_reasons = borrowed_power_locked_reasons_pure(
            player_data,
            borrowed_spell_id,
        )
        if borrowed_reasons:
            return borrowed_reasons
    preset_reasons = combat_magic_preset_locked_reasons_pure(player_data)
    if preset_reasons:
        return preset_reasons
    missing = _combat_magic_missing_runes(player_data, spell_spec, target_id, equipment_data)
    if missing:
        return ("runes: " + ", ".join(missing),)
    return tuple()


def _combat_npc_xp_multiplier(enemy):
    stats = enemy.get("stats", {}) if isinstance(enemy, Mapping) else {}
    bonuses = enemy.get("bonuses", {}) if isinstance(enemy, Mapping) else {}
    if not isinstance(stats, Mapping):
        stats = {}
    if not isinstance(bonuses, Mapping):
        bonuses = {}
    average_level = floor(
        (
            _positive_int(stats.get("attack", 1), 1)
            + _positive_int(stats.get("strength", 1), 1)
            + _positive_int(stats.get("defence", 1), 1)
            + _positive_int(stats.get("hitpoints", 1), 1)
        )
        / 4.0
    )
    average_defence_bonus = floor(
        (
            _signed_int(bonuses.get("defence_stab", 0), 0)
            + _signed_int(bonuses.get("defence_slash", 0), 0)
            + _signed_int(bonuses.get("defence_crush", 0), 0)
        )
        / 3.0
    )
    attack_bonus = max(
        _signed_int(bonuses.get("attack_stab", 0), 0),
        _signed_int(bonuses.get("attack_slash", 0), 0),
        _signed_int(bonuses.get("attack_crush", 0), 0),
    )
    strength_bonus = _signed_int(bonuses.get("melee_strength", 0), 0)
    source_multiplier = _non_negative_float(enemy.get("xp_multiplier", 1.0), 1.0)
    return (
        1.0
        + floor(average_level * (average_defence_bonus + strength_bonus + attack_bonus) / 5120.0) / 40.0
    ) * source_multiplier


def _combat_apply_xp(xp_rewards, style_id, damage_lifepoints, npc_xp_multiplier):
    if damage_lifepoints <= 0:
        return
    combat_xp = float(damage_lifepoints) * 0.4 * npc_xp_multiplier
    constitution_xp = float(damage_lifepoints) * 0.133 * npc_xp_multiplier
    shared_xp = float(damage_lifepoints) * 0.133 * npc_xp_multiplier
    if style_id == "accurate":
        xp_rewards["attack_exp"] = xp_rewards.get("attack_exp", 0.0) + combat_xp
    elif style_id == "aggressive":
        xp_rewards["strength_exp"] = xp_rewards.get("strength_exp", 0.0) + combat_xp
    elif style_id == "defensive":
        xp_rewards["defense_exp"] = xp_rewards.get("defense_exp", 0.0) + combat_xp
    elif style_id == "controlled":
        for exp_key in ("attack_exp", "strength_exp", "defense_exp"):
            xp_rewards[exp_key] = xp_rewards.get(exp_key, 0.0) + shared_xp
    elif style_id in {"ranged_accurate", "ranged_rapid"}:
        xp_rewards["ranged_exp"] = xp_rewards.get("ranged_exp", 0.0) + combat_xp
    elif style_id == "ranged_longrange":
        split_xp = float(damage_lifepoints) * 0.2 * npc_xp_multiplier
        xp_rewards["ranged_exp"] = xp_rewards.get("ranged_exp", 0.0) + split_xp
        xp_rewards["defense_exp"] = xp_rewards.get("defense_exp", 0.0) + split_xp
    xp_rewards["constitution_exp"] = xp_rewards.get("constitution_exp", 0.0) + constitution_xp


def _combat_apply_magic_xp(xp_rewards, spell_spec, damage_lifepoints, npc_xp_multiplier):
    if not isinstance(spell_spec, Mapping):
        return
    base_xp = _non_negative_float(spell_spec.get("base_magic_xp", 0.0), 0.0)
    clamped_damage = max(0, _non_negative_int(damage_lifepoints, 0))
    magic_xp = base_xp + float(clamped_damage) * 0.2 * npc_xp_multiplier
    constitution_xp = float(clamped_damage) * 0.133 * npc_xp_multiplier
    if magic_xp > 0:
        xp_rewards["magic_exp"] = xp_rewards.get("magic_exp", 0.0) + magic_xp
    if constitution_xp > 0:
        xp_rewards["constitution_exp"] = xp_rewards.get("constitution_exp", 0.0) + constitution_xp


def _combat_slot_drop_quantity(slot, rng):
    quantity_choices = slot.get("quantity_choices")
    if isinstance(quantity_choices, (tuple, list)):
        choices = tuple(_positive_int(value, 0) for value in quantity_choices)
        choices = tuple(value for value in choices if value > 0)
        if choices:
            try:
                roll = float(rng())
            except (TypeError, ValueError):
                roll = 0.0
            index = int(max(0.0, min(roll, 0.999999999)) * len(choices))
            return choices[index]
    quantity_range = slot.get("quantity_range")
    if isinstance(quantity_range, (tuple, list)) and len(quantity_range) >= 2:
        low = _positive_int(quantity_range[0], 0)
        high = _positive_int(quantity_range[1], 0)
        if low > 0 and high >= low:
            try:
                roll = float(rng())
            except (TypeError, ValueError):
                roll = 0.0
            width = high - low + 1
            return low + int(max(0.0, min(roll, 0.999999999)) * width)
    return max(1, _positive_int(slot.get("quantity", 1), 1))


def combat_observed_drops_for_target_pure(player_data, target_id):
    if (
        not isinstance(player_data, Mapping)
        or not isinstance(target_id, str)
        or not target_id
    ):
        return {}
    observed = player_data.get("combat_observed_drops", {}) or {}
    if not isinstance(observed, Mapping):
        return {}
    return _sanitize_combat_observed_drops(
        {target_id: observed.get(target_id)}
    ).get(target_id, {})


def combat_observed_drop_item_names_pure(player_data, target_id):
    return tuple(combat_observed_drops_for_target_pure(player_data, target_id))


def combat_enemy_drop_item_names_pure(enemy):
    """Distinct item names an enemy can drop (guaranteed + all table slots,
    nested tables included), in encounter order. For the advanced loot UI."""
    names = []
    seen = set()

    def add(candidate):
        if isinstance(candidate, str) and candidate and candidate not in seen:
            seen.add(candidate)
            names.append(candidate)

    def walk_table(table):
        if not isinstance(table, Mapping):
            return
        for slot in table.get("slots", ()) or ():
            if not isinstance(slot, Mapping):
                continue
            add(slot.get("item"))
            walk_table(slot.get("table"))

    if not isinstance(enemy, Mapping):
        return tuple()
    drops = enemy.get("drops", {})
    if not isinstance(drops, Mapping):
        return tuple()
    for entry in drops.get("guaranteed", ()) or ():
        if isinstance(entry, (list, tuple)) and entry:
            add(entry[0])
    for table in drops.get("tables", ()) or ():
        walk_table(table)
    return tuple(names)


def _combat_drop_requirements_met(spec, player_data):
    requirements = spec.get("required_skill_levels", ()) if isinstance(spec, Mapping) else ()
    if not requirements:
        return True
    if not isinstance(player_data, Mapping):
        return False
    for requirement in requirements:
        if not isinstance(requirement, (tuple, list)) or len(requirement) < 2:
            return False
        skill_id = requirement[0]
        if (
            not isinstance(skill_id, str)
            or _combat_base_skill_level(player_data, skill_id, 1)
            < _positive_int(requirement[1], 1)
        ):
            return False
    return True


def _combat_roll_drop_table(table, rng, drops, player_data=None):
    if not isinstance(table, Mapping):
        return
    if not _combat_drop_requirements_met(table, player_data):
        return
    total = _positive_int(table.get("total", 0), 0)
    slots = tuple(row for row in table.get("slots", ()) or () if isinstance(row, Mapping))
    if total <= 0 or not slots:
        return
    try:
        roll = float(rng())
    except (TypeError, ValueError):
        roll = 0.0
    threshold = int(max(0.0, min(roll, 0.999999999)) * total)
    cursor = 0
    for slot in slots:
        cursor += _positive_int(slot.get("slots", 0), 0)
        if threshold >= cursor:
            continue
        nested_table = slot.get("table")
        if isinstance(nested_table, Mapping):
            _combat_roll_drop_table(nested_table, rng, drops, player_data)
            break
        item_name = slot.get("item")
        if isinstance(item_name, str):
            drops[item_name] = drops.get(item_name, 0) + _combat_slot_drop_quantity(slot, rng)
        break


def _combat_roll_drops(
    enemy, rng, player_data=None, *, include_clue_refusal=False
):
    drops = {}
    drop_spec = enemy.get("drops", {}) if isinstance(enemy, Mapping) else {}
    if not isinstance(drop_spec, Mapping):
        return (drops, "") if include_clue_refusal else drops
    for item_name, quantity in drop_spec.get("guaranteed", ()) or ():
        if isinstance(item_name, str):
            drops[item_name] = drops.get(item_name, 0) + max(1, _positive_int(quantity, 1))
    for table in drop_spec.get("tables", ()) or ():
        _combat_roll_drop_table(table, rng, drops, player_data)
    if not isinstance(player_data, Mapping):
        return (drops, "") if include_clue_refusal else drops
    # Both filters enforce a one-at-a-time ownership rule the drop table itself
    # knows nothing about: one Court summons, and one clue scroll across every
    # tier.
    filtered = filter_court_summons_outputs_pure(player_data, drops)
    clue_filtered = filter_clue_scroll_outputs_pure(player_data, filtered)
    clue_refusal = clue_refusal_reason_pure(player_data, filtered, clue_filtered)
    if include_clue_refusal:
        return clue_filtered, clue_refusal
    return clue_filtered


def _combat_apply_triple_charm_reward(data, drops):
    state = data.get("summoning_state", {}) or {}
    if (
        not isinstance(state, Mapping)
        or _non_negative_int(
            state.get("triple_charm_reviews_remaining", 0), 0
        ) <= 0
    ):
        return drops
    eligible = {
        "Gold charm",
        "Green charm",
        "Crimson charm",
        "Blue charm",
        "Obsidian charm",
        "Abyssal charm",
    }
    return {
        item_name: amount * 3 if item_name in eligible else amount
        for item_name, amount in drops.items()
    }


def apply_combat_finisher_pure(player_data, enemy_data=None, rng=None):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    rng = rng or (lambda: 0.0)
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data, enemy_data))
    target_id = data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    enemy = enemy_data.get(target_id) if isinstance(enemy_data, Mapping) else None
    locked_reasons = combat_target_locked_reasons_pure(
        data, target_id, enemy_data
    )
    if locked_reasons:
        return player_data, False, {
            "reason": "combat_locked",
            "target_id": target_id,
            "locked_reasons": locked_reasons,
        }
    finisher = _combat_finisher_spec(enemy)
    if finisher is None:
        return player_data, False, {"reason": "no_finisher", "target_id": target_id}
    state = combat_finisher_state_pure(data, target_id, enemy_data)
    if not state["ready"]:
        return player_data, False, {
            "reason": "finisher_not_ready",
            "target_id": target_id,
            "threshold_lifepoints": state["threshold_lifepoints"],
        }
    if not state["available"] or not _combat_consume_loaded_finisher(data, finisher):
        return player_data, False, {
            "reason": "finisher_item_missing",
            "target_id": target_id,
            "item": state["item"],
        }

    rolled_drops, clue_refusal_reason = _combat_roll_drops(
        enemy, rng, data, include_clue_refusal=True
    )
    kill_drops = _combat_apply_triple_charm_reward(data, rolled_drops)
    (
        data,
        kill_drops,
        passive_prayer_xp,
        _prayer_ticks,
        _prayer_effects,
    ) = resolve_prayer_kill_effects_pure(
        data,
        target_id,
        kill_drops,
        bool(data.get("combat_auto_prayer_training")),
    )
    xp_rewards = {}
    if passive_prayer_xp > 0:
        xp_rewards["prayer_exp"] = passive_prayer_xp
        data["prayer_exp"] = (
            float(data.get("prayer_exp", 0.0) or 0.0) + passive_prayer_xp
        )
    inventory = dict(data.get("inventory", {}) or {})
    for item_name, amount in kill_drops.items():
        inventory[item_name] = (
            _non_negative_int(inventory.get(item_name, 0), 0)
            + _non_negative_int(amount, 0)
        )
    data["inventory"] = inventory
    _record_combat_observed_drops_pure(data, target_id, kill_drops)
    kill_counts = dict(data.get("combat_kill_counts", {}) or {})
    kill_counts[target_id] = _non_negative_int(kill_counts.get(target_id, 0), 0) + 1
    data["combat_kill_counts"] = kill_counts
    data["combat_encounter"] = {}
    data["combat_action"] = "attack"
    result = {
        "reason": "combat_finisher",
        "target_id": target_id,
        "display_name": str(enemy.get("display_name", target_id)),
        "ticks": 0,
        "ticks_elapsed": 0,
        "player_damage": 0,
        "enemy_damage": 0,
        "enemy_lifepoints": 0,
        "player_lifepoints": _non_negative_int(
            data.get("combat_lifepoints", combat_max_lifepoints_pure(data)), 0
        ),
        "killed": True,
        "kills": 1,
        "died": False,
        "fled": False,
        "familiar_escape": False,
        "stop_reason": "",
        "food_used": tuple(),
        "potions_used": tuple(),
        "ammo_used": {},
        "runes_used": {},
        "status_damage": {},
        "status_applied": {},
        "status_expired": tuple(),
        "drops": kill_drops,
        "clue_refusal_reason": clue_refusal_reason,
        "xp_rewards": xp_rewards,
        "finisher_item": state["item"],
        "finisher_consumed": bool(finisher.get("consume", False)),
        "automatic_finisher": False,
    }
    data["combat_last_result"] = result
    return data, True, result


def _combat_consume_auto_food(data, current_lifepoints, max_lifepoints, rng):
    threshold_percent = _positive_int(data.get("combat_auto_eat_threshold_percent", 40), 40)
    threshold = max(1, int(max_lifepoints * threshold_percent / 100.0))
    if current_lifepoints > threshold or current_lifepoints >= max_lifepoints:
        return current_lifepoints, None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    food_loadout = dict(loadout.get("food", {}) or {})
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        food = COMBAT_FOOD_DATA.get(item_name)
        if not food or _positive_int(food_loadout.get(item_name, 0), 0) <= 0:
            continue
        food_loadout[item_name] = _positive_int(food_loadout.get(item_name, 0), 0) - 1
        if food_loadout[item_name] <= 0:
            food_loadout.pop(item_name, None)
        loadout["food"] = food_loadout
        data["combat_supply_loadout"] = loadout
        healed_by = _positive_int(food.get("heal_lifepoints", 0), 0)
        maximum = max_lifepoints + _positive_int(
            food.get("max_overheal_lifepoints", 0),
            0,
        )
        return min(maximum, current_lifepoints + healed_by), {
            "item": item_name,
            "healed_by": healed_by,
        }
    return current_lifepoints, None


def apply_combat_stat_delta_pure(data, skill_id, delta):
    """Reusable current-level mutation (shared by consumables and future
    potions). Reads the effective current level (base if unset), applies the
    signed delta, clamps at 1, and stores an absolute current level — dropping
    the entry when it lands back on base. Mutates and returns ``data``."""
    currents = dict(_sanitize_combat_current_levels(data.get("combat_current_levels")))
    base = _combat_base_skill_level(data, skill_id, currents.get(skill_id, 1))
    current = currents.get(skill_id, base)
    updated = max(1, current + _signed_int(delta, 0))
    if updated == base:
        currents.pop(skill_id, None)
    else:
        currents[skill_id] = updated
    data["combat_current_levels"] = currents
    return data
