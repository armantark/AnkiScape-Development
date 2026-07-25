"""logic_pure_magic.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

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

from .logic_pure_progression import (  # noqa: F401  (re-export)
    REVIEW_SUCCESS_CAP,
    REVIEW_SUCCESS_MINIMUM,
    REVIEW_SUCCESS_SCALE,
    calculate_new_level,
    calculate_probability_with_level,
    default_red_sandstone_daily_state_pure,
    get_exp_to_next_level,
    get_newly_completed_achievements,
    normalize_review_success_probability_pure,
    pick_gem,
    pick_weighted_item_pure,
    red_sandstone_daily_remaining_pure,
    red_sandstone_daily_state_pure,
    red_sandstone_review_day_pure,
    sanitize_red_sandstone_daily_state_pure,
    sanitize_review_action_multiplier,
    sanitize_xp_multiplier,
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

from .logic_pure_progression import (
    sanitize_review_action_multiplier,
)

from .logic_pure_landmarks import (
    MAGE_ARENA_GOD_DATA,
    MAGE_ARENA_SPELL_TO_GOD,
    sanitize_mage_arena_state_pure,
)

from .logic_pure_state import (
    _copy_player_data_with_nested,
    _non_negative_int,
    _positive_int,
    _requirements_from_spec,
    quest_completed_pure,
)


def _magic_quest_gate_complete_pure(player_data, gate):
    if not gate:
        return True
    if gate in {"mage_arena", "mage_training_arena"}:
        return bool((player_data.get(gate, {}) or {}).get("completed"))
    return quest_completed_pure(player_data, str(gate))


def _farming_spell_locked_reasons_pure(player_data, target_id, patch_id=None):
    from ..logic.farming_logic import farming_spell_target_locked_reasons_pure
    return farming_spell_target_locked_reasons_pure(player_data, target_id, patch_id)


def _apply_farming_spell_pure(player_data, target_id, patch_id=None):
    from ..logic.farming_logic import apply_farming_spell_pure
    return apply_farming_spell_pure(player_data, target_id, patch_id)


def _apply_remote_farm_pure(player_data):
    from ..logic.farming_logic import apply_remote_farm_pure
    return apply_remote_farm_pure(player_data)


def _livid_spell_locked_reasons_pure(player_data, unlock_id):
    from ..logic.livid_farm_logic import sanitize_livid_farm_state_pure
    state = sanitize_livid_farm_state_pure(player_data.get("livid_farm"))
    if str(unlock_id) in set(map(str, state["unlocked_spells"])):
        return ()
    return ("Unlock at Livid Farm",)


MAGIC_CHARGE_DURATION_TICKS = 700


TEMPORARY_EFFECT_TICKS_PER_ACTION = 50


def advance_temporary_effects_pure(
    player_data,
    action_ticks=1,
    *,
    elapsed_ticks=None,
    advance_dragonfire=True,
):
    """Advance review-paced temporary effects without reading wall time."""
    data = dict(player_data)
    ticks = max(0, int(elapsed_ticks)) if elapsed_ticks is not None else (
        TEMPORARY_EFFECT_TICKS_PER_ACTION
        * sanitize_review_action_multiplier(action_ticks)
    )
    remaining = _non_negative_int(
        data.get(
            "magic_charge_ticks_remaining",
            MAGIC_CHARGE_DURATION_TICKS
            if data.get("magic_charge_active", False)
            else 0,
        ),
        0,
    )
    remaining = max(0, remaining - ticks)
    data["magic_charge_ticks_remaining"] = remaining
    data["magic_charge_active"] = remaining > 0
    shooting_star = data.get("shooting_star")
    if isinstance(shooting_star, dict):
        shooting_star = dict(shooting_star)
        shooting_star["ore_bonus_ticks_remaining"] = max(
            0,
            _non_negative_int(
                shooting_star.get("ore_bonus_ticks_remaining", 0),
                0,
            )
            - ticks,
        )
        data["shooting_star"] = shooting_star
    if advance_dragonfire:
        for effect_key in (
            "combat_antifire_ticks_remaining",
            "combat_super_antifire_ticks_remaining",
        ):
            data[effect_key] = max(
                0,
                _non_negative_int(data.get(effect_key, 0), 0) - ticks,
            )
    return data


def effective_magic_rune_cost_pure(player_data, rune_cost):
    """Waive elemental runes covered by the best owned/equipped staff."""
    cost = {str(name): _non_negative_int(amount, 0) for name, amount in (rune_cost or {}).items()}
    inventory = player_data.get("inventory", {}) or {}
    equipment = player_data.get("equipment", {}) or {}
    owned = set(equipment.values())
    owned.update(name for name, amount in inventory.items() if _non_negative_int(amount, 0) > 0)
    for staff_name, staff in COMBAT_MAGIC_STAFF_DATA.items():
        if staff_name not in owned:
            continue
        for rune_name in staff.get("covered_runes", ()):
            cost.pop(str(rune_name), None)
    return cost


def _magic_dynamic_requirements_pure(
    player_data,
    spec,
    alch_values,
    farming_patch_id=None,
):
    action = str(spec.get("action", "pure"))
    inventory = player_data.get("inventory", {}) or {}
    requirements = dict(_requirements_from_spec(spec))
    if action == "alchemy":
        item = str(player_data.get("magic_alchemy_item", ""))
        if not item or item == "Coins" or item not in alch_values:
            return requirements, ("Choose a tradeable bank item",)
        requirements[item] = requirements.get(item, 0) + 1
    elif action == "bones_conversion":
        eligible = ("Bones",) if spec.get("id") == "bones_to_bananas" else ("Bones", "Big bones")
        if not any(_non_negative_int(inventory.get(item, 0), 0) > 0 for item in eligible):
            return requirements, ("Bones",)
    elif action == "bake_pie":
        if not any(_non_negative_int(inventory.get(item, 0), 0) > 0 for item in ("Uncooked meat pie", "Uncooked berry pie", "Uncooked apple pie", "Raw garden pie", "Raw fish pie", "Raw admiral pie", "Raw wild pie", "Raw summer pie")):
            return requirements, ("Uncooked pie",)
    elif action == "humidify":
        if not any(_non_negative_int(inventory.get(item, 0), 0) > 0 for item in ("Bucket", "Jug", "Vial", "Clay")):
            return requirements, ("Empty water vessel or clay",)
    elif action == "superglass":
        if _non_negative_int(inventory.get("Bucket of sand", 0), 0) <= 0 or not any(_non_negative_int(inventory.get(item, 0), 0) > 0 for item in ("Soda ash", "Seaweed", "Swamp weed")):
            return requirements, ("Bucket of sand + soda ash/seaweed",)
    elif action == "tan_leather":
        selected_hide = str(spec.get("leather_input", "") or "")
        if selected_hide:
            if _non_negative_int(inventory.get(selected_hide, 0), 0) <= 0:
                return requirements, (selected_hide,)
        elif not any(
            _non_negative_int(inventory.get(item, 0), 0) > 0
            for item in _LEATHER_OUTPUTS
        ):
            return requirements, ("Hide",)
    elif action == "string_jewellery":
        if not any(_non_negative_int(inventory.get(item, 0), 0) > 0 for item in _STRINGABLE_AMULETS):
            return requirements, ("Unstrung amulet",)
    elif str(spec.get("id", "")) in {"cure_plant", "fertile_soil"}:
        return requirements, _farming_spell_locked_reasons_pure(
            player_data,
            str(spec["id"]),
            farming_patch_id,
        )
    return requirements, ()


def magic_target_locked_reasons_pure(
    player_data,
    target_id,
    magic_data,
    alch_values=None,
    *,
    farming_patch_id=None,
):
    spec = magic_data.get(target_id)
    if not isinstance(spec, Mapping):
        return ("Unknown Magic target",)
    reasons = []
    level = _positive_int(player_data.get("magic_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if level < required_level:
        reasons.append(f"Magic level {required_level}")
    secondary_skill = str(spec.get("secondary_skill", "") or "")
    secondary_level = _positive_int(spec.get("secondary_level", 1), 1)
    if secondary_skill and _positive_int(player_data.get(f"{secondary_skill}_level", 1), 1) < secondary_level:
        reasons.append(f"{secondary_skill.title()} level {secondary_level}")
    gate = spec.get("quest_gate")
    if gate and not _magic_quest_gate_complete_pure(player_data, gate):
        reasons.append(str(gate).replace("_", " ").title())
    native_gate = spec.get("borrowed_native_quest_gate")
    if native_gate and not _magic_quest_gate_complete_pure(player_data, native_gate):
        reasons.append(str(native_gate).replace("_", " ").title())
    livid_unlock = spec.get("livid_unlock")
    if livid_unlock:
        reasons.extend(_livid_spell_locked_reasons_pure(player_data, livid_unlock))
    consumer_unavailable = spec.get("consumer_unavailable")
    if consumer_unavailable:
        reasons.append(str(consumer_unavailable))
    if spec.get("museum_unlock") == "digsite_pendant":
        museum_state = player_data.get("varrock_museum")
        if not (
            isinstance(museum_state, Mapping)
            and bool(museum_state.get("digsite_pendant_unlocked"))
        ):
            reasons.append("Learn Digsite-pendant enchanting at Varrock Museum")
    borrowed_spell_id = spec.get("borrowed_spell_id")
    if borrowed_spell_id:
        from ..logic.livid_farm_logic import borrowed_power_locked_reasons_pure
        reasons.extend(
            borrowed_power_locked_reasons_pure(
                player_data,
                borrowed_spell_id,
            )
        )
    god_id = MAGE_ARENA_SPELL_TO_GOD.get(target_id)
    if god_id:
        state = sanitize_mage_arena_state_pure(player_data.get("mage_arena"))
        if target_id not in state["attuned_spells"]:
            reasons.append(
                f"Attune {MAGE_ARENA_GOD_DATA[god_id]['spell_name']} in the Mage Arena"
            )
    inventory = player_data.get("inventory", {}) or {}
    requirements, dynamic_reasons = _magic_dynamic_requirements_pure(
        player_data,
        spec,
        alch_values or {},
        farming_patch_id,
    )
    reasons.extend(dynamic_reasons)
    for item_name, amount in requirements.items():
        if _non_negative_int(inventory.get(item_name, 0), 0) < amount:
            reasons.append(f"{item_name} x{amount}")
    for rune_name, amount in effective_magic_rune_cost_pure(player_data, spec.get("rune_cost", {})).items():
        if _non_negative_int(inventory.get(rune_name, 0), 0) < amount:
            reasons.append(f"{rune_name} x{amount}")
    return tuple(dict.fromkeys(reasons))


_PIE_OUTPUTS = {
    "Uncooked meat pie": ("Meat pie", 110.0), "Uncooked berry pie": ("Redberry pie", 78.0),
    "Uncooked apple pie": ("Apple pie", 130.0), "Raw garden pie": ("Garden pie", 138.0),
    "Raw fish pie": ("Fish pie", 164.0), "Raw admiral pie": ("Admiral pie", 210.0),
    "Raw wild pie": ("Wild pie", 240.0), "Raw summer pie": ("Summer pie", 260.0),
}


_HUMIDIFY_OUTPUTS = {"Bucket": "Bucket of water", "Jug": "Jug of water", "Vial": "Vial of water", "Clay": "Soft clay"}


_LEATHER_OUTPUTS = {"Cowhide": "Leather", "Green dragonhide": "Green dragon leather", "Blue dragonhide": "Blue dragon leather", "Red dragonhide": "Red dragon leather", "Black dragonhide": "Black dragon leather"}


_STRINGABLE_AMULETS = {
    "Gold amulet (u)": "Gold amulet",
    "Sapphire amulet (u)": "Sapphire amulet",
    "Emerald amulet (u)": "Emerald amulet",
    "Ruby amulet (u)": "Ruby amulet",
    "Diamond amulet (u)": "Diamond amulet",
    "Dragonstone ammy (u)": "Dragonstone ammy",
    "Onyx amulet (u)": "Onyx amulet",
}


def apply_magic_action_pure(
    player_data,
    target_id,
    magic_data,
    alch_values=None,
    random_random=None,
    *,
    farming_patch_id=None,
):
    """Apply one closed-contract noncombat cast as a single undoable mutation."""
    spec = magic_data.get(target_id)
    alch_values = alch_values or {}
    random_random = random_random or (lambda: 1.0)
    if not isinstance(spec, Mapping) or magic_target_locked_reasons_pure(
        player_data,
        target_id,
        magic_data,
        alch_values,
        farming_patch_id=farming_patch_id,
    ):
        return player_data, 0.0, {}, {}, False, "Magic target is locked"
    data = _copy_player_data_with_nested(player_data)
    inventory = data.setdefault("inventory", {})
    for rune_name, amount in effective_magic_rune_cost_pure(data, spec.get("rune_cost", {})).items():
        inventory[rune_name] = _non_negative_int(inventory.get(rune_name, 0), 0) - amount
    requirements, _ = _magic_dynamic_requirements_pure(
        data,
        spec,
        alch_values,
        farming_patch_id,
    )
    for item_name, amount in requirements.items():
        inventory[item_name] = _non_negative_int(inventory.get(item_name, 0), 0) - amount

    action = str(spec.get("action", "pure"))
    effect_target_id = str(spec.get("borrowed_spell_id", target_id) or target_id)
    outputs = {}
    secondary = {}

    def add(item, amount):
        quantity = max(0, int(amount))
        if quantity:
            inventory[item] = _non_negative_int(inventory.get(item, 0), 0) + quantity
            outputs[item] = outputs.get(item, 0) + quantity

    if action == "alchemy":
        item = str(data.get("magic_alchemy_item", ""))
        value = _non_negative_int(alch_values.get(item, 0), 0)
        add("Coins", int(value * (.6 if effect_target_id == "high_alchemy" else .4)))
    elif action in {"transform", "produce"}:
        for item, amount in (spec.get("outputs", {}) or {}).items():
            add(str(item), amount)
        if action == "transform" and target_id.startswith("plank_make_"):
            livid_state = data.get("livid_farm", {}) or {}
            if (
                isinstance(livid_state, Mapping)
                and bool(livid_state.get("more_planks_active_this_review"))
                and random_random() < 0.10
            ):
                for item, amount in (spec.get("outputs", {}) or {}).items():
                    add(str(item), amount)
        if spec.get("secondary_skill") and float(spec.get("secondary_exp", 0) or 0) > 0:
            secondary[str(spec["secondary_skill"])] = float(spec["secondary_exp"])
    elif action == "bones_conversion":
        eligible = ("Bones",) if effect_target_id == "bones_to_bananas" else ("Bones", "Big bones")
        output = next(iter((spec.get("outputs", {}) or {"Banana": 1})))
        total = 0
        for item in eligible:
            count = _non_negative_int(inventory.get(item, 0), 0)
            inventory[item] = 0
            total += count
        add(output, total)
    elif action == "bake_pie":
        for raw, (cooked, xp) in _PIE_OUTPUTS.items():
            count = _non_negative_int(inventory.get(raw, 0), 0)
            if count:
                inventory[raw] -= 1
                add(cooked, 1)
                secondary["cooking"] = xp
                break
    elif action == "humidify":
        for empty, filled in _HUMIDIFY_OUTPUTS.items():
            count = _non_negative_int(inventory.get(empty, 0), 0)
            if count:
                inventory[empty] = 0
                add(filled, count)
    elif action == "superglass":
        sand = _non_negative_int(inventory.get("Bucket of sand", 0), 0)
        reagent = next((item for item in ("Soda ash", "Seaweed", "Swamp weed") if _non_negative_int(inventory.get(item, 0), 0) > 0), "")
        count = min(sand, _non_negative_int(inventory.get(reagent, 0), 0))
        inventory["Bucket of sand"] -= count
        inventory[reagent] -= count
        # oldid=6587788: buckets are consumed and each pair independently
        # produces one glass plus a 30% chance of a second (1.30 long-run mean).
        add("Molten glass", count + sum(1 for _ in range(count) if random_random() < 0.30))
        secondary["crafting"] = 10.0 * count
    elif action == "tan_leather":
        hide = str(spec.get("leather_input", "") or "")
        if not hide:
            hide = next(
                item
                for item in _LEATHER_OUTPUTS
                if _non_negative_int(inventory.get(item, 0), 0) > 0
            )
        leather = str(spec.get("leather_output", "") or _LEATHER_OUTPUTS[hide])
        count = min(5, _non_negative_int(inventory.get(hide, 0), 0))
        inventory[hide] -= count
        add(leather, count)
    elif action == "string_jewellery":
        total = 0
        for item, strung_item in _STRINGABLE_AMULETS.items():
            count = _non_negative_int(inventory.get(item, 0), 0)
            if count:
                inventory[item] = 0
                add(strung_item, count)
                total += count
        secondary["crafting"] = 4.0 * total
    elif action == "magic_imbue":
        data["magic_imbue_active"] = True
    elif action == "charge":
        data["magic_charge_active"] = True
        data["magic_charge_ticks_remaining"] = MAGIC_CHARGE_DURATION_TICKS
    elif action == "teleport":
        destination = str(spec.get("destination", "") or "")
        data["magic_last_teleport"] = {
            "target_id": target_id,
            "destination": destination,
        }
        if effect_target_id == "teleport_to_trollheim":
            data["farming_spell_patch"] = "trollheim_herb"
    elif action == "remote_farm":
        data, remote_info = _apply_remote_farm_pure(data)
        data["magic_last_remote_farm"] = remote_info
    elif target_id in {"cure_plant", "fertile_soil"}:
        data, applied, message = _apply_farming_spell_pure(
            data,
            target_id,
            farming_patch_id,
        )
        if not applied:
            return player_data, 0.0, {}, {}, False, message
    elif action == "cure_me":
        statuses = dict(data.get("combat_status_effects", {}) or {})
        statuses.pop("poison", None)
        data["combat_status_effects"] = statuses
    elif action == "monster_examine":
        target = str(data.get("current_combat_target", ""))
        enemy = COMBAT_ENEMY_DATA.get(target, {})
        stats = enemy.get("stats", {}) if isinstance(enemy, Mapping) else {}
        data["magic_last_examine"] = {"target_id": target, "display_name": enemy.get("display_name", target), "stats": dict(stats or {})}

    if spec.get("borrowed_spell_id"):
        from ..logic.livid_farm_logic import consume_arcane_capacitor_charge_pure
        data, consumed, _charge_info = consume_arcane_capacitor_charge_pure(
            data,
            effect_target_id,
        )
        if not consumed:
            return player_data, 0.0, {}, {}, False, "Arcane capacitor charge is unavailable"

    return data, float(spec.get("exp", 0.0) or 0.0), secondary, outputs, True, str(spec.get("display_name", target_id))
