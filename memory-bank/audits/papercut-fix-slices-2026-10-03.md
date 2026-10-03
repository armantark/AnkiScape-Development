# Papercut fix slices — 2026-10-03

## Goal and scope

Repair each remaining cause in a separate slice. This document proposes work; this triage changes no code.

Repository root: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-papercut-triage-2026-10-03
Base: 91cf104af15cb85bd8f4d3d602ccebb291c4cd55. Branch: goal/papercut-triage-2026-10-03.
Evidence root: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-03/

The open log has 14 exact entries after review. The 15 proposed causes below cover the original 11 open entries; the three reopened incidents and their evidence gaps are recorded in papercut-triage-2026-10-03.md. Original line numbers refer to papercuts-before.md in the evidence folder.
The compound cleanup entry remains verbatim until its four remaining emitters work. Four other emitters already landed.
The alchemy entry has separate probe and visible-layout causes. S09 supplies the acceptance helper for S10.

## Rank by agent-time cost

Rank uses observed friction and repeat work, not a measured future duration. Equal ranks mean insufficient evidence to distinguish cost.
Normal mirror delays have the strongest elapsed evidence. Silent projection errors and repeated source requests force extra diagnosis.
Period source qualification has a larger investigation burden than a local CLI refusal. Source-blocked emitter costs are tied.

| Rank | Slice | Cause | User interface change |
| --- | --- | --- | --- |
| 1 | S01 | Normal runners can overtake an earlier mirror waiter | No |
| 2 | S02 | A HUD projection error leaves silent stale content | Yes, if the failure clears stale content or shows a controlled error |
| 3 | S03 | The source downloader corrupts existing URL parameters | No runtime interface change |
| 4 | S04 | The retained quest catalog cites later revisions | Only if qualified sources require visible content changes |
| 5 | S05 | Oronwen has no mourner-trouser repair action | Yes, a real repair service becomes reachable |
| 5 | S06 | The clockwork penguin has no construction action | Yes, a real quest crafting action becomes reachable |
| 5 | S07 | The Myreque sapphire preparation has no spell target | Yes, a quest spell target becomes reachable |
| 5 | S08 | The Seergaze emerald preparation has no spell target | Yes, a quest spell target becomes reachable |
| 6 | S09 | The text-fit probe does not measure painted combo text | No; this slice repairs only the QA helper |
| 7 | S10 | The selected alchemy item is clipped at the laptop sizes | Yes, the alchemy selector geometry changes |
| 8 | S11 | The expanded Fremennik Isles card lacks exact fit proof | Unknown until the exact probe; yes if geometry needs repair |
| 9 | S12 | Malformed cache ID input reaches Integer.parseInt | No |
| 9 | S15 | The asset audit sends an unsupported imageinfo parameter | No |
| 10 | S13 | The mirror fixture kills a process without reaping it | No |
| 11 | S14 | The Slayer quick-finisher unlock has no purchase path | Yes, Slayer Rewards gains a working purchase |

## Shared acceptance rules

1. Use the assigned checkout as the command directory.
2. Keep the canonical checkout, test instruments, pinned baselines and foreign runners unchanged.
3. Qualify period facts before a new gameplay action. The owner resolves source or product decisions.
4. Run each listed behavior selection after its scenario coverage exists. New modules can extend the same selection.
5. Collect the exact final selection count with root run_tests.py. Use that count with the unchanged MacBook runner.
6. Use plain for pure behavior and Qt for widget scenarios. A focused remote result requires the exact count and zero skips.
7. Preserve raw output, exact commands, source revision, result lines and reproducible scenario inputs.
8. Every user interface change needs the required visual check. Preserve screenshots at the named sizes and fix all visible text clipping.
9. Remove an open entry only through a verbatim move with checked closure evidence.

The commands below are complete behavior checks from the repository root. Plain runs can skip widget cases locally.
MacBook acceptance must use the correct lane and zero skips. It cannot rely on a local widget skip.

## S01 — Normal runners can overtake an earlier mirror waiter

Rank: 1. Open record: Original line 62.

Cost evidence: Historical queue at original line 18 lasted 17:43; line 62 names two later runs that acquired the mirror. Gate priority does not order normal runners.

Files: `tools/run_remote_tests.py`, `tests/promotion/test_remote_mirror_lock.py`, `tests/promotion/test_remote_mirror_priority.py`.

User interface change: No.

Acceptance: Add deterministic real-process scenarios for an older normal waiter, later normal arrivals and a waiting promotion gate. The older normal waiter must precede later normal runners once gate priority clears. Preserve the gate timeout, heartbeat and inherited-descriptor checks. Every spawned process must exit and release its lock.

