# Pass 11 Owner Notes and Slice Briefs

Date: 2026-08-22. Author: the design thread. Consumers: the ox-alpha
implementation agents and the Sol reviewers. The standing slice contract
(`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md`) binds every agent
dispatched from this brief. Read it completely before you edit anything.

A read-only Sol scout diagnosed all five items on 2026-08-22 with probes and
line-level traces. The fix sites below come from that scout and were current at
intake. Re-measure each line number before you edit; `main` moves.

## Goal

Pass 11 must make the carried-pack surface truthful, make every deselection
path end on Bankstanding, make bank runs work and show during combat, make the
bank search responsive, and make Fish Flingers start with one click.

## Owner notes (verbatim clauses)

From `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/TXT.rtf`, Pass 11
section, plus two same-night additions in chat:

1. Screenshot (Equipment tab, Carried pack Auto, Supply mode Max output): the
   summary reads "Runes: Air rune x5, Mind rune x5" while the Current
   inventory grid shows no runes. Annotation: "Where's the air runes and mind
   runes? Why are they even part of the 'max output' if I'm not even using
   magic".
2. "Standardize what switches to bankstanding vs. just nothing selected. I
   think everything should just become bankstanding."
3. "The bank run button during combat didn't seem to do anything. Also,
   there's never any indication when I'm going back to the bank regardless."
4. "the search with the new bank grid is extremely laggy" (chat, 2026-08-22).
5. "getting Fish Flingers started is glitchy af. I had asked a while back that
   there should not be two surfaces to start the activity, and they seem to be
   coupled in an incoherent manner now" (chat, 2026-08-22).
6. "Yeah the entire xp bar needs to be replaced showing that a bank run is
   happening" (chat, 2026-08-22).

## Rulings

1. **Owner, ratified in chat:** manual combat bank runs are allowed during a
   live encounter. The encounter survives the two-review trip and resumes
   after, the same as the automatic state machine.
2. **Owner, ratified in chat:** while any bank run is active, the travel
   display owns the entire reviewer-strip progress area, including combat's
   health and enemy presentation. The normal display returns when the run
   state clears.
3. **Owner clause 2:** every path that ends, refuses, invalidates, or stops an
   activity or target selects Bankstanding. No path leaves `current_skill ==
   "None"` except profile bootstrap.
4. **Owner clause 1:** rune costs load only when the effective combat class is
   `magic`. This includes supplemental spell runes such as Vengeance.
5. **Standing Pass 8 ruling:** one commit action starts a D&D. A detail-page
   click that enters an event must also activate it for reviews.
6. **Design thread, vetoable:** weapon, action, attack-style, and spell
   mutations are rejected during a live encounter, consistent with the
   existing supply-mode behavior; outside an encounter they reconcile the
   supply loadout (unload, then refill against the new effective method).

## Slices

Six slices. Branch names use the pattern `goal/pass11-<key>-2026-08-22`.
Worktree leaves use `pass11-<key>`. One attributable commit each.

### Slice `runes` — carried pack truth and the magic gate (item A)

Three defects. The loadout summary is truthful (it projects the persisted
`combat_supply_loadout`); the other surfaces lie around it.

- Gate the complete rune-cost calculation on an effective magic combat class.
  The supplemental loop at `logic_pure/logic_pure_combat_model.py:2438-2449`
  sits outside the magic gate; `_combat_required_rune_cost_pure()` must return
  no rune cost when `combat_class != "magic"`. `Max output` enables Vengeance
  through `data/magic_data.py:622-625`; that must stop producing rune loads
  for melee and ranged.
- Route weapon, action, attack-style, and spell mutations
  (`__init__.py:4560-4626`, equip at `:5065-5073`, unequip at `:5100-5108`)
  through one pure combat-method reconciliation that applies the mutation,
  unloads the old loadout, and refills against the new effective method.
  Reuse the unload/refill sequence at
  `logic_pure/logic_pure_combat_engine.py:2709-2720`. Apply ruling 6 for live
  encounters.
- Move the "Current inventory" label and scroll area (`ui/ui.py:25520-25526`)
  inside `custom_view` so Auto mode stops showing the unrelated
  `carried_inventory` overlay (`__init__.py:1991-2000`) next to the combat
  loadout summary.
- Do not change the summary to read bank inventory. It correctly reports
  loaded supplies.

Scout probe evidence: after a magic refill loads Air x5 and Mind x5, a weapon
switch to melee `accurate` leaves both loaded and unreconciled.

