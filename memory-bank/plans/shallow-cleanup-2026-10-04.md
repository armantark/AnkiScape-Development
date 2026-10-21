# Shallow module cleanup — 2026-10-04

## Goal
Remove the approved unused code and forwarding layer. Preserve game behavior and both asset command names.
This is a separate bounded task. The earlier queue goal remains paused.

## Baseline and ownership
Base: ca859eb0ef06a0b298d25bcedd9338a1120afabc.
Root reused clean pool checkouts 4, 5 and 7. Their prior branches remain intact.
Root owns integration, this plan, artifacts, shared evidence and all remote runners.
Leaf runtime owns runtime/runtime_actions.py, runtime/runtime_actions_carried.py and tests/test_runtime_actions.py in pool 5.
Leaf unused owns core/utils.py, its two dedicated tests, core/logic.py, logic/farming_logic.py, ui/ui.py, __init__.py, data/bork_data.py, data/dominion_tower_data.py, data/prayer_data.py and data/conquest_data.py in pool 4.
Leaf tools owns the two asset commands and their minimal shared implementation in pool 7.
No concurrent leaf owns the same file. Root removes obsolete UI test substitutions after integration.

## Runtime contract
Remove runtime_actions_carried.py. Import its carried exports from the requirements and overlay owners.
Preserve the existing runtime_actions interface. Remove obsolete origin metadata work.
Correct the cadence patch in test_runtime_actions.py to patch the overlay owner.
Do not change the import limit or measuring instruments.

## Unused-code contract
Delete core/utils.py and tests/test_utils.py plus tests/test_utils_edge.py.
Delete only core.logic get_exp_to_next_level, calculate_woodcutting_probability and calculate_mining_probability.
Delete farming_status_projection_pure; retain farming_frontend_projection_pure.
Delete update_menu_visibility, show_review_popup and the root popup forwarding function and their no-op calls.
Delete equipment_summary_text and its private tables, retaining the live tooltip and requirements helpers.
Delete bork_mage_enemy_pure, bork_enemy_data_pure, dominion_tower_enemy_registry_as_dict, combat_prayers_as_dict and conquest_units_as_dicts.
Remove imports made unused by these deletions. Retain live catalogs and constructors.
Do not remove the pure progression helper with the same name.
Do not touch the generated shop helper or the shared boss-room module.

## Tools contract
Share the existing Dominion Tower and Gnome Restaurant command bodies.
Keep filenames, command flags, manifest order, cutoff, source, rate limit, size, output and provenance policy.
Use the existing asset implementation. Do not add a registry, plugin layer, or network policy.
Root must check configured schedulers and running processes before retirement of gap_driver.py, gap_loop_prompt.md and test_gap_driver.py.
Preserve the historical backlog, evidence and source branches.

## Verification
Each leaf checks surrounding code and current callers before deletion, then runs the appropriate existing focused tests.
Each leaf runs the plain suite and standing audits. Root runs both full lanes with promotion_gate.py --remote-lanes on the integrated commit.
Qt branch verification is omitted under the standing promotion-gate exception; root owns the exact integrated Qt gate.
Every test count comes from a fresh inventory. Retire only tests dedicated to the approved retired code.
Do not weaken tests, audits, limits or baselines. Do not add implementation-mirroring tests.
Root independently checks the leaf evidence and obtains a diff-only simplification review.
Native acceptance remains a separate requirement where the binding runtime contract requires it.
No runtime landing occurs without required native acceptance. No push or unrelated queue work.

## Success criteria
Runtime: the forwarding module is absent; current imports resolve; cadence patch targets its actual owner; runtime behavior tests pass.
Unused: listed definitions are absent; retained live paths pass existing tests; no surviving executable caller references a removed definition.
Tools: both command names work with the same arguments and policy; no output assets or provenance are changed by validation.
Integration: all accepted commits are included; the authoritative full gate passes on the exact commit; required acceptance is complete.
If a condition is blocked, preserve committed source and exact evidence. Report the missing condition.

## Events
- 2026-10-04: Plan settled. Pool acquire refused: all 16 worktrees are in use or dirty (max_trees = 16). Reused clean root-owned leases without raising the limit.

- 2026-10-04: The standing goal/* branch rule governs the leaf branches. Each leaf renames its assigned branch to goal/shallow-<scope>-cleanup-2026-10-04. No gate or standing rule changed.

- 2026-10-04: Root will reuse the existing commit snapshot and native source-copy rules for the required native handoff. A small tools/native command will make this repeated sequence reproducible. Before use, check refusal for a wrong revision, dirty source, an existing output directory and an add-on symlink. Check archive extraction against the file manifest and native source digest. The command must not open Anki or access a collection.

- 2026-10-04: Documentation selection must honor the owner's publisher-only check for status HTML. Check that ordinary HTML and status-folder Markdown remain audited. Keep the startup budget and all other checks unchanged. The native freeze command will also own the repeated packet transfer, using the existing remote runner's retries and supported options. A disposable transfer canary must reject a wrong remote hash and retain the successful packet identity before native use.
