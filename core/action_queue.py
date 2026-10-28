"""The action queue: up to five actions that reviews work through once, top to bottom.

At 10x speed an action uses up its materials in a few cards, so the player
plans a chain such as mine, smelt, smith instead of restarting each step. An
entry is an action in the last-action record shape and a count in that
action's own unit: the product items it makes, the one item it uses when it
makes nothing (bones buried), kills for a fight, reviews for any other action,
and no count for a quest, which runs until it stops.

An entry makes exactly its count (owner, Pass 18): the queue counts every step,
the step that reaches the count makes only the remainder, and the rest of the
card goes to the next entry when that is a skill or utility; a fight or quest
starts on the next card, and a finished queue ends at Bankstanding. A review
count goes up once per card.

When an entry's action stops for a missing material or requirement, the queue
notes why and starts the next entry in place of the switch to Bankstanding;
only a finished queue lets that switch happen, with its usual notice. A manual
Stop pauses the queue; Resume continues its entry. Clear cancels the plan: it
drops every entry and stops the entry the queue is running, which Resume
offers back.

A new plan never replaces an action the player started by hand: at
Bankstanding its first entry starts at once, otherwise the plan waits until
that action stops, or until the player starts it now.

The owner ruled out loops (2026-10-26): the queue never repeats and holds at
most five entries, so the player still plans his training.

Transitions inside a review or a menu action write the save directly, because
each tab's own setter would open a second undo step inside the running one.
"""

from __future__ import annotations

from typing import Any, Mapping

from .action_products import (
    action_product_items_pure,
    action_target_spec_pure,
    action_use_size_pure,
    action_used_input_pure,
    spec_field_pure,
)
from .action_registry import UTILITY_REVIEW_ACTION_DISPLAY_NAME, is_utility_review_action, review_action_handler_key
from .last_action import (
    LAST_ACTION_KEY,
    last_action_name_pure,
    last_action_record_pure,
    refresh_review_hud,
    resume_button_view_pure,
    resume_last_action,
    saved_last_action_pure,
    start_action,
    start_values,
    valid_action_record_pure,
)
from .review_event_log import record_review_event_pure
from ..logic.agility_logic import apply_agility_command_pure
from ..logic.inventory_pure import review_item_changes_pure
from ..logic_pure.logic_pure import quest_state_pure

ACTION_QUEUE_KEY = "action_queue"
MAX_QUEUE_ENTRIES = 5
QUEUE_FULL_TEXT = f"The queue holds {MAX_QUEUE_ENTRIES} entries. Clear it to plan again."


def _empty_queue() -> dict[str, Any]:
    return {"entries": [], "index": 0, "done": 0, "paused": False, "waiting": False}


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
        "waiting": bool(raw.get("waiting")),
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
    """Add progress up to the entry's count; True when that fills the entry and the next takes over."""
    entry = current_queue_entry_pure(queue)
    if entry is None or entry["count"] is None:
        return dict(queue), False
    done = min(queue["done"] + progress, entry["count"])
    if done < entry["count"]:
        return {**queue, "done": done}, False
    return pass_queue_entry_pure({**queue, "done": done}), True


def remove_queue_entry_pure(queue: Mapping[str, Any], position: int) -> tuple[dict[str, Any], bool]:
    """Drop one entry that is not running; the entry the queue runs now refuses."""
    entries = list(queue["entries"])
    running = position == queue["index"] and not (queue["paused"] or queue["waiting"])
    if not 0 <= position < len(entries) or running:
        return dict(queue), False
    del entries[position]
    if position < queue["index"]:
        return {**queue, "entries": entries, "index": queue["index"] - 1}, True
    done = 0 if position == queue["index"] else queue["done"]
    return {**queue, "entries": entries, "done": done}, True


def same_action_pure(first: Mapping[str, Any], second: Mapping[str, Any]) -> bool:
    """Whether two records name one action, whatever reason either stopped for."""
    return {k: v for k, v in first.items() if k != "reason"} == {
        k: v for k, v in second.items() if k != "reason"
    }