Exact behavior command:

```sh
python3 run_tests.py promotion.test_remote_mirror_lock promotion.test_remote_mirror_priority
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count promotion.test_remote_mirror_lock promotion.test_remote_mirror_priority
```

## S02 — A HUD projection error leaves silent stale content

Rank: 2. Open record: Original line 7.

Cost evidence: The outer exception handler conceals the failing projection and forces extra content probes.

Files: `ui/ui.py`, `tests/test_hud_singleton_and_cleanup.py`.

User interface change: Yes, if the failure clears stale content or shows a controlled error.

Acceptance: Drive a good HUD update, a deliberate set_data failure, and a later good update. The error must reach a diagnostic sink once. The failed update must not retain a misleading prior card. The later update must restore correct content. Obey the owner decision for the visible failure state.

Exact behavior command:

```sh
python3 run_tests.py test_hud_singleton_and_cleanup
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count test_hud_singleton_and_cleanup
```

## S03 — The source downloader corrupts existing URL parameters

Rank: 3. Open record: Original line 64.

Cost evidence: The downloader retries the same transformed URL three times before the SHA-1 refusal. The historical source had to be fetched separately.

Files: `tools/fetch_assets.py`, `tests/test_fetch_assets.py`.

User interface change: No runtime interface change.

Acceptance: Use the exact Crumble Undead provenance URL with cb and format=original. Capture the outgoing request in a byte-serving fixture. Preserve the source query semantics, require SHA-1 263b75038c03b742bdfa93843623f38a656896b7, and reject mismatched bytes. Keep the existing optimized-image behavior covered. Do not change provenance hashes or normalize the source to pass.

Exact behavior command:

```sh
python3 run_tests.py test_fetch_assets
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count test_fetch_assets
```

## S04 — The retained quest catalog cites later revisions

Rank: 4. Open record: Original line 50.

Cost evidence: The checked pin contains 19 affected field references; each source requires period qualification.

Files: `tools/generation/refresh_quest_sources.py`, `tools/generation/quest_sources.json.gz`, `tools/generation/quest_sources.md`, `generated/quest_catalog_generated.py`, `tests/quest_catalog/test_source_refresh.py`, `tests/test_pre_eoc_quest_catalog_builder.py`.

User interface change: Only if qualified sources require visible content changes.

Acceptance: Resolve every quest, field and oldid in post-cutoff-citation-check.json against qualified period evidence. The top-level source, reward_source and journal_source census must contain zero unqualified late references. Check repeated nested references too. Two offline builds must produce identical catalog bytes. Source changes must have an explicit semantic review; do not substitute current pages or relax a cutoff instrument.

Exact behavior command:

```sh
python3 run_tests.py quest_catalog.test_source_refresh test_pre_eoc_quest_catalog_builder
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count quest_catalog.test_source_refresh test_pre_eoc_quest_catalog_builder
```

## S05 — Oronwen has no mourner-trouser repair action

Rank: 5. Open record: Original line 3.

Cost evidence: A source-blocked required action fails full-catalog closure and requires a qualified service route. Cost is tied with S06 through S08.

Files: `logic/shop/services.py`, `data/quest_action_proof_data.py`, `data/quest/stage_cleanups.py`, `tests/test_quest_action_proofs.py`.

User interface change: Yes, a real repair service becomes reachable.

Acceptance: With a stage-3 Mourning’s End Part I save and qualified materials, perform the real Oronwen repair service. It must emit the exact proof Have Oronwen repair the mourner trousers. A Quests review must advance 3 to 4. Undo must restore materials, proof and stage. Wrong-stage or missing-material attempts must not emit proof. Remove only this tuple from _UNEMITTED_CLEANUP_ACTIONS after runtime proof.

Exact behavior command:

```sh
python3 run_tests.py test_quest_action_proofs
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count test_quest_action_proofs
```

## S06 — The clockwork penguin has no construction action

Rank: 5. Open record: Original line 3.

Cost evidence: The furniture exists, but the required stage action has no emitter. Cost is tied with S05, S07 and S08.

Files: `logic_pure/logic_pure_construction.py`, `data/construction_data.py`, `data/quest_action_proof_data.py`, `data/quest/stage_cleanups.py`, `tests/test_construction.py`, `tests/test_quest_action_proofs.py`.

User interface change: Yes, a real quest crafting action becomes reachable.

Acceptance: From Cold War stage 2, use the qualified crafting-table-3 route and real ingredients. Emit Build the clockwork penguin on a crafting table 3. A Quests review must advance 2 to 3. Undo must restore the ingredients, proof and stage. A lower table, wrong stage or missing ingredient must refuse without proof. Remove only this unresolved tuple after the runtime proof.

