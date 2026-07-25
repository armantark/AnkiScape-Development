"""Pure, persisted Barrows mound, tunnel, combat, chest, and repair flow."""

from __future__ import annotations

import copy
import math
from collections import deque
from collections.abc import Callable, Mapping
from typing import Any

from ..data.barrows_data import (
    BARROWS_ACTIVITY_ID,
    BARROWS_BROTHER_DATA,
    BARROWS_BROTHER_ORDER,
    BARROWS_COMBAT_TARGET_ID,
    BARROWS_COMBAT_TICKS_PER_REVIEW,
    BARROWS_ENEMY_DATA,
    BARROWS_MAX_REWARD_POTENTIAL,
    BARROWS_ORDINARY_REWARDS,
    BARROWS_STATE_VERSION,
    BARROWS_TUNNEL_ENEMY_DATA,
)
from ..data.equipment_condition_data import EQUIPMENT_CONDITION_DATA
from .equipment_instance_logic import (
    add_equipment_instance_pure,
    condition_name_pure,
    sanitize_equipment_instance_state_pure,
)
from ..logic_pure.logic_pure import apply_combat_burst_pure


_VALID_MODES = frozenset({"casual", "advanced"})
_SOURCE_BROTHER_ORDER = ("ahrim", "dharok", "guthan", "karil", "torag", "verac", "akrisae")
_PERIMETER = (0, 1, 2, 5, 8, 7, 6, 3)
_CORNERS = (0, 2, 6, 8)
_CENTER_APPROACHES = (1, 3, 5, 7)


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return max(minimum, int(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _unit(value: Any) -> float:
    try:
        return max(0.0, min(0.999999999, float(value)))
    except (TypeError, ValueError, OverflowError):
        return 0.5


def _roll(rng: Callable[[], float] | None) -> float:
    if rng is None:
        return 0.5
    try:
        return _unit(rng())
    except (TypeError, ValueError, StopIteration):
        return 0.5


def _choice(values: tuple[Any, ...] | list[Any], rng: Callable[[], float] | None) -> Any:
    return values[min(len(values) - 1, int(_roll(rng) * len(values)))]


def _edge(a: int, b: int) -> str:
    return f"{min(a, b)}-{max(a, b)}"


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    quests = player_data.get("quests")
    state = quests.get(quest_id) if isinstance(quests, Mapping) else None
    return bool(isinstance(state, Mapping) and state.get("completed"))


def _empty_session() -> dict[str, str]:
    return {"active_id": ""}


def default_barrows_state_pure() -> dict[str, Any]:
    return {
        "version": BARROWS_STATE_VERSION,
        "active": False,
        "suspended": False,
        "automation_mode": "casual",
        "phase": "ready",
        "available_brothers": list(_SOURCE_BROTHER_ORDER[:6]),
        "hidden_brother": "",
        "slain_brothers": [],
        "surface_queue": [],
        "selected_brother": "",
        "start_room": -1,
        "current_room": -1,
        "usable_edges": [],
        "revealed_rooms": [],
        "selected_room": -1,
        "tunnel_kill_count": 0,
        "active_encounter": {},
        "prayer_drain_residual": 0,
        "previous_combat_target": "",
        "chests_opened": 0,
        "last_reward": {},
        "last_result": "Ready to disturb the Barrows mounds.",
    }


def _sanitize_encounter(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    enemy_id = str(raw.get("enemy_id", ""))
    spec = BARROWS_ENEMY_DATA.get(enemy_id)
    kind = str(raw.get("kind", ""))
    if spec is None or kind not in {"brother", "creature"}:
        return {}
    maximum = _int(spec["stats"]["hitpoints"], 1, minimum=1)
    lifepoints = min(maximum, _int(raw.get("lifepoints"), maximum, minimum=1))
    encounter = raw.get("encounter")
    encounter = copy.deepcopy(dict(encounter)) if isinstance(encounter, Mapping) else {}
    encounter["target_id"] = BARROWS_COMBAT_TARGET_ID
    encounter["enemy_lifepoints"] = lifepoints
    protected = str(raw.get("protected_class", "melee"))
    if protected not in {"melee", "ranged", "magic"}:
        protected = "melee"
    return {
        "kind": kind,
        "enemy_id": enemy_id,
        "lifepoints": lifepoints,
        "encounter": encounter,
        "protected_class": protected,
        "protection_damage": min(149, _int(raw.get("protection_damage"))),
    }


def sanitize_barrows_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_barrows_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    if mode not in _VALID_MODES:
        mode = "casual"
    available = [
        value for value in dict.fromkeys(str(v) for v in source.get("available_brothers", ()))
        if value in BARROWS_BROTHER_DATA
    ]
    if not available:
        available = list(_SOURCE_BROTHER_ORDER[:6])
    slain = [
        value for value in dict.fromkeys(str(v) for v in source.get("slain_brothers", ()))
        if value in available
    ]
    hidden = str(source.get("hidden_brother", ""))
    if hidden not in _SOURCE_BROTHER_ORDER[:6]:
        hidden = ""
    queue = [
        value for value in dict.fromkeys(str(v) for v in source.get("surface_queue", ()))
        if value in available and value != hidden and value not in slain
    ]
    usable_edges = []
    for value in source.get("usable_edges", ()) or ():
        text = str(value)
        parts = text.split("-")
        if len(parts) != 2:
            continue
        try:
            a, b = (int(parts[0]), int(parts[1]))
        except ValueError:
            continue
        if 0 <= a <= 8 and 0 <= b <= 8 and a != b:
            usable_edges.append(_edge(a, b))
    revealed = sorted({
        _int(value, -1, minimum=-1)
        for value in source.get("revealed_rooms", ()) or ()
        if _int(value, -1, minimum=-1) in range(9)
    })
    phase = str(source.get("phase", "ready"))
    if phase not in {"ready", "mounds", "tunnels", "chest"}:
        phase = "ready"
    active = bool(source.get("active", False)) and phase != "ready"
    suspended = bool(source.get("suspended", False)) and not active and phase != "ready"
    selected_brother = str(source.get("selected_brother", ""))
    if selected_brother not in queue:
        selected_brother = ""
    return {
        **defaults,
        "active": active,
        "suspended": suspended,
        "automation_mode": mode,
        "phase": phase,
        "available_brothers": available,
        "hidden_brother": hidden,
        "slain_brothers": slain,
        "surface_queue": queue,
        "selected_brother": selected_brother,
        "start_room": min(8, _int(source.get("start_room"), -1, minimum=-1)),
        "current_room": min(8, _int(source.get("current_room"), -1, minimum=-1)),
        "usable_edges": sorted(set(usable_edges)),
        "revealed_rooms": revealed,
        "selected_room": min(8, _int(source.get("selected_room"), -1, minimum=-1)),
        "tunnel_kill_count": _int(source.get("tunnel_kill_count")),
        "active_encounter": _sanitize_encounter(source.get("active_encounter")),
        "prayer_drain_residual": min(99, _int(source.get("prayer_drain_residual"))),
        "previous_combat_target": str(source.get("previous_combat_target", ""))[:120],
        "chests_opened": _int(source.get("chests_opened")),
        "last_reward": copy.deepcopy(dict(source.get("last_reward", {}))) if isinstance(source.get("last_reward"), Mapping) else {},
        "last_result": str(source.get("last_result", defaults["last_result"]))[:500],
    }


def _new_topology(rng: Callable[[], float] | None) -> tuple[int, list[str]]:
    start = int(_choice(list(_CORNERS), rng))
    perimeter_edges = [_edge(_PERIMETER[i], _PERIMETER[(i + 1) % len(_PERIMETER)]) for i in range(len(_PERIMETER))]
    locked = str(_choice(perimeter_edges, rng))
    center_approach = int(_choice(list(_CENTER_APPROACHES), rng))
    return start, sorted([value for value in perimeter_edges if value != locked] + [_edge(center_approach, 4)])


def _neighbors(state: Mapping[str, Any], room: int) -> tuple[int, ...]:
    result = []
    for raw in state.get("usable_edges", ()) or ():
        a, b = (int(value) for value in str(raw).split("-"))
        if a == room:
            result.append(b)
        elif b == room:
            result.append(a)
    return tuple(sorted(result))


def _path_to_center(state: Mapping[str, Any]) -> tuple[int, ...]:
    start = _int(state.get("current_room"), -1, minimum=-1)
    if start not in range(9):
        return ()
    queue = deque([(start, ())])
    seen = {start}
    while queue:
        room, path = queue.popleft()
        if room == 4:
            return path
        for neighbor in _neighbors(state, room):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, (*path, neighbor)))
    return ()


def barrows_reward_potential_pure(state: Mapping[str, Any]) -> int:
    return min(
        BARROWS_MAX_REWARD_POTENTIAL,
        110 * len(state.get("slain_brothers", ()) or ())
        + 73 * _int(state.get("tunnel_kill_count")),
    )


def _available_doors(state: Mapping[str, Any]) -> tuple[int, ...]:
    room = _int(state.get("current_room"), -1, minimum=-1)
    if room not in range(9):
        return ()
    return _neighbors(state, room)


def barrows_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_barrows_state_pure(player_data.get("barrows"))
    encounter = state["active_encounter"]
    encounter_spec = BARROWS_ENEMY_DATA.get(str(encounter.get("enemy_id", "")), {})
    doors = _available_doors(state) if state["phase"] == "tunnels" else ()
    can_review = bool(state["active"])
    if state["automation_mode"] == "advanced" and state["phase"] == "mounds" and not encounter:
        can_review = can_review and bool(state["selected_brother"] or len(state["surface_queue"]) == 1)
    if state["automation_mode"] == "advanced" and state["phase"] == "tunnels" and not encounter and state["current_room"] != 4:
        can_review = can_review and state["selected_room"] in doors
    if state["automation_mode"] == "advanced" and state["phase"] == "chest" and not encounter:
        can_review = False
    repair_rows = []
    instances = player_data.get("equipment_instances")
    if isinstance(instances, Mapping):
        for instance_id, record in instances.items():
            if not isinstance(record, Mapping) or record.get("location") != "bank":
                continue
            family_id = str(record.get("family_id", ""))
            spec = EQUIPMENT_CONDITION_DATA.get(family_id)
            if not family_id.startswith("barrows_") or not isinstance(spec, Mapping):
                continue
            maximum = _int(spec.get("max_condition"), 1, minimum=1)
            condition = min(maximum, _int(record.get("condition")))
            if condition >= maximum:
                continue
            cost = math.ceil(_int(spec.get("repair_cost"), 100_000) * (maximum - condition) / maximum)
            repair_rows.append({
                "instance_id": str(instance_id),
                "family_id": family_id,
                "item_name": str(record.get("item_name", "")),
                "condition": condition,
                "maximum": maximum,
                "cost": cost,
            })
    return {
        **state,
        "reward_potential": barrows_reward_potential_pure(state),
        "available_doors": doors,
        "route_to_center": _path_to_center(state),
        "can_review": can_review,
        "encounter_name": str(encounter_spec.get("display_name", "")),
        "encounter_lifepoints": _int(encounter.get("lifepoints")),
        "encounter_max_lifepoints": _int((encounter_spec.get("stats") or {}).get("hitpoints")),
        "repair_rows": tuple(sorted(repair_rows, key=lambda row: (row["item_name"], row["instance_id"]))),
    }


def _start_encounter(state: dict[str, Any], kind: str, enemy_id: str) -> None:
    maximum = _int(BARROWS_ENEMY_DATA[enemy_id]["stats"]["hitpoints"], 1, minimum=1)
    state["active_encounter"] = {
        "kind": kind,
        "enemy_id": enemy_id,
        "lifepoints": maximum,
        "encounter": {"target_id": BARROWS_COMBAT_TARGET_ID, "enemy_lifepoints": maximum},
        "protected_class": "melee",
        "protection_damage": 0,
    }


def _award_stack(data: dict[str, Any], item_name: str, amount: int) -> None:
    if amount <= 0:
        return
    inventory = dict(data.get("inventory", {}) or {})
    inventory[item_name] = _int(inventory.get(item_name)) + amount
    data["inventory"] = inventory


def _roll_chest_rewards(
    data: dict[str, Any], state: Mapping[str, Any], rng: Callable[[], float] | None
) -> tuple[dict[str, Any], dict[str, int]]:
    slain = tuple(value for value in _SOURCE_BROTHER_ORDER if value in state["slain_brothers"])
    points = barrows_reward_potential_pure(state)
    rolls = max(1, min(7, len(slain) + 1))
    denominator = max(73, min(450, 450 - 58 * len(slain)))
    rewards: dict[str, int] = {}
    for roll_index in range(rolls):
        if roll_index < len(slain) and _roll(rng) < 1.0 / denominator:
            brother_id = str(_choice(list(slain), rng))
            family_id = f"barrows_{brother_id}"
            data, instance_id = add_equipment_instance_pure(data, family_id, EQUIPMENT_CONDITION_DATA)
            if instance_id:
                item_name = str(BARROWS_BROTHER_DATA[brother_id]["reward_item"])
                rewards[item_name] = rewards.get(item_name, 0) + 1
                continue
        ordinary_awarded = False
        for threshold, item_name, minimum, maximum in BARROWS_ORDINARY_REWARDS:
            if points < threshold or _roll(rng) >= 125 / 1_012:
                continue
            amount = minimum + int(_roll(rng) * (maximum - minimum + 1))
            _award_stack(data, item_name, amount)
            rewards[item_name] = rewards.get(item_name, 0) + amount
            ordinary_awarded = True
            break
        if ordinary_awarded:
            continue
        _award_stack(data, "Coins", points)
        rewards["Coins"] = rewards.get("Coins", 0) + points
    return data, rewards


def _repair_at_bob(
    data: dict[str, Any], instance_id: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = sanitize_equipment_instance_state_pure(data, EQUIPMENT_CONDITION_DATA)
    record = data["equipment_instances"].get(instance_id)
    if not isinstance(record, dict) or record.get("location") != "bank":
        return data, False, {"reason": "That damaged Barrows item is not in the Bank."}
    family_id = str(record.get("family_id", ""))
    spec = EQUIPMENT_CONDITION_DATA.get(family_id)
    if not family_id.startswith("barrows_") or not isinstance(spec, Mapping):
        return data, False, {"reason": "That item cannot be repaired by Bob."}
    maximum = _int(spec.get("max_condition"), 1, minimum=1)
    current = min(maximum, _int(record.get("condition")))
    if current >= maximum:
        return data, False, {"reason": "That Barrows item is already fully repaired."}
    cost = math.ceil(_int(spec.get("repair_cost"), 100_000) * (maximum - current) / maximum)
    inventory = dict(data.get("inventory", {}) or {})
    if _int(inventory.get("Coins")) < cost:
        return data, False, {"reason": f"Bob needs {cost:,} coins for that repair."}
    before_name = str(record.get("item_name", ""))
    after_name = condition_name_pure(family_id, maximum, EQUIPMENT_CONDITION_DATA)
    inventory["Coins"] = _int(inventory.get("Coins")) - cost
    inventory[before_name] = max(0, _int(inventory.get(before_name)) - 1)
    inventory[after_name] = _int(inventory.get(after_name)) + 1
    record["condition"] = maximum
    record["item_name"] = after_name
    data["inventory"] = inventory
    return data, True, {"message": f"Bob repaired {after_name} for {cost:,} coins.", "cost": cost, "item_name": after_name}


def apply_barrows_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the encounter is rebuilt as a deep copy, and the
    # repair path rebinds to sanitize_equipment_instance_state_pure output
    # before editing a record.
    data = dict(player_data)
    state = sanitize_barrows_state_pure(data.get("barrows"))
    data["barrows"] = state
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "enter":
        if state["active"]:
            data["activity_session"] = {"active_id": BARROWS_ACTIVITY_ID}
            data["current_utility"] = BARROWS_ACTIVITY_ID
            return data, True, {"message": "The active Barrows run is selected for reviews."}
        active_session = data.get("activity_session")
        if isinstance(active_session, Mapping) and active_session.get("active_id"):
            return data, False, {"reason": "Another persistent activity is active."}
        encounter = data.get("combat_encounter")
        if isinstance(encounter, Mapping) and encounter:
            return data, False, {"reason": "Finish or leave the current Combat encounter first."}
        follower = ((data.get("summoning_state") or {}).get("active_follower") if isinstance(data.get("summoning_state"), Mapping) else None)
        if isinstance(follower, Mapping) and follower.get("kind") == "familiar":
            return data, False, {"reason": "Familiars cannot enter Barrows. Dismiss it first."}
        if state["suspended"]:
            state["active"] = True
            state["suspended"] = False
            message = "Resumed the suspended Barrows run."
        else:
            available = list(_SOURCE_BROTHER_ORDER[:6])
            if _quest_complete(data, "ritual_of_the_mahjarrat"):
                available.append("akrisae")
            hidden = str(_choice(list(_SOURCE_BROTHER_ORDER[:6]), rng))
            start, edges = _new_topology(rng)
            state = default_barrows_state_pure()
            state.update({
                "active": True,
                "phase": "mounds",
                "automation_mode": str(data.get("barrows", {}).get("automation_mode", "casual")) if isinstance(data.get("barrows"), Mapping) else "casual",
                "available_brothers": available,
                "hidden_brother": hidden,
                "surface_queue": [value for value in BARROWS_BROTHER_ORDER if value in available and value != hidden],
                "start_room": start,
                "current_room": start,
                "usable_edges": edges,
                "revealed_rooms": [start],
                "previous_combat_target": str(data.get("current_combat_target", ""))[:120],
                "last_result": "Entered Barrows and disturbed the first mound.",
            })
            message = state["last_result"]
        data["barrows"] = state
        data["activity_session"] = {"active_id": BARROWS_ACTIVITY_ID}
        data["current_utility"] = BARROWS_ACTIVITY_ID
        return data, True, {"message": message}

    if action_id == "leave":
        if not state["active"]:
            return data, False, {"reason": "No Barrows run is active."}
        encounter = state["active_encounter"]
        if encounter.get("kind") == "brother":
            _start_encounter(state, "brother", str(encounter["enemy_id"]))
        state["active"] = False
        state["suspended"] = True
        state["last_result"] = "Left Barrows; the exact run state is ready to resume."
        data["barrows"] = state
        data["activity_session"] = _empty_session()
        data["combat_encounter"] = {}
        data["current_combat_target"] = str(state.get("previous_combat_target", ""))
        return data, True, {"message": state["last_result"]}

    if action_id == "set_mode":
        mode = str(payload.get("automation_mode", ""))
        if mode not in _VALID_MODES:
            return data, False, {"reason": "Unknown Barrows automation mode."}
        state["automation_mode"] = mode
        state["selected_brother"] = ""
        state["selected_room"] = -1
        data["barrows"] = state
        return data, True, {"message": f"Barrows mode set to {mode}."}

    if action_id == "select_brother":
        brother_id = str(payload.get("brother_id", ""))
        if brother_id not in state["surface_queue"]:
            return data, False, {"reason": "That mound is not currently available."}
        state["selected_brother"] = brother_id
        data["barrows"] = state
        return data, True, {"message": f"Selected {BARROWS_BROTHER_DATA[brother_id]['display_name']}."}

    if action_id == "select_room":
        room = _int(payload.get("room"), -1, minimum=-1)
        if room not in _available_doors(state):
            return data, False, {"reason": "That door is not reachable from the current room."}
        state["selected_room"] = room
        data["barrows"] = state
        return data, True, {"message": f"Selected tunnel room {room + 1}."}

    if action_id == "claim_chest":
        if not state["active"] or state["phase"] != "chest":
            return data, False, {"reason": "Reach the central Barrows chest first."}
        if state["active_encounter"] and state["automation_mode"] != "advanced":
            return data, False, {"reason": "Casual mode defeats the waiting brother before looting."}
        data, rewards = _roll_chest_rewards(data, state, rng)
        points = barrows_reward_potential_pure(state)
        chests = state["chests_opened"] + 1
        mode = state["automation_mode"]
        previous = str(state.get("previous_combat_target", ""))
        completed = default_barrows_state_pure()
        completed["automation_mode"] = mode
        completed["chests_opened"] = chests
        completed["last_reward"] = dict(rewards)
        completed["last_result"] = f"Looted Barrows chest {chests} at {points:,}/1,012 potential."
        data["barrows"] = completed
        data["activity_session"] = _empty_session()
        data["combat_encounter"] = {}
        data["current_combat_target"] = previous
        return data, True, {"message": completed["last_result"], "rewards": rewards, "reward_potential": points, "complete": True}

    if action_id == "repair":
        return _repair_at_bob(data, str(payload.get("instance_id", "")))

    return data, False, {"reason": "Unknown Barrows command."}


def _drain_barrows_prayer(
    data: dict[str, Any], state: dict[str, Any], ticks_elapsed: int
) -> int:
    drain_per_ten_seconds = 80 + 10 * len(state["slain_brothers"])
    ticks = min(BARROWS_COMBAT_TICKS_PER_REVIEW, _int(ticks_elapsed))
    numerator = state["prayer_drain_residual"] + drain_per_ten_seconds * ticks * 6
    drain, state["prayer_drain_residual"] = divmod(numerator, 100)
    available = _int(data.get("combat_prayer_points"))
    applied = min(available, drain)
    data["combat_prayer_points"] = available - applied
    if data["combat_prayer_points"] <= 0:
        data["combat_selected_prayers"] = []
    return applied


def _apply_brother_special(
    data: dict[str, Any],
    state: dict[str, Any],
    encounter: dict[str, Any],
    combat_result: Mapping[str, Any],
    rng: Callable[[], float] | None,
) -> str:
    enemy_id = str(encounter["enemy_id"])
    damage_to_player = _int(combat_result.get("enemy_damage"))
    damage_to_enemy = _int(combat_result.get("player_damage"))
    if enemy_id == "guthan" and damage_to_player > 0 and _roll(rng) < 0.25:
        maximum = _int(BARROWS_BROTHER_DATA[enemy_id]["stats"]["hitpoints"], 1, minimum=1)
        healed = min(damage_to_player, maximum - encounter["lifepoints"])
        encounter["lifepoints"] += healed
        encounter["encounter"]["enemy_lifepoints"] = encounter["lifepoints"]
        return f"Guthan healed {healed} LP"
    if enemy_id == "ahrim" and damage_to_player > 0 and _roll(rng) < 0.20:
        levels = dict(data.get("combat_current_levels", {}) or {})
        base = _int(data.get("strength_level"), 1, minimum=1)
        levels["strength"] = max(1, _int(levels.get("strength"), base, minimum=1) - 5)
        data["combat_current_levels"] = levels
        return "Ahrim drained 5 Strength levels"
    if enemy_id == "karil" and damage_to_player > 0 and _roll(rng) < 1 / 3:
        levels = dict(data.get("combat_current_levels", {}) or {})
        base = _int(data.get("agility_level"), 1, minimum=1)
        levels["agility"] = max(1, _int(levels.get("agility"), base, minimum=1) - max(1, base // 5))
        data["combat_current_levels"] = levels
        return "Karil drained 20% of base Agility"
    if enemy_id == "torag" and damage_to_player > 0 and _roll(rng) < 1 / 3:
        before = _int(data.get("agility_run_energy_credit_pct"))
        after = max(0, before - 4)
        data["agility_run_energy_credit_pct"] = after
        drained = before - after
        return (
            f"Torag drained {drained} run-energy percentage points"
            if drained
            else "Torag's run-energy drain found no remaining credit"
        )
    if enemy_id == "akrisae" and damage_to_enemy > 0:
        total = encounter["protection_damage"] + damage_to_enemy
        switches, encounter["protection_damage"] = divmod(total, 150)
        if switches:
            classes = ("melee", "ranged", "magic")
            index = classes.index(encounter["protected_class"])
            encounter["protected_class"] = classes[(index + switches) % len(classes)]
            return f"Akrisae now protects from {encounter['protected_class']}"
    return ""


def _resolve_encounter(
    data: dict[str, Any],
    state: dict[str, Any],
    rng: Callable[[], float] | None,
    equipment_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    encounter = state["active_encounter"]
    enemy_id = str(encounter["enemy_id"])
    enemy = copy.deepcopy(BARROWS_ENEMY_DATA[enemy_id])
    if enemy_id == "dharok":
        maximum = _int(enemy["stats"]["hitpoints"], 1, minimum=1)
        missing = max(0, maximum - _int(encounter["lifepoints"], maximum))
        enemy["max_hit"] = 300 + (380 * missing // maximum)
    if enemy_id == "akrisae":
        enemy["protect_from_player_class"] = encounter["protected_class"]
    saved_prayers = list(data.get("combat_selected_prayers", ()) or ())
    verac_special = enemy_id == "verac" and _roll(rng) < 1 / 3
    if verac_special:
        data["combat_selected_prayers"] = []
        enemy["stats"]["attack"] = 100_000
    data["current_combat_target"] = BARROWS_COMBAT_TARGET_ID
    data["combat_encounter"] = copy.deepcopy(encounter["encounter"])
    data, ok, result = apply_combat_burst_pure(
        data,
        {BARROWS_COMBAT_TARGET_ID: enemy},
        equipment_data,
        ticks=BARROWS_COMBAT_TICKS_PER_REVIEW,
        rng=rng or (lambda: 0.5),
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=False,
        allow_bank_run=False,
    )
    if verac_special and _int(data.get("combat_prayer_points")) > 0:
        data["combat_selected_prayers"] = saved_prayers
    if not ok:
        return data, False, dict(result)
    prayer_drained = _drain_barrows_prayer(
        data,
        state,
        _int(result.get("ticks_elapsed"), BARROWS_COMBAT_TICKS_PER_REVIEW),
    )
    if result.get("died"):
        chests = state["chests_opened"]
        mode = state["automation_mode"]
        previous = str(state.get("previous_combat_target", ""))
        failed = default_barrows_state_pure()
        failed["chests_opened"] = chests
        failed["automation_mode"] = mode
        failed["last_result"] = "Defeated at Barrows; the dangerous run was lost."
        data["barrows"] = failed
        data["activity_session"] = _empty_session()
        data["current_combat_target"] = previous
        return data, True, {**result, "outcome": "death", "status": failed["last_result"], "prayer_drained": prayer_drained}
    killed = bool(result.get("killed"))
    if killed:
        kind = encounter["kind"]
        if kind == "brother" and enemy_id not in state["slain_brothers"]:
            state["slain_brothers"].append(enemy_id)
            state["surface_queue"] = [value for value in state["surface_queue"] if value != enemy_id]
            state["selected_brother"] = ""
        elif kind == "creature":
            state["tunnel_kill_count"] += 1
        state["active_encounter"] = {}
        data["combat_encounter"] = {}
        special = ""
    else:
        encounter["lifepoints"] = max(1, _int(result.get("enemy_lifepoints"), encounter["lifepoints"], minimum=1))
        encounter["encounter"] = copy.deepcopy(dict(data.get("combat_encounter", {})))
        special = _apply_brother_special(data, state, encounter, result, rng) if encounter["kind"] == "brother" else ""
    encounter_status = "defeated" if killed else f"{encounter.get('lifepoints', 0):,} LP"
    status = f"{enemy['display_name']}: {encounter_status}"
    if verac_special:
        status += " · Defiler ignored armour and prayer"
    if special:
        status += f" · {special}"
    return data, True, {**result, "status": status, "prayer_drained": prayer_drained, "encounter_killed": killed}


def _prepare_next_surface_encounter(state: dict[str, Any]) -> bool:
    if not state["surface_queue"]:
        state["phase"] = "tunnels"
        state["selected_brother"] = ""
        state["last_result"] = "The remaining brother is hidden below; the tunnel route is ready."
        return False
    brother_id = state["selected_brother"] if state["automation_mode"] == "advanced" else ""
    if brother_id not in state["surface_queue"]:
        if state["automation_mode"] == "advanced" and len(state["surface_queue"]) > 1:
            return False
        brother_id = next(value for value in BARROWS_BROTHER_ORDER if value in state["surface_queue"])
    _start_encounter(state, "brother", brother_id)
    return True


def _prepare_tunnel_transition(state: dict[str, Any], rng: Callable[[], float] | None) -> tuple[bool, str]:
    current = state["current_room"]
    if current == 4:
        state["phase"] = "chest"
        return False, "Reached the central chest."
    doors = _available_doors(state)
    destination = state["selected_room"] if state["automation_mode"] == "advanced" else -1
    if destination not in doors:
        if state["automation_mode"] == "advanced":
            return False, "Choose one of the revealed tunnel doors."
        path = _path_to_center(state)
        destination = path[0] if path else -1
    if destination not in doors:
        return False, "No usable tunnel route remains."
    state["current_room"] = destination
    state["selected_room"] = -1
    state["revealed_rooms"] = sorted(set((*state["revealed_rooms"], destination, *_available_doors(state))))
    if destination == 4:
        hidden = state["hidden_brother"]
        if hidden and hidden not in state["slain_brothers"]:
            _start_encounter(state, "brother", hidden)
            state["phase"] = "chest"
            return True, "The central-door puzzle resolves; the hidden brother appears at the chest."
        state["phase"] = "chest"
        return False, "The central-door puzzle resolves and the reward chest is ready."
    remaining = state["hidden_brother"] not in state["slain_brothers"]
    if remaining and _roll(rng) < 0.10:
        _start_encounter(state, "brother", state["hidden_brother"])
        return True, "The hidden brother emerges as the door opens."
    creature_id = str(_choice(list(BARROWS_TUNNEL_ENEMY_DATA), rng))
    _start_encounter(state, "creature", creature_id)
    return True, f"Entered room {destination + 1}; a crypt creature attacks."


def apply_barrows_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None,
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the encounter is rebuilt as a deep copy, and the
    # repair path rebinds to sanitize_equipment_instance_state_pure output
    # before editing a record.
    data = dict(player_data)
    state = sanitize_barrows_state_pure(data.get("barrows"))
    if not state["active"]:
        return data, False, {"reason": "Enter or resume Barrows before training it."}
    data["barrows"] = state
    if state["active_encounter"]:
        data, ok, result = _resolve_encounter(data, state, rng, equipment_data or {})
        if not ok or result.get("outcome") == "death":
            return data, ok, result
        if state["phase"] == "mounds" and not state["active_encounter"] and not state["surface_queue"]:
            state["phase"] = "tunnels"
        if state["phase"] == "chest" and not state["active_encounter"] and state["automation_mode"] == "casual":
            data["barrows"] = state
            data, claimed, chest = apply_barrows_command_pure(data, "claim_chest", rng=rng)
            return data, claimed, {**result, **chest, "status": str(chest.get("message", result.get("status", "")))}
        state["last_result"] = str(result.get("status", "Barrows encounter advanced."))[:500]
        data["barrows"] = state
        data["activity_session"] = {"active_id": BARROWS_ACTIVITY_ID}
        return data, True, result

    if state["phase"] == "mounds":
        if not _prepare_next_surface_encounter(state):
            data["barrows"] = state
            return data, True, {"status": state["last_result"], "transition": "tunnels"}
        lead = f"Disturbed {BARROWS_BROTHER_DATA[state['active_encounter']['enemy_id']]['display_name']}."
    elif state["phase"] == "tunnels":
        spawned, lead = _prepare_tunnel_transition(state, rng)
        if not spawned:
            state["last_result"] = lead
            data["barrows"] = state
            if state["phase"] == "chest" and state["automation_mode"] == "casual":
                data, claimed, chest = apply_barrows_command_pure(data, "claim_chest", rng=rng)
                return data, claimed, {**chest, "status": str(chest.get("message", lead))}
            return data, True, {"status": lead, "transition": "chest" if state["phase"] == "chest" else "blocked"}
    elif state["phase"] == "chest":
        if state["automation_mode"] == "casual":
            data, claimed, chest = apply_barrows_command_pure(data, "claim_chest", rng=rng)
            return data, claimed, {**chest, "status": str(chest.get("message", "Barrows chest looted."))}
        return data, False, {"reason": "Open the chest from the Barrows activity card."}
    else:
        return data, False, {"reason": "Start a new Barrows run."}

    data["barrows"] = state
    data, ok, result = _resolve_encounter(data, state, rng, equipment_data or {})
    if ok and not result.get("outcome"):
        if state["phase"] == "mounds" and not state["active_encounter"] and not state["surface_queue"]:
            state["phase"] = "tunnels"
        result["status"] = f"{lead} {result.get('status', '')}".strip()
        state["last_result"] = str(result["status"])[:500]
        data["barrows"] = state
        data["activity_session"] = {"active_id": BARROWS_ACTIVITY_ID}
    return data, ok, result
