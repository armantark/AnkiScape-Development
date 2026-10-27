"""The action queue: up to five actions that reviews work through once, top to bottom.

At 10x speed an action uses up its materials in a few cards, so the player
plans a chain such as mine, smelt, smith instead of restarting each step. An
entry is an action in the last-action record shape and a count in that
action's own unit: the product items it makes, kills for a fight, reviews for
an action that makes nothing, and no count for a quest, which runs until it
stops. After each review the runtime adds the review's progress, and a full
entry starts the next one. When an entry's action stops for a missing material
or requirement, the queue notes why and starts the next entry in place of the
switch to Bankstanding; only a finished queue lets that switch happen, with its
usual notice. A manual Stop pauses the queue; Resume continues its entry.

The owner ruled out loops (2026-10-26): the queue never repeats and holds at
most five entries, so the player still plans his training.

Transitions inside a review or a menu action write the save directly, because
each tab's own setter would open a second undo step inside the running one.
"""

from __future__ import annotations

from typing import Any, Mapping

from .action_products import action_product_items_pure, action_target_spec_pure
from .action_registry import (
    COMBAT_REVIEW_ACTION_DISPLAY_NAME,
    QUEST_REVIEW_ACTION_DISPLAY_NAME,
    utility_review_surface_for_target,
)
from .constants import QUEST_DATA
from .last_action import (
    LAST_ACTION_KEY,
    last_action_name_pure,
    last_action_record_pure,
    resume_button_view_pure,
    resume_last_action,
    saved_last_action_pure,
    valid_action_record_pure,
)
from .menu_cooking import with_cooking_target
from .review_event_log import record_review_event_pure
from .skill_registry import get_skill
from ..data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
from ..logic.inventory_pure import review_item_changes_pure
from ..logic.shooting_star_logic import apply_shooting_star_join_pure
from ..logic_pure.logic_pure import quest_state_pure, start_quest_pure

ACTION_QUEUE_KEY = "action_queue"
MAX_QUEUE_ENTRIES = 5


def _empty_queue() -> dict[str, Any]:
    return {"entries": [], "index": 0, "done": 0, "paused": False}


def action_queue_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """The saved queue; an entry this game can no longer start is dropped."""
    raw = player_data.get(ACTION_QUEUE_KEY)
    if not isinstance(raw, Mapping):
        return _empty_queue()
    entries = []
    for entry in raw.get("entries") or ():
        action = valid_action_record_pure(entry.get("action") if isinstance(entry, Mapping) else None)
        if action:
            entries.append({**entry, "action": action})
    entries = entries[:MAX_QUEUE_ENTRIES]
    return {
        "entries": entries,
        "index": min(max(0, int(raw.get("index") or 0)), len(entries)),
        "done": max(0, int(raw.get("done") or 0)),
        "paused": bool(raw.get("paused")),
    }


def current_queue_entry_pure(queue: Mapping[str, Any]) -> dict[str, Any] | None:
    """The entry running now; None for an empty or finished queue."""
    entries = queue["entries"]
    return entries[queue["index"]] if queue["index"] < len(entries) else None


def add_queue_entry_pure(queue: Mapping[str, Any], action: Mapping[str, Any], count: Any) -> tuple[dict[str, Any], bool]:
    """Append an entry; a full queue, an unknown action or a count below one refuses.

    A quest takes no count. A finished queue gives way to the new plan.
    """
    record = valid_action_record_pure({key: value for key, value in action.items() if key != "reason"})
    if not record:
        return dict(queue), False
    if record["kind"] == "quest":
        count = None
    elif not isinstance(count, int) or isinstance(count, bool) or count < 1:
        return dict(queue), False
    if current_queue_entry_pure(queue) is None:
        queue = _empty_queue()
    if len(queue["entries"]) >= MAX_QUEUE_ENTRIES:
        return dict(queue), False
    return {**queue, "entries": [*queue["entries"], {"action": record, "count": count}]}, True


