"""The action queue: up to five actions that reviews work through once, top to bottom.

At 10x speed an action uses up its materials in a few cards, so the player
plans a chain such as mine, smelt, smith instead of restarting each step. An
entry is an action in the last-action record shape and a count in that
action's own unit: the product items it makes, the one item it uses when it
makes nothing (bones buried), kills for a fight, reviews for any other action,
and no count for a quest, which runs until it stops.

An entry makes its count (owner, Pass 18), and a whole lot stays whole: the queue
counts every step, the step that reaches the count makes only the remainder, and the rest of the
card goes to the next entry when that is a skill or utility; a fight or quest
starts on the next card, and a finished queue ends at Bankstanding. A review
count goes up once per card.

The queue holds only the entries still to run, the first one running (owner,
Pass 18): an entry that ends, done or stopped, leaves at once and frees its
place, and the Event log keeps its "Queue: <name> done" or stop line.

When an entry's action stops for a missing material or requirement, the queue
notes why and starts the next entry in place of the switch to Bankstanding;
only a finished queue lets that switch happen, with its usual notice. A manual
Stop on an entry pauses the queue; Resume continues its entry. A hand-started
action sets the plan aside until that action stops, then the top entry resumes.
Clear cancels the plan: it drops every entry and stops whatever runs, also an action the player started
by hand, and Resume offers that back.

Up and Down move an entry (owner, Pass 20). A new first entry in a running
queue starts at once, and the old one keeps only the count it still owes. A
paused or set-aside queue only changes its order: a pause holds until Resume,
and a hand-started action keeps running until it stops.

The ✕ removes any entry (owner, Pass 21). Removing the running first entry
starts the next one, or ends at Bankstanding when none is left; what that entry
already made stays. A paused or set-aside queue only changes its list.

An add means the player wants the plan to run (owner, Pass 19): a queue
that does not run its first entry, because it is new, paused, or put aside
for an action the player started by hand, starts that entry at once in place
of whatever runs.

The owner ruled out loops (2026-10-26): the queue never repeats and holds at
most five entries, so the player still plans his training.

Transitions inside a review or a menu action write the save directly, because
each tab's own setter would open a second undo step inside the running one.
"""

from __future__ import annotations

from typing import Any, Mapping
from uuid import uuid4

from .action_products import (
    action_product_items_pure,
    action_target_spec_pure,
    action_use_size_pure,
    action_used_input_pure,
    spec_field_pure,
)
from .action_registry import UTILITY_REVIEW_ACTION_DISPLAY_NAME, is_utility_review_action, review_action_handler_key
from .constants import QUEST_DATA
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
from .review_event_log import _answered_reviews_pure, record_review_event_pure
from ..logic.agility_logic import apply_agility_command_pure
from ..logic.inventory_pure import review_item_changes_pure
from ..logic_pure.logic_pure import quest_locked_reasons_pure, quest_state_pure

ACTION_QUEUE_KEY = "action_queue"
MAX_QUEUE_ENTRIES = 5
QUEUE_FULL_TEXT = "The queue is full."


def _empty_queue() -> dict[str, Any]:
    return {"entries": [], "done": 0, "paused": False, "suspended": False}


def action_queue_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """The saved queue, the entries still to run in order.

    An entry this game can no longer start is dropped, and so is each ended
    entry that a Pass 17 save kept before its ``index``.
    """
    raw = player_data.get(ACTION_QUEUE_KEY)
    if not isinstance(raw, Mapping):
        return _empty_queue()
    entries = []
    for entry in list(raw.get("entries") or ())[max(0, int(raw.get("index") or 0)):]:
        action = valid_action_record_pure(entry.get("action") if isinstance(entry, Mapping) else None)
        if action:
            entries.append({
                "action": action, "count": entry.get("count"),
                **({"wilderness_fingerprint": entry["wilderness_fingerprint"]} if entry.get("wilderness_fingerprint") else {}),
            })
    if not entries:
        return _empty_queue()
    return {
        "entries": entries[:MAX_QUEUE_ENTRIES],
        "done": max(0, int(raw.get("done") or 0)),
        "paused": bool(raw.get("paused")),
        "suspended": bool(raw.get("suspended")) and not bool(raw.get("paused")),
    }


