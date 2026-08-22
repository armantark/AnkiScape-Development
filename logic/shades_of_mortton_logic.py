"""Pure Shades of Mort'ton repair, sanctity, production, and cremation loop."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from ..logic_pure.logic_pure import apply_combat_burst_pure
from ..data.shades_of_mortton_data import (
    SHADES_ALTAR_LIGHT_CHANCE,
    SHADES_BRONZE_CHEST_REWARD_GROUPS,
    SHADES_BRONZE_KEY_ROLL_MODIFIERS,
    SHADES_BRONZE_KEYS,
    SHADES_CROWD_REPAIR,
    SHADES_DUTY_IDS,
    SHADES_LOAR_PRAYER_XP,
    SHADES_OIL_SANCTITY_PER_DOSE_TENTHS,
    SHADES_PYRE_LOGS,
    SHADES_REPAIR_CHANCE_BY_HAMMER,
    SHADES_REPAIR_MAX,
    SHADES_REPAIR_PROGRESS,
    SHADES_REPAIR_SANCTITY_TENTHS,
    SHADES_REPAIR_UNLOCK,
    SHADES_RESOURCE_PACK,
    SHADES_RESOURCE_PACK_POINTS,
    SHADES_SANCTITY_DECAY_REVIEWS,
    SHADES_SANCTITY_MAX_TENTHS,
    SHADES_SERUM_SANCTITY_TENTHS,
    SHADES_SHADE_DAMAGE,
    SHADES_SHADE_KILL_SANCTITY_TENTHS,
    SHADES_OF_MORTTON_ACTIVITY_ID,
    SHADES_OF_MORTTON_COMBAT_TARGET_ID,
    shades_of_mortton_loar_enemy_pure,
)
from .treasure_trails_logic import (
    clue_ownership_reason_pure,
    filter_clue_scroll_outputs_pure,
)


SHADES_OF_MORTTON_STATE_VERSION = 1
_VALID_MODES = frozenset({"casual", "advanced"})


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _roll(rng) -> float:
    try:
        return max(0.0, min(0.999999999, float(rng())))
    except (TypeError, ValueError, StopIteration):
        return 0.5


def _quest_completed(data: Mapping[str, Any]) -> bool:
    quests = data.get("quests")
    state = quests.get("shades_of_mortton") if isinstance(quests, Mapping) else None
    return isinstance(state, Mapping) and bool(state.get("completed"))


def _inventory(data: Mapping[str, Any]) -> dict[str, int]:
    source = data.get("inventory")
    if not isinstance(source, Mapping):
        return {}
    return {str(name): _int(amount) for name, amount in source.items()}


def _consume(inventory: dict[str, int], requirements: Mapping[str, int]) -> bool:
    if any(_int(inventory.get(name)) < amount for name, amount in requirements.items()):
        return False
    for name, amount in requirements.items():
        inventory[name] = _int(inventory.get(name)) - amount
        if inventory[name] <= 0:
            inventory.pop(name, None)
    return True


def _add(inventory: dict[str, int], item: str, amount: int = 1) -> None:
    inventory[item] = _int(inventory.get(item)) + amount


def _consume_sacred_oil_doses(inventory: dict[str, int], required: int) -> bool:
    total = sum(
        dose * _int(inventory.get(f"Sacred oil ({dose})"))
        for dose in range(1, 5)
    )
    if total < required:
        return False
    remaining = required
    for dose in range(4, 0, -1):
        item = f"Sacred oil ({dose})"
        while remaining > 0 and _int(inventory.get(item)):
            _consume(inventory, {item: 1})
            used = min(dose, remaining)
            leftover = dose - used
            remaining -= used
            if leftover:
                _add(inventory, f"Sacred oil ({leftover})")
            else:
                _add(inventory, "Vial")
    return True


def default_shades_of_mortton_state_pure() -> dict[str, Any]:
    return {
        "shades_of_mortton": {
            "version": SHADES_OF_MORTTON_STATE_VERSION,
            "active": False,
            "temple_repair": 0,
            "sanctity_tenths": 0,
            "resources": 0,
            "altar_lit": False,
            "sanctity_decay_progress": 0,
            "encounter": {},
            "previous_combat_target": "",
        },
        "shades_of_mortton_policy": {
            "automation_mode": "casual",
            "duty": "repair",
        },
        "shades_of_mortton_repairs": 0,
        "shades_of_mortton_cremations": 0,
        "shades_of_mortton_chests_opened": 0,
        "shades_of_mortton_last_result": "",
    }


def sanitize_shades_of_mortton_policy_pure(raw: Any) -> dict[str, str]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    duty = str(source.get("duty", "repair"))
    return {
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "duty": duty if duty in SHADES_DUTY_IDS else "repair",
    }


def sanitize_shades_of_mortton_loop_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    repair = _int(source.get("temple_repair"), maximum=SHADES_REPAIR_MAX)
    encounter = source.get("encounter")
    return {
        "version": SHADES_OF_MORTTON_STATE_VERSION,
        "active": bool(source.get("active", False)),
        "temple_repair": repair,
        "sanctity_tenths": _int(
            source.get("sanctity_tenths"), maximum=SHADES_SANCTITY_MAX_TENTHS
        ),
        "resources": _int(source.get("resources"), maximum=100),
        "altar_lit": bool(source.get("altar_lit", False)) and repair >= SHADES_REPAIR_UNLOCK,
        "sanctity_decay_progress": _int(
            source.get("sanctity_decay_progress"),
            maximum=SHADES_SANCTITY_DECAY_REVIEWS - 1,
        ),
        "encounter": copy.deepcopy(dict(encounter)) if isinstance(encounter, Mapping) else {},
        "previous_combat_target": str(source.get("previous_combat_target", ""))[:120],
    }


def sanitize_shades_of_mortton_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    loop = sanitize_shades_of_mortton_loop_pure(source.get("shades_of_mortton"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if loop["active"] and active_id not in {"", SHADES_OF_MORTTON_ACTIVITY_ID}:
        loop["active"] = False
        loop["encounter"] = {}
    return {
        "shades_of_mortton": loop,
        "shades_of_mortton_policy": sanitize_shades_of_mortton_policy_pure(
            source.get("shades_of_mortton_policy")
        ),
        "shades_of_mortton_repairs": _int(source.get("shades_of_mortton_repairs")),
        "shades_of_mortton_cremations": _int(
            source.get("shades_of_mortton_cremations")
        ),
        "shades_of_mortton_chests_opened": _int(
            source.get("shades_of_mortton_chests_opened")
        ),
        "shades_of_mortton_last_result": str(
            source.get("shades_of_mortton_last_result", "") or ""
        )[:500],
    }


def set_shades_of_mortton_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_shades_of_mortton_state_pure rebuilds all
    # its keys and deep-copies the nested encounter, so nothing writes through
    # the input.
    data = dict(player_data)
    state = sanitize_shades_of_mortton_state_pure(data)
    candidate = dict(state["shades_of_mortton_policy"])
    candidate.update(dict(payload or {}))
    policy = sanitize_shades_of_mortton_policy_pure(candidate)
    data.update(state)
    data["shades_of_mortton_policy"] = policy
    return data, True, {"message": "Shades of Mort'ton plan saved.", "policy": policy}


def enter_shades_of_mortton_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_shades_of_mortton_state_pure rebuilds all
    # its keys and deep-copies the nested encounter, so nothing writes through
    # the input.
    data = dict(player_data)
    state = sanitize_shades_of_mortton_state_pure(data)
    loop = state["shades_of_mortton"]
    if loop["active"]:
        return data, False, {"reason": "Shades of Mort'ton is already active."}
    if not _quest_completed(data):
        return data, False, {"reason": "Complete Shades of Mort'ton first."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != SHADES_OF_MORTTON_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {"reason": "Finish or leave the current Combat encounter first."}

    candidate = dict(state["shades_of_mortton_policy"])
    candidate.update(dict(payload or {}))
    policy = sanitize_shades_of_mortton_policy_pure(candidate)
    loop["active"] = True
    loop["previous_combat_target"] = str(data.get("current_combat_target", ""))[:120]
    data.update(state)
    data["shades_of_mortton_policy"] = policy
    data["shades_of_mortton"] = loop
    data["activity_session"] = {"active_id": SHADES_OF_MORTTON_ACTIVITY_ID}
    data["current_utility"] = SHADES_OF_MORTTON_ACTIVITY_ID
    data["combat_encounter"] = {}
    data["shades_of_mortton_last_result"] = "Entered Mort'ton · the open temple loop is active"
    return data, True, {"message": data["shades_of_mortton_last_result"]}


def leave_shades_of_mortton_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_shades_of_mortton_state_pure rebuilds all
    # its keys and deep-copies the nested encounter, so nothing writes through
    # the input.
    data = dict(player_data)
    state = sanitize_shades_of_mortton_state_pure(data)
    loop = state["shades_of_mortton"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not loop["active"] or active_id != SHADES_OF_MORTTON_ACTIVITY_ID:
        return data, False, {"reason": "No Shades of Mort'ton loop is active."}
    loop["active"] = False
    loop["encounter"] = {}
    data.update(state)
    data["shades_of_mortton"] = loop
    data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = loop["previous_combat_target"]
    data["shades_of_mortton_last_result"] = "Left Mort'ton · temple and sanctity meters preserved"
    return data, True, {"message": data["shades_of_mortton_last_result"]}


def _apply_world_beat(loop: dict[str, Any], population: str) -> int:
    crowd = SHADES_CROWD_REPAIR.get(str(population).lower(), SHADES_CROWD_REPAIR["normal"])
    delta = crowd - SHADES_SHADE_DAMAGE
    loop["temple_repair"] = max(
        0, min(SHADES_REPAIR_MAX, int(loop["temple_repair"]) + delta)
    )
    if loop["temple_repair"] < SHADES_REPAIR_UNLOCK:
        loop["altar_lit"] = False
    progress = int(loop["sanctity_decay_progress"]) + 1
    if progress >= SHADES_SANCTITY_DECAY_REVIEWS:
        loop["sanctity_tenths"] = max(0, int(loop["sanctity_tenths"]) - 10)
        progress = 0
    loop["sanctity_decay_progress"] = progress
    return delta


def _choose_duty(data: Mapping[str, Any], loop: Mapping[str, Any]) -> str:
    policy = data["shades_of_mortton_policy"]
    if policy["automation_mode"] == "advanced":
        return policy["duty"]
    inventory = _inventory(data)
    can_supply = int(loop["resources"]) > 0 or all(
        _int(inventory.get(name)) >= amount for name, amount in SHADES_RESOURCE_PACK.items()
    )
    if int(loop["temple_repair"]) < SHADES_REPAIR_UNLOCK and can_supply:
        return "repair"
    if _int(inventory.get("Loar remains")) and any(
        _int(inventory.get(name)) for name in SHADES_PYRE_LOGS
    ):
        return "cremate"
    return "combat"


def _repair(
    data: dict[str, Any], loop: dict[str, Any], rng
) -> tuple[dict[str, float], str, dict[str, Any]]:
    inventory = _inventory(data)
    hammer = "Flamtaer hammer" if _int(inventory.get("Flamtaer hammer")) else "Hammer"
    if not _int(inventory.get(hammer)):
        return {}, "A hammer is required to repair the temple", {"blocked": True}
    if int(loop["resources"]) <= 0:
        if not _consume(inventory, SHADES_RESOURCE_PACK):
            return {}, "Missing a timber beam, limestone brick, or five swamp paste", {"blocked": True}
        loop["resources"] = SHADES_RESOURCE_PACK_POINTS
    success = _roll(rng) < SHADES_REPAIR_CHANCE_BY_HAMMER[hammer]
    if success:
        xp = float(20 + int(_roll(rng) * 16))
        loop["resources"] -= 1
        loop["temple_repair"] = min(
            SHADES_REPAIR_MAX, int(loop["temple_repair"]) + SHADES_REPAIR_PROGRESS
        )
        loop["sanctity_tenths"] = min(
            SHADES_SANCTITY_MAX_TENTHS,
            int(loop["sanctity_tenths"]) + SHADES_REPAIR_SANCTITY_TENTHS,
        )
        data["shades_of_mortton_repairs"] = _int(data.get("shades_of_mortton_repairs")) + 1
        status = f"Repaired the temple to {loop['temple_repair']}%"
    else:
        xp = float(5 + int(_roll(rng) * 5))
        status = "Worked on the wall without completing a repair point"
    data["inventory"] = inventory
    return {"crafting": xp}, status, {"success": success, "hammer": hammer}


def _fight_loar(
    data: dict[str, Any], loop: dict[str, Any], rng, equipment_data
) -> tuple[dict[str, float], str, dict[str, Any]]:
    encounter = loop.get("encounter") or {
        "target_id": SHADES_OF_MORTTON_COMBAT_TARGET_ID,
        "enemy_lifepoints": 380,
    }
    data["current_combat_target"] = SHADES_OF_MORTTON_COMBAT_TARGET_ID
    data["combat_encounter"] = copy.deepcopy(encounter)
    updated, ok, result = apply_combat_burst_pure(
        data,
        {SHADES_OF_MORTTON_COMBAT_TARGET_ID: shades_of_mortton_loar_enemy_pure()},
        equipment_data,
        ticks=6,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=False,
        allow_bank_run=True,
    )
    data.clear()
    data.update(updated)
    if not ok:
        return {}, str(result.get("reason", "Combat could not advance")), {"combat_failed": True, **result}
    if result.get("killed"):
        loop["encounter"] = {}
        loop["sanctity_tenths"] = min(
            SHADES_SANCTITY_MAX_TENTHS,
            int(loop["sanctity_tenths"]) + SHADES_SHADE_KILL_SANCTITY_TENTHS,
        )
        return {}, "Defeated a Loar Shade · +2% sanctity", result
    after = data.get("combat_encounter")
    loop["encounter"] = copy.deepcopy(dict(after)) if isinstance(after, Mapping) else {}
    return {}, "Fought a Loar Shade for six live ticks", result


def _cremate(
    data: dict[str, Any], loop: dict[str, Any], rng
) -> tuple[dict[str, float], str, dict[str, Any]]:
    inventory = _inventory(data)
    log_name = next((name for name in SHADES_PYRE_LOGS if _int(inventory.get(name))), "")
    if not log_name or not _int(inventory.get("Loar remains")):
        return {}, "Loar remains and compatible pyre logs are required", {"blocked": True}
    if _int(data.get("firemaking_level"), 1) < int(SHADES_PYRE_LOGS[log_name]["level"]):
        return {}, f"Requires level {SHADES_PYRE_LOGS[log_name]['level']} Firemaking", {"blocked": True}
    _consume(inventory, {log_name: 1, "Loar remains": 1})
    reward_roll = _roll(rng)
    if reward_roll < 1.0 / 3.0:
        key = SHADES_BRONZE_KEYS[min(int(_roll(rng) * len(SHADES_BRONZE_KEYS)), len(SHADES_BRONZE_KEYS) - 1)]
        _add(inventory, key)
        reward = key
    else:
        coins = 400 + int(_roll(rng) * 101)
        _add(inventory, "Coins", coins)
        reward = f"{coins} coins"
    data["inventory"] = inventory
    data["shades_of_mortton_cremations"] = _int(data.get("shades_of_mortton_cremations")) + 1
    return (
        {
            "firemaking": float(SHADES_PYRE_LOGS[log_name]["cremation_xp"]),
            "prayer": SHADES_LOAR_PRAYER_XP[log_name],
        },
        f"Cremated Loar remains with {log_name} · {reward}",
        {"reward": reward, "pyre_logs": log_name},
    )


def apply_shades_of_mortton_review_pure(
    player_data: Mapping[str, Any],
    rng=lambda: 0.5,
    *,
    productive: bool = True,
    population: str = "normal",
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_shades_of_mortton_state_pure rebuilds all
    # its keys and deep-copies the nested encounter, so nothing writes through
    # the input.
    data = dict(player_data)
    state = sanitize_shades_of_mortton_state_pure(data)
    loop = state["shades_of_mortton"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not loop["active"] or active_id != SHADES_OF_MORTTON_ACTIVITY_ID:
        return data, False, {"reason": "No Shades of Mort'ton loop is active."}
    data.update(state)
    world_delta = _apply_world_beat(loop, population)
    duty = "idle"
    skill_xp: dict[str, float] = {}
    detail: dict[str, Any] = {}
    status = "The temple population shifted while you waited"
    if productive:
        duty = _choose_duty(data, loop)
        if duty == "repair":
            skill_xp, status, detail = _repair(data, loop, rng)
        elif duty == "combat":
            skill_xp, status, detail = _fight_loar(data, loop, rng, equipment_data or {})
        else:
            skill_xp, status, detail = _cremate(data, loop, rng)
    data["shades_of_mortton"] = sanitize_shades_of_mortton_loop_pure(loop)
    data["shades_of_mortton_last_result"] = status
    return data, True, {
        "duty": duty,
        "skill_xp": skill_xp,
        "status": status,
        "population": str(population).lower(),
        "communal_repair_delta": world_delta,
        **detail,
    }


def light_shades_altar_pure(
    player_data: Mapping[str, Any], rng=lambda: 0.5
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_shades_of_mortton_state_pure rebuilds all
    # its keys and deep-copies the nested encounter, so nothing writes through
    # the input.
    data = dict(player_data)
    state = sanitize_shades_of_mortton_state_pure(data)
    loop = state["shades_of_mortton"]
    inventory = _inventory(data)
    if not loop["active"]:
        return data, False, {"reason": "Enter Shades of Mort'ton first."}
    if int(loop["temple_repair"]) < SHADES_REPAIR_UNLOCK:
        return data, False, {"reason": "The temple must reach 99% repair."}
    if int(loop["sanctity_tenths"]) <= 100:
        return data, False, {"reason": "More than 10% sanctity is required."}
    if not _int(inventory.get("Tinderbox")):
        return data, False, {"reason": "A tinderbox is required."}
    if loop["altar_lit"]:
        return data, False, {"reason": "The fire altar is already lit."}
    if _roll(rng) >= SHADES_ALTAR_LIGHT_CHANCE:
        return data, True, {"message": "The fire altar failed to light.", "skill_xp": {}}
    loop["altar_lit"] = True
    data.update(state)
    data["shades_of_mortton"] = loop
    data["shades_of_mortton_last_result"] = "Lit the fire altar"
    return data, True, {"message": "Lit the fire altar.", "skill_xp": {"firemaking": 100.0}}


def bless_shades_item_pure(
    player_data: Mapping[str, Any], item_name: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_shades_of_mortton_state_pure rebuilds all
    # its keys and deep-copies the nested encounter, so nothing writes through
    # the input.
    data = dict(player_data)
    state = sanitize_shades_of_mortton_state_pure(data)
    loop = state["shades_of_mortton"]
    inventory = _inventory(data)
    conversions = {
        **{
            f"Olive oil ({dose})": (f"Sacred oil ({dose})", dose * SHADES_OIL_SANCTITY_PER_DOSE_TENTHS, 101)
            for dose in range(1, 5)
        },
        **{
            f"Serum 207 ({dose})": (f"Serum 208 ({dose})", SHADES_SERUM_SANCTITY_TENTHS, 200)
            for dose in range(1, 5)
        },
    }
    conversion = conversions.get(str(item_name))
    if not loop["active"] or not loop["altar_lit"]:
        return data, False, {"reason": "The Mort'ton fire altar must be active and lit."}
    if conversion is None:
        return data, False, {"reason": "That item cannot be blessed here."}
    output, cost, minimum = conversion
    if int(loop["sanctity_tenths"]) < minimum:
        return data, False, {"reason": f"At least {minimum / 10:g}% sanctity is required."}
    if not _consume(inventory, {str(item_name): 1}):
        return data, False, {"reason": f"No {item_name} is available."}
    loop["sanctity_tenths"] -= cost
    _add(inventory, output)
    data.update(state)
    data["shades_of_mortton"] = loop
    data["inventory"] = inventory
    data["shades_of_mortton_last_result"] = f"Blessed {item_name} into {output}"
    return data, True, {"message": data["shades_of_mortton_last_result"], "output": output}


def make_shades_pyre_logs_pure(
    player_data: Mapping[str, Any], output_name: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_shades_of_mortton_state_pure rebuilds all
    # its keys and deep-copies the nested encounter, so nothing writes through
    # the input.
    data = dict(player_data)
    recipe = SHADES_PYRE_LOGS.get(str(output_name))
    if recipe is None:
        return data, False, {"reason": "Unknown pyre-log recipe."}
    if _int(data.get("firemaking_level"), 1) < int(recipe["level"]):
        return data, False, {"reason": f"Requires level {recipe['level']} Firemaking."}
    inventory = _inventory(data)
    doses = int(recipe["oil_doses"])
    if not _int(inventory.get(str(recipe["base_log"]))) or not _consume_sacred_oil_doses(
        dict(inventory), doses
    ):
        return data, False, {"reason": f"Requires {recipe['base_log']} and {doses} sacred-oil doses."}
    _consume(inventory, {str(recipe["base_log"]): 1})
    _consume_sacred_oil_doses(inventory, doses)
    _add(inventory, str(output_name))
    data["inventory"] = inventory
    return data, True, {
        "message": f"Made {output_name}.",
        "skill_xp": {"firemaking": float(recipe["creation_xp"])},
    }


def open_shades_bronze_chest_pure(
    player_data: Mapping[str, Any], key_name: str, rng=lambda: 0.5
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_shades_of_mortton_state_pure rebuilds all
    # its keys and deep-copies the nested encounter, so nothing writes through
    # the input.
    data = dict(player_data)
    if not _quest_completed(data):
        return data, False, {"reason": "Complete Shades of Mort'ton first."}
    if str(key_name) not in SHADES_BRONZE_KEYS:
        return data, False, {"reason": "A low bronze shade key is required."}
    inventory = _inventory(data)
    if not _consume(inventory, {str(key_name): 1}):
        return data, False, {"reason": f"No {key_name} is available."}
    coins = 10 + int(_roll(rng) * 261)
    reward_roll = (
        _roll(rng)
        * 128
        * SHADES_BRONZE_KEY_ROLL_MODIFIERS[str(key_name)]
    )
    cumulative_slots = 0
    reward_rows = SHADES_BRONZE_CHEST_REWARD_GROUPS[-1]["rewards"]
    # Darkan's DropList sorts chance groups ascending before assigning roll
    # intervals. Keeping that non-obvious order is what makes better-colour
    # keys increase access to the rare Fine-cloth and rune groups.
    for group in sorted(
        SHADES_BRONZE_CHEST_REWARD_GROUPS, key=lambda row: int(row["slots"])
    ):
        cumulative_slots += int(group["slots"])
        if reward_roll < cumulative_slots:
            reward_rows = group["rewards"]
            break
    reward_row = reward_rows[int(_roll(rng) * len(reward_rows))]
    reward = str(reward_row[0])
    minimum, maximum = int(reward_row[1]), int(reward_row[2])
    quantity = minimum
    if maximum > minimum:
        quantity += int(_roll(rng) * (maximum - minimum + 1))
    _add(inventory, "Coins", coins)
    rewards = {"Coins": coins}
    ownership_reason = clue_ownership_reason_pure(data)
    main_rewards = filter_clue_scroll_outputs_pure(data, {reward: quantity})
    clue_refusal_reason = (
        ownership_reason
        if ownership_reason and reward not in main_rewards
        else ""
    )
    for item_name, amount in main_rewards.items():
        _add(inventory, item_name, amount)
        rewards[item_name] = amount
    # The period page says paste is occasional while Darkan's zero-rate table
    # makes it unconditional. A single disclosed breadth abstraction preserves
    # the attested optional route without claiming either conflicting behavior.
    if _roll(rng) < 0.25:
        paste = 10 + int(_roll(rng) * 11)
        _add(inventory, "Swamp paste", paste)
        rewards["Swamp paste"] = paste
    data["inventory"] = inventory
    data["shades_of_mortton_chests_opened"] = _int(
        data.get("shades_of_mortton_chests_opened")
    ) + 1
    reward_summary = (
        f"{reward} x{quantity}" if reward in main_rewards else "no extra reward"
    )
    data["shades_of_mortton_last_result"] = (
        f"Opened a bronze chest · {reward_summary}"
        + (f" · {clue_refusal_reason}" if clue_refusal_reason else "")
    )
    return data, True, {
        "message": data["shades_of_mortton_last_result"],
        "rewards": rewards,
        "clue_refusal_reason": clue_refusal_reason,
    }


def shades_of_mortton_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_shades_of_mortton_state_pure(player_data)
    loop = state["shades_of_mortton"]
    activity = player_data.get("activity_session")
    active_id = str(activity.get("active_id", "")) if isinstance(activity, Mapping) else ""
    encounter = player_data.get("combat_encounter")
    entry_reason = ""
    quest_complete = _quest_completed(player_data)
    if not quest_complete:
        entry_reason = "Complete Shades of Mort'ton first."
    elif active_id and active_id != SHADES_OF_MORTTON_ACTIVITY_ID:
        entry_reason = "Finish the active persistent activity first."
    elif isinstance(encounter, Mapping) and encounter:
        entry_reason = "Finish or leave the current Combat encounter first."
    return {
        "active": loop["active"],
        "quest_complete": quest_complete,
        "can_enter": not entry_reason,
        "entry_reason": entry_reason,
        "temple_repair": loop["temple_repair"],
        "sanctity": loop["sanctity_tenths"] / 10.0,
        "resources": loop["resources"],
        "altar_lit": loop["altar_lit"],
        "policy": state["shades_of_mortton_policy"],
        "repairs": state["shades_of_mortton_repairs"],
        "cremations": state["shades_of_mortton_cremations"],
        "chests_opened": state["shades_of_mortton_chests_opened"],
        "last_result": state["shades_of_mortton_last_result"],
    }


def apply_shades_of_mortton_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    *,
    rng=lambda: 0.5,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "enter":
        return enter_shades_of_mortton_pure(player_data, body)
    if action_id == "leave":
        return leave_shades_of_mortton_pure(player_data)
    if action_id == "set_policy":
        return set_shades_of_mortton_policy_pure(player_data, body)
    if action_id == "light_altar":
        return light_shades_altar_pure(player_data, rng)
    if action_id == "bless":
        return bless_shades_item_pure(player_data, str(body.get("item_name", "")))
    if action_id == "make_pyre_logs":
        return make_shades_pyre_logs_pure(player_data, str(body.get("output_name", "")))
    if action_id == "open_bronze_chest":
        return open_shades_bronze_chest_pure(
            player_data, str(body.get("key_name", "")), rng
        )
    # Shallow on purpose: an unknown action changes nothing, and the failure
    # branch in every caller drops the returned save without touching it.
    return dict(player_data), False, {"reason": "Unknown Shades of Mort'ton action."}