Focused tests: `tests/test_combat_logic.py:531`, `:568`, `:5535`, `:5557`
(currently asserts melee Vengeance runes; reverse it),
`tests/test_main_menu_widget.py:3668` (contrary assertions at `:3754-3766`),
`:6642`, `:6796`, `tests/test_integration_smoke.py:4062` (esp. `:3886-3910`).
Neighbours: `tests/test_inventory_pure.py`,
`tests/test_direct_action_undo_seam.py`.

Acceptance: a regression starts with loaded magic runes, switches to a
scimitar through the real equipment callback, and proves the runes return to
bank and leave the loadout. A fresh melee `Max output` refill loads zero
runes. Auto mode renders no Current inventory grid.

### Slice `bankstand-seam` — the Bankstanding policy seam (item B, part 1)

- Make `_deactivate_current_skill()` (`__init__.py:1466-1486`) delegate to
  `_switch_to_bankstanding()` (`__init__.py:1487-1493`). This converts every
  runtime `ctx.deactivate_current_skill()` refusal path in one edit.
- Route the UI Stop button (`ui/ui.py:5194-5209`) through Bankstanding
  activation; the local active surface becomes Utilities, not `"None"`.
- Add one shared transition predicate for `activity_session.active_id`
  going nonempty to empty, applied at the direct-command boundary
  (`__init__.py:1038-1047`) and at the review boundaries
  (`__init__.py:5470-5476`, `:5757-5762`). A completed transaction whose
  session cleared routes through `_switch_to_bankstanding()` before the undo
  snapshot is finalized, so undo restores the former activity atomically.
- Combat-session exits that restore a prior combat target may keep the saved
  target, but the active review surface still becomes Bankstanding.
- Profile bootstrap (`__init__.py:335`) stays `"None"`. Out of scope.

Focused tests: `tests/test_integration_smoke.py:2234`, `:2111`, `:2472`,
`:2762`, `tests/test_runtime_actions.py:819-859`, `tests/test_logic.py:963`,
`tests/test_main_menu_widget.py:12213`. Neighbours:
`tests/test_direct_action_undo_seam.py`, the `test_undo_seam_*.py` family.

Acceptance: explicit Stop, a level/quest invalidation, a review-driven
completion, a direct Leave command, and a combat-session completion all end on
Utilities + `current_utility == "bankstanding"`, and undo restores the prior
state after each.

### Slice `bankstand-sites` — the stragglers (item B, part 2)

Depends on nothing in part 1; both call seams already exist.

- Invalid selected IDs must stop repairing to per-skill defaults and instead
  switch to Bankstanding: `runtime/runtime_actions_utility.py:773-775`,
  `runtime/runtime_actions_gathering.py:432-438`, `:561-567`, `:694-700`,
  `:933-939`, `runtime/runtime_actions_magic.py:417-423`,
  `runtime/runtime_actions_combat.py:419-425`,
  `runtime/runtime_actions_production.py:555-560`, `:622-627`, `:710-717`,
  `:771-776`, `:871-876`, `:937-942`, `:1035-1040`, `:1189-1194`,
  `:1279-1284`, `:1395-1400`,
  `runtime/runtime_actions_activities.py:2902-2917`.
- Refusal branches that return `False` without any deactivation call the seam
  explicitly: Dungeoneering, Temple Trekking, Gnome Restaurant, and Dominion
  Tower refusal paths.
- Special inconsistent paths: the Shooting Star write-then-deactivate
  contradiction (`__init__.py:372-388`), Evil Tree terminal paths selecting
  `make_soft_clay` (`logic/evil_tree_logic.py:436-449`, `:511-525`), Flash
  Powder Factory resetting Agility to default
  (`logic/flash_powder_factory_logic.py:413-420`, `:538-545`, `:606-613`),
  and the Brimhaven Stop path (`ui/ui.py:5194-5207`, coordinate with the
  `bankstand-seam` slice owner if the hunk overlaps).

Focused tests: `tests/test_shooting_star_logic.py:100`, `:195`,
`tests/test_thieving.py:763`, plus each `tests/test_<activity>.py` suite whose
module you touch. Neighbours: `tests/test_runtime_actions.py`,
`tests/test_direct_action_undo_seam.py`.

Acceptance: no touched path selects a default action or leaves `"None"`; each
lands on Bankstanding.

### Slice `bankrun-strip` — combat bank runs and the travel display (items C, 6)