def current_queue_entry_pure(queue: Mapping[str, Any]) -> dict[str, Any] | None:
    """The entry running now, the first; None for an empty queue."""
    return queue["entries"][0] if queue["entries"] else None


def add_queue_entry_pure(queue: Mapping[str, Any], action: Mapping[str, Any], count: Any) -> tuple[dict[str, Any], bool]:
    """Append an entry; a full queue, an unknown action or a count below one refuses.

    A quest takes no count. An empty queue starts a new plan.
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


def pass_queue_entry_pure(queue: Mapping[str, Any]) -> dict[str, Any]:
    """The queue without its first entry, which ended; the next entry starts from nothing."""
    return {**queue, "entries": queue["entries"][1:], "done": 0}


def advance_queue_pure(queue: Mapping[str, Any], progress: int) -> tuple[dict[str, Any], bool]:
    """Add progress up to the entry's count; True when that fills the entry and the next takes over."""
    entry = current_queue_entry_pure(queue)
    if entry is None or entry["count"] is None:
        return dict(queue), False
    done = min(queue["done"] + progress, entry["count"])
    if done < entry["count"]:
        return {**queue, "done": done}, False
    return pass_queue_entry_pure(queue), True


def remove_queue_entry_pure(queue: Mapping[str, Any], position: int) -> tuple[dict[str, Any], bool]:
    """Drop one entry; a position outside the queue refuses. A new first entry starts from nothing."""
    entries = list(queue["entries"])
    if not 0 <= position < len(entries):
        return dict(queue), False
    del entries[position]
    return {**queue, "entries": entries, "done": queue["done"] if position else 0}, True


def move_queue_entry_pure(queue: Mapping[str, Any], position: int, new_index: int) -> tuple[dict[str, Any], bool]:
    """Move one entry; a move off the end of the queue refuses.

    Progress lives once at queue level, so a move that changes the first entry
    leaves the old one owing only what it has left, and the new one starts from nothing.
    """
    entries = list(queue["entries"])
    if position == new_index or not (0 <= position < len(entries) and 0 <= new_index < len(entries)):
        return dict(queue), False
    done = queue["done"]
    if done and 0 in (position, new_index):
        entries[0] = {**entries[0], "count": entries[0]["count"] - done}
        done = 0
    entries.insert(new_index, entries.pop(position))
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


def _entry_line(action: Mapping[str, Any], reason: str | None = None) -> str:
    """An ended entry's Event log line: done, or stopped and why."""
    name = queue_entry_name_pure(action)
    return f"Queue: {name} done" if reason is None else f"Queue: {name} stopped · {reason}"


def _queue_entry_row(queue: Mapping[str, Any], position: int) -> dict[str, Any]:
    action = queue["entries"][position]["action"]
    current = position == 0
    return {
        "name": queue_entry_name_pure(action),
        "unit": queue_entry_unit_pure(action),
        "products": action_product_items_pure(action),
        "used": action_used_input_pure(action),
        "count": queue["entries"][position]["count"],
        "done": queue["done"] if current else 0,
        "state": "current" if current else "waiting",
    }


def action_queue_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """What a queue panel shows: each entry's name, unit, count, progress and state."""
    queue = action_queue_pure(player_data)
    rows = [_queue_entry_row(queue, position) for position in range(len(queue["entries"]))]
    return {
        "entries": rows,
        "paused": queue["paused"],
        "suspended": queue["suspended"],
    }


def queue_notice_view_pure(player_data: Mapping[str, Any], activity_lines=()) -> str:
    """The latest queue transition stays in the HUD until the next answered card or a queue change from the menu."""
    review = _answered_reviews_pure(player_data)
    text = next((
        row["text"] for row in reversed(player_data.get("review_event_log") or ())
        if row.get("kind") == "queue" and row.get("review") == review
    ), "")
    return " • ".join(filter(None, (text, *activity_lines)))


