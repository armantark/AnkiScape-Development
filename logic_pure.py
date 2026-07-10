# logic_pure.py - Pure logic functions for AnkiScape (no Anki dependencies)
from __future__ import annotations

from math import floor, sqrt
from typing import Iterable, Mapping, Optional

try:
    from .equipment_data import EQUIPMENT_BONUS_FIELDS, EquipmentBonuses
except ImportError:
    from equipment_data import EQUIPMENT_BONUS_FIELDS, EquipmentBonuses

try:
    from .inventory_pure import CARRIED_CAPACITY, carried_slots_used, clamp_carried_view_to_bank
except ImportError:
    from inventory_pure import CARRIED_CAPACITY, carried_slots_used, clamp_carried_view_to_bank

try:
    from .item_values import STACKABLE_ITEM_NAMES
except ImportError:
    try:
        from item_values import STACKABLE_ITEM_NAMES
    except ImportError:  # values not generated in this checkout
        STACKABLE_ITEM_NAMES = frozenset()

try:
    from .skill_registry import get_skill, implemented_skill_definitions
except ImportError:
    from skill_registry import get_skill, implemented_skill_definitions

try:
    from .potion_data import POTION_FAMILIES, potion_dose_name, potion_flask_name
except ImportError:
    from potion_data import POTION_FAMILIES, potion_dose_name, potion_flask_name

