# Spec: Anki Redo restores the review rewards that Undo retracted

Status: ready for implementation after the owner answers the open questions.
Source: the owner accepted this idea on 2026-09-19 (kanban card "Upstream
ideas from AnkiScape 3.0 — 2026-09-19"). Priority matrix row 5 sends it
straight to spec. Written 2026-09-25 against main `d0904603`.

## 1. Problem

A player answers a card and gets experience points (XP), items, and
world-clock progress. The player presses Undo. AnkiScape takes back the
rewards. The player presses Redo. Anki puts the answer back, but the rewards
do not come back.

The real problem is larger than the kanban card says. Today, Anki Redo is not
available at all after an AnkiScape undo. The undo handler writes the save to
collection config. Every non-undoable config write empties Anki's redo queue.
A probe on Anki 25.09.4 (the `.venv-qt` build) shows this:

| Step on a disposable collection | `col.undo_status().redo` |
| --- | --- |
| Answer a card, then `col.undo()` | `Answer Card` |
| `SELECT 1 FROM revlog WHERE id = ?` | `Answer Card` |
| `col.set_config("ankiscape_player_data", ...)` | empty |

The Anki source agrees. `set_config_json` with `undoable=False` uses
`Op::SkipUndo`. `UndoManager::begin_step` clears `redo_steps` for every
operation in normal mode (`rslib/src/undo/mod.rs`, ankitects/anki
`1f7c8d7c`). The direct-action undo has the same effect.

## 2. What the player gets

- After Undo of an answer, Edit > Redo stays available, as in plain Anki.
- Redo gives back exactly the rewards that Undo took: the same XP, items,
  drops, level, achievements, event-log lines, action, and random state.
- Redo never rolls again. A redo cannot turn a bad drop into a good drop.
- Undo after Redo takes the rewards back again. The player can go back and
  forth as many times as Anki allows.

## 3. Facts the design depends on

1. Review undo today. `on_answer_card` in `__init__.py` pushes one diff
   snapshot per answer onto `_state.review_undo_stack` (limit 30). The
   snapshot holds the old values of changed `player_data` keys, the keys the
   answer added, `current_skill`, and the Python `random` state.
   `_on_state_did_undo` pops it when the undone operation is named
   `Answer Card`. `_restore_review_award_snapshot` applies it and calls
   `save_player_data()`.
2. The save lives in collection config: `ankiscape_player_data` and
   `ankiscape_current_skill` (`core/storage.py`).
3. Anki Redo puts back the same revlog row with the same `id`
   (`UndoableRevlogChange::Removed` in `rslib/src/revlog/undo.rs`). The probe
   confirms this. The revlog `id` is therefore a stable identity for one answer
   across undo and redo.
4. Anki has no redo hook. After Redo, aqt calls `update_undo_actions`
   (`undo_state_did_change`) and then `operation_did_execute`. After Undo, aqt
   calls `state_did_undo` first, then the same two hooks
   (`qt/aqt/operations/__init__.py`, `on_op_finished`).
5. A `SELECT` through `mw.col.db` does not touch the undo or redo queue. Any
   other statement through `mw.col.db` empties both queues
   (`rslib/src/backend/dbproxy.rs`, `is_dql`).
6. Anki keeps at most 30 undo steps (`UNDO_LIMIT`). Anki's undo and redo
   queues live in memory only. A profile close or a restart loses them.

Upstream learned fact 3 first. Upstream `evolved/engine.py` `reconcile_undo`
(wilsonhyeh/ankiscape `97b79fbc`) checks revlog row presence after each
operation: a missing row retracts, a row that comes back restores. Upstream
keeps its save outside the collection, so its writes never empty the redo
queue. This fork cannot copy that part while the save stays in collection
config.

## 4. Exact behaviour

### 4.1 Tag each review snapshot with its revlog row

1. In `on_answer_card`, before the wrapped `_old` call starts the answer
   operation, read the revlog ids of the card with one `SELECT`. Record the
   card id and these ids in the snapshot.
2. In `reviewer_did_answer_card`, read the revlog ids of the same card again
   with one `SELECT`. The new row is the id that the second read has and the
   first read does not have.
3. Attach that id to the top snapshot when all of these are true:
   - the card ids match;
   - the snapshot has no revlog id yet;
   - exactly one new id exists.
4. In all other cases, leave the snapshot without a revlog id. That answer
   can still be undone as today. It cannot be redone.

Do not use the greatest revlog id of the card. Anki makes the id of a new
row from the desktop clock (`answered_at_millis=int_time(1000)` in
`anki/scheduler/v3.py`). A phone review of the same card can have a later
clock time, and thus a greater id than the new desktop row.

The answer operation runs in the background, so its revlog row does not
exist when `on_answer_card` returns. The next answer cannot start before
`reviewer_did_answer_card` runs, so step 3 always tags the correct snapshot.
The review-log catch-up spec uses the same new-row id (its section 5.6).

### 4.2 Review Undo

When `state_did_undo` reports `Answer Card`:

1. Read the top review snapshot. If it has no revlog id, pop it, as today.
   If it has a revlog id, read that row with one `SELECT`. If the row is
   still present, the undone answer made no snapshot. Leave the snapshot on
   the stack and stop. If the row is absent, pop the snapshot.
2. If the popped snapshot has a revlog id, make a redo entry. The entry
   holds:
   - the snapshot itself;
   - the current value (or absence) of every key the snapshot will change;
   - the current `current_skill`;
   - the current random state.

   These current values are the "after" state that the undo removes.
3. Restore the snapshot, as today.
4. If step 2 made a redo entry, push it onto a new in-memory
   `review_redo_stack` (limit 30) and do not write the save now. Mark the save
   as "undo not yet written".
5. If step 2 made no redo entry, write the save at once, as today.

### 4.3 When the held undo gets written

The in-memory save is the truth while "undo not yet written" is set. The
game writes it, and clears `review_redo_stack`, at the first of these:

1. Any other game-save write, that is, a write of `ankiscape_player_data` or
   `ankiscape_current_skill` through `save_player_data`. That one function
   clears the redo stack. A new answer and a direct action are both in this
   group.
2. `undo_state_did_change` or `operation_did_execute`, when section 4.4 did
   not redo an answer on that hook and `col.undo_status().redo` is empty.
   Anki then has no redo step of any kind, so no held state can come back.
   This rule also applies when `review_redo_stack` is already empty.
3. `sync_will_start`. The collection must not upload a save that still holds
   undone rewards.
4. `profile_will_close`. Write the held save, then clear `review_undo_stack`
   and `review_redo_stack`. Anki's undo and redo queues die with the
   collection, so no snapshot of this profile can pair with the next
   profile's history.

The save export in `memory-bank/specs/save-export-restore.md` is not a
flush event. It reads the in-memory save, which already holds the undone
state, and it writes no config.

The game writes the held save only when Anki's whole redo queue is empty.
Each game write empties that queue. Thus a write when only
`review_redo_stack` is empty would destroy the Anki redo steps of other
operations, for example a note edit.

The add-on's other config writes do not flush. These writes call
`set_config` directly:

- the Review heads-up display (HUD) toggle in `ui/ui.py`;
- the Stats skill choice in `ui/ui.py`;
- developer mode in `ui/ui.py`;
- the review-action multiplier in `ui/ui.py`;
- the Smith, Craft, and Activity collapse keys in `ui/ui.py`;
- the floating HUD keys;
- the `ankiscape_current_skill` writes in `initialize_skill`,
  `_select_review_action`, and `_restore_direct_action_snapshot` in
  `__init__.py`.

Each of these writes empties Anki's redo queue. None of them runs a
collection operation, so no hook fires. The redo is then gone, and rule 2
flushes at the next operation. The only cost is the crash window of
question 1. A single choke point for all config writes is out of scope. It
touches about 15 call sites, and the save relocation removes the need for
it.

### 4.4 How the game notices Anki Redo

On every `undo_state_did_change` and every `operation_did_execute`, if
`review_redo_stack` is not empty, do this before rule 4.3.2:

1. Read the top entry's revlog id with one `SELECT`.
2. If the row is present, Anki has redone that answer. Apply section 4.5.
   Do not apply rule 4.3.2 on this hook.
3. If the row is absent, go to rule 4.3.2.

The order is necessary. After an operation, aqt fires
`undo_state_did_change` before `operation_did_execute` (fact 4). After a
redo takes the last redo step, `col.undo_status().redo` is already empty (a
probe on Anki 25.09.4 confirms this). A flush that ran first would destroy
the entry of the most common case, one Undo and one Redo. Detection on both
hooks is safe to repeat. After 4.5 pops the entry, the second hook sees the
next entry or an empty stack. The row of the next entry is still absent.

Only the top entry needs a test. Anki redoes in last-in, first-out order, so
a deeper answer cannot come back before the top one. This catches Redo from
the main window, the Browser, and the keyboard shortcut, because all of them
run a collection operation.

### 4.5 Review Redo

1. Pop the top redo entry.
2. Compare the live state with the state that the undo wrote. Every key the
   entry changes must hold the value the undo wrote (or be absent if the undo
   removed it). `current_skill` must equal the value the undo wrote.
3. If all values match, write the "after" values into the in-memory save.
   Remove the keys that were absent before the undo. Set `current_skill` and
   the random state from the entry.
4. Push the original snapshot back onto `review_undo_stack`. Undo after Redo
   then works with no new capture.
5. Refresh the same surfaces that `_restore_review_award_snapshot` refreshes.
   Show no XP popup, level-up dialog, achievement dialog, or bankstanding
   dialog. The original answer already showed them.
6. Keep holding the save. Rule 4.3.2 writes it when Anki's redo queue is
   empty. Do not write it only because `review_redo_stack` is empty.
7. If step 2 finds a difference, do not restore. Clear
   `review_redo_stack` and apply the owner's answer to question 3. Keep
   holding the save, as in step 6, because a write now would also remove
   the other redo steps in Anki's queue.

Do not compare the random state in step 2. Other code in the process can use
`random`. The redo sets the random state from the entry anyway.

### 4.6 Independence from direct-action undo

- Redo never reads or changes `direct_action_undo_stack`.
- Direct-action undo keeps its immediate write. That write empties Anki's
  redo queue, so a direct action cannot be redone. This is the current
  behaviour; this spec makes it a rule.
- A direct action after a review undo writes the save through
  `commit_direct_action`. Rule 4.3.1 clears the review redo stack. Anki also
  empties its own redo queue because of the custom undo entry.
- Anki undo is last-in, first-out across both kinds. A review redo can only
  run when no direct action happened after the matching undo.

### 4.7 Edge cases

| Case | Result |
| --- | --- |
| Undo, then answer the same card again | Normal answer. Anki empties redo; 4.3.1 clears the game redo stack. The restored random state gives the same rolls, as today. |
| Undo two answers, redo one, answer a new card | The new answer writes the save and clears the one remaining redo entry. |
| Undo, then undo a note edit, then Redo twice | Redo order is: the edit first, then the answer (Anki redoes the most recently undone step first; probe on 25.09.4). On the edit redo, the top entry's row is absent and Anki's redo queue is not empty, so nothing happens. On the answer redo, the row is present and 4.5 runs. |
| Answer, edit a note, undo the edit, undo the answer, redo the answer | After the answer redo, `review_redo_stack` is empty, but Anki still holds the note edit for Redo. The game does not write (4.5.6). Redo of the edit stays available. The save is written when Anki's redo queue becomes empty (4.3.2), or at another flush event. |
| Undo, then edit or delete a card | A normal operation empties Anki redo. 4.3.2 writes the save. |
| Undo, then Check Database or any raw `mw.col.db` write | Anki empties both queues. 4.3.2 writes the save. |
| Undo, then another add-on writes config | Anki empties redo. The next `undo_state_did_change` or game write flushes. |
| Undo, then the player changes an AnkiScape setting or switches skill | The direct `set_config` empties Anki redo, so the redo ends with no message, as in plain Anki after any config change. The held save flushes at the next hook or game write (end of 4.3). A crash in that window is the question 1 window. |
| Undo, then sync | 4.3.3 writes first. Sync then runs as normal. |
| Reviews synced from AnkiMobile or AnkiDroid | They never enter the desktop undo queue. No change. |
| Undo, then profile switch or quit | 4.3.4 writes and clears both review stacks. The new profile starts with empty review undo and redo stacks. |
| Anki crashes after Undo, before any write | The save on disk still holds the undone rewards. See question 1. |
| Collection restore from a backup taken in that window | Same as the crash case. |
| An answer whose snapshot has no revlog id | Undo works as today and writes the save at once (4.2.5). That write empties Anki's redo queue, so Redo is not available for that answer, as today. |
| A phone review of the same card has an id after the desktop clock | 4.1 tags the new desktop row, not the greatest id. Undo and Redo work as for any answer. |
| Answer undone in the Browser, redone in the main window | Works. Detection uses revlog rows, not the window. |

## 5. Data

| Data | Read or write | Why it is authoritative |
| --- | --- | --- |
| `revlog.id` of the answered card | Read, `SELECT` only | Anki removes it on Undo and puts back the same id on Redo. |
| `col.undo_status().redo` | Read | Anki's own statement of whether a redo can still happen. |
| `ankiscape_player_data`, `ankiscape_current_skill` | Write, delayed as in 4.3 | The save. No new config keys. |
| `review_undo_stack`, new `review_redo_stack` | Memory only | They match Anki's queues, which are also memory only. |

The save format does not change. No config version bump is necessary.

## 6. It must never

- Roll again, or call a skill handler, on Redo.
- Write the game save between a review undo and its possible redo, except for
  the flush events in 4.3. (A settings write by the player ends the redo, as
  in plain Anki; see the end of 4.3.)
- Write to the database with anything other than `SELECT`.
- Touch `direct_action_undo_stack` from review undo or redo code.
- Restore rewards for a revlog row that is not present.
- Show new dialogs or popups on Redo.

## 7. Verification

End-to-end tests come first. Each run leaves a JSON trace with the seed, the
steps, and the save hash after each step, under `memory-bank/evidence/`.

1. Medium scenario, real `anki.collection.Collection` in `.venv-qt`, with a
   driver that fires the hooks in aqt's order (fact 4). Answer three cards
   with Woodcutting. Undo three times. Redo three times. The save and the
   random state must equal the state after the third answer, byte for byte.
   `col.undo_status().redo` must be non-empty after each undo. Then run the
   single case: answer one card, undo once, redo once. The save must equal
   the save after the answer.
2. High scenario, same harness, with five runs.
   - Run 1: answer, direct action, answer. Undo twice (the second answer and
     the direct action). Answer again. Redo must not be available. The next
     Undo must retract the new answer. The Undo after that must retract the
     first answer. A step must not apply the undone direct action again.
   - Run 2: answer, undo, toggle the Review HUD setting, then run a note edit.
     Redo must not be available. The save must be written with the undone
     state after the note edit.
   - Run 3: answer, edit a note, undo the edit, undo the answer, redo the
     answer. The save must not be written yet, and Redo of the note edit must
     be available. Redo the edit. The save must then be written with the
     answer's rewards.
   - Run 4: before the answer, insert a revlog row for the same card. Give
     it an id one hour after the desktop clock, as a phone with a fast clock
     makes. Answer, undo, redo. The snapshot must hold the id of the new
     desktop row, not the greater phone id. The redo must restore the
     rewards.
   - Run 5: answer card A with Woodcutting. Answer card B, but do not fire
     the show-answer hook first, so that the add-on does not process the
     answer and makes no snapshot. Undo B. A's snapshot must stay on the
     stack, and the save must not change. Undo A. The save must equal the
     save before A.
3. Monte Carlo, same harness, 500 seeded sequences of 30 steps. Each step
   is one of: answer, undo, redo, direct action, note edit, AnkiScape
   setting write, skill switch, sync start, profile close and reopen. Do a
   check of these invariants after each step and its hooks:
   - The in-memory save equals the save that the run recorded at the same
     point in Anki's undo history.
   - When "undo not yet written" is clear, the saved config equals the
     in-memory save.
   - After a step that fires `undo_state_did_change`, and after a game save
     write, do a check of Anki's redo queue. If it is empty, then
     `review_redo_stack` must be empty and "undo not yet written" must be
     clear. A
     setting write and a skill switch fire no hook. For them, this check
     waits for the next step that fires one (end of 4.3).
4. Native check on the laptop test host, per `memory-bank/remote-test-host.md`,
   on a disposable collection. Answer until a level-up. Press Undo. Edit >
   Redo must be enabled. Press Redo. The HUD must show the level and XP
   again with no second level-up dialog. Record screenshots and the save
   hash before and after.
5. Lean unit tests only for the pure parts: building the redo entry from a
   snapshot and the live save, and the conflict comparison in 4.5.2.

## 8. Dependencies

- Save relocation (owner-gated, grill pending). If the save moves out of
  collection config, game writes no longer empty Anki's redo queue. Section
  4.3 then goes away and the undo write happens at once. Redo does not need
  to wait for that decision.
- Review-log catch-up spec. Its credit counts ride the review snapshot, so
  Redo gives back the count with the rewards, and catch-up does not credit
  the redone row again. Both specs use the new-row id of 4.1.
- `memory-bank/specs/save-export-restore.md`. Export reads the in-memory
  save and writes no config, so a held undo and Anki's Redo stay (4.3).
- The "one dialog for a multi-level gain" check. Redo shows no dialogs, so it
  adds no new dialog path.

## 9. Open questions for the owner

1. A crash between Undo and the next write leaves the undone rewards in the
   save. Accept that window? Recommended: yes. It needs a crash in a short
   window, and the save relocation removes it. A side file to close it now
   would be a second save store that the relocation would delete.
2. Should Redo show any game feedback? Recommended: no. Anki already shows
   "Redo Answer Card", and the HUD updates. Undo shows no feedback either.
3. If the state changed between Undo and Redo (4.5.7), what does the player
   see? Recommended: one review event log line that says the redo did not
   restore the rewards. The text goes through the project's copy route. No
   new surface is needed, so no frontend-taste review applies. The case
   needs an in-memory change with no write, which no known path makes.
4. Today, Undo of any `Answer Card` pops the top snapshot, even if that
   snapshot belongs to a different answer. An answer that the add-on does
   not process makes no snapshot (`review_answered` is false in
   `on_answer_card`, `__init__.py:5690`). Its undo pops the snapshot of the
   answer before it.

   Section 4.2.1 matches by revlog id: it pops a tagged snapshot only when
   its row is absent. Accept that change? Recommended: yes, in the same change. Redo pairs on
   the same id, and a wrong pop would also make a wrong redo entry.

   A top snapshot with no revlog id (4.1.3) keeps today's positional pop, so
   undo of those answers does not change. No snapshot from before this
   change can exist, because the stacks are in memory and the change loads
   only after a restart.

## 10. Conflicts and findings

- Conflict: `memory-bank/systemPatterns.md` line 548 says review undo
  "restores those values and saves config". This spec delays the write
  (4.2.4). The owner must accept that change; update the line when it lands.
- Finding: Anki Redo is unavailable after every AnkiScape review undo and
  direct-action undo (section 1 probe). The kanban card describes only the
  missing rewards.
- Finding: `review_undo_stack` and `direct_action_undo_stack` are never
  cleared at profile load. After a profile switch, the old profile's
  snapshots stay under the new ones. Aligned pops never reach them, but a
  wrong pop (question 4) can. This spec clears `review_undo_stack` and
  `review_redo_stack` on `profile_will_close` (4.3.4). The direct-action
  stack needs its own fix.