def _cleared_queue_notice_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """The save values of a queue change from the menu: this card's queue lines stay in the Event log and leave the HUD.

    A line such as "Next: Combat" names the entry that started then, so it can
    be wrong once the player changes the list.
    """
    review = _answered_reviews_pure(player_data)
    return {"review_event_log": [
        {**row, "kind": "activity"} if row.get("kind") == "queue" and row.get("review") == review else row
        for row in player_data.get("review_event_log") or ()
    ]}


def _record_queue_notice(addon, text: str, row=None) -> None:
    player_data = addon._state.player_data
    if row is None:
        player_data.update(record_review_event_pure(player_data, "queue", text))
    else:
        row.update(kind="queue", text=text[:500])


def runtime_notice_callbacks(addon):
    """One stop decision serves every handler: a continuing queue gets a line."""
    last_reason = {"text": "", "stop": None, "continued": False}

    def show_error(title, message, queue_message=None, detail=""):
        last_reason.update(text=str(message or "").strip(), caller_owns_notice=True)
        refine_stop_reason(addon, last_reason["stop"], last_reason["text"])
        if last_reason["continued"]:
            row = _ended_entry_row(addon)
            text = queue_message or (row["text"] if row else last_reason["text"])
            next_name = last_action_name_pure(last_action_record_pure(addon._state.player_data, addon._state.current_skill))
            _record_queue_notice(addon, f"{text.rstrip('.')}. Next: {next_name}." + (f" {detail}" if detail else ""), row)
            return True
        if addon._state.pending_bankstanding_notice is not None:
            addon._state.pending_bankstanding_notice["show_dialog"] = False
        addon.show_error_message(title, message)
        return False

    def switch(reason=None, *, caller_owns_notice=False):
        notice_owned = bool(caller_owns_notice or last_reason.get("caller_owns_notice"))
        reason = reason or last_reason["text"]
        last_reason["stop"] = None if reason else unexplained_stop_pure(addon._state.player_data, addon._state.current_skill)
        addon._switch_to_bankstanding(reason, caller_owns_notice=notice_owned)
        last_reason["continued"] = queue_runs_pure(addon._state.player_data, addon._state.current_skill)

    def show_gain(text):
        last_reason.update(text=str(text or "").strip(), caller_owns_notice=False)
        refine_stop_reason(addon, last_reason["stop"], last_reason["text"])
        addon._show_activity_gain(text)

    return show_error, switch, show_gain


def _entry_start_refusal(addon, current, entry) -> str:
    action = entry["action"]
    if action["kind"] != "combat":
        return ""
    runtime = addon.runtime_actions
    fingerprint = runtime.wilderness_combat_risk_fingerprint(
        current, action["target"], runtime.COMBAT_ENEMY_DATA.get(action["target"], {})
    )
    if fingerprint and fingerprint != entry.get("wilderness_fingerprint"):
        return "Wilderness equipment risk changed; confirm this target again."
    return ""