- Remove only the active-encounter rejection in
  `request_combat_bank_run_now_pure`
  (`logic_pure/logic_pure_combat_engine.py:2691-2696`). The state assignment
  at `:2701-2705` already preserves the encounter and starts the two-review
  route.
- Add one pure travel projection beside
  `review_bank_run_button_view_pure` (`logic/review_strip_logic.py:263-289`)
  returning active/queued status, kind, label, total, remaining, percent, and
  display text. Sources: `combat_bank_run` (total always
  `COMBAT_BANK_RUN_REVIEWS` = 2, `logic_pure/logic_pure_state.py:157-167`),
  `skilling_bank_run` (`reviews_total`/`route_label` optional,
  `logic/inventory_pure.py:340-355`), and the pending request fields
  `review_bank_run_requested_target`, `skilling_bank_run_requested`,
  `review_bank_run_requested_handler`. Select the current handler's route;
  combat and carried states can coexist in persisted saves.
- At the top of `ReviewHUD.set_data()` (`ui/ui.py:2619-2624`), before every
  branch: while the projection is active, the travel display owns the whole
  progress area. Hide stale `second_progress`, `second_progress_lbl`,
  `combat_resources`, `enemy_progress`, `chips_lbl`, and unrelated labels.
  Render the existing `progress_lbl` and thin `progress` bar
  (`ui/ui.py:2402-2415`) as the travel status. Ruling 2: this replaces
  combat's player/enemy presentation (`ui/ui.py:2792-2839`) during the run.
  When the state clears, ordinary branch rendering returns by itself.
- Replace the button-only refresher (`__init__.py:1729-1738`) with one shared
  helper that refreshes the HUD and the button. Use it after manual strip
  requests (`__init__.py:1724-1733`), review completion
  (`__init__.py:5764-5769`), direct GE actions (`__init__.py:2166-2177`), and
  the reviewer-surface refresh (`__init__.py:5826-5841`). GE needs no route
  state of its own; it delegates through `_trigger_active_bank_run()`.
- Adjacent fix (in scope): combat bank-run reviews currently fall through to
  the generic zero-damage message at
  `runtime/runtime_actions_combat.py:877-893`. Add an explicit bank-run
  branch so the event log does not contradict the travel display.

Focused tests: `tests/test_combat_logic.py:546`, `:4707`,
`tests/test_review_strip_logic.py:752`, `:773` (obsolete refusal expectation;
replace), `tests/test_review_strip.py:566`, `:614`, `:643`, `:663`,
`tests/test_integration_smoke.py:6999`, `:6761`, `:8955`,
`tests/test_runtime_actions.py:2433-2510`, `:2382`, `:5190`, `:5510`.
Neighbour: `tests/test_direct_action_undo_seam.py`.

Acceptance: the Qt regression renders normal Mining, active carried travel,
restored Mining, live combat, active combat travel, and restored live combat.
The manual button starts a run mid-fight and the encounter survives. A GE
collect during combat produces a real two-review combat route and the strip
shows it.

### Slice `bank-search` — debounce the bank grid search (item D)

Scout probe: with 300 bank stacks, every keystroke costs 535 to 850 ms and
rebuilds all 600 carried-picker buttons even for a zero-result query.

- Add one single-shot `QTimer` (120 to 150 ms) beside the search control.
  Restart it on `textChanged` (`ui/ui.py:26303-26305`); on timeout run a
  search-only refresh.
- Extend `_refresh_bank_surface()` (`ui/ui.py:25826-25832`) with a narrow
  `refresh_carried` flag; the debounced path runs with `rebuild_tabs=False,
  refresh_carried=False`, skipping `_refresh_carried_panel()` and
  `_render_bank_tabs()` (`ui/ui.py:26317-26327`).
- Keep the final main-grid rebuild. Do not attempt a cell cache or a
  model/view rewrite in this slice; each cell owns drag/drop, menus, icons,
  quantity text, accessibility, and tooltips.

Focused tests: `tests/test_main_menu_widget.py:10520`, `:10356`, `:10411`,
`:10546`, `:3518`, `:1383`. Add a coalescing regression: several `setText()`
calls inside one debounce interval produce one completed render, and
carried-picker plus bank-tab button identities survive query changes.
Neighbours: `tests/test_bank_layout_logic.py`, `tests/test_inventory_pure.py`.

Coordination: this slice and `runes` edit nearby `ui/ui.py` regions
(`:25421-25427` vs `:25517+`). Distinct hunks; do not widen either.