try:
    from .combat_data import (
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
except ImportError:
    from combat_data import (  # type: ignore
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

REVIEW_SUCCESS_MINIMUM = 0.20
REVIEW_SUCCESS_SCALE = 0.72
REVIEW_SUCCESS_CAP = 0.95
QUEST_COMBAT_CONFIG_VERSION = 1
QUEST_COMBAT_RESOLVER_ENABLED_KEY = "resolver_enabled"


def default_quest_combat_config_pure():
    return {"version": QUEST_COMBAT_CONFIG_VERSION, QUEST_COMBAT_RESOLVER_ENABLED_KEY: False}


def sanitize_quest_combat_config_pure(raw_config):
    config = default_quest_combat_config_pure()
    if isinstance(raw_config, Mapping):
        config[QUEST_COMBAT_RESOLVER_ENABLED_KEY] = bool(raw_config.get(QUEST_COMBAT_RESOLVER_ENABLED_KEY, False))
    return config


def quest_combat_resolver_enabled_pure(player_data):
    return bool(sanitize_quest_combat_config_pure(player_data.get("quest_combat_config")).get(QUEST_COMBAT_RESOLVER_ENABLED_KEY))

def get_exp_to_next_level(player_data, EXP_TABLE):
    """Return exp needed to reach the next level for Mining.
    Supports EXP_TABLE as list or dict. Uses mining_exp, falls back to legacy total_exp.
    When at or beyond max level or threshold missing, returns 0.
    """
    current_level = player_data.get("mining_level", player_data.get("level", 1))
    if current_level >= 99:
        return 0
    # Determine threshold for next level from EXP_TABLE
    if isinstance(EXP_TABLE, dict):
        threshold = EXP_TABLE.get(current_level)
    else:
        try:
            threshold = EXP_TABLE[current_level]
        except (IndexError, TypeError):
            threshold = None
    if threshold is None:
        return 0
    skill_exp = player_data.get("mining_exp", player_data.get("total_exp", 0))
    needed = threshold - skill_exp
    return needed if needed > 0 else 0

def calculate_new_level(skill_exp, current_level, EXP_TABLE):
    """
    Calculate the new level for a skill given experience, current level, and EXP_TABLE.
    Supports EXP_TABLE as a dict (level -> threshold) or a list where index (level-1) stores threshold.
    Returns the new level (int).
    """
    new_level = current_level
    while new_level < 99:
        # Determine threshold to reach next level (new_level+1)
        if isinstance(EXP_TABLE, dict):
            threshold = EXP_TABLE.get(new_level + 1)
        else:
            try:
                # In list form, index equals current level (new_level) for threshold to reach next level
                threshold = EXP_TABLE[new_level]
            except (IndexError, TypeError):
                threshold = None

        if threshold is None or skill_exp < threshold:
            break
        new_level += 1
    return new_level

def get_newly_completed_achievements(player_data, ACHIEVEMENTS):
    """
    Returns a list of achievement names that are newly completed (not yet in player_data["completed_achievements"])
    """
    completed = set(player_data.get("completed_achievements", []))
    newly_completed = []
    for name, data in ACHIEVEMENTS.items():
        if name not in completed and data["condition"](player_data):
            newly_completed.append(name)
    return newly_completed

def calculate_probability_with_level(player_level, base_probability, level_bonus_factor, source_probability, cap=0.95):
    """
    Compute success probability given a player's level and base probabilities.
    Probability = min(base_probability + player_level * level_bonus_factor, cap) * source_probability
    """
    level_bonus = player_level * level_bonus_factor
    return min(base_probability + level_bonus, cap) * source_probability

def pick_gem(gem_data, r):
    """
    Deterministically pick a gem given gem_data and a random draw r in [0, 1).
    gem_data: { name: { "probability": float }, ... }
    Returns the gem name, or None if r exceeds the total probability mass.
    """
    cumulative = 0.0
    for gem, data in gem_data.items():
        cumulative += data.get("probability", 0.0)
        if r < cumulative:
            return gem
    return None


def pick_weighted_item_pure(weighted_items, r, total_weight=None):
    """Pick an item from source-style weighted slots using a [0, 1) roll."""
    if total_weight is None:
        total_weight = sum(_positive_int(item.get("weight", 0), 0) for item in weighted_items)
    if total_weight <= 0:
        return None
    threshold = max(0.0, min(float(r), 0.999999999)) * total_weight
    cumulative = 0
    for item in weighted_items:
        cumulative += _positive_int(item.get("weight", 0), 0)
        if threshold < cumulative:
            return item.get("item")
    last = weighted_items[-1] if weighted_items else {}
    return last.get("item")

def _requirements_from_spec(spec):
    return spec.get("requirements") or spec.get("ore_required", {})


def can_smelt_any_bar_pure(inventory, smithing_level, bar_data):
    """
    Return True if at least one bar can be smelted given the player's smithing_level and inventory.
    bar_data format: { bar_name: {"level": int, "ore_required": {ore: amount}} }
    """
    for _, data in bar_data.items():
        if data.get("station") not in (None, "furnace"):
            continue
        if smithing_level >= data.get("level", 0):
            if all(inventory.get(material, 0) >= amount for material, amount in _requirements_from_spec(data).items()):
                return True
    return False


def has_smithing_materials_pure(target, inventory, smithing_data):
    """Return True when inventory satisfies a Smithing recipe's material needs."""
    spec = smithing_data.get(target)
    if not spec:
        return False
    for material, amount in _requirements_from_spec(spec).items():
        if inventory.get(material, 0) < amount:
            return False
    return True


def can_smith_item_pure(smithing_level, inventory, target, smithing_data):
    """Return True if level and materials allow one Smithing recipe action."""
    spec = smithing_data.get(target)
    if not spec:
        return False
    if smithing_level < spec.get("level", 1):
        return False
    return has_smithing_materials_pure(target, inventory, smithing_data)


def smithing_target_locked_reasons_pure(player_data, target, smithing_data, quest_unlock_rules=()):
    spec = smithing_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    smithing_level = _positive_int(player_data.get("smithing_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if smithing_level < required_level:
        reasons.append(f"level {required_level}")
    if not has_smithing_materials_pure(target, player_data.get("inventory", {}) or {}, smithing_data):
        reasons.append("materials")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "smithing",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def can_smith_any_pure(inventory, smithing_level, smithing_data):
    """Return True if any smelt or forge recipe can run right now."""
    return any(
        can_smith_item_pure(smithing_level, inventory, target, smithing_data)
        for target in smithing_data
    )


def sanitize_review_action_multiplier(value, default=1, minimum=1, maximum=10):
    """Return the integer number of game action ticks one review can run."""
    if isinstance(value, bool):
        return default
    try:
        multiplier = float(value)
    except (TypeError, ValueError):
        return default
    if multiplier != multiplier:
        return default
    if multiplier < minimum:
        return minimum
    if multiplier > maximum:
        return maximum
    return int(multiplier)


def sanitize_xp_multiplier(value, default=1.0, minimum=0.0, maximum=100.0):
    """Compatibility wrapper for old configs/tests; review rewards no longer use it."""
    if isinstance(value, bool):
        return default
    try:
        multiplier = float(value)
    except (TypeError, ValueError):
        return default
    if multiplier != multiplier:
        return default
    if multiplier < minimum:
        return minimum
    if multiplier > maximum:
        return maximum
    return multiplier


def create_soft_clay_pure(inventory):
    """
    Deduct 1 "Clay" and add 1 "Soft clay" if possible.
    Returns (new_inventory, success: bool). Does not mutate input.
    """
    current_clay = inventory.get("Clay", 0)
    if current_clay > 0:
        new_inv = dict(inventory)
        new_inv["Clay"] = current_clay - 1
        new_inv["Soft clay"] = new_inv.get("Soft clay", 0) + 1
        return new_inv, True
    return inventory, False


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


def normalize_review_success_probability_pure(
    source_chance,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Adapt source tick odds to one AnkiScape review-action roll."""
    try:
        source = float(source_chance)
    except (TypeError, ValueError):
        source = 0.0
    source = max(0.0, min(source, 1.0))
    return max(0.0, min(float(minimum) + (sqrt(source) * float(scale)), float(cap)))


def default_action_telemetry_pure():
    return {"version": 1, "actions": {}}


def sanitize_action_telemetry_pure(telemetry):
    sanitized = default_action_telemetry_pure()
    if not isinstance(telemetry, Mapping):
        return sanitized
    raw_actions = telemetry.get("actions", {})
    if not isinstance(raw_actions, Mapping):
        return sanitized
    actions = {}
    for key, raw_record in raw_actions.items():
        if not isinstance(key, str) or not isinstance(raw_record, Mapping):
            continue
        record = dict(raw_record)
        record.setdefault("skill_id", key.split(":", 1)[0])
        record.setdefault("action_id", key.split(":", 1)[1] if ":" in key else key)
        record["attempts"] = _non_negative_int(record.get("attempts", 0), 0)
        record["successes"] = _non_negative_int(record.get("successes", 0), 0)
        record["failures"] = _non_negative_int(record.get("failures", 0), 0)
        record["expected_successes"] = _non_negative_float(record.get("expected_successes", 0.0), 0.0)
        record["current_dry_streak"] = _non_negative_int(record.get("current_dry_streak", 0), 0)
        record["longest_dry_streak"] = _non_negative_int(record.get("longest_dry_streak", 0), 0)
        if not isinstance(record.get("outputs"), Mapping):
            record["outputs"] = {}
        if not isinstance(record.get("failure_kinds"), Mapping):
            record["failure_kinds"] = {}
        actions[key] = record
    sanitized["actions"] = actions
    return sanitized


def action_telemetry_key_pure(skill_id, action_id):
    return f"{str(skill_id)}:{str(action_id)}"


def record_action_telemetry_pure(
    player_data,
    skill_id,
    action_id,
    success,
    *,
    expected_success_chance=None,
    output_item=None,
    output_qty=1,
    output_items=None,
    failure_kind=None,
):
    """Record one started review action and return its action telemetry row."""
    telemetry = sanitize_action_telemetry_pure(player_data.get("action_telemetry"))
    player_data["action_telemetry"] = telemetry
    actions = telemetry.setdefault("actions", {})
    key = action_telemetry_key_pure(skill_id, action_id)
    record = actions.setdefault(
        key,
        {
            "skill_id": str(skill_id),
            "action_id": str(action_id),
            "attempts": 0,
            "successes": 0,
            "failures": 0,
            "expected_successes": 0.0,
            "current_dry_streak": 0,
            "longest_dry_streak": 0,
            "outputs": {},
            "failure_kinds": {},
        },
    )
    record["attempts"] = _non_negative_int(record.get("attempts", 0), 0) + 1
    is_success = bool(success)
    record["last_success"] = is_success

    if expected_success_chance is not None:
        try:
            expected = float(expected_success_chance)
        except (TypeError, ValueError):
            expected = 0.0
        expected = max(0.0, min(expected, 1.0))
        record["expected_successes"] = _non_negative_float(record.get("expected_successes", 0.0), 0.0) + expected
        record["last_expected_success_chance"] = expected

    if is_success:
        record["successes"] = _non_negative_int(record.get("successes", 0), 0) + 1
        record["current_dry_streak"] = 0
        record.pop("last_failure_kind", None)
    else:
        record["failures"] = _non_negative_int(record.get("failures", 0), 0) + 1
        dry_streak = _non_negative_int(record.get("current_dry_streak", 0), 0) + 1
        record["current_dry_streak"] = dry_streak
        record["longest_dry_streak"] = max(_non_negative_int(record.get("longest_dry_streak", 0), 0), dry_streak)
        kind = str(failure_kind or "dry")
        failure_kinds = dict(record.get("failure_kinds", {}) or {})
        failure_kinds[kind] = _non_negative_int(failure_kinds.get(kind, 0), 0) + 1
        record["failure_kinds"] = failure_kinds
        record["last_failure_kind"] = kind

    outputs = dict(record.get("outputs", {}) or {})
    if isinstance(output_items, Mapping):
        for item_name, amount in output_items.items():
            if not item_name:
                continue
            qty = _positive_int(amount, 1)
            outputs[str(item_name)] = _non_negative_int(outputs.get(str(item_name), 0), 0) + qty
            record["last_output_item"] = str(item_name)
    elif output_item:
        qty = _positive_int(output_qty, 1)
        outputs[str(output_item)] = _non_negative_int(outputs.get(str(output_item), 0), 0) + qty
        record["last_output_item"] = str(output_item)
    record["outputs"] = outputs
    return record


def summarize_action_telemetry_pure(player_data):
    telemetry = sanitize_action_telemetry_pure(player_data.get("action_telemetry"))
    rows = []
    for key, record in sorted(telemetry.get("actions", {}).items()):
        attempts = _non_negative_int(record.get("attempts", 0), 0)
        successes = _non_negative_int(record.get("successes", 0), 0)
        expected_successes = _non_negative_float(record.get("expected_successes", 0.0), 0.0)
        rows.append(
            {
                "key": key,
                "skill_id": record.get("skill_id", key.split(":", 1)[0]),
                "action_id": record.get("action_id", key.split(":", 1)[1] if ":" in key else key),
                "attempts": attempts,
                "successes": successes,
                "failures": _non_negative_int(record.get("failures", 0), 0),
                "observed_success_rate": (successes / attempts) if attempts else 0.0,
                "expected_success_rate": (expected_successes / attempts) if attempts else 0.0,
                "current_dry_streak": _non_negative_int(record.get("current_dry_streak", 0), 0),
                "longest_dry_streak": _non_negative_int(record.get("longest_dry_streak", 0), 0),
                "outputs": dict(record.get("outputs", {}) or {}),
                "failure_kinds": dict(record.get("failure_kinds", {}) or {}),
            }
        )
    return tuple(rows)


def _max_batches_for_requirements(requirements, inventory, batch_size):
    if not requirements:
        return batch_size
    possible = batch_size
    for material, amount in requirements.items():
        per_batch = _positive_int(amount)
        possible = min(possible, inventory.get(material, 0) // per_batch)
    return possible

def has_crafting_materials_pure(item, inventory, crafting_data):
    """Return True if inventory satisfies crafting requirements for the given item.
    Unknown items return False.
    """
    spec = crafting_data.get(item)
    if not spec:
        return False
    requirements = spec.get("requirements", {})
    for material, amount in requirements.items():
        if inventory.get(material, 0) < amount:
            return False
    return True

def apply_crafting_pure(item, inventory, crafting_data):
    """If inventory meets requirements, deduct inputs and return (new_inventory, exp, success).
    Does not mutate input inventory. Unknown items return (inventory, 0, False).
    """
    spec = crafting_data.get(item)
    if not spec or not has_crafting_materials_pure(item, inventory, crafting_data):
        return inventory, 0, False
    requirements = spec.get("requirements", {})
    # Crafting is XP-bearing; batching is reserved for no-XP Utility/Activities.
    batch_count = _max_batches_for_requirements(requirements, inventory, 1)
    if batch_count <= 0:
        return inventory, 0, False
    new_inv = dict(inventory)
    for material, amount in requirements.items():
        new_inv[material] = new_inv.get(material, 0) - (_positive_int(amount) * batch_count)
    output_item = spec.get("output_item", item)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + (output_qty * batch_count)
    # Source-backed byproducts (e.g. molten glass returns the emptied bucket).
    for byproduct, amount in (spec.get("byproducts") or {}).items():
        new_inv[byproduct] = new_inv.get(byproduct, 0) + (_positive_int(amount) * batch_count)
    exp = spec.get("exp", 0) * batch_count
    return new_inv, exp, True


def can_perform_utility_activity_pure(inventory, activity_key, utility_activity_data):
    """Return True if a no-XP Utility/Activity can run for at least one batch."""
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return False
    openable_items = spec.get("openable_items")
    if openable_items:
        return any(inventory.get(item_name, 0) > 0 for item_name in openable_items)
    requirements = spec.get("requirements", {})
    batch_size = _positive_int(spec.get("batch_size", 1))
    return _max_batches_for_requirements(requirements, inventory, batch_size) > 0


def utility_activity_locked_reasons_pure(player_data, activity_key, utility_activity_data, quest_unlock_rules=()):
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return ("unknown activity",)
    reasons = []
    inventory = player_data.get("inventory", {}) or {}
    if not can_perform_utility_activity_pure(inventory, activity_key, utility_activity_data):
        reasons.append("materials")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "utility",
            activity_key,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def _utility_outputs_from_spec(spec):
    outputs = spec.get("outputs")
    if isinstance(outputs, Mapping):
        return {
            str(item): _positive_int(amount, 1)
            for item, amount in outputs.items()
            if isinstance(item, str) and item
        }
    output_item = spec.get("output_item")
    if isinstance(output_item, str) and output_item:
        return {output_item: _positive_int(spec.get("output_qty", 1), 1)}
    return {}


def apply_utility_activity_pure(activity_key, inventory, utility_activity_data):
    """Apply a no-XP Utility/Activity and return (inventory, exp, success, processed)."""
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return inventory, 0, False, 0
    requirements = spec.get("requirements", {})
    batch_size = _positive_int(spec.get("batch_size", 1))
    batch_count = _max_batches_for_requirements(requirements, inventory, batch_size)
    if batch_count <= 0:
        return inventory, 0, False, 0

    new_inv = dict(inventory)
    for material, amount in requirements.items():
        new_inv[material] = new_inv.get(material, 0) - (_positive_int(amount) * batch_count)
    outputs = _utility_outputs_from_spec(spec)
    if not outputs:
        outputs = {activity_key: 1}
    for output_item, output_qty in outputs.items():
        new_inv[output_item] = new_inv.get(output_item, 0) + (output_qty * batch_count)
    return new_inv, 0, True, batch_count


# --- Stronghold of Security (one-time landmark) ---------------------------
# The Stronghold has four levels, one per horseman of the apocalypse. The
# player walks one level per review; finishing the last level unlocks a choice
# between two stat-identical boots plus a 10k-coin cash bag (2011Scape reward).
STRONGHOLD_STEP_NAMES = (
    "Vault of War",
    "Catacomb of Famine",
    "Pit of Pestilence",
    "Sepulchre of Death",
)
STRONGHOLD_TOTAL_STEPS = len(STRONGHOLD_STEP_NAMES)
STRONGHOLD_REWARD_COINS = 10000
STRONGHOLD_BOOT_CHOICES = ("Fancy boots", "Fighting boots")


def default_stronghold_state_pure():
    """Fresh Stronghold progress: not started, no reward taken."""
    return {"step": 0, "completed": False, "boots_choice": None}


def sanitize_stronghold_state_pure(raw):
    """Coerce a loaded Stronghold blob back into shape, clamping the step and
    keeping ``completed`` consistent with it."""
    state = default_stronghold_state_pure()
    if isinstance(raw, Mapping):
        try:
            step = int(raw.get("step", 0))
        except (TypeError, ValueError):
            step = 0
        state["step"] = max(0, min(step, STRONGHOLD_TOTAL_STEPS))
        state["completed"] = bool(raw.get("completed")) or state["step"] >= STRONGHOLD_TOTAL_STEPS
        choice = raw.get("boots_choice")
        state["boots_choice"] = choice if choice in STRONGHOLD_BOOT_CHOICES else None
    return state


def apply_stronghold_step_pure(player_data):
    """Advance the Stronghold of Security by one level (one review = one step).

    Steps run 0 -> STRONGHOLD_TOTAL_STEPS with no XP or items earned en route;
    reaching the final level flips ``completed``. A no-op once completed.
    Returns {"advanced", "step", "completed", "just_completed"}.
    """
    state = player_data.setdefault("stronghold_of_security", default_stronghold_state_pure())
    if state.get("completed"):
        return {
            "advanced": False,
            "step": int(state.get("step", STRONGHOLD_TOTAL_STEPS)),
            "completed": True,
            "just_completed": False,
        }
    step = min(int(state.get("step", 0)) + 1, STRONGHOLD_TOTAL_STEPS)
    just_completed = step >= STRONGHOLD_TOTAL_STEPS
    state["step"] = step
    state["completed"] = just_completed
    return {"advanced": True, "step": step, "completed": just_completed, "just_completed": just_completed}


def grant_stronghold_reward_pure(player_data, boots_choice):
    """One-time completion reward: STRONGHOLD_REWARD_COINS coins plus the chosen
    boots. Guarded on an unset ``boots_choice`` so it can fire only once.
    Returns True when the reward was granted.
    """
    if boots_choice not in STRONGHOLD_BOOT_CHOICES:
        return False
    state = player_data.setdefault("stronghold_of_security", default_stronghold_state_pure())
    if not state.get("completed") or state.get("boots_choice") is not None:
        return False
    inventory = player_data.setdefault("inventory", {})
    inventory["Coins"] = inventory.get("Coins", 0) + STRONGHOLD_REWARD_COINS
    inventory[boots_choice] = inventory.get(boots_choice, 0) + 1
    state["boots_choice"] = boots_choice
    return True


def apply_smelt_pure(bar_name, inventory, bar_data):
    """
    Attempt to smelt a specific bar. Returns (new_inventory, exp, success).
    Does not mutate input inventory. Only checks materials; level checks should be handled by caller.
    bar_data format: { bar_name: {"exp": float, "ore_required": {ore: amount}} }
    """
    spec = bar_data.get(bar_name)
    if not spec:
        return inventory, 0, False
    requirements = _requirements_from_spec(spec)
    # Check materials
    if not all(inventory.get(ore, 0) >= amount for ore, amount in requirements.items()):
        return inventory, 0, False
    # Deduct and add bar
    new_inv = dict(inventory)
    for ore, amount in requirements.items():
        new_inv[ore] = new_inv.get(ore, 0) - amount
    output_item = spec.get("output_item", bar_name)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True


def apply_smithing_pure(target, inventory, smithing_data):
    """Apply one source-backed Smithing recipe, smelt or forge.

    Smithing actions are XP-bearing, so this intentionally does not honor a
    recipe-level batch size. Review pacing runs multiple normal actions when the
    global actions-per-review setting is greater than one.
    """
    spec = smithing_data.get(target)
    if not spec or not has_smithing_materials_pure(target, inventory, smithing_data):
        return inventory, 0, False

    new_inv = dict(inventory)
    for material, amount in _requirements_from_spec(spec).items():
        new_inv[material] = new_inv.get(material, 0) - amount

    output_item = spec.get("output_item", target)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True


RING_OF_FORGING_ITEM = "Ring of forging"
RING_OF_FORGING_MAX_CHARGES = 140


def _equipment_has_ring_of_forging_pure(player_data):
    return (player_data.get("equipment", {}) or {}).get("ring") == RING_OF_FORGING_ITEM


def ring_of_forging_charges_pure(player_data):
    if not _equipment_has_ring_of_forging_pure(player_data):
        return 0
    charges = (player_data.get("item_charges", {}) or {}).get(RING_OF_FORGING_ITEM)
    if charges is None:
        return RING_OF_FORGING_MAX_CHARGES
    return max(0, _positive_int(charges, 0))


def has_ring_of_forging_pure(player_data):
    return ring_of_forging_charges_pure(player_data) > 0


def consume_ring_of_forging_charge_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    if not _equipment_has_ring_of_forging_pure(data):
        return data
    remaining = ring_of_forging_charges_pure(data) - 1
    item_charges = data.setdefault("item_charges", {})
    if remaining > 0:
        item_charges[RING_OF_FORGING_ITEM] = remaining
    else:
        item_charges.pop(RING_OF_FORGING_ITEM, None)
        data.setdefault("equipment", {}).pop("ring", None)
    return data


def calculate_iron_smelting_success_probability_pure(smithing_level, has_ring_of_forging=False):
    if has_ring_of_forging:
        return 1.0
    level = max(15, min(_positive_int(smithing_level, 15), 45))
    # SmeltingAction.rollIronBar: level.coerceAtMost(45).interpolate(50, 80,
    # 15, 45, 100) -> success iff nextInt(100) <= interp, i.e. probability
    # (interp + 1)/100 — the source curve is 51%..81%, not 50%..80%.
    interp = 50 + ((80 - 50) * (level - 15) // (45 - 15))
    return min(1.0, (interp + 1) / 100.0)


def smithing_success_probability_pure(target, spec, smithing_level, has_ring_of_forging=False):
    if target == "smelt_iron_bar" and (spec or {}).get("station") == "furnace":
        return calculate_iron_smelting_success_probability_pure(smithing_level, has_ring_of_forging)
    return 1.0


def apply_smithing_action_pure(
    target,
    inventory,
    smithing_data,
    smithing_level,
    r_action=0.0,
    has_ring_of_forging=False,
):
    """Apply one source-shaped Smithing action.

    Returns (inventory, base_exp, processed, output_item, failed). Iron smelting
    failure consumes ore and processes the action, but gives no bar or XP.
    """
    spec = smithing_data.get(target)
    if not spec or not has_smithing_materials_pure(target, inventory, smithing_data):
        return inventory, 0, False, None, False

    new_inv = dict(inventory)
    for material, amount in _requirements_from_spec(spec).items():
        new_inv[material] = new_inv.get(material, 0) - amount

    success_probability = smithing_success_probability_pure(
        target,
        spec,
        smithing_level,
        has_ring_of_forging=has_ring_of_forging,
    )
    try:
        roll = float(r_action)
    except (TypeError, ValueError):
        roll = 1.0
    if success_probability < 1.0 and roll >= success_probability:
        return new_inv, 0, True, None, True

    output_item = spec.get("output_item", target)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True, output_item, False

def apply_woodcutting_pure(tree_name, inventory, tree_data, r_action, success_probability):
    """
    Attempt a woodcutting action. Returns (new_inventory, exp_gained, success).
    Does not mutate input inventory. The caller provides a random draw and success probability.
    """
    success = r_action < success_probability
    if not success:
        return inventory, 0, False
    new_inv = dict(inventory)
    output_item = tree_data[tree_name].get("output_item", tree_name)
    if output_item:
        new_inv[output_item] = new_inv.get(output_item, 0) + 1
    exp = tree_data[tree_name].get("exp", 0)
    return new_inv, exp, True


def _toolbelt_ids(toolbelt, skill_key):
    if not isinstance(toolbelt, Mapping):
        return set()
    raw = toolbelt.get(skill_key, ())
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, Iterable):
        return {item for item in raw if isinstance(item, str)}
    return set()


def best_woodcutting_axe_pure(woodcutting_level, inventory, toolbelt, axe_data):
    """Return the best usable axe spec, considering bound tools and owned items."""
    bound_ids = _toolbelt_ids(toolbelt, "woodcutting")
    best = None
    for axe_id, spec in axe_data.items():
        if spec.get("status", "implemented") != "implemented":
            continue
        display_name = spec.get("display_name", axe_id)
        owned = axe_id in bound_ids or inventory.get(display_name, 0) > 0
        if not owned or woodcutting_level < spec.get("level", 1):
            continue
        if best is None or spec.get("ratio", 0) >= best.get("ratio", 0):
            best = spec
    return best


def best_mining_pickaxe_pure(mining_level, inventory, toolbelt, pickaxe_data):
    """Return the best usable pickaxe spec, considering bound tools and owned items."""
    bound_ids = _toolbelt_ids(toolbelt, "mining")
    best = None
    best_power = 0.0
    for pickaxe_id, spec in pickaxe_data.items():
        if spec.get("status", "implemented") != "implemented":
            continue
        display_name = spec.get("display_name", pickaxe_id)
        owned = pickaxe_id in bound_ids or inventory.get(display_name, 0) > 0
        if not owned or mining_level < spec.get("level", 1):
            continue
        power = float(spec.get("ratio", 0))
        if "dragon" in str(spec.get("display_name", "")).lower():
            power *= 1.12
        if best is None or power >= best_power:
            best = spec
            best_power = power
    return best


def _equipment_value(spec: object, key: str, default: object = None) -> object:
    if isinstance(spec, Mapping):
        return spec.get(key, default)
    return getattr(spec, key, default)


def _equipment_bonuses(spec: object) -> object:
    bonuses = _equipment_value(spec, "bonuses", None)
    return bonuses if bonuses is not None else EquipmentBonuses()


def _equipment_bonus_value(bonuses: object, key: str) -> int:
    if isinstance(bonuses, Mapping):
        value = bonuses.get(key, 0)
    else:
        value = getattr(bonuses, key, 0)
    if isinstance(value, bool):
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _normalized_equipment_slot(slot: object) -> str:
    if not isinstance(slot, str):
        return ""
    return {"amulet": "neck", "chest": "body"}.get(slot, slot)


def _combat_level_key(combat_skill: object) -> Optional[str]:
    if not isinstance(combat_skill, str) or not combat_skill:
        return None
    return f"{combat_skill}_level"


def _equipment_skill_requirements(spec: object) -> tuple[tuple[str, int, str], ...]:
    raw_requirements = _equipment_value(spec, "skill_requirements", ())
    parsed: list[tuple[str, int, str]] = []
    if isinstance(raw_requirements, Mapping):
        requirement_iterable = raw_requirements.items()
    elif isinstance(raw_requirements, (tuple, list)):
        requirement_iterable = raw_requirements
    else:
        requirement_iterable = ()
    for requirement in requirement_iterable:
        if isinstance(requirement, Mapping):
            combat_skill = requirement.get("skill")
            raw_level = requirement.get("level")
        elif isinstance(requirement, (tuple, list)) and len(requirement) >= 2:
            combat_skill = requirement[0]
            raw_level = requirement[1]
        else:
            continue
        level_key = _combat_level_key(combat_skill)
        required_level = _positive_int(raw_level, 1)
        if isinstance(combat_skill, str) and level_key is not None and required_level > 1:
            parsed.append((combat_skill, required_level, level_key))
    if parsed:
        return tuple(parsed)

    combat_skill = _equipment_value(spec, "combat_skill", None)
    level_key = _combat_level_key(combat_skill)
    required_level = _positive_int(_equipment_value(spec, "required_level", 1), 1)
    if isinstance(combat_skill, str) and level_key is not None and required_level > 1:
        return ((combat_skill, required_level, level_key),)
    return ()


def _combat_skill_label(combat_skill: object) -> str:
    labels = {
        "attack": "Attack",
        "defense": "Defense",
        "ranged": "Ranged",
        "strength": "Strength",
        "magic": "Magic",
        "prayer": "Prayer",
        "constitution": "Constitution",
    }
    if isinstance(combat_skill, str):
        return labels.get(combat_skill, combat_skill.replace("_", " ").title())
    return "Combat"


def equipment_bonus_state_pure(equipment: Mapping[str, str], bonus_item_data: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    """Summarize Mining bonuses from explicitly worn equipment slots."""
    has_glory = False
    varrock_tier = 0
    equipped_by_slot = {
        _normalized_equipment_slot(slot): item_name
        for slot, item_name in equipment.items()
        if isinstance(slot, str) and isinstance(item_name, str)
    }
    for spec in bonus_item_data.values():
        display_name = spec.get("display_name")
        slot = _normalized_equipment_slot(spec.get("equipment_slot"))
        if not isinstance(display_name, str) or equipped_by_slot.get(slot) != display_name:
            continue
        if spec.get("equipment_type") == "gem_chance":
            has_glory = True
        if spec.get("equipment_type") == "extra_ore":
            varrock_tier = max(varrock_tier, _positive_int(spec.get("tier", 0), 0))
    return {"has_glory": has_glory, "varrock_armour_tier": varrock_tier}


def can_equip_item_pure(
    item_name: str,
    equipment_data: Mapping[str, object],
    player_data: Mapping[str, object],
) -> tuple[bool, str]:
    spec = equipment_data.get(item_name)
    if spec is None:
        return False, "Item is not equippable"
    for combat_skill, required_level, level_key in _equipment_skill_requirements(spec):
        current_level = _positive_int(player_data.get(level_key, 1), 1)
        if current_level < required_level:
            return False, f"Requires level {required_level} {_combat_skill_label(combat_skill)}"
    return True, ""


def equip_item_pure(
    item_name: str,
    inventory: Mapping[str, int],
    equipment: Mapping[str, str],
    equipment_data: Mapping[str, object],
) -> tuple[dict[str, int], dict[str, str], bool]:
    spec = equipment_data.get(item_name)
    if spec is None:
        return dict(inventory), dict(equipment), False
    slot = _equipment_value(spec, "slot", None)
    if not isinstance(slot, str) or not slot:
        return dict(inventory), dict(equipment), False
    owned_qty = inventory.get(item_name, 0)
    if owned_qty <= 0:
        return dict(inventory), dict(equipment), False

    new_inventory = dict(inventory)
    new_equipment = {
        equipped_slot: equipped_item
        for equipped_slot, equipped_item in equipment.items()
        if isinstance(equipped_slot, str) and isinstance(equipped_item, str)
    }
    new_inventory[item_name] = owned_qty - 1

    displaced = new_equipment.get(slot)
    if displaced:
        new_inventory[displaced] = new_inventory.get(displaced, 0) + 1
    new_equipment[slot] = item_name

    two_handed = bool(_equipment_value(spec, "two_handed", False))
    if slot == "weapon" and two_handed:
        shield_item = new_equipment.pop("shield", None)
        if shield_item:
            new_inventory[shield_item] = new_inventory.get(shield_item, 0) + 1
    elif slot == "shield":
        weapon_item = new_equipment.get("weapon")
        if weapon_item:
            weapon_spec = equipment_data.get(weapon_item)
            if bool(_equipment_value(weapon_spec, "two_handed", False)):
                removed_weapon = new_equipment.pop("weapon")
                new_inventory[removed_weapon] = new_inventory.get(removed_weapon, 0) + 1

    return new_inventory, new_equipment, True


def unequip_item_pure(
    slot: str,
    inventory: Mapping[str, int],
    equipment: Mapping[str, str],
) -> tuple[dict[str, int], dict[str, str], bool]:
    if slot not in equipment or not isinstance(equipment.get(slot), str):
        return dict(inventory), dict(equipment), False
    new_inventory = dict(inventory)
    new_equipment = {
        equipped_slot: equipped_item
        for equipped_slot, equipped_item in equipment.items()
        if isinstance(equipped_slot, str) and isinstance(equipped_item, str)
    }
    item_name = new_equipment.pop(slot)
    new_inventory[item_name] = new_inventory.get(item_name, 0) + 1
    return new_inventory, new_equipment, True


def equipment_stat_totals_pure(
    equipment: Mapping[str, str],
    equipment_data: Mapping[str, object],
) -> EquipmentBonuses:
    totals = {field: 0 for field in EQUIPMENT_BONUS_FIELDS}
    for item_name in equipment.values():
        if not isinstance(item_name, str):
            continue
        spec = equipment_data.get(item_name)
        if spec is None:
            continue
        bonuses = _equipment_bonuses(spec)
        for field in EQUIPMENT_BONUS_FIELDS:
            totals[field] += _equipment_bonus_value(bonuses, field)
    return EquipmentBonuses(**totals)


_DEFAULT_COMBAT_AUTO_EAT_FOOD = (
    "Shark",
    "Swordfish",
    "Lobster",
    "Tuna",
    "Salmon",
    "Trout",
    "Cooked meat",
    "Cooked chicken",
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
COMBAT_BANK_RUN_REVIEWS = 2

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


def _combat_coerce_pack_mode(mode):
    return mode if mode in _COMBAT_VALID_PACK_MODES else _COMBAT_DEFAULT_PACK_MODE


def _combat_food_slot_cap(data):
    mode = _combat_coerce_pack_mode(data.get("combat_pack_mode", _COMBAT_DEFAULT_PACK_MODE))
    return min(COMBAT_FOOD_LOADOUT_CAPACITY, _COMBAT_FOOD_CAP_BY_MODE.get(mode, 14))


def _combat_potion_flask_cap(data):
    mode = _combat_coerce_pack_mode(data.get("combat_pack_mode", _COMBAT_DEFAULT_PACK_MODE))
    return _COMBAT_POTION_FLASK_CAP_BY_MODE.get(mode, 4)
COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS = 1000
COMBAT_GRAVE_RECOVERY_REVIEWS = 5
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


def default_combat_supply_loadout_pure():
    return {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "cannonballs": 0}


def default_combat_state_pure():
    return {
        "current_combat_target": DEFAULT_COMBAT_TARGET,
        "combat_attack_style": DEFAULT_COMBAT_ATTACK_STYLE,
        "combat_attack_style_type": "auto",
        "current_combat_spell": DEFAULT_COMBAT_SPELL,
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
        "combat_recovery_progress": {},
        "combat_bank_run": {},
        "combat_encounter": {},
        "combat_kill_counts": {},
        "combat_last_result": {},
        "combat_grave": {},
        "death_office": {},
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
            and item_name in COMBAT_ANTIPOISON_POTION_DATA
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
    loadout["cannonballs"] = _non_negative_int(raw_loadout.get("cannonballs", 0), 0)
    return loadout


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


def _carried_inventory_grave_counts(data):
    """What is actually in hand at death ({item: count}) — the carried view of the
    target being fought, i.e. the loot from this trip.

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
    target_id = data.get("current_combat_target")
    view = carried.get(target_id) if isinstance(target_id, str) else None
    if not isinstance(view, Mapping):
        return {}
    # Clamp to what the bank still holds. The view can outlive its items (discard,
    # shop sale, eating looted food), and graving more than existed would mint the
    # difference when the grave is reclaimed.
    return clamp_carried_view_to_bank(view, data.get("inventory"))


def _combat_apply_pvm_death(data, max_player_lifepoints, grave_source="combat_death"):
    equipment = dict(data.get("equipment", {}) or {})
    grave_items = [item_name for item_name in equipment.values() if isinstance(item_name, str)]
    # Carried items are a view over the flat store: remove them from the bank and
    # drop them into the grave, expanded one grave entry per unit. Only the view of
    # the target being fought is at risk — other targets' saved packs are loadouts
    # resting in the bank, not carried, so they must survive the death.
    carried_counts = _carried_inventory_grave_counts(data)
    if carried_counts:
        inventory = dict(data.get("inventory", {}) or {})
        for item_name, count in carried_counts.items():
            inventory[item_name] = max(0, _non_negative_int(inventory.get(item_name, 0), 0) - count)
            grave_items.extend([item_name] * count)
        data["inventory"] = inventory
    fought_target = data.get("current_combat_target")
    if isinstance(fought_target, str):
        for map_key in ("carried_inventory", "carried_churn"):
            container = data.get(map_key)
            if isinstance(container, Mapping) and fought_target in container:
                container = dict(container)
                container.pop(fought_target, None)
                data[map_key] = container
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
    data["equipment"] = {}
    data["combat_grave"] = {
        "items": grave_items,
        "reviews_remaining": COMBAT_GRAVE_RECOVERY_REVIEWS,
        "source": grave_source,
        "loadout": equipment,
    } if grave_items else {}
    data["combat_encounter"] = {}
    data["combat_status_effects"] = {}
    data["combat_lifepoints"] = max_player_lifepoints
    return max_player_lifepoints


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
    kill_counts = player_data.get("combat_kill_counts", {}) or {}
    if not isinstance(kill_counts, Mapping):
        kill_counts = {}
    special_energy = _non_negative_int(
        player_data.get("combat_special_attack_energy", defaults["combat_special_attack_energy"]),
        defaults["combat_special_attack_energy"],
    )
    return {
        "current_combat_target": target,
        "combat_attack_style": style,
        "combat_attack_style_type": style_type,
        "current_combat_spell": spell,
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
        "combat_recovery_progress": _sanitize_combat_recovery_progress(player_data.get("combat_recovery_progress")),
        "combat_bank_run": _sanitize_combat_bank_run(player_data.get("combat_bank_run")),
        "combat_encounter": dict(encounter),
        "combat_kill_counts": {
            str(target_id): _positive_int(count, 0)
            for target_id, count in kill_counts.items()
            if isinstance(target_id, str)
        },
        "combat_last_result": dict(player_data.get("combat_last_result", {}) or {}),
        "combat_grave": _sanitize_combat_grave_state(player_data.get("combat_grave", {}) or {}),
        "death_office": _sanitize_death_office_state(player_data.get("death_office", {}) or {}),
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


def combat_target_locked_reasons_pure(player_data, target_id, enemy_data=None, style_data=None, equipment_data=None):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    style_data = style_data or COMBAT_ATTACK_STYLE_DATA
    enemy = enemy_data.get(target_id)
    if enemy is None:
        return ("unknown enemy",)
    stats = enemy.get("stats", {})
    if not isinstance(stats, Mapping) or _positive_int(stats.get("hitpoints", 0), 0) <= 0:
        return ("missing source combat stats",)
    drops = enemy.get("drops")
    if not isinstance(drops, Mapping):
        return ("missing source drop behavior",)
    style_id = combat_attack_style_for_equipment_pure(player_data, equipment_data)
    style = style_data.get(style_id)
    if not isinstance(style, Mapping):
        return ("invalid attack style",)
    combat_class = style.get("combat_class")
    if combat_class == "melee":
        return tuple()
    if combat_class == "ranged":
        return _combat_ranged_locked_reasons(player_data, target_id, equipment_data or {})
    if combat_class == "magic":
        return _combat_magic_locked_reasons(player_data, target_id, equipment_data or {})
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


def _signed_int(value, default=0):
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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


COMBAT_ENEMY_ATTACK_CLASSES = ("melee", "ranged", "magic")


def _combat_enemy_attack_class(enemy):
    """The style the ENEMY attacks with. Determines which of its attack bonuses
    drives its accuracy and which of the player's defence bonuses resists it.
    Unknown values fall back to melee (every roster enemy is melee today)."""
    if not isinstance(enemy, Mapping):
        return "melee"
    style = enemy.get("attack_style", "melee")
    return style if style in COMBAT_ENEMY_ATTACK_CLASSES else "melee"


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


def _combat_ranged_max_hit_old_hp(effective_ranged, ranged_strength_bonus):
    return max(0.0, 0.5 + float(effective_ranged) * (float(ranged_strength_bonus) + 64.0) / 640.0)


def _combat_magic_max_hit_old_hp(spell_spec, player_totals):
    if not isinstance(spell_spec, Mapping):
        return 0.0
    base_hit = _positive_int(spell_spec.get("max_hit_old_hp", 0), 0)
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


def _combat_selected_ranged_ammo(player_data, weapon_spec, target_id):
    if not isinstance(weapon_spec, Mapping):
        return None
    for ammo_name in weapon_spec.get("compatible_ammo", ()) or ():
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
    if _combat_selected_ranged_ammo(player_data, weapon_spec, target_id) is None:
        return ("compatible ammunition",)
    return tuple()


def _combat_selected_magic_spell(player_data):
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
    _spell_id, spell_spec = _combat_selected_magic_spell(player_data)
    if not isinstance(spell_spec, Mapping) or not spell_spec:
        return ("source-backed combat spell",)
    required_level = _positive_int(spell_spec.get("required_magic_level", 1), 1)
    if _combat_effective_skill_level(player_data, "magic", 1) < required_level:
        return (f"Magic level {required_level}",)
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


def _combat_roll_damage_lifepoints(max_hit_old_hp, rng):
    # Darkan CombatFormula.kt rolls Utils.random(minHit=1, maxHit) on a landed
    # hit, and Utils.random(min, max) is min + nextInt(|max - min|): uniform
    # 1..maxHit-1 lifepoints, never 0 and never the displayed max (maxHit 1
    # always deals 1). A 0 can only come from the accuracy roll failing.
    max_damage = int(max(0.0, float(max_hit_old_hp) * 10.0))
    if max_damage <= 0:
        return 0
    spread = max_damage - 1
    if spread <= 0:
        return 1
    try:
        roll = float(rng())
    except (TypeError, ValueError):
        roll = 0.0
    return 1 + int(max(0.0, min(roll, 0.999999999)) * spread)


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


def _combat_roll_drop_table(table, rng, drops):
    if not isinstance(table, Mapping):
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
            _combat_roll_drop_table(nested_table, rng, drops)
            break
        item_name = slot.get("item")
        if isinstance(item_name, str):
            drops[item_name] = drops.get(item_name, 0) + _combat_slot_drop_quantity(slot, rng)
        break


def _combat_roll_drops(enemy, rng):
    drops = {}
    drop_spec = enemy.get("drops", {}) if isinstance(enemy, Mapping) else {}
    if not isinstance(drop_spec, Mapping):
        return drops
    for item_name, quantity in drop_spec.get("guaranteed", ()) or ():
        if isinstance(item_name, str):
            drops[item_name] = drops.get(item_name, 0) + max(1, _positive_int(quantity, 1))
    for table in drop_spec.get("tables", ()) or ():
        _combat_roll_drop_table(table, rng, drops)
    return drops


def _combat_refill_food_loadout(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    food_loadout = dict(loadout.get("food", {}) or {})
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        data["combat_supply_loadout"] = loadout
        return
    inventory = dict(inventory)
    # Food is capped by the packing mode's slot allocation (food is unstackable,
    # so count == slots); the freed slots leave room for damage potions.
    food_cap = _combat_food_slot_cap(data)
    loaded_food = sum(_non_negative_int(amount, 0) for amount in food_loadout.values())
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        if loaded_food >= food_cap:
            break
        if item_name not in COMBAT_FOOD_DATA:
            continue
        available = _non_negative_int(inventory.get(item_name, 0), 0)
        if available <= 0:
            continue
        take = min(available, food_cap - loaded_food)
        inventory[item_name] = available - take
        food_loadout[item_name] = _non_negative_int(food_loadout.get(item_name, 0), 0) + take
        loaded_food += take
    loadout["food"] = {item: amount for item, amount in food_loadout.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_loaded_food_count(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    food_loadout = loadout.get("food", {}) or {}
    total = 0
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        if isinstance(item_name, str):
            total += _non_negative_int(food_loadout.get(item_name, 0), 0)
    return total


def _combat_banked_auto_food_count(data):
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return 0
    total = 0
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        if isinstance(item_name, str) and item_name in COMBAT_FOOD_DATA:
            total += _non_negative_int(inventory.get(item_name, 0), 0)
    return total


def _combat_loaded_ranged_ammo(data, weapon_spec):
    if not isinstance(weapon_spec, Mapping):
        return None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    ammo_loadout = loadout.get("ammo", {}) or {}
    for ammo_name in weapon_spec.get("compatible_ammo", ()) or ():
        if isinstance(ammo_name, str) and _non_negative_int(ammo_loadout.get(ammo_name, 0), 0) > 0:
            return ammo_name
    return None


def _combat_banked_ranged_ammo_count(data, weapon_spec):
    if not isinstance(weapon_spec, Mapping):
        return 0
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return 0
    total = 0
    for ammo_name in weapon_spec.get("compatible_ammo", ()) or ():
        if isinstance(ammo_name, str):
            total += _non_negative_int(inventory.get(ammo_name, 0), 0)
    return total


def _combat_missing_loaded_runes(data, spell_spec, equipment_data=None):
    rune_cost = spell_spec.get("rune_cost", {}) if isinstance(spell_spec, Mapping) else {}
    if not isinstance(rune_cost, Mapping) or not rune_cost:
        return {}
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    rune_loadout = loadout.get("runes", {}) or {}
    covered_runes = combat_staff_covered_runes_pure(data, equipment_data)
    missing = {}
    for rune_name, amount in rune_cost.items():
        if not isinstance(rune_name, str) or rune_name in covered_runes:
            continue
        required = _positive_int(amount, 0)
        loaded = _non_negative_int(rune_loadout.get(rune_name, 0), 0)
        if required > loaded:
            missing[rune_name] = required - loaded
    return missing


def _combat_bank_has_runes(data, missing_runes):
    if not missing_runes:
        return False
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return False
    return all(_non_negative_int(inventory.get(rune_name, 0), 0) >= amount for rune_name, amount in missing_runes.items())


def _combat_loaded_antipoison_count(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    return sum(_non_negative_int(amount, 0) for amount in (loadout.get("potions", {}) or {}).values())


def _combat_banked_antipoison_count(data):
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return 0
    return sum(_non_negative_int(inventory.get(item_name, 0), 0) for item_name in COMBAT_ANTIPOISON_POTION_DATA)


def _combat_loot_slots(data, target_id):
    """Carried slots the kept combat loot for this target occupies. Clamped to the
    bank so loot the player has since sold/discarded/eaten cannot occupy phantom
    slots and force a bank run that has nothing to deposit."""
    if not isinstance(target_id, str):
        return 0
    carried = data.get("carried_inventory")
    view = carried.get(target_id) if isinstance(carried, Mapping) else None
    if not isinstance(view, Mapping):
        return 0
    return carried_slots_used(clamp_carried_view_to_bank(view, data.get("inventory")), STACKABLE_ITEM_NAMES)


def _combat_deposit_loot(data, target_id):
    """Banking deposits carried loot: it stays in the flat store but is no longer
    at risk (cleared from the carried view, so death no longer drops it)."""
    if not isinstance(target_id, str):
        return
    carried = data.get("carried_inventory")
    if isinstance(carried, Mapping) and target_id in carried:
        carried = dict(carried)
        carried.pop(target_id, None)
        data["carried_inventory"] = carried


def _combat_refill_context_supplies(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data=None, enemy_data=None):
    _combat_refill_food_loadout(data)
    _combat_refill_stat_potions(data, combat_class)
    enemy_lookup = enemy_data or COMBAT_ENEMY_DATA
    enemy = enemy_lookup.get(target_id, {}) if isinstance(target_id, str) and isinstance(enemy_lookup, Mapping) else {}
    target_poison = _positive_int(enemy.get("poison_damage", 0), 0) if isinstance(enemy, Mapping) else 0
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if target_poison > 0 or "poison" in effects:
        _combat_refill_antipoison_loadout(data)
    if combat_class == "ranged":
        _combat_refill_ranged_ammo_loadout(data, ranged_weapon_spec)
    elif combat_class == "magic":
        _combat_refill_magic_rune_loadout(data, spell_spec, equipment_data)
    # The same bank trip deposits accumulated loot (owner: loot banks alongside
    # supply depletion).
    _combat_deposit_loot(data, target_id)


def _combat_bank_run_needed(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data=None, enemy_data=None):
    # One 28-slot inventory: supplies (food/potions/ammo/runes) and loot share it,
    # so a bank run is forced when together they fill it. As food is eaten the
    # freed slots become loot room, exactly like a real inventory.
    #
    # Guard: only *loot* is deposited by a bank run, so with nothing to deposit a
    # full inventory cannot be relieved by banking. Requiring loot here means an
    # over-budget supply loadout can never softlock combat into a permanent
    # bank-run loop (it would refill the same supplies and re-trigger forever).
    loot_slots = _combat_loot_slots(data, target_id)
    if loot_slots > 0 and _combat_supply_slots_used(data) + loot_slots >= CARRIED_CAPACITY:
        return True
    if _combat_loaded_food_count(data) <= 0 and _combat_banked_auto_food_count(data) > 0:
        return True
    enemy_lookup = enemy_data or COMBAT_ENEMY_DATA
    enemy = enemy_lookup.get(target_id, {}) if isinstance(target_id, str) and isinstance(enemy_lookup, Mapping) else {}
    target_poison = _positive_int(enemy.get("poison_damage", 0), 0) if isinstance(enemy, Mapping) else 0
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if (target_poison > 0 or "poison" in effects) and _combat_loaded_antipoison_count(data) <= 0:
        if _combat_banked_antipoison_count(data) > 0:
            return True
    if combat_class == "ranged":
        return _combat_loaded_ranged_ammo(data, ranged_weapon_spec) is None and _combat_banked_ranged_ammo_count(data, ranged_weapon_spec) > 0
    if combat_class == "magic":
        missing_runes = _combat_missing_loaded_runes(data, spell_spec, equipment_data)
        return _combat_bank_has_runes(data, missing_runes)
    return False


def _combat_bank_run_result(data, target_id, started=False, completed=False):
    bank_run = _sanitize_combat_bank_run(data.get("combat_bank_run"))
    return {
        "reason": "combat_bank_run",
        "target_id": target_id,
        "display_name": COMBAT_ENEMY_DATA.get(target_id, {}).get("display_name", target_id)
        if isinstance(target_id, str)
        else "",
        "bank_run_started": bool(started),
        "bank_run_completed": bool(completed),
        "bank_run_reviews_remaining": _non_negative_int(bank_run.get("reviews_remaining", 0), 0),
        "ticks": 0,
        "ticks_elapsed": 0,
        "player_damage": 0,
        "enemy_damage": 0,
        "killed": False,
        "died": False,
        "stop_reason": "bank_run",
        "food_used": tuple(),
        "potions_used": tuple(),
        "ammo_used": {},
        "runes_used": {},
        "status_damage": {},
        "status_applied": {},
        "status_expired": tuple(),
        "drops": {},
        "xp_rewards": {},
    }


def _combat_locks_can_bank_run(locked_reasons):
    if not locked_reasons:
        return True
    return all(
        isinstance(reason, str)
        and (reason == "compatible ammunition" or reason.startswith("runes: "))
        for reason in locked_reasons
    )


def _combat_progress_or_start_bank_run(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data=None, enemy_data=None):
    bank_run = _sanitize_combat_bank_run(data.get("combat_bank_run"))
    if bank_run and bank_run.get("target_id") not in (None, target_id):
        bank_run = {}
    started = False
    if not bank_run and _combat_bank_run_needed(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data):
        bank_run = {"reviews_remaining": COMBAT_BANK_RUN_REVIEWS, "target_id": target_id}
        started = True
    if not bank_run:
        data["combat_bank_run"] = {}
        return None
    remaining = _non_negative_int(bank_run.get("reviews_remaining", 0), 0) - 1
    if remaining <= 0:
        data["combat_bank_run"] = {}
        _combat_refill_context_supplies(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data)
        return _combat_bank_run_result(data, target_id, started=started, completed=True)
    data["combat_bank_run"] = {"reviews_remaining": remaining, "target_id": target_id}
    return _combat_bank_run_result(data, target_id, started=started, completed=False)


def _combat_refill_ranged_ammo_loadout(data, weapon_spec):
    if not isinstance(weapon_spec, Mapping):
        return
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    ammo_loadout = dict(loadout.get("ammo", {}) or {})
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        data["combat_supply_loadout"] = loadout
        return
    inventory = dict(inventory)
    for ammo_name in weapon_spec.get("compatible_ammo", ()) or ():
        if not isinstance(ammo_name, str):
            continue
        available = _non_negative_int(inventory.get(ammo_name, 0), 0)
        if available <= 0:
            continue
        inventory[ammo_name] = 0
        ammo_loadout[ammo_name] = _non_negative_int(ammo_loadout.get(ammo_name, 0), 0) + available
    loadout["ammo"] = {item: amount for item, amount in ammo_loadout.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_refill_magic_rune_loadout(data, spell_spec, equipment_data=None):
    if not isinstance(spell_spec, Mapping):
        return
    rune_cost = spell_spec.get("rune_cost", {})
    if not isinstance(rune_cost, Mapping):
        return
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    rune_loadout = dict(loadout.get("runes", {}) or {})
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        data["combat_supply_loadout"] = loadout
        return
    inventory = dict(inventory)
    covered_runes = combat_staff_covered_runes_pure(data, equipment_data)
    for rune_name in rune_cost:
        if not isinstance(rune_name, str):
            continue
        if rune_name in covered_runes:
            loaded = _non_negative_int(rune_loadout.pop(rune_name, 0), 0)
            if loaded > 0:
                inventory[rune_name] = _non_negative_int(inventory.get(rune_name, 0), 0) + loaded
            continue
        available = _non_negative_int(inventory.get(rune_name, 0), 0)
        if available <= 0:
            continue
        inventory[rune_name] = 0
        rune_loadout[rune_name] = _non_negative_int(rune_loadout.get(rune_name, 0), 0) + available
    loadout["runes"] = {item: amount for item, amount in rune_loadout.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_consume_ranged_ammo(data, weapon_spec, target_id):
    ammo_name = _combat_selected_ranged_ammo(data, weapon_spec, target_id)
    if not isinstance(ammo_name, str):
        return None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    ammo_loadout = dict(loadout.get("ammo", {}) or {})
    current = _non_negative_int(ammo_loadout.get(ammo_name, 0), 0)
    if current <= 0:
        return None
    ammo_loadout[ammo_name] = current - 1
    if ammo_loadout[ammo_name] <= 0:
        ammo_loadout.pop(ammo_name, None)
    loadout["ammo"] = ammo_loadout
    data["combat_supply_loadout"] = loadout
    return ammo_name


def _combat_consume_magic_runes(data, spell_spec, target_id, equipment_data=None):
    if not isinstance(spell_spec, Mapping):
        return None
    rune_cost = spell_spec.get("rune_cost", {})
    if not isinstance(rune_cost, Mapping) or not rune_cost:
        return {}
    if _combat_magic_missing_runes(data, spell_spec, target_id, equipment_data):
        return None
    covered_runes = combat_staff_covered_runes_pure(data, equipment_data)
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    rune_loadout = dict(loadout.get("runes", {}) or {})
    used = {}
    for rune_name, amount in rune_cost.items():
        if not isinstance(rune_name, str):
            continue
        if rune_name in covered_runes:
            continue
        required = _positive_int(amount, 0)
        if required <= 0:
            continue
        current = _non_negative_int(rune_loadout.get(rune_name, 0), 0)
        rune_loadout[rune_name] = current - required
        if rune_loadout[rune_name] <= 0:
            rune_loadout.pop(rune_name, None)
        used[rune_name] = required
    loadout["runes"] = rune_loadout
    data["combat_supply_loadout"] = loadout
    return used


def _combat_ranged_strength_bonus(player_totals, ammo_name):
    ammo_spec = COMBAT_RANGED_AMMO_DATA.get(ammo_name) if isinstance(ammo_name, str) else None
    ammo_bonus = _positive_int(ammo_spec.get("ranged_strength", 0), 0) if isinstance(ammo_spec, Mapping) else 0
    return _equipment_bonus_value(player_totals, "ranged_strength") + ammo_bonus


def _combat_regenerate_special_attack_energy(data, ticks):
    energy = _non_negative_int(
        data.get("combat_special_attack_energy", COMBAT_SPECIAL_ATTACK_MAX_ENERGY),
        COMBAT_SPECIAL_ATTACK_MAX_ENERGY,
    )
    regen = int(max(0, _non_negative_int(ticks, 0)) * COMBAT_SPECIAL_ATTACK_REGEN_PER_50_TICKS / COMBAT_BURST_TICKS)
    data["combat_special_attack_energy"] = min(COMBAT_SPECIAL_ATTACK_MAX_ENERGY, energy + regen)


def _combat_recover_current_levels(data, ticks):
    """Restore boosted/drained current levels toward base by one level per
    COMBAT_STAT_DRAIN_RECOVERY_TICKS ticks (engine restoreTick cadence:
    +1 toward max every 100 ticks). Boosts decay down, drains recover up."""
    currents = _sanitize_combat_current_levels(data.get("combat_current_levels"))
    progress = _sanitize_combat_recovery_progress(data.get("combat_recovery_progress"))
    if not currents:
        progress.pop("stat_drain_ticks", None)
        data["combat_current_levels"] = {}
        data["combat_recovery_progress"] = progress
        return
    stat_drain_ticks = _non_negative_int(progress.get("stat_drain_ticks", 0), 0) + max(0, _non_negative_int(ticks, 0))
    steps = stat_drain_ticks // COMBAT_STAT_DRAIN_RECOVERY_TICKS
    stat_drain_ticks = stat_drain_ticks % COMBAT_STAT_DRAIN_RECOVERY_TICKS
    if steps > 0:
        restored = {}
        for skill_id, current in currents.items():
            base = _combat_base_skill_level(data, skill_id, current)
            if current < base:
                current = min(base, current + steps)
            elif current > base:
                current = max(base, current - steps)
            if current != base:
                restored[skill_id] = current
        currents = restored
    progress["stat_drain_ticks"] = stat_drain_ticks if currents and stat_drain_ticks > 0 else 0
    data["combat_current_levels"] = currents
    data["combat_recovery_progress"] = {key: value for key, value in progress.items() if value > 0}


def combat_poison_immunity_ticks_pure(player_data):
    effects = _sanitize_combat_status_effects(player_data.get("combat_status_effects"))
    immunity = effects.get("poison_immunity", {})
    return _non_negative_int(immunity.get("ticks_left", 0), 0) if isinstance(immunity, Mapping) else 0


def _combat_refill_antipoison_loadout(data):
    """Load a couple of antipoison doses — one cures the poison, so two cover a
    trip and refill at every bank run. Uncapped, this loaded the player's entire
    antipoison stock into the loadout, which (since each unstackable dose costs a
    slot) could push supplies past the whole 28-slot inventory and softlock combat
    into a permanent bank-run loop."""
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    potion_loadout = dict(loadout.get("potions", {}) or {})
    inventory = dict(data.get("inventory", {}) or {})
    loaded = sum(_non_negative_int(amount, 0) for amount in potion_loadout.values())
    for item_name in COMBAT_ANTIPOISON_POTION_DATA:
        if loaded >= _COMBAT_ANTIPOISON_SLOT_CAP:
            break
        available = _non_negative_int(inventory.get(item_name, 0), 0)
        if available <= 0:
            continue
        take = min(available, _COMBAT_ANTIPOISON_SLOT_CAP - loaded)
        potion_loadout[item_name] = _non_negative_int(potion_loadout.get(item_name, 0), 0) + take
        inventory[item_name] = available - take
        loaded += take
    loadout["potions"] = {item_name: amount for item_name, amount in potion_loadout.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_consume_antipoison_if_needed(data):
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if "poison" not in effects:
        data["combat_status_effects"] = effects
        return None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    potion_loadout = dict(loadout.get("potions", {}) or {})
    for item_name, spec in COMBAT_ANTIPOISON_POTION_DATA.items():
        amount = _non_negative_int(potion_loadout.get(item_name, 0), 0)
        if amount <= 0:
            continue
        amount -= 1
        if amount > 0:
            potion_loadout[item_name] = amount
        else:
            potion_loadout.pop(item_name, None)
        replacement = str(spec.get("replacement", ""))
        if replacement in COMBAT_ANTIPOISON_POTION_DATA:
            potion_loadout[replacement] = _non_negative_int(potion_loadout.get(replacement, 0), 0) + 1
        elif replacement:
            inventory = dict(data.get("inventory", {}) or {})
            inventory[replacement] = _non_negative_int(inventory.get(replacement, 0), 0) + 1
            data["inventory"] = inventory
        immunity_ticks = _positive_int(spec.get("immunity_ticks", 0), 0)
        current_immunity = effects.get("poison_immunity", {})
        current_ticks = (
            _non_negative_int(current_immunity.get("ticks_left", 0), 0)
            if isinstance(current_immunity, Mapping)
            else 0
        )
        effects.pop("poison", None)
        effects["poison_immunity"] = {
            "ticks_left": max(current_ticks, immunity_ticks),
            "source": spec.get("source", POTION_TYPE_SOURCE_PATH),
        }
        loadout["potions"] = {potion: qty for potion, qty in potion_loadout.items() if qty > 0}
        data["combat_supply_loadout"] = loadout
        data["combat_status_effects"] = effects
        return {
            "item": item_name,
            "replacement": replacement,
            "effect": "poison_cure",
            "immunity_ticks": immunity_ticks,
        }
    data["combat_status_effects"] = effects
    return None


def combat_poison_ticks_for_initial_damage_pure(initial_damage):
    damage = _positive_int(initial_damage, 0)
    return max(0, damage * 5 - 4)


def combat_poison_damage_for_ticks_pure(ticks_left):
    return ((_non_negative_int(ticks_left, 0) // 5) + 1) * 10


def _combat_apply_poison_effect_to_data(data, initial_damage):
    ticks_left = combat_poison_ticks_for_initial_damage_pure(initial_damage)
    if ticks_left <= 0:
        return False, "invalid poison damage"
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if combat_poison_immunity_ticks_pure({"combat_status_effects": effects}) > 0:
        data["combat_status_effects"] = effects
        return False, "poison immune"
    current_poison = effects.get("poison", {})
    current_damage = combat_poison_damage_for_ticks_pure(current_poison.get("ticks_left", 0)) if current_poison else 0
    new_damage = combat_poison_damage_for_ticks_pure(ticks_left)
    if current_poison and current_damage > new_damage:
        data["combat_status_effects"] = effects
        return False, "existing poison is stronger"
    effects["poison"] = {
        "ticks_left": ticks_left,
        "tick_progress": 0,
        "source": COMBAT_POISON_SOURCE_PATH,
    }
    data["combat_status_effects"] = effects
    return True, ""


def apply_combat_poison_effect_pure(player_data, initial_damage):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    applied, reason = _combat_apply_poison_effect_to_data(data, initial_damage)
    return data, applied, reason


def _combat_advance_status_effects(data, ticks, current_lifepoints=None, max_lifepoints=None):
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if current_lifepoints is not None:
        data["combat_lifepoints"] = _non_negative_int(current_lifepoints, 0)
    max_lp = max_lifepoints if max_lifepoints is not None else combat_max_lifepoints_pure(data)
    player_lp = max(
        0,
        min(
            _non_negative_int(data.get("combat_lifepoints", max_lp), max_lp),
            max_lp + COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
        ),
    )
    result = {"damage": {}, "expired": tuple(), "died": False}
    expired = []
    immunity = effects.get("poison_immunity")
    if immunity:
        ticks_left = max(
            0,
            _non_negative_int(immunity.get("ticks_left", 0), 0) - max(0, _non_negative_int(ticks, 0)),
        )
        if ticks_left > 0:
            effects["poison_immunity"] = {
                "ticks_left": ticks_left,
                "source": immunity.get("source", POTION_TYPE_SOURCE_PATH),
            }
        else:
            effects.pop("poison_immunity", None)
            expired.append("poison_immunity")
    poison = effects.get("poison")
    if poison:
        progress = _non_negative_int(poison.get("tick_progress", 0), 0) + max(0, _non_negative_int(ticks, 0))
        ticks_left = _non_negative_int(poison.get("ticks_left", 0), 0)
        poison_damage = 0
        while ticks_left > 0 and progress >= COMBAT_POISON_TICK_DELAY and player_lp > 0:
            progress -= COMBAT_POISON_TICK_DELAY
            damage = min(player_lp, combat_poison_damage_for_ticks_pure(ticks_left))
            poison_damage += damage
            player_lp -= damage
            ticks_left -= 1
        if poison_damage > 0:
            result["damage"]["poison"] = poison_damage
        if ticks_left > 0 and player_lp > 0:
            effects["poison"] = {
                "ticks_left": ticks_left,
                "tick_progress": min(progress, COMBAT_POISON_TICK_DELAY - 1),
                "source": poison.get("source", COMBAT_POISON_SOURCE_PATH),
            }
        else:
            effects.pop("poison", None)
            if ticks_left <= 0:
                expired.append("poison")
    result["died"] = player_lp <= 0 and bool(result["damage"])
    result["expired"] = tuple(expired)
    data["combat_lifepoints"] = player_lp
    data["combat_status_effects"] = effects
    return result


def combat_status_summary_pure(player_data):
    effects = _sanitize_combat_status_effects(player_data.get("combat_status_effects"))
    poison = effects.get("poison")
    if poison:
        ticks_left = _non_negative_int(poison.get("ticks_left", 0), 0)
        tick_progress = _non_negative_int(poison.get("tick_progress", 0), 0)
        next_damage = combat_poison_damage_for_ticks_pure(ticks_left)
        ticks_until = max(1, COMBAT_POISON_TICK_DELAY - min(tick_progress, COMBAT_POISON_TICK_DELAY - 1))
        return f"Poisoned: {next_damage} LP in {ticks_until} ticks"
    immunity_ticks = combat_poison_immunity_ticks_pure({"combat_status_effects": effects})
    if immunity_ticks > 0:
        return f"Poison immune: {immunity_ticks} ticks"
    return ""


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
        return min(max_lifepoints, current_lifepoints + healed_by), {"item": item_name, "healed_by": healed_by}
    return current_lifepoints, None


def _combat_auto_eat_food_available(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    food_loadout = loadout.get("food", {}) or {}
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        if item_name in COMBAT_FOOD_DATA and _positive_int(food_loadout.get(item_name, 0), 0) > 0:
            return True
    return False


def _combat_should_auto_flee(data, current_lifepoints, max_lifepoints):
    """Auto-flee bails out of the burst when LP has fallen to the auto-eat
    threshold and there is no food left to recover with — the "dying silently"
    case. Enabled by default; the last-ditch heal has already been attempted by
    the caller, so reaching here means the player genuinely cannot recover."""
    if not data.get("combat_auto_flee", True):
        return False
    threshold_percent = _positive_int(data.get("combat_auto_eat_threshold_percent", 40), 40)
    threshold = max(1, int(max_lifepoints * threshold_percent / 100.0))
    if current_lifepoints > threshold:
        return False
    return not _combat_auto_eat_food_available(data)


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


def apply_combat_stat_boost_to_pure(data, skill_id, boost):
    """Potion-style boost (shared by all stat potions): sets current to
    base + boost *as a floor* — it cures a drained stat and boosts to the
    ceiling, but never lowers an already-higher boost and never stacks past
    base + boost (engine `boostCap`). Mutates and returns ``data``."""
    base = _combat_base_skill_level(data, skill_id, 1)
    target = base + max(0, int(boost))
    current = _combat_effective_skill_level(data, skill_id, base)
    if target > current:
        apply_combat_stat_delta_pure(data, skill_id, target - current)
    return data


def _potion_boost_amount(base_level, strategy):
    # PotionType.kt: regular = floor(base/10)+3, super = floor(15*base/100)+5.
    base = max(1, int(base_level))
    if strategy == "s":
        return int(15 * base / 100) + 5
    return base // 10 + 3


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
_COMBAT_STAT_POTION_ITEM_NAMES = frozenset(_COMBAT_STAT_POTION_BY_DOSE)


def _combat_relevant_potion_skills(combat_class):
    """The stat(s) a potion should boost for the active combat style — the ones
    that actually raise output (max hit / accuracy). Defence is not an output
    stat, so it is not auto-potioned."""
    if combat_class == "ranged":
        return ("ranged",)
    if combat_class == "magic":
        return ("magic",)
    return ("strength", "attack")


def _combat_pick_potion_for_skill(stat_potions, skill_id):
    """Choose the loadout stat-potion dose to drink for ``skill_id``: prefer a
    super potion (bigger boost), then the higher dose (drink the fuller flask
    first, RS-style). Returns the dose item name or None."""
    best = None
    best_rank = None
    for item_name, count in stat_potions.items():
        if _non_negative_int(count, 0) <= 0:
            continue
        entry = _COMBAT_STAT_POTION_BY_DOSE.get(item_name)
        if entry is None or skill_id not in entry[1]:
            continue
        _base, _skills, strategy, dose, _is_flask = entry
        rank = (1 if strategy == "s" else 0, dose)
        if best_rank is None or rank > best_rank:
            best, best_rank = item_name, rank
    return best


def _combat_auto_drink_potions(data, combat_class):
    """Drink carried stat potions at burst start to (re)apply the output boosts
    for the active style. Only drinks a stat that has no active boost (effective
    <= base), so one flask lasts until its boost fully decays. Drinking a dose
    consumes it (a (4) leaves a (3); a (1) empties). Returns the drink events."""
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    stat_potions = dict(loadout.get("stat_potions", {}) or {})
    if not stat_potions:
        return []
    events = []
    for skill_id in _combat_relevant_potion_skills(combat_class):
        base = _combat_base_skill_level(data, skill_id, 1)
        if _combat_effective_skill_level(data, skill_id, base) > base:
            continue  # a boost is already active on this stat
        item_name = _combat_pick_potion_for_skill(stat_potions, skill_id)
        if item_name is None:
            continue
        base_name, skills, strategy, dose, is_flask = _COMBAT_STAT_POTION_BY_DOSE[item_name]
        # Consume one dose: the vial/flask drops to the next-lower dose (dropped at 0/empty).
        stat_potions[item_name] = _non_negative_int(stat_potions.get(item_name, 0), 0) - 1
        if stat_potions[item_name] <= 0:
            stat_potions.pop(item_name, None)
        if dose > 1:
            lower = potion_flask_name(base_name, dose - 1) if is_flask else potion_dose_name(base_name, dose - 1)
            stat_potions[lower] = _non_negative_int(stat_potions.get(lower, 0), 0) + 1
        # Apply the boost to every stat the family covers (Combat potion = both).
        for boosted_skill in skills:
            boost = _potion_boost_amount(_combat_base_skill_level(data, boosted_skill, 1), strategy)
            apply_combat_stat_boost_to_pure(data, boosted_skill, boost)
        events.append({"item": item_name, "skills": tuple(skills)})
    loadout["stat_potions"] = {name: amount for name, amount in stat_potions.items() if amount > 0}
    data["combat_supply_loadout"] = loadout
    return events


def _combat_relevant_potion_items(combat_class):
    """Style-relevant stat-potion dose items, best-first: supers before regulars,
    a Combat potion (boosts both melee stats from one slot) preferred, fuller
    flasks first. Used so a small potion cap is never wasted on an off-style flask."""
    relevant_skills = set(_combat_relevant_potion_skills(combat_class))
    items = []
    for item_name, (base_name, skills, strategy, dose, _is_flask) in _COMBAT_STAT_POTION_BY_DOSE.items():
        if relevant_skills.intersection(skills):
            covers_two = len(skills) > 1
            # More doses per slot ranks higher, so a full flask (6) beats a vial (4).
            rank = (1 if strategy == "s" else 0, 1 if covers_two else 0, int(dose))
            items.append((rank, item_name))
    items.sort(reverse=True)
    return [item_name for _rank, item_name in items]


def _combat_refill_stat_potions(data, combat_class="melee"):
    """Load style-relevant stat-potion flasks into the loadout, up to the packing
    mode's flask cap (a couple of doses last a whole trip and refill every bank
    run). One flask = one slot; off-style potions are never loaded."""
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    stat_potions = dict(loadout.get("stat_potions", {}) or {})
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        data["combat_supply_loadout"] = loadout
        return
    inventory = dict(inventory)
    cap = _combat_potion_flask_cap(data)
    loaded = sum(_non_negative_int(amount, 0) for amount in stat_potions.values())
    for item_name in _combat_relevant_potion_items(combat_class):
        if loaded >= cap:
            break
        available = _non_negative_int(inventory.get(item_name, 0), 0)
        if available <= 0:
            continue
        take = min(available, cap - loaded)
        inventory[item_name] = available - take
        stat_potions[item_name] = _non_negative_int(stat_potions.get(item_name, 0), 0) + take
        loaded += take
    loadout["stat_potions"] = {name: amount for name, amount in stat_potions.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_supply_slots_used(data):
    """Slots the combat loadout occupies in the shared 28-slot inventory. Food and
    unstackable potions cost one slot each; ammo/runes/cannonballs are stackable,
    so one slot per distinct stack. What's left is room for loot."""
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    slots = 0
    for key in ("food", "potions", "stat_potions"):
        slots += sum(_non_negative_int(amount, 0) for amount in (loadout.get(key, {}) or {}).values())
    for key in ("ammo", "runes"):
        slots += sum(1 for amount in (loadout.get(key, {}) or {}).values() if _non_negative_int(amount, 0) > 0)
    if _non_negative_int(loadout.get("cannonballs", 0), 0) > 0:
        slots += 1
    return slots


def _consumable_heal(data, amount):
    max_lp = combat_max_lifepoints_pure(data)
    current = _non_negative_int(data.get("combat_lifepoints", max_lp), max_lp)
    healed = min(max_lp, current + max(0, int(amount)))
    data["combat_lifepoints"] = healed
    return healed - current


def apply_consumable_pure(player_data, item_name, rng=None):
    """Eat/drink a stat-affecting consumable (Kebab, Beer). Consumes one from
    inventory, applies the source effect (heal + current-level boosts/drains),
    and returns (new_data, result). Undo-safe: never mutates the input."""
    rng = rng or (lambda: 0.0)
    spec = CONSUMABLE_DATA.get(item_name)
    if spec is None:
        return dict(player_data), {"allowed": False, "reason": "not_a_consumable"}
    data = _copy_player_data_with_nested(player_data)
    inventory = dict(data.get("inventory", {}) or {})
    if _non_negative_int(inventory.get(item_name, 0), 0) <= 0:
        return dict(player_data), {"allowed": False, "reason": "missing_item", "item_name": item_name}
    inventory[item_name] = _non_negative_int(inventory.get(item_name, 0), 0) - 1
    if inventory[item_name] <= 0:
        inventory.pop(item_name, None)
    data["inventory"] = inventory

    healed = 0
    boosts = {}
    drains = {}
    message = str(spec.get("message", ""))

    if spec["kind"] == "kebab_random":
        roll = max(0.0, min(float(rng()) * 100.0, 99.999999))
        outcome = next(o for o in spec["effect_table"] if roll < float(o["upto"]))
        message = str(outcome.get("message", message))
        if "heal_max_pct" in outcome:
            healed = _consumable_heal(data, int(combat_max_lifepoints_pure(data) * float(outcome["heal_max_pct"])))
        elif "heal_range" in outcome:
            lo, hi = outcome["heal_range"]
            healed = _consumable_heal(data, lo + int(max(0.0, min(float(rng()), 0.999999999)) * (hi - lo)))
        elif "heal" in outcome:
            healed = _consumable_heal(data, int(outcome["heal"]))
        for skill_id, (lo, hi) in (outcome.get("boost_levels", {}) or {}).items():
            amount = lo + int(max(0.0, min(float(rng()), 0.999999999)) * (hi - lo))
            apply_combat_stat_delta_pure(data, skill_id, amount)
            boosts[skill_id] = amount
        if "drain_random_skill" in outcome:
            lo, hi = outcome["drain_random_skill"]
            amount = lo + int(max(0.0, min(float(rng()), 0.999999999)) * (hi - lo))
            index = min(len(KEBAB_DRAINABLE_SKILLS) - 1, int(max(0.0, min(float(rng()), 0.999999999)) * len(KEBAB_DRAINABLE_SKILLS)))
            skill_id = KEBAB_DRAINABLE_SKILLS[index]
            apply_combat_stat_delta_pure(data, skill_id, -amount)
            drains[skill_id] = amount
    elif spec["kind"] == "beer":
        healed = _consumable_heal(data, _positive_int(spec.get("heal_constitution_ticks", 1), 1) * 10)
        current_strength = _combat_effective_skill_level(data, "strength", 1)
        current_attack = _combat_effective_skill_level(data, "attack", 1)
        str_boost = int(floor(current_strength * float(spec.get("strength_boost_pct", 0.0))))
        atk_drain = int(floor(current_attack * float(spec.get("attack_drain_pct", 0.0))))
        if str_boost > 0:
            apply_combat_stat_delta_pure(data, "strength", str_boost)
            boosts["strength"] = str_boost
        if atk_drain > 0:
            apply_combat_stat_delta_pure(data, "attack", -atk_drain)
            drains["attack"] = atk_drain
    elif spec["kind"] == "potion":
        for skill_id in spec.get("skills", ()):
            base = _combat_base_skill_level(data, skill_id, 1)
            amount = _potion_boost_amount(base, spec.get("strategy", "r"))
            apply_combat_stat_boost_to_pure(data, skill_id, amount)
            boosts[skill_id] = amount
        # Leave the next-lower dose (or an empty Vial at dose 1) in inventory.
        leaves = str(spec.get("leaves", ""))
        if leaves:
            inv = dict(data.get("inventory", {}) or {})
            inv[leaves] = _non_negative_int(inv.get(leaves, 0), 0) + 1
            data["inventory"] = inv

    return data, {
        "allowed": True,
        "item_name": item_name,
        "healed": healed,
        "boosts": boosts,
        "drains": drains,
        "message": message,
    }


def combat_target_preview_pure(player_data, target_id, enemy_data=None, equipment_data=None):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    enemy = enemy_data.get(target_id)
    if enemy is None:
        return {"state": "blocked", "risk_band": "Blocked", "reasons": ("unknown enemy",)}
    equipment_data = equipment_data or {}
    reasons = combat_target_locked_reasons_pure(player_data, target_id, enemy_data, equipment_data=equipment_data)
    if reasons:
        return {"state": "blocked", "risk_band": "Blocked", "reasons": reasons}
    player_totals = equipment_stat_totals_pure(player_data.get("equipment", {}) or {}, equipment_data)
    enemy_totals = _combat_enemy_bonuses(enemy)
    style_id = combat_attack_style_for_equipment_pure(player_data, equipment_data)
    style = COMBAT_ATTACK_STYLE_DATA.get(style_id, COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE])
    combat_class = str(style.get("combat_class", "melee"))
    melee_style_type = (
        _combat_resolve_melee_slot(player_data, equipment_data)["style_type"]
        if combat_class == "melee"
        else None
    )
    spell_id, spell_spec = _combat_selected_magic_spell(player_data)
    if combat_class == "ranged":
        weapon_name, _weapon_equipment, weapon_spec = _combat_ranged_weapon_spec(player_data, equipment_data)
        ammo_name = _combat_selected_ranged_ammo(player_data, weapon_spec, target_id)
        player_attack_roll = _combat_effective_player_ranged_level(player_data, style_id) * (
            _combat_attack_bonus_from_totals(player_totals, "ranged") + 64
        )
    elif combat_class == "magic":
        weapon_name = None
        ammo_name = None
        player_attack_roll = _combat_effective_player_magic_level(player_data) * (
            _combat_attack_bonus_from_totals(player_totals, "magic") + 64
        )
    else:
        weapon_name = None
        ammo_name = None
        player_attack_roll = _combat_effective_player_attack_level(player_data, style_id) * (
            _combat_attack_bonus_from_totals(player_totals, style_type=melee_style_type) + 64
        )
    enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * (
        _combat_defence_bonus_from_totals(enemy_totals, combat_class, style_type=melee_style_type) + 64
    )
    accuracy = _combat_accuracy(player_attack_roll, enemy_defence_roll)
    if combat_class == "ranged":
        player_max_hit = _combat_ranged_max_hit_old_hp(
            _combat_effective_player_ranged_level(player_data, style_id),
            _combat_ranged_strength_bonus(player_totals, ammo_name),
        )
    elif combat_class == "magic":
        player_max_hit = _combat_magic_max_hit_old_hp(spell_spec, player_totals)
    else:
        player_max_hit = _combat_melee_max_hit_old_hp(
            _combat_effective_player_strength_level(player_data, style_id),
            _equipment_bonus_value(player_totals, "melee_strength"),
        )
    enemy_max_hit = _combat_enemy_max_hit_old_hp(
        enemy,
        _positive_int(enemy.get("stats", {}).get("strength", 1), 1) + 8,
        _equipment_bonus_value(enemy_totals, "melee_strength"),
        enemy_totals,
    )
    max_lp = combat_max_lifepoints_pure(player_data)
    current_lp = max(0, min(_positive_int(player_data.get("combat_lifepoints", max_lp), max_lp), max_lp))
    enemy_max_lp_hit = int(enemy_max_hit * 10)
    encounter = player_data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
    loadout = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    bank_inventory = player_data.get("inventory", {}) or {}
    has_food = False
    for item_name in player_data.get("combat_auto_eat_food", _DEFAULT_COMBAT_AUTO_EAT_FOOD):
        if item_name not in COMBAT_FOOD_DATA:
            continue
        loadout_count = _non_negative_int((loadout.get("food", {}) or {}).get(item_name, 0), 0)
        bank_count = 0 if active_encounter else _non_negative_int(bank_inventory.get(item_name, 0), 0)
        if loadout_count + bank_count > 0:
            has_food = True
            break
    if enemy_max_lp_hit <= 0 or current_lp > enemy_max_lp_hit * 3:
        risk = "Safe"
    elif has_food:
        risk = "Food advised"
    else:
        risk = "Death possible"
    poison_damage = _positive_int(enemy.get("poison_damage", 0), 0)
    poison_immunity_ticks = combat_poison_immunity_ticks_pure(player_data)
    poison_lifepoints = 0
    if poison_damage > 0 and poison_immunity_ticks <= 0:
        poison_lifepoints = combat_poison_damage_for_ticks_pure(
            combat_poison_ticks_for_initial_damage_pure(poison_damage)
        )
        if risk == "Safe":
            risk = "Food advised"
    state = "Fighting" if active_encounter else "Ready"
    return {
        "state": state,
        "risk_band": risk,
        "reasons": tuple(),
        "accuracy": accuracy,
        "enemy_max_hit": enemy_max_lp_hit,
        "player_lifepoints": current_lp,
        "player_max_lifepoints": max_lp,
        "enemy_lifepoints": combat_enemy_current_lifepoints_pure(player_data, target_id, enemy_data),
        "enemy_max_lifepoints": _positive_int(enemy.get("stats", {}).get("hitpoints", 0), 0),
        "player_max_hit": int(player_max_hit * 10),
        "ammo": ammo_name or "",
        "spell_id": spell_id if combat_class == "magic" else "",
        "spell": spell_spec.get("display_name", "") if combat_class == "magic" and isinstance(spell_spec, Mapping) else "",
        "runes": dict(spell_spec.get("rune_cost", {}) or {}) if combat_class == "magic" and isinstance(spell_spec, Mapping) else {},
        "weapon": weapon_name or "",
        "poison_damage": poison_lifepoints,
        "poison_chance": COMBAT_POISON_NPC_ATTACK_CHANCE if poison_damage > 0 and poison_immunity_ticks <= 0 else 0.0,
        "poison_immunity_ticks": poison_immunity_ticks,
        "source": enemy.get("source", ""),
    }


def apply_safe_combat_recovery_pure(player_data, equipment_data=None):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    equipment_data = equipment_data or {}
    max_lp = combat_max_lifepoints_pure(data)
    current_lp = _non_negative_int(data.get("combat_lifepoints", max_lp), max_lp)
    rest_reviews = _non_negative_int(data.get("combat_rest_reviews", 0), 0)
    if current_lp > max_lp:
        data["combat_lifepoints"] = max(max_lp, current_lp - SAFE_COMBAT_RECOVERY_LIFEPOINTS)
    elif current_lp < max_lp:
        # Just left combat: heal to full over COMBAT_REST_FULL_HEAL_REVIEWS reviews
        # (a share of the missing LP each review, so the last one tops off). Once
        # that rest window is spent, fall back to the slow natural-regen trickle.
        missing = max_lp - current_lp
        turns_left = COMBAT_REST_FULL_HEAL_REVIEWS - rest_reviews
        if turns_left >= 1:
            heal = -(-missing // turns_left)  # ceil so the final rest review reaches full
        else:
            heal = NATURAL_COMBAT_RECOVERY_LIFEPOINTS
        heal = max(heal, NATURAL_COMBAT_RECOVERY_LIFEPOINTS)
        data["combat_lifepoints"] = min(max_lp, current_lp + heal)
    data["combat_rest_reviews"] = rest_reviews + 1
    _combat_regenerate_special_attack_energy(data, SAFE_COMBAT_RECOVERY_TICKS)
    _combat_recover_current_levels(data, SAFE_COMBAT_RECOVERY_TICKS)
    _combat_consume_antipoison_if_needed(data)
    status_result = _combat_advance_status_effects(data, SAFE_COMBAT_RECOVERY_TICKS)
    if status_result.get("died"):
        _combat_apply_pvm_death(data, max_lp, "combat_poison_death")
        return data
    style = COMBAT_ATTACK_STYLE_DATA.get(
        combat_attack_style_for_equipment_pure(data, equipment_data),
        COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE],
    )
    combat_class = str(style.get("combat_class", "melee"))
    target_id = data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    _weapon_name, _equipment_spec, weapon_spec = _combat_ranged_weapon_spec(data, equipment_data)
    _spell_id, spell_spec = _combat_selected_magic_spell(data)
    bank_run_result = _combat_progress_or_start_bank_run(
        data,
        target_id,
        combat_class,
        weapon_spec,
        spell_spec,
        equipment_data,
    )
    if bank_run_result is not None:
        data["combat_last_result"] = bank_run_result
        return data
    grave = data.get("combat_grave", {}) or {}
    if isinstance(grave, Mapping) and grave.get("items"):
        grave = dict(grave)
        remaining = max(
            0,
            _positive_int(
                grave.get("reviews_remaining", COMBAT_GRAVE_RECOVERY_REVIEWS),
                COMBAT_GRAVE_RECOVERY_REVIEWS,
            )
            - 1,
        )
        grave["reviews_remaining"] = remaining
        if remaining <= 0:
            _combat_reclaim_items_to_player(
                data,
                grave.get("items", ()) or (),
                _combat_stored_loadout(grave),
            )
            data["combat_grave"] = {}
        else:
            data["combat_grave"] = grave
    return data


def combat_death_office_items_pure(player_data):
    return tuple(_combat_death_office_items(player_data.get("death_office", {}) or {}))


def combat_death_office_reclaim_cost_pure(player_data):
    return len(combat_death_office_items_pure(player_data)) * COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM


def combat_death_office_summary_pure(player_data):
    items = combat_death_office_items_pure(player_data)
    cost = len(items) * COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM
    inventory = player_data.get("inventory", {}) or {}
    coins = _non_negative_int(inventory.get("Coins", 0), 0) if isinstance(inventory, Mapping) else 0
    return {
        "items": items,
        "item_count": len(items),
        "reclaim_cost": cost,
        "coins": coins,
        "can_reclaim": bool(items) and coins >= cost,
    }


def reclaim_death_office_items_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    items = _combat_death_office_items(data.get("death_office", {}) or {})
    if not items:
        return player_data, False, "No gear is waiting in Death's Office."
    cost = len(items) * COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM
    inventory = dict(data.get("inventory", {}) or {})
    coins = _non_negative_int(inventory.get("Coins", 0), 0)
    if coins < cost:
        return player_data, False, f"Need {cost} Coins to reclaim this gear."
    inventory["Coins"] = coins - cost
    data["inventory"] = inventory
    _combat_reclaim_items_to_player(
        data,
        items,
        _combat_stored_loadout(data.get("death_office", {}) or {}),
    )
    data["death_office"] = {}
    return data, True, ""


def apply_combat_burst_pure(player_data, enemy_data=None, equipment_data=None, ticks=None, rng=None):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    equipment_data = equipment_data or {}
    rng = rng or (lambda: 0.0)
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data, enemy_data))
    target_id = data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    if target_id not in enemy_data:
        locked_reasons = combat_target_locked_reasons_pure(data, target_id, enemy_data, equipment_data=equipment_data)
        return player_data, False, {"reason": "combat_locked", "locked_reasons": locked_reasons}
    style_id = combat_attack_style_for_equipment_pure(data, equipment_data)
    data["combat_attack_style"] = style_id
    style = COMBAT_ATTACK_STYLE_DATA.get(style_id, COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE])
    combat_class = str(style.get("combat_class", "melee"))
    # melee_style_type feeds the D1 attack/defence-type parity; melee_xp_style_id
    # captures the two-handed-sword aggressive/crush/SHARED xp anomaly (defaults to
    # style_id, so ranged/magic keep their existing xp path unchanged).
    melee_style_type = None
    melee_xp_style_id = style_id
    if combat_class == "melee":
        _melee_slot = _combat_resolve_melee_slot(data, equipment_data)
        melee_style_type = _melee_slot["style_type"]
        melee_xp_style_id = _COMBAT_XP_MODE_TO_STYLE_ID[_melee_slot["xp_mode"]]
    weapon_name, weapon_spec, ranged_weapon_spec = _combat_ranged_weapon_spec(data, equipment_data)
    spell_id, spell_spec = _combat_selected_magic_spell(data)
    locked_reasons = combat_target_locked_reasons_pure(data, target_id, enemy_data, equipment_data=equipment_data)
    bank_run_result = _combat_progress_or_start_bank_run(
        data,
        target_id,
        combat_class,
        ranged_weapon_spec,
        spell_spec,
        equipment_data,
        enemy_data,
    )
    if bank_run_result is not None:
        if not _combat_locks_can_bank_run(locked_reasons):
            return player_data, False, {"reason": "combat_locked", "locked_reasons": locked_reasons}
        data["combat_last_result"] = bank_run_result
        return data, True, bank_run_result
    if locked_reasons:
        return player_data, False, {"reason": "combat_locked", "locked_reasons": locked_reasons}
    enemy = enemy_data[target_id]

    # Auto-drink carried stat potions before the rolls are computed, so the boost
    # flows through the effective-level reads into this burst's max-hit/accuracy.
    stat_potion_events = _combat_auto_drink_potions(data, combat_class)

    max_player_lp = combat_max_lifepoints_pure(data)
    player_lp = max(
        0,
        min(
            _non_negative_int(data.get("combat_lifepoints", max_player_lp), max_player_lp),
            max_player_lp + COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
        ),
    )
    enemy_max_lp = _positive_int(enemy.get("stats", {}).get("hitpoints", 1), 1)
    encounter = data.get("combat_encounter", {}) or {}
    if isinstance(encounter, Mapping) and encounter.get("target_id") == target_id:
        enemy_lp = max(0, min(_positive_int(encounter.get("enemy_lifepoints", enemy_max_lp), enemy_max_lp), enemy_max_lp))
    else:
        enemy_lp = enemy_max_lp

    player_totals = equipment_stat_totals_pure(data.get("equipment", {}) or {}, equipment_data)
    enemy_totals = _combat_enemy_bonuses(enemy)
    player_attack_speed = max(1, _positive_int(_equipment_value(weapon_spec, "attack_speed", 4), 4))
    if combat_class == "ranged":
        player_attack_speed = max(1, player_attack_speed + _signed_int(style.get("attack_speed_delta", 0), 0))
    elif combat_class == "magic":
        player_attack_speed = max(1, _positive_int(spell_spec.get("attack_speed", 5), 5))
    enemy_attack_speed = max(1, _positive_int(enemy.get("attack_speed", 4), 4))

    selected_ammo = None
    if combat_class == "ranged":
        selected_ammo = _combat_selected_ranged_ammo(data, ranged_weapon_spec, target_id)
        player_attack_roll = _combat_effective_player_ranged_level(data, style_id) * (
            _combat_attack_bonus_from_totals(player_totals, "ranged") + 64
        )
        enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * (
            _combat_defence_bonus_from_totals(enemy_totals, "ranged") + 64
        )
        player_max_hit = _combat_ranged_max_hit_old_hp(
            _combat_effective_player_ranged_level(data, style_id),
            _combat_ranged_strength_bonus(player_totals, selected_ammo),
        )
    elif combat_class == "magic":
        player_attack_roll = _combat_effective_player_magic_level(data) * (
            _combat_attack_bonus_from_totals(player_totals, "magic") + 64
        )
        enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * (
            _combat_defence_bonus_from_totals(enemy_totals, "magic") + 64
        )
        player_max_hit = _combat_magic_max_hit_old_hp(spell_spec, player_totals)
    else:
        player_attack_roll = _combat_effective_player_attack_level(data, style_id) * (
            _combat_attack_bonus_from_totals(player_totals, style_type=melee_style_type) + 64
        )
        enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * (
            _combat_defence_bonus_from_totals(enemy_totals, style_type=melee_style_type) + 64
        )
        player_max_hit = _combat_melee_max_hit_old_hp(
            _combat_effective_player_strength_level(data, style_id),
            _equipment_bonus_value(player_totals, "melee_strength"),
        )
    player_accuracy = _combat_accuracy(player_attack_roll, enemy_defence_roll)

    # The enemy attacks with ITS style: a mage's accuracy comes off its magic
    # level + magic attack bonus, and the player resists with magic defence.
    enemy_class = _combat_enemy_attack_class(enemy)
    enemy_attack_stat = {"magic": "magic", "ranged": "ranged"}.get(enemy_class, "attack")
    enemy_attack_roll = (_positive_int(enemy.get("stats", {}).get(enemy_attack_stat, 1), 1) + 8) * (
        _combat_attack_bonus_from_totals(enemy_totals, enemy_class) + 64
    )
    player_defence_roll = _combat_effective_player_defence_level(data, style_id) * (
        _combat_defence_bonus_from_totals(player_totals, enemy_class) + 64
    )
    enemy_accuracy = _combat_accuracy(enemy_attack_roll, player_defence_roll)
    enemy_max_hit = _combat_enemy_max_hit_old_hp(
        enemy,
        _positive_int(enemy.get("stats", {}).get("strength", 1), 1) + 8,
        _equipment_bonus_value(enemy_totals, "melee_strength"),
        enemy_totals,
    )

    total_ticks = max(1, _positive_int(ticks, COMBAT_BURST_TICKS))
    next_player_attack = 0
    next_enemy_attack = enemy_attack_speed
    player_damage = 0
    enemy_damage = 0
    food_used = []
    potions_used = list(stat_potion_events)
    ammo_used = {}
    runes_used = {}
    status_damage = {}
    status_applied = {}
    status_expired = []
    xp_rewards = {}
    drops = {}
    kills = 0
    killed = False
    died = False
    fled = False
    out_of_ammo = False
    out_of_runes = False
    npc_xp_multiplier = _combat_npc_xp_multiplier(enemy)
    ticks_elapsed = 0
    # This is a live combat review, so the out-of-combat rest window restarts from
    # zero; the next non-combat review begins healing you back toward full.
    data["combat_rest_reviews"] = 0

    for tick in range(total_ticks):
        ticks_elapsed = tick + 1
        potion_event = _combat_consume_antipoison_if_needed(data)
        if potion_event:
            potions_used.append(potion_event)
        status_result = _combat_advance_status_effects(data, 1, player_lp, max_player_lp)
        player_lp = _non_negative_int(data.get("combat_lifepoints", player_lp), player_lp)
        for effect_name, amount in (status_result.get("damage", {}) or {}).items():
            status_damage[effect_name] = _non_negative_int(status_damage.get(effect_name, 0), 0) + _non_negative_int(amount, 0)
        status_expired.extend(status_result.get("expired", ()) or ())
        if status_result.get("died"):
            died = True
            break
        if status_result.get("damage"):
            player_lp, food_event = _combat_consume_auto_food(data, player_lp, max_player_lp, rng)
            if food_event:
                food_used.append(food_event)

        if _combat_should_auto_flee(data, player_lp, max_player_lp):
            fled = True
            break

        if tick >= next_player_attack and enemy_lp > 0:
            next_player_attack += player_attack_speed
            if combat_class == "ranged":
                ammo_name = _combat_consume_ranged_ammo(data, ranged_weapon_spec, target_id)
                if ammo_name is None:
                    out_of_ammo = True
                    break
                selected_ammo = ammo_name
                ammo_used[ammo_name] = _non_negative_int(ammo_used.get(ammo_name, 0), 0) + 1
            elif combat_class == "magic":
                used = _combat_consume_magic_runes(data, spell_spec, target_id, equipment_data)
                if used is None:
                    out_of_runes = True
                    break
                for rune_name, amount in used.items():
                    runes_used[rune_name] = _non_negative_int(runes_used.get(rune_name, 0), 0) + amount
            landed = False
            try:
                landed = float(rng()) < player_accuracy
            except (TypeError, ValueError):
                landed = False
            damage = _combat_roll_damage_lifepoints(player_max_hit, rng) if landed else 0
            damage = min(enemy_lp, damage)
            if damage > 0:
                enemy_lp -= damage
                player_damage += damage
            if combat_class == "magic":
                _combat_apply_magic_xp(xp_rewards, spell_spec, damage, npc_xp_multiplier)
            elif damage > 0:
                _combat_apply_xp(xp_rewards, melee_xp_style_id, damage, npc_xp_multiplier)
            if enemy_lp <= 0:
                kills += 1
                killed = True
                kill_drops = _combat_roll_drops(enemy, rng)
                for drop_name, drop_amount in kill_drops.items():
                    drops[drop_name] = _non_negative_int(drops.get(drop_name, 0), 0) + _non_negative_int(drop_amount, 0)
                # Chain into the next spawn of the same target for the remaining
                # tick budget instead of ending the burst on the first kill (the
                # old `break` wasted up to half of a ~30s review window). A fresh
                # enemy respawns at full LP and re-engages after its normal attack
                # delay, so it gets no free instant hit on the kill tick.
                enemy_lp = enemy_max_lp
                next_enemy_attack = tick + 1 + enemy_attack_speed
                continue

        if tick >= next_enemy_attack and enemy_lp > 0:
            next_enemy_attack += enemy_attack_speed
            landed = False
            try:
                landed = float(rng()) < enemy_accuracy
            except (TypeError, ValueError):
                landed = False
            damage = _combat_roll_damage_lifepoints(enemy_max_hit, rng) if landed else 0
            damage = min(player_lp, damage)
            if damage > 0:
                player_lp -= damage
                enemy_damage += damage
            if player_lp <= 0:
                died = True
                break
            player_lp, food_event = _combat_consume_auto_food(data, player_lp, max_player_lp, rng)
            if food_event:
                food_used.append(food_event)
            poison_damage = _positive_int(enemy.get("poison_damage", 0), 0)
            if poison_damage > 0:
                try:
                    poison_roll = float(rng())
                except (TypeError, ValueError):
                    poison_roll = 1.0
                if poison_roll < COMBAT_POISON_NPC_ATTACK_CHANCE:
                    applied, _reason = _combat_apply_poison_effect_to_data(data, poison_damage)
                    if applied:
                        status_applied["poison"] = combat_poison_damage_for_ticks_pure(
                            combat_poison_ticks_for_initial_damage_pure(poison_damage)
                        )
                        potion_event = _combat_consume_antipoison_if_needed(data)
                        if potion_event:
                            potions_used.append(potion_event)

    inventory = data.get("inventory", {}) or {}
    for item_name, amount in drops.items():
        inventory[item_name] = inventory.get(item_name, 0) + amount
    data["inventory"] = inventory

    for exp_key, amount in xp_rewards.items():
        data[exp_key] = data.get(exp_key, 0.0) + amount

    # Chaining means a single burst can defeat several enemies and still end in
    # a partial survivor or a death, so kills, death, and the carried encounter
    # are now independent rather than mutually exclusive branches.
    if kills > 0:
        kill_counts = dict(data.get("combat_kill_counts", {}) or {})
        kill_counts[target_id] = _positive_int(kill_counts.get(target_id, 0), 0) + kills
        data["combat_kill_counts"] = kill_counts

    if died:
        player_lp = _combat_apply_pvm_death(data, max_player_lp)
    elif fled or enemy_lp <= 0 or enemy_lp >= enemy_max_lp:
        # No partial progress to carry: the player fled, nothing was fought, or the
        # burst ended right after a kill respawned a fresh full-LP enemy.
        data["combat_encounter"] = {}
    else:
        data["combat_encounter"] = {"target_id": target_id, "enemy_lifepoints": enemy_lp}

    _combat_regenerate_special_attack_energy(data, ticks_elapsed)
    data["combat_lifepoints"] = player_lp
    result = {
        "reason": "combat_burst",
        "target_id": target_id,
        "display_name": enemy.get("display_name", target_id),
        "ticks": total_ticks,
        "ticks_elapsed": ticks_elapsed,
        "player_damage": player_damage,
        "enemy_damage": enemy_damage,
        "enemy_lifepoints": enemy_lp,
        "player_lifepoints": player_lp,
        "killed": killed,
        "kills": kills,
        "died": died,
        "fled": fled,
        "stop_reason": (
            "out_of_ammo" if out_of_ammo
            else "out_of_runes" if out_of_runes
            else "auto_flee" if fled
            else ""
        ),
        "food_used": tuple(food_used),
        "potions_used": tuple(potions_used),
        "ammo_used": dict(ammo_used),
        "runes_used": dict(runes_used),
        "status_damage": dict(status_damage),
        "status_applied": dict(status_applied),
        "status_expired": tuple(dict.fromkeys(status_expired)),
        "drops": drops,
        "xp_rewards": xp_rewards,
        "player_accuracy": player_accuracy,
        "enemy_accuracy": enemy_accuracy,
        "combat_class": combat_class,
        "weapon": weapon_name or "",
        "ammo": selected_ammo or "",
        "spell_id": spell_id if combat_class == "magic" else "",
        "spell": spell_spec.get("display_name", "") if combat_class == "magic" and isinstance(spell_spec, Mapping) else "",
        "formula_source": (
            RANGED_FORMULA_SOURCE_PATH
            if combat_class == "ranged"
            else MAGIC_FORMULA_SOURCE_PATH
            if combat_class == "magic"
            else MELEE_FORMULA_SOURCE_PATH
        ),
        "xp_source": (
            RANGED_STRATEGY_SOURCE_PATH
            if combat_class == "ranged"
            else MAGIC_STRATEGY_SOURCE_PATH
            if combat_class == "magic"
            else MELEE_STRATEGY_SOURCE_PATH
        ),
    }
    data["combat_last_result"] = result
    return data, True, result


def bank_gear_rows_pure(player_data, pickaxe_data, axe_data, _bonus_item_data):
    """Read-only gear summary the Bank tab renders below the inventory.

    Why surface the *best owned* tool rather than the raw bound toolbelt id:
    the toolbelt is auto-resolved (best_*_pure already picks the strongest
    usable tool from bound ids + bank items), and the owner has decided that
    binding a tool is "basically a formality." Showing the active tool keeps
    the bank honest as the player smiths/loots upgrades, without any equip step.

    Worn equipment now lives in player_data["equipment"]. The Bank frontend still
    uses this read-only summary until the dedicated Equipment tab lands.

    Returns {"toolbelt": [(label, display_name), ...],
             "equipped": [(slot, display_name), ...]}.
    """
    inventory = player_data.get("inventory", {}) or {}
    toolbelt = player_data.get("toolbelt", {}) or {}
    toolbelt_rows: list = []
    pick = best_mining_pickaxe_pure(
        player_data.get("mining_level", 1), inventory, toolbelt, pickaxe_data
    )
    if pick is not None:
        toolbelt_rows.append(("Pickaxe", str(pick.get("display_name", ""))))
    axe = best_woodcutting_axe_pure(
        player_data.get("woodcutting_level", 1), inventory, toolbelt, axe_data
    )
    if axe is not None:
        toolbelt_rows.append(("Hatchet", str(axe.get("display_name", ""))))

    equipped_rows: list = []
    equipment = player_data.get("equipment", {}) or {}
    if isinstance(equipment, Mapping):
        for slot, item_name in equipment.items():
            if isinstance(slot, str) and isinstance(item_name, str):
                equipped_rows.append((slot, item_name))
    return {"toolbelt": toolbelt_rows, "equipped": equipped_rows}


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
    copied["combat_status_effects"] = dict(player_data.get("combat_status_effects", {}) or {})
    copied["combat_recovery_progress"] = dict(player_data.get("combat_recovery_progress", {}) or {})
    copied["combat_bank_run"] = _sanitize_combat_bank_run(player_data.get("combat_bank_run"))
    copied["item_charges"] = dict(player_data.get("item_charges", {}) or {})
    copied["unlocked_abilities"] = list(player_data.get("unlocked_abilities", []) or [])
    return copied


def combat_supply_loadout_summary_pure(player_data):
    loadout = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    return {
        "food_loaded": sum(_non_negative_int(amount, 0) for amount in (loadout.get("food", {}) or {}).values()),
        "potions_loaded": sum(_non_negative_int(amount, 0) for amount in (loadout.get("potions", {}) or {}).values()),
        "potions_loaded_items": dict(loadout.get("potions", {}) or {}),
        "stat_potions_loaded": sum(_non_negative_int(amount, 0) for amount in (loadout.get("stat_potions", {}) or {}).values()),
        "stat_potions_loaded_items": dict(loadout.get("stat_potions", {}) or {}),
        "ammo_loaded": dict(loadout.get("ammo", {}) or {}),
        "runes_loaded": dict(loadout.get("runes", {}) or {}),
        "cannonballs_loaded": _non_negative_int(loadout.get("cannonballs", 0), 0),
    }


def combat_has_active_encounter_pure(player_data):
    encounter = player_data.get("combat_encounter", {}) or {}
    return isinstance(encounter, Mapping) and isinstance(encounter.get("target_id"), str)


def set_combat_pack_mode_pure(player_data, mode):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    data["combat_pack_mode"] = _combat_coerce_pack_mode(mode)
    return data


def set_combat_auto_eat_threshold_pure(player_data, threshold_percent):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    data["combat_auto_eat_threshold_percent"] = max(1, min(_positive_int(threshold_percent, 40), 99))
    return data


def set_combat_auto_eat_food_pure(player_data, food_name):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    if not isinstance(food_name, str) or food_name not in COMBAT_FOOD_DATA:
        return data, False, "unsupported food"
    existing = data.get("combat_auto_eat_food", []) or []
    data["combat_auto_eat_food"] = [food_name] + [
        item_name
        for item_name in existing
        if isinstance(item_name, str) and item_name in COMBAT_FOOD_DATA and item_name != food_name
    ]
    return data, True, ""


def refill_combat_supply_loadout_pure(player_data, equipment_data=None):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    if combat_has_active_encounter_pure(data):
        return data, False, "An active fight cannot refill supplies between review bursts."
    _combat_refill_food_loadout(data)
    _combat_refill_antipoison_loadout(data)
    style = COMBAT_ATTACK_STYLE_DATA.get(
        combat_attack_style_for_equipment_pure(data, equipment_data or {}),
        COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE],
    )
    combat_class = str(style.get("combat_class", "melee"))
    _combat_refill_stat_potions(data, combat_class)
    if combat_class == "ranged":
        _weapon_name, _equipment_spec, weapon_spec = _combat_ranged_weapon_spec(data, equipment_data or {})
        _combat_refill_ranged_ammo_loadout(data, weapon_spec)
    elif combat_class == "magic":
        _spell_id, spell_spec = _combat_selected_magic_spell(data)
        _combat_refill_magic_rune_loadout(data, spell_spec, equipment_data or {})
    return data, True, ""


def unload_combat_supply_loadout_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    if combat_has_active_encounter_pure(data):
        return data, False, "An active fight cannot unload supplies between review bursts."
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    inventory = dict(data.get("inventory", {}) or {})
    for key in ("food", "potions", "stat_potions", "ammo", "runes"):
        for item_name, amount in (loadout.get(key, {}) or {}).items():
            if isinstance(item_name, str):
                inventory[item_name] = _non_negative_int(inventory.get(item_name, 0), 0) + _non_negative_int(amount, 0)
    cannonballs = _non_negative_int(loadout.get("cannonballs", 0), 0)
    if cannonballs > 0:
        inventory["Cannonball"] = _non_negative_int(inventory.get("Cannonball", 0), 0) + cannonballs
    data["inventory"] = inventory
    data["combat_supply_loadout"] = default_combat_supply_loadout_pure()
    return data, True, ""


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


def _implemented_exp_keys():
    return {skill.exp_key for skill in implemented_skill_definitions() if skill.implemented}


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
    if skill is None or not skill.implemented:
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


def _quest_flag_completed(player_data, collection_key, quest_id, flag_id):
    raw_collection = player_data.get(collection_key, {})
    if isinstance(raw_collection, Mapping):
        quest_flags = raw_collection.get(quest_id, ())
        if isinstance(quest_flags, Mapping):
            return bool(quest_flags.get(flag_id, False))
        if isinstance(quest_flags, str):
            return quest_flags == flag_id
        if isinstance(quest_flags, Iterable):
            return flag_id in {flag for flag in quest_flags if isinstance(flag, str)}
    elif isinstance(raw_collection, Iterable) and not isinstance(raw_collection, str):
        return flag_id in {flag for flag in raw_collection if isinstance(flag, str)}
    return False


def _mark_quest_stage_actions(data, quest_id, action_ids):
    actions = tuple(action_id for action_id in action_ids if isinstance(action_id, str) and action_id)
    if not actions:
        return
    raw_collection = data.get("quest_stage_actions", {})
    if not isinstance(raw_collection, Mapping):
        raw_collection = {}
        data["quest_stage_actions"] = raw_collection

    raw_values = raw_collection.get(quest_id, ())
    if isinstance(raw_values, Mapping):
        completed = [action_id for action_id, enabled in raw_values.items() if isinstance(action_id, str) and enabled]
    elif isinstance(raw_values, str):
        completed = [raw_values]
    elif isinstance(raw_values, Iterable):
        completed = [action_id for action_id in raw_values if isinstance(action_id, str)]
    else:
        completed = []

    seen = set(completed)
    for action_id in actions:
        if action_id not in seen:
            completed.append(action_id)
            seen.add(action_id)
    raw_collection[quest_id] = completed


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
    return 1


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
    if state["completed"]:
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


def _quest_combat_total_quantity(encounter):
    return _positive_int(encounter.get("quantity", 1), 1)


def _quest_combat_completed_count(player_data, quest_id, encounter_id, encounter):
    quantity = _quest_combat_total_quantity(encounter)
    if _quest_flag_completed(player_data, "quest_combat_encounters", quest_id, encounter_id):
        return quantity
    raw_counts = player_data.get("quest_combat_encounter_counts", {})
    if not isinstance(raw_counts, Mapping):
        return 0
    quest_counts = raw_counts.get(quest_id, {})
    if not isinstance(quest_counts, Mapping):
        return 0
    return min(quantity, _positive_int(quest_counts.get(encounter_id, 0), 0))


def _quest_combat_remaining_count(player_data, quest_id, encounter_id, encounter):
    quantity = _quest_combat_total_quantity(encounter)
    return max(0, quantity - _quest_combat_completed_count(player_data, quest_id, encounter_id, encounter))


def _has_quest_tool(player_data, tool_name, amount):
    inventory = player_data.get("inventory", {}) or {}
    if inventory.get(tool_name, 0) >= amount:
        return True
    equipment = player_data.get("equipment", {}) or {}
    if isinstance(equipment, Mapping) and tool_name in {str(item_name) for item_name in equipment.values()}:
        return True
    lowered = tool_name.lower()
    toolbelt = player_data.get("toolbelt", {}) or {}
    if lowered == "pickaxe":
        mining_tools = toolbelt.get("mining", ()) if isinstance(toolbelt, Mapping) else ()
        if isinstance(mining_tools, str):
            mining_tools = (mining_tools,)
        if isinstance(mining_tools, Iterable) and any(str(tool) for tool in mining_tools):
            return True
        return any(str(name).lower().endswith("pickaxe") and count >= amount for name, count in inventory.items())
    if lowered in {"hatchet", "axe"}:
        woodcutting_tools = toolbelt.get("woodcutting", ()) if isinstance(toolbelt, Mapping) else ()
        if isinstance(woodcutting_tools, str):
            woodcutting_tools = (woodcutting_tools,)
        if isinstance(woodcutting_tools, Iterable) and any(str(tool) for tool in woodcutting_tools):
            return True
        return any(
            (str(name).lower().endswith("hatchet") or str(name).lower().endswith(" axe")) and count >= amount
            for name, count in inventory.items()
        )
    return False


def _quest_blocker(stage, kind, reason, source="", **extra):
    row = {"stage": stage, "kind": kind, "reason": reason, "source": source}
    row.update(extra)
    return row


def player_combat_level_pure(player_data):
    attack = _positive_int(player_data.get("attack_level", 1), 1)
    defence = _positive_int(player_data.get("defense_level", 1), 1)
    strength = _positive_int(player_data.get("strength_level", 1), 1)
    constitution = _positive_int(player_data.get("constitution_level", 10), 10)
    prayer = _positive_int(player_data.get("prayer_level", 1), 1)
    ranged = _positive_int(player_data.get("ranged_level", 1), 1)
    magic = _positive_int(player_data.get("magic_level", 1), 1)
    summoning = _positive_int(player_data.get("summoning_level", 1), 1)
    base = 0.25 * (defence + constitution + int(prayer * 0.5) + int(summoning * 0.5))
    melee = base + 0.325 * (attack + strength)
    ranged_score = base + 0.325 * (int(ranged * 0.5) + ranged)
    magic_score = base + 0.325 * (int(magic * 0.5) + magic)
    return int(max(melee, ranged_score, magic_score))


# Which skill exp keys each attack style feeds, mirroring _combat_apply_xp /
# _combat_apply_magic_xp so the HUD chips and the Combat stats screen name
# exactly the skills a burst will train. Constitution is always trained on damage
# and is appended separately.
_COMBAT_STYLE_XP_KEYS = {
    "accurate": ("attack_exp",),
    "aggressive": ("strength_exp",),
    "defensive": ("defense_exp",),
    "controlled": ("attack_exp", "strength_exp", "defense_exp"),
    "ranged_accurate": ("ranged_exp",),
    "ranged_rapid": ("ranged_exp",),
    "ranged_longrange": ("ranged_exp", "defense_exp"),
    "magic_standard": ("magic_exp",),
}

_COMBAT_EXP_KEY_DISPLAY = {
    "attack_exp": "Attack",
    "strength_exp": "Strength",
    "defense_exp": "Defence",
    "ranged_exp": "Ranged",
    "magic_exp": "Magic",
    "constitution_exp": "Constitution",
}


def combat_attack_style_trained_skills_pure(style_id):
    """Display names of the skills a given attack style trains, Constitution last."""
    keys = _COMBAT_STYLE_XP_KEYS.get(style_id, _COMBAT_STYLE_XP_KEYS[DEFAULT_COMBAT_ATTACK_STYLE])
    ordered = list(keys) + ["constitution_exp"]
    return tuple(_COMBAT_EXP_KEY_DISPLAY[key] for key in ordered)


def combat_weapon_style_options_pure(player_data, equipment_data=None):
    """UI-ready attack-style options for the equipped weapon (D2 per-weapon slots).

    For a melee weapon this is one row per AttackStyleData slot, each carrying the
    weapon_style and style_type to persist, a display name that names the attack
    type (e.g. "Aggressive (Crush)"), the skills it actually trains, and whether it
    is the current selection. Ranged/magic keep the class-filtered
    COMBAT_ATTACK_STYLE_DATA rows with a fixed "auto" style_type. Each row is
    ``{weapon_style, style_type, display_name, trained_skills, is_current}``."""
    if _combat_weapon_is_ranged(player_data, equipment_data) or _combat_weapon_is_magic(player_data, equipment_data):
        current = combat_attack_style_for_equipment_pure(player_data, equipment_data)
        combat_class = str(COMBAT_ATTACK_STYLE_DATA.get(current, {}).get("combat_class", "ranged"))
        return [
            {
                "weapon_style": sid,
                "style_type": "auto",
                "display_name": str(spec.get("display_name", sid)),
                "trained_skills": combat_attack_style_trained_skills_pure(sid),
                "is_current": sid == current,
            }
            for sid, spec in COMBAT_ATTACK_STYLE_DATA.items()
            if str(spec.get("combat_class")) == combat_class
        ]
    slots = combat_weapon_attack_style_slots_pure(player_data, equipment_data)
    current_slot = _combat_resolve_melee_slot(player_data, equipment_data)
    return [
        {
            "weapon_style": slot["weapon_style"],
            "style_type": slot["style_type"],
            "display_name": f"{slot['weapon_style'].title()} ({slot['style_type'].title()})",
            "trained_skills": combat_attack_style_trained_skills_pure(
                _COMBAT_XP_MODE_TO_STYLE_ID[slot["xp_mode"]]
            ),
            "is_current": slot is current_slot,
        }
        for slot in slots
    ]


def combat_hud_state_pure(player_data, enemy_data=None, equipment_data=None):
    """Structured view the combat HUD renders: player and enemy health bars, the
    skills the current attack style trains (the XP chips), and the running kill
    count. Kept pure so the Qt widget stays a thin renderer."""
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    max_lp = combat_max_lifepoints_pure(player_data)
    current_lp = max(0, min(_non_negative_int(player_data.get("combat_lifepoints", max_lp), max_lp), max_lp))

    target_id = player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    enemy = enemy_data.get(target_id) if isinstance(target_id, str) else None
    if isinstance(enemy, Mapping):
        enemy_name = str(enemy.get("display_name", target_id))
        enemy_max_lp = _positive_int(enemy.get("stats", {}).get("hitpoints", 1), 1)
    else:
        enemy_name = "Enemy"
        enemy_max_lp = 0
    encounter = player_data.get("combat_encounter", {}) or {}
    carried = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id and enemy_max_lp > 0
    if carried:
        enemy_lp = max(0, min(_positive_int(encounter.get("enemy_lifepoints", enemy_max_lp), enemy_max_lp), enemy_max_lp))
    else:
        enemy_lp = enemy_max_lp

    style_id = combat_attack_style_for_equipment_pure(player_data, equipment_data)
    style = COMBAT_ATTACK_STYLE_DATA.get(style_id, {})
    # xp_style_id captures the two-handed-sword aggressive/crush/SHARED anomaly so
    # the XP chips name the skills actually trained, not what weapon_style implies.
    _melee_style_type, xp_style_id = combat_melee_attack_type_pure(player_data, equipment_data)

    kills_total = _non_negative_int((player_data.get("combat_kill_counts", {}) or {}).get(target_id, 0), 0)
    last = player_data.get("combat_last_result", {}) or {}
    last = last if isinstance(last, Mapping) else {}
    last_kills = _non_negative_int(last.get("kills", 0), 0)
    if last.get("died"):
        last_outcome = "died"
    elif last.get("fled"):
        last_outcome = "fled"
    else:
        last_outcome = ""

    def _pct(value, ceiling):
        return int((min(value, ceiling) / ceiling) * 100) if ceiling > 0 else 0

    return {
        "combat_level": player_combat_level_pure(player_data),
        "player_lifepoints": current_lp,
        "player_max_lifepoints": max_lp,
        "player_pct": _pct(current_lp, max_lp),
        "enemy_name": enemy_name,
        "enemy_lifepoints": enemy_lp,
        "enemy_max_lifepoints": enemy_max_lp,
        "enemy_pct": _pct(enemy_lp, enemy_max_lp),
        "enemy_carried": bool(carried),
        "attack_style_id": style_id,
        "attack_style_name": str(style.get("display_name", style_id)),
        "trained_skills": combat_attack_style_trained_skills_pure(xp_style_id),
        "kills_total": kills_total,
        "last_kills": last_kills,
        "last_outcome": last_outcome,
        "status": combat_status_summary_pure(player_data),
    }


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
    if all(_positive_int(stats.get(key, 0), 0) > 0 for key in _quest_combat_required_stat_keys(encounter)):
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


def _quest_combat_enemy_spec(quest_id, encounter_id, encounter):
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
    display_name, level, _quantity, _level_text, _quantity_text, source = _quest_combat_display(encounter)
    enemy = {
        "display_name": display_name,
        "level": level,
        "stats": stats,
        "bonuses": _quest_combat_normalized_bonuses(encounter),
        "drops": {"guaranteed": (), "tables": ()},
        "source": source,
        "quest_id": quest_id,
        "quest_encounter_id": encounter_id,
        "attack_style": attack_style or "melee",
        "attack_speed": _positive_int(configs.get("attack_speed", 4), 4),
    }
    max_hit = _positive_int(configs.get("max_hit", 0), 0)
    if max_hit > 0:
        enemy["max_hit"] = max_hit
    return enemy


def _quest_combat_default_rng():
    return lambda: 0.5


def quest_combat_encounter_ready_pure(player_data, encounter):
    if not quest_combat_resolver_enabled_pure(player_data):
        return False, "combat_locked"
    if not quest_combat_encounter_has_stats_pure(encounter):
        return False, "combat_missing_stats"
    encounter_level = _positive_int(encounter.get("level", 0), 0)
    player_level = player_combat_level_pure(player_data)
    if encounter_level > 0 and player_level < encounter_level:
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


def _quest_requirement_blockers(player_data, quest_id, requirement):
    stage = _positive_int(requirement.get("stage", 0), 0)
    source = str(requirement.get("source", ""))
    inventory = player_data.get("inventory", {}) or {}
    blockers = []

    required_items = {}
    for item_name, amount in (
        _quest_stage_item_pairs(requirement, "required_inventory")
        + _quest_stage_item_pairs(requirement, "consumed_inventory")
    ):
        required_items[item_name] = max(required_items.get(item_name, 0), amount)
    for item_name, amount in required_items.items():
        owned = _positive_int(inventory.get(item_name, 0), 0)
        if owned < amount:
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
        if not _quest_flag_completed(player_data, "quest_stage_actions", quest_id, action_id):
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
        if not quest_combat_resolver_enabled_pure(player_data):
            blockers.append(
                _quest_blocker(
                    stage,
                    "combat_locked",
                    f"Combat locked until battle support is enabled: {display_name}{level_text}{remaining_quantity_text}",
                    encounter_source,
                    encounter_id=encounter_id,
                    display_name=display_name,
                    level=level,
                    quantity=remaining_quantity,
                    total_quantity=quantity,
                    completed_quantity=completed_quantity,
                    remaining_quantity=remaining_quantity,
                )
            )
            continue
        if not quest_combat_encounter_has_stats_pure(encounter):
            blockers.append(
                _quest_blocker(
                    stage,
                    "combat_missing_stats",
                    f"Combat stats required before battle support can resolve: {display_name}{level_text}{remaining_quantity_text}",
                    encounter_source,
                    encounter_id=encounter_id,
                    display_name=display_name,
                    level=level,
                    quantity=remaining_quantity,
                    total_quantity=quantity,
                    completed_quantity=completed_quantity,
                    remaining_quantity=remaining_quantity,
                )
            )
            continue
        player_level = player_combat_level_pure(player_data)
        if level > 0 and player_level < level:
            blockers.append(
                _quest_blocker(
                    stage,
                    "combat_underpowered",
                    f"Requires combat level {level} for battle: {display_name}{level_text}{remaining_quantity_text}",
                    encounter_source,
                    encounter_id=encounter_id,
                    display_name=display_name,
                    level=level,
                    quantity=remaining_quantity,
                    total_quantity=quantity,
                    completed_quantity=completed_quantity,
                    remaining_quantity=remaining_quantity,
                    player_combat_level=player_level,
                )
            )
            continue
        blockers.append(
            _quest_blocker(
                stage,
                "combat_encounter",
                f"Battle required: {display_name}{level_text}{remaining_quantity_text}",
                encounter_source,
                encounter_id=encounter_id,
                display_name=display_name,
                level=level,
                quantity=remaining_quantity,
                total_quantity=quantity,
                completed_quantity=completed_quantity,
                remaining_quantity=remaining_quantity,
            )
        )
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
    "missing_tool",
    "required_action",
    "unmet_route",
    "quest_choice",
}

_QUEST_COMBAT_PREREQUISITE_BLOCKER_KINDS = {
    "missing_item",
    "missing_item_option",
    "missing_tool",
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


def ability_unlocked_pure(player_data, ability_id):
    abilities = player_data.get("unlocked_abilities", ())
    if isinstance(abilities, str):
        return abilities == ability_id
    if isinstance(abilities, Iterable):
        return ability_id in {ability for ability in abilities if isinstance(ability, str)}
    return False


def _target_ids_for_unlock_rule(rule):
    target_ids = rule.get("target_ids", ())
    if isinstance(target_ids, str):
        return {target_ids}
    if isinstance(target_ids, Iterable):
        return {item for item in target_ids if isinstance(item, str)}
    return set()


def _requirements_for_unlock_rule(rule):
    requirements = rule.get("requirements")
    if isinstance(requirements, Mapping):
        return (requirements,)
    if isinstance(requirements, Iterable) and not isinstance(requirements, str):
        return tuple(requirement for requirement in requirements if isinstance(requirement, Mapping))
    quest_id = rule.get("quest_id")
    if isinstance(quest_id, str):
        return (
            {
                "kind": "quest_completed",
                "quest_id": quest_id,
                "reason": rule.get("reason") or quest_id.replace("_", " ").title(),
                "source": rule.get("source", ""),
            },
        )
    return tuple()


def target_unlock_locked_reasons_pure(player_data, skill_id, target_id, target_unlock_rules):
    reasons = []
    for rule in target_unlock_rules or ():
        if not isinstance(rule, Mapping):
            continue
        if rule.get("gate_kind", "target") != "target":
            continue
        if rule.get("skill_id") != skill_id:
            continue
        if target_id not in _target_ids_for_unlock_rule(rule):
            continue
        for requirement in _requirements_for_unlock_rule(rule):
            kind = requirement.get("kind", "quest_completed")
            if kind == "quest_completed":
                quest_id = requirement.get("quest_id")
                if not isinstance(quest_id, str) or quest_completed_pure(player_data, quest_id):
                    continue
                reason = requirement.get("reason") or quest_id.replace("_", " ").title()
                reasons.append(str(reason))
            elif kind == "ability_unlocked":
                ability_id = requirement.get("ability_id")
                if not isinstance(ability_id, str) or ability_unlocked_pure(player_data, ability_id):
                    continue
                reason = requirement.get("reason") or ability_id.replace("_", " ").title()
                reasons.append(str(reason))
    return tuple(dict.fromkeys(reasons))


def quest_unlock_locked_reasons_pure(player_data, skill_id, target_id, quest_unlock_rules):
    return target_unlock_locked_reasons_pure(player_data, skill_id, target_id, quest_unlock_rules)


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
    return bool(quest_current_stage_resolvable_combat_blockers_pure(player_data, quest_id, quest_data))


def start_quest_pure(player_data, quest_id, quest_data):
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
    data["current_quest"] = quest_id
    return data, True


def _consume_quest_current_stage_items(data, quest_id, quest):
    inventory = data["inventory"]
    requirements, blockers = _quest_current_stage_selected_requirements(data, quest_id, {quest_id: quest})
    if blockers:
        return
    for requirement in requirements:
        _mark_quest_stage_actions(data, quest_id, _quest_stage_strings(requirement, "auto_actions"))
        for item_name, amount in _quest_stage_item_pairs(requirement, "consumed_inventory"):
            inventory[item_name] = max(0, _positive_int(inventory.get(item_name, 0), 0) - amount)
        for options in _quest_stage_item_option_groups(requirement, "consumed_inventory_options"):
            for item_name, amount in options:
                if _positive_int(inventory.get(item_name, 0), 0) >= amount:
                    inventory[item_name] = max(0, _positive_int(inventory.get(item_name, 0), 0) - amount)
                    break
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


def apply_quest_combat_encounter_pure(player_data, quest_id, quest_data, encounter_id=None, ticks=None, rng=None, equipment_data=None):
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
    encounter = _quest_current_stage_encounter_by_id(player_data, quest_id, quest_data, encounter_id)
    if encounter is None:
        return player_data, False, {"reason": "encounter_not_current_stage"}
    ready, reason = quest_combat_encounter_ready_pure(player_data, encounter)
    if not ready:
        return player_data, False, {"reason": reason}
    quantity = _quest_combat_total_quantity(encounter)
    completed_quantity = _quest_combat_completed_count(player_data, quest_id, encounter_id, encounter)
    if completed_quantity >= quantity:
        return player_data, False, {"reason": "combat_already_resolved"}

    quest_target_id = _quest_combat_target_id(quest_id, encounter_id)
    quest_enemy_data = {quest_target_id: _quest_combat_enemy_spec(quest_id, encounter_id, encounter)}
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
    # Quest battles are deliberate, story-gating fights: they resolve to a kill or
    # a death rather than silently auto-fleeing out of the encounter (which would
    # soft-lock quest progress). Auto-flee stays scoped to the regular combat loop.
    combat_player_data["combat_auto_flee"] = False
    if saved_lifepoints > 0:
        combat_player_data["combat_encounter"] = {
            "target_id": quest_target_id,
            "enemy_lifepoints": saved_lifepoints,
        }
    else:
        combat_player_data["combat_encounter"] = {}
    combat_rng = rng if rng is not None else _quest_combat_default_rng()
    combat_ticks = ticks if ticks is not None else QUEST_COMBAT_DEFAULT_BURST_TICKS
    data, combat_ok, combat_result = apply_combat_burst_pure(
        combat_player_data,
        quest_enemy_data,
        equipment_data or {},
        ticks=combat_ticks,
        rng=combat_rng,
    )
    if not combat_ok:
        return player_data, False, combat_result

    data["current_combat_target"] = original_combat_target
    data["combat_encounter"] = {} if combat_result.get("died") else original_combat_encounter
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

    if combat_result.get("killed"):
        quest_active.pop(encounter_id, None)
    elif combat_result.get("died"):
        quest_active.pop(encounter_id, None)
    else:
        enemy_lifepoints = _non_negative_int(combat_result.get("enemy_lifepoints", 0), 0)
        if enemy_lifepoints > 0:
            quest_active[encounter_id] = enemy_lifepoints

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


def apply_quest_progress_pure(player_data, quest_id, quest_data):
    data, ok = start_quest_pure(player_data, quest_id, quest_data)
    if not ok:
        return player_data, False, False
    quest = quest_data[quest_id]
    state = quest_state_pure(data, quest_id)
    if state["completed"]:
        return data, False, False
    if quest_current_stage_blockers_pure(data, quest_id, quest_data):
        return player_data, False, False
    current_stage = quest_current_stage_pure(data, quest_id, quest_data)
    _consume_quest_current_stage_items(data, quest_id, quest)
    total_stages = _positive_int(quest.get("stages", 1), 1)
    state["progress"] = min(total_stages, current_stage + 1)
    completed_now = state["progress"] >= total_stages
    if completed_now:
        state["completed"] = True
        data["quest_points"] = max(0, _positive_int(data.get("quest_points", 0), 0)) + _positive_int(quest.get("point_reward", 0), 0)
        inventory = data["inventory"]
        for item_name, amount in (quest.get("rewards", {}) or {}).items():
            inventory[item_name] = inventory.get(item_name, 0) + _positive_int(amount, 1)
        _apply_quest_xp_rewards(data, quest)
    data.setdefault("quests", {})[quest_id] = state
    return data, True, completed_now


def _apply_quest_xp_rewards(data, quest):
    implemented_exp_keys = _implemented_exp_keys()
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
        if exp_key in implemented_exp_keys and skill is not None and skill.implemented:
            data[exp_key] = data.get(exp_key, 0) + amount
        else:
            clean_pending[exp_key] = float(clean_pending.get(exp_key, 0) or 0) + amount
    data["pending_skill_exp_rewards"] = {
        key: value for key, value in clean_pending.items() if value > 0
    }


def _apply_skill_xp_reward(data, skill_id, amount):
    skill = get_skill(skill_id)
    exp_key = skill.exp_key if skill is not None else f"{skill_id}_exp"
    implemented_exp_keys = _implemented_exp_keys()
    if exp_key in implemented_exp_keys and skill is not None and skill.implemented:
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
                "lines": tuple(journal_stages.get(stage, ())),
                "completed": state["completed"] or stage < progress,
                "current": (not state["completed"] and stage == progress),
            }
        )
    return tuple(rows)


def claim_locked_reasons_pure(player_data, claim_id, claim_data):
    claim = claim_data.get(claim_id)
    if not claim:
        return ("unknown claim",)
    state = (player_data.get("claims", {}) or {}).get(claim_id, {})
    if isinstance(state, Mapping) and state.get("claimed"):
        return ("claimed",)
    reasons = []
    required_quest = claim.get("required_quest")
    if required_quest and not quest_completed_pure(player_data, str(required_quest)):
        reasons.append("quest")
    required_level = _positive_int(claim.get("required_runecrafting_level", 1), 1)
    if required_level > 1 and _positive_int(player_data.get("runecrafting_level", 1), 1) < required_level:
        reasons.append(f"Runecrafting level {required_level}")
    return tuple(reasons)


def _claim_bundle_items(claim):
    raw_items = claim.get("items", ()) if isinstance(claim, Mapping) else ()
    if isinstance(raw_items, Mapping):
        candidates = raw_items.items()
    elif isinstance(raw_items, Iterable) and not isinstance(raw_items, (str, bytes)):
        candidates = raw_items
    else:
        candidates = ()
    items = []
    for raw_item in candidates:
        if isinstance(raw_item, Mapping):
            name = raw_item.get("item_name", raw_item.get("item"))
            quantity = raw_item.get("quantity", raw_item.get("amount", 1))
        elif isinstance(raw_item, (tuple, list)) and len(raw_item) >= 2:
            name, quantity = raw_item[0], raw_item[1]
        else:
            continue
        if not isinstance(name, str) or not name:
            continue
        quantity = _positive_int(quantity, 0)
        if quantity <= 0:
            continue
        items.append((name, quantity))
    return tuple(items)


def claim_rows_pure(player_data, claim_data):
    rows = []
    for claim_id, claim in claim_data.items():
        reasons = claim_locked_reasons_pure(player_data, claim_id, claim_data)
        claimed = reasons == ("claimed",)
        eligible = not reasons
        items = _claim_bundle_items(claim)
        rows.append(
            {
                "claim_id": claim_id,
                "display_name": claim.get("display_name", claim_id),
                "claim_type": claim.get("claim_type", "item"),
                "item_name": claim.get("item_name", claim_id),
                "quantity": _positive_int(claim.get("quantity", 1), 1),
                "items": items,
                "xp_amount": float(claim.get("xp_amount", 0) or 0),
                "skill_options": tuple(claim.get("skill_options", ()) or ()),
                "minimum_level": _positive_int(claim.get("minimum_level", 1), 1),
                "eligible": eligible,
                "claimed": claimed,
                "locked_reasons": reasons,
            }
        )
    return tuple(rows)


def _skill_level_for_reward(player_data, skill_id):
    skill = get_skill(skill_id)
    level_key = skill.level_key if skill is not None else f"{skill_id}_level"
    return _positive_int(player_data.get(level_key, 1), 1)


def apply_claim_pure(player_data, claim_id, claim_data, selected_skill_id=None):
    if claim_locked_reasons_pure(player_data, claim_id, claim_data):
        return player_data, False
    claim = claim_data.get(claim_id)
    if not claim:
        return player_data, False
    data = _copy_player_data_with_nested(player_data)
    claim_type = str(claim.get("claim_type", "item"))
    if claim_type == "xp_lamp":
        skill_id = selected_skill_id
        if not isinstance(skill_id, str):
            return player_data, False
        skill_options = tuple(claim.get("skill_options", ()) or ())
        if skill_options and skill_id not in skill_options:
            return player_data, False
        minimum_level = _positive_int(claim.get("minimum_level", 1), 1)
        if _skill_level_for_reward(player_data, skill_id) < minimum_level:
            return player_data, False
        amount = float(claim.get("xp_amount", 0) or 0)
        if amount <= 0:
            return player_data, False
        _apply_skill_xp_reward(data, skill_id, amount)
    elif claim_type == "item_bundle":
        bundle_items = _claim_bundle_items(claim)
        if not bundle_items:
            return player_data, False
        inventory = data.setdefault("inventory", {})
        for item_name, quantity in bundle_items:
            inventory[item_name] = inventory.get(item_name, 0) + quantity
    else:
        item_name = str(claim.get("item_name", claim_id))
        quantity = _positive_int(claim.get("quantity", 1), 1)
        data["inventory"][item_name] = data["inventory"].get(item_name, 0) + quantity
    data.setdefault("claims", {}).setdefault(claim_id, {})["claimed"] = True
    return data, True


def _altar_for_target(target, runecrafting_data):
    altar_id = target.get("altar_id")
    for candidate in runecrafting_data.values():
        if candidate.get("kind") == "standard" and candidate.get("altar_id") == altar_id:
            return candidate
    return None


def runecrafting_unlocked_pure(player_data):
    return quest_completed_pure(player_data, "rune_mysteries")


def _fed_altars(player_data):
    hood = player_data.get("wicked_hood", {}) or {}
    raw = hood.get("fed_altars", ()) if isinstance(hood, Mapping) else ()
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, Iterable):
        return {altar for altar in raw if isinstance(altar, str)}
    return set()


def _altar_access_item_names(altar_id, runecrafting_data):
    talisman = None
    tiara = None
    for target in runecrafting_data.values():
        if target.get("kind") == "tiara" and target.get("altar_id") == altar_id:
            talisman = target.get("talisman_item")
            tiara = target.get("output_item")
            break
    if talisman is None:
        standard = _altar_for_target({"altar_id": altar_id}, runecrafting_data)
        if standard:
            rune_item = str(standard.get("output_item", "")).replace(" rune", "")
            talisman = f"{rune_item} talisman" if rune_item else None
            tiara = f"{rune_item} tiara" if rune_item else None
    return talisman, tiara


def runecrafting_altar_access_source_pure(player_data, altar_id, runecrafting_data):
    inventory = player_data.get("inventory", {}) or {}
    equipment = player_data.get("equipment", {}) or {}
    talisman_item, tiara_item = _altar_access_item_names(altar_id, runecrafting_data)
    if tiara_item and equipment.get("head") == tiara_item:
        return "tiara"
    if altar_id in _fed_altars(player_data):
        return "hood"
    if talisman_item and inventory.get(talisman_item, 0) > 0:
        return "talisman"
    return ""


def runecrafting_standard_base_capacity_pure(player_data, target, runecrafting_data):
    source = runecrafting_altar_access_source_pure(player_data, target.get("altar_id"), runecrafting_data)
    if source in {"tiara", "hood"}:
        return 28
    if source == "talisman":
        return 27
    return 0


def _pouch_capacity_after_degradation(pouch, degradation):
    threshold = pouch.get("degradation_threshold")
    capacity = _positive_int(pouch.get("capacity", 0), 0)
    if threshold is None:
        return capacity
    try:
        threshold_int = int(threshold)
    except (TypeError, ValueError):
        threshold_int = 0
    loss = max(0, int(degradation) - threshold_int)
    return max(0, capacity - loss)


def _repair_degraded_pouches(data, pouch_data):
    inventory = data["inventory"]
    pouch_state = data.setdefault("runecrafting_pouches", {})
    for pouch_id, pouch in pouch_data.items():
        degraded_item = pouch.get("degraded_item")
        display_name = pouch.get("display_name")
        if degraded_item and display_name and inventory.get(degraded_item, 0) > 0:
            count = inventory.get(degraded_item, 0)
            inventory[degraded_item] = 0
            inventory[display_name] = inventory.get(display_name, 0) + count
            pouch_state[pouch_id] = {"degradation": 0}


def runecrafting_pouch_capacity_pure(player_data, pouch_data):
    level = _positive_int(player_data.get("runecrafting_level", 1), 1)
    inventory = player_data.get("inventory", {}) or {}
    pouch_state = player_data.get("runecrafting_pouches", {}) or {}
    total = 0
    for pouch_id, pouch in pouch_data.items():
        display_name = pouch.get("display_name")
        if not display_name or inventory.get(display_name, 0) <= 0:
            continue
        if level < _positive_int(pouch.get("required_level", 1), 1):
            continue
        state = pouch_state.get(pouch_id, {}) if isinstance(pouch_state, Mapping) else {}
        degradation = _positive_int(state.get("degradation", 0), 0) if isinstance(state, Mapping) else 0
        total += _pouch_capacity_after_degradation(pouch, degradation)
    return total


def _degrade_used_pouches(data, pouch_data, extra_essence_used):
    level = _positive_int(data.get("runecrafting_level", 1), 1)
    inventory = data["inventory"]
    pouch_state = data.setdefault("runecrafting_pouches", {})
    remaining_extra = max(0, int(extra_essence_used))
    for pouch_id, pouch in pouch_data.items():
        if remaining_extra <= 0:
            break
        display_name = pouch.get("display_name")
        if not display_name or inventory.get(display_name, 0) <= 0:
            continue
        if level < _positive_int(pouch.get("required_level", 1), 1):
            continue
        state = pouch_state.setdefault(pouch_id, {"degradation": 0})
        degradation_before = _positive_int(state.get("degradation", 0), 0)
        capacity_before = _pouch_capacity_after_degradation(pouch, degradation_before)
        if capacity_before <= 0:
            continue
        remaining_extra -= min(remaining_extra, capacity_before)
        threshold = pouch.get("degradation_threshold")
        if threshold is None:
            continue
        degradation = degradation_before + 1
        state["degradation"] = degradation
        if _pouch_capacity_after_degradation(pouch, degradation) <= 0 and pouch.get("degraded_item"):
            inventory[display_name] = max(0, inventory.get(display_name, 0) - 1)
            degraded_item = str(pouch["degraded_item"])
            inventory[degraded_item] = inventory.get(degraded_item, 0) + 1
            state["degradation"] = 0


def _available_essence_count(inventory, essence_items):
    return sum(_positive_int(inventory.get(item, 0), 0) for item in essence_items)


def _consume_essence_ordered(inventory, essence_items, amount):
    remaining = amount
    consumed = {}
    for item in essence_items:
        if remaining <= 0:
            break
        take = min(remaining, _positive_int(inventory.get(item, 0), 0))
        if take > 0:
            inventory[item] = inventory.get(item, 0) - take
            consumed[item] = take
            remaining -= take
    return amount - remaining, consumed


def _runecrafting_multiplier_info(target, level):
    output_item = str(target.get("output_item", ""))
    divisors = {
        "Air rune": 11,
        "Mind rune": 14,
        "Water rune": 19,
        "Earth rune": 26,
        "Fire rune": 35,
        "Body rune": 46,
        "Cosmic rune": 59,
        "Chaos rune": 74,
        "Nature rune": 91,
    }
    divisor = divisors.get(output_item)
    if divisor is None:
        return 1, 0.0, 1
    base = int(level) // divisor + 1
    max_base = 99 // divisor + 1
    if base >= max_base:
        return base, 0.0, max_base
    current_start = divisor * (base - 1)
    next_start = divisor * base
    span = max(1, next_start - current_start)
    chance = max(0.0, min(((float(level) - current_start) / span) * 0.60, 0.60))
    return base, chance, max_base


def _standard_output_count(target, level, essence_used, rolls):
    base, chance, max_base = _runecrafting_multiplier_info(target, level)
    if base >= max_base or chance <= 0:
        return base * essence_used
    total = 0
    roll_iter = iter(rolls or ())
    for _ in range(essence_used):
        try:
            roll = float(next(roll_iter))
        except (StopIteration, TypeError, ValueError):
            roll = 1.0
        total += base + 1 if roll < chance else base
    return total


def binding_necklace_charges_pure(player_data):
    if (player_data.get("equipment", {}) or {}).get("neck") != "Binding necklace":
        return 0
    charges = (player_data.get("item_charges", {}) or {}).get("Binding necklace")
    if charges is None:
        return 15
    return max(0, _positive_int(charges, 0))


def runecrafting_locked_reasons_pure(player_data, target_id, runecrafting_data, pouch_data, quest_unlock_rules=()):
    target = runecrafting_data.get(target_id)
    if not target:
        return ("unknown target",)
    reasons = []
    if not runecrafting_unlocked_pure(player_data):
        reasons.append("Rune Mysteries")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "runecrafting",
            target_id,
            quest_unlock_rules,
        )
    )
    level = _positive_int(player_data.get("runecrafting_level", 1), 1)
    required_level = _positive_int(target.get("level", 1), 1)
    if level < required_level:
        reasons.append(f"Runecrafting level {required_level}")
    inventory = player_data.get("inventory", {}) or {}
    kind = target.get("kind")
    if kind == "standard":
        if runecrafting_standard_base_capacity_pure(player_data, target, runecrafting_data) <= 0:
            reasons.append("altar access")
        if _available_essence_count(inventory, tuple(target.get("essence_items", ()))) <= 0:
            reasons.append("essence")
    elif kind == "combination":
        if runecrafting_altar_access_source_pure(player_data, target.get("altar_id"), runecrafting_data) == "":
            reasons.append("altar access")
        for item_name in ("Pure essence", target.get("component_rune"), target.get("consumed_talisman")):
            if item_name and inventory.get(item_name, 0) <= 0:
                reasons.append(str(item_name))
    elif kind == "tiara":
        for item_name in ("Tiara", target.get("talisman_item")):
            if item_name and inventory.get(item_name, 0) <= 0:
                reasons.append(str(item_name))
    elif kind == "hood_feed":
        equipment = player_data.get("equipment", {}) or {}
        has_hood = inventory.get("Wicked hood", 0) > 0 or equipment.get("head") == "Wicked hood"
        if not has_hood:
            reasons.append("Wicked hood")
        if target.get("altar_id") in _fed_altars(player_data):
            reasons.append("already fed")
        input_item = target.get("input_item")
        if input_item and inventory.get(input_item, 0) <= 0:
            reasons.append(str(input_item))
    return tuple(dict.fromkeys(reasons))


def can_runecraft_target_pure(player_data, target_id, runecrafting_data, pouch_data, quest_unlock_rules=()):
    return not runecrafting_locked_reasons_pure(
        player_data,
        target_id,
        runecrafting_data,
        pouch_data,
        quest_unlock_rules,
    )


def can_runecraft_any_pure(player_data, runecrafting_data, pouch_data, quest_unlock_rules=()):
    return any(
        can_runecraft_target_pure(
            player_data,
            target_id,
            runecrafting_data,
            pouch_data,
            quest_unlock_rules,
        )
        for target_id in runecrafting_data
    )


def apply_runecrafting_action_pure(player_data, target_id, runecrafting_data, pouch_data, rolls=(), quest_unlock_rules=()):
    target = runecrafting_data.get(target_id)
    if not target:
        return player_data, 0, False, "Unknown Runecrafting target"
    locked_reasons = runecrafting_locked_reasons_pure(
        player_data,
        target_id,
        runecrafting_data,
        pouch_data,
        quest_unlock_rules,
    )
    if locked_reasons:
        return player_data, 0, False, "Runecrafting target is locked: " + ", ".join(locked_reasons)

    data = _copy_player_data_with_nested(player_data)
    _repair_degraded_pouches(data, pouch_data)
    inventory = data["inventory"]
    level = _positive_int(data.get("runecrafting_level", 1), 1)
    kind = target.get("kind")
    roll_iter = iter(rolls or ())

    if kind == "standard":
        base_capacity = runecrafting_standard_base_capacity_pure(data, target, runecrafting_data)
        capacity = base_capacity + runecrafting_pouch_capacity_pure(data, pouch_data)
        essence_items = tuple(target.get("essence_items", ()))
        essence_to_use = min(capacity, _available_essence_count(inventory, essence_items))
        used, _consumed = _consume_essence_ordered(inventory, essence_items, essence_to_use)
        if used <= 0:
            return player_data, 0, False, "No essence available"
        output_count = _standard_output_count(target, level, used, roll_iter)
        output_item = str(target.get("output_item"))
        inventory[output_item] = inventory.get(output_item, 0) + output_count
        if used > base_capacity:
            _degrade_used_pouches(data, pouch_data, used - base_capacity)
        return data, float(target.get("base_exp", 0.0)) * used, True, f"+{output_count} {output_item}"

    if kind == "combination":
        base_capacity = 26
        capacity = base_capacity + runecrafting_pouch_capacity_pure(data, pouch_data)
        pure_count = _positive_int(inventory.get("Pure essence", 0), 0)
        component_rune = str(target.get("component_rune"))
        consumed_talisman = str(target.get("consumed_talisman"))
        craft_count = min(capacity, pure_count, _positive_int(inventory.get(component_rune, 0), 0))
        if craft_count <= 0 or inventory.get(consumed_talisman, 0) <= 0:
            return player_data, 0, False, "Missing combination materials"
        inventory["Pure essence"] = inventory.get("Pure essence", 0) - craft_count
        inventory[component_rune] = inventory.get(component_rune, 0) - craft_count
        inventory[consumed_talisman] = inventory.get(consumed_talisman, 0) - 1
        output_item = str(target.get("output_item"))
        charges = binding_necklace_charges_pure(data)
        if charges > 0:
            output_count = craft_count
            remaining = charges - 1
            if remaining > 0:
                data.setdefault("item_charges", {})["Binding necklace"] = remaining
            else:
                data.setdefault("item_charges", {}).pop("Binding necklace", None)
                data.setdefault("equipment", {}).pop("neck", None)
        else:
            try:
                roll = float(next(roll_iter))
            except (StopIteration, TypeError, ValueError):
                roll = 0.0
            output_count = min(craft_count, int(max(0.0, min(roll, 0.999999999)) * craft_count) + 1)
        inventory[output_item] = inventory.get(output_item, 0) + output_count
        if craft_count > base_capacity:
            _degrade_used_pouches(data, pouch_data, craft_count - base_capacity)
        return data, float(target.get("base_exp", 0.0)) * craft_count, True, f"+{output_count} {output_item}"

    if kind == "tiara":
        talisman = str(target.get("talisman_item"))
        inventory["Tiara"] = inventory.get("Tiara", 0) - 1
        inventory[talisman] = inventory.get(talisman, 0) - 1
        output_item = str(target.get("output_item"))
        inventory[output_item] = inventory.get(output_item, 0) + 1
        return data, float(target.get("base_exp", 0.0)), True, f"+1 {output_item}"

    if kind == "hood_feed":
        input_item = str(target.get("input_item"))
        altar_id = str(target.get("altar_id"))
        inventory[input_item] = inventory.get(input_item, 0) - 1
        hood = data.setdefault("wicked_hood", {})
        fed = set(_fed_altars(data))
        fed.add(altar_id)
        hood["fed_altars"] = sorted(fed)
        return data, 0, True, f"{input_item} fed"

    return player_data, 0, False, "Unsupported Runecrafting target"


def _scape2011_interpolate_255(low, high, level):
    # MiscExt.kt 3-arg interpolate: floor(low*(99-level)/98 +
    # floor(high*(level-1)/98) + 1). Success in Mining/Woodcutting is
    # `interp > nextInt(255)`, i.e. probability interp/255.
    level = max(1, min(int(level), 99))
    return floor((int(low) * (99 - level)) / 98.0 + floor((int(high) * (level - 1)) / 98.0) + 1)


def mining_source_roll_chance_pure(mining_level, target_spec, pickaxe_spec):
    """Exact 2011Scape mining roll (Mining.kt): the interpolated chance is
    ratio-free in source (the pickaxe sets roll cadence via
    ticksBetweenRolls); AnkiScape folds that cadence into the per-action
    chance as a declared adaptation of the one-roll-per-review model."""
    interpolated = float(_scape2011_interpolate_255(
        target_spec.get("low_chance", 0), target_spec.get("high_chance", 0), _positive_int(mining_level, 1)
    ))
    ratio = float(pickaxe_spec.get("ratio", 1.0))
    # Mining.kt gives PickaxeType.DRAGON an accumulator: +0.2 per swing, and
    # each fifth swing rolls again at 1.12x base. AnkiScape folds that bonus
    # into every roll as a declared simplification of the same source
    # constant, keyed on the stable pickaxe id (gilded variants share it).
    if _non_negative_int(pickaxe_spec.get("item_id"), 0) == 15261:  # Dragon pickaxe
        ratio *= 1.12
    return max(0.0, min((interpolated * ratio) / 255.0, 1.0))


def calculate_mining_success_probability_pure(
    mining_level,
    target_spec,
    pickaxe_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Translate source mining odds into one review-scale success probability."""
    source_chance = mining_source_roll_chance_pure(mining_level, target_spec, pickaxe_spec)
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def mining_target_locked_reasons_pure(player_data, target_id, ore_data, pickaxe_data, quest_unlock_rules=()):
    spec = ore_data.get(target_id)
    if not spec:
        return ("unknown target",)
    reasons = []
    mining_level = _positive_int(player_data.get("mining_level", 1), 1)
    if mining_level < _positive_int(spec.get("level", 1), 1):
        reasons.append(f"Mining level {spec.get('level', 1)}")
    if best_mining_pickaxe_pure(
        mining_level,
        player_data.get("inventory", {}) or {},
        player_data.get("toolbelt", {}) or {},
        pickaxe_data,
    ) is None:
        reasons.append("no usable pickaxe")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "mining",
            target_id,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def can_mine_target_pure(mining_level, target_id, ore_data, inventory, toolbelt, pickaxe_data):
    spec = ore_data.get(target_id)
    if not spec:
        return False
    if mining_level < spec.get("level", 1):
        return False
    return best_mining_pickaxe_pure(mining_level, inventory, toolbelt, pickaxe_data) is not None


def woodcutting_source_roll_chance_pure(woodcutting_level, target_spec, axe_spec):
    """Exact 2011Scape chop roll (Woodcutting.kt): the axe ratio scales the
    chance inputs (truncated to int) before the shared interpolate helper,
    and success is `interp > nextInt(255)`."""
    ratio = float(axe_spec.get("ratio", 1.0))
    low = int(float(target_spec.get("low_chance", 0)) * ratio)
    high = int(float(target_spec.get("high_chance", 0)) * ratio)
    interpolated = _scape2011_interpolate_255(low, high, _positive_int(woodcutting_level, 1))
    return max(0.0, min(interpolated / 255.0, 1.0))


def calculate_woodcutting_success_probability_pure(
    woodcutting_level,
    target_spec,
    axe_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Translate source chop odds into a review-scale success probability.

    2011Scape rolls every few game ticks; AnkiScape rolls once per eligible card.
    The square-root adapter preserves ordering and tool upgrades while avoiding
    extremely dry high-tier trees at normal review cadence.
    """
    source_chance = woodcutting_source_roll_chance_pure(woodcutting_level, target_spec, axe_spec)
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def can_chop_woodcutting_target_pure(woodcutting_level, target_id, tree_data, inventory, toolbelt, axe_data):
    spec = tree_data.get(target_id)
    if not spec:
        return False
    if woodcutting_level < spec.get("level", 1):
        return False
    return best_woodcutting_axe_pure(woodcutting_level, inventory, toolbelt, axe_data) is not None


def apply_woodcutting_action_pure(
    target_id,
    inventory,
    tree_data,
    woodcutting_level,
    axe_spec,
    r_action,
    r_nest_drop=None,
    r_nest_type=None,
    nest_drop_table=None,
    nest_drop_chance=0.0,
    r_inferno_adze=None,
):
    spec = tree_data.get(target_id)
    if not spec or not axe_spec:
        return inventory, 0, False, None, None
    success_probability = calculate_woodcutting_success_probability_pure(woodcutting_level, spec, axe_spec)
    if r_action >= success_probability:
        return inventory, 0, False, None, None

    new_inv = dict(inventory)
    output_item = spec.get("output_item")
    if (
        output_item
        and axe_spec.get("incinerates_logs", False)
        and r_inferno_adze is not None
        and r_inferno_adze < axe_spec.get("incinerate_chance", 0.0)
    ):
        output_item = None
    elif output_item:
        new_inv[output_item] = new_inv.get(output_item, 0) + 1

    nest_item = None
    if r_nest_drop is not None and r_nest_type is not None and nest_drop_table and r_nest_drop < nest_drop_chance:
        nest_item = pick_weighted_item_pure(nest_drop_table, r_nest_type)
        if nest_item:
            new_inv[nest_item] = new_inv.get(nest_item, 0) + 1

    return new_inv, spec.get("exp", 0), True, output_item, nest_item


def fishing_source_roll_chance_pure(fishing_level, fish_spec):
    """Exact 2011Scape fish roll (Fish.kt: level.interpolate(min, max, 1, 99,
    255)): integer-division linear interpolation, success iff
    nextInt(255) <= interp, i.e. probability (interp + 1)/255."""
    low = int(_non_negative_float(fish_spec.get("min_chance", 0), 0.0))
    high = int(_non_negative_float(fish_spec.get("max_chance", 0), 0.0))
    level = max(1, min(_positive_int(fishing_level, 1), 99))
    interp = low + ((high - low) * (level - 1)) // 98
    return max(0.0, min((interp + 1) / 255.0, 1.0))


def calculate_fishing_success_probability_pure(
    fishing_level,
    fish_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Translate source Fishing odds into one review-scale success probability."""
    source_chance = fishing_source_roll_chance_pure(fishing_level, fish_spec)
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def eligible_fishing_fish_pure(method_spec, fishing_level, strength_level=1, agility_level=1):
    """Fish rows whose Fishing and hidden side-level gates are currently met."""
    eligible = []
    for fish in method_spec.get("fish", ()):
        if fishing_level < _positive_int(fish.get("level", 1), 1):
            continue
        strength_req = fish.get("strength_level")
        if strength_req is not None and strength_level < _positive_int(strength_req, 1):
            continue
        agility_req = fish.get("agility_level")
        if agility_req is not None and agility_level < _positive_int(agility_req, 1):
            continue
        eligible.append(fish)
    return tuple(eligible)


def has_fishing_bait_pure(inventory, method_spec):
    """Return True if the method has no consumable bait or any allowed bait is held."""
    bait_options = tuple(method_spec.get("bait_options") or ())
    if not bait_options:
        return True
    return any(inventory.get(bait, 0) > 0 for bait in bait_options)


def can_fish_method_pure(fishing_level, inventory, target_id, fishing_data, strength_level=1, agility_level=1):
    """Return True if a Fishing target can make at least one source roll now."""
    method_spec = fishing_data.get(target_id)
    if not method_spec:
        return False
    if fishing_level < method_spec.get("level", 1):
        return False
    if not has_fishing_bait_pure(inventory, method_spec):
        return False
    return bool(eligible_fishing_fish_pure(method_spec, fishing_level, strength_level, agility_level))


def fishing_method_locked_reasons_pure(player_data, target_id, fishing_data, quest_unlock_rules=()):
    method_spec = fishing_data.get(target_id)
    if not method_spec:
        return ("unknown target",)
    reasons = []
    fishing_level = _positive_int(player_data.get("fishing_level", 1), 1)
    strength_level = _positive_int(player_data.get("strength_level", 1), 1)
    agility_level = _positive_int(player_data.get("agility_level", 1), 1)
    inventory = player_data.get("inventory", {}) or {}
    if fishing_level < _positive_int(method_spec.get("level", 1), 1):
        reasons.append(f"Fishing level {method_spec.get('level', 1)}")
    if not has_fishing_bait_pure(inventory, method_spec):
        reasons.append("materials")
    if (
        fishing_level >= _positive_int(method_spec.get("level", 1), 1)
        and not eligible_fishing_fish_pure(method_spec, fishing_level, strength_level, agility_level)
    ):
        reasons.append("side levels")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "fishing",
            target_id,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def can_fish_any_pure(inventory, fishing_level, fishing_data, strength_level=1, agility_level=1):
    """Return True if any Fishing method can be attempted now."""
    return any(
        can_fish_method_pure(fishing_level, inventory, target, fishing_data, strength_level, agility_level)
        for target in fishing_data
    )


def apply_fishing_action_pure(
    target_id,
    inventory,
    fishing_data,
    fishing_level,
    strength_level=1,
    agility_level=1,
    rolls=(),
):
    """Apply one ordered source-shaped Fishing attempt.

    Returns (inventory, base_fishing_exp, success, output_item, xp_rewards).
    Bait is consumed only after a catch, mirroring the 2011Scape runtime.
    """
    method_spec = fishing_data.get(target_id)
    if not method_spec:
        return inventory, 0, False, None, tuple()
    if not can_fish_method_pure(fishing_level, inventory, target_id, fishing_data, strength_level, agility_level):
        return inventory, 0, False, None, tuple()

    roll_iter = iter(rolls or ())
    for fish in eligible_fishing_fish_pure(method_spec, fishing_level, strength_level, agility_level):
        try:
            roll = float(next(roll_iter))
        except (StopIteration, TypeError, ValueError):
            roll = 1.0
        success_probability = calculate_fishing_success_probability_pure(fishing_level, fish)
        if roll >= success_probability:
            continue

        new_inv = dict(inventory)
        for bait in method_spec.get("bait_options") or ():
            if new_inv.get(bait, 0) > 0:
                new_inv[bait] = new_inv.get(bait, 0) - 1
                break
        output_item = fish.get("output_item")
        if output_item:
            new_inv[output_item] = new_inv.get(output_item, 0) + 1

        xp_rewards = normalize_xp_rewards_pure(fish, "fishing", fish.get("exp", 0))
        return new_inv, primary_xp_reward_amount_pure(xp_rewards, "fishing"), True, output_item, xp_rewards

    return inventory, 0, False, None, tuple()


def _hunter_outputs_from_spec(spec):
    raw_outputs = spec.get("outputs", {})
    if isinstance(raw_outputs, Mapping):
        return {
            str(item): _positive_int(amount, 1)
            for item, amount in raw_outputs.items()
            if isinstance(item, str) and item
        }
    output_item = spec.get("output_item")
    if isinstance(output_item, str) and output_item:
        return {output_item: _positive_int(spec.get("output_qty", 1), 1)}
    return {}


def hunter_source_roll_chance_pure(hunter_level, target_spec):
    """Exact Darkan Hunter catch odds (Utils.skillSuccess, verified by
    bytecode disassembly of core-2.0.5.jar): chance = int(rate1 +
    (rate99 - rate1) * level / 99), clamped to 0..256, success iff
    nextInt(255) <= chance, i.e. probability (chance + 1)/255."""
    if bool(target_spec.get("deterministic", False)):
        return 1.0
    low = int(_non_negative_float(target_spec.get("rate1", 128), 128.0))
    high = int(_non_negative_float(target_spec.get("rate99", 256), 256.0))
    level = max(1, _positive_int(hunter_level, 1))
    chance = int(low + (high - low) * (level / 99.0))
    chance = max(0, min(chance, 256))
    return max(0.0, min((chance + 1) / 255.0, 1.0))


def calculate_hunter_success_probability_pure(
    hunter_level,
    target_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Translate source Hunter odds into one review-scale success probability."""
    if bool(target_spec.get("deterministic", False)):
        return 1.0
    source_chance = hunter_source_roll_chance_pure(hunter_level, target_spec)
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def has_hunter_materials_pure(target, inventory, hunter_data):
    """Return True when inventory satisfies a Hunter target's consumable needs."""
    spec = hunter_data.get(target)
    if not spec:
        return False
    requirements = spec.get("requirements", {})
    if not isinstance(requirements, Mapping):
        return True
    for material, amount in requirements.items():
        if inventory.get(material, 0) < _positive_int(amount, 1):
            return False
    return True


def missing_hunter_tools_pure(target, inventory, hunter_data):
    """Return reusable Hunter tools missing from inventory/bank state."""
    spec = hunter_data.get(target)
    if not spec:
        return ("unknown target",)
    tools = spec.get("tools", {})
    if not isinstance(tools, Mapping):
        return tuple()
    missing = []
    for tool, amount in tools.items():
        required = _positive_int(amount, 1)
        if inventory.get(tool, 0) < required:
            missing.append(str(tool))
    return tuple(missing)


def has_hunter_tools_pure(target, inventory, hunter_data):
    return not missing_hunter_tools_pure(target, inventory, hunter_data)


def hunter_target_locked_reasons_pure(player_data, target, hunter_data, quest_unlock_rules=()):
    spec = hunter_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    hunter_level = _positive_int(player_data.get("hunter_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if hunter_level < required_level:
        reasons.append(f"Hunter level {required_level}")
    if not has_hunter_materials_pure(target, player_data.get("inventory", {}) or {}, hunter_data):
        reasons.append("materials")
    reasons.extend(missing_hunter_tools_pure(target, player_data.get("inventory", {}) or {}, hunter_data))
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "hunter",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def can_hunt_target_pure(hunter_level, inventory, target, hunter_data):
    spec = hunter_data.get(target)
    if not spec:
        return False
    if hunter_level < _positive_int(spec.get("level", 1), 1):
        return False
    return has_hunter_materials_pure(target, inventory, hunter_data) and has_hunter_tools_pure(target, inventory, hunter_data)


def apply_hunter_action_pure(target, inventory, hunter_data, hunter_level, r_action):
    """Apply one Hunter attempt and return inventory, XP, success, output, rewards."""
    spec = hunter_data.get(target)
    if not spec or not can_hunt_target_pure(hunter_level, inventory, target, hunter_data):
        return inventory, 0, False, None, tuple()
    success_probability = calculate_hunter_success_probability_pure(hunter_level, spec)
    if float(r_action) >= success_probability:
        return inventory, 0, False, None, tuple()

    new_inv = dict(inventory)
    requirements = spec.get("requirements", {})
    if isinstance(requirements, Mapping):
        for material, amount in requirements.items():
            new_inv[material] = new_inv.get(material, 0) - _positive_int(amount, 1)
    outputs = _hunter_outputs_from_spec(spec)
    for item_name, amount in outputs.items():
        new_inv[item_name] = new_inv.get(item_name, 0) + amount
    primary_output = spec.get("primary_output") or spec.get("output_item")
    xp_rewards = normalize_xp_rewards_pure(spec, "hunter", spec.get("exp", 0))
    return new_inv, primary_xp_reward_amount_pure(xp_rewards, "hunter"), True, primary_output, xp_rewards


def can_open_bird_nests_pure(inventory, nest_open_tables):
    return any(inventory.get(input_item, 0) > 0 for input_item in nest_open_tables)


def apply_open_bird_nests_pure(inventory, nest_open_tables, rolls=(), batch_size=28):
    """Open up to batch_size source bird nests and return inert contents."""
    remaining = _positive_int(batch_size, 28)
    roll_iter = iter(rolls or ())
    new_inv = dict(inventory)
    opened = 0
    outputs = {}
    for input_item, table in nest_open_tables.items():
        while remaining > 0 and new_inv.get(input_item, 0) > 0:
            new_inv[input_item] = new_inv.get(input_item, 0) - 1
            opened += 1
            remaining -= 1

            guaranteed_item = table.get("guaranteed_item")
            if guaranteed_item:
                new_inv[guaranteed_item] = new_inv.get(guaranteed_item, 0) + 1
                outputs[guaranteed_item] = outputs.get(guaranteed_item, 0) + 1

            weighted_items = table.get("rolls", ())
            total_weight = table.get("total_weight")
            try:
                roll = next(roll_iter)
            except StopIteration:
                roll = 0.0
            rolled_item = pick_weighted_item_pure(weighted_items, roll, total_weight)
            if rolled_item:
                new_inv[rolled_item] = new_inv.get(rolled_item, 0) + 1
                outputs[rolled_item] = outputs.get(rolled_item, 0) + 1
    return new_inv, opened > 0, opened, outputs

def apply_mining_pure(
    ore_name,
    inventory,
    ore_data,
    gem_data,
    r_action,
    success_probability,
    r_gem_chance=None,
    r_gem_pick=None,
    gem_drop_chance=1/256,
):
    """
    Attempt a mining action. Returns (new_inventory, exp_gained, success, gem_name).
    If success, may also award a gem using provided randoms and gem_drop_chance.
    Does not mutate input inventory.
    """
    success = r_action < success_probability
    if not success:
        return inventory, 0, False, None
    new_inv = dict(inventory)
    new_inv[ore_name] = new_inv.get(ore_name, 0) + 1
    exp = ore_data[ore_name].get("exp", 0)

    gem_name = None
    if r_gem_chance is not None and r_gem_pick is not None and r_gem_chance < gem_drop_chance:
        gem_name = pick_gem(gem_data, r_gem_pick)
        if gem_name:
            new_inv[gem_name] = new_inv.get(gem_name, 0) + 1
            exp += gem_data[gem_name].get("exp", 0)
    return new_inv, exp, True, gem_name


def apply_mining_action_pure(
    target_id,
    inventory,
    ore_data,
    mining_level,
    pickaxe_spec,
    r_action,
    r_output=None,
    r_gem_chance=None,
    r_gem_pick=None,
    gem_drop_table=(),
    gem_drop_chance=1 / 256,
    varrock_armour_tier=0,
):
    """Apply one source-shaped Anki Mining attempt.

    Returns (inventory, base_exp, success, output_item, gem_item, extra_output).
    Random gem drops are inventory-only side drops; they do not add Mining XP.
    """
    spec = ore_data.get(target_id)
    if not spec or not pickaxe_spec:
        return inventory, 0, False, None, None, None
    success_probability = calculate_mining_success_probability_pure(mining_level, spec, pickaxe_spec)
    if r_action >= success_probability:
        return inventory, 0, False, None, None, None

    new_inv = dict(inventory)
    output_item = spec.get("output_item")
    base_exp = spec.get("exp", 0)
    weighted_outputs = spec.get("weighted_outputs", ())
    if weighted_outputs:
        picked = pick_weighted_item_pure(weighted_outputs, 0.0 if r_output is None else r_output)
        if picked:
            output_item = picked
            for weighted in weighted_outputs:
                if weighted.get("item") == picked:
                    base_exp = weighted.get("exp", base_exp)
                    break
    alternate_output_item = spec.get("alternate_output_item")
    alternate_output_level = spec.get("alternate_output_level")
    if isinstance(alternate_output_item, str) and isinstance(alternate_output_level, int) and mining_level >= alternate_output_level:
        output_item = alternate_output_item

    if output_item:
        new_inv[output_item] = new_inv.get(output_item, 0) + 1

    extra_output = None
    required_varrock_tier = spec.get("varrock_armour_tier")
    if (
        output_item
        and isinstance(required_varrock_tier, int)
        and required_varrock_tier > 0
        and varrock_armour_tier >= required_varrock_tier
    ):
        extra_output = output_item
        new_inv[output_item] = new_inv.get(output_item, 0) + 1

    gem_item = None
    if (
        spec.get("allows_random_gems", True)
        and r_gem_chance is not None
        and r_gem_pick is not None
        and gem_drop_table
        and r_gem_chance < gem_drop_chance
    ):
        gem_item = pick_weighted_item_pure(gem_drop_table, r_gem_pick)
        if gem_item:
            new_inv[gem_item] = new_inv.get(gem_item, 0) + 1

    return new_inv, base_exp, True, output_item, gem_item, extra_output


def can_mine_ore_pure(mining_level, ore_name, ore_data):
    """Return True if mining_level meets the ore's required level."""
    spec = ore_data.get(ore_name)
    if not spec:
        return False
    return mining_level >= spec.get("level", 1)


def can_cut_tree_pure(woodcutting_level, tree_name, tree_data):
    """Return True if woodcutting_level meets the tree's required level."""
    spec = tree_data.get(tree_name)
    if not spec:
        return False
    return woodcutting_level >= spec.get("level", 1)


def can_craft_item_pure(crafting_level, inventory, item, crafting_data):
    """Return True if level and materials allow crafting the item."""
    spec = crafting_data.get(item)
    if not spec:
        return False
    if crafting_level < spec.get("level", 1):
        return False
    return has_crafting_materials_pure(item, inventory, crafting_data)


def crafting_target_locked_reasons_pure(player_data, target, crafting_data, quest_unlock_rules=()):
    spec = crafting_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    crafting_level = _positive_int(player_data.get("crafting_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if crafting_level < required_level:
        reasons.append(f"level {required_level}")
    if not has_crafting_materials_pure(target, player_data.get("inventory", {}) or {}, crafting_data):
        reasons.append("materials")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "crafting",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def fletching_material_requirements_pure(target, inventory, fletching_data):
    """Resolve a Fletching target's exact material consumption from inventory."""
    spec = fletching_data.get(target)
    if not spec:
        return None
    requirements = dict(spec.get("requirements", {}))
    for material, alternatives in spec.get("material_options", {}).items():
        amount = requirements.get(material)
        if amount is None:
            continue
        selected = next(
            (option for option in alternatives if inventory.get(option, 0) >= amount),
            None,
        )
        if selected is None:
            return None
        del requirements[material]
        requirements[selected] = amount
    for material, amount in requirements.items():
        if inventory.get(material, 0) < amount:
            return None
    return requirements


def has_fletching_materials_pure(target, inventory, fletching_data):
    """Return True when inventory satisfies a Fletching target's material needs."""
    return fletching_material_requirements_pure(target, inventory, fletching_data) is not None


def can_fletch_item_pure(fletching_level, inventory, target, fletching_data):
    """Return True if level and materials allow the Fletching target."""
    spec = fletching_data.get(target)
    if not spec:
        return False
    if fletching_level < spec.get("level", 1):
        return False
    return has_fletching_materials_pure(target, inventory, fletching_data)


def fletching_target_locked_reasons_pure(player_data, target, fletching_data, target_unlock_rules=()):
    spec = fletching_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    fletching_level = _positive_int(player_data.get("fletching_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if fletching_level < required_level:
        reasons.append(f"Fletching level {required_level}")
    if not has_fletching_materials_pure(target, player_data.get("inventory", {}) or {}, fletching_data):
        reasons.append("materials")
    reasons.extend(
        target_unlock_locked_reasons_pure(
            player_data,
            "fletching",
            target,
            target_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def apply_fletching_pure(target, inventory, fletching_data):
    """Consume logs and produce the selected Fletching output.

    Fletching is intentionally modeled as a processing skill like Crafting:
    the caller handles level checks so UI/runtime code can report a precise
    locked reason, while this pure function owns inventory mutation safety.
    """
    spec = fletching_data.get(target)
    if not spec or not has_fletching_materials_pure(target, inventory, fletching_data):
        return inventory, 0, False

    requirements = fletching_material_requirements_pure(target, inventory, fletching_data)
    if requirements is None:
        return inventory, 0, False

    new_inv = dict(inventory)
    for material, amount in requirements.items():
        new_inv[material] = new_inv.get(material, 0) - amount

    output_item = spec.get("output_item", target)
    output_qty = spec.get("output_qty", 1)
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True


def has_herblore_materials_pure(target, inventory, herblore_data):
    """Return True when inventory satisfies a Herblore target's material needs."""
    spec = herblore_data.get(target)
    if not spec:
        return False
    for material, amount in spec.get("requirements", {}).items():
        if inventory.get(material, 0) < amount:
            return False
    return True


def can_herblore_target_pure(herblore_level, inventory, target, herblore_data):
    """Return True if level and materials allow the Herblore target."""
    spec = herblore_data.get(target)
    if not spec:
        return False
    if herblore_level < spec.get("level", 1):
        return False
    return has_herblore_materials_pure(target, inventory, herblore_data)


def herblore_target_locked_reasons_pure(player_data, target, herblore_data, target_unlock_rules=()):
    spec = herblore_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    herblore_level = _positive_int(player_data.get("herblore_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if herblore_level < required_level:
        reasons.append(f"Herblore level {required_level}")
    if not has_herblore_materials_pure(target, player_data.get("inventory", {}) or {}, herblore_data):
        reasons.append("materials")
    reasons.extend(
        target_unlock_locked_reasons_pure(
            player_data,
            "herblore",
            target,
            target_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def apply_herblore_action_pure(target, inventory, herblore_data):
    """Consume herblore inputs and produce the selected output.

    The three pipeline stages (clean → unfinished → finished) share this one
    processing path; each stage's XP is baked into the target's ``exp`` field
    from HerbData.kt / PotionData.kt (herb XP for clean, zero for unfinished,
    recipe XP for finished), so no stage-specific branching is needed here.
    """
    spec = herblore_data.get(target)
    if not spec or not has_herblore_materials_pure(target, inventory, herblore_data):
        return inventory, 0, False

    new_inv = dict(inventory)
    for material, amount in spec.get("requirements", {}).items():
        new_inv[material] = new_inv.get(material, 0) - amount

    output_item = spec.get("output_item", target)
    output_qty = spec.get("output_qty", 1)
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True


def has_cooking_materials_pure(target, inventory, cooking_data):
    """Return True when inventory has the raw/prepared item for one Cooking action."""
    spec = cooking_data.get(target)
    if not spec:
        return False
    requirements = spec.get("requirements", {})
    return all(inventory.get(material, 0) >= amount for material, amount in requirements.items())


def can_cook_target_pure(cooking_level, inventory, target, cooking_data):
    """Return True when level and materials permit one Cooking action."""
    spec = cooking_data.get(target)
    if not spec:
        return False
    if not spec.get("source_no_level_requirement") and int(cooking_level or 1) < _positive_int(spec.get("level", 1), 1):
        return False
    return has_cooking_materials_pure(target, inventory, cooking_data)


def cooking_target_locked_reasons_pure(player_data, target, cooking_data, quest_unlock_rules=()):
    spec = cooking_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    cooking_level = _positive_int(player_data.get("cooking_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if not spec.get("source_no_level_requirement") and cooking_level < required_level:
        reasons.append(f"Cooking level {required_level}")
    if not has_cooking_materials_pure(target, player_data.get("inventory", {}) or {}, cooking_data):
        reasons.append("materials")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "cooking",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def cooking_source_roll_chance_pure(cooking_level, target_spec):
    """Exact 2011Scape Cooking roll (CookingAction.kt): the shared 3-arg
    interpolate helper (floors + 1) with success on interp > nextInt(255)."""
    source_formula = target_spec.get("source_success_formula")
    if isinstance(source_formula, Mapping):
        base = float(source_formula["base"])
        level_multiplier = float(source_formula["level_multiplier"])
        level_range = float(source_formula["level_range"])
        cap = float(source_formula["cap"])
        divisor = float(source_formula["divisor"])
        return min(base + level_multiplier * (float(cooking_level) - 1) / level_range, cap) / divisor
    if target_spec.get("source_always_succeeds"):
        return 1.0
    interpolated = _scape2011_interpolate_255(
        target_spec.get("low_chance", 1),
        target_spec.get("high_chance", 255),
        _positive_int(cooking_level, 1),
    )
    return max(0.0, min(interpolated / 255.0, 1.0))


def calculate_cooking_success_probability_pure(
    cooking_level,
    target_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Translate source Cooking odds into one review-scale success probability."""
    source_chance = cooking_source_roll_chance_pure(cooking_level, target_spec)
    if target_spec.get("source_success_formula") or target_spec.get("source_always_succeeds"):
        return source_chance
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def apply_cooking_action_pure(target, inventory, cooking_data, cooking_level, roll, byproduct_roll=None):
    """Apply one Cooking action.

    Returns (inventory, exp, processed, output_item, burned). A failed burn still
    counts as processed because the raw input was consumed and a burnt item was
    produced; it simply awards zero XP.
    """
    spec = cooking_data.get(target)
    if not spec or not has_cooking_materials_pure(target, inventory, cooking_data):
        return inventory, 0, False, None, False

    new_inv = dict(inventory)
    for material, amount in spec.get("requirements", {}).items():
        new_inv[material] = new_inv.get(material, 0) - amount

    success_probability = calculate_cooking_success_probability_pure(cooking_level, spec)
    source_runtime_action = bool(spec.get("source_success_formula") or spec.get("source_always_succeeds"))
    succeeded = float(roll) <= success_probability if source_runtime_action else float(roll) < success_probability
    if succeeded:
        output_item = spec.get("output_item", target)
        output_qty = _positive_int(spec.get("output_qty", 1), 1)
        new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
        byproduct_item = spec.get("byproduct_item")
        if isinstance(byproduct_item, str) and byproduct_item and byproduct_roll is not None:
            if float(byproduct_roll) <= float(spec.get("byproduct_chance", 0.0)):
                new_inv[byproduct_item] = new_inv.get(byproduct_item, 0) + 1
        return new_inv, spec.get("exp", 0), True, output_item, False

    burnt_item = spec.get("burnt_item")
    if isinstance(burnt_item, str) and burnt_item:
        new_inv[burnt_item] = new_inv.get(burnt_item, 0) + 1
    else:
        burnt_item = None
    return new_inv, 0, True, burnt_item, True


def firemaking_source_roll_chance_pure(firemaking_level, target_spec):
    """Exact 2011Scape Firemaking roll (FiremakingAction.kt): the shared
    3-arg interpolate helper (floors + 1) with success on
    interp > nextInt(255)."""
    interpolated = _scape2011_interpolate_255(
        target_spec.get("low_chance", 65),
        target_spec.get("high_chance", 513),
        _positive_int(firemaking_level, 1),
    )
    return max(0.0, min(interpolated / 255.0, 1.0))


def calculate_firemaking_success_probability_pure(
    firemaking_level,
    target_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    overlevel_window=40,
    cap=REVIEW_SUCCESS_CAP,
    tier_minimum=0.30,
    tier_scale=0.65,
):
    """Translate source lighting odds into one review-scale success probability.

    The source chance mostly depends on Firemaking level, not the log tier. To
    make higher-level logs feel slower near unlock in AnkiScape, this adapter
    also applies a target-level curve: old logs become comfortable as the player
    overlevels them, while newly unlocked logs start stickier.
    """
    source_chance = firemaking_source_roll_chance_pure(firemaking_level, target_spec)
    source_adapter = normalize_review_success_probability_pure(source_chance, minimum, scale, cap)
    required_level = _positive_int(target_spec.get("level", 1), 1)
    overlevel = max(0.0, float(firemaking_level) - float(required_level))
    window = max(float(overlevel_window), 1.0)
    tier_progress = max(0.0, min((overlevel + 1.0) / window, 1.0))
    tier_adapter = normalize_review_success_probability_pure(tier_progress, tier_minimum, tier_scale, cap)
    return max(0.0, min(source_adapter, tier_adapter, cap))


def has_firemaking_materials_pure(target, inventory, firemaking_data):
    """Return True when inventory has the log/root for one Firemaking action."""
    spec = firemaking_data.get(target)
    if not spec:
        return False
    for material, amount in spec.get("requirements", {}).items():
        if inventory.get(material, 0) < amount:
            return False
    return True


def can_burn_firemaking_target_pure(firemaking_level, inventory, target, firemaking_data):
    """Return True if level and materials allow one Firemaking attempt."""
    spec = firemaking_data.get(target)
    if not spec:
        return False
    if firemaking_level < spec.get("level", 1):
        return False
    return has_firemaking_materials_pure(target, inventory, firemaking_data)


def firemaking_target_locked_reasons_pure(player_data, target, firemaking_data, quest_unlock_rules=()):
    spec = firemaking_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    firemaking_level = _positive_int(player_data.get("firemaking_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if firemaking_level < required_level:
        reasons.append(f"Firemaking level {required_level}")
    if not has_firemaking_materials_pure(target, player_data.get("inventory", {}) or {}, firemaking_data):
        reasons.append("materials")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "firemaking",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def can_burn_firemaking_target_with_unlocks_pure(player_data, target, firemaking_data, quest_unlock_rules=()):
    return not firemaking_target_locked_reasons_pure(player_data, target, firemaking_data, quest_unlock_rules)


def can_burn_any_firemaking_target_pure(inventory, firemaking_level, firemaking_data):
    """Return True if any Firemaking target can be attempted right now."""
    return any(
        can_burn_firemaking_target_pure(firemaking_level, inventory, target, firemaking_data)
        for target in firemaking_data
    )


def apply_firemaking_action_pure(target, inventory, firemaking_data, firemaking_level, r_action):
    """Apply one Firemaking attempt.

    Returns (inventory, base_exp, success, output_item). Failed attempts consume
    no log and award no XP/items, matching AnkiScape's gathering-style pacing.
    """
    spec = firemaking_data.get(target)
    if not spec or not has_firemaking_materials_pure(target, inventory, firemaking_data):
        return inventory, 0, False, None
    success_probability = calculate_firemaking_success_probability_pure(firemaking_level, spec)
    if r_action >= success_probability:
        return inventory, 0, False, None

    new_inv = dict(inventory)
    for material, amount in spec.get("requirements", {}).items():
        new_inv[material] = new_inv.get(material, 0) - amount
    output_item = spec.get("output_item", "Ashes")
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True, output_item
