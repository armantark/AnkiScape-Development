"""The main menu's side of the action queue: what "Add to queue" offers, and its commands.

The count box starts at the most the Bank holds inputs for now, so a sensible
count needs no arithmetic; the player may type more, because an earlier entry
can make what a later one uses. An action no Bank item limits, such as mining
or a fight, starts at one inventory, the unit a 2012 player counts gathering in.
"""

from __future__ import annotations

from typing import Any, Mapping

from .action_products import action_product_items_pure, action_target_spec_pure
from .action_queue import (
    MAX_QUEUE_ENTRIES,
    QUEUE_FULL_TEXT,
    action_queue_view_pure,
    queue_entry_name_pure,
    queue_entry_unit_pure,
)
from .action_registry import utility_review_surface_for_target
from .constants import QUEST_DATA, UTILITY_ACTIVITY_DATA
from .last_action import last_action_record_pure
from .skill_registry import get_skill
from ..logic.inventory_pure import CARRIED_CAPACITY
from ..logic.summoning_logic import summoning_action_requirements_pure
from ..logic_pure.logic_pure import _runecrafting_multiplier_info, quest_locked_reasons_pure, quest_state_pure

_STATE_LABELS = {"done": "Done", "stopped": "Stopped", "waiting": "Next"}


def _field(spec: Any, name: str) -> Any:
    return spec.get(name) if isinstance(spec, Mapping) else getattr(spec, name, None)


def menu_action_record_pure(player_data: Mapping[str, Any], surface: str) -> dict[str, Any]:
    """The action a skill panel's Start would run now; empty when the panel has none selected.

    A save that never picked a target runs the skill's default one, so the entry
    names and counts that target.
    """
    record = last_action_record_pure(player_data, surface)
    if record.get("kind") == "utility" and utility_review_surface_for_target(record["utility_id"]) != surface:
        return {}
    if record.get("kind") == "skill" and record["target"] is None:
        record["target"] = get_skill(surface).default_target
    return record


def utility_action_record_pure(utility_id: str) -> dict[str, Any]:
    """The record of an activity card's action; empty when no card is open."""
    return {"kind": "utility", "utility_id": utility_id} if utility_id else {}


def _inputs_and_yield(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> tuple[dict[str, tuple[str, ...]], dict[str, int], int]:
    """What one run uses, as alternatives per input and an amount, and the products it makes."""
    if action["kind"] == "utility":
        spec = UTILITY_ACTIVITY_DATA.get(action["utility_id"], {})
    else:
        spec = action_target_spec_pure(action)
    made = int(_field(spec, "output_qty") or _field(spec, "output_quantity") or 1)
    if action.get("skill") == "Summoning":
        needs = summoning_action_requirements_pure(player_data, str(action["target"]))
        return {item: (item,) for item in needs}, needs, made
    if action.get("skill") == "Runecrafting" and _field(spec, "kind") == "standard":
        level = int(player_data.get("runecrafting_level") or 1)
        return {"essence": tuple(_field(spec, "essence_items"))}, {"essence": 1}, _runecrafting_multiplier_info(spec, level)[0]
    needs = dict(_field(spec, "requirements") or {})
    options = dict(_field(spec, "material_options") or {})
    return {item: tuple(options.get(item) or (item,)) for item in needs}, needs, made


def action_bank_limit_pure(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> int | None:
    """The most products the Bank holds inputs for now; None when no Bank item limits the entry.

    Only an entry that counts products has this limit: a review of an action
    that makes nothing can use several inputs, so its count in reviews is unknown.
    """
    if queue_entry_unit_pure(action) != "items":
        return None
    alternatives, needs, made = _inputs_and_yield(player_data, action)
    if not needs:
        return None
    bank = player_data.get("inventory") or {}
    runs = min(
        sum(int(bank.get(item) or 0) for item in alternatives[need]) // max(1, int(amount))
        for need, amount in needs.items()
    )
    return runs * made


def _unit_text(unit: str, products: tuple[str, ...]) -> str:
    if unit != "items":
        return unit
    return products[0] if len(products) == 1 else "items"


def _add_refusal(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> str:
    """Why "Add to queue" cannot take ``action`` now; empty when it can."""
    if not action:
        return "Choose what to do first."
    if not action_queue_view_pure(player_data)["can_add"]:
        return QUEUE_FULL_TEXT
    if action["kind"] != "quest":
        return ""
    if quest_state_pure(player_data, action["quest_id"]).get("completed"):
        return "This quest is complete."
    locked = quest_locked_reasons_pure(player_data, action["quest_id"], QUEST_DATA)
    return "Requires: " + ", ".join(map(str, locked)) if locked else ""


def queue_add_view_pure(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> dict[str, Any]:
    """What an "Add to queue" control shows for ``action``: whether it can add, and the count box."""
    refusal = _add_refusal(player_data, action)
    has_count = bool(action) and action["kind"] != "quest"
    limit = action_bank_limit_pure(player_data, action) if has_count else None
    unit = _unit_text(queue_entry_unit_pure(action), action_product_items_pure(action)) if has_count else ""
    if refusal:
        tooltip = refusal
    elif has_count:
        tooltip = f"Add {queue_entry_name_pure(action)} to the queue. It runs until the count is reached, then the next entry starts."
    else:
        tooltip = f"Add {queue_entry_name_pure(action)} to the queue. A quest runs until it stops, then the next entry starts."
    if not has_count:
        count_tooltip = ""
    elif limit is None:
        count_tooltip = "Nothing in your Bank limits this; type any count."
    else:
        count_tooltip = f"Your Bank holds enough for {limit:,} {unit}. Type more to use what an earlier entry makes."
    return {
        "enabled": not refusal,
        "has_count": has_count,
        "count": CARRIED_CAPACITY if limit is None else limit,
        "unit": unit,
        "count_tooltip": count_tooltip,
        "tooltip": tooltip,
    }


def _row_text(row: Mapping[str, Any]) -> str:
    if row["count"] is None:
        return f"{row['name']} · until the quest stops"
    text = f"{row['name']} · {row['done']:,} / {row['count']:,} {_unit_text(row['unit'], row['products'])}"
    return f"{text} · stopped: {row['stopped']}" if row["stopped"] else text


def queue_panel_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """The menu's queue list: one line per entry with its state, and the Resume and Clear controls."""
    view = action_queue_view_pure(player_data)
    can_resume = view["paused"] and not view["finished"]
    labels = {**_STATE_LABELS, "current": "Paused" if can_resume else "Now"}
    if view["finished"]:
        status = "Finished. Add an entry to plan again."
    elif can_resume:
        status = "Paused. Resume continues the paused entry."
    else:
        status = "Runs top to bottom while you study."
    return {
        "visible": bool(view["entries"]),
        "title": f"Queue {len(view['entries'])}/{MAX_QUEUE_ENTRIES}",
        "status": status,
        "rows": [{"state": labels[row["state"]], "text": _row_text(row)} for row in view["entries"]],
        "can_resume": can_resume,
    }
