"""Pure Dungeoneering progression and starter-floor substrate."""

from __future__ import annotations

import copy
import math
import random
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from typing import Any, Iterable, Optional

from ..data.dungeoneering_data import (
    AMMO_BIND_CAPACITY,
    BIND_LOADOUT_COUNT,
    BIND_SLOTS_BY_LEVEL,
    COAL_BAG_CAPACITY,
    COAL_BAG_REWARD,
    COLLECTED_BIND_LIMIT,
    COMPLEXITIES_BY_LEVEL,
    DUNGEONEERING_ACTIVITY_ID,
    DUNGEONEERING_COMBAT_TARGET_ID,
    DUNGEONEERING_COMBAT_TICKS_PER_REVIEW,
    DUNGEONEERING_MAX_FLOOR,
    DUNGEONEERING_REWARDS,
    DUNGEONEERING_REWARDS_BY_ID,
    DUNGEONEERING_MAX_LEVEL,
    DUNGEONEERING_STATE_VERSION,
    FLOOR_SIZES_BY_ID,
    FLOOR_THEMES,
    FLOOR_THEMES_BY_ID,
    FROZEN_BOSSES,
    FROZEN_BOSSES_BY_ID,
    FROZEN_BOSS_COMBAT_LEVEL_LADDERS,
    FROZEN_SKILL_DOORS,
    FROZEN_SKILL_DOORS_BY_ID,
    KINSHIP_CLASSES,
    KINSHIP_CLASSES_BY_ID,
    KINSHIP_TIER_COSTS,
    SALT_IN_THE_WOUND_AMMO_BIND_CAPACITY,
    SKILL_DOOR_FAILURE_CHANCE,
    SKILL_DOOR_FAILURE_DAMAGE_MULTIPLIER,
    SMUGGLER_ITEMS_BY_ID,
    SMUGGLER_SELLBACK_RATE,
    SMUGGLER_STOCK_BANDS,
    STARTER_HERBLORE_CHAIN,
    STARTER_RESOURCE_CHAIN,
    STARTER_SKILL_DOOR_REQUIREMENT,
    STARTER_SMALL_GRAPH_ROOM_COUNT,
    STARTER_SMALL_REVIEW_BUDGET,
    FloorTheme,
    FrozenBoss,
    RoomFamily,
)
from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    combat_max_lifepoints_pure,
    player_combat_level_pure,
)


@dataclass(frozen=True)
class DungeonRoom:
    id: int
    family: RoomFamily
    connected_room_ids: tuple[int, ...]
    critical_path: bool
    skill_door_id: str = ""
    required_level: int = 0


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
    total_modifier: float


# PLACEHOLDER(dungeoneering.floor_xp_curve): a period server getFloorXP routine or decoded completion table
_FLOOR_XP_SIZE_SCALES = {"small": 1.0, "medium": 2.0, "large": 3.5}
# PLACEHOLDER(dungeoneering.completion_modifiers): a period Winterface coefficient table or decoded completion routine
_COMPLETION_SIZE_BONUSES = {"small": 0.0, "medium": 0.0792, "large": 0.1583}
_COMPLETION_BONUS_ROOM_CAP = 0.1267
_COMPLETION_GUIDE_PENALTY = 0.05
_COMPLETION_MINIMUM_MULTIPLIER = 0.10
# PLACEHOLDER(dungeoneering.death_xp_penalty_curve): a period modifier table giving the first-death value and all increments
_DEATH_PENALTY_MINIMUM = 0.04
_DEATH_PENALTY_MAXIMUM = 0.70
_DEATH_PENALTY_COUNT_CAP = 15
_VALID_RESOURCE_POLICIES = frozenset({"gather_and_process", "gather_only", "skip"})
# PLACEHOLDER(dungeoneering.starter_guardian_coin_drops): a decoded period drop table for the Frozen-floor guardians
_STARTER_GUARDIAN_COIN_DROPS = (
    SMUGGLER_ITEMS_BY_ID["vial"].buy_price
    + SMUGGLER_ITEMS_BY_ID["void_dust"].buy_price
)


def _roll(rng: Callable[[], float] | None) -> float:
    if rng is None:
        return 0.5
    try:
        return max(0.0, min(0.999999999, float(rng())))
    except (TypeError, ValueError, OverflowError, StopIteration):
        return 0.5


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    quests = player_data.get("quests")
    state = quests.get(quest_id) if isinstance(quests, Mapping) else None
    return bool(isinstance(state, Mapping) and state.get("completed"))


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


def _clean_modifier(value: object, name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"{name} must be finite")
    return parsed


