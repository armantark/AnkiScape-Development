"""Pure persistent Conquest setup, board simulation, settlement, and view."""

from __future__ import annotations

import copy
import math
from collections import deque
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from ..data.conquest_data import (
    CONQUEST_ACTIVITY_ID,
    CONQUEST_BATTLEFIELD_LAYOUTS,
    CONQUEST_BOARD_SIZE,
    CONQUEST_COMMANDS,
    CONQUEST_COMMANDS_BY_ID,
    CONQUEST_COMBAT_REQUIREMENT,
    CONQUEST_DEFAULT_COMMANDS,
    CONQUEST_DEFAULT_SQUAD,
    CONQUEST_DEPLOYMENT_ROWS,
    CONQUEST_DOCTRINES,
    CONQUEST_EARLY_GAME_THRESHOLD,
    CONQUEST_MAX_COMMANDS,
    CONQUEST_PASSIVE_COMMAND_POINTS,
    CONQUEST_RATING_FLOOR,
    CONQUEST_RATING_DIVISOR,
    CONQUEST_RATING_K,
    CONQUEST_RATING_START,
    CONQUEST_SETUP_BUDGET,
    CONQUEST_STARTING_COMMAND_POINTS,
    CONQUEST_TURN_RATIO_CURVE,
    CONQUEST_TIMEOUT_RESOLUTION,
    CONQUEST_UNIT_CAP,
    CONQUEST_UNITS,
    CONQUEST_UNITS_BY_ID,
)
from ..data.pest_control_data import PEST_CONTROL_COMMENDATION_CAP
from ..logic_pure.logic_pure import player_combat_level_pure
from .music_log_logic import refresh_music_log_pure


CONQUEST_STATE_VERSION = 1
_DOCTRINES = frozenset(row[0] for row in CONQUEST_DOCTRINES)
_SIDES = ("player", "opponent")
# A stored troop count is bounded only so a corrupt save cannot allocate without
# limit. The squad cap is a rule the reducers refuse, never a silent clamp: a
# clamp would turn an illegal squad into a legal one and report success.
_SQUAD_INPUT_MAX = 999_999


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _roll(rng: Callable[[], float] | None) -> float:
    try:
        return max(0.0, min(float(rng()) if rng is not None else 0.5, 0.999999999))
    except (TypeError, ValueError, OverflowError):
        return 0.5


def _copy_squad(raw: Any) -> dict[str, int]:
    source = raw if isinstance(raw, Mapping) else {}
    return {
        unit.id: _int(source.get(unit.id), maximum=_SQUAD_INPUT_MAX)
        for unit in CONQUEST_UNITS
    }


def _copy_commands(raw: Any) -> tuple[str, ...]:
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return ()
    selected: list[str] = []
    for value in raw:
        command_id = str(value)
        if command_id in CONQUEST_COMMANDS_BY_ID and command_id not in selected:
            selected.append(command_id)
        if len(selected) >= CONQUEST_MAX_COMMANDS:
            break
    return tuple(selected)


def _squad_totals(squad: Mapping[str, Any]) -> tuple[int, int]:
    count = sum(_int(squad.get(unit.id), maximum=_SQUAD_INPUT_MAX) for unit in CONQUEST_UNITS)
    cost = sum(
        unit.cost * _int(squad.get(unit.id), maximum=_SQUAD_INPUT_MAX)
        for unit in CONQUEST_UNITS
    )
    return count, cost


def _setup_errors(squad: Mapping[str, Any], commands: Sequence[str]) -> tuple[str, ...]:
    count, cost = _squad_totals(squad)
    errors: list[str] = []
    if count <= 0:
        errors.append("Choose at least one troop.")
    if count > CONQUEST_UNIT_CAP:
        errors.append(f"Squads are limited to {CONQUEST_UNIT_CAP} troops.")
    if cost > CONQUEST_SETUP_BUDGET:
        errors.append(f"Squads are limited to {CONQUEST_SETUP_BUDGET:,} setup points.")
    if len(commands) > CONQUEST_MAX_COMMANDS:
        errors.append(f"Choose at most {CONQUEST_MAX_COMMANDS} commands.")
    return tuple(errors)


def default_conquest_state_pure() -> dict[str, Any]:
    return {
        "conquest": {},
        "conquest_policy": {
            "automation_mode": "casual",
            "doctrine": "balanced",
            "squad": dict(CONQUEST_DEFAULT_SQUAD),
            "commands": list(CONQUEST_DEFAULT_COMMANDS),
        },
        "conquest_rating": CONQUEST_RATING_START,
        "conquest_matches_started": 0,
        "conquest_games_won": 0,
        "conquest_games_lost": 0,
        "conquest_resignations": 0,
        "conquest_last_result": "",
    }


