# Grimy herb slice handoff

## Goal

Fix the four regressions on `goal/herbs-2026-08-11`.
Do not plan the grimy herb slice again.
Keep all correct work from commit `f6b44e100051c29588f3c0f2c5637e55597a6457`.

## Repository state

The work branch is `goal/herbs-2026-08-11`.
The preservation commit is `f6b44e100051c29588f3c0f2c5637e55597a6457`.
Canonical main remains untouched at `0071218b` for this work.
No commit is pushed.
The slice is incomplete and red.

## Current plain lane result

The plain lane runs 4059 tests.
It has 4 failures and 494 skips.

The four failing tests are:

- `test_capes_and_distinctions.EffectiveLevelTest.test_the_boost_moves_thirty_nine_roll_paths_not_one`
- `test_integration_smoke.TestIntegrationSmoke.test_razor_backed_tracking_review_and_undo_use_the_real_hunter_path`
- `test_integration_smoke.TestIntegrationSmoke.test_vinesweeper_loaded_addon_review_and_direct_actions_are_undoable`
- `test_target_metadata.TargetMetadataTest.test_carrion_jadinko_row_exposes_tool_and_seed_roll`

All four failures are regressions from this slice.
Canonical main at `0071218b` passes the three tests that exist there.
The fourth failure is a new contract from this slice.
Resume the work by fixing these failures.
Do not replace this step with a new plan.

## Work that is complete

Do not redo the Jadinko seed acquisition route.
Carrion Jadinko supplies the five vine-herb seeds.

Do not redo the five runnable vine-herb crops.
The crops are Erzille, Argway, Ugune, Shengo, and Samaden.
The tracked code uses a four-stage curve with 20 minutes per stage.
The tracked code uses 67 and 80 as the save endpoints.
The tracked code uses six disease slots through the registered
`farming.shared_disease_slots` placeholder. Darkan supplies the generic selector,
but a period Habitat-specific disease rate remains unrecovered.
Do not redo the runnable crop path.

Do not redo the reachability parser fix.
`tools/audit_item_reachability.py:56` reads `weighted_secondary_outputs`.

Do not remove the producer-route contract.
The contract is `test_habitat_vine_herb_chain_is_reachable`.
It is in `tests/test_item_reachability_audit.py`.

## Herblore level corrections

Keep all four corrected clean levels.
These values were wrong before this slice.
The corrections must survive all later fixes.

| Herb | Old level | Correct level | Tracked source pin |
| --- | ---: | ---: | --- |
| Argway | 56 | 57 | Herblore Habitat oldid `6513740`, `2012-10-31T21:20:32Z` |
| Ugune | 55 | 56 | Herblore Habitat oldid `6513740`, `2012-10-31T21:20:32Z` |
| Shengo | 57 | 58 | Herblore Habitat oldid `6513740`, `2012-10-31T21:20:32Z` |
| Samaden | 58 | 59 | Herblore Habitat oldid `6513740`, `2012-10-31T21:20:32Z` |

The runtime source field still points to the checked-in `HerbData.kt` transcription.
The dated wiki pin is in `memory-bank/source-audits/farming-wiki-pin-ledger-2026-07-11.md:50`.

## Reachability baseline

This slice measures against its own merge-base.
Its merge-base is `0071218b`.

| Record | Actions | Reachable items | Orphan inputs | Blocked actions |
| --- | ---: | ---: | ---: | ---: |
| This worktree | 1562 | 2594 | 87 | 91 |
| This slice merge-base | 1556 | 2573 | 102 | 101 |

Do not use the sibling branch baseline for this slice.
The values `1556 / 2585 / 90 / 85` belong to `goal/breadth-2026-08-11`.
They must never appear as the baseline for this branch.

## Separate queue item

Do not fix this item in the grimy herb slice.
This defect is pre-existing.
It needs a separate slice across every skill button.

`ui/ui.py:1467-1470` applies Hunter availability as a one-way enable.
The code enables the Hunter button when pure availability becomes true.
The code never disables the button when pure availability becomes false.
Hunter can remain enabled with no actionable target.
Neighbouring skill buttons use the same one-way pattern.

Use this reproduction:

1. Create a fake Hunter button.
2. Call `ui.refresh_skill_availability` with `can_hunt_any_item` set to `True`.
3. Call `ui.refresh_skill_availability` with `can_hunt_any_item` set to `False`.
4. Observe that the fake button remains enabled.

## Process rule

Give one writer one narrow unit.
Verify each fact before it enters a shared brief.
A wrong shared fact reaches every agent.
Each agent then returns the same false regression.
