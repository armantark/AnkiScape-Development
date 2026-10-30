"""The main menu's side of the action queue: what "Add to queue" offers, and the queue list.

The count box starts at the most the Bank holds inputs for now, so a sensible
count needs no arithmetic; the player may type more, because an earlier entry
can make what a later one uses, and the line beside the box names both: what
the Bank holds and what the queue will make. An action no Bank item limits,
such as mining or a fight, starts at one inventory, the unit a 2012 player
counts gathering in.
"""

from __future__ import annotations

from typing import Any, Mapping

from .action_products import (
    action_product_items_pure,
    action_target_spec_pure,
    action_used_input_pure,
    spec_field_pure,
)
from .action_queue import (
    MAX_QUEUE_ENTRIES,
    action_queue_pure,
    add_queue_entry_pure,
    action_queue_view_pure,
    current_queue_entry_pure,
    queue_add_refusal_pure,
    queue_entry_unit_pure,
    queue_runs_pure,
)
from .action_registry import COMBAT_REVIEW_ACTION_DISPLAY_NAME, utility_review_surface_for_target
from .constants import UTILITY_ACTIVITY_DATA
from .last_action import last_action_record_pure
from .skill_registry import get_skill
from ..logic.inventory_pure import CARRIED_CAPACITY
from ..logic.summoning_logic import summoning_action_requirements_pure
from ..logic_pure.logic_pure import _runecrafting_multiplier_info


def menu_action_record_pure(player_data: Mapping[str, Any], surface: str, picked: Any = None) -> dict[str, Any]:
    """The action a skill panel's Start would run now; empty when the panel has none selected.

    ``picked`` is a target the player picked while the queue runs this panel's
    action, which the panel holds for the queue instead of switching the
    running entry. A save that never picked a target runs the skill's default
    one, so the entry names and counts that target.
    """
    record = last_action_record_pure(player_data, surface)
    if picked is not None and record.get("kind") == "utility":
        record["utility_id"] = picked
    elif picked is not None and record:
        record["target"] = picked
    if record.get("kind") == "utility" and utility_review_surface_for_target(record["utility_id"]) != surface:
        return {}
    if record.get("kind") == "skill" and record["target"] is None:
        record["target"] = get_skill(surface).default_target
    return record


def queue_runs_surface_pure(player_data: Mapping[str, Any], surface: str) -> bool:
    """Whether the queue's running entry is this panel's action, so a target click must not switch it."""
    queue = action_queue_pure(player_data)
    entry = current_queue_entry_pure(queue)
    if entry is None or queue["paused"]:
        return False
    action = entry["action"]
    if action["kind"] == "utility":
        return utility_review_surface_for_target(action["utility_id"]) == surface
    if action["kind"] == "combat":
        return surface == COMBAT_REVIEW_ACTION_DISPLAY_NAME
    return action.get("skill") == surface


def activity_started_by_add_pure(
    player_data: Mapping[str, Any], current_skill: Any, action: Mapping[str, Any], count: Any
) -> str:
    """The activity an add starts at once, as Start would, so it first asks to leave a running session.

    That is the queue's first entry, or the added one in an empty queue. Empty
    when the queue refuses the add, so no session ends for nothing; when the
    queue already runs, so the add only waits its turn; or when the entry that
    starts is not an activity.
    """
    queue = action_queue_pure(player_data)
    if queue_add_refusal_pure(player_data, action) or not add_queue_entry_pure(queue, action, count)[1]:
        return ""
    if queue_runs_pure(player_data, current_skill):
        return ""
    entry = current_queue_entry_pure(queue)
    starting = entry["action"] if entry is not None else action
    return str(starting["utility_id"]) if starting.get("kind") == "utility" else ""


def utility_action_record_pure(utility_id: str) -> dict[str, Any]:
    """The record of an activity card's action; empty when no card is open."""
    return {"kind": "utility", "utility_id": utility_id} if utility_id else {}