def pass_queue_entry_pure(queue: Mapping[str, Any], stop_reason: str = "") -> dict[str, Any]:
    """Move on to the next entry, keeping what it did; ``stop_reason`` marks one that stopped short."""
    entries = list(queue["entries"])
    entries[queue["index"]] = {**entries[queue["index"]], "done": queue["done"]}
    if stop_reason:
        entries[queue["index"]]["stopped"] = stop_reason
    return {**queue, "entries": entries, "index": queue["index"] + 1, "done": 0}


def advance_queue_pure(queue: Mapping[str, Any], progress: int) -> tuple[dict[str, Any], bool]:
    """Add a review's progress; True when that fills the entry and the next takes over."""
    entry = current_queue_entry_pure(queue)
    if entry is None or entry["count"] is None:
        return dict(queue), False
    done = queue["done"] + progress
    if done < entry["count"]:
        return {**queue, "done": done}, False
    return pass_queue_entry_pure({**queue, "done": done}), True


def same_action_pure(first: Mapping[str, Any], second: Mapping[str, Any]) -> bool:
    """Whether two records name one action, whatever reason either stopped for."""
    return {k: v for k, v in first.items() if k != "reason"} == {
        k: v for k, v in second.items() if k != "reason"
    }


def queue_entry_unit_pure(action: Mapping[str, Any]) -> str:
    """What an entry counts: "items" (its products), "kills", "reviews", or "" for a quest."""
    if action["kind"] == "quest":
        return ""
    if action["kind"] == "combat":
        return "kills"
    return "items" if action_product_items_pure(action) else "reviews"


def queue_entry_progress_pure(
    action: Mapping[str, Any], before: Mapping[str, Any], after: Mapping[str, Any]
) -> int:
    """One review's progress on an entry, in the entry's unit."""
    unit = queue_entry_unit_pure(action)
    if unit == "kills":
        target = action["target"]
        return max(0, int((after.get("combat_kill_counts") or {}).get(target, 0)) - int(
            (before.get("combat_kill_counts") or {}).get(target, 0)
        ))
    if unit == "items":
        changes = review_item_changes_pure(before, after)
        return sum(max(0, changes.get(item, 0)) for item in action_product_items_pure(action))
    return 1 if unit == "reviews" else 0


def queue_entry_name_pure(action: Mapping[str, Any]) -> str:
    """The action's name plus its target, so two Smithing entries read apart."""
    name = last_action_name_pure(action)
    spec = action_target_spec_pure(action)
    target = spec.get("display_name") if isinstance(spec, Mapping) else getattr(spec, "display_name", None)
    return f"{name}: {target}" if target else name


def _queue_entry_row(queue: Mapping[str, Any], position: int) -> dict[str, Any]:
    entry = queue["entries"][position]
    action = entry["action"]
    if position < queue["index"]:
        state, done = "stopped" if entry.get("stopped") else "done", entry.get("done", 0)
    else:
        state = "current" if position == queue["index"] else "waiting"
        done = queue["done"] if state == "current" else 0
    return {
        "name": queue_entry_name_pure(action),
        "unit": queue_entry_unit_pure(action),
        "products": action_product_items_pure(action),
        "count": entry["count"],
        "done": done,
        "state": state,
        "stopped": str(entry.get("stopped") or ""),
    }


def action_queue_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """What a queue panel shows: each entry's name, unit, count, progress and state."""
    queue = action_queue_pure(player_data)
    rows = [_queue_entry_row(queue, position) for position in range(len(queue["entries"]))]
    finished = bool(rows) and current_queue_entry_pure(queue) is None
    return {
        "entries": rows,
        "paused": queue["paused"],
        "finished": finished,
        "can_add": finished or len(rows) < MAX_QUEUE_ENTRIES,
    }


