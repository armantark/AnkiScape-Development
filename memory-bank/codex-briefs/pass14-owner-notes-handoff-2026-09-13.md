# Pass 14 owner notes — handoff brief, 2026-09-13

Design seat: Fable, session 61069f54. Rulings: `memory-bank/design-thread-queue.md`
§4.27. The Codex thread obeys `memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md`
in full. The orchestrator stays parked (rulings ledger §57). The owner starts
the Codex thread himself.

## Goal

Close the Pass 14 owner notes with two code slices and no others: no lock of
any kind while an enemy is alive, an encounter that ends when the player
leaves the fight, and a blocking dialog plus one HUD line when a Slayer
assignment completes. Combat pace and menu open time need no code in this
pass.

## Owner notes (verbatim, 2026-09-13)

> Don't require combat to end to go back to the bank to swap equipment.
> Deeply optimize the loading of the menu
> I even tried changing my combat style when bankstanding for several turns
> and it still thinks I'm in combat and can't switch it. What finally worked
> was switching to chickens, waiitng for one to die and a new one coming in
> with fresh HP, then switching it.
> Also, combat pace is way too slow. This does not feel like the same xp/hr
> rates as the real game. not sure how to balance this with the cadence
> kernel. But yeah it feels like it takes 50+ cards just to kill one bear for
> my slayer task.
> Make a more obvious popup for when a slayer assignment is done (though it's
> possible there was in fact a popup and I just ignored it, which would be my
> bad)

## Rulings (from §4.27)

1. Nothing is locked while an enemy is alive. Style, spell, weapon, supply
   mode, and action change are never refused. A change applies from the next
   review.
2. An encounter survives only between reviews of the same combat action
   against the same target. A kill, a death, a flee, a bank run, or any action
   change ends it. The next fight starts a fresh enemy.
3. Combat pace stays as the cadence contract of 2026-07-13 sets it. No code.
4. Menu open time is parked on `memory-bank/future-work-kanban.md`. No code.
5. Slayer completion shows a blocking dialog on the Level Up surface, after the
   review. The fight continues. The review HUD shows the assignment count.
6. Glossary terms Action and Encounter are in `GLOSSARY.md`. Use them.

## Facts (fact-finders of 2026-09-13, read-only)

- The encounter predicate is `combat_has_active_encounter_pure`
  (`logic_pure/logic_pure_combat_engine.py:2648-2654`): a mapping with a string
  `target_id` and no `disengaged` flag. Weaker copies of the test exist at
  `logic_pure_combat_engine.py:1336-1395` and `core/target_metadata.py:1386-1472`.
- Kill, death, flee, and exhausted enemy LP clear the record with
  `data["combat_encounter"] = {}` (`logic_pure_combat_engine.py:2250-2277,
  2340-2352`; `logic_pure_combat_model.py:840-896, 941-974, 2773-2840`).
- The refusals live at `logic_pure_combat_engine.py:2676-2696`, messages
  "Finish the active fight before changing combat method." and "Finish the
  active fight before changing supply mode." The UI shows them under the titles
  "Cannot change combat method" (`__init__.py:4800-4825`), "Cannot equip item",
  and "Cannot unequip item" (`__init__.py:5244-5343`). The style combo restores
  the old value after a refusal (`ui/ui.py:7693-7710`).
- Utilities selection sets `player_data["current_utility"]` with no encounter
  branch (`ui/ui.py:20599-21261`). `_switch_to_bankstanding`
  (`__init__.py:1553-1601`) and Stop (`__init__.py:4596-4620`) do not touch
  `combat_encounter`. A bank run returns before combat ticks
  (`logic_pure_combat_engine.py:1218-1314`) and preserves the encounter
  (`logic_pure_combat_supplies.py:965-991`).
- Slayer completion sets `completed=True`, increments `slayer_tasks_completed`,
  and records `slayer_last_family_id` (`logic/slayer_logic.py:227-277`). The
  combat handler builds "Defeated {kill_phrase} · Slayer assignment complete"
  (`runtime/runtime_actions_combat.py:774-806`) and sends it through
  `show_activity_gain`, which on an XP-paying review only records the event
  (`__init__.py:654-692`). The XP bubble `ExpPopup` holds 900 ms and fades
  500 ms (`ui/ui.py:3557-3670`). No dialog exists.
- The Level Up surface is `show_level_up_dialog` (`ui/ui.py:4513-4547`), a
  blocking custom `QDialog` with "OK". The diary dialogs queue during review
  and flush after it with `QTimer.singleShot(0, ...)` (`core/logic.py:81-113`;
  `__init__.py:1522-1539, 5821-5829`).
- The review HUD shows "Kills: {kills} · Trains {trains}" and no assignment
  state (`ui/ui.py:2836-2883`).
- Pace arithmetic at the owner's stats: 7.6 reviews per fresh black bear,
  10 observed; XP per bear 2012-exact. Recorded in §4.27 item 3. Do not change
  `LIVE_COMBAT_TICKS_PER_REVIEW` (`logic/cadence_live.py:30-32`).

