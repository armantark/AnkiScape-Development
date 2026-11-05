"""The main menu's side of the action queue: what "Add to queue" offers, and the queue list.

The count box starts at what the Bank and the earlier entries supply inputs
for, never below one, so a sensible count needs no arithmetic and an entry can
plan on what an earlier one makes; the line beside the box names both sources.
An action no Bank item limits, such as mining or a fight, starts at one
inventory, the unit a 2012 player counts gathering in.

A target row locked only for lack of what its run uses up is plan-only (owner,
Pass 21): it takes the click and the Add record, because an earlier entry can
make those items, and Start stays off until they exist.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping

from .action_products import (
    _action_locks,
    _inputs_and_yield,
    _projected_stock,
    _stock_count,
    _used_items,
    action_supply_limit_pure as _action_supply_limit,
    queue_plan_refusal_pure as _queue_plan_refusal,
    action_product_items_pure,
    action_used_input_pure,
)
from .action_queue import (
    MAX_QUEUE_ENTRIES,
    action_queue_pure,
    add_queue_entry_pure,
    action_queue_view_pure,
    current_queue_entry_pure,
    move_queue_entry_pure,
    queue_add_refusal_pure,
    queue_entry_unit_pure,
    queue_move_takes_over_pure,
    queue_runs_pure,
    remove_queue_entry_pure,
)
from .action_registry import COMBAT_REVIEW_ACTION_DISPLAY_NAME, is_utility_review_action, utility_review_surface_for_target
from .last_action import last_action_record_pure
from .skill_registry import get_skill
from .target_row import TargetRowMetadata
from ..logic.inventory_pure import CARRIED_CAPACITY


# More than any recipe uses, so a supposed Bank never locks a row by quantity.
_PLANNED_STOCK = 2_147_483_647


def menu_action_record_pure(player_data: Mapping[str, Any], surface: str, picked: Any = None) -> dict[str, Any]:
    """The action a skill panel's Start would run now; empty when the panel has none selected.

    ``picked`` is a target the player picked while the queue runs this panel's
    action, which the panel holds for the queue instead of switching the
    running entry. A save that never picked a target runs the skill's default
    one, so the entry names and counts that target.
    """
    record = last_action_record_pure(player_data, surface)
    if picked is not None and is_utility_review_action(surface):
        record = {"kind": "utility", "utility_id": picked}
    elif picked is not None and record:
        record["target"] = picked
    if record.get("kind") == "utility" and utility_review_surface_for_target(record["utility_id"]) != surface:
        return {}
    if record.get("kind") == "skill" and record["target"] is None:
        record["target"] = get_skill(surface).default_target
    return record


def queue_runs_surface_pure(player_data: Mapping[str, Any], surface: str, current_skill: Any) -> bool:
    """Whether the queue really runs its first entry on this panel, so a target click must not switch it."""
    if not queue_runs_pure(player_data, current_skill):
        return False
    action = action_queue_pure(player_data)["entries"][0]["action"]
    if action["kind"] == "utility":
        return utility_review_surface_for_target(action["utility_id"]) == surface
    if action["kind"] == "combat":
        return surface == COMBAT_REVIEW_ACTION_DISPLAY_NAME
    return action.get("skill") == surface


def surface_trains_pick_pure(player_data: Mapping[str, Any], surface: str, active: Any, picked: Any) -> bool:
    """Whether the panel's skill runs the target the panel shows; a held pick of another target does not."""
    return active == surface and menu_action_record_pure(player_data, surface, picked) == menu_action_record_pure(
        player_data, surface
    )


def _activity_id(action: Mapping[str, Any]) -> str:
    return str(action["utility_id"]) if action.get("kind") == "utility" else "bankstanding"


def activity_started_by_add_pure(
    player_data: Mapping[str, Any], current_skill: Any, action: Mapping[str, Any], count: Any
) -> str:
    """The activity an add starts at once, as Start would, so it first asks to leave a running session.

    That is the queue's first entry, or the added one in an empty queue. Empty
    when the queue refuses the add, so no session ends for nothing; when the
    queue already runs, so the add only waits its turn.
    """
    queue = action_queue_pure(player_data)
    if queue_add_refusal_pure(player_data, action) or not add_queue_entry_pure(queue, action, count)[1]:
        return ""
    if queue_runs_pure(player_data, current_skill):
        return ""
    entry = current_queue_entry_pure(queue)
    return _activity_id(entry["action"] if entry is not None else action)


def activity_started_by_move_pure(
    player_data: Mapping[str, Any], current_skill: Any, position: int, new_index: int
) -> str:
    """The activity a move starts at once, so it first asks to leave a running session, as an add does."""
    queue, ok = move_queue_entry_pure(action_queue_pure(player_data), position, new_index)
    if not ok or not queue_move_takes_over_pure(player_data, current_skill, position, new_index):
        return ""
    return _activity_id(current_queue_entry_pure(queue)["action"])


def activity_started_by_remove_pure(player_data: Mapping[str, Any], current_skill: Any, position: int) -> str:
    """Where removing the running entry lands, so it first asks to leave a running session: the next activity or Bankstanding."""
    queue, ok = remove_queue_entry_pure(action_queue_pure(player_data), position)
    if not ok or position or not queue_runs_pure(player_data, current_skill):
        return ""
    entry = current_queue_entry_pure(queue)
    return _activity_id(entry["action"]) if entry is not None else "bankstanding"