def _start_values(addon, current: Mapping[str, Any], action: Mapping[str, Any]) -> tuple[dict[str, Any], str] | None:
    """The save and review action that start ``action`` as its tab's Start would; None when it cannot."""
    kind = action["kind"]
    if kind == "quest":
        updated, ok = start_quest_pure(current, action["quest_id"], QUEST_DATA)
        return (updated, QUEST_REVIEW_ACTION_DISPLAY_NAME) if ok else None
    if kind == "utility":
        utility_id = action["utility_id"]
        updated, joined = dict(current), True
        if utility_id == SHOOTING_STAR_ACTIVITY_ID:
            updated, joined, _info = apply_shooting_star_join_pure(current)
        updated["current_utility"] = utility_id
        return (updated, utility_review_surface_for_target(utility_id)) if joined else None
    if kind == "combat":
        values = {**addon._combat_target_values(current, action["target"]), "combat_action": action["combat_action"]}
        return {**current, **values}, COMBAT_REVIEW_ACTION_DISPLAY_NAME
    skill = get_skill(action["skill"])
    updated = dict(current)
    if skill.current_target_key and action.get("target") is not None:
        updated[skill.current_target_key] = action["target"]
        if skill.id == "cooking":
            updated = with_cooking_target(addon, updated, action["target"])
    return updated, skill.display_name


