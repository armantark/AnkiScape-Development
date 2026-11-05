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
    move_queue_entry_pure,
    queue_add_refusal_pure,
    queue_entry_unit_pure,
    queue_move_takes_over_pure,
    queue_runs_pure,
    remove_queue_entry_pure,
)
from .action_registry import COMBAT_REVIEW_ACTION_DISPLAY_NAME, is_utility_review_action, utility_review_surface_for_target
from .constants import QUEST_UNLOCK_RULES, UTILITY_ACTIVITY_DATA
from .last_action import last_action_record_pure
from .skill_guide_locks import target_lock_reasons_pure
from .skill_registry import get_skill
from .target_row import TargetRowMetadata
from ..data.construction_data import NAIL_DATA
from ..logic.inventory_pure import CARRIED_CAPACITY
from ..logic.summoning_logic import summoning_action_requirements_pure
from ..logic_pure.logic_pure import _runecrafting_multiplier_info, utility_activity_locked_reasons_pure
from ..logic_pure.logic_pure_magic import magic_used_items_pure


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


def _action_spec(action: Mapping[str, Any]) -> Any:
    if action["kind"] == "utility":
        return UTILITY_ACTIVITY_DATA.get(action["utility_id"], {})
    return action_target_spec_pure(action)


def _inputs_and_yield(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> tuple[dict[str, tuple[str, ...]], dict[str, int], int]:
    """What one run uses, as alternatives per input and an amount, and the products it makes."""
    spec = _action_spec(action)
    made = int(spec_field_pure(spec, "output_qty") or spec_field_pure(spec, "output_quantity") or 1)
    if action.get("skill") == "Summoning":
        needs = summoning_action_requirements_pure(player_data, str(action["target"]))
        return {item: (item,) for item in needs}, needs, made
    if action.get("skill") == "Runecrafting" and spec_field_pure(spec, "kind") == "standard":
        level = int(player_data.get("runecrafting_level") or 1)
        return {"essence": tuple(spec_field_pure(spec, "essence_items"))}, {"essence": 1}, _runecrafting_multiplier_info(spec, level)[0]
    needs = dict(spec_field_pure(spec, "requirements") or {})
    options = {"Nails": tuple(NAIL_DATA), **dict(spec_field_pure(spec, "material_options") or {})}
    return {item: tuple(options.get(item) or (item,)) for item in needs}, needs, made


def _used_items(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> set[str]:
    """Every item a run of the action can use up; never a tool, an access item or a wage, so those locks stay."""
    alternatives, _needs, _made = _inputs_and_yield(player_data, action)
    items = {item for options in alternatives.values() for item in options}
    spec = _action_spec(action)
    for field in ("bait_options", "any_requirements", "openable_items"):
        items.update(spec_field_pure(spec, field) or ())
    if rune := spec_field_pure(spec, "component_rune"):
        items.update(("Pure essence", rune, spec_field_pure(spec, "consumed_talisman")))
    if action.get("skill") == "Magic":
        items.update(magic_used_items_pure(spec))
    if "Nails" in items:
        items.update(NAIL_DATA)
    return items


def _action_locks(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> tuple[str, ...]:
    """What the action's target row says locks it now; empty for an action no row list locks."""
    if action.get("kind") == "skill":
        return target_lock_reasons_pure(player_data, get_skill(action["skill"]).id, action["target"])
    if action.get("utility_id") in UTILITY_ACTIVITY_DATA:
        return utility_activity_locked_reasons_pure(
            player_data, action["utility_id"], UTILITY_ACTIVITY_DATA, QUEST_UNLOCK_RULES
        )
    return ()


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
    return tuple(replace(row, plan_only=_plan_only(player_data, surface, row)) for row in rows)


def _bank_count(player_data: Mapping[str, Any], items: tuple[str, ...]) -> int:
    bank = player_data.get("inventory") or {}
    return sum(int(bank.get(item) or 0) for item in items)


def _queued_makes(player_data: Mapping[str, Any], items: tuple[str, ...]) -> list[tuple[int, int]]:
    """What the queue's entries will still make of ``items``: (entry number, amount)."""
    queue = action_queue_pure(player_data)
    makes = []
    for position, entry in enumerate(queue["entries"]):
        done = queue["done"] if position == 0 else 0
        if entry["count"] is not None and set(items) & set(action_product_items_pure(entry["action"])):
            makes.append((position + 1, max(0, entry["count"] - done)))
    return makes


def _supply_count(player_data: Mapping[str, Any], items: tuple[str, ...]) -> int:
    return _bank_count(player_data, items) + sum(amount for _entry, amount in _queued_makes(player_data, items))


def action_supply_limit_pure(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> int | None:
    """The most of the entry's unit the Bank and earlier entries supply inputs for; None when no Bank item limits it.

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
        return sum(_supply_count(player_data, items) for items in alternatives.values())
    return min(
        _supply_count(player_data, alternatives[need]) // max(1, int(amount)) for need, amount in needs.items()
    ) * made


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
        "enabled": not refusal,
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