Exact behavior command:

```sh
python3 run_tests.py test_construction test_quest_action_proofs
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count test_construction test_quest_action_proofs
```

## S07 — The Myreque sapphire preparation has no spell target

Rank: 5. Open record: Original line 3.

Cost evidence: The required Silvthrill-rod enchant action still lacks a genuine source-qualified target. Cost is tied with S05, S06 and S08.

Files: `data/magic_data.py`, `logic_pure/logic_pure_magic.py`, `data/quest_action_proof_data.py`, `data/quest/stage_cleanups.py`, `tests/test_magic.py`, `tests/test_quest_action_proofs.py`.

User interface change: Yes, a quest spell target becomes reachable.

Acceptance: At In Aid of the Myreque stage 6, cast the qualified enchant action on the real quest item. Emit Enchant sapphire for the Myreque preparations. A Quests review must advance 6 to 7. Undo must restore runes, item state, proof and stage. Ordinary sapphire jewellery and wrong-stage casts must not supply this quest proof. Remove only this unresolved tuple after the runtime proof.

Exact behavior command:

```sh
python3 run_tests.py test_magic test_quest_action_proofs
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count test_magic test_quest_action_proofs
```

## S08 — The Seergaze emerald preparation has no spell target

Rank: 5. Open record: Original line 3.

Cost evidence: The required emerald action remains source-blocked. Cost is tied with S05 through S07.

Files: `data/magic_data.py`, `logic_pure/logic_pure_magic.py`, `data/quest_action_proof_data.py`, `data/quest/stage_cleanups.py`, `tests/test_magic.py`, `tests/test_quest_action_proofs.py`.

User interface change: Yes, a quest spell target becomes reachable.

Acceptance: At Legacy of Seergaze stage 5, cast the qualified enchant action with its real emerald preparation. Emit Cast Enchant Level 2 Jewellery for the emerald preparations. A Quests review must advance 5 to 6. Undo must restore runes, quest item, proof and stage. Ordinary jewellery and wrong-stage casts must not emit this proof. Remove only this unresolved tuple after the runtime proof.

Exact behavior command:

```sh
python3 run_tests.py test_magic test_quest_action_proofs
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count test_magic test_quest_action_proofs
```

## S09 — The text-fit probe does not measure painted combo text

Rank: 6. Open record: Original line 24.

Cost evidence: The screenshot exposed a false negative, so a green probe cannot establish visual acceptance.

Files: `tests/ui_flows/qt_text_fit.py`, `tests/ui_flows/test_skills_panel_text_fit.py`.

User interface change: No; this slice repairs only the QA helper.

Acceptance: Use an editable combo with the exact Bronze platebody label and the reported constrained width. The helper must report the painted-text clipping before the geometry repair. A wide control with the same text must pass. Measure the actual editable text rectangle and horizontal position, rather than the control size hint. Preserve scrollbar and offscreen-widget exclusions.

Exact behavior command:

```sh
python3 run_tests.py ui_flows.test_skills_panel_text_fit
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count ui_flows.test_skills_panel_text_fit
```

## S10 — The selected alchemy item is clipped at the laptop sizes

Rank: 7. Open record: Original line 24.

Cost evidence: Two reported screenshots show the selected label tail; visual recovery requires another menu run.

Files: `ui/ui.py`, `tests/ui_flows/test_skills_panel_text_fit.py`.

User interface change: Yes, the alchemy selector geometry changes.

Acceptance: At 720 x 540 and 720 x 560, select Bronze platebody in magicAlchemyItemCombo. Show the full meaningful selected item text with no clipping or hidden start. Use the corrected probe from S09 and retain screenshots of both sizes. Check long labels and both themes. Perform the required visual check; no all-caps labels or decorative subtitle are added.

Exact behavior command:

```sh
python3 run_tests.py ui_flows.test_skills_panel_text_fit
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count ui_flows.test_skills_panel_text_fit
```

## S11 — The expanded Fremennik Isles card lacks exact fit proof

Rank: 8. Open record: Original line 5.

Cost evidence: The reported horizontal range was 84 at both heights; existing proof checks four other quests only.

Files: `ui/ui.py`, `tests/ui_flows/test_bank_quest_fit.py`.

User interface change: Unknown until the exact probe; yes if geometry needs repair.

Acceptance: Expand The Fremennik Isles card at 720 x 540 and 720 x 560 with the original blocker and journal content. Every visible quest scroller must have horizontalScrollBar().maximum() equal to zero. Visible text must have no clip, ellipsis or overlap. Preserve screenshots and the exact fixture. If this already passes, close from that exact proof without a geometry change.