def queue_entry_unit_pure(action: Mapping[str, Any]) -> str:
    """What an entry counts: "items" (its products), "uses" (its one input), "kills", "reviews", or "" for a quest."""
    if action["kind"] == "quest":
        return ""
    if action["kind"] == "combat":
        return "kills"
    if action_product_items_pure(action):
        return "items"
    return "uses" if action_used_input_pure(action) else "reviews"


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
    if unit == "uses":
        return max(0, -review_item_changes_pure(before, after).get(action_used_input_pure(action), 0))
    return 1 if unit == "reviews" else 0


def queue_entry_name_pure(action: Mapping[str, Any]) -> str:
    """The action's name plus its target, so two Smithing entries read apart."""
    name = last_action_name_pure(action)
    target = spec_field_pure(action_target_spec_pure(action), "display_name")
    return f"{name}: {target}" if target else name


def _queue_entry_row(queue: Mapping[str, Any], position: int) -> dict[str, Any]:
    entry = queue["entries"][position]
    action = entry["action"]
    if position < queue["index"]:
        state, done = "stopped" if entry.get("stopped") else "done", entry.get("done", 0)
    else:
        state = "current" if position == queue["index"] else "waiting"
        done = queue["done"] if state == "current" else 0
    running = state == "current" and not (queue["paused"] or queue["waiting"])
    return {
        "name": queue_entry_name_pure(action),
        "unit": queue_entry_unit_pure(action),
        "products": action_product_items_pure(action),
        "used": action_used_input_pure(action),
        "count": entry["count"],
        "done": done,
        "state": state,
        "stopped": str(entry.get("stopped") or ""),
        "removable": not running,
    }


def action_queue_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """What a queue panel shows: each entry's name, unit, count, progress and state."""
    queue = action_queue_pure(player_data)
    rows = [_queue_entry_row(queue, position) for position in range(len(queue["entries"]))]
    finished = bool(rows) and current_queue_entry_pure(queue) is None
    return {
        "entries": rows,
        "paused": queue["paused"],
        "waiting": queue["waiting"] and not finished,
        "finished": finished,
        "can_add": finished or len(rows) < MAX_QUEUE_ENTRIES,
    }