## Slices

### S1 `encounter-no-lock`

1. Delete the refusal seam for combat method and supply mode at
   `logic_pure/logic_pure_combat_engine.py:2676-2696`, and the weapon equip
   and unequip refusals that call it (`__init__.py:5244-5343`). Remove the
   three dialog titles and the combo restore that exist only for them.
2. End the encounter when the action leaves combat or the target changes:
   clear `combat_encounter` in `_switch_to_bankstanding`, in Stop, in the
   Utilities and skill selection paths, and at the start of a bank run. Use
   the same `data["combat_encounter"] = {}` seam the kill path uses.
3. A change of style, spell, weapon, or supply mode inside a live encounter
   keeps the enemy's LP and countdown. Assumption to hold: no reset.
4. Replace the pin `test_live_encounter_rejects_every_combat_method_mutation`
   (`tests/test_integration_smoke.py:4066-4124`) with tests that assert each
   change is accepted mid-encounter and applies on the next review. Add a
   test per ending event in ruling 2, including the bank run, that asserts a
   fresh enemy on return.
5. Reproduce the owner's incident on the offscreen harness before and after:
   fight, switch to Bankstanding, change style. Before: refusal. After: the
   change sticks and the next fight starts a fresh enemy.

Fix sites: `logic_pure/logic_pure_combat_engine.py`,
`logic_pure/logic_pure_combat_supplies.py`, `__init__.py`, `ui/ui.py`.
Tests: `tests/test_integration_smoke.py`, `tests/test_cadence_kernel.py`,
`tests/runtime_actions/test_bankstanding_notice.py`.

### S2 `slayer-complete-dialog`

1. On the review that lands the last kill, queue one completion notice, and
   flush it after the review with the diary dialog mechanism. Fire it once per
   assignment.
2. The dialog uses the Level Up surface. Title "Slayer assignment complete".
   Body "You have defeated {count} {enemy plural}. See a Slayer master for a
   new assignment." Button "OK". Keep the existing activity text and event
   log entry.
3. Add one HUD line under the kills line: "Slayer: {remaining} of {total}
   left". Show it only while an assignment is active. Do not change any other
   HUD row.
4. Tests: the dialog fires once on the last kill and not on earlier kills;
   the HUD line reads the assignment state; the fight continues after the
   dialog.
5. Offscreen Qt screenshots of the dialog and of the HUD line at the default
   size and at 560 logical points tall, per
   `.claude/rules/qt-offscreen-screenshots.md`. Frontend-taste review before
   promotion (project rule).

Fix sites: `runtime/runtime_actions_combat.py:774-806`, `__init__.py`
(notice queue), `ui/ui.py` (dialog beside `show_level_up_dialog`; HUD at
`2836-2883`). Tests: `tests/test_runtime_actions.py:2826-2860`,
`tests/test_slayer_logic.py`, `tests/test_main_menu_widget.py`.

## Non-goals

- No change to `LIVE_COMBAT_TICKS_PER_REVIEW`, the review action multiplier,
  or any XP formula.
- No menu open-time work.
- No new assignment on completion; the player visits the Slayer master.

## Coordination

- Both slices touch `__init__.py` and `ui/ui.py`. Declare line ranges. The
  6,250-line cap on `__init__.py` is a hard gate; S1 deletes more than it adds.
- The canonical checkout is the owner's live Anki install. No slice edits it.
  Pooled worktrees only, through `python3 tools/worktree_guard.py lease`.

## Verification

Per slice: focused suites plus neighbours, both lanes, and offscreen Qt
screenshots for S2. Promotion: `python3 tools/promotion_gate.py run
--remote-lanes <worktree>` then `land <worktree>`, one batch, after re-absorbing
`main`. Module-surface pins move when `__init__.py` or `ui/ui.py` change;
re-measure with `python3 tools/module_surface.py --digest-only <module>` and
take the remote-lane values.

## Paste prompt for the Codex thread

```
Read memory-bank/codex-briefs/pass14-owner-notes-handoff-2026-09-13.md and memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md in full before any edit. Implement slices S1 encounter-no-lock and S2 slayer-complete-dialog exactly as the brief states; rulings are in memory-bank/design-thread-queue.md §4.27 and are not open. Use GLOSSARY.md terms Action and Encounter. Work in a pooled worktree from python3 tools/worktree_guard.py lease pass14 --holder codex; never edit the canonical checkout under addons21; never call treehouse directly; never use --no-verify, amend, push, or SLOP_GATE_* variables. Commit each slice atomically with a subject that says why it matters. Verify with the focused suites, both lanes, and offscreen Qt screenshots for S2 at the default size and at 560 logical points tall; attach the screenshot paths. Promote with python3 tools/promotion_gate.py run --remote-lanes <worktree> then land <worktree>. Report: the commit SHAs, the gate log path under ankiscape_worktrees/, the two before/after reproductions of the owner's incident, and any second-level finding you did not fix.
```