### Slice `flingers-start` — one-click Fish Flingers (item E)

- The detail button's handler (`ui/ui.py:13764-13772`) enters the event but
  calls the non-activating selection route, so from an ordinary skill the
  review surface never switches while the button claims "Selected for
  reviews" (`ui/ui.py:13704-13716`). After successful entry, call
  `_set_utility_selection(FISH_FLINGERS_ACTIVITY_ID, activate=True)` — the
  same seam Big Top already uses (`ui/ui.py:15125-15139`) and the global
  Activities control uses (`ui/ui.py:21079-21086`).
- Do not change Fish Flingers pure logic
  (`logic/fish_flingers_logic.py:245-263` already writes correct event
  state) and do not globally change `_request_utility_selection`.
- Big Top does not share this defect; leave it alone.

Focused tests: `tests/test_main_menu_widget.py:14921` (currently expects the
non-activating callback; correct it), `:12575`, `:12680`, `:12706`, `:17361`,
`tests/test_integration_smoke.py:3717`, `tests/test_fish_flingers.py:177`,
`tests/test_circus.py:339`.

Acceptance: starting on Mining, one click on the Fish Flingers primary button
consumes a ticket, opens the session, sets `current_utility ==
"fish_flingers"`, calls `on_start_activity("fish_flingers")`, and the training
surface reads Activities.

## Verification lanes — promotion-gate exception invoked

The orchestrator re-runs both lanes on each merged tree as the promotion gate.
Each slice agent therefore runs: its focused tests, the shared neighbour
suites named in its slice, and the plain lane
(`/opt/homebrew/bin/python3 run_tests.py`). Do not run the offscreen Qt lane
branch-side; say in your report that you skipped it under this exception.
Qt-touching slices still run their focused Qt tests through
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest <module>`.

Mutation hygiene per the contract: prove your focused test load-bearing by
mutating YOUR OWN change into the trap shape, observe the failure verbatim,
restore, then run `git diff --stat` against your branch point and confirm only
your slice's files appear.

## Collision rule

The intake head is `cba00cc7` on `main`. The harvesting loop is live and
merges to `main` on its own schedule; the design thread re-absorbs `main`
before each Pass 11 landing. Before editing, record HEAD, run
`python3 tools/worktree_guard.py audit`, and stop the slice if another writer
changed an overlapping file.

## Non-goals

- Do not change cadence math, XP curves, or the GE bank-run trigger set.
- Do not change profile bootstrap to Bankstanding.
- Do not rewrite the bank grid as a Qt model/view.
- Do not weaken any audit, test, or pinned baseline (contract section 8).
- Do not push to any remote. Never commit to `main`.

## Batch trace (closure, 2026-08-23)

| Slice | Author | Commits | Review path | Result |
| --- | --- | --- | --- | --- |
| flingers-start | ox-alpha | `4da82992` | Sol accept (round 1) | landed |
| bankstand-seam | ox-alpha + Sol fix | `a7db2d37` + `9408fa14` | Sol reject (3 major) → Sol fix → ox closure accept | landed |
| bankrun-strip | ox-alpha + Sol fix | `74240a1f` + `9711acb6` | Sol reject (1 major, 4 minor) → Sol fix → ox closure accept | landed |
| runes | Sol (ox lost round 1) | `e7d51f8d` + `384e557e` | Opus reject (1 major, 3 minor) → Sol fix → ox closure accept | landed |
| bankstand-sites | Sol (ox stalled round 1) | `4d88cea6` + `e812c985` | Opus 1 major → Sol fix → ox closure accept | landed |
| bank-search | Sol (ox lost round 1) | `f6b502f09` + `80c7772f` | Opus 2 minor → Sol fix → ox closure accept | landed |

Promotion: six branches merged clean into `promote-pass11/2026-08-23`. First
gate at `84c7748f` went green (plain 4,389 OK skipped=506; Qt 4,389 OK
skipped=3) and was invalidated by a loop landing; the absorbed tree `246c8298`
re-gated green (plain and Qt 4,415 OK, skips 506/3; docs pass; 0 hard issues;
diff-check clean; reachability at the known informational baseline). Landed on
`main` as `9c6fcd75` inside a coordinated hold window with the harvesting
loop. The Opus reviewer's melee-lockout catch on `runes` (Vengeance charged
runes it never loaded) was the highest-value finding of the pass.