def utility_action_record_pure(utility_id: str) -> dict[str, Any]:
    """The record of an activity card's action; empty when no card is open."""
    return {"kind": "utility", "utility_id": utility_id} if utility_id else {}


def pick_can_start_pure(player_data: Mapping[str, Any], surface: str, picked: Any) -> bool:
    """Whether the panel's Start can run this target now, so a pick without its inputs leaves Start off."""
    return not _action_locks(player_data, menu_action_record_pure(player_data, surface, picked))


def _plan_only(player_data: Mapping[str, Any], surface: str, row: TargetRowMetadata) -> bool:
    """Whether the row's own lock reasons all clear once the Bank holds what its run uses up."""
    action = menu_action_record_pure(player_data, surface, row.target_id)
    locks = _action_locks(player_data, action)
    if row.enabled or not locks or not set(row.locked_reasons) <= set(locks):
        return False
    bank = {**(player_data.get("inventory") or {}), **dict.fromkeys(_used_items(player_data, action), _PLANNED_STOCK)}
    return not _action_locks({**player_data, "inventory": bank}, action)


def plan_rows_pure(
    player_data: Mapping[str, Any], surface: str, rows: tuple[TargetRowMetadata, ...]
) -> tuple[TargetRowMetadata, ...]:
    """The panel's rows, with each row that lacks only what its run uses up marked plan-only."""
    planned = []
    for row in rows:
        only = _plan_only(player_data, surface, row)
        action = menu_action_record_pure(player_data, surface, row.target_id)
        ready = only and not queue_plan_refusal_pure(player_data, action)
        planned.append(replace(row, plan_only=only, plan_ready=ready))
    return tuple(planned)


def _bank_count(player_data: Mapping[str, Any], items: tuple[str, ...]) -> int:
    bank = player_data.get("inventory") or {}
    return sum(int(bank.get(item) or 0) for item in items)


def _queued_makes(player_data: Mapping[str, Any], items: tuple[str, ...]) -> list[tuple[int, int]]:
    return [(position, count) for position, bank in enumerate(_projected_stock(player_data, action_queue_pure(player_data)))
            if position and (count := _stock_count([bank], items))]


def action_supply_limit_pure(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> int | None:
    return _action_supply_limit(player_data, action, action_queue_pure(player_data))


def queue_plan_refusal_pure(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> str:
    return _queue_plan_refusal(player_data, action, action_queue_pure(player_data))


def _materials_text(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> str:
    """Where an entry's inputs come from: "Iron ore: 0 in Bank, 100 from entry 1"; empty when none."""
    alternatives, _needs, _made = _inputs_and_yield(player_data, action)
    return " · ".join(
        f"{need[:1].upper()}{need[1:]}: "
        + ", ".join([
            f"{_bank_count(player_data, items):,} in Bank",
            *(f"{amount:,} from entry {entry}" for entry, amount in _queued_makes(player_data, items)),
        ])
        for need, items in alternatives.items()
    )


def _unit_text(unit: str, products: tuple[str, ...], used: str) -> str:
    if unit == "uses":
        return f"{used} used"
    if unit != "items":
        return unit
    return products[0] if len(products) == 1 else "items"


def queue_add_view_pure(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> dict[str, Any]:
    """What an "Add to queue" control shows for ``action``: whether it can add, and the count box."""
    refusal = queue_add_refusal_pure(player_data, action)
    has_count = bool(action) and action["kind"] != "quest"
    limit = action_supply_limit_pure(player_data, action) if has_count else None
    unit = (
        _unit_text(queue_entry_unit_pure(action), action_product_items_pure(action), action_used_input_pure(action))
        if has_count
        else ""
    )
    return {
        "enabled": not refusal and limit != 0,
        "maximum": max(1, limit) if limit is not None else 2_147_483_647,
        "has_count": has_count,
        "count": CARRIED_CAPACITY if limit is None else max(1, limit),
        "unit": unit,
        "materials": _materials_text(player_data, action) if has_count else "",
        "count_tooltip": "Starts at your Bank plus earlier entries." if limit is not None else "",
        "tooltip": refusal,
    }


def _row_text(row: Mapping[str, Any]) -> str:
    if row["count"] is None:
        return f"{row['name']} · until it stops"
    return f"{row['name']} · {row['done']:,} / {row['count']:,} {_unit_text(row['unit'], row['products'], row['used'])}"


def queue_panel_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """The menu's queue box: a title, one numbered line per entry with its moves, Resume for a paused queue, and Clear."""
    view = action_queue_view_pure(player_data)
    labels = {"current": "Paused" if view["paused"] else "Next" if view["suspended"] else "Now", "waiting": "Next"}
    count = len(view["entries"])
    return {
        "title": f"Queue: {count} of {MAX_QUEUE_ENTRIES}" if count else "Queue: empty",
        "rows": [
            {
                "position": f"{position + 1}.",
                "state": labels[row["state"]],
                "text": _row_text(row),
                "current": row["state"] == "current",
                "can_move_up": position > 0,
                "can_move_down": position + 1 < count,
            }
            for position, row in enumerate(view["entries"])
        ],
        "resume_text": "Resume queue" if view["paused"] or view["suspended"] else "",
    }