def calculate_completion_payout_pure(
    *,
    active_floor_xp: object,
    prestige_floor_xp: object,
    complexity: object,
    death_penalty: object = 0.0,
    completion_modifier: object = 0.0,
    minimum_multiplier: object = _COMPLETION_MINIMUM_MULTIPLIER,
) -> CompletionPayout:
    """Apply the sourced active/prestige average and additive modifier order."""

    active = _clean_xp(active_floor_xp, "active_floor_xp")
    prestige = _clean_xp(prestige_floor_xp, "prestige_floor_xp")
    death = _clean_xp(death_penalty, "death_penalty")
    completion = _clean_modifier(completion_modifier, "completion_modifier")
    minimum = _clean_xp(minimum_multiplier, "minimum_multiplier")
    if death > 1:
        raise ValueError("death_penalty cannot exceed 1")
    if minimum > 1:
        raise ValueError("minimum_multiplier cannot exceed 1")
    base = (active + prestige) / 2.0
    complexity_multiplier = complexity_multiplier_pure(complexity)
    adjusted = base * complexity_multiplier
    total_modifier = max(
        minimum,
        complexity_multiplier + completion - death,
    )
    final = base * total_modifier
    return CompletionPayout(
        base,
        adjusted,
        final,
        math.floor(final / 10.0),
        total_modifier,
    )


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
    # PLACEHOLDER(dungeoneering.floor_replay_substitution_direction): a period routine or dated worked example with several unticked lower floors
    lower = [
        candidate
        for candidate in range(theme.first_floor, floor)
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


def select_frozen_boss_pure(*, floor: object, level: object, seed: object) -> FrozenBoss:
    eligible = eligible_frozen_bosses_pure(floor, level)
    if not eligible:
        raise ValueError("no Frozen boss is eligible for this floor")
    try:
        parsed_seed = int(seed)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("seed must be an integer") from exc
    return random.Random(parsed_seed ^ 0xD06E).choice(eligible)


def frozen_boss_combat_level_pure(
    boss_id: object,
    player_data: Mapping[str, Any],
) -> int:
    ladder = FROZEN_BOSS_COMBAT_LEVEL_LADDERS.get(str(boss_id))
    if ladder is None:
        raise ValueError("unknown Frozen boss")
    # PLACEHOLDER(dungeoneering.boss_level_scaling_formula): period server logic covering player level, complexity, and intended party size
    target = 1.5 * player_combat_level_pure(player_data)
    return min(ladder, key=lambda level: (abs(level - target), level))


def frozen_boss_enemy_pure(boss_id: object, combat_level: object) -> dict[str, Any]:
    boss = FROZEN_BOSSES_BY_ID.get(str(boss_id))
    ladder = FROZEN_BOSS_COMBAT_LEVEL_LADDERS.get(str(boss_id))
    try:
        level = int(combat_level)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("combat_level must be on the boss ladder") from exc
    if boss is None or ladder is None or level not in ladder:
        raise ValueError("combat_level must be on the boss ladder")
    # PLACEHOLDER(dungeoneering.boss_combat_definitions): authentic per-tier combat definitions or a decoded period stat table
    lifepoints = (25 * level) + 1
    hp_level = lifepoints // 10
    defence = int((((level / 1.32) + 1) / 0.25) - hp_level)
    remaining = level - int((defence + hp_level) * 0.25) - 1
    offence = int((remaining / 0.325) / 1.5)
    generated = max(0, min(120, int((defence + offence) / 2)))
    return {
        "display_name": boss.display_name,
        "level": level,
        "group": "Dungeoneering",
        "stats": {
            "attack": generated,
            "strength": generated,
            "defence": generated,
            "magic": generated,
            "ranged": generated,
            "hitpoints": lifepoints,
        },
        "bonuses": {},
        "max_hit": level,
        "drops": {"guaranteed": (), "tables": ()},
        "source": "registered Dungeoneering boss placeholders; empty drops are deliberate",
    }


def _connect(adjacency: dict[int, set[int]], left: int, right: int) -> None:
    adjacency[left].add(right)
    adjacency[right].add(left)


def build_starter_floor_graph_pure(
    *,
    seed: object,
    complexity: object,
    room_count: object = STARTER_SMALL_GRAPH_ROOM_COUNT,
    skill_levels: Mapping[str, object] | None = None,
) -> tuple[DungeonRoom, ...]:
    """Build the owner-approved seeded small-floor graph.

    The default graph gives the pre-resolved start room and eight-review
    critical path one optional branch. The period source proves only that a
    small floor has a 4x4 grid, at most sixteen rooms, and usually fewer.
    ``skill_levels`` remains an accepted storage-call input, but the starter's
    disclosed level-1 proof doors do not derive requirements from player state.
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
    critical_count = min(parsed_count, STARTER_SMALL_REVIEW_BUDGET + 1)
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
    critical_interior = list(critical_ids[1:-1])
    rng.shuffle(critical_interior)
    for room_id, family in zip(critical_interior, available_families):
        assigned[room_id] = family
    remaining_ids = [room_id for room_id in interior_ids if room_id not in assigned]
    rng.shuffle(remaining_ids)
    for room_id in remaining_ids:
        assigned[room_id] = rng.choice(available_families)

    rooms = []
    for room_id in range(parsed_count):
        if room_id == 0:
            family: RoomFamily = "start"
        elif room_id == boss_id:
            family = "boss"
        else:
            family = assigned[room_id]
        skill_door_id = ""
        required_level = 0
        if family == "skill":
            skill_door = rng.choice(FROZEN_SKILL_DOORS)
            skill_door_id = skill_door.id
            required_level = STARTER_SKILL_DOOR_REQUIREMENT
        rooms.append(
            DungeonRoom(
                room_id,
                family,
                tuple(sorted(adjacency[room_id])),
                room_id in critical_ids,
                skill_door_id,
                required_level,
            )
        )
    return tuple(rooms)


def begin_starter_session_pure(
    *,
    floor: object,
    dungeoneering_level: object,
    complexity: object,
    seed: object,
    room_count: object = STARTER_SMALL_GRAPH_ROOM_COUNT,
    skill_levels: Mapping[str, object] | None = None,
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
        skill_levels=skill_levels,
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


def starter_floor_xp_pure(
    *,
    floor: object,
    size: object,
    opened_rooms: object,
) -> int:
    parsed_floor = _validate_floor(floor)
    size_id = str(size)
    definition = FLOOR_SIZES_BY_ID.get(size_id)
    if definition is None:
        raise ValueError("size must be small, medium, or large")
    try:
        opened = int(opened_rooms)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("opened_rooms must be an integer") from exc
    opened = max(0, min(opened, definition.maximum_rooms))
    curve = (
        0.16 * parsed_floor**3
        + 0.28 * parsed_floor**2
        + 76.94 * parsed_floor
        + 100
    )
    return math.trunc(
        curve
        * _FLOOR_XP_SIZE_SCALES[size_id]
        * opened
        / definition.maximum_rooms
    )


def death_xp_penalty_pure(death_count: object) -> float:
    try:
        counted = int(death_count)
    except (TypeError, ValueError, OverflowError):
        counted = 0
    counted = max(0, min(counted, _DEATH_PENALTY_COUNT_CAP))
    if counted == 0:
        return 0.0
    if counted == 1:
        return _DEATH_PENALTY_MINIMUM
    return _DEATH_PENALTY_MINIMUM + (
        (_DEATH_PENALTY_MAXIMUM - _DEATH_PENALTY_MINIMUM)
        * (counted - 1)
        / (_DEATH_PENALTY_COUNT_CAP - 1)
    )


def starter_completion_modifier_pure(
    session: DungeonSession,
    *,
    size: object = "small",
) -> float:
    size_id = str(size)
    if size_id not in _COMPLETION_SIZE_BONUSES:
        raise ValueError("size must be small, medium, or large")
    resolved = set(session.resolved_room_ids)
    bonus_rooms = [room for room in session.rooms if not room.critical_path]
    opened_bonus_rooms = sum(room.id in resolved for room in bonus_rooms)
    bonus_room_modifier = (
        _COMPLETION_BONUS_ROOM_CAP * opened_bonus_rooms / len(bonus_rooms)
        if bonus_rooms
        else 0.0
    )
    guardian_rooms = [room for room in session.rooms if room.family == "guardian"]
    level_modifier = 0.0
    if guardian_rooms:
        guardian_fraction = sum(
            room.id in resolved for room in guardian_rooms
        ) / len(guardian_rooms)
        level_modifier = (0.20 * guardian_fraction) - 0.10
    guide_penalty = (
        _COMPLETION_GUIDE_PENALTY
        if COMPLEXITIES_BY_LEVEL[session.complexity].forced_guide_mode
        else 0.0
    )
    return (
        _COMPLETION_SIZE_BONUSES[size_id]
        + bonus_room_modifier
        + level_modifier
        - guide_penalty
    )


def dungeon_session_as_dict_pure(session: DungeonSession) -> dict[str, Any]:
    return {
        "floor": session.floor,
        "complexity": session.complexity,
        "seed": session.seed,
        "rooms": [
            {
                "id": room.id,
                "family": room.family,
                "connected_room_ids": list(room.connected_room_ids),
                "critical_path": room.critical_path,
                "skill_door_id": room.skill_door_id,
                "required_level": room.required_level,
            }
            for room in session.rooms
        ],
        "resolved_room_ids": list(session.resolved_room_ids),
        "frontier_room_ids": list(session.frontier_room_ids),
        "current_room_id": session.current_room_id,
        "death_count": session.death_count,
        "completed": session.completed,
    }


def _session_from_storage_pure(
    raw: object,
    skill_levels: Mapping[str, object] | None = None,
) -> DungeonSession | None:
    if not isinstance(raw, Mapping):
        return None
    try:
        floor = _validate_floor(raw.get("floor"))
        complexity = int(raw.get("complexity"))
        seed = int(raw.get("seed"))
    except (TypeError, ValueError, OverflowError):
        return None
    if floor_theme_for_floor_pure(floor).id != "frozen" or complexity not in (1, 6):
        return None
    rooms = build_starter_floor_graph_pure(
        seed=seed,
        complexity=complexity,
        skill_levels=skill_levels,
    )
    valid_ids = {room.id for room in rooms}
    resolved = {0}
    for value in raw.get("resolved_room_ids", ()) or ():
        try:
            room_id = int(value)
        except (TypeError, ValueError, OverflowError):
            continue
        if room_id in valid_ids:
            resolved.add(room_id)
    frontier = {
        neighbor
        for room_id in resolved
        for neighbor in rooms[room_id].connected_room_ids
        if neighbor not in resolved
    }
    try:
        current = int(raw.get("current_room_id", 0))
    except (TypeError, ValueError, OverflowError):
        current = 0
    if current not in resolved:
        current = 0
    try:
        deaths = max(0, int(raw.get("death_count", 0)))
    except (TypeError, ValueError, OverflowError):
        deaths = 0
    boss_id = next(room.id for room in rooms if room.family == "boss")
    completed = boss_id in resolved
    return DungeonSession(
        floor=floor,
        complexity=complexity,
        seed=seed,
        rooms=rooms,
        resolved_room_ids=tuple(sorted(resolved)),
        frontier_room_ids=tuple(sorted(frontier)),
        current_room_id=current,
        death_count=deaths,
        completed=completed,
    )


def default_dungeoneering_state_pure() -> dict[str, Any]:
    return {
        "version": DUNGEONEERING_STATE_VERSION,
        "active": False,
        "floor": 1,
        "size": "small",
        "complexity": 1,
        "automation_mode": "casual",
        "resource_policy": "gather_and_process",
        "next_seed": 1,
        "selected_room_id": -1,
        "session": {},
        "entry_skill_levels": {},
        "session_inventory": {},
        "session_equipment": {},
        "session_coins": 0,
        "boss": {},
        "pending_bind_offer": {},
        "bound_items": [],
        "bind_loadouts": [[] for _ in range(BIND_LOADOUT_COUNT)],
        "active_bind_loadout": 0,
        "ammo_bind": {},
        "remembered_bind_choice": "skip",
        "kinship_active_class": KINSHIP_CLASSES[0].id,
        "kinship_tiers": {kinship_class.id: 0 for kinship_class in KINSHIP_CLASSES},
        "checked_floors": {theme.id: [] for theme in FLOOR_THEMES},
        "previous_progress": {theme.id: 0 for theme in FLOOR_THEMES},
        "tokens": 0,
        "tokens_earned": 0,
        "tokens_spent": 0,
        "coal_bag_owned": False,
        "coal_bag_coal": 0,
        "floors_completed": 0,
        "total_deaths": 0,
        "last_payout": {},
        "last_automation": "No in-floor automation has run yet.",
        "last_result": "Ready to enter a Frozen starter floor.",
    }


def _non_negative_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _sanitize_item_counts(raw: object) -> dict[str, int]:
    if not isinstance(raw, Mapping):
        return {}
    return {
        str(item_name)[:120]: amount
        for item_name, raw_amount in raw.items()
        if str(item_name)[:120]
        and (amount := _non_negative_int(raw_amount)) > 0
    }


def _sanitize_session_equipment(raw: object) -> dict[str, str]:
    if not isinstance(raw, Mapping):
        return {}
    return {
        str(slot)[:80]: str(item_name)[:120]
        for slot, item_name in raw.items()
        if str(slot)[:80] and str(item_name)[:120]
    }


def _sanitize_entry_skill_levels(raw: object) -> dict[str, int]:
    source = raw if isinstance(raw, Mapping) else {}
    return {
        door.skill_id: _clean_level(source.get(door.skill_id, 1))
        for door in FROZEN_SKILL_DOORS
    }


def _sanitize_bound_items(raw: object) -> list[dict[str, Any]]:
    bound = []
    seen = set()
    for record in raw if isinstance(raw, (list, tuple)) else ():
        if not isinstance(record, Mapping):
            continue
        item_name = str(record.get("item_name", ""))[:120]
        slot = str(record.get("slot", ""))[:80]
        if not item_name or not slot or item_name in seen:
            continue
        seen.add(item_name)
        bound.append({"item_name": item_name, "quantity": 1, "slot": slot})
        if len(bound) >= COLLECTED_BIND_LIMIT:
            break
    return bound


def _sanitize_bind_loadouts(
    raw: object,
    bound_items: list[dict[str, Any]],
) -> list[list[str]]:
    bound_names = {record["item_name"] for record in bound_items}
    has_stored_loadouts = isinstance(raw, (list, tuple))
    source = raw if has_stored_loadouts else ()
    loadouts: list[list[str]] = []
    maximum_active = BIND_SLOTS_BY_LEVEL[-1][1]
    for index in range(BIND_LOADOUT_COUNT):
        raw_loadout = source[index] if index < len(source) else ()
        names = []
        for value in raw_loadout if isinstance(raw_loadout, (list, tuple)) else ():
            item_name = str(value)[:120]
            if item_name in bound_names and item_name not in names:
                names.append(item_name)
            if len(names) >= maximum_active:
                break
        loadouts.append(names)
    if bound_items and not has_stored_loadouts:
        loadouts[0] = [
            record["item_name"] for record in bound_items[:maximum_active]
        ]
    return loadouts


def _sanitize_ammo_bind(raw: object) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    item_name = str(raw.get("item_name", ""))[:120]
    quantity = min(
        SALT_IN_THE_WOUND_AMMO_BIND_CAPACITY,
        _non_negative_int(raw.get("quantity")),
    )
    return {"item_name": item_name, "quantity": quantity} if item_name and quantity else {}


def _sanitize_kinship_tiers(raw: object) -> dict[str, int]:
    source = raw if isinstance(raw, Mapping) else {}
    return {
        kinship_class.id: min(10, _non_negative_int(source.get(kinship_class.id)))
        for kinship_class in KINSHIP_CLASSES
    }


def _sanitize_bind_offer(raw: object) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    item_name = str(raw.get("item_name", ""))[:120]
    quantity = _non_negative_int(raw.get("quantity"))
    kind = str(raw.get("kind", "ordinary"))
    slot = str(raw.get("slot", ""))[:80]
    if not item_name or quantity <= 0 or kind not in {"ordinary", "ammo"}:
        return {}
    if kind == "ordinary" and not slot:
        return {}
    return {
        "item_name": item_name,
        "quantity": quantity,
        "kind": kind,
        "slot": slot,
    }


def _bind_offer_backed_by_inventory_pure(
    raw_offer: object,
    inventory: Mapping[str, Any],
) -> dict[str, Any]:
    offer = _sanitize_bind_offer(raw_offer)
    if not offer:
        return {}
    available = _non_negative_int(inventory.get(offer["item_name"]))
    if available <= 0:
        return {}
    offer["quantity"] = min(offer["quantity"], available)
    return offer


def _sanitize_boss_state(
    raw: object,
    session: DungeonSession | None,
) -> dict[str, Any]:
    if session is None:
        return {}
    source = raw if isinstance(raw, Mapping) else {}
    boss_id = str(source.get("boss_id", ""))
    boss = FROZEN_BOSSES_BY_ID.get(boss_id)
    if boss is None or not (boss.first_floor <= session.floor <= boss.last_floor):
        boss = select_frozen_boss_pure(
            floor=session.floor,
            level=required_level_for_floor_pure(session.floor),
            seed=session.seed,
        )
        boss_id = boss.id
    ladder = FROZEN_BOSS_COMBAT_LEVEL_LADDERS[boss_id]
    combat_level = _non_negative_int(source.get("combat_level"), ladder[0])
    if combat_level not in ladder:
        combat_level = ladder[0]
    maximum = frozen_boss_enemy_pure(boss_id, combat_level)["stats"]["hitpoints"]
    lifepoints = min(maximum, max(1, _non_negative_int(source.get("lifepoints"), maximum)))
    encounter_source = source.get("encounter")
    encounter = (
        copy.deepcopy(dict(encounter_source))
        if isinstance(encounter_source, Mapping)
        else {}
    )
    encounter["target_id"] = DUNGEONEERING_COMBAT_TARGET_ID
    encounter["enemy_lifepoints"] = lifepoints
    return {
        "boss_id": boss_id,
        "combat_level": combat_level,
        "lifepoints": lifepoints,
        "encounter": encounter,
    }


def sanitize_dungeoneering_state_pure(raw: object) -> dict[str, Any]:
    defaults = default_dungeoneering_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    if mode not in {"casual", "advanced"}:
        mode = "casual"
    resource_policy = str(source.get("resource_policy", "gather_and_process"))
    if resource_policy not in _VALID_RESOURCE_POLICIES:
        resource_policy = "gather_and_process"
    floor = _non_negative_int(source.get("floor"), 1)
    if floor < 1 or floor > 11:
        floor = 1
    complexity = _non_negative_int(source.get("complexity"), 1)
    if complexity not in (1, 6):
        complexity = 1
    raw_checked = source.get("checked_floors")
    raw_previous = source.get("previous_progress")
    checked_floors: dict[str, list[int]] = {}
    previous_progress: dict[str, int] = {}
    for theme in FLOOR_THEMES:
        checked_source = (
            raw_checked.get(theme.id, ())
            if isinstance(raw_checked, Mapping)
            else ()
        )
        checked = []
        for value in checked_source or ():
            try:
                candidate = int(value)
            except (TypeError, ValueError, OverflowError):
                continue
            if theme.first_floor <= candidate <= theme.last_floor:
                checked.append(candidate)
        checked_floors[theme.id] = sorted(set(checked))
        previous_value = (
            raw_previous.get(theme.id, 0)
            if isinstance(raw_previous, Mapping)
            else 0
        )
        previous_progress[theme.id] = min(
            theme.last_floor - theme.first_floor + 1,
            _non_negative_int(previous_value),
        )
    entry_skill_levels = _sanitize_entry_skill_levels(source.get("entry_skill_levels"))
    session = _session_from_storage_pure(
        source.get("session"),
        entry_skill_levels,
    )
    active = bool(source.get("active", False)) and session is not None
    if session is not None and session.completed:
        active = False
    if not active:
        session = None
        entry_skill_levels = {}
    if session is not None:
        floor = session.floor
        complexity = session.complexity
    try:
        selected = int(source.get("selected_room_id", -1))
    except (TypeError, ValueError, OverflowError):
        selected = -1
    if selected not in (session.frontier_room_ids if session else ()):
        selected = -1
    last_payout_source = source.get("last_payout")
    last_payout = (
        {
            str(key): value
            for key, value in last_payout_source.items()
            if isinstance(key, str)
            and isinstance(value, (str, int, float, bool))
        }
        if isinstance(last_payout_source, Mapping)
        else {}
    )
    bound_items = _sanitize_bound_items(source.get("bound_items"))
    bind_loadouts = _sanitize_bind_loadouts(source.get("bind_loadouts"), bound_items)
    active_bind_loadout = min(
        BIND_LOADOUT_COUNT - 1,
        _non_negative_int(source.get("active_bind_loadout")),
    )
    ammo_bind = _sanitize_ammo_bind(source.get("ammo_bind"))
    remembered_choice = str(source.get("remembered_bind_choice", "skip"))
    if remembered_choice not in {"bind", "replace", "skip"}:
        remembered_choice = "skip"
    kinship_active_class = str(
        source.get("kinship_active_class", KINSHIP_CLASSES[0].id)
    )
    if kinship_active_class not in KINSHIP_CLASSES_BY_ID:
        kinship_active_class = KINSHIP_CLASSES[0].id
    kinship_tiers = _sanitize_kinship_tiers(source.get("kinship_tiers"))
    tokens = _non_negative_int(source.get("tokens"))
    tokens_spent = _non_negative_int(source.get("tokens_spent"))
    tokens_earned = max(
        _non_negative_int(source.get("tokens_earned")),
        tokens + tokens_spent,
    )
    coal_bag_owned = bool(source.get("coal_bag_owned", False))
    coal_bag_coal = (
        min(COAL_BAG_CAPACITY, _non_negative_int(source.get("coal_bag_coal")))
        if coal_bag_owned
        else 0
    )
    session_inventory = _sanitize_item_counts(source.get("session_inventory")) if active else {}
    session_equipment = _sanitize_session_equipment(source.get("session_equipment")) if active else {}
    session_coins = _non_negative_int(source.get("session_coins")) if active else 0
    pending_offer = (
        _bind_offer_backed_by_inventory_pure(
            source.get("pending_bind_offer"),
            session_inventory,
        )
        if active
        else {}
    )
    boss = _sanitize_boss_state(source.get("boss"), session)
    return {
        **defaults,
        "active": active,
        "floor": floor,
        "complexity": complexity,
        "automation_mode": mode,
        "resource_policy": resource_policy,
        "next_seed": max(1, _non_negative_int(source.get("next_seed"), 1)),
        "selected_room_id": selected,
        "session": dungeon_session_as_dict_pure(session) if session else {},
        "entry_skill_levels": entry_skill_levels,
        "session_inventory": session_inventory,
        "session_equipment": session_equipment,
        "session_coins": session_coins,
        "boss": boss,
        "pending_bind_offer": pending_offer,
        "bound_items": bound_items,
        "bind_loadouts": bind_loadouts,
        "active_bind_loadout": active_bind_loadout,
        "ammo_bind": ammo_bind,
        "remembered_bind_choice": remembered_choice,
        "kinship_active_class": kinship_active_class,
        "kinship_tiers": kinship_tiers,
        "checked_floors": checked_floors,
        "previous_progress": previous_progress,
        "tokens": tokens,
        "tokens_earned": tokens_earned,
        "tokens_spent": tokens_spent,
        "coal_bag_owned": coal_bag_owned,
        "coal_bag_coal": coal_bag_coal,
        "floors_completed": _non_negative_int(source.get("floors_completed")),
        "total_deaths": _non_negative_int(source.get("total_deaths")),
        "last_payout": last_payout,
        "last_automation": str(
            source.get("last_automation", defaults["last_automation"])
        )[:500],
        "last_result": str(source.get("last_result", defaults["last_result"]))[:500],
    }


def _player_requirement_level_pure(
    player_data: Mapping[str, Any],
    skill_name: str,
) -> int:
    return _clean_level(player_data.get(f"{skill_name.lower()}_level", 1))


def _carried_coal_for_current_smith_pure(player_data: Mapping[str, Any]) -> int:
    carried = player_data.get("carried_inventory")
    if not isinstance(carried, Mapping):
        return 0
    target = str(player_data.get("current_smith", ""))
    pack = carried.get(target)
    return (
        _non_negative_int(pack.get("Coal"))
        if isinstance(pack, Mapping)
        else 0
    )


def _kinship_effect_view_pure(state: Mapping[str, Any]) -> dict[str, Any]:
    class_id = str(state.get("kinship_active_class", KINSHIP_CLASSES[0].id))
    kinship_class = KINSHIP_CLASSES_BY_ID[class_id]
    tier = min(10, _non_negative_int((state.get("kinship_tiers") or {}).get(class_id)))
    percent = kinship_class.tier_values_percent[tier - 1] if tier else 0
    if class_id == "gatherer":
        application = (
            f"Live at {percent}%: a chance at one extra gathered resource and "
            f"{percent}% less failed skill-task damage."
            if tier
            else "Buy tier 1 to activate extra resources and failed-task damage reduction."
        )
    elif class_id == "artisan":
        application = (
            f"Live at {percent}%: a chance to save processing inputs and "
            f"{percent}% less failed skill-task damage."
            if tier
            else "Buy tier 1 to activate resource saves and failed-task damage reduction."
        )
    elif class_id == "medic":
        application = (
            "No solo-floor effect: the sourced perk heals another player, and the starter expedition is solo."
        )
    else:
        application = (
            "No automated-floor effect: this sourced combat perk depends on a per-hit stance or spell behavior "
            "that the starter floor does not expose, so no substitute bonus is invented."
        )
    return {
        "id": kinship_class.id,
        "display_name": kinship_class.display_name,
        "category": kinship_class.category,
        "tier": tier,
        "percent": percent,
        "source_effect": kinship_class.effect,
        "application": application,
    }


def _active_kinship_task_reduction_percent(state: Mapping[str, Any]) -> int:
    effect = _kinship_effect_view_pure(state)
    return (
        int(effect["percent"])
        if effect["id"] in {"gatherer", "artisan"}
        else 0
    )


def _casual_route_room_pure(session: DungeonSession) -> int | None:
    boss_id = next(room.id for room in session.rooms if room.family == "boss")

    def distance_to_boss(start: int) -> int:
        queue = deque([(start, 0)])
        seen = {start}
        while queue:
            room_id, distance = queue.popleft()
            if room_id == boss_id:
                return distance
            for neighbor in session.rooms[room_id].connected_room_ids:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, distance + 1))
        return len(session.rooms) + 1

    if not session.frontier_room_ids:
        return None
    return min(
        session.frontier_room_ids,
        key=lambda room_id: (distance_to_boss(room_id), room_id),
    )


def _completion_projection_pure(
    state: Mapping[str, Any],
    session: DungeonSession,
) -> tuple[CompletionPayout, FloorReplayResolution, int]:
    checked = set(state["checked_floors"]["frozen"])
    replay = resolve_floor_replay_pure(session.floor, checked)
    projected_checked = set(checked)
    if replay.credited_floor is not None:
        projected_checked.add(replay.credited_floor)
    current_progress = len(projected_checked)
    previous_progress = state["previous_progress"]["frozen"]
    prestige = prestige_value_pure(current_progress, previous_progress)
    opened_rooms = len(session.resolved_room_ids)
    active_floor_xp = starter_floor_xp_pure(
        floor=replay.xp_floor,
        size="small",
        opened_rooms=opened_rooms,
    )
    prestige_floor_xp = (
        starter_floor_xp_pure(
            floor=prestige,
            size="small",
            opened_rooms=opened_rooms,
        )
        if prestige > 0 and not replay.repeated_without_credit
        else 0
    )
    payout = calculate_completion_payout_pure(
        active_floor_xp=active_floor_xp,
        prestige_floor_xp=prestige_floor_xp,
        complexity=session.complexity,
        death_penalty=death_xp_penalty_pure(session.death_count),
        completion_modifier=starter_completion_modifier_pure(session),
    )
    return payout, replay, prestige


def _entry_skill_levels_pure(player_data: Mapping[str, Any]) -> dict[str, int]:
    return {
        door.skill_id: _clean_level(player_data.get(f"{door.skill_id}_level", 1))
        for door in FROZEN_SKILL_DOORS
    }


def _add_session_item(state: dict[str, Any], item_name: str, quantity: int) -> None:
    if quantity <= 0:
        return
    inventory = dict(state["session_inventory"])
    inventory[item_name] = _non_negative_int(inventory.get(item_name)) + quantity
    state["session_inventory"] = inventory


def _remove_session_item(state: dict[str, Any], item_name: str, quantity: int) -> bool:
    inventory = dict(state["session_inventory"])
    available = _non_negative_int(inventory.get(item_name))
    if quantity <= 0 or available < quantity:
        return False
    remaining = available - quantity
    if remaining:
        inventory[item_name] = remaining
    else:
        inventory.pop(item_name, None)
    state["session_inventory"] = inventory
    state["pending_bind_offer"] = _bind_offer_backed_by_inventory_pure(
        state.get("pending_bind_offer"),
        inventory,
    )
    if not remaining:
        state["session_equipment"] = {
            slot: equipped_name
            for slot, equipped_name in state["session_equipment"].items()
            if equipped_name != item_name
        }
    return True


def _initial_bound_floor_state_pure(
    state: Mapping[str, Any],
    player_data: Mapping[str, Any],
) -> tuple[dict[str, int], dict[str, str]]:
    inventory: dict[str, int] = {}
    equipment: dict[str, str] = {}
    active_slots = active_bind_slots_for_level_pure(
        player_data.get("dungeoneering_level", 1)
    )
    records_by_name = {
        str(record["item_name"]): record for record in state["bound_items"]
    }
    selected_names = state["bind_loadouts"][state["active_bind_loadout"]][
        :active_slots
    ]
    for item_name in selected_names:
        record = records_by_name[item_name]
        inventory[item_name] = inventory.get(item_name, 0) + 1
        slot = str(record["slot"])
        if slot not in equipment:
            equipment[slot] = item_name
    ammo = state["ammo_bind"]
    if ammo:
        capacity = ammo_bind_capacity_pure(
            salt_in_the_wound_complete=_quest_complete(
                player_data,
                "salt_in_the_wound",
            )
        )
        quantity = min(capacity, _non_negative_int(ammo.get("quantity")))
        if quantity:
            item_name = str(ammo["item_name"])
            inventory[item_name] = inventory.get(item_name, 0) + quantity
    return inventory, equipment


def _clear_floor_state_pure(state: dict[str, Any]) -> None:
    state["selected_room_id"] = -1
    state["session"] = {}
    state["entry_skill_levels"] = {}
    state["session_inventory"] = {}
    state["session_equipment"] = {}
    state["session_coins"] = 0
    state["boss"] = {}
    state["pending_bind_offer"] = {}


def record_dungeon_drop_pure(
    player_data: Mapping[str, Any],
    item_name: object,
    quantity: object = 1,
    *,
    equipment_slot: object = "",
    ammo: bool = False,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_dungeoneering_state_pure(data.get("dungeoneering"))
    if not state["active"]:
        return data, False, {"reason": "Enter a floor before recording an in-floor drop."}
    name = str(item_name)[:120]
    amount = _non_negative_int(quantity)
    slot = str(equipment_slot)[:80]
    if not name or amount <= 0:
        return data, False, {"reason": "The in-floor drop must have an item and quantity."}
    _add_session_item(state, name, amount)
    if slot:
        equipment = dict(state["session_equipment"])
        equipment[slot] = name
        state["session_equipment"] = equipment
    ordinary_eligible = slot and name not in {
        record["item_name"] for record in state["bound_items"]
    }
    if not state["pending_bind_offer"] and (ammo or ordinary_eligible):
        state["pending_bind_offer"] = {
            "item_name": name,
            "quantity": amount,
            "kind": "ammo" if ammo else "ordinary",
            "slot": "" if ammo else slot,
        }
    data["dungeoneering"] = state
    return data, True, {
        "item_name": name,
        "quantity": amount,
        "bind_offer": bool(state["pending_bind_offer"]),
    }


def _destroy_bound_floor_item(state: dict[str, Any], record: Mapping[str, Any]) -> None:
    item_name = str(record.get("item_name", ""))
    _remove_session_item(state, item_name, _non_negative_int(record.get("quantity"), 1))
    equipment = dict(state["session_equipment"])
    for slot, equipped_name in tuple(equipment.items()):
        if equipped_name == item_name:
            equipment.pop(slot, None)
    state["session_equipment"] = equipment


def _resolve_bind_offer_pure(
    player_data: Mapping[str, Any],
    state: dict[str, Any],
    choice: str,
) -> tuple[bool, str]:
    offer = state["pending_bind_offer"]
    if not offer:
        return False, "No eligible in-floor drop is waiting for a bind choice."
    if choice not in {"bind", "replace", "skip"}:
        return False, "Choose Bind, Replace, or Skip."
    if choice == "skip":
        state["pending_bind_offer"] = {}
        state["remembered_bind_choice"] = choice
        return True, f"Skipped binding {offer['item_name']}."

    if offer["kind"] == "ammo":
        current = state["ammo_bind"]
        if choice == "bind" and current:
            return False, "The separate ammo bind is full; choose Replace or Skip."
        if choice == "replace" and not current:
            return False, "There is no ammo bind to replace."
        if current:
            _destroy_bound_floor_item(state, current)
        capacity = ammo_bind_capacity_pure(
            salt_in_the_wound_complete=_quest_complete(
                player_data,
                "salt_in_the_wound",
            )
        )
        quantity = min(capacity, _non_negative_int(offer["quantity"]))
        state["ammo_bind"] = {
            "item_name": offer["item_name"],
            "quantity": quantity,
        }
    else:
        bound = list(state["bound_items"])
        bound_names = {record["item_name"] for record in bound}
        if offer["item_name"] in bound_names:
            return False, f"{offer['item_name']} is already in the bind collection."
        if choice == "bind" and len(bound) >= COLLECTED_BIND_LIMIT:
            return False, "The ten-item bind collection is full; choose Replace or Skip."
        if choice == "replace" and not bound:
            return False, "There is no ordinary bind to replace."
        loadouts = [list(loadout) for loadout in state["bind_loadouts"]]
        active_index = state["active_bind_loadout"]
        active_loadout = loadouts[active_index]
        if choice == "replace":
            replaced_name = active_loadout[0] if active_loadout else bound[0]["item_name"]
            replaced_index = next(
                index
                for index, record in enumerate(bound)
                if record["item_name"] == replaced_name
            )
            _destroy_bound_floor_item(state, bound.pop(replaced_index))
            loadouts = [
                [item_name for item_name in loadout if item_name != replaced_name]
                for loadout in loadouts
            ]
            active_loadout = loadouts[active_index]
        record = {
            "item_name": offer["item_name"],
            "quantity": 1,
            "slot": offer["slot"],
        }
        bound.append(record)
        slots = active_bind_slots_for_level_pure(
            player_data.get("dungeoneering_level", 1)
        )
        if len(active_loadout) < slots:
            active_loadout.append(offer["item_name"])
        loadouts[active_index] = active_loadout
        state["bound_items"] = bound
        state["bind_loadouts"] = loadouts
        equipment = dict(state["session_equipment"])
        equipment[offer["slot"]] = offer["item_name"]
        state["session_equipment"] = equipment
    state["pending_bind_offer"] = {}
    state["remembered_bind_choice"] = choice
    verb = "Replaced the active bind with" if choice == "replace" else "Bound"
    return True, f"{verb} {offer['item_name']}."


def _smuggler_stock_pure(complexity: int) -> tuple[Any, ...]:
    band = SMUGGLER_STOCK_BANDS[complexity]
    return tuple(
        SMUGGLER_ITEMS_BY_ID[item_id]
        for item_id in band.item_ids
    )


def _smuggler_reachable_coins_pure(
    state: Mapping[str, Any],
    session: DungeonSession | None,
) -> int:
    bound_names = {record["item_name"] for record in state["bound_items"]}
    if state["ammo_bind"]:
        bound_names.add(state["ammo_bind"]["item_name"])
    reachable = _non_negative_int(state["session_coins"])
    for item in SMUGGLER_ITEMS_BY_ID.values():
        if item.item_name in bound_names:
            continue
        quantity = _non_negative_int(
            state["session_inventory"].get(item.item_name)
        )
        reachable += quantity * math.floor(
            item.buy_price * SMUGGLER_SELLBACK_RATE
        )
    if session is not None:
        resolved = set(session.resolved_room_ids)
        remaining_resources = sum(
            room.family == "resource" and room.id not in resolved
            for room in session.rooms
        )
        raw_crab = SMUGGLER_ITEMS_BY_ID["raw_heim_crab"]
        reachable += remaining_resources * math.floor(
            raw_crab.buy_price * SMUGGLER_SELLBACK_RATE
        )
    return reachable


def _smuggler_buy_pure(
    state: dict[str, Any],
    item_id: str,
) -> tuple[bool, str, Any | None]:
    item = SMUGGLER_ITEMS_BY_ID.get(item_id)
    band = SMUGGLER_STOCK_BANDS[state["complexity"]]
    if item is None or item.id not in band.item_ids:
        return False, "That item is not in the current Smuggler stock band.", None
    if state["session_coins"] < item.buy_price:
        return False, f"Need {item.buy_price:,} session coins for {item.item_name}.", None
    state["session_coins"] -= item.buy_price
    return True, f"Bought {item.item_name} for {item.buy_price:,} session coins.", item


def _smuggler_sell_pure(state: dict[str, Any], item_id: str) -> tuple[bool, str]:
    item = SMUGGLER_ITEMS_BY_ID.get(item_id)
    if item is None:
        return False, "The Smuggler has no registered price for that floor item."
    if _non_negative_int(state["session_inventory"].get(item.item_name)) <= 0:
        return False, f"No {item.item_name} is in the session inventory."
    bound_names = {record["item_name"] for record in state["bound_items"]}
    if state["ammo_bind"]:
        bound_names.add(state["ammo_bind"]["item_name"])
    if item.item_name in bound_names:
        return False, "Bound items cannot be sold to the Smuggler."
    if not _remove_session_item(state, item.item_name, 1):
        return False, f"No {item.item_name} is in the session inventory."
    value = math.floor(item.buy_price * SMUGGLER_SELLBACK_RATE)
    state["session_coins"] += value
    return True, f"Sold {item.item_name} for {value:,} session coins."


def _award_chain_xp(
    rewards: dict[str, float],
    skill_id: str,
    amount: float,
) -> None:
    if amount > 0:
        rewards[skill_id] = rewards.get(skill_id, 0.0) + amount


def _run_chain_step_pure(
    state: dict[str, Any],
    player_data: Mapping[str, Any],
    step: Any,
) -> bool:
    skill_id = step.skill.lower()
    if state["complexity"] < step.minimum_complexity:
        return False
    if _clean_level(player_data.get(f"{skill_id}_level", 1)) < step.level:
        return False
    inventory = state["session_inventory"]
    if any(_non_negative_int(inventory.get(name)) < quantity for name, quantity in step.inputs):
        return False
    for name, quantity in step.inputs:
        _remove_session_item(state, name, quantity)
    _add_session_item(state, step.output[0], step.output[1])
    return True


def _kinship_resource_roll_succeeds_pure(
    state: Mapping[str, Any],
    class_id: str,
    rng: Callable[[], float] | None,
) -> bool:
    effect = _kinship_effect_view_pure(state)
    return (
        effect["id"] == class_id
        and int(effect["percent"]) > 0
        and _roll(rng) < int(effect["percent"]) / 100.0
    )


def _restore_chain_inputs_pure(state: dict[str, Any], step: Any) -> None:
    for item_name, quantity in step.inputs:
        _add_session_item(state, item_name, quantity)


def _guardian_coin_drop_pure(session: DungeonSession, room: DungeonRoom) -> int:
    critical_guardian_ids = tuple(
        candidate.id
        for candidate in session.rooms
        if candidate.family == "guardian" and candidate.critical_path
    )
    share, remainder = divmod(
        _STARTER_GUARDIAN_COIN_DROPS,
        len(critical_guardian_ids),
    )
    if room.id not in critical_guardian_ids:
        return share
    return share + (critical_guardian_ids.index(room.id) < remainder)


def _automate_herblore_chain_pure(
    state: dict[str, Any],
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None,
) -> tuple[dict[str, float], tuple[str, ...]]:
    if state["complexity"] < 5 or not _quest_complete(player_data, "druidic_ritual"):
        return {}, ()
    rewards: dict[str, float] = {}
    reports: list[str] = []
    if (
        _non_negative_int(state["session_inventory"].get("Vial")) > 0
        and _non_negative_int(state["session_inventory"].get("Vial of water")) == 0
    ):
        _remove_session_item(state, "Vial", 1)
        _add_session_item(state, "Vial of water", 1)
        reports.append("filled a Vial")
    for step in STARTER_HERBLORE_CHAIN:
        if _run_chain_step_pure(state, player_data, step):
            _award_chain_xp(rewards, "herblore", step.xp)
            reports.append(step.display_name.lower())
            if step.inputs and _kinship_resource_roll_succeeds_pure(
                state, "artisan", rng
            ):
                _restore_chain_inputs_pure(state, step)
                reports.append(f"Artisan saved inputs for {step.display_name.lower()}")
    return rewards, tuple(reports)


def _automate_resource_room_pure(
    state: dict[str, Any],
    player_data: Mapping[str, Any],
    session: DungeonSession,
    rng: Callable[[], float] | None,
) -> tuple[dict[str, float], tuple[str, ...]]:
    policy = state["resource_policy"]
    if policy == "skip":
        return {}, ("Resource automation skipped by policy",)
    rewards: dict[str, float] = {}
    reports: list[str] = []
    caught = STARTER_RESOURCE_CHAIN[0]
    if _run_chain_step_pure(state, player_data, caught):
        _award_chain_xp(rewards, "fishing", caught.xp)
        reports.append("caught Raw heim crab")
        if _kinship_resource_roll_succeeds_pure(state, "gatherer", rng):
            _add_session_item(state, caught.output[0], caught.output[1])
            reports.append("Gatherer found one extra Raw heim crab")
    first_resource_room = not any(
        session.rooms[room_id].family == "resource"
        for room_id in session.resolved_room_ids
    )
    if first_resource_room and state["complexity"] >= 5:
        herb_name, herb_quantity = STARTER_HERBLORE_CHAIN[0].inputs[0]
        _add_session_item(state, herb_name, herb_quantity)
        reports.append(f"gathered {herb_name}")
    if policy == "gather_and_process":
        cooked = STARTER_RESOURCE_CHAIN[1]
        if _run_chain_step_pure(state, player_data, cooked):
            _award_chain_xp(rewards, "cooking", cooked.xp)
            reports.append("cooked Heim crab")
            if _kinship_resource_roll_succeeds_pure(state, "artisan", rng):
                _restore_chain_inputs_pure(state, cooked)
                reports.append("Artisan saved the Raw heim crab")
    return rewards, tuple(reports)


def dungeoneering_view_pure(
    player_data: Mapping[str, Any],
    *,
    selected_skill: object = "",
) -> dict[str, Any]:
    state = sanitize_dungeoneering_state_pure(player_data.get("dungeoneering"))
    session = _session_from_storage_pure(state["session"], state["entry_skill_levels"])
    level = _clean_level(player_data.get("dungeoneering_level", 1))
    maximum_floor = min(11, maximum_floor_for_level_pure(level))
    active_session = player_data.get("activity_session")
    active_session_id = (
        str(active_session.get("active_id", ""))
        if isinstance(active_session, Mapping)
        else ""
    )
    selected_for_reviews = str(selected_skill) == "Dungeoneering"
    frontier_rows = ()
    projection = None
    if session is not None:
        casual_room_id = _casual_route_room_pure(session)
        frontier_rows = tuple(
            {
                "room_id": room_id,
                "family": session.rooms[room_id].family,
                "label": (
                    f"Door {room_id + 1} · "
                    + (
                        FROZEN_SKILL_DOORS_BY_ID[session.rooms[room_id].skill_door_id].display_name
                        if session.rooms[room_id].family == "skill"
                        else FROZEN_BOSSES_BY_ID[state["boss"]["boss_id"]].display_name
                        if session.rooms[room_id].family == "boss" and state["boss"]
                        else session.rooms[room_id].family.title()
                    )
                ),
                "selected": room_id == state["selected_room_id"],
                "casual_recommended": room_id == casual_room_id,
            }
            for room_id in session.frontier_room_ids
        )
        projection = _completion_projection_pure(state, session)[0]
    active = bool(state["active"] and session is not None)
    advanced = state["automation_mode"] == "advanced"
    route_selected = bool(
        session is not None and state["selected_room_id"] in session.frontier_room_ids
    )
    session_selected = active_session_id == DUNGEONEERING_ACTIVITY_ID
    can_review = (
        active
        and session_selected
        and selected_for_reviews
        and not state["pending_bind_offer"]
        and (not advanced or route_selected)
    )
    competing_session = bool(
        active_session_id and active_session_id != DUNGEONEERING_ACTIVITY_ID
    )
    pending_offer = state["pending_bind_offer"]
    bind_slots = active_bind_slots_for_level_pure(level)
    active_loadout = state["bind_loadouts"][state["active_bind_loadout"]][:bind_slots]
    smuggler_band = SMUGGLER_STOCK_BANDS[state["complexity"]]
    bound_names = {record["item_name"] for record in state["bound_items"]}
    if state["ammo_bind"]:
        bound_names.add(state["ammo_bind"]["item_name"])
    smuggler_reachable_coins = _smuggler_reachable_coins_pure(state, session)
    smuggler_rows = tuple(
        {
            "item_id": item.id,
            "item_name": item.item_name,
            "buy_price": item.buy_price,
            "sell_price": math.floor(item.buy_price * SMUGGLER_SELLBACK_RATE),
            "owned": _non_negative_int(state["session_inventory"].get(item.item_name)),
            "can_buy": active and state["session_coins"] >= item.buy_price,
            "can_sell": (
                active
                and item.item_name not in bound_names
                and _non_negative_int(state["session_inventory"].get(item.item_name)) > 0
            ),
        }
        for item in _smuggler_stock_pure(state["complexity"])
        if item.buy_price <= smuggler_reachable_coins
        or _non_negative_int(state["session_inventory"].get(item.item_name)) > 0
    )
    boss_state = state["boss"]
    boss_label = ""
    if boss_state:
        boss = FROZEN_BOSSES_BY_ID[boss_state["boss_id"]]
        maximum = frozen_boss_enemy_pure(
            boss.id,
            boss_state["combat_level"],
        )["stats"]["hitpoints"]
        boss_label = (
            f"{boss.display_name} · level {boss_state['combat_level']} · "
            f"{boss_state['lifepoints']:,}/{maximum:,} LP"
        )
    kinship_effect = _kinship_effect_view_pure(state)
    kinship_rows = []
    for kinship_class in KINSHIP_CLASSES:
        tier = state["kinship_tiers"][kinship_class.id]
        next_cost = KINSHIP_TIER_COSTS[tier] if tier < 10 else 0
        kinship_rows.append(
            {
                "class_id": kinship_class.id,
                "display_name": kinship_class.display_name,
                "category": kinship_class.category,
                "tier": tier,
                "next_tier": tier + 1 if tier < 10 else 10,
                "next_cost": next_cost,
                "source_effect": kinship_class.effect,
                "selected": kinship_class.id == state["kinship_active_class"],
                "can_upgrade": (
                    not active
                    and tier < 10
                    and state["tokens"] >= next_cost
                ),
            }
        )
    reward_rows = []
    for reward in DUNGEONEERING_REWARDS:
        locked_reasons = []
        if level < reward.dungeoneering_level:
            locked_reasons.append(f"Dungeoneering {reward.dungeoneering_level}")
        for skill_name, required_level in reward.other_skill_requirements:
            if _player_requirement_level_pure(player_data, skill_name) < required_level:
                locked_reasons.append(f"{skill_name} {required_level}")
        owned = reward.id == "coal_bag" and state["coal_bag_owned"]
        if not reward.fully_functional:
            status_text = "Catalogued — not purchasable yet"
        elif owned:
            status_text = "Owned"
        elif locked_reasons:
            status_text = "Requires " + ", ".join(locked_reasons)
        elif state["tokens"] < reward.token_cost:
            status_text = f"Need {reward.token_cost - state['tokens']:,} more tokens"
        elif active:
            status_text = "Leave the floor to purchase"
        else:
            status_text = "Available"
        reward_rows.append(
            {
                "reward_id": reward.id,
                "display_name": reward.display_name,
                "token_cost": reward.token_cost,
                "dungeoneering_level": reward.dungeoneering_level,
                "other_skill_requirements": reward.other_skill_requirements,
                "requirements_text": (
                    "No level requirement"
                    if reward.dungeoneering_level <= 0 and not reward.other_skill_requirements
                    else ", ".join(
                        ([f"Dungeoneering {reward.dungeoneering_level}"] if reward.dungeoneering_level > 0 else [])
                        + [f"{skill_name} {required_level}" for skill_name, required_level in reward.other_skill_requirements]
                    )
                ),
                "fully_functional": reward.fully_functional,
                "owned": owned,
                "locked_reasons": tuple(locked_reasons),
                "status_text": status_text,
                "can_purchase": (
                    reward.fully_functional
                    and not owned
                    and not locked_reasons
                    and not active
                    and state["tokens"] >= reward.token_cost
                ),
                "notes": reward.notes,
            }
        )
    total_coal = _non_negative_int((player_data.get("inventory") or {}).get("Coal"))
    carried_coal = min(total_coal, _carried_coal_for_current_smith_pure(player_data))
    bank_coal = max(0, total_coal - carried_coal)
    coal_space = COAL_BAG_CAPACITY - state["coal_bag_coal"]
    return {
        **state,
        "theme": "frozen",
        "theme_label": FLOOR_THEMES_BY_ID["frozen"].display_name,
        "size_label": FLOOR_SIZES_BY_ID["small"].display_name,
        "floor_options": tuple(range(1, maximum_floor + 1)),
        "complexity_options": (1, 6),
        "resource_policy_options": (
            ("gather_and_process", "Gather + process"),
            ("gather_only", "Gather only"),
            ("skip", "Skip resources"),
        ),
        "frontier_rows": frontier_rows,
        "session_inventory_rows": tuple(sorted(state["session_inventory"].items())),
        "session_equipment_rows": tuple(sorted(state["session_equipment"].items())),
        "bound_rows": tuple(state["bound_items"]),
        "active_bound_rows": tuple(
            record
            for item_name in active_loadout
            for record in state["bound_items"]
            if record["item_name"] == item_name
        ),
        "bind_loadout_options": tuple(range(BIND_LOADOUT_COUNT)),
        "bind_loadout_control_enabled": not active,
        "kinship_rows": tuple(kinship_rows),
        "kinship_effect": kinship_effect,
        "kinship_control_enabled": not active,
        "phase_c_entry_controls_visible": not active,
        "kinship_upgrade_enabled": bool(
            next(
                row["can_upgrade"]
                for row in kinship_rows
                if row["selected"]
            )
        ),
        "reward_rows": tuple(reward_rows),
        "reward_catalog_count": len(reward_rows),
        "reward_purchase_count": sum(row["can_purchase"] for row in reward_rows),
        "reward_trader_enabled": not active,
        "token_balance": state["tokens"],
        "token_earned": state["tokens_earned"],
        "token_spent": state["tokens_spent"],
        "coal_bag_capacity": COAL_BAG_CAPACITY,
        "coal_bag_bank_coal": bank_coal,
        "coal_bag_carried_coal": carried_coal,
        "coal_bag_space": coal_space,
        "coal_bag_can_fill_bank": bool(
            state["coal_bag_owned"] and coal_space > 0 and bank_coal > 0
        ),
        "coal_bag_can_fill_carried": bool(
            state["coal_bag_owned"] and coal_space > 0 and carried_coal > 0
        ),
        "coal_bag_controls_visible": bool(
            state["coal_bag_owned"] and not active
        ),
        "collected_bind_limit": COLLECTED_BIND_LIMIT,
        "bind_slots": bind_slots,
        "bind_slots_used": len(active_loadout),
        "ammo_bind_capacity": ammo_bind_capacity_pure(
            salt_in_the_wound_complete=_quest_complete(player_data, "salt_in_the_wound")
        ),
        "bind_offer_visible": active and bool(pending_offer),
        "bind_offer_label": (
            f"{pending_offer.get('item_name', '')} ×{pending_offer.get('quantity', 0)}"
            if pending_offer
            else ""
        ),
        "bind_can_bind": bool(
            pending_offer
            and (
                not state["ammo_bind"]
                if pending_offer.get("kind") == "ammo"
                else len(state["bound_items"]) < COLLECTED_BIND_LIMIT
            )
        ),
        "bind_can_replace": bool(
            pending_offer
            and (
                state["ammo_bind"]
                if pending_offer.get("kind") == "ammo"
                else state["bound_items"]
            )
        ),
        "smuggler_open": active and smuggler_band.source_row_count > 0,
        "smuggler_source_row_count": smuggler_band.source_row_count,
        "smuggler_reachable_coins": smuggler_reachable_coins,
        "smuggler_rows": smuggler_rows,
        "boss_label": boss_label,
        "eat_threshold_percent": max(
            1,
            min(_non_negative_int(player_data.get("combat_auto_eat_threshold_percent"), 40), 99),
        ),
        "resolved_rooms": len(session.resolved_room_ids) if session else 0,
        "room_budget": len(session.rooms) if session else STARTER_SMALL_GRAPH_ROOM_COUNT,
        "deaths": session.death_count if session else 0,
        "projected_xp": projection.final_xp if projection else 0.0,
        "projected_tokens": projection.tokens if projection else 0,
        "projection_disclosure": (
            "Projection uses registered placeholder payout coefficients and changes with rooms and deaths."
        ),
        "selected_for_reviews": selected_for_reviews,
        "session_selected": session_selected,
        "can_review": can_review,
        "can_enter": not competing_session,
        "can_abandon": active,
        "entry_controls_enabled": not active,
        "policy_control_enabled": True,
        "resource_policy_control_enabled": True,
        "smuggler_controls_enabled": active and smuggler_band.source_row_count > 0,
        "route_choice_visible": active and advanced,
        "route_choice_enabled": (
            active and session_selected and advanced and bool(frontier_rows)
        ),
        "projection_visible": active,
        "primary_text": (
            "Floor active"
            if active and session_selected
            else "Resume floor"
            if active
            else "Enter floor"
        ),
        "primary_enabled": (
            not competing_session and not (active and session_selected)
        ),
        "abandon_visible": active,
        "abandon_enabled": active,
        "status_label": "CHOICE" if pending_offer else "ACTIVE" if active else "READY",
    }


def apply_dungeoneering_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_dungeoneering_state_pure(data.get("dungeoneering"))
    data["dungeoneering"] = state
    payload = payload if isinstance(payload, Mapping) else {}
    active_session = data.get("activity_session")
    active_session_id = (
        str(active_session.get("active_id", ""))
        if isinstance(active_session, Mapping)
        else ""
    )

    if action_id == "select_kinship_class":
        if state["active"]:
            return data, False, {"reason": "Choose a Ring of Kinship class between floors."}
        class_id = str(payload.get("class_id", ""))
        kinship_class = KINSHIP_CLASSES_BY_ID.get(class_id)
        if kinship_class is None:
            return data, False, {"reason": "Choose one of the twelve Ring of Kinship classes."}
        state["kinship_active_class"] = class_id
        state["last_result"] = f"Ring of Kinship set to {kinship_class.display_name}."
        data["dungeoneering"] = state
        return data, True, {"message": state["last_result"]}

    if action_id == "upgrade_kinship_class":
        if state["active"]:
            return data, False, {"reason": "Upgrade Ring of Kinship classes between floors."}
        class_id = str(payload.get("class_id", state["kinship_active_class"]))
        kinship_class = KINSHIP_CLASSES_BY_ID.get(class_id)
        if kinship_class is None:
            return data, False, {"reason": "Choose one of the twelve Ring of Kinship classes."}
        tier = state["kinship_tiers"][class_id]
        if tier >= 10:
            return data, False, {"reason": f"{kinship_class.display_name} is already tier 10."}
        cost = KINSHIP_TIER_COSTS[tier]
        if state["tokens"] < cost:
            return data, False, {"reason": f"Need {cost:,} tokens for {kinship_class.display_name} tier {tier + 1}."}
        state["tokens"] -= cost
        state["tokens_spent"] += cost
        state["kinship_tiers"][class_id] = tier + 1
        state["last_result"] = (
            f"Upgraded {kinship_class.display_name} to tier {tier + 1} for {cost:,} tokens."
        )
        data["dungeoneering"] = state
        return data, True, {"message": state["last_result"], "tokens_spent": cost}

    if action_id == "purchase_reward":
        if state["active"]:
            return data, False, {"reason": "Leave the floor before using the reward trader."}
        reward_id = str(payload.get("reward_id", ""))
        reward = DUNGEONEERING_REWARDS_BY_ID.get(reward_id)
        if reward is None:
            return data, False, {"reason": "Unknown Dungeoneering reward."}
        if not reward.fully_functional:
            return data, False, {"reason": f"{reward.display_name} is catalogued but not purchasable yet."}
        if reward.id == "coal_bag" and state["coal_bag_owned"]:
            return data, False, {"reason": "Only one Coal bag may be owned."}
        if _clean_level(data.get("dungeoneering_level", 1)) < reward.dungeoneering_level:
            return data, False, {"reason": f"Need Dungeoneering {reward.dungeoneering_level} for {reward.display_name}."}
        for skill_name, required_level in reward.other_skill_requirements:
            if _player_requirement_level_pure(data, skill_name) < required_level:
                return data, False, {"reason": f"Need {skill_name} {required_level} for {reward.display_name}."}
        if state["tokens"] < reward.token_cost:
            return data, False, {"reason": f"Need {reward.token_cost:,} tokens for {reward.display_name}."}
        state["tokens"] -= reward.token_cost
        state["tokens_spent"] += reward.token_cost
        if reward.id == "coal_bag":
            state["coal_bag_owned"] = True
            state["coal_bag_coal"] = 0
        state["last_result"] = f"Bought {reward.display_name} for {reward.token_cost:,} tokens."
        data["dungeoneering"] = state
        return data, True, {"message": state["last_result"], "tokens_spent": reward.token_cost}

    if action_id == "fill_coal_bag":
        if not state["coal_bag_owned"]:
            return data, False, {"reason": "Buy the Coal bag before filling it."}
        space = COAL_BAG_CAPACITY - state["coal_bag_coal"]
        if space <= 0:
            return data, False, {"reason": "The Coal bag already holds 27 Coal."}
        source_id = str(payload.get("source", "bank"))
        inventory = dict(data.get("inventory") or {})
        total_coal = _non_negative_int(inventory.get("Coal"))
        carried_root = dict(data.get("carried_inventory") or {})
        target_id = str(data.get("current_smith", ""))
        carried_pack = dict(carried_root.get(target_id) or {})
        carried_coal = min(total_coal, _non_negative_int(carried_pack.get("Coal")))
        available = carried_coal if source_id == "carried" else max(0, total_coal - carried_coal)
        if source_id not in {"bank", "carried"}:
            return data, False, {"reason": "Fill the Coal bag from Bank or carried Coal."}
        amount = min(space, available)
        if amount <= 0:
            source_label = "carried pack" if source_id == "carried" else "Bank"
            return data, False, {"reason": f"No Coal is available in the {source_label}."}
        remaining_total = total_coal - amount
        if remaining_total:
            inventory["Coal"] = remaining_total
        else:
            inventory.pop("Coal", None)
        if source_id == "carried":
            remaining_carried = carried_coal - amount
            if remaining_carried:
                carried_pack["Coal"] = remaining_carried
            else:
                carried_pack.pop("Coal", None)
            if carried_pack:
                carried_root[target_id] = carried_pack
            else:
                carried_root.pop(target_id, None)
        for carried_target, raw_pack in tuple(carried_root.items()):
            pack = dict(raw_pack) if isinstance(raw_pack, Mapping) else {}
            if "Coal" in pack:
                clamped = min(remaining_total, _non_negative_int(pack.get("Coal")))
                if clamped:
                    pack["Coal"] = clamped
                else:
                    pack.pop("Coal", None)
                if pack:
                    carried_root[str(carried_target)] = pack
                else:
                    carried_root.pop(carried_target, None)
        state["coal_bag_coal"] += amount
        state["last_result"] = (
            f"Filled the Coal bag with {amount} Coal from "
            f"{'the carried pack' if source_id == 'carried' else 'Bank'} "
            f"({state['coal_bag_coal']}/{COAL_BAG_CAPACITY})."
        )
        data["inventory"] = inventory
        data["carried_inventory"] = carried_root
        data["dungeoneering"] = state
        return data, True, {"message": state["last_result"], "coal_added": amount}

    if action_id == "enter":
        if active_session_id not in {"", DUNGEONEERING_ACTIVITY_ID}:
            return data, False, {"reason": "Another persistent activity is active."}
        if state["active"]:
            data["activity_session"] = {"active_id": DUNGEONEERING_ACTIVITY_ID}
            return data, True, {"message": f"Resumed Frozen floor {state['floor']}."}
        floor = payload.get("floor", state["floor"])
        complexity = payload.get("complexity", state["complexity"])
        mode = str(payload.get("automation_mode", state["automation_mode"]))
        if mode not in {"casual", "advanced"}:
            return data, False, {"reason": "Unknown Dungeoneering route policy."}
        if str(payload.get("size", "small")) != "small":
            return data, False, {"reason": "The starter expedition uses Small floors."}
        entry_skill_levels = _entry_skill_levels_pure(data)
        try:
            session = begin_starter_session_pure(
                floor=floor,
                dungeoneering_level=data.get("dungeoneering_level", 1),
                complexity=complexity,
                seed=state["next_seed"],
                skill_levels=entry_skill_levels,
            )
            boss = select_frozen_boss_pure(
                floor=session.floor,
                level=data.get("dungeoneering_level", 1),
                seed=session.seed,
            )
            boss_level = frozen_boss_combat_level_pure(boss.id, data)
        except ValueError as exc:
            return data, False, {"reason": str(exc)}
        session_inventory, session_equipment = _initial_bound_floor_state_pure(
            state,
            data,
        )
        boss_enemy = frozen_boss_enemy_pure(boss.id, boss_level)
        boss_lifepoints = boss_enemy["stats"]["hitpoints"]
        kinship_effect = _kinship_effect_view_pure(state)
        state.update(
            {
                "active": True,
                "floor": session.floor,
                "size": "small",
                "complexity": session.complexity,
                "automation_mode": mode,
                "next_seed": state["next_seed"] + 1,
                "selected_room_id": -1,
                "session": dungeon_session_as_dict_pure(session),
                "entry_skill_levels": entry_skill_levels,
                "session_inventory": session_inventory,
                "session_equipment": session_equipment,
                "session_coins": 0,
                "pending_bind_offer": {},
                "boss": {
                    "boss_id": boss.id,
                    "combat_level": boss_level,
                    "lifepoints": boss_lifepoints,
                    "encounter": {
                        "target_id": DUNGEONEERING_COMBAT_TARGET_ID,
                        "enemy_lifepoints": boss_lifepoints,
                    },
                },
                "last_automation": "No in-floor automation has run on this floor yet.",
                "last_result": f"Entered Frozen floor {session.floor}; the first frontier is revealed.",
            }
        )
        data["dungeoneering"] = state
        data["activity_session"] = {"active_id": DUNGEONEERING_ACTIVITY_ID}
        return data, True, {"message": state["last_result"]}

    if action_id == "abandon":
        if not state["active"]:
            return data, False, {"reason": "No Dungeoneering floor is active."}
        state["active"] = False
        _clear_floor_state_pure(state)
        state["last_result"] = "Abandoned the floor; session items evaporated and no completion XP or tokens were awarded."
        data["dungeoneering"] = state
        if active_session_id == DUNGEONEERING_ACTIVITY_ID:
            data["activity_session"] = {"active_id": ""}
        return data, True, {"message": state["last_result"]}

    if action_id == "set_policy":
        mode = str(payload.get("automation_mode", ""))
        if mode not in {"casual", "advanced"}:
            return data, False, {"reason": "Unknown Dungeoneering route policy."}
        state["automation_mode"] = mode
        state["selected_room_id"] = -1
        data["dungeoneering"] = state
        return data, True, {"message": f"Dungeoneering route policy set to {mode}."}

    if action_id == "set_resource_policy":
        policy = str(payload.get("resource_policy", ""))
        if policy not in _VALID_RESOURCE_POLICIES:
            return data, False, {"reason": "Unknown Dungeoneering resource policy."}
        state["resource_policy"] = policy
        data["dungeoneering"] = state
        return data, True, {"message": f"Dungeoneering resource policy set to {policy.replace('_', ' ')}."}

    if action_id in {"select_bind_loadout", "set_bind_loadout"}:
        if state["active"]:
            return data, False, {"reason": "Bind loadouts can only be changed between floors."}
        try:
            loadout_index = int(payload.get("loadout_index"))
        except (TypeError, ValueError, OverflowError):
            loadout_index = -1
        if loadout_index not in range(BIND_LOADOUT_COUNT):
            return data, False, {"reason": "Choose bind loadout 1, 2, or 3."}
        if action_id == "set_bind_loadout":
            raw_names = payload.get("item_names")
            if not isinstance(raw_names, (list, tuple)):
                return data, False, {"reason": "Choose the collected items for this loadout."}
            collected_names = {
                record["item_name"] for record in state["bound_items"]
            }
            item_names = []
            for value in raw_names:
                item_name = str(value)[:120]
                if item_name not in collected_names:
                    return data, False, {"reason": f"{item_name} is not in the bind collection."}
                if item_name not in item_names:
                    item_names.append(item_name)
            slots = active_bind_slots_for_level_pure(
                data.get("dungeoneering_level", 1)
            )
            if len(item_names) > slots:
                return data, False, {"reason": f"This level supports {slots} active bind slots."}
            loadouts = [list(loadout) for loadout in state["bind_loadouts"]]
            loadouts[loadout_index] = item_names
            state["bind_loadouts"] = loadouts
        state["active_bind_loadout"] = loadout_index
        data["dungeoneering"] = state
        return data, True, {"message": f"Bind loadout {loadout_index + 1} selected."}

    if action_id == "resolve_bind_offer":
        if not state["active"]:
            return data, False, {"reason": "Enter a floor before resolving a bind offer."}
        ok, message = _resolve_bind_offer_pure(
            data,
            state,
            str(payload.get("choice", "")),
        )
        if not ok:
            return data, False, {"reason": message}
        data["dungeoneering"] = state
        return data, True, {"message": message}

    if action_id in {"smuggler_buy", "smuggler_sell"}:
        if not state["active"]:
            return data, False, {"reason": "Enter a floor before using the Smuggler."}
        if SMUGGLER_STOCK_BANDS[state["complexity"]].source_row_count <= 0:
            return data, False, {"reason": "The Smuggler shop is closed at Complexity 1."}
        item_id = str(payload.get("item_id", ""))
        if action_id == "smuggler_buy":
            ok, message, item = _smuggler_buy_pure(state, item_id)
            if not ok or item is None:
                return data, False, {"reason": message}
            data["dungeoneering"] = state
            data, recorded, _drop = record_dungeon_drop_pure(
                data,
                item.item_name,
                equipment_slot=item.equipment_slot,
                ammo=item.ammo_bind,
            )
            if not recorded:
                return data, False, {"reason": "The purchased floor item could not be stored."}
            return data, True, {"message": message}
        ok, message = _smuggler_sell_pure(state, item_id)
        if not ok:
            return data, False, {"reason": message}
        data["dungeoneering"] = state
        return data, True, {"message": message}

    if action_id == "select_route":
        session = _session_from_storage_pure(state["session"], state["entry_skill_levels"])
        if not state["active"] or session is None:
            return data, False, {"reason": "Enter a floor before choosing a door."}
        if state["automation_mode"] != "advanced":
            return data, False, {"reason": "Switch to Advanced before choosing a door."}
        try:
            room_id = int(payload.get("room_id"))
        except (TypeError, ValueError, OverflowError):
            room_id = -1
        if room_id not in session.frontier_room_ids:
            return data, False, {"reason": "That door is not on the revealed frontier."}
        state["selected_room_id"] = room_id
        data["dungeoneering"] = state
        return data, True, {"message": f"Selected door {room_id + 1}."}

    return data, False, {"reason": "Unknown Dungeoneering command."}


def _auto_eat_heim_crab_pure(
    data: dict[str, Any],
    state: dict[str, Any],
) -> int:
    available = _non_negative_int(state["session_inventory"].get("Heim crab"))
    if available <= 0:
        return 0
    maximum = combat_max_lifepoints_pure(data)
    current = min(maximum, _non_negative_int(data.get("combat_lifepoints"), maximum))
    threshold = max(
        1,
        min(_non_negative_int(data.get("combat_auto_eat_threshold_percent"), 40), 99),
    )
    if current * 100 > maximum * threshold:
        return 0
    if not _remove_session_item(state, "Heim crab", 1):
        return 0
    healed = min(20, maximum - current)
    data["combat_lifepoints"] = current + healed
    return healed


def _skill_door_review_pure(
    data: dict[str, Any],
    state: dict[str, Any],
    session: DungeonSession,
    room: DungeonRoom,
    rng: Callable[[], float] | None,
) -> tuple[DungeonSession, bool, dict[str, Any]]:
    door = FROZEN_SKILL_DOORS_BY_ID[room.skill_door_id]
    level = _clean_level(data.get(f"{door.skill_id}_level", 1))
    if level < room.required_level:
        return session, False, {
            "reason": f"{door.display_name} requires {door.skill_id.title()} {room.required_level}."
        }
    if _roll(rng) >= SKILL_DOOR_FAILURE_CHANCE:
        xp = room.required_level * 5
        return session, True, {
            "skill_door": door.id,
            "skill_door_failed": False,
            "xp_rewards": {door.skill_id: float(xp)},
            "automation": f"opened {door.display_name} for {xp} {door.skill_id.title()} XP",
        }

    base_damage = room.required_level * SKILL_DOOR_FAILURE_DAMAGE_MULTIPLIER
    reduction_percent = _active_kinship_task_reduction_percent(state)
    damage = (
        max(1, math.floor(base_damage * (100 - reduction_percent) / 100))
        if base_damage > 0
        else 0
    )
    ring_report = (
        f"; Ring reduced the failed-task damage from {base_damage} to {damage}"
        if reduction_percent and damage < base_damage
        else ""
    )
    current = _non_negative_int(
        data.get("combat_lifepoints"),
        combat_max_lifepoints_pure(data),
    )
    data["combat_lifepoints"] = max(0, current - damage)
    died = data["combat_lifepoints"] <= 0
    if died:
        session = record_starter_death_pure(session)
        data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
        state["total_deaths"] += 1
    healed = 0 if died else _auto_eat_heim_crab_pure(data, state)
    return session, False, {
        "skill_door": door.id,
        "skill_door_failed": True,
        "damage": damage,
        "death": died,
        "healed": healed,
        "status": (
            f"Failed {door.display_name} for {damage} true damage{ring_report}; respawned at the floor start."
            if died
            else f"Failed {door.display_name} for {damage} true damage{ring_report}"
            + (f"; auto-ate Heim crab for {healed} LP." if healed else ".")
        ),
    }


def _restore_outside_value(
    data: dict[str, Any],
    source: Mapping[str, Any],
    key: str,
) -> None:
    if key in source:
        data[key] = copy.deepcopy(source[key])
    else:
        data.pop(key, None)


def _boss_review_pure(
    player_data: Mapping[str, Any],
    state: dict[str, Any],
    session: DungeonSession,
    rng: Callable[[], float] | None,
    equipment_data: Mapping[str, Any],
) -> tuple[dict[str, Any], DungeonSession, bool, dict[str, Any]]:
    data = dict(player_data)
    boss_state = state["boss"]
    enemy = frozen_boss_enemy_pure(
        boss_state["boss_id"],
        boss_state["combat_level"],
    )
    healed = _auto_eat_heim_crab_pure(data, state)
    combat_input = dict(data)
    combat_input["inventory"] = dict(state["session_inventory"])
    combat_input["equipment"] = dict(state["session_equipment"])
    combat_input["current_combat_target"] = DUNGEONEERING_COMBAT_TARGET_ID
    combat_input["combat_encounter"] = copy.deepcopy(boss_state["encounter"])
    combat_input["combat_auto_flee"] = False
    combat_input["combat_auto_eat_food"] = []
    combat_input["combat_supply_loadout"] = {}
    combat_input["carried_inventory"] = {}
    combat_data, ok, combat_result = apply_combat_burst_pure(
        combat_input,
        {DUNGEONEERING_COMBAT_TARGET_ID: enemy},
        equipment_data,
        ticks=DUNGEONEERING_COMBAT_TICKS_PER_REVIEW,
        rng=rng or (lambda: 0.5),
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=True,
        allow_bank_run=False,
    )
    if not ok:
        return dict(player_data), session, False, dict(combat_result)

    state["session_inventory"] = _sanitize_item_counts(combat_data.get("inventory"))
    state["session_equipment"] = _sanitize_session_equipment(combat_data.get("equipment"))
    encounter = combat_data.get("combat_encounter")
    lifepoints = _non_negative_int(combat_result.get("enemy_lifepoints"))
    if not combat_result.get("killed"):
        lifepoints = max(1, lifepoints or boss_state["lifepoints"])
        state["boss"] = {
            **boss_state,
            "lifepoints": lifepoints,
            "encounter": (
                copy.deepcopy(dict(encounter))
                if isinstance(encounter, Mapping)
                else {
                    "target_id": DUNGEONEERING_COMBAT_TARGET_ID,
                    "enemy_lifepoints": lifepoints,
                }
            ),
        }
    else:
        state["boss"] = {**boss_state, "lifepoints": 0, "encounter": {}}

    for key in (
        "inventory",
        "equipment",
        "current_combat_target",
        "combat_encounter",
        "combat_auto_flee",
        "combat_auto_eat_food",
        "combat_supply_loadout",
        "carried_inventory",
    ):
        _restore_outside_value(combat_data, player_data, key)

    killed = bool(combat_result.get("killed"))
    if combat_result.get("died"):
        session = record_starter_death_pure(session)
        combat_data["combat_lifepoints"] = combat_max_lifepoints_pure(combat_data)
        state["total_deaths"] += 1
        status = (
            f"Defeated {enemy['display_name']} but also fell; the floor completion counts the death."
            if killed
            else f"Defeated by {enemy['display_name']}; respawned at the floor start with "
            f"the boss at {state['boss']['lifepoints']:,} LP."
        )
        return combat_data, session, killed, {
            **combat_result,
            "xp_rewards": {},
            "death": True,
            "boss_killed": killed,
            "healed": healed,
            "combat_xp_rewards": dict(combat_result.get("xp_rewards", {}) or {}),
            "status": status,
        }

    status = (
        f"Defeated {enemy['display_name']}."
        if killed
        else f"{enemy['display_name']} has {state['boss']['lifepoints']:,} LP remaining."
    )
    if healed:
        status += f" Auto-ate Heim crab for {healed} LP."
    return combat_data, session, killed, {
        **combat_result,
        "xp_rewards": {},
        "boss_killed": killed,
        "healed": healed,
        "combat_xp_rewards": dict(combat_result.get("xp_rewards", {}) or {}),
        "status": status,
    }


def apply_dungeoneering_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    equipment_data: Mapping[str, Any] | None = None,
    player_died: bool = False,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_dungeoneering_state_pure(data.get("dungeoneering"))
    session = _session_from_storage_pure(state["session"], state["entry_skill_levels"])
    active_session = data.get("activity_session")
    active_session_id = (
        str(active_session.get("active_id", ""))
        if isinstance(active_session, Mapping)
        else ""
    )
    if not state["active"] or session is None:
        return data, False, {"reason": "Enter a Dungeoneering floor before training it."}
    if active_session_id != DUNGEONEERING_ACTIVITY_ID:
        return data, False, {"reason": "Resume this floor on the Dungeoneering surface first."}
    if state["pending_bind_offer"]:
        return data, False, {"reason": "Resolve the Bind / Replace / Skip offer first."}

    if player_died:
        session = record_starter_death_pure(session)
        data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
        state["session"] = dungeon_session_as_dict_pure(session)
        state["selected_room_id"] = -1
        state["total_deaths"] += 1
        state["last_result"] = (
            f"Defeated on floor {session.floor}; respawned at the start with "
            f"{session.death_count} death{'s' if session.death_count != 1 else ''}."
        )
        data["dungeoneering"] = state
        return data, True, {
            "death": True,
            "status": state["last_result"],
            "room_resolved": False,
        }

    if state["automation_mode"] == "advanced":
        room_id = state["selected_room_id"]
        if room_id not in session.frontier_room_ids:
            return data, False, {"reason": "Choose one of the revealed frontier doors."}
    else:
        room_id = _casual_route_room_pure(session)
        if room_id is None:
            return data, False, {"reason": "No revealed route remains."}
    room = session.rooms[room_id]
    xp_rewards: dict[str, float] = {}
    automation_reports: list[str] = []
    combat_info: dict[str, Any] = {}

    if room.family == "skill":
        session, door_opened, door_info = _skill_door_review_pure(
            data,
            state,
            session,
            room,
            rng,
        )
        if not door_opened:
            state["session"] = dungeon_session_as_dict_pure(session)
            state["selected_room_id"] = -1
            state["last_automation"] = str(door_info.get("status", "Skill door attempt failed."))
            state["last_result"] = state["last_automation"]
            data["dungeoneering"] = state
            return data, True, {
                **door_info,
                "room_id": room_id,
                "room_family": room.family,
                "room_resolved": False,
                "complete": False,
            }
        xp_rewards.update(door_info.get("xp_rewards", {}))
        automation_reports.append(str(door_info["automation"]))

    if room.family == "boss":
        data, session, boss_killed, combat_info = _boss_review_pure(
            data,
            state,
            session,
            rng,
            equipment_data or {},
        )
        if not boss_killed:
            state["session"] = dungeon_session_as_dict_pure(session)
            state["selected_room_id"] = -1
            state["last_automation"] = str(combat_info.get("status", "Boss encounter advanced."))
            state["last_result"] = state["last_automation"]
            data["dungeoneering"] = state
            return data, True, {
                **combat_info,
                "room_id": room_id,
                "room_family": room.family,
                "room_resolved": False,
                "complete": False,
            }
        automation_reports.append(str(combat_info.get("status", "Boss defeated.")))

    resolved = resolve_starter_room_pure(session, room_id)
    state["selected_room_id"] = -1
    if room.family == "guardian":
        coin_drop = _guardian_coin_drop_pure(session, room)
        state["session_coins"] += coin_drop
        automation_reports.append(f"guardian enemies dropped {coin_drop:,} Rusty coins")
    if room.family == "resource":
        chain_xp, chain_reports = _automate_resource_room_pure(
            state,
            data,
            session,
            rng,
        )
        for skill_id, amount in chain_xp.items():
            _award_chain_xp(xp_rewards, skill_id, amount)
        automation_reports.extend(chain_reports)
    if state["resource_policy"] == "gather_and_process" and any(
        resolved.rooms[resolved_room_id].family == "resource"
        for resolved_room_id in resolved.resolved_room_ids
    ):
        chain_xp, chain_reports = _automate_herblore_chain_pure(state, data, rng)
        for skill_id, amount in chain_xp.items():
            _award_chain_xp(xp_rewards, skill_id, amount)
        automation_reports.extend(chain_reports)
    state["session"] = dungeon_session_as_dict_pure(resolved)
    if automation_reports:
        state["last_automation"] = "; ".join(automation_reports)[:500]

    if not resolved.completed:
        status = (
            f"Resolved {room.family} room {room_id + 1}; "
            f"{len(resolved.frontier_room_ids)} frontier doors are revealed."
        )
        if automation_reports:
            status += " Automation: " + "; ".join(automation_reports) + "."
        state["last_result"] = status[:500]
        data["dungeoneering"] = state
        result = {
            "room_id": room_id,
            "room_family": room.family,
            "room_resolved": True,
            "complete": False,
            "status": state["last_result"],
        }
        if xp_rewards:
            result["xp_rewards"] = xp_rewards
        if combat_info:
            result["combat_xp_rewards"] = combat_info.get("combat_xp_rewards", {})
        return data, True, result

    payout, replay, prestige = _completion_projection_pure(state, resolved)
    checked = set(state["checked_floors"]["frozen"])
    if replay.credited_floor is not None:
        checked.add(replay.credited_floor)
    accessible = set(
        range(
            FLOOR_THEMES_BY_ID["frozen"].first_floor,
            min(
                FLOOR_THEMES_BY_ID["frozen"].last_floor,
                maximum_floor_for_level_pure(data.get("dungeoneering_level", 1)),
            )
            + 1,
        )
    )
    prestige_reset = bool(accessible and accessible.issubset(checked))
    if prestige_reset:
        state["previous_progress"]["frozen"] = max(
            state["previous_progress"]["frozen"],
            len(checked),
        )
        checked.clear()
    state["checked_floors"]["frozen"] = sorted(checked)
    state["tokens"] += payout.tokens
    state["tokens_earned"] += payout.tokens
    state["floors_completed"] += 1
    state["active"] = False
    state["last_payout"] = {
        "floor": resolved.floor,
        "credited_floor": replay.credited_floor or 0,
        "prestige": prestige,
        "xp": payout.final_xp,
        "tokens": payout.tokens,
        "deaths": resolved.death_count,
        "prestige_reset": prestige_reset,
    }
    xp_rewards["dungeoneering"] = payout.final_xp
    state["last_result"] = (
        f"Completed Frozen floor {resolved.floor} · +{payout.final_xp:,.1f} "
        f"Dungeoneering XP · +{payout.tokens:,} tokens · session items evaporated."
    )
    _clear_floor_state_pure(state)
    data["dungeoneering"] = state
    data["activity_session"] = {"active_id": ""}
    return data, True, {
        **combat_info,
        "room_id": room_id,
        "room_family": room.family,
        "room_resolved": True,
        "complete": True,
        "status": state["last_result"],
        "xp_rewards": xp_rewards,
        "combat_xp_rewards": combat_info.get("combat_xp_rewards", {}),
        "tokens": payout.tokens,
        "payout": state["last_payout"],
    }