Exact behavior command:

```sh
python3 run_tests.py ui_flows.test_bank_quest_fit
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count ui_flows.test_bank_quest_fit
```

## S12 — Malformed cache ID input reaches Integer.parseInt

Rank: 9. Open record: Original line 6.

Cost evidence: An avoidable raw Java exception forces a source-query retry.

Files: `tools/query_openrs2_cache_definitions.sh`, `tools/OpenRs2CacheDefinitionSearch.java`.

User interface change: No.

Acceptance: With a valid disposable disk cache, run a single --id with two numeric IDs and require both definitions. Repeat --id and use a nonnumeric ID. Each invalid call must exit 2 with a usage diagnostic and no NumberFormatException or stack trace. Validate before opening the cache or compiling where practical. Keep --params and --combat-levels argument rules consistent.

Exact behavior command:

```sh
python3 run_tests.py test_papercut_tools
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count test_papercut_tools
```

## S13 — The mirror fixture kills a process without reaping it

Rank: 10. Open record: Original line 12; duplicate line 13.

Cost evidence: Two green local fixture runs emit subprocess ResourceWarning and can obscure real verification failures.

Files: `tests/promotion/test_remote_mirror_lock.py`.

User interface change: No.

Acceptance: Run the existing mirror-lock fixtures with ResourceWarning enabled and allocation traceback enabled. The complete output must contain no still-running subprocess warning. Every process started by the fixture must be waited for after termination. Assert that no owned PID remains. Check the pass path and an assertion-failure cleanup path without terminating any foreign lane.

Exact behavior command:

```sh
python3 run_tests.py promotion.test_remote_mirror_lock
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count promotion.test_remote_mirror_lock
```

## S14 — The Slayer quick-finisher unlock has no purchase path

Rank: 11. Open record: Original line 4.

Cost evidence: Combat fixtures can set the flag, but a menu action cannot reach that state. No elapsed work cost was measured.

Files: `ui/ui.py`, `logic/slayer_logic.py`, `data/slayer_data.py`, `data/combat/slayer/slayer_finishers.py`, `tests/test_slayer_logic.py`, `tests/ui_flows/test_slayer_progress.py`, `tests/combat/test_encounter_lifecycle.py`.

User interface change: Yes, Slayer Rewards gains a working purchase.

Acceptance: From a qualified Smoking Kills save with exactly 400 Slayer points, buy Deliver killing blows quicker through the real Rewards surface. Deduct 400 points and persist slayer_quick_finishers_unlocked. A second purchase and a 399-point purchase must refuse without mutation. With the required finisher item present, a chained respawn must use the unlock; without the item it must remain locked. Verify save/reload and Undo.

Exact behavior command:

```sh
python3 run_tests.py test_slayer_logic ui_flows.test_slayer_progress combat.test_encounter_lifecycle
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count test_slayer_logic ui_flows.test_slayer_progress combat.test_encounter_lifecycle
```

## S15 — The asset audit sends an unsupported imageinfo parameter

Rank: 9. Open record: Original line 58.

Cost evidence: The API warning requires another source lookup; the same invalid parameter occurs in two callers.

Files: `tools/audit_asset_cutoff.py`, `tools/fetch_navigation_icons.py`, `tests/test_audit_asset_cutoff.py`, `tests/test_fetch_assets.py`.

User interface change: No.

Acceptance: Capture outgoing imageinfo queries for both callers. Neither query can contain iidir. Preserve iistart and newest-at-or-before selection. With mixed newer and period revisions, return only a qualified period revision or fail explicitly. Retain one live canary query without Unrecognized parameter: iidir.; redirect the audit report to an evidence path. Do not change fixed cutoff instruments or provenance hashes to satisfy the check.

Exact behavior command:

```sh
python3 run_tests.py test_audit_asset_cutoff test_fetch_assets
```

Exact count command for MacBook acceptance:

```sh
python3 run_tests.py --count test_audit_asset_cutoff test_fetch_assets
```

## Triage verification

The triage uses the unchanged docs selection tests.test_docs_audit tests.memory_bank_tools.
The local count is Matching tests: 20. The exact MacBook command is:

```sh
/opt/homebrew/bin/python3 tools/run_remote_tests.py "$PWD" plain --select tests.test_docs_audit --select tests.memory_bank_tools --expected-tests 20
```

Run the two separate integrity checks:

```sh
python3 tools/audit_docs.py
python3 tools/memory_bank/move_papercuts.py check 91cf104a
```

The first check validates docs syntax and paths. The second check validates exact preservation and disjoint open and fixed logs.