def _run_current_entry(addon, current: Mapping[str, Any], queue: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """The save that runs the queue's current entry, passing each entry that cannot start.

    The review action is None when no entry is left to run.
    """
    updated = dict(current)
    while (entry := current_queue_entry_pure(queue)) is not None:
        refusal = _entry_start_refusal(addon, updated, entry)
        started = None if refusal else start_values(addon, updated, entry["action"])
        if started is not None:
            return {**started[0], ACTION_QUEUE_KEY: queue}, started[1]
        updated = record_review_event_pure(updated, "queue", _entry_line(entry["action"], refusal or "it could not start"))
        queue = pass_queue_entry_pure(queue)
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


def _commit_queue(addon, queue: dict[str, Any], **commit_options: Any) -> bool:
    """Save a changed queue as one undoable menu action, with no change to what runs unless the options ask."""
    return addon.commit_direct_action(
        lambda current: ({**current, **_cleared_queue_notice_pure(current), ACTION_QUEUE_KEY: queue}, True),
        **commit_options,
    )


def _commit_run(addon, queue: dict[str, Any], no_entry_reason: str | None = None) -> bool:
    """Run the queue's current entry as one undoable menu action.

    When no entry can run, what runs now carries on, or with ``no_entry_reason`` stops for it at Bankstanding.
    """
    review_action = None

    def _change(current):
        nonlocal review_action
        updated, review_action = _run_current_entry(addon, {**current, **_cleared_queue_notice_pure(current)}, queue)
        return updated, True

    def _select():
        if review_action is not None:
            addon._select_review_action(review_action)
        elif no_entry_reason is not None:
            addon._switch_to_bankstanding(no_entry_reason, automatic=False)

    committed = addon.commit_direct_action(_change, after_apply=_select)
    if committed:
        refresh_review_hud(addon)
        addon.update_review_event_log_drawer(addon._state.player_data)
    return committed


def queue_runs_pure(player_data: Mapping[str, Any], current_skill: Any) -> bool:
    """Whether the queue runs its first entry now: it is not paused, and that entry is the selected action.

    A hand-started action sets the queue aside until that action stops.
    """
    queue = action_queue_pure(player_data)
    entry = current_queue_entry_pure(queue)
    return (
        entry is not None
        and not queue["paused"]
        and not queue["suspended"]
        and same_action_pure(last_action_record_pure(player_data, current_skill), entry["action"])
    )


def set_aside_action_queue(addon) -> None:
    """A hand start preserves a manual pause, or sets the running plan aside."""
    player_data = addon._state.player_data
    queue = action_queue_pure(player_data)
    if queue["entries"] and not queue["paused"] and not queue_runs_pure(player_data, addon._state.current_skill):
        player_data[ACTION_QUEUE_KEY] = {**queue, "suspended": True}


def queue_add_refusal_pure(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> str:
    """Why the queue refuses ``action`` now, one text per cause; empty when it takes it. The count is checked on add."""
    if not action:
        return "Nothing selected."
    if len(action_queue_pure(player_data)["entries"]) >= MAX_QUEUE_ENTRIES:
        return QUEUE_FULL_TEXT
    if not valid_action_record_pure(action):
        return "This action cannot be queued."
    if action["kind"] != "quest":
        return ""
    if quest_state_pure(player_data, action["quest_id"]).get("completed"):
        return "This quest is complete."
    locked = quest_locked_reasons_pure(player_data, action["quest_id"], QUEST_DATA)
    return "Requires: " + ", ".join(map(str, locked)) if locked else ""


def add_to_action_queue(addon, action: Mapping[str, Any], count: Any) -> str:
    """Add an entry; why the queue refused it, empty when it took it.

    A queue that does not run its first entry starts it now, as ``queue_runs_pure`` tells.
    """
    player_data = addon._state.player_data
    refusal = queue_add_refusal_pure(player_data, action)
    if refusal:
        return refusal
    runs = queue_runs_pure(player_data, addon._state.current_skill)
    queue, ok = add_queue_entry_pure(action_queue_pure(player_data), action, count)
    if not ok:
        # Every other cause was refused above.
        return "Type a count of 1 or more."
    if action["kind"] == "combat":
        if not addon.ui.confirm_wilderness_queue_action(player_data, action):
            return "Wilderness entry was not added."
        fingerprint = addon.runtime_actions.wilderness_combat_risk_fingerprint(
            player_data, action["target"], addon.runtime_actions.COMBAT_ENEMY_DATA.get(action["target"], {})
        )
        if fingerprint:
            queue["entries"][-1]["wilderness_fingerprint"] = fingerprint
    if runs:
        committed = _commit_queue(addon, queue)
    else:
        committed = _commit_run(addon, {**queue, "paused": False, "suspended": False})
        # The run passed every entry that could not start, the new one too, so the player's action runs on.
        if committed and current_queue_entry_pure(action_queue_pure(addon._state.player_data)) is None:
            return f"{queue_entry_name_pure(action)} could not start."
    return "" if committed else "Anki could not save the change. Try again."


def clear_action_queue(addon) -> bool:
    """Cancel the plan: drop every entry and stop whatever runs, with no dialog.

    An action the player started by hand stops too, so clearing the plan always
    stops the work (owner, Pass 18). What stopped lands at Bankstanding as the
    last action, so Resume offers it back.
    """
    return _commit_queue(
        addon, _empty_queue(), bankstanding_reason="The queue was cleared.", bankstanding_automatic=False
    )


def remove_action_queue_entry(addon, position: int, entry: Mapping[str, Any], expected_queue=None) -> bool:
    """Drop ``entry`` as one undoable menu action, starting the next entry when it was the one running.

    Leaving a minigame session first can already have passed ``entry``, so a
    position that holds another entry now refuses and that entry stays.
    """
    player_data = addon._state.player_data
    before = action_queue_pure(player_data)
    queue, ok = remove_queue_entry_pure(before, position)
    if expected_queue is not None and before != expected_queue:
        return False
    if not ok or before["entries"][position] != entry:
        return False
    if position == 0 and queue_runs_pure(player_data, addon._state.current_skill):
        return _commit_run(addon, queue, no_entry_reason="The queue is empty.")
    return _commit_queue(addon, queue)


def queue_move_takes_over_pure(player_data: Mapping[str, Any], current_skill: Any, position: int, new_index: int) -> bool:
    """Whether a move starts a new first entry at once: the queue runs, and the move changes that entry."""
    return 0 in (position, new_index) and queue_runs_pure(player_data, current_skill)


def move_action_queue_entry(addon, position: int, new_index: int) -> bool:
    """Move one entry as one undoable menu action, starting a new first entry when the queue runs."""
    player_data = addon._state.player_data
    queue, ok = move_queue_entry_pure(action_queue_pure(player_data), position, new_index)
    if not ok:
        return False
    if queue_move_takes_over_pure(player_data, addon._state.current_skill, position, new_index):
        return _commit_run(addon, queue)
    return _commit_queue(addon, queue)


def resume_action_queue(addon) -> bool:
    """Continue a paused or set-aside queue; False when it starts no entry.

    A paused entry restarts as Resume restarts any action: a refusal shows its
    tab's reason, starts nothing and leaves the queue paused.
    """
    queue = action_queue_pure(addon._state.player_data)
    entry = current_queue_entry_pure(queue)
    if not (queue["paused"] or queue["suspended"]) or entry is None:
        return False
    return start_action(addon, entry["action"], {
        **_cleared_queue_notice_pure(addon._state.player_data),
        ACTION_QUEUE_KEY: {**queue, "paused": False, "suspended": False},
    })


def apply_action_queue_command(addon, command: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    """Run a queue command from the main menu; the result names the review action running after it."""
    message = ""
    if command == "add":
        message = add_to_action_queue(addon, payload["action"], payload.get("count"))
        ok = not message
    elif command == "clear":
        ok = clear_action_queue(addon)
    elif command == "resume":
        ok = resume_action_queue(addon)
    elif command == "remove":
        ok = remove_action_queue_entry(addon, int(payload["position"]), payload["entry"], payload.get("expected_queue"))
    elif command == "move":
        ok = move_action_queue_entry(addon, int(payload["position"]), int(payload["new_index"]))
    else:
        raise ValueError(f"Unknown action queue command: {command!r}")
    refresh_review_hud(addon)
    return {"ok": ok, "active": addon._state.current_skill, "message": message}


def stop_action(addon) -> Any:
    """Stop the running action; return to a set-aside queue, otherwise to Bankstanding.

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
    A hand-started action runs without crediting any pending entry.
    """

    def __init__(self, addon) -> None:
        self.addon = addon
        self.full = self.stepped = False
        player_data = addon._state.player_data
        queue = action_queue_pure(player_data)
        self.entry, self.done, self.unit = current_queue_entry_pure(queue), queue["done"], ""
        # Entries never join during a card, so a shorter queue means this entry ended.
        self.left = len(queue["entries"])
        set_aside_action_queue(addon)
        if not queue_runs_pure(player_data, addon._state.current_skill):
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
        remainder = self.entry["count"] - self.done
        use_size = action_use_size_pure(action) if self.unit == "uses" else 0
        if remainder < use_size:
            used = action_used_input_pure(action)
            self.addon._switch_to_bankstanding(f"Only {remainder} {used} left to use; one action needs {use_size}.")
            return False
        before = {**player_data, "inventory": dict(player_data.get("inventory") or {})}
        ctx.queue_remainder, ctx.queue_use_size = remainder, use_size
        ctx.queue_wilderness_fingerprint = self.entry.get("wilderness_fingerprint", "")
        result = step(ctx)
        ctx.queue_remainder, ctx.queue_use_size = None, 0
        ctx.queue_wilderness_fingerprint = ""
        progress = queue_entry_progress_pure(action, before, player_data)
        self._credit(min(progress, remainder))
        return result

    def _credit(self, progress: int) -> None:
        """Add progress to the entry.

        A stop inside the step passed the entry as stopped before its progress
        came in; when that progress reached the count, its line reads done.
        """
        player_data = self.addon._state.player_data
        queue = action_queue_pure(player_data)
        self.done += progress
        if len(queue["entries"]) == self.left:
            player_data[ACTION_QUEUE_KEY], self.full = advance_queue_pure(queue, progress)
        elif self.done >= self.entry["count"] and (row := _ended_entry_row(self.addon)):
            row["text"] = _entry_line(self.entry["action"])

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
        name = queue_entry_name_pure(self.entry["action"])
        player_data = addon._state.player_data
        queue = action_queue_pure(player_data)
        review_action = None
        logged = record_review_event_pure(player_data, "queue", _entry_line(self.entry["action"]))
        player_data.update(logged)
        if current_queue_entry_pure(queue) is not None:
            updated, review_action = _run_current_entry(addon, logged, queue)
            _apply_in_transaction(addon, updated, review_action)
        if review_action is None:
            addon._switch_to_bankstanding(f"Queue finished after {name}.")
        addon._begin_review_feedback_context()
        return review_action is not None and review_action_handler_key(review_action) not in {
            "combat", *addon.runtime_actions.ONE_PER_CARD_HANDLER_KEYS
        }


def _remove_completed_quest(addon, queue: dict[str, Any], action: Mapping[str, Any]) -> tuple[dict[str, Any], bool]:
    """Completion removes every queued copy, even from a paused plan."""
    if action.get("kind") != "quest" or not quest_state_pure(addon._state.player_data, action["quest_id"]).get("completed"):
        return queue, False
    entries = [entry for entry in queue["entries"] if not same_action_pure(entry["action"], action)]
    if len(entries) != len(queue["entries"]):
        addon._state.player_data.update(record_review_event_pure(addon._state.player_data, "activity", _entry_line(action)))
    first_removed = bool(queue["entries"]) and same_action_pure(queue["entries"][0]["action"], action)
    return {**queue, "entries": entries, "done": 0 if first_removed else queue["done"]}, True


def _queue_takes_over_stop(addon, stopped: Mapping[str, Any], reason: str, *, automatic: bool) -> bool:
    """Return from a hand start, pause a manual Stop, or pass an ended entry."""
    player_data = addon._state.player_data
    queue = action_queue_pure(player_data)
    runs = queue_runs_pure(player_data, addon._state.current_skill)
    queue, completed = _remove_completed_quest(addon, queue, stopped)
    player_data[ACTION_QUEUE_KEY] = queue
    if queue["paused"]:
        return False
    if runs and not automatic:
        player_data[ACTION_QUEUE_KEY] = {**queue, "paused": True, "suspended": False}
        return False
    if runs and not completed:
        addon._state.ended_entry_line = uuid4().hex
        player_data.update(record_review_event_pure(
            player_data, "activity", _entry_line(stopped, reason), ref=addon._state.ended_entry_line
        ))
        queue = pass_queue_entry_pure(queue)
    queue = {**queue, "suspended": False}
    player_data[ACTION_QUEUE_KEY] = queue
    if current_queue_entry_pure(queue) is None:
        return False
    updated, review_action = _run_current_entry(addon, player_data, queue)
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
    addon._state.ended_entry_line = ""
    stopped = last_action_record_pure(player_data, addon._state.current_skill)
    reason_text = str(reason or "").strip() or generic_stop_reason_pure(player_data, addon._state.current_skill)
    if _queue_takes_over_stop(addon, stopped, reason_text, automatic=automatic):
        row = _ended_entry_row(addon)
        if row is not None:
            row["kind"] = "queue"
        return None
    player_data[LAST_ACTION_KEY] = {**stopped, "reason": reason_text} if stopped else {}
    return reason_text


def unexplained_stop_pure(player_data: Mapping[str, Any], current_skill: Any) -> dict[str, Any]:
    """A stop given no reason, as it starts: the generic reason it records and what it may replace.

    That is the queue's running entry, which it may end, and the last action it may write over.
    """
    queue = action_queue_pure(player_data)
    return {
        "reason": generic_stop_reason_pure(player_data, current_skill),
        "entry": current_queue_entry_pure(queue),
        "left": len(queue["entries"]),
        "last_action": player_data.get(LAST_ACTION_KEY),
    }


def refine_stop_reason(addon, stop: Mapping[str, Any] | None, reason: str) -> None:
    """Put the words a review shows after its ``stop`` where that stop wrote its generic reason.

    Most review handlers stop their action first and say why after, so the
    stop records a generic reason. The refusal's own words replace it in the
    Bankstanding notice and its log line, the last action that Resume shows,
    and the log line of the queue entry this stop ended; a last action or
    entry line an earlier stop wrote with the same words keeps them. ``stop`` is None
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
    _refine_ended_entry(addon, stop, reason)


def _refine_bankstanding_notice(notice: dict[str, Any] | None, player_data: dict[str, Any], reason: str) -> None:
    if notice is None:
        return
    notice["reason"] = reason
    event_log = player_data.get("review_event_log")
    if isinstance(event_log, list) and event_log and isinstance(event_log[-1], dict):
        event_log[-1]["text"] = bankstanding_event_text(reason)[:500]


def _refine_ended_entry(addon, stop: Mapping[str, Any], reason: str) -> None:
    """The log line of the entry ``stop`` ended takes ``reason``; a stop that ended none changes no line.

    A line that already took the words of the review's first refusal keeps them.
    """
    if stop["entry"] is None or len(action_queue_pure(addon._state.player_data)["entries"]) >= stop["left"]:
        return
    row = _ended_entry_row(addon)
    action = stop["entry"]["action"]
    if row is not None and row["text"] == _entry_line(action, stop["reason"]):
        row["text"] = _entry_line(action, reason)[:500]


def _ended_entry_row(addon) -> dict[str, Any] | None:
    """The Event log row of the queue entry the latest stop ended, which ``_queue_takes_over_stop`` wrote."""
    ref = addon._state.ended_entry_line
    if not ref:
        return None
    rows = addon._state.player_data.get("review_event_log") or ()
    return next((row for row in reversed(rows) if isinstance(row, dict) and row.get("ref") == ref), None)


def select_review_action(addon, skill, *, keep_encounter=False):
    selected_skill = addon._normalize_legacy_utility_skill(skill)
    changed = selected_skill != addon._state.current_skill
    if changed:
        addon._state.player_data.update(addon._restore_quest_equipment_pure(addon._state.player_data, force=True))
    if not keep_encounter and (changed or not addon.is_combat_review_action(selected_skill)):
        addon._state.player_data["combat_encounter"] = {}
    addon._state.current_skill = selected_skill
    set_aside_action_queue(addon)
    try:
        addon.mw.col.set_config("ankiscape_current_skill", addon._state.current_skill)
    except AttributeError:
        pass
    return changed
