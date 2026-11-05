# Native first-card banking and HUD title, 2026-11-05

Scope: contract points 4 and 11 in `followup-grill.md`. Implementation only on
`goal/pass21-followup`; no promotion, remote lane or player-save access.

## Bank runs

Synthetic replay uses Shortbow, an empty Ammunition slot, 500 Bronze arrows,
200 Iron arrows, 60 banked Lobsters and no carried food; combat skills are 45,
lifepoints 450, speed 10x. Every random roll is 0.5. It uses the real combat
answer handler and records the real bank-trigger predicate's inputs.

| Replay review | Trigger | Worn Iron arrows | Loaded food | Supply slots | Loot slots |
| --- | --- | --- | --- | --- | --- |
| 1 | Food refill | 200 | 0 | 0 | 0 |
| 4 | Full pack | 193 | 14 | 14 | 15 |
| 7 | Full pack | 186 | 14 | 14 | 15 |
| 10 | Full pack | 179 | 14 | 14 | 15 |

The first trigger occurs **after** the free starting-ammo fill. It spends 60
ticks and leaves 40 ticks of travel, matching the supplied first-card screenshot's
one-review remainder. Review 2 finishes travel and fires 5 Iron arrows. Changing
only banked Lobsters from 60 to 0 makes review 1 fire 10 Iron arrows without a
bank run. The ammo slot did not cause the initial trip.

Every later trigger in this replay has 14 Lobsters plus 7 Bones, 7 Raw chicken
and one Feather stack: 29 slots against capacity 28. Food and ammunition remain
available. These are loot-deposit trips, not ammunition or food refills.

Source comparison against `main` at
`c710813faa75528ea2619740a3bf5de198539692` found the complete function sources
identical for `_combat_bank_run_needed`, `_combat_refill_food_loadout`,
`_combat_refill_context_supplies` and `_combat_progress_or_start_bank_run` in
`logic_pure/logic_pure_combat_supplies.py`. No banking behavior changed.

The native images show no internal trigger reason or RNG stream. The replay
establishes causes from the supplied seed; its later review numbers are not a
claim about the exact native sequence. Individual later native trips cannot be
proved from those images alone.

## Title fix and geometry

The nested title row was compressed inside the fixed-height HUD. With a
13-point Helvetica Neue font, the regression test measured 19 px of title height
against a 21 px size hint and font height. Before the fix it failed all eight
original theme/size/button combinations with `AssertionError: 19 not greater
than or equal to 21`. The title now keeps its natural minimum height. The
pickup button retains its existing seat; no other HUD styling or layout changed.

The final matrix covers Fusion light/dark, pickup present/absent, and windows
1000×700 (fixture default), 667×602 (supplied default-size native image at 2×),
and 720×560. The fixture shows the window before resizing and pumps five event
passes before measuring or grabbing it. All twelve cases have title height
21 px, size hint 21 px and font height 21 px. The HUD remains 340×128.
With pickup present, the title rect is `(50, 10, 182, 21)`, pickup is
`(236, 11, 92, 16)` and player bar is `(50, 33, 278, 12)`. Without pickup,
the title expands to `(50, 10, 278, 21)`. The button and other row rectangles
matched the pre-fix geometry probe. Geometry tests check complete title width
and height, containment, separation from the bar, and the pickup's right edge.

Repeatable captures and trigger records:

```sh
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python tools/maintenance/pass21_followup_probe.py --output /tmp/pass21-followup-evidence
```

`/tmp/pass21-followup-evidence/evidence.json` holds measurements and both replay
traces. Each matrix case has a HUD PNG and a full-window PNG in that directory.
This is offscreen Qt evidence, not a new native Anki verification. The font is
a reproduction fixture; the native tester's exact font configuration is unknown.

## Required selectors

```sh
python3 run_tests.py tests.pace.test_ground_ammunition tests.pace.test_ammunition_hud tests.pace.test_ammunition_pack tests.test_review_hud tests.test_review_strip
```

Final output from `/tmp/pass21-required-tests.log`:

```text
Ran 77 tests in 6.636s

OK
```

New behavior coverage proves the food/full-pack diagnosis, the ammo-only
counterfactual, and complete title geometry across the requested variants.

## Promotion-gate follow-up

The supplied `gate-fbd17ce8e.log` failures reproduce in a focused run:
`Ran 27 tests in 19.825s`, `FAILED (failures=5, errors=1)`. All are test
maintenance under the settled contract; no further product change was needed.

- The integration HUD stub omitted `ammo_pickup_action`. It now accepts and
  records that callback, and verifies it is the real pickup action.
- `test_an_add_confirms_on_its_button_and_marks_its_new_line_for_a_moment`
  spent all 37 ore on its first entry. It now queues two funded ten-bar entries
  so it can still verify the second confirmation and highlight.
- `test_the_count_box_starts_at_what_the_bank_allows_and_keeps_a_typed_count`
  expected 100 bars from 37 ore. It now proves the cap at 37, retains a valid
  typed count of 12, and projects those 12 bars into two platebodies.
- `test_the_fifth_entry_fills_the_queue_and_clear_empties_it` now supplies
  15 ore for five three-bar entries. The five-entry cap and Clear assertions
  remain; repeated entries cannot reuse the same three ore.
- `test_clicks_move_rows_and_the_top_click_changes_what_the_next_card_runs`
  and `test_a_move_flashes_the_row_at_its_new_place_and_never_says_added`
  moved a platebody ahead of its only bar producer. Each now banks five bars,
  preserving the move and highlight scenarios without an unfunded entry. The
  first test verifies ten bars after smelting five more.

The repaired focused selection reports `Ran 27 tests in 20.418s`, `OK`.
An additional thirteen-test queue/Bork/diary selection passes and supports the
papercut closures. The first attempt to select the Bork regression used its
retired name and was refused before execution; the current test ID was listed
before the successful selection.

`tools/memory_bank/move_papercuts.py` moved thirteen repaired entries verbatim
to `memory-bank/papercuts-fixed-2026-11-05.md`, with repair revisions and checks
beside each group. Its `check 309289ed7c21651a55ca8e8684d78fa8e0ab4f4b`
reports no lost line and no entry both open and fixed. Two new lookup incidents
remain open. The open file has 799 lines; no entry was deleted.

Required expanded command:

```sh
python3 run_tests.py tests.integration_smoke.test_world_clock_and_routes tests.main_menu
```

Output from `/tmp/pass21-added-required-tests.log`:

```text
Ran 487 tests in 255.519s

OK
```

`python3 tools/audit_docs.py` reports:

```text
Audited 1153 Markdown and 2 HTML files.
Documentation audit passed.
```
