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