def _inputs_and_yield(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> tuple[dict[str, tuple[str, ...]], dict[str, int], int]:
    """What one run uses, as alternatives per input and an amount, and the products it makes."""
    if action["kind"] == "utility":
        spec = UTILITY_ACTIVITY_DATA.get(action["utility_id"], {})
    else:
        spec = action_target_spec_pure(action)
    made = int(spec_field_pure(spec, "output_qty") or spec_field_pure(spec, "output_quantity") or 1)
    if action.get("skill") == "Summoning":
        needs = summoning_action_requirements_pure(player_data, str(action["target"]))
        return {item: (item,) for item in needs}, needs, made
    if action.get("skill") == "Runecrafting" and spec_field_pure(spec, "kind") == "standard":
        level = int(player_data.get("runecrafting_level") or 1)
        return {"essence": tuple(spec_field_pure(spec, "essence_items"))}, {"essence": 1}, _runecrafting_multiplier_info(spec, level)[0]
    needs = dict(spec_field_pure(spec, "requirements") or {})
    options = dict(spec_field_pure(spec, "material_options") or {})
    return {item: tuple(options.get(item) or (item,)) for item in needs}, needs, made


def _bank_count(player_data: Mapping[str, Any], items: tuple[str, ...]) -> int:
    bank = player_data.get("inventory") or {}
    return sum(int(bank.get(item) or 0) for item in items)


def action_bank_limit_pure(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> int | None:
    """The most of the entry's unit the Bank holds inputs for now; None when no Bank item limits it.

    An entry that counts reviews has no such limit: one review can use several
    inputs, so its count in reviews is unknown.
    """
    unit = queue_entry_unit_pure(action)
    if unit not in {"items", "uses"}:
        return None
    alternatives, needs, made = _inputs_and_yield(player_data, action)
    if not needs:
        return None
    if unit == "uses":
        return sum(_bank_count(player_data, items) for items in alternatives.values())
    return min(
        _bank_count(player_data, alternatives[need]) // max(1, int(amount)) for need, amount in needs.items()
    ) * made


def _queued_makes(player_data: Mapping[str, Any], items: tuple[str, ...]) -> list[str]:
    """What the queue's entries will still make of ``items``: "100 from entry 1"."""
    queue = action_queue_pure(player_data)
    parts = []
    for position, entry in enumerate(queue["entries"]):
        done = queue["done"] if position == 0 else 0
        if entry["count"] is not None and set(items) & set(action_product_items_pure(entry["action"])):
            parts.append(f"{max(0, entry['count'] - done):,} from entry {position + 1}")
    return parts


def _materials_text(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> str:
    """Where an entry's inputs come from: "Iron ore: 0 in Bank, 100 from entry 1"; empty when none."""
    alternatives, _needs, _made = _inputs_and_yield(player_data, action)
    return " · ".join(
        f"{need[:1].upper()}{need[1:]}: "
        + ", ".join([f"{_bank_count(player_data, items):,} in Bank", *_queued_makes(player_data, items)])
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
    limit = action_bank_limit_pure(player_data, action) if has_count else None
    unit = (
        _unit_text(queue_entry_unit_pure(action), action_product_items_pure(action), action_used_input_pure(action))
        if has_count
        else ""
    )
    return {
        "enabled": not refusal,
        "has_count": has_count,
        "count": CARRIED_CAPACITY if limit is None else limit,
        "unit": unit,
        "materials": _materials_text(player_data, action) if has_count else "",
        "count_tooltip": "Starts at the most your Bank allows." if limit is not None else "",
        "tooltip": refusal,
    }


def _row_text(row: Mapping[str, Any]) -> str:
    if row["count"] is None:
        return f"{row['name']} · until it stops"
    return f"{row['name']} · {row['done']:,} / {row['count']:,} {_unit_text(row['unit'], row['products'], row['used'])}"


def queue_panel_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """The menu's queue box: a title, one numbered line per entry, Resume for a paused queue, and Clear."""
    view = action_queue_view_pure(player_data)
    labels = {"current": "Paused" if view["paused"] else "Now", "waiting": "Next"}
    count = len(view["entries"])
    return {
        "title": f"Queue: {count} of {MAX_QUEUE_ENTRIES}" if count else "Queue: empty",
        "rows": [
            {
                "position": f"{position + 1}.",
                "state": labels[row["state"]],
                "text": _row_text(row),
                "current": row["state"] == "current",
                "removable": row["removable"],
            }
            for position, row in enumerate(view["entries"])
        ],
        "resume_text": "Resume queue" if view["paused"] else "",
    }