def _run_current_entry(addon, current: Mapping[str, Any], queue: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """The save that runs the queue's current entry, passing each entry that cannot start.

    The review action is None when no entry is left to run.
    """
    updated = dict(current)
    while (entry := current_queue_entry_pure(queue)) is not None:
        started = _start_values(addon, updated, entry["action"])
        if started is not None:
            return {**started[0], ACTION_QUEUE_KEY: queue}, started[1]
        reason = "it could not start"
        updated = record_review_event_pure(
            updated, "activity", f"Queue: {queue_entry_name_pure(entry['action'])} stopped · {reason}"
        )
        queue = pass_queue_entry_pure(queue, reason)
    return {**updated, ACTION_QUEUE_KEY: queue}, None


def _apply_in_transaction(addon, updated: Mapping[str, Any], review_action: str | None) -> None:
    player_data = addon._state.player_data
    updated = addon.runtime_actions.drop_superseded_bank_run_requests_pure(player_data, dict(updated))
    # The running handler holds this dict, so it is refilled, never replaced.
    player_data.clear()
    player_data.update(updated)
    if review_action is not None:
        addon._select_review_action(review_action)
        addon.update_review_hud(player_data, addon._state.current_skill)


def _commit_run(addon, queue: dict[str, Any]) -> bool:
    """Run the queue's current entry as one undoable menu action."""
    review_action = None

    def _change(current):
        nonlocal review_action
        updated, review_action = _run_current_entry(addon, current, queue)
        return updated, True

    def _select():
        if review_action is not None:
            addon._select_review_action(review_action)

    committed = addon.commit_direct_action(_change, after_apply=_select)
    if committed:
        addon.update_review_hud(addon._state.player_data, addon._state.current_skill)
    return committed


def add_to_action_queue(addon, action: Mapping[str, Any], count: Any) -> bool:
    """Add an entry; an idle queue starts it at once. False when the queue refuses it."""
    queue = action_queue_pure(addon._state.player_data)
    idle = current_queue_entry_pure(queue) is None
    queue, ok = add_queue_entry_pure(queue, action, count)
    if not ok:
        return False
    if idle:
        return _commit_run(addon, queue)
    return addon.commit_direct_action(lambda current: ({**current, ACTION_QUEUE_KEY: queue}, True))


def clear_action_queue(addon) -> bool:
    """Empty the queue; the action running now carries on as an ordinary action."""
    return addon.commit_direct_action(lambda current: ({**current, ACTION_QUEUE_KEY: _empty_queue()}, True))


def resume_action_queue(addon) -> bool:
    """Continue a paused queue's current entry; False when no paused entry waits."""
    queue = action_queue_pure(addon._state.player_data)
    if not queue["paused"] or current_queue_entry_pure(queue) is None:
        return False
    return _commit_run(addon, {**queue, "paused": False})


def resume_action(addon) -> bool:
    """The Resume click: a paused queue continues the entry it stopped, else the last action restarts."""
    player_data = addon._state.player_data
    queue = action_queue_pure(player_data)
    entry = current_queue_entry_pure(queue)
    if (
        queue["paused"]
        and entry is not None
        and same_action_pure(saved_last_action_pure(player_data), entry["action"])
        and resume_button_view_pure(player_data, addon._state.current_skill)["visible"]
    ):
        return resume_action_queue(addon)
    return resume_last_action(addon)


def advance_action_queue(addon, before_player_data: Mapping[str, Any]) -> None:
    """After a review: add its progress to the current entry; a full entry starts the next.

    A review of any other action pauses the queue, because the player started
    that action himself.
    """
    player_data = addon._state.player_data
    queue = action_queue_pure(player_data)
    entry = current_queue_entry_pure(queue)
    if entry is None or queue["paused"]:
        return
    if not same_action_pure(last_action_record_pure(player_data, addon._state.current_skill), entry["action"]):
        player_data[ACTION_QUEUE_KEY] = {**queue, "paused": True}
        return
    progress = queue_entry_progress_pure(entry["action"], before_player_data, player_data)
    queue, full = advance_queue_pure(queue, progress)
    player_data[ACTION_QUEUE_KEY] = queue
    if not full:
        return
    done = f"{queue_entry_name_pure(entry['action'])} done"
    if current_queue_entry_pure(queue) is not None:
        updated, review_action = _run_current_entry(
            addon, record_review_event_pure(player_data, "activity", f"Queue: {done}"), queue
        )
        _apply_in_transaction(addon, updated, review_action)
        if review_action is not None:
            return
    addon._switch_to_bankstanding(f"The queue is finished: {done}.")


def _queue_takes_over_stop(addon, stopped: Mapping[str, Any], reason: str, *, automatic: bool) -> bool:
    """Whether the queue runs its next entry in place of this switch to Bankstanding.

    A manual Stop of the queue's entry pauses the queue and lets the switch
    happen. An automatic stop passes the entry with its reason, or as done for a
    quest that just completed, and starts the next entry; when no entry is left
    the switch happens, and its notice is the queue's last.
    """
    player_data = addon._state.player_data
    queue = action_queue_pure(player_data)
    entry = current_queue_entry_pure(queue)
    if entry is None or queue["paused"] or not same_action_pure(stopped, entry["action"]):
        return False
    if not automatic:
        player_data[ACTION_QUEUE_KEY] = {**queue, "paused": True}
        return False
    action = entry["action"]
    completed = action["kind"] == "quest" and quest_state_pure(player_data, action["quest_id"]).get("completed")
    name = queue_entry_name_pure(action)
    text = f"Queue: {name} done" if completed else f"Queue: {name} stopped · {reason}"
    queue = pass_queue_entry_pure(queue, "" if completed else reason)
    player_data[ACTION_QUEUE_KEY] = queue
    if current_queue_entry_pure(queue) is None:
        return False
    updated, review_action = _run_current_entry(addon, record_review_event_pure(player_data, "activity", text), queue)
    _apply_in_transaction(addon, updated, review_action)
    return review_action is not None


def record_bankstanding_stop(addon, reason: Any, *, automatic: bool) -> str | None:
    """Settle what a switch to Bankstanding stops; the reason it gives, or None when the queue runs on.

    Otherwise the stopped action becomes the last action, which Resume restarts.
    """
    player_data = addon._state.player_data
    stopped = last_action_record_pure(player_data, addon._state.current_skill)
    reason_text = str(reason or "").strip() or f"{last_action_name_pure(stopped) or 'Current action'} could not continue."
    if _queue_takes_over_stop(addon, stopped, reason_text, automatic=automatic):
        return None
    player_data[LAST_ACTION_KEY] = {**stopped, "reason": reason_text} if stopped else {}
    return reason_text
