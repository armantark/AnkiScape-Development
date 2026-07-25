"""Pure Dungeoneering progression and starter-floor substrate."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Iterable, Optional

from ..data.dungeoneering_data import (
    AMMO_BIND_CAPACITY,
    BIND_SLOTS_BY_LEVEL,
    COMPLEXITIES_BY_LEVEL,
    DUNGEONEERING_MAX_FLOOR,
    DUNGEONEERING_MAX_LEVEL,
    FLOOR_SIZES_BY_ID,
    FLOOR_THEMES,
    FROZEN_BOSSES,
    SALT_IN_THE_WOUND_AMMO_BIND_CAPACITY,
    STARTER_SMALL_ROOM_BUDGET,
    FloorTheme,
    FrozenBoss,
    RoomFamily,
)


@dataclass(frozen=True)
class DungeonRoom:
    id: int
    family: RoomFamily
    connected_room_ids: tuple[int, ...]
    critical_path: bool


@dataclass(frozen=True)
class DungeonSession:
    floor: int
    complexity: int
    seed: int
    rooms: tuple[DungeonRoom, ...]
    resolved_room_ids: tuple[int, ...]
    frontier_room_ids: tuple[int, ...]
    current_room_id: int
    death_count: int = 0
    completed: bool = False


@dataclass(frozen=True)
class FloorReplayResolution:
    completed_floor: int
    credited_floor: Optional[int]
    xp_floor: int
    repeated_without_credit: bool


@dataclass(frozen=True)
class CompletionPayout:
    base_xp: float
    adjusted_xp: float
    final_xp: float
    tokens: int


def _clean_level(level: object) -> int:
    try:
        parsed = int(level)
    except (TypeError, ValueError, OverflowError):
        parsed = 1
    return max(1, min(parsed, DUNGEONEERING_MAX_LEVEL))


def _validate_floor(floor: object) -> int:
    if isinstance(floor, bool):
        raise ValueError("floor must be an integer from 1 to 60")
    try:
        parsed = int(floor)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("floor must be an integer from 1 to 60") from exc
    if parsed < 1 or parsed > DUNGEONEERING_MAX_FLOOR:
        raise ValueError("floor must be an integer from 1 to 60")
    return parsed


def required_level_for_floor_pure(floor: object) -> int:
    return (_validate_floor(floor) * 2) - 1


def maximum_floor_for_level_pure(level: object) -> int:
    return min(DUNGEONEERING_MAX_FLOOR, (_clean_level(level) + 1) // 2)


def floor_theme_for_floor_pure(floor: object) -> FloorTheme:
    parsed = _validate_floor(floor)
    return next(
        theme
        for theme in FLOOR_THEMES
        if theme.first_floor <= parsed <= theme.last_floor
    )


def active_bind_slots_for_level_pure(level: object) -> int:
    clean = _clean_level(level)
    return max(slots for minimum_level, slots in BIND_SLOTS_BY_LEVEL if clean >= minimum_level)


def ammo_bind_capacity_pure(*, salt_in_the_wound_complete: bool = False) -> int:
    return (
        SALT_IN_THE_WOUND_AMMO_BIND_CAPACITY
        if salt_in_the_wound_complete
        else AMMO_BIND_CAPACITY
    )


def complexity_multiplier_pure(complexity: object) -> float:
    try:
        parsed = int(complexity)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("complexity must be from 1 to 6") from exc
    definition = COMPLEXITIES_BY_LEVEL.get(parsed)
    if definition is None:
        raise ValueError("complexity must be from 1 to 6")
    return (100.0 - definition.xp_penalty_percent) / 100.0


def prestige_value_pure(current_progress: object, previous_progress: object) -> int:
    def clean(value: object) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError, OverflowError):
            parsed = 0
        return max(0, min(parsed, DUNGEONEERING_MAX_FLOOR))

    return max(clean(current_progress), clean(previous_progress))


def _clean_xp(value: object, name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite and non-negative") from exc
    if not math.isfinite(parsed) or parsed < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return parsed


def calculate_completion_payout_pure(
    *,
    active_floor_xp: object,
    prestige_floor_xp: object,
    complexity: object,
    death_multiplier: object = 1.0,
    bonus_multiplier: object = 1.0,
) -> CompletionPayout:
    """Apply the sourced payout order with externally supplied blocked factors.

    This does not derive the active/prestige floor XP curve or the death
    multiplier.  Callers must supply those only after their own source boundary
    is closed; a no-death floor uses ``death_multiplier=1``.
    """

    active = _clean_xp(active_floor_xp, "active_floor_xp")
    prestige = _clean_xp(prestige_floor_xp, "prestige_floor_xp")
    death = _clean_xp(death_multiplier, "death_multiplier")
    bonus = _clean_xp(bonus_multiplier, "bonus_multiplier")
    if death > 1:
        raise ValueError("death_multiplier cannot exceed 1")
    base = (active + prestige) / 2.0
    adjusted = base * complexity_multiplier_pure(complexity) * death
    final = adjusted * bonus
    return CompletionPayout(base, adjusted, final, math.floor(final / 10.0))


def resolve_floor_replay_pure(
    completed_floor: object,
    checked_floors: Iterable[object],
) -> FloorReplayResolution:
    """Resolve the period same-theme lower-then-higher substitution rule."""

    floor = _validate_floor(completed_floor)
    checked: set[int] = set()
    for candidate in checked_floors:
        try:
            checked.add(_validate_floor(candidate))
        except ValueError:
            continue
    if floor not in checked:
        return FloorReplayResolution(floor, floor, floor, False)

    theme = floor_theme_for_floor_pure(floor)
    lower = [
        candidate
        for candidate in range(floor - 1, theme.first_floor - 1, -1)
        if candidate not in checked
    ]
    if lower:
        credited = lower[0]
        return FloorReplayResolution(floor, credited, credited, False)

    higher = [
        candidate
        for candidate in range(floor + 1, theme.last_floor + 1)
        if candidate not in checked
    ]
    if higher:
        credited = higher[0]
        return FloorReplayResolution(floor, credited, floor, False)

    return FloorReplayResolution(floor, None, floor, True)


def eligible_frozen_bosses_pure(floor: object, level: object) -> tuple[FrozenBoss, ...]:
    parsed_floor = _validate_floor(floor)
    if floor_theme_for_floor_pure(parsed_floor).id != "frozen":
        return ()
    clean_level = _clean_level(level)
    return tuple(
        boss
        for boss in FROZEN_BOSSES
        if boss.first_floor <= parsed_floor <= boss.last_floor
        and clean_level >= boss.minimum_level
    )


def _connect(adjacency: dict[int, set[int]], left: int, right: int) -> None:
    adjacency[left].add(right)
    adjacency[right].add(left)


def build_starter_floor_graph_pure(
    *,
    seed: object,
    complexity: object,
    room_count: object = STARTER_SMALL_ROOM_BUDGET,
) -> tuple[DungeonRoom, ...]:
    """Build the owner-approved seeded small-floor graph.

    The default eight-room budget is an explicitly labelled AnkiScape
    translation.  The period source proves only that a small floor has a 4x4
    grid, at most sixteen rooms, and usually fewer.
    """

    try:
        parsed_seed = int(seed)
        parsed_complexity = int(complexity)
        parsed_count = int(room_count)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("seed, complexity, and room_count must be integers") from exc
    if parsed_complexity not in (1, 6):
        raise ValueError("the starter expedition supports complexity 1 or 6")
    maximum_rooms = FLOOR_SIZES_BY_ID["small"].maximum_rooms
    if parsed_count < 4 or parsed_count > maximum_rooms:
        raise ValueError("starter room_count must be from 4 to 16")

    rng = random.Random(parsed_seed)
    critical_count = max(4, math.ceil(parsed_count * 2 / 3))
    critical_ids = tuple(range(critical_count))
    boss_id = critical_ids[-1]
    adjacency = {room_id: set() for room_id in range(parsed_count)}
    for left, right in zip(critical_ids, critical_ids[1:]):
        _connect(adjacency, left, right)

    branch_parents = list(critical_ids[1:-1]) or [0]
    for room_id in range(critical_count, parsed_count):
        parent = rng.choice(branch_parents)
        _connect(adjacency, parent, room_id)
        branch_parents.append(room_id)

    if parsed_complexity == 1:
        available_families: tuple[RoomFamily, ...] = ("guardian", "key")
    else:
        available_families = ("guardian", "key", "skill", "resource")
    interior_ids = list(range(1, parsed_count))
    interior_ids.remove(boss_id)
    assigned: dict[int, RoomFamily] = {}
    shuffled_ids = interior_ids[:]
    rng.shuffle(shuffled_ids)
    required = list(available_families)
    for room_id, family in zip(shuffled_ids, required):
        assigned[room_id] = family
    for room_id in shuffled_ids[len(required) :]:
        assigned[room_id] = rng.choice(available_families)

    rooms = []
    for room_id in range(parsed_count):
        if room_id == 0:
            family: RoomFamily = "start"
        elif room_id == boss_id:
            family = "boss"
        else:
            family = assigned[room_id]
        rooms.append(
            DungeonRoom(
                room_id,
                family,
                tuple(sorted(adjacency[room_id])),
                room_id in critical_ids,
            )
        )
    return tuple(rooms)


def begin_starter_session_pure(
    *,
    floor: object,
    dungeoneering_level: object,
    complexity: object,
    seed: object,
    room_count: object = STARTER_SMALL_ROOM_BUDGET,
) -> DungeonSession:
    parsed_floor = _validate_floor(floor)
    level = _clean_level(dungeoneering_level)
    if floor_theme_for_floor_pure(parsed_floor).id != "frozen":
        raise ValueError("the starter expedition is limited to Frozen floors 1-11")
    if level < required_level_for_floor_pure(parsed_floor):
        raise ValueError("Dungeoneering level is too low for this floor")
    rooms = build_starter_floor_graph_pure(
        seed=seed,
        complexity=complexity,
        room_count=room_count,
    )
    start = rooms[0]
    return DungeonSession(
        parsed_floor,
        int(complexity),
        int(seed),
        rooms,
        (start.id,),
        start.connected_room_ids,
        start.id,
    )


def resolve_starter_room_pure(
    session: DungeonSession,
    room_id: object,
) -> DungeonSession:
    if session.completed:
        raise ValueError("the floor is already complete")
    try:
        parsed_room = int(room_id)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("room_id must be an integer") from exc
    if parsed_room not in session.frontier_room_ids:
        raise ValueError("room is not on the revealed frontier")
    room = session.rooms[parsed_room]
    resolved = tuple(sorted(set(session.resolved_room_ids) | {parsed_room}))
    frontier = set(session.frontier_room_ids)
    frontier.discard(parsed_room)
    frontier.update(
        neighbor
        for neighbor in room.connected_room_ids
        if neighbor not in resolved
    )
    return replace(
        session,
        resolved_room_ids=resolved,
        frontier_room_ids=tuple(sorted(frontier)),
        current_room_id=parsed_room,
        completed=room.family == "boss",
    )


def record_starter_death_pure(session: DungeonSession) -> DungeonSession:
    start = session.rooms[0]
    return replace(
        session,
        current_room_id=start.id,
        death_count=session.death_count + 1,
        completed=False,
    )
