"""Pure Shattered Heart collection, museum, and replica mechanics."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.shattered_heart_data import (
    SHATTERED_HEART_BAG_ITEM,
    SHATTERED_HEART_ELIGIBLE_SKILLS,
    SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS,
    SHATTERED_HEART_KUDOS_REWARD,
    SHATTERED_HEART_PLINTH_ITEM,
    SHATTERED_HEART_REPLICA_PIECE_LIMIT,
    SHATTERED_HEART_ROCK_CHANCE,
    SHATTERED_HEART_ROCK_ITEMS,
    SHATTERED_HEART_SOURCE,
    SHATTERED_HEART_SECOND_ROCK_MODIFIER,
    SHATTERED_HEART_SKILLS,
    SHATTERED_HEART_SKILLS_BY_ID,
)
from .pace.world_clock import world_day_index_pure


SHATTERED_HEART_STATE_VERSION = 1
_KNOWN_ROCK_ITEMS = set(SHATTERED_HEART_ROCK_ITEMS)
_KNOWN_SKILLS = set(SHATTERED_HEART_ELIGIBLE_SKILLS)
_OUTPUT_REPLACEMENT_ITEMS: frozenset[str] | None = None


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _inventory(player_data: Mapping[str, Any]) -> Mapping[str, Any]:
    inventory = player_data.get("inventory")
    return inventory if isinstance(inventory, Mapping) else {}


def _known_unique(raw: Any, known: set[str]) -> list[str]:
    if not isinstance(raw, (list, tuple, set, frozenset)):
        return []
    return [value for value in dict.fromkeys(str(item) for item in raw) if value in known]


def default_shattered_heart_state_pure() -> dict[str, Any]:
    return {
        "version": SHATTERED_HEART_STATE_VERSION,
        "auto_discard": False,
        "bag_rocks": [],
        "placed_pairs": [],
        "last_rock_skill": "",
        "statues_completed": 0,
        "completion_day": -SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS,
        "replica_pieces_awarded": 0,
        "replica_pairs_added": [],
        "replica_plinth_built": False,
        "last_result": "",
    }


def sanitize_shattered_heart_state_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    statues_completed = _int(source.get("statues_completed"))
    replica_pieces_awarded = min(
        SHATTERED_HEART_REPLICA_PIECE_LIMIT,
        _int(source.get("replica_pieces_awarded")),
    )
    replica_pairs_added = _known_unique(
        source.get("replica_pairs_added"), _KNOWN_SKILLS
    )[: replica_pieces_awarded // 2]
    last_skill = str(source.get("last_rock_skill", ""))
    completion_day = max(
        -SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS,
        _int(
            source.get(
                "completion_day",
                -SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS,
            ),
            -SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS,
            minimum=-SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS,
        ),
    )
    if statues_completed == 0:
        completion_day = -SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS
    return {
        "version": SHATTERED_HEART_STATE_VERSION,
        "auto_discard": bool(source.get("auto_discard", False)),
        "bag_rocks": _known_unique(source.get("bag_rocks"), _KNOWN_ROCK_ITEMS),
        # A fifteenth pair is never persisted: its placement explodes the statue
        # atomically and starts the next one.
        "placed_pairs": _known_unique(source.get("placed_pairs"), _KNOWN_SKILLS)[:14],
        "last_rock_skill": last_skill if last_skill in _KNOWN_SKILLS else "",
        "statues_completed": statues_completed,
        "completion_day": completion_day,
        "replica_pieces_awarded": replica_pieces_awarded,
        "replica_pairs_added": replica_pairs_added,
        "replica_plinth_built": bool(source.get("replica_plinth_built", False)),
        "last_result": str(source.get("last_result", ""))[:500],
    }


def _bag_carried(player_data: Mapping[str, Any]) -> bool:
    return _int(_inventory(player_data).get(SHATTERED_HEART_BAG_ITEM)) > 0


def _piece_owned(
    inventory: Mapping[str, Any], bag_rocks: set[str], item_name: str
) -> bool:
    return _int(inventory.get(item_name)) > 0 or item_name in bag_rocks


def _skill_rock_count(
    inventory: Mapping[str, Any], bag_rocks: set[str], skill_id: str
) -> int:
    return sum(
        _piece_owned(inventory, bag_rocks, item_name)
        for item_name in SHATTERED_HEART_SKILLS_BY_ID[skill_id].rock_items
    )


def _complete_pair_ids(
    inventory: Mapping[str, Any], bag_rocks: set[str]
) -> tuple[str, ...]:
    return tuple(
        row.id
        for row in SHATTERED_HEART_SKILLS
        if _skill_rock_count(inventory, bag_rocks, row.id) == 2
    )


def _final_pair_ready(state: Mapping[str, Any], current_day: int) -> bool:
    return _int(state.get("statues_completed")) == 0 or current_day >= (
        _int(
            state.get("completion_day"),
            -SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS,
            minimum=-SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS,
        )
        + SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS
    )


def _addable_pair_ids(
    state: Mapping[str, Any], complete_pair_ids: tuple[str, ...], current_day: int
) -> tuple[str, ...]:
    available = set(complete_pair_ids)
    placed = set(str(value) for value in state.get("placed_pairs", ()))
    final_ready = _final_pair_ready(state, current_day)
    addable: list[str] = []
    while True:
        skill_id = next(
            (
                row.id
                for row in SHATTERED_HEART_SKILLS
                if row.id in available and row.id not in placed
            ),
            "",
        )
        if not skill_id or (len(placed) == 14 and not final_ready):
            break
        available.remove(skill_id)
        placed.add(skill_id)
        addable.append(skill_id)
        if len(placed) == len(SHATTERED_HEART_SKILLS):
            placed.clear()
            final_ready = False
    return tuple(addable)


def _replica_pair_ids(
    inventory: Mapping[str, Any], already_added: set[str]
) -> tuple[str, ...]:
    return tuple(
        row.id
        for row in SHATTERED_HEART_SKILLS
        if row.id not in already_added
        and all(_int(inventory.get(item_name)) > 0 for item_name in row.replica_items)
    )


def shattered_heart_pair_xp_pure(level: Any) -> float:
    base_level = min(99, _int(level, 1, minimum=1))
    return float(base_level * base_level - 2 * base_level + 100)


def shattered_heart_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_shattered_heart_state_pure(player_data.get("shattered_heart"))
    inventory = _inventory(player_data)
    bag_rocks = set(state["bag_rocks"])
    complete_pairs = _complete_pair_ids(inventory, bag_rocks)
    current_day = world_day_index_pure(player_data)
    addable_pairs = _addable_pair_ids(state, complete_pairs, current_day)
    placed_count = len(state["placed_pairs"])
    final_ready = _final_pair_ready(state, current_day)
    final_blocked = bool(
        placed_count == 14
        and any(skill_id not in state["placed_pairs"] for skill_id in complete_pairs)
        and not final_ready
    )
    ready_day = state["completion_day"] + SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS
    days_remaining = max(0, ready_day - current_day) if state["statues_completed"] else 0

    has_bag = _bag_carried(player_data)
    loose_rocks = sum(_int(inventory.get(item_name)) for item_name in SHATTERED_HEART_ROCK_ITEMS)
    replica_added = set(state["replica_pairs_added"])
    replica_pairs_ready = _replica_pair_ids(inventory, replica_added)
    rooms = player_data.get("house_rooms_bought")
    has_study = bool(
        player_data.get("house_owned")
        and isinstance(rooms, Mapping)
        and rooms.get("study")
    )
    has_plinth_item = _int(inventory.get(SHATTERED_HEART_PLINTH_ITEM)) > 0
    replica_complete = len(replica_added) == len(SHATTERED_HEART_SKILLS)

    status_label = (
        "Auto-discarding"
        if state["auto_discard"]
        else "Bag carried"
        if has_bag
        else "Collecting loose rocks"
    )
    summary_text = (
        f"{placed_count}/15 museum pairs placed · {len(complete_pairs)} complete "
        f"pair{'s' if len(complete_pairs) != 1 else ''} ready · "
        f"{loose_rocks} loose, {len(bag_rocks)} bagged rocks · "
        f"{state['statues_completed']} statue completions"
    )
    if final_blocked:
        weekly_gate_text = (
            f"The final pair unlocks on world day {ready_day} "
            f"({days_remaining} day{'s' if days_remaining != 1 else ''} remaining)."
        )
    else:
        weekly_gate_text = "The final pair is ready."

    return {
        **state,
        "bag_carried": has_bag,
        "loose_rock_count": loose_rocks,
        "bag_rock_count": len(bag_rocks),
        "complete_pair_ids": complete_pairs,
        "addable_pair_ids": addable_pairs,
        "current_day": current_day,
        "final_pair_ready": final_ready,
        "final_pair_blocked": final_blocked,
        "ready_day": ready_day,
        "days_remaining": days_remaining,
        "replica_pair_ids_ready": replica_pairs_ready,
        "has_study": has_study,
        "has_plinth_item": has_plinth_item,
        "status_label": status_label,
        "summary_text": summary_text,
        "progress_max": len(SHATTERED_HEART_SKILLS),
        "progress_value": placed_count,
        "progress_format": f"{placed_count}/15 museum pairs",
        "weekly_gate_text": weekly_gate_text,
        "weekly_gate_visible": final_blocked,
        "claim_bag_visible": not has_bag,
        "claim_bag_enabled": not has_bag,
        "destroy_bag_visible": has_bag,
        "destroy_bag_enabled": has_bag,
        "add_pairs_label": f"Add all completed pairs ({len(addable_pairs)})",
        "add_pairs_enabled": bool(addable_pairs),
        "auto_discard_enabled": True,
        "replica_progress_max": SHATTERED_HEART_REPLICA_PIECE_LIMIT,
        "replica_progress_value": len(replica_added) * 2,
        "replica_progress_format": f"{len(replica_added) * 2}/30 replica pieces",
        "build_plinth_visible": bool(
            state["statues_completed"] and not state["replica_plinth_built"]
        ),
        "build_plinth_enabled": bool(
            state["statues_completed"]
            and not state["replica_plinth_built"]
            and has_study
            and has_plinth_item
        ),
        "add_replica_visible": bool(
            state["replica_plinth_built"] and not replica_complete
        ),
        "add_replica_enabled": bool(
            state["replica_plinth_built"] and replica_pairs_ready
        ),
        "source": SHATTERED_HEART_SOURCE,
    }


def _rng_value(rng) -> float:
    try:
        value = float(rng())
    except (TypeError, ValueError, OverflowError):
        return 1.0
    if value != value:
        return 1.0
    return max(0.0, min(1.0, value))


def _output_replacement_items() -> frozenset[str]:
    global _OUTPUT_REPLACEMENT_ITEMS
    if _OUTPUT_REPLACEMENT_ITEMS is None:
        from ..core.constants import ITEM_DEFINITIONS

        _OUTPUT_REPLACEMENT_ITEMS = frozenset(
            item.storage_key for item in ITEM_DEFINITIONS if item.tradeable
        )
    return _OUTPUT_REPLACEMENT_ITEMS


def apply_shattered_heart_skilling_hook_pure(
    player_data: Mapping[str, Any],
    skill_id: str,
    rng,
    output_items: Mapping[str, int] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Roll strange rocks after one successful eligible skilling action.

    ``output_items`` names quantities produced by this action and already
    present in inventory. The shared item registry decides which tradeable
    outputs may be replaced; a carried bag leaves every ordinary output intact.
    """

    data = dict(player_data)
    state = sanitize_shattered_heart_state_pure(data.get("shattered_heart"))
    data["shattered_heart"] = state
    skill_id = str(skill_id)
    if skill_id not in SHATTERED_HEART_SKILLS_BY_ID:
        return data, False, {"reason": "Skill is not eligible for strange rocks."}
    if state["auto_discard"]:
        return data, False, {"reason": "Strange-rock collection is disabled."}

    inventory = dict(_inventory(data))
    bag_rocks = set(state["bag_rocks"])
    row = SHATTERED_HEART_SKILLS_BY_ID[skill_id]
    if _skill_rock_count(inventory, bag_rocks, skill_id) >= 2:
        return data, False, {"reason": "Both strange rocks for this skill are held."}

    outputs = {
        item_name: _int(quantity)
        for item_name, quantity in (
            output_items.items() if isinstance(output_items, Mapping) else ()
        )
        if isinstance(item_name, str)
        and item_name in _output_replacement_items()
        and _int(quantity) > 0
    }
    bag_carried = _bag_carried(data)
    awarded: list[str] = []
    replaced: dict[str, int] = {}
    chances: list[float] = []

    owned_count = _skill_rock_count(inventory, bag_rocks, skill_id)
    while owned_count < 2:
        chance = SHATTERED_HEART_ROCK_CHANCE
        if owned_count == 1 and state["last_rock_skill"] == skill_id:
            chance *= SHATTERED_HEART_SECOND_ROCK_MODIFIER
        chances.append(chance)
        if _rng_value(rng) >= chance:
            break
        item_name = next(
            name
            for name in row.rock_items
            if not _piece_owned(inventory, bag_rocks, name)
        )
        if bag_carried:
            bag_rocks.add(item_name)
        else:
            inventory[item_name] = _int(inventory.get(item_name)) + 1
            replacement = next(
                (
                    output_name
                    for output_name, remaining in outputs.items()
                    if remaining > 0 and _int(inventory.get(output_name)) > 0
                ),
                "",
            )
            if replacement:
                inventory[replacement] = _int(inventory.get(replacement)) - 1
                outputs[replacement] -= 1
                replaced[replacement] = replaced.get(replacement, 0) + 1
        awarded.append(item_name)
        owned_count += 1
        state["last_rock_skill"] = skill_id

    if not awarded:
        return data, False, {
            "reason": "No strange rock was found.",
            "skill_id": skill_id,
            "chances": tuple(chances),
        }

    data["inventory"] = inventory
    state["bag_rocks"] = [
        item_name for item_name in SHATTERED_HEART_ROCK_ITEMS if item_name in bag_rocks
    ]
    state["last_result"] = (
        f"Found {len(awarded)} {row.display_name} strange "
        f"rock{'s' if len(awarded) != 1 else ''}."
    )
    data["shattered_heart"] = state
    return data, True, {
        "skill_id": skill_id,
        "rocks": tuple(awarded),
        "route": "bag" if bag_carried else "loose",
        "replaced_outputs": replaced,
        "chances": tuple(chances),
        "message": state["last_result"],
    }


