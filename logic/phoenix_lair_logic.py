"""Pure, review-driven Phoenix Lair session mechanics."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    combat_target_locked_reasons_pure,
)
from .inventory_pure import (
    CARRIED_CAPACITY,
    apply_carried_layout_pure,
    carried_advanced_for,
    clamp_carried_view_to_bank,
)
from .pet_logic import acquire_pet_pure
from ..data.item_values import STACKABLE_ITEM_NAMES
from ..data.pet_data import PETS_BY_ID
from ..data.phoenix_lair_data import (
    CRACKED_PHOENIX_EGG_ITEM,
    PHOENIX_EGG_ITEM,
    PHOENIX_EGG_CONTEXT_ID,
    PHOENIX_LAIR_ACTIVITY_ID,
    PHOENIX_LAIR_EGG_CHANCE,
    PHOENIX_LAIR_FIXED_REWARDS,
    PHOENIX_LAIR_GUARDIAN_COUNT,
    PHOENIX_LAIR_GUARDIAN_IDS,
    PHOENIX_LAIR_GUARDIAN_TARGET_ID,
    PHOENIX_LAIR_GUARDIANS,
    PHOENIX_LAIR_PHOENIX,
    PHOENIX_LAIR_PHOENIX_TARGET_ID,
    PHOENIX_LAIR_WORLD_DAY_REVIEWS,
    PHOENIX_QUILL_ITEM,
)
from ..core.review_context import remember_review_context_choice_pure
from ..core.tool_belt import tool_on_belt


PHOENIX_LAIR_STATE_VERSION = 1
PHOENIX_EGG_CHOICES = {
    "clap": (PHOENIX_EGG_ITEM, "cute_phoenix_eggling"),
    "kick": (CRACKED_PHOENIX_EGG_ITEM, "mean_phoenix_eggling"),
}


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    return _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0


def _world_day(player_data: Mapping[str, Any]) -> int:
    return _answered_cards(player_data) // PHOENIX_LAIR_WORLD_DAY_REVIEWS


def default_phoenix_lair_state_pure() -> dict[str, Any]:
    return {
        "version": PHOENIX_LAIR_STATE_VERSION,
        "active": False,
        "phase": "idle",
        "guardian_roster": [],
        "guardian_lifepoints": 0,
        "guardian_max_lifepoints": 0,
        "guardian_review_index": 0,
        "phoenix_lifepoints": 0,
        "phoenix_review_count": 0,
        "encounter": {},
        "previous_combat_target": "",
        "last_completed_world_day": -1,
        "runs_completed": 0,
        "pending_egg": False,
        "last_result": "",
    }


def _sanitize_encounter(raw: Any, target_id: str, lifepoints: int) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    encounter = {
        str(key): copy.deepcopy(value)
        for key, value in source.items()
        if isinstance(key, str)
    }
    if lifepoints > 0 and target_id:
        encounter["target_id"] = target_id
        encounter["enemy_lifepoints"] = lifepoints
    else:
        encounter = {}
    return encounter


def sanitize_phoenix_lair_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_phoenix_lair_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    roster = [
        str(guardian_id)
        for guardian_id in (source.get("guardian_roster", ()) or ())
        if str(guardian_id) in PHOENIX_LAIR_GUARDIANS
    ][:PHOENIX_LAIR_GUARDIAN_COUNT]
    phase = str(source.get("phase", "idle"))
    if phase not in {"idle", "guardians", "prepare", "phoenix"}:
        phase = "idle"
    active = bool(source.get("active", False))
    if not active:
        phase = "idle"
    guardian_max = sum(
        _int(PHOENIX_LAIR_GUARDIANS[guardian_id]["stats"]["hitpoints"], 1, minimum=1)
        for guardian_id in roster
    )
    guardian_lp = min(
        guardian_max,
        _int(source.get("guardian_lifepoints"), guardian_max),
    )
    phoenix_max = _int(PHOENIX_LAIR_PHOENIX["stats"]["hitpoints"], 1, minimum=1)
    phoenix_lp = min(
        phoenix_max,
        _int(source.get("phoenix_lifepoints"), phoenix_max),
    )
    if active and phase == "guardians" and len(roster) != PHOENIX_LAIR_GUARDIAN_COUNT:
        active = False
        phase = "idle"
        guardian_lp = 0
    target_id = (
        PHOENIX_LAIR_GUARDIAN_TARGET_ID
        if phase == "guardians"
        else PHOENIX_LAIR_PHOENIX_TARGET_ID
        if phase == "phoenix"
        else ""
    )
    lifepoints = guardian_lp if phase == "guardians" else phoenix_lp
    return {
        **defaults,
        "active": active,
        "phase": phase,
        "guardian_roster": roster,
        "guardian_lifepoints": guardian_lp if active else 0,
        "guardian_max_lifepoints": guardian_max if active else 0,
        "guardian_review_index": _int(source.get("guardian_review_index")),
        "phoenix_lifepoints": phoenix_lp if active and phase == "phoenix" else 0,
        "phoenix_review_count": _int(source.get("phoenix_review_count")),
        "encounter": _sanitize_encounter(source.get("encounter"), target_id, lifepoints),
        "previous_combat_target": str(source.get("previous_combat_target", ""))[:120],
        "last_completed_world_day": max(-1, _int(source.get("last_completed_world_day"), -1, minimum=-1)),
        "runs_completed": _int(source.get("runs_completed")),
        "pending_egg": bool(source.get("pending_egg", False)),
        "last_result": str(source.get("last_result", ""))[:500],
    }


def _advanced_carried_pack(player_data: Mapping[str, Any]) -> dict[str, int]:
    inventory = player_data.get("inventory")
    layouts = player_data.get("carried_layout")
    layout = (
        layouts.get(PHOENIX_LAIR_ACTIVITY_ID)
        if isinstance(layouts, Mapping)
        else None
    )
    if isinstance(layout, Mapping) and layout:
        return apply_carried_layout_pure(
            inventory if isinstance(inventory, Mapping) else {},
            layout,
            CARRIED_CAPACITY,
            STACKABLE_ITEM_NAMES,
        )
    carried_root = player_data.get("carried_inventory")
    carried = (
        carried_root.get(PHOENIX_LAIR_ACTIVITY_ID)
        if isinstance(carried_root, Mapping)
        else None
    )
    return clamp_carried_view_to_bank(carried, inventory)


def _tool_available(player_data: Mapping[str, Any], item_name: str) -> bool:
    if tool_on_belt(player_data, item_name):
        return True
    inventory = player_data.get("inventory")
    if not carried_advanced_for(player_data, PHOENIX_LAIR_ACTIVITY_ID):
        return isinstance(inventory, Mapping) and _int(inventory.get(item_name)) > 0

    return _int(_advanced_carried_pack(player_data).get(item_name)) > 0


def _tool_location_label(player_data: Mapping[str, Any]) -> str:
    return (
        "carried pack or toolbelt"
        if carried_advanced_for(player_data, PHOENIX_LAIR_ACTIVITY_ID)
        else "Bank or toolbelt"
    )


def _quest_complete(player_data: Mapping[str, Any]) -> bool:
    quests = player_data.get("quests")
    quest = quests.get("in_pyre_need") if isinstance(quests, Mapping) else None
    return isinstance(quest, Mapping) and bool(quest.get("completed"))


def _roll_guardian(rng) -> str:
    try:
        roll = min(0.999999999, max(0.0, float(rng())))
    except (TypeError, ValueError, OverflowError):
        roll = 0.0
    return PHOENIX_LAIR_GUARDIAN_IDS[int(roll * len(PHOENIX_LAIR_GUARDIAN_IDS))]


def _guardian_front_enemy(state: Mapping[str, Any]) -> dict[str, Any]:
    roster = list(state.get("guardian_roster", ()) or ())
    index = _int(state.get("guardian_review_index")) % max(1, len(roster))
    current = PHOENIX_LAIR_GUARDIANS[roster[index]]
    maximum = _int(state.get("guardian_max_lifepoints"), 1, minimum=1)
    return {
        **copy.deepcopy(current),
        "display_name": "Reborn guardian front",
        "npc_id": 0,
        "stats": {**copy.deepcopy(current["stats"]), "hitpoints": maximum},
        "drops": {"guaranteed": (), "tables": ()},
        "slayer_xp": 0.0,
        "source": (
            "Five mandatory cavern blockers sampled from the six period Reborn variants; "
            "one-per-cavern roster is a bounded traversal abstraction"
        ),
    }


def phoenix_lair_view_pure(
    player_data: Mapping[str, Any],
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state = sanitize_phoenix_lair_state_pure(player_data.get("phoenix_lair"))
    missing = []
    if not _quest_complete(player_data):
        missing.append("Complete In Pyre Need")
    if _int(player_data.get("slayer_level"), 1, minimum=1) < 51:
        missing.append("Slayer level 51")
    missing_tools = [
        tool
        for tool in ("Knife", "Secateurs", "Tinderbox")
        if not _tool_available(player_data, tool)
    ]
    if missing_tools:
        missing.append(
            f"{', '.join(missing_tools)} in {_tool_location_label(player_data)}"
        )
    current_day = _world_day(player_data)
    daily_ready = current_day > state["last_completed_world_day"]
    current_guardian = ""
    current_attack_style = ""
    if state["guardian_roster"]:
        index = state["guardian_review_index"] % len(state["guardian_roster"])
        guardian = PHOENIX_LAIR_GUARDIANS[state["guardian_roster"][index]]
        current_guardian = guardian["display_name"]
        current_attack_style = guardian["attack_style"]
    return {
        **state,
        "requirements_met": not missing,
        "missing_requirements": tuple(missing),
        "daily_ready": daily_ready,
        "reviews_to_reset": (
            0
            if daily_ready
            else PHOENIX_LAIR_WORLD_DAY_REVIEWS
            - (_answered_cards(player_data) % PHOENIX_LAIR_WORLD_DAY_REVIEWS)
        ),
        "current_guardian": current_guardian,
        "current_attack_style": current_attack_style,
        "egg_chance_label": "1 in 1,000 per completion",
    }


def _end_run(data: dict[str, Any], state: dict[str, Any], message: str) -> None:
    state["active"] = False
    state["phase"] = "idle"
    state["guardian_roster"] = []
    state["guardian_lifepoints"] = 0
    state["guardian_max_lifepoints"] = 0
    state["phoenix_lifepoints"] = 0
    state["encounter"] = {}
    state["last_result"] = message[:500]
    data["phoenix_lair"] = state
    data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(state.get("previous_combat_target", ""))


def apply_phoenix_lair_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    *,
    rng=None,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the run state and its encounter are rebuilt as deep
    # copies, and every cross-module receiver rebuilds before writing.
    data = dict(player_data)
    state = sanitize_phoenix_lair_state_pure(data.get("phoenix_lair"))
    data["phoenix_lair"] = state
    rng = rng or (lambda: 0.0)

    if action_id == "enter":
        if state["active"]:
            data["activity_session"] = {"active_id": PHOENIX_LAIR_ACTIVITY_ID}
            data["current_utility"] = PHOENIX_LAIR_ACTIVITY_ID
            return data, True, {"message": "Phoenix Lair run selected for reviews."}
        active_session = data.get("activity_session")
        if isinstance(active_session, Mapping) and active_session.get("active_id"):
            return data, False, {"reason": "Another persistent activity is active."}
        if not _quest_complete(data):
            return data, False, {"reason": "Complete In Pyre Need first."}
        if _int(data.get("slayer_level"), 1, minimum=1) < 51:
            return data, False, {"reason": "Phoenix Lair requires Slayer level 51."}
        missing_tools = [
            tool
            for tool in ("Knife", "Secateurs", "Tinderbox")
            if not _tool_available(data, tool)
        ]
        if missing_tools:
            return data, False, {
                "reason": (
                    f"Missing tools from {_tool_location_label(data)}: "
                    + ", ".join(missing_tools)
                    + "."
                )
            }
        if _world_day(data) <= state["last_completed_world_day"]:
            return data, False, {"reason": "The Phoenix has already rewarded you this world day."}
        if carried_advanced_for(data, PHOENIX_LAIR_ACTIVITY_ID):
            carried_root = dict(data.get("carried_inventory") or {})
            carried_pack = _advanced_carried_pack(data)
            if carried_pack:
                carried_root[PHOENIX_LAIR_ACTIVITY_ID] = carried_pack
            else:
                carried_root.pop(PHOENIX_LAIR_ACTIVITY_ID, None)
            data["carried_inventory"] = carried_root
        roster = [_roll_guardian(rng) for _ in range(PHOENIX_LAIR_GUARDIAN_COUNT)]
        maximum = sum(
            _int(PHOENIX_LAIR_GUARDIANS[guardian_id]["stats"]["hitpoints"], 1, minimum=1)
            for guardian_id in roster
        )
        state.update(
            {
                "active": True,
                "phase": "guardians",
                "guardian_roster": roster,
                "guardian_lifepoints": maximum,
                "guardian_max_lifepoints": maximum,
                "guardian_review_index": 0,
                "phoenix_lifepoints": 0,
                "phoenix_review_count": 0,
                "encounter": {
                    "target_id": PHOENIX_LAIR_GUARDIAN_TARGET_ID,
                    "enemy_lifepoints": maximum,
                },
                "previous_combat_target": str(data.get("current_combat_target", ""))[:120],
                "last_result": "Entered the Phoenix Lair. The Reborn guardian front blocks five caverns.",
            }
        )
        data["current_combat_target"] = PHOENIX_LAIR_GUARDIAN_TARGET_ID
        data["combat_encounter"] = copy.deepcopy(state["encounter"])
        enemy_data = {PHOENIX_LAIR_GUARDIAN_TARGET_ID: _guardian_front_enemy(state)}
        locked = combat_target_locked_reasons_pure(
            data,
            PHOENIX_LAIR_GUARDIAN_TARGET_ID,
            enemy_data,
            equipment_data=equipment_data or {},
        )
        if locked:
            # Shallow rollback: only top-level keys of the local copy were
            # written, and _apply_phoenix_lair_command reads just the reason
            # when the command fails, so this save is never stored.
            return dict(player_data), False, {
                "reason": "Combat loadout is not ready: " + "; ".join(locked)
            }
        data["phoenix_lair"] = state
        data["activity_session"] = {"active_id": PHOENIX_LAIR_ACTIVITY_ID}
        data["current_utility"] = PHOENIX_LAIR_ACTIVITY_ID
        return data, True, {"message": state["last_result"]}

    if action_id == "leave":
        if not state["active"]:
            return data, False, {"reason": "No Phoenix Lair run is active."}
        _end_run(data, state, "Abandoned the Phoenix Lair; unfinished ritual progress was lost.")
        return data, True, {"message": state["last_result"]}

    return data, False, {"reason": "Unknown Phoenix Lair command."}


def _apply_phoenix_dust_drain(data: dict[str, Any]) -> None:
    levels = dict(data.get("combat_current_levels", {}) or {})
    for skill in ("attack", "magic", "ranged"):
        base = _int(data.get(f"{skill}_level"), 1, minimum=1)
        current = _int(levels.get(skill), base, minimum=1)
        levels[skill] = max(1, current // 2)
    data["combat_current_levels"] = levels


def _merge_xp_rewards(*rows: Mapping[str, Any]) -> dict[str, float]:
    merged: dict[str, float] = {}
    for row in rows:
        for key, amount in row.items():
            merged[str(key)] = merged.get(str(key), 0.0) + _float(amount)
    return merged


def apply_phoenix_lair_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the run state and its encounter are rebuilt as deep
    # copies, and every cross-module receiver rebuilds before writing.
    data = dict(player_data)
    state = sanitize_phoenix_lair_state_pure(data.get("phoenix_lair"))
    if not state["active"]:
        return data, False, {"reason": "Enter the Phoenix Lair before training it."}

    if state["phase"] == "prepare":
        state["phase"] = "phoenix"
        state["phoenix_lifepoints"] = _int(
            PHOENIX_LAIR_PHOENIX["stats"]["hitpoints"], 1, minimum=1
        )
        state["encounter"] = {
            "target_id": PHOENIX_LAIR_PHOENIX_TARGET_ID,
            "enemy_lifepoints": state["phoenix_lifepoints"],
        }
        state["last_result"] = "Cut five twigs into ribbons and built the pyre. The Phoenix has appeared."
        data["phoenix_lair"] = state
        data["current_combat_target"] = PHOENIX_LAIR_PHOENIX_TARGET_ID
        data["combat_encounter"] = copy.deepcopy(state["encounter"])
        data["activity_session"] = {"active_id": PHOENIX_LAIR_ACTIVITY_ID}
        return data, True, {
            "status": state["last_result"],
            "phase_advanced": True,
            "xp_rewards": {},
        }

    if state["phase"] == "guardians":
        target_id = PHOENIX_LAIR_GUARDIAN_TARGET_ID
        enemy = _guardian_front_enemy(state)
        lifepoints = state["guardian_lifepoints"]
    elif state["phase"] == "phoenix":
        target_id = PHOENIX_LAIR_PHOENIX_TARGET_ID
        enemy = copy.deepcopy(PHOENIX_LAIR_PHOENIX)
        lifepoints = state["phoenix_lifepoints"]
        state["phoenix_review_count"] += 1
    else:
        return data, False, {"reason": "Phoenix Lair session state is invalid."}

    data["current_combat_target"] = target_id
    data["combat_encounter"] = _sanitize_encounter(state.get("encounter"), target_id, lifepoints)
    # The bounded encounter cannot be left mid-fight, so the engine's
    # auto-flee is suspended for the burst and restored after — the engine
    # reads the boolean combat_auto_flee, not the old percent key, which
    # this family zeroed for months without effect.
    auto_flee = data.get("combat_auto_flee", True)
    data["combat_auto_flee"] = False
    data, ok, combat_result = apply_combat_burst_pure(
        data,
        {target_id: enemy},
        equipment_data or {},
        ticks=6,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=False,
        allow_bank_run=False,
    )
    data["combat_auto_flee"] = auto_flee
    if not ok:
        # Shallow rollback: apply_combat_burst_pure copies nested values before
        # touching them, so nothing of the input was written, and
        # _handle_phoenix_lair_answer reads only the result when ok is False.
        return dict(player_data), False, combat_result

    if combat_result.get("died"):
        _end_run(data, state, "Defeated in the Phoenix Lair; the unfinished ritual was reset.")
        return data, True, {
            **combat_result,
            "outcome": state["last_result"],
            "status": state["last_result"],
        }

    if state["phase"] == "guardians":
        state["guardian_review_index"] += 1
        if combat_result.get("killed"):
            inventory = dict(data.get("inventory", {}) or {})
            inventory["Ashes"] = _int(inventory.get("Ashes")) + PHOENIX_LAIR_GUARDIAN_COUNT
            data["inventory"] = inventory
            state["phase"] = "prepare"
            state["guardian_lifepoints"] = 0
            state["encounter"] = {}
            data["combat_encounter"] = {}
            state["last_result"] = "Defeated the aggregate guardian front, cut all five twigs, and kept five Ashes."
        else:
            state["guardian_lifepoints"] = max(
                1, _int(combat_result.get("enemy_lifepoints"), lifepoints, minimum=1)
            )
            state["encounter"] = _sanitize_encounter(
                data.get("combat_encounter"), target_id, state["guardian_lifepoints"]
            )
            current = _guardian_front_enemy(state)
            state["last_result"] = (
                f"Guardian front: {state['guardian_lifepoints']:,}/"
                f"{state['guardian_max_lifepoints']:,} LP · next pressure "
                f"{current['attack_style']}"
            )
        data["phoenix_lair"] = state
        data["activity_session"] = {"active_id": PHOENIX_LAIR_ACTIVITY_ID}
        return data, True, {**combat_result, "status": state["last_result"]}

    if not combat_result.get("killed"):
        state["phoenix_lifepoints"] = max(
            1, _int(combat_result.get("enemy_lifepoints"), lifepoints, minimum=1)
        )
        state["encounter"] = _sanitize_encounter(
            data.get("combat_encounter"), target_id, state["phoenix_lifepoints"]
        )
        dust_attack = state["phoenix_review_count"] % 5 == 0
        if dust_attack:
            _apply_phoenix_dust_drain(data)
        state["last_result"] = (
            f"Phoenix: {state['phoenix_lifepoints']:,}/2,550 LP"
            + (" · dust attack halved Attack, Magic, and Ranged" if dust_attack else "")
        )
        data["phoenix_lair"] = state
        data["activity_session"] = {"active_id": PHOENIX_LAIR_ACTIVITY_ID}
        return data, True, {
            **combat_result,
            "dust_attack": dust_attack,
            "status": state["last_result"],
        }

    first_completion = state["runs_completed"] == 0
    completion_rewards = {
        **PHOENIX_LAIR_FIXED_REWARDS,
        "slayer_exp": 5000.0 if first_completion else 500.0,
    }
    for exp_key, amount in completion_rewards.items():
        data[exp_key] = _float(data.get(exp_key)) + amount
    inventory = dict(data.get("inventory", {}) or {})
    inventory[PHOENIX_QUILL_ITEM] = _int(inventory.get(PHOENIX_QUILL_ITEM)) + 5
    data["inventory"] = inventory
    try:
        egg_dropped = float(rng()) < PHOENIX_LAIR_EGG_CHANCE
    except (TypeError, ValueError, OverflowError):
        egg_dropped = False
    state["pending_egg"] = egg_dropped
    state["runs_completed"] += 1
    state["last_completed_world_day"] = _world_day(data)
    message = (
        "Phoenix Lair complete · +7,500 Firemaking XP · +3,000 Fletching XP · "
        "+1,000 Crafting XP · +"
        f"{int(completion_rewards['slayer_exp']):,} Slayer XP · +5 Phoenix quills"
        + (" · Phoenix egg choice available" if egg_dropped else "")
    )
    _end_run(data, state, message)
    data["phoenix_lair"] = state
    return data, True, {
        **combat_result,
        "outcome": message,
        "status": message,
        "egg_dropped": egg_dropped,
        "first_completion": first_completion,
        "xp_rewards": _merge_xp_rewards(
            combat_result.get("xp_rewards", {}) or {}, completion_rewards
        ),
    }


def resolve_phoenix_egg_choice_pure(
    player_data: Mapping[str, Any],
    option_id: str,
    *,
    remember_choice: bool = False,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if option_id not in PHOENIX_EGG_CHOICES:
        # Shallow on purpose: nothing has been read or written yet, and the
        # review-context callers discard this save when the choice is rejected.
        return dict(player_data), False, {"reason": "Unknown Phoenix egg choice."}
    # Shallow on purpose: the run state and its encounter are rebuilt as deep
    # copies, and every cross-module receiver rebuilds before writing.
    data = dict(player_data)
    state = sanitize_phoenix_lair_state_pure(data.get("phoenix_lair"))
    if not state["pending_egg"]:
        return data, False, {"reason": "No Phoenix egg choice is pending."}
    if remember_choice:
        data = remember_review_context_choice_pure(
            data, PHOENIX_EGG_CONTEXT_ID, option_id
        )
    item_name, pet_id = PHOENIX_EGG_CHOICES[option_id]
    if _int(data.get("summoning_level"), 1, minimum=1) >= 72:
        data, ok, instance_id = acquire_pet_pure(data, pet_id)
        if not ok:
            # Shallow rollback: acquire_pet_pure rebuilds the summoning state it
            # writes, and the review-context callers discard this save on failure.
            return dict(player_data), False, {"reason": instance_id}
        result = {"pet_id": pet_id, "instance_id": instance_id, "item_name": ""}
    else:
        inventory = dict(data.get("inventory", {}) or {})
        inventory[item_name] = _int(inventory.get(item_name)) + 1
        data["inventory"] = inventory
        result = {"pet_id": "", "instance_id": "", "item_name": item_name}
    state = sanitize_phoenix_lair_state_pure(data.get("phoenix_lair"))
    state["pending_egg"] = False
    state["last_result"] = (
        f"Hatched {PETS_BY_ID[pet_id].display_name}."
        if result["pet_id"]
        else f"Received {item_name}."
    )
    data["phoenix_lair"] = state
    return data, True, result