def sanitize_conquest_policy_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    doctrine = str(source.get("doctrine", "balanced"))
    if mode not in {"casual", "advanced"}:
        mode = "casual"
    if doctrine not in _DOCTRINES:
        doctrine = "balanced"
    squad = _copy_squad(source.get("squad"))
    commands = _copy_commands(source.get("commands"))
    if mode == "casual" or _setup_errors(squad, commands):
        squad = dict(CONQUEST_DEFAULT_SQUAD)
        commands = tuple(CONQUEST_DEFAULT_COMMANDS)
    return {
        "automation_mode": mode,
        "doctrine": doctrine,
        "squad": squad,
        "commands": list(commands),
    }


def _sanitize_unit(raw: Any, occupied: set[tuple[int, int]]) -> dict[str, Any] | None:
    if not isinstance(raw, Mapping):
        return None
    unit_type = str(raw.get("unit_type", ""))
    spec = CONQUEST_UNITS_BY_ID.get(unit_type)
    side = str(raw.get("side", ""))
    x = _int(raw.get("x"), maximum=CONQUEST_BOARD_SIZE - 1)
    y = _int(raw.get("y"), maximum=CONQUEST_BOARD_SIZE - 1)
    if spec is None or side not in _SIDES or (x, y) in occupied:
        return None
    lifepoints = min(
        _int(raw.get("lifepoints", spec.lifepoints), spec.lifepoints),
        spec.lifepoints + 400,
    )
    if lifepoints <= 0:
        return None
    occupied.add((x, y))
    effects = raw.get("effects")
    source_effects = effects if isinstance(effects, Mapping) else {}
    return {
        "id": str(raw.get("id", ""))[:60] or f"{side}-{unit_type}-{len(occupied)}",
        "side": side,
        "unit_type": unit_type,
        "lifepoints": lifepoints,
        "x": x,
        "y": y,
        "effects": {
            "battle_cry": bool(source_effects.get("battle_cry")),
            "stoicism": bool(source_effects.get("stoicism")),
            "charge": bool(source_effects.get("charge")),
            "chastised": bool(source_effects.get("chastised")),
            "vigilance": bool(source_effects.get("vigilance")),
            "shield_wall": bool(source_effects.get("shield_wall")),
        },
    }


def sanitize_conquest_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    occupied: set[tuple[int, int]] = set()
    units = [
        unit
        for value in (raw.get("units") if isinstance(raw.get("units"), Sequence) else ())
        if (unit := _sanitize_unit(value, occupied)) is not None
    ]
    if not units or not any(unit["side"] == "player" for unit in units):
        return {}
    if not any(unit["side"] == "opponent" for unit in units):
        return {}
    for side in _SIDES:
        squad: dict[str, int] = {}
        for unit in units:
            if unit["side"] == side:
                squad[unit["unit_type"]] = squad.get(unit["unit_type"], 0) + 1
        if _setup_errors(squad, ()):
            return {}
    selected_commands = {
        side: list(_copy_commands(
            (raw.get("commands") if isinstance(raw.get("commands"), Mapping) else {}).get(side)
        ))
        for side in _SIDES
    }
    cooldown_source = raw.get("cooldowns")
    cp_source = raw.get("command_points")
    cursor_source = raw.get("unit_cursor")
    first_player = str(raw.get("first_player", "player"))
    obstacles = []
    for value in raw.get("obstacles", ()) if isinstance(raw.get("obstacles"), Sequence) else ():
        if (
            isinstance(value, Sequence)
            and not isinstance(value, (str, bytes))
            and len(value) == 2
        ):
            point = (
                _int(value[0], maximum=CONQUEST_BOARD_SIZE - 1),
                _int(value[1], maximum=CONQUEST_BOARD_SIZE - 1),
            )
            if point not in occupied and point not in obstacles:
                obstacles.append(point)
    return {
        "version": CONQUEST_STATE_VERSION,
        "opponent_label": "Bounded simulated opponent",
        "units": units,
        "obstacles": [list(point) for point in obstacles],
        "commands": selected_commands,
        "cooldowns": {
            side: {
                command_id: _int(
                    (
                        cooldown_source.get(side)
                        if isinstance(cooldown_source, Mapping)
                        and isinstance(cooldown_source.get(side), Mapping)
                        else {}
                    ).get(command_id),
                    maximum=command.cooldown,
                )
                for command_id, command in CONQUEST_COMMANDS_BY_ID.items()
                if command_id in selected_commands[side]
            }
            for side in _SIDES
        },
        "command_points": {
            side: _int(
                (cp_source if isinstance(cp_source, Mapping) else {}).get(
                    side, CONQUEST_STARTING_COMMAND_POINTS
                ),
                maximum=999_999,
            )
            for side in _SIDES
        },
        "doctrines": {
            "player": (
                str((raw.get("doctrines") or {}).get("player", "balanced"))
                if (
                    isinstance(raw.get("doctrines"), Mapping)
                    and str((raw.get("doctrines") or {}).get("player", "balanced"))
                    in _DOCTRINES
                )
                else "balanced"
            ),
            "opponent": "balanced",
        },
        "first_player": first_player if first_player in _SIDES else "player",
        "round": _int(raw.get("round"), maximum=999_999),
        "side_turns": _int(raw.get("side_turns"), maximum=1_999_998),
        "unit_cursor": {
            side: _int(
                (cursor_source if isinstance(cursor_source, Mapping) else {}).get(side),
                maximum=999_999,
            )
            for side in _SIDES
        },
        # The harvest observes the rating floor of 0 and states no maximum, so
        # only the shared storage bound applies here.
        "opponent_rating": _int(
            raw.get("opponent_rating", CONQUEST_RATING_START),
            CONQUEST_RATING_START,
        ),
        "last_exchange": str(raw.get("last_exchange", ""))[:500],
    }