def _run_current_entry(addon, current: Mapping[str, Any], queue: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """The save that runs the queue's current entry, passing each entry that cannot start.

    The review action is None when no entry is left to run.
    """
    updated = dict(current)
    while (entry := current_queue_entry_pure(queue)) is not None:
        started = start_values(addon, updated, entry["action"])
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
        refresh_review_hud(addon)
    return committed


def add_starts_now_pure(player_data: Mapping[str, Any], current_skill: Any) -> bool:
    """Whether an add starts its entry at once: no plan runs and the player is at Bankstanding.

    While an action the player started by hand runs, a new plan waits for it to stop.
    """
    return current_queue_entry_pure(action_queue_pure(player_data)) is None and not last_action_record_pure(
        player_data, current_skill
    )


def add_to_action_queue(addon, action: Mapping[str, Any], count: Any) -> bool:
    """Add an entry; False when the queue refuses it. A new plan starts or waits as ``add_starts_now_pure`` says."""
    player_data = addon._state.player_data
    starts_now = add_starts_now_pure(player_data, addon._state.current_skill)
    queue = action_queue_pure(player_data)
    idle = current_queue_entry_pure(queue) is None
    queue, ok = add_queue_entry_pure(queue, action, count)
    if not ok:
        return False
    if starts_now:
        return _commit_run(addon, queue)
    queue = {**queue, "waiting": queue["waiting"] or idle}
    return addon.commit_direct_action(lambda current: ({**current, ACTION_QUEUE_KEY: queue}, True))


def _runs_queue_entry(addon, queue: Mapping[str, Any]) -> bool:
    entry = current_queue_entry_pure(queue)
    running = last_action_record_pure(addon._state.player_data, addon._state.current_skill)
    return (
        entry is not None
        and not (queue["paused"] or queue["waiting"])
        and same_action_pure(running, entry["action"])
    )


def clear_action_queue(addon) -> bool:
    """Cancel the plan: drop every entry and stop the entry the queue is running.

    The stopped entry lands at Bankstanding as the last action, so Resume
    offers it back. An action the player started by hand is not the plan's,
    so it keeps running.
    """
    runs_entry = _runs_queue_entry(addon, action_queue_pure(addon._state.player_data))
    stop = {"bankstanding_reason": "The queue was cleared.", "bankstanding_automatic": False} if runs_entry else {}
    return addon.commit_direct_action(lambda current: ({**current, ACTION_QUEUE_KEY: _empty_queue()}, True), **stop)


def remove_action_queue_entry(addon, position: int) -> bool:
    """Drop one entry that is not running, as one undoable menu action."""
    queue, ok = remove_queue_entry_pure(action_queue_pure(addon._state.player_data), position)
    return ok and addon.commit_direct_action(lambda current: ({**current, ACTION_QUEUE_KEY: queue}, True))


def resume_action_queue(addon) -> bool:
    """Continue a paused queue, or start a waiting one now; False when neither starts an entry.

    A paused entry restarts as Resume restarts any action: a refusal shows its
    tab's reason, starts nothing and leaves the queue paused.
    """
    queue = action_queue_pure(addon._state.player_data)
    entry = current_queue_entry_pure(queue)
    if not (queue["paused"] or queue["waiting"]) or entry is None:
        return False
    if queue["waiting"]:
        return _commit_run(addon, {**queue, "paused": False, "waiting": False})
    return start_action(addon, entry["action"], {ACTION_QUEUE_KEY: {**queue, "paused": False}})


def apply_action_queue_command(addon, command: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    """Run a queue command from the main menu; the result names the review action running after it."""
    message = ""
    if command == "add":
        ok = add_to_action_queue(addon, payload["action"], payload.get("count"))
        if not ok:
            full = not action_queue_view_pure(addon._state.player_data)["can_add"]
            message = QUEUE_FULL_TEXT if full else "Type a count of 1 or more."
    elif command == "clear":
        ok = clear_action_queue(addon)
    elif command == "resume":
        ok = resume_action_queue(addon)
    elif command == "remove":
        ok = remove_action_queue_entry(addon, int(payload["position"]))
    else:
        raise ValueError(f"Unknown action queue command: {command!r}")
    refresh_review_hud(addon)
    return {"ok": ok, "active": addon._state.current_skill, "message": message}


def stop_action(addon) -> Any:
    """Stop the running action by hand and land on Bankstanding; the review action running after, or False.

    Stop training and a Bankstanding picked by hand both come here, so either
    saves what it stopped as the last action, which Resume offers back, and
    pauses a queue that ran it. At Bankstanding already nothing stops, so no
    Edit > Undo step is added that would undo nothing.
    """
    surface = addon._normalize_legacy_utility_skill(addon._state.current_skill)
    if surface == UTILITY_REVIEW_ACTION_DISPLAY_NAME and addon._state.player_data.get("current_utility") == "bankstanding":
        return addon._state.current_skill

    def _change(current):
        updated = current
        if (
            addon._state.current_skill == "Agility"
            and current.get("current_agility") == "brimhaven_arena"
            and (current.get("agility_activity_state") or {}).get("brimhaven")
        ):
            updated, result = apply_agility_command_pure(current, "abandon", {}, roll=0.5)
            if not result.get("allowed"):
                return current, False
        updated = dict(updated)
        updated["current_utility"] = "bankstanding"
        updated["combat_encounter"] = {}
        return updated, True

    return addon.commit_direct_action(
        _change,
        bankstanding_reason="Training was stopped manually.",
        bankstanding_automatic=False,
    ) and addon._state.current_skill


def select_utility_target(addon, activity_id: str) -> Any:
    """A utility list's pick: Bankstanding picked while a utility runs stops it, else the pick waits for Start."""
    if activity_id == "bankstanding" and is_utility_review_action(addon._state.current_skill):
        return stop_action(addon)
    return addon._set_value("current_utility", activity_id)


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


class QueueCount:
    """The queue's count of one card's steps on its running entry.

    Each step of an entry that counts items, uses or kills learns what the entry
    still needs. A step that can only make a whole lot (15 arrow shafts from a log)
    keeps the whole lot: 2012 never made part of one, and taking products back
    after the inputs were spent would lose what the player paid for.
    A full entry stops the card's steps, and ``hand_over`` starts the next entry.
    A queue whose running entry is not the selected action pauses, because the
    player started that action himself; a plan that waits is left waiting.
    """

    def __init__(self, addon) -> None:
        self.addon = addon
        self.full = self.stepped = False
        player_data = addon._state.player_data
        queue = action_queue_pure(player_data)
        self.entry, self.position, self.unit = current_queue_entry_pure(queue), queue["index"], ""
        if self.entry is None or queue["paused"] or queue["waiting"]:
            self.entry = None
        elif not same_action_pure(last_action_record_pure(player_data, addon._state.current_skill), self.entry["action"]):
            player_data[ACTION_QUEUE_KEY] = {**queue, "paused": True}
            self.entry = None
        else:
            self.unit = queue_entry_unit_pure(self.entry["action"])

    def counted(self, step):
        """``step``, counted on the running entry."""
        def _counted(ctx):
            self.stepped = True
            return self._counted_step(ctx, step) if self.unit in ("items", "uses", "kills") else step(ctx)
        return _counted

    def _counted_step(self, ctx, step):
        player_data = self.addon._state.player_data
        action = self.entry["action"]
        remainder = self.entry["count"] - action_queue_pure(player_data)["done"]
        use_size = action_use_size_pure(action) if self.unit == "uses" else 0
        if remainder < use_size:
            used = action_used_input_pure(action)
            self.addon._switch_to_bankstanding(f"One action uses {use_size} {used}, and the count has only {remainder} left.")
            return False
        before = {**player_data, "inventory": dict(player_data.get("inventory") or {})}
        ctx.queue_remainder, ctx.queue_use_size = remainder, use_size
        result = step(ctx)
        ctx.queue_remainder, ctx.queue_use_size = None, 0
        progress = queue_entry_progress_pure(action, before, player_data)
        self._credit(min(progress, remainder))
        return result

    def _credit(self, progress: int) -> None:
        """Add progress to the entry; when a stop inside the step passed it, the passed entry takes it."""
        player_data = self.addon._state.player_data
        queue = action_queue_pure(player_data)
        if queue["index"] == self.position:
            queue, self.full = advance_queue_pure(queue, progress)
        else:
            entries = list(queue["entries"])
            entries[self.position] = {**entries[self.position], "done": entries[self.position].get("done", 0) + progress}
            queue = {**queue, "entries": entries}
        player_data[ACTION_QUEUE_KEY] = queue

    def hand_over(self) -> bool:
        """After the card's steps: count a review entry's card, and start the next entry after a full one.

        True when the next entry takes the rest of the card. A fight, quest or
        Dungeoneering room starts on the next card, and a finished queue
        switches to Bankstanding, which ends the card. The full entry's feedback shows first, so its lines
        come before the queue's.
        """
        if self.unit == "reviews" and self.stepped:
            self._credit(1)
        if not self.full:
            return False
        addon = self.addon
        addon._finish_review_feedback_context()
        done = f"{queue_entry_name_pure(self.entry['action'])} done"
        player_data = addon._state.player_data
        queue = action_queue_pure(player_data)
        review_action = None
        if current_queue_entry_pure(queue) is not None:
            logged = record_review_event_pure(player_data, "activity", f"Queue: {done}")
            updated, review_action = _run_current_entry(addon, logged, queue)
            _apply_in_transaction(addon, updated, review_action)
        if review_action is None:
            addon._switch_to_bankstanding(f"The queue is finished: {done}.")
        addon._begin_review_feedback_context()
        return review_action is not None and review_action_handler_key(review_action) not in {
            "combat", *addon.runtime_actions.ONE_PER_CARD_HANDLER_KEYS
        }


def _queue_takes_over_stop(addon, stopped: Mapping[str, Any], reason: str, *, automatic: bool) -> bool:
    """Whether the queue runs its next entry in place of this switch to Bankstanding.

    A manual Stop of the queue's entry pauses the queue and lets the switch
    happen. An automatic stop passes the entry with its reason, or as done for a
    quest that just completed, and starts the next entry; when no entry is left
    the switch happens, and its notice is the queue's last. A plan that waited
    for a hand-started action starts as that action stops, for any reason.
    """
    player_data = addon._state.player_data
    queue = action_queue_pure(player_data)
    entry = current_queue_entry_pure(queue)
    if entry is not None and queue["waiting"]:
        return _start_waiting_plan(addon, stopped, queue)
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


def _start_waiting_plan(addon, stopped: Mapping[str, Any], queue: Mapping[str, Any]) -> bool:
    text = f"Queue: {last_action_name_pure(stopped) or 'The action'} stopped, so the plan starts"
    updated, review_action = _run_current_entry(
        addon, record_review_event_pure(addon._state.player_data, "activity", text), {**queue, "waiting": False}
    )
    _apply_in_transaction(addon, updated, review_action)
    return review_action is not None


def bankstanding_event_text(reason: str) -> str:
    return f"Switched to Bankstanding · {reason}"


def generic_stop_reason_pure(player_data: Mapping[str, Any], current_skill: Any) -> str:
    """The reason a stop of the running action records when it was given none."""
    stopped = last_action_record_pure(player_data, current_skill)
    return f"{last_action_name_pure(stopped) or 'Current action'} could not continue."


def record_bankstanding_stop(addon, reason: Any, *, automatic: bool) -> str | None:
    """Settle what a switch to Bankstanding stops; the reason it gives, or None when the queue runs on.

    Otherwise the stopped action becomes the last action, which Resume restarts.
    """
    player_data = addon._state.player_data
    stopped = last_action_record_pure(player_data, addon._state.current_skill)
    reason_text = str(reason or "").strip() or generic_stop_reason_pure(player_data, addon._state.current_skill)
    if _queue_takes_over_stop(addon, stopped, reason_text, automatic=automatic):
        return None
    player_data[LAST_ACTION_KEY] = {**stopped, "reason": reason_text} if stopped else {}
    return reason_text


def unexplained_stop_pure(player_data: Mapping[str, Any], current_skill: Any) -> dict[str, Any]:
    """A stop given no reason, as it starts: the generic reason it records and what it may replace.

    That is the queue position whose entry it may pass and the last action it may write over.
    """
    return {
        "reason": generic_stop_reason_pure(player_data, current_skill),
        "position": action_queue_pure(player_data)["index"],
        "last_action": player_data.get(LAST_ACTION_KEY),
    }


def refine_stop_reason(addon, stop: Mapping[str, Any] | None, reason: str) -> None:
    """Put the words a review shows after its ``stop`` where that stop wrote its generic reason.

    Most review handlers stop their action first and say why after, so the
    stop records a generic reason. The refusal's own words replace it in the
    Bankstanding notice and its log line, the last action that Resume shows,
    and the queue entry this stop passed with its log line; a last action or
    entry an earlier stop wrote with the same words keeps them. ``stop`` is None
    when the handler stopped nothing or gave its stop a reason; only a pending
    notice takes the new words then.
    """
    reason = str(reason or "").strip()
    if not reason:
        return
    player_data = addon._state.player_data
    _refine_bankstanding_notice(addon._state.pending_bankstanding_notice, player_data, reason)
    if stop is None:
        return
    record = player_data.get(LAST_ACTION_KEY)
    # The stop saves a new record whenever it records one, so the record held
    # before it, even one with equal words, belongs to an earlier stop.
    if record is not stop["last_action"] and isinstance(record, dict) and record.get("reason") == stop["reason"]:
        player_data[LAST_ACTION_KEY] = {**record, "reason": reason}
    _refine_passed_entry(player_data, stop, reason)


def _refine_bankstanding_notice(notice: dict[str, Any] | None, player_data: dict[str, Any], reason: str) -> None:
    if notice is None:
        return
    notice["reason"] = reason
    event_log = player_data.get("review_event_log")
    if isinstance(event_log, list) and event_log and isinstance(event_log[-1], dict):
        event_log[-1]["text"] = bankstanding_event_text(reason)[:500]


def _refine_passed_entry(player_data: dict[str, Any], stop: Mapping[str, Any], reason: str) -> None:
    """The entry ``stop`` passed, and its log line, take ``reason``; a stop that passed none changes no entry.

    An older entry passed with the same generic words belongs to an earlier stop.
    """
    queue = action_queue_pure(player_data)
    position, generic = stop["position"], stop["reason"]
    if position >= queue["index"] or queue["entries"][position].get("stopped") != generic:
        return
    entries = list(queue["entries"])
    entries[position] = {**entries[position], "stopped": reason}
    player_data[ACTION_QUEUE_KEY] = {**queue, "entries": entries}
    line = f"Queue: {queue_entry_name_pure(entries[position]['action'])} stopped · "
    for row in reversed(player_data.get("review_event_log") or ()):
        if isinstance(row, dict) and row.get("text") == line + generic:
            row["text"] = (line + reason)[:500]
            break