def _consume_piece(
    inventory: dict[str, Any], bag_rocks: set[str], item_name: str
) -> None:
    if _int(inventory.get(item_name)) > 0:
        inventory[item_name] = _int(inventory.get(item_name)) - 1
    else:
        bag_rocks.discard(item_name)


def apply_shattered_heart_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Apply one atomic Shattered Heart command.

    Pair XP is returned in ``info['skill_xp']`` for the runtime award seam. This pure
    command deliberately never writes skill experience fields itself.
    """

    data = dict(player_data)
    state = sanitize_shattered_heart_state_pure(data.get("shattered_heart"))
    data["shattered_heart"] = state
    inventory = dict(_inventory(data))
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "claim_bag":
        if _int(inventory.get(SHATTERED_HEART_BAG_ITEM)) > 0:
            return data, False, {"reason": "The statue collection bag is already carried."}
        inventory[SHATTERED_HEART_BAG_ITEM] = 1
        data["inventory"] = inventory
        state["last_result"] = "Claimed a statue collection bag."
        return data, True, {"message": state["last_result"]}

    if action_id == "destroy_bag":
        if _int(inventory.get(SHATTERED_HEART_BAG_ITEM)) <= 0:
            return data, False, {"reason": "No statue collection bag is carried."}
        discarded = len(state["bag_rocks"])
        inventory[SHATTERED_HEART_BAG_ITEM] = 0
        data["inventory"] = inventory
        state["bag_rocks"] = []
        state["last_result"] = (
            f"Destroyed the statue collection bag and {discarded} stored "
            f"rock{'s' if discarded != 1 else ''}."
        )
        return data, True, {
            "discarded_rocks": discarded,
            "message": state["last_result"],
        }

    if action_id == "set_auto_discard":
        state["auto_discard"] = bool(payload.get("enabled", False))
        state["last_result"] = (
            "Future strange rocks will be discarded."
            if state["auto_discard"]
            else "Strange-rock collection resumed."
        )
        return data, True, {
            "enabled": state["auto_discard"],
            "message": state["last_result"],
        }

    if action_id == "build_replica_plinth":
        view = shattered_heart_view_pure(data)
        if state["replica_plinth_built"]:
            return data, False, {"reason": "The replica plinth is already built."}
        if not state["statues_completed"]:
            return data, False, {"reason": "Complete the museum statue first."}
        if not view["has_study"]:
            return data, False, {"reason": "An owned Study is required."}
        if not view["has_plinth_item"]:
            return data, False, {"reason": "A Statue plinth item is required."}
        inventory[SHATTERED_HEART_PLINTH_ITEM] = (
            _int(inventory.get(SHATTERED_HEART_PLINTH_ITEM)) - 1
        )
        data["inventory"] = inventory
        state["replica_plinth_built"] = True
        state["last_result"] = "Built Dahmaroc's replica plinth in the Study."
        return data, True, {
            "skill_xp": {"construction": 1.0},
            "message": state["last_result"],
        }

    if action_id == "add_replica_pairs":
        if not state["replica_plinth_built"]:
            return data, False, {"reason": "Build the replica plinth first."}
        ready = _replica_pair_ids(inventory, set(state["replica_pairs_added"]))
        if not ready:
            return data, False, {"reason": "No complete replica pair is ready."}
        for skill_id in ready:
            row = SHATTERED_HEART_SKILLS_BY_ID[skill_id]
            for item_name in row.replica_items:
                inventory[item_name] = _int(inventory.get(item_name)) - 1
            state["replica_pairs_added"].append(skill_id)
        data["inventory"] = inventory
        state["last_result"] = (
            f"Added {len(ready)} replica pair{'s' if len(ready) != 1 else ''}."
        )
        return data, True, {
            "pair_ids": ready,
            "pieces_added": len(ready) * 2,
            "replica_complete": len(state["replica_pairs_added"])
            == len(SHATTERED_HEART_SKILLS),
            "message": state["last_result"],
        }

    if action_id == "add_completed_pairs":
        bag_rocks = set(state["bag_rocks"])
        complete = _complete_pair_ids(inventory, bag_rocks)
        addable = _addable_pair_ids(state, complete, world_day_index_pure(data))
        if not addable:
            final_blocked = (
                len(state["placed_pairs"]) == 14
                and any(
                    skill_id not in state["placed_pairs"] for skill_id in complete
                )
                and not _final_pair_ready(state, world_day_index_pure(data))
            )
            reason = (
                "The final pair is still on its seven-day cooldown."
                if final_blocked
                else "No completed strange-rock pair is ready."
            )
            return data, False, {"reason": reason, "skill_xp": {}}

        skill_xp: dict[str, float] = {}
        completions_before = state["statues_completed"]
        replica_items: list[str] = []
        for skill_id in addable:
            row = SHATTERED_HEART_SKILLS_BY_ID[skill_id]
            for item_name in row.rock_items:
                _consume_piece(inventory, bag_rocks, item_name)
            state["placed_pairs"].append(skill_id)
            skill_xp[skill_id] = shattered_heart_pair_xp_pure(
                data.get(f"{skill_id}_level", 1)
            )
            if len(state["placed_pairs"]) != len(SHATTERED_HEART_SKILLS):
                continue

            state["statues_completed"] += 1
            state["completion_day"] = world_day_index_pure(data)
            state["placed_pairs"] = []
            if state["statues_completed"] == 1:
                inventory[SHATTERED_HEART_PLINTH_ITEM] = (
                    _int(inventory.get(SHATTERED_HEART_PLINTH_ITEM)) + 1
                )
            if state["replica_pieces_awarded"] < SHATTERED_HEART_REPLICA_PIECE_LIMIT:
                item_name = tuple(
                    item
                    for skill in SHATTERED_HEART_SKILLS
                    for item in skill.replica_items
                )[state["replica_pieces_awarded"]]
                inventory[item_name] = _int(inventory.get(item_name)) + 1
                state["replica_pieces_awarded"] += 1
                replica_items.append(item_name)

        data["inventory"] = inventory
        state["bag_rocks"] = [
            item_name for item_name in SHATTERED_HEART_ROCK_ITEMS if item_name in bag_rocks
        ]
        completions = state["statues_completed"] - completions_before
        kudos = SHATTERED_HEART_KUDOS_REWARD if completions_before == 0 and completions else 0
        state["last_result"] = (
            f"Added {len(addable)} museum pair{'s' if len(addable) != 1 else ''}"
            + (f" and completed {completions} statue." if completions else ".")
        )
        return data, True, {
            "pair_ids": addable,
            "skill_xp": skill_xp,
            "statues_completed": completions,
            "kudos": kudos,
            "plinth_awarded": bool(kudos),
            "replica_items": tuple(replica_items),
            "message": state["last_result"],
        }

    return data, False, {"reason": "Unknown Shattered Heart command."}


__all__ = [
    "SHATTERED_HEART_STATE_VERSION",
    "apply_shattered_heart_command_pure",
    "apply_shattered_heart_skilling_hook_pure",
    "default_shattered_heart_state_pure",
    "sanitize_shattered_heart_state_pure",
    "shattered_heart_pair_xp_pure",
    "shattered_heart_view_pure",
]