def sanitize_conquest_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    session = sanitize_conquest_session_pure(source.get("conquest"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", CONQUEST_ACTIVITY_ID}:
        session = {}
    result = {
        "conquest": session,
        "conquest_policy": sanitize_conquest_policy_pure(source.get("conquest_policy")),
        "conquest_rating": _int(
            source.get("conquest_rating", CONQUEST_RATING_START),
            CONQUEST_RATING_START,
        ),
        "conquest_matches_started": _int(source.get("conquest_matches_started")),
        "conquest_games_won": _int(source.get("conquest_games_won")),
        "conquest_games_lost": _int(source.get("conquest_games_lost")),
        "conquest_resignations": _int(source.get("conquest_resignations")),
        "conquest_last_result": str(source.get("conquest_last_result", ""))[:500],
    }
    if session and not active_id:
        result["activity_session"] = {"active_id": CONQUEST_ACTIVITY_ID}
    elif not session and active_id == CONQUEST_ACTIVITY_ID:
        result["activity_session"] = {"active_id": ""}
    return result


def set_conquest_policy_pure(
    player_data: Mapping[str, Any],
    payload: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_conquest_state_pure(data)
    if state["conquest"]:
        return data, False, {"reason": "Finish or resign from the current match first."}
    candidate = dict(state["conquest_policy"])
    candidate.update(dict(payload or {}))
    mode = str(candidate.get("automation_mode", "casual"))
    doctrine = str(candidate.get("doctrine", "balanced"))
    if mode not in {"casual", "advanced"}:
        return data, False, {"reason": "Choose Casual or Advanced setup."}
    if doctrine not in _DOCTRINES:
        return data, False, {"reason": "Choose a valid doctrine."}
    squad = (
        dict(CONQUEST_DEFAULT_SQUAD)
        if mode == "casual"
        else _copy_squad(candidate.get("squad"))
    )
    raw_commands = candidate.get("commands")
    if (
        mode == "advanced"
        and isinstance(raw_commands, Sequence)
        and not isinstance(raw_commands, (str, bytes))
        and len(
            {
                str(value)
                for value in raw_commands
                if str(value) in CONQUEST_COMMANDS_BY_ID
            }
        )
        > CONQUEST_MAX_COMMANDS
    ):
        return data, False, {
            "reason": f"Choose at most {CONQUEST_MAX_COMMANDS} commands."
        }
    commands = (
        tuple(CONQUEST_DEFAULT_COMMANDS)
        if mode == "casual"
        else _copy_commands(raw_commands)
    )
    errors = _setup_errors(squad, commands)
    if errors:
        return data, False, {"reason": errors[0], "errors": errors}
    policy = {
        "automation_mode": mode,
        "doctrine": doctrine,
        "squad": squad,
        "commands": list(commands),
    }
    data.update(state)
    data["conquest_policy"] = policy
    return data, True, {"message": "Conquest setup saved.", "policy": policy}


def _deployed_units(squad: Mapping[str, int], side: str) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    # PLACEHOLDER(conquest.default_deployment): troops fill the owner's three
    # deployment rows in reading order, starting on the row at the owner's own
    # edge, so a ten-troop squad forms a single line.
    positions = [
        (column, row if side == "player" else CONQUEST_BOARD_SIZE - 1 - row)
        for row in range(CONQUEST_DEPLOYMENT_ROWS)
        for column in range(CONQUEST_BOARD_SIZE)
    ]
    index = 0
    for spec in CONQUEST_UNITS:
        for serial in range(_int(squad.get(spec.id), maximum=CONQUEST_UNIT_CAP)):
            x, y = positions[index]
            units.append(
                {
                    "id": f"{side}-{spec.id}-{serial + 1}",
                    "side": side,
                    "unit_type": spec.id,
                    "lifepoints": spec.lifepoints,
                    "x": x,
                    "y": y,
                    "effects": {
                        "battle_cry": False,
                        "stoicism": False,
                        "charge": False,
                        "chastised": False,
                        "vigilance": False,
                        "shield_wall": False,
                    },
                }
            )
            index += 1
    return units


def enter_conquest_pure(
    player_data: Mapping[str, Any],
    payload: Mapping[str, Any] | None = None,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    active = player_data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != CONQUEST_ACTIVITY_ID:
        return dict(player_data), False, {
            "reason": "Finish the active persistent activity first."
        }
    if isinstance(player_data.get("combat_encounter"), Mapping) and player_data.get(
        "combat_encounter"
    ):
        return dict(player_data), False, {
            "reason": "Finish or leave the current Combat encounter first."
        }
    if player_combat_level_pure(player_data) < CONQUEST_COMBAT_REQUIREMENT:
        return dict(player_data), False, {
            "reason": f"Conquest requires combat level {CONQUEST_COMBAT_REQUIREMENT}."
        }
    data, ok, info = set_conquest_policy_pure(player_data, payload)
    if not ok:
        return data, False, info
    state = sanitize_conquest_state_pure(data)
    if state["conquest"]:
        return data, False, {"reason": "A Conquest match is already active."}
    policy = state["conquest_policy"]
    layout_index = int(_roll(rng) * len(CONQUEST_BATTLEFIELD_LAYOUTS))
    first_player = (
        "player" if _roll(rng) < 0.5 else "opponent"
    )  # PLACEHOLDER(conquest.first_player_selection)
    # PLACEHOLDER(conquest.simulated_opponent_rating)
    opponent_rating = max(
        CONQUEST_RATING_FLOOR,
        state["conquest_rating"] + int((_roll(rng) - 0.5) * 200),
    )
    units = _deployed_units(policy["squad"], "player")
    units.extend(_deployed_units(CONQUEST_DEFAULT_SQUAD, "opponent"))
    session = {
        "version": CONQUEST_STATE_VERSION,
        "opponent_label": "Bounded simulated opponent",
        "units": units,
        "obstacles": [
            list(point) for point in CONQUEST_BATTLEFIELD_LAYOUTS[layout_index]
        ],
        "commands": {
            "player": list(policy["commands"]),
            "opponent": list(CONQUEST_DEFAULT_COMMANDS),
        },
        "cooldowns": {
            "player": {command_id: 0 for command_id in policy["commands"]},
            "opponent": {command_id: 0 for command_id in CONQUEST_DEFAULT_COMMANDS},
        },
        "command_points": {
            "player": CONQUEST_STARTING_COMMAND_POINTS,
            "opponent": CONQUEST_STARTING_COMMAND_POINTS,
        },
        "doctrines": {
            "player": policy["doctrine"],
            "opponent": "balanced",
        },
        "first_player": first_player,
        "round": 0,
        "side_turns": 0,
        "unit_cursor": {"player": 0, "opponent": 0},
        "opponent_rating": opponent_rating,
        "last_exchange": "Armies deployed.",
    }
    data.update(state)
    data["conquest"] = session
    data["activity_session"] = {"active_id": CONQUEST_ACTIVITY_ID}
    data["current_utility"] = CONQUEST_ACTIVITY_ID
    data["conquest_matches_started"] = state["conquest_matches_started"] + 1
    data["conquest_last_result"] = (
        f"Conquest started against {session['opponent_label']}; "
        f"{first_player} moves first."
    )
    data, newly = refresh_music_log_pure(data)
    return data, True, {
        "message": data["conquest_last_result"],
        "music_unlocked": newly,
        "first_player": first_player,
    }


def _units_for(session: Mapping[str, Any], side: str) -> list[dict[str, Any]]:
    return [unit for unit in session["units"] if unit["side"] == side]


def _distance(left: Mapping[str, Any], right: Mapping[str, Any]) -> int:
    # PLACEHOLDER(conquest.board_metric): four-direction (Manhattan) squares.
    return abs(int(left["x"]) - int(right["x"])) + abs(int(left["y"]) - int(right["y"]))


def _clear_turn_effects(unit: dict[str, Any]) -> None:
    spec = CONQUEST_UNITS_BY_ID[unit["unit_type"]]
    effects = unit["effects"]
    if effects.get("battle_cry") or effects.get("stoicism"):
        unit["lifepoints"] = min(spec.lifepoints, int(unit["lifepoints"]))
    for effect in ("battle_cry", "stoicism", "charge", "vigilance", "shield_wall"):
        effects[effect] = False


def _choose_target(
    enemies: Sequence[dict[str, Any]], doctrine: str, origin: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    if doctrine == "aggressive":
        return min(enemies, key=lambda unit: (int(unit["lifepoints"]), unit["id"]))
    if doctrine == "defensive":
        return max(enemies, key=lambda unit: (int(unit["lifepoints"]), unit["id"]))
    if origin is not None:
        return min(enemies, key=lambda unit: (_distance(origin, unit), unit["id"]))
    return min(enemies, key=lambda unit: unit["id"])


def _use_command(
    session: dict[str, Any],
    side: str,
    rng: Callable[[], float] | None,
) -> str:
    allies = _units_for(session, side)
    enemy_side = "opponent" if side == "player" else "player"
    enemies = _units_for(session, enemy_side)
    cp = int(session["command_points"][side])
    doctrine = str(session["doctrines"][side])
    for command_id in session["commands"][side]:
        command = CONQUEST_COMMANDS_BY_ID[command_id]
        if int(session["cooldowns"][side].get(command_id, 0)) or cp < command.cost:
            continue
        target: dict[str, Any] | None = None
        if command_id == "regenerate":
            damaged = [
                unit
                for unit in allies
                if int(unit["lifepoints"]) < CONQUEST_UNITS_BY_ID[unit["unit_type"]].lifepoints
            ]
            if not damaged:
                continue
            target = min(damaged, key=lambda unit: (int(unit["lifepoints"]), unit["id"]))
            target["lifepoints"] = CONQUEST_UNITS_BY_ID[target["unit_type"]].lifepoints
        elif command_id == "bombard":
            target = _choose_target(enemies, doctrine)
            target["lifepoints"] = max(0, int(target["lifepoints"]) - 100)
            if not target["lifepoints"]:
                session["units"].remove(target)
        elif command_id == "winds_of_fate":
            cooling = [
                value
                for value in session["commands"][side]
                if int(session["cooldowns"][side].get(value, 0)) > 0
            ]
            if not cooling:
                continue
            target_id = cooling[int(_roll(rng) * len(cooling))]
            session["cooldowns"][side][target_id] = 0
        elif command_id == "chastise":
            if len(enemies) <= 1:
                continue
            target = _choose_target(enemies, doctrine)
            target["effects"]["chastised"] = True
        else:
            target = (
                min(allies, key=lambda unit: (int(unit["lifepoints"]), unit["id"]))
                if command_id in {"stoicism", "shield_wall", "vigilance"}
                else max(
                    allies,
                    key=lambda unit: (
                        CONQUEST_UNITS_BY_ID[unit["unit_type"]].damage,
                        unit["id"],
                    ),
                )
            )
            if command_id == "battle_cry":
                target["effects"]["battle_cry"] = True
                target["lifepoints"] += 200
            elif command_id == "stoicism":
                target["effects"]["stoicism"] = True
                target["lifepoints"] += 400
            else:
                target["effects"][command_id] = True
        session["command_points"][side] = cp - command.cost
        session["cooldowns"][side][command_id] = command.cooldown
        return command.display_name
    return ""


def _reachable_positions(
    session: Mapping[str, Any], unit: Mapping[str, Any], movement: int
) -> set[tuple[int, int]]:
    blocked = {
        (int(other["x"]), int(other["y"]))
        for other in session["units"]
        if other["id"] != unit["id"]
    }
    blocked.update(tuple(point) for point in session["obstacles"])
    start = (int(unit["x"]), int(unit["y"]))
    seen = {start}
    queue = deque([(start, 0)])
    while queue:
        (x, y), steps = queue.popleft()
        if steps >= movement:
            continue
        # PLACEHOLDER(conquest.board_metric): steps share the same four
        # directions the range metric measures.
        for point in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (
                0 <= point[0] < CONQUEST_BOARD_SIZE
                and 0 <= point[1] < CONQUEST_BOARD_SIZE
                and point not in blocked
                and point not in seen
            ):
                seen.add(point)
                queue.append((point, steps + 1))
    return seen


def _damage(attacker: Mapping[str, Any], defender: Mapping[str, Any]) -> int:
    amount = CONQUEST_UNITS_BY_ID[attacker["unit_type"]].damage
    if attacker["effects"].get("battle_cry"):
        amount += 200
    if defender["effects"].get("shield_wall"):
        amount = min(amount, 100)
    return amount


def _attack(
    session: dict[str, Any], attacker: dict[str, Any], defender: dict[str, Any]
) -> tuple[bool, bool]:
    if defender["effects"].get("vigilance"):
        attacker["lifepoints"] = max(0, int(attacker["lifepoints"]) - _damage(defender, attacker))
        if not attacker["lifepoints"]:
            session["units"].remove(attacker)
            session["command_points"][defender["side"]] += CONQUEST_UNITS_BY_ID[
                attacker["unit_type"]
            ].cost  # PLACEHOLDER(conquest.kill_command_points)
            return False, True
    defender["lifepoints"] = max(0, int(defender["lifepoints"]) - _damage(attacker, defender))
    if not defender["lifepoints"]:
        session["units"].remove(defender)
        session["command_points"][attacker["side"]] += CONQUEST_UNITS_BY_ID[
            defender["unit_type"]
        ].cost  # PLACEHOLDER(conquest.kill_command_points)
        return True, False
    return False, False


def _run_side_turn(
    session: dict[str, Any], side: str, rng: Callable[[], float] | None
) -> str:
    allies = _units_for(session, side)
    if not allies:
        return f"{side} had no troops."
    for unit in allies:
        _clear_turn_effects(unit)
    for command_id in session["cooldowns"][side]:
        session["cooldowns"][side][command_id] = max(
            0, int(session["cooldowns"][side][command_id]) - 1
        )  # PLACEHOLDER(conquest.command_cooldown_boundary)
    if int(session["side_turns"]) > 0:
        session["command_points"][side] += CONQUEST_PASSIVE_COMMAND_POINTS
    command_name = _use_command(session, side, rng)
    enemies = _units_for(session, "opponent" if side == "player" else "player")
    if not enemies:
        return f"{side} used {command_name}." if command_name else f"{side} ended the match."
    movable = [unit for unit in allies if not unit["effects"].get("chastised")]
    if not movable:
        for unit in allies:
            unit["effects"]["chastised"] = False
        session["side_turns"] += 1
        return f"{side} was Chastised."
    cursor = int(session["unit_cursor"][side]) % len(movable)
    attacker = sorted(movable, key=lambda unit: unit["id"])[cursor]
    session["unit_cursor"][side] = cursor + 1
    doctrine = str(session["doctrines"][side])
    target = _choose_target(enemies, doctrine, attacker)
    spec = CONQUEST_UNITS_BY_ID[attacker["unit_type"]]
    movement = spec.movement * (2 if attacker["effects"].get("charge") else 1)
    reachable = _reachable_positions(session, attacker, movement)
    best = min(
        reachable,
        key=lambda point: (
            abs(point[0] - int(target["x"])) + abs(point[1] - int(target["y"])),
            point[1] if side == "player" else -point[1],
            point[0],
        ),
    )
    attacker["x"], attacker["y"] = best
    enemies = _units_for(session, "opponent" if side == "player" else "player")
    in_range = [unit for unit in enemies if _distance(attacker, unit) <= spec.attack_range]
    detail = ""
    if in_range:
        target = _choose_target(in_range, doctrine, attacker)
        killed, counter_killed = _attack(session, attacker, target)
        if killed:
            detail = f"killed {target['unit_type'].replace('_', ' ')}"
        elif counter_killed:
            detail = "fell to Vigilance"
        else:
            detail = f"hit {target['unit_type'].replace('_', ' ')}"
    else:
        detail = "advanced"
    session["side_turns"] += 1
    for unit in allies:
        unit["effects"]["chastised"] = False
    prefix = f"{side} used {command_name}; " if command_name else f"{side} "
    return prefix + detail + "."


def _commendation_multiplier(combat_level: int) -> tuple[int, int]:
    if combat_level >= 100:
        return 4, 40
    if combat_level >= 70:
        return 3, 30
    return 2, 20


def _turn_ratio(rounds: int) -> int:
    ratio = 1
    for minimum, value in CONQUEST_TURN_RATIO_CURVE:
        if rounds >= minimum:
            ratio = value
    return ratio


def _rating_delta(winner_rating: int, loser_rating: int) -> int:
    expected = 1.0 / (
        1.0
        + math.pow(
            10.0,
            (loser_rating - winner_rating) / CONQUEST_RATING_DIVISOR,
        )
    )
    return max(1, round(CONQUEST_RATING_K * (1.0 - expected)))


def _finish_match(
    data: dict[str, Any], session: Mapping[str, Any], outcome: str, reason: str
) -> dict[str, Any]:
    state = sanitize_conquest_state_pure(data)
    data.update(state)
    rounds = _int(session.get("round"))
    eligible = rounds >= CONQUEST_EARLY_GAME_THRESHOLD
    commendations = 0
    rating_change = 0
    if eligible:
        multiplier, cap = _commendation_multiplier(player_combat_level_pure(data))
        commendations = min(cap, _turn_ratio(rounds) * multiplier)
        old_wallet = _int(
            data.get("pest_control_commendations"),
            maximum=PEST_CONTROL_COMMENDATION_CAP,
        )
        data["pest_control_commendations"] = min(
            PEST_CONTROL_COMMENDATION_CAP, old_wallet + commendations
        )
        # A wallet at the shared cap absorbs part of the award, so the match
        # reports what it actually paid rather than what it earned.
        commendations = data["pest_control_commendations"] - old_wallet
        player_rating = state["conquest_rating"]
        opponent_rating = _int(session.get("opponent_rating"), CONQUEST_RATING_START)
        if outcome == "won":
            rating_change = _rating_delta(player_rating, opponent_rating)
        else:
            rating_change = -_rating_delta(opponent_rating, player_rating)
        data["conquest_rating"] = max(
            CONQUEST_RATING_FLOOR, player_rating + rating_change
        )
    if outcome == "won":
        data["conquest_games_won"] = state["conquest_games_won"] + 1
    else:
        data["conquest_games_lost"] = state["conquest_games_lost"] + 1
    if reason == "resigned":
        data["conquest_resignations"] = state["conquest_resignations"] + 1
    data["conquest"] = {}
    data["activity_session"] = {"active_id": ""}
    eligibility_note = (
        f"{commendations} commendations, rating {rating_change:+d}"
        if eligible
        else "ended before the reward threshold; no rating or commendations"
    )
    message = f"Conquest {outcome}: {reason}; {eligibility_note}."
    data["conquest_last_result"] = message
    return {
        "terminal": True,
        "won": outcome == "won",
        "outcome": outcome,
        "reason": reason,
        "eligible": eligible,
        "commendations": commendations,
        "rating_change": rating_change,
        "message": message,
    }


def apply_conquest_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    productive: bool = True,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if not productive:
        return dict(player_data), False, {
            "reason": "Only a productive review advances Conquest."
        }
    data = copy.deepcopy(dict(player_data))
    state = sanitize_conquest_state_pure(data)
    session = copy.deepcopy(state["conquest"])
    if not session:
        return dict(player_data), False, {
            "reason": "Enter Conquest before training."
        }
    order = (
        (session["first_player"], "opponent" if session["first_player"] == "player" else "player")
    )
    events: list[str] = []
    for side in order:
        events.append(_run_side_turn(session, side, rng))
        enemy_side = "opponent" if side == "player" else "player"
        if not _units_for(session, enemy_side):
            session["round"] += 1
            result = _finish_match(
                data,
                session,
                "won" if side == "player" else "lost",
                "the opposing army was eliminated",
            )
            return data, True, {**result, "events": tuple(events)}
    session["round"] += 1
    session["last_exchange"] = " ".join(events)
    data.update(state)
    data["conquest"] = session
    data["conquest_last_result"] = (
        f"Conquest round {session['round']}: {session['last_exchange']}"
    )
    return data, True, {
        "terminal": False,
        "round": session["round"],
        "events": tuple(events),
        "status": data["conquest_last_result"],
        "message": data["conquest_last_result"],
    }


def resign_conquest_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_conquest_state_pure(data)
    if not state["conquest"]:
        return dict(player_data), False, {"reason": "No Conquest match is active."}
    result = _finish_match(data, state["conquest"], "lost", "resigned")
    return data, True, result


def conquest_view_pure(
    player_data: Mapping[str, Any],
    draft_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state = sanitize_conquest_state_pure(player_data)
    session = state["conquest"]
    policy = state["conquest_policy"]
    if draft_policy is not None and not session:
        source = dict(policy)
        source.update(dict(draft_policy))
        mode = str(source.get("automation_mode", "casual"))
        doctrine = str(source.get("doctrine", "balanced"))
        policy = {
            "automation_mode": mode if mode in {"casual", "advanced"} else "casual",
            "doctrine": doctrine if doctrine in _DOCTRINES else "balanced",
            "squad": (
                dict(CONQUEST_DEFAULT_SQUAD)
                if mode == "casual"
                else _copy_squad(source.get("squad"))
            ),
            "commands": list(
                CONQUEST_DEFAULT_COMMANDS
                if mode == "casual"
                else _copy_commands(source.get("commands"))
            ),
        }
    combat_level = player_combat_level_pure(player_data)
    active = player_data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    entry_reasons: list[str] = []
    if combat_level < CONQUEST_COMBAT_REQUIREMENT:
        entry_reasons.append(
            f"Requires combat level {CONQUEST_COMBAT_REQUIREMENT}."
        )
    if active_id and active_id != CONQUEST_ACTIVITY_ID:
        entry_reasons.append("Finish the active persistent activity first.")
    if isinstance(player_data.get("combat_encounter"), Mapping) and player_data.get(
        "combat_encounter"
    ):
        entry_reasons.append("Finish the active Combat encounter first.")
    selected_squad = _copy_squad(policy["squad"])
    selected_commands = _copy_commands(policy["commands"])
    count, cost = _squad_totals(selected_squad)
    setup_errors = _setup_errors(selected_squad, selected_commands)
    advanced = policy["automation_mode"] == "advanced"
    command_rows = []
    for command in CONQUEST_COMMANDS:
        selected = command.id in selected_commands
        command_rows.append(
            {
                "id": command.id,
                "label": f"{command.display_name} · {command.cost} CP · CD {command.cooldown}",
                "effect": command.effect,
                "selected": selected,
                "enabled": (
                    not session
                    and advanced
                    and (selected or len(selected_commands) < CONQUEST_MAX_COMMANDS)
                ),
                "tooltip": command.effect,
            }
        )
    return {
        **state,
        "active": bool(session),
        "combat_level": combat_level,
        "entry_reasons": tuple(entry_reasons),
        "primary_text": (
            "Selected for reviews"
            if session and str(player_data.get("current_utility", "")) == CONQUEST_ACTIVITY_ID
            else "Select for reviews"
            if session
            else "Start Conquest"
        ),
        "primary_enabled": bool(session) or not entry_reasons and not setup_errors,
        "resign_visible": bool(session),
        "resign_enabled": bool(session),
        "setup_controls_enabled": not session,
        "advanced_controls_enabled": not session and advanced,
        "save_enabled": not session and not setup_errors,
        "setup_errors": setup_errors,
        "opponent_label": (
            str(session.get("opponent_label", "")) if session else "Bounded simulated opponent"
        ),
        "status_text": (
            state["conquest_last_result"]
            or "Safe Activities match · one productive review resolves one turn exchange."
        ),
        "summary_text": (
            f"Round {session['round']} · "
            f"{len(_units_for(session, 'player'))}–{len(_units_for(session, 'opponent'))} troops · "
            f"{session['command_points']['player']} CP"
            if session
            else f"{count}/{CONQUEST_UNIT_CAP} troops · {cost:,}/{CONQUEST_SETUP_BUDGET:,} points · "
            f"{len(selected_commands)}/{CONQUEST_MAX_COMMANDS} commands"
        ),
        "squad_rows": tuple(
            {
                "id": unit.id,
                "label": unit.display_name,
                "stat_text": (
                    f"{unit.cost} · {unit.lifepoints} LP · {unit.damage} dmg · "
                    f"move {unit.movement} · range {unit.attack_range}"
                ),
                "count": selected_squad[unit.id],
                "enabled": not session and advanced,
            }
            for unit in CONQUEST_UNITS
        ),
        "command_rows": tuple(command_rows),
        "rating": state["conquest_rating"],
        "commendations": _int(
            player_data.get("pest_control_commendations"),
            maximum=PEST_CONTROL_COMMENDATION_CAP,
        ),
        "timeout_resolution": CONQUEST_TIMEOUT_RESOLUTION,
    }


def apply_conquest_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if action_id == "enter":
        return enter_conquest_pure(player_data, payload, rng)
    if action_id == "set_policy":
        return set_conquest_policy_pure(player_data, payload)
    if action_id == "resign":
        return resign_conquest_pure(player_data)
    return dict(player_data), False, {"reason": "Unknown Conquest command."}
