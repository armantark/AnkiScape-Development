# Papercut triage — 2026-10-02

Base: `60d7bd83`. Branch: `goal/papercut-triage-2026-10-02`.
The base open log contains 56 entries. Six operator-friction records arose during this triage and its review resolution; all six were closed.
The final open log contains seven entries. All 55 closed occurrences remain verbatim in `../papercuts-fixed-2026-10-02.md`.

| Disposition | Base entries | New entries | Total |
| --- | --- | --- | --- |
| fixed | 11 | 0 | 11 |
| duplicate | 1 | 0 | 1 |
| record_only | 13 | 4 | 17 |
| documented | 24 | 2 | 26 |
| open | 7 | 0 | 7 |

## Open causes

### Entry 001 — Quest cleanup actions lack emitters

tests/test_quest_action_proofs.py:875 retains seven un-emitted cleanup actions. The round-shield action is repaired, but the other seven causes remain. The acceptance test preserves the source-blocked set rather than proving closure.

### Entry 002 — Slayer quick-finisher purchases are unavailable

ui/ui.py:8529 still shows a reward-purchase placeholder. References to slayer_quick_finishers_unlocked occur in finisher definitions and tests, with no runtime purchase writer.

### Entry 003 — Quest generation still depends on drifting source inputs

Equipment drift is fixed by 06324e44: the non-writing generation probe produced byte-identical equipment_data.py (/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/equipment-regeneration-diff.log). Quest generation still reads external Darkan NPC definitions (tools/build_pre_eoc_quest_catalog.py:90) and writes its whole output at line 2613. Commit 8b57b4da explicitly leaves that drift unresolved; no reproducible retained input/output check closes it.

### Entry 048 — HUD projection failures silently retain stale content

ui/ui.py:4165 still wraps ReviewHUD.set_data() in an outer except Exception: pass at lines 4183-4184. No error is surfaced or logged in that path; stale content can conceal the failing projection.

### Entry 055 — The Crafting repair awaits integration

tools/fetch_crafting_assets.py:175 still constructs HttpWikiClient() without before_timestamp. Lines 156-166 expose no cutoff or User-Agent options; tools/fetch_assets.py:123-133 supports both in the shared client. The command can still fetch current art on this tree. Commits 1fc5cb70 and 075e90a9 repair the client identity and cutoff on `goal/pass15b-logic-followups`. Neither commit is an ancestor of this slice or `main` at review time. Keep the exact open line until that repair is integrated and verified.

### Entry 030 — The reported expanded quest card lacks exact proof

Commit 7fd60fee repairs general quest width behavior. `tests/ui_flows/test_bank_quest_fit.py:91` covers four other quest cards at 720 × 560.
It never opens The Fremennik Isles card and does not cover 720 × 540. The reported horizontal maximum was 84 at both heights.
Return the original occurrence to the open log. The repair is present, but this exact case remains unverified.

### Entry 038 — Repeated ID flags raise a raw Java exception

`tools/query_openrs2_cache_definitions.sh` passes all trailing arguments to the Java reader without validation.
`tools/OpenRs2CacheDefinitionSearch.java:37` parses every token after the first `--id` with `Integer.parseInt`.
A second `--id` therefore raises the reported `java.lang.NumberFormatException: For input string: "--id"`.
Return the original occurrence to the open log. The documented CLI form does not excuse the raw exception.

## Verification evidence

The checked-in docs audit checks formatting, links and test selectors. The separate papercut check proves preservation and disjoint open/fixed logs.
The move helper does not accept `documented`; the direct move used its unchanged `problems` proof and locked file replacement.
The proof compares exact occurrence counts, so the repeated records remain present twice.

Evidence directory: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02`.
The original base log is `papercuts-before.md`. `triage-decisions.json` maps every occurrence to its disposition and checked evidence.
`archived-packet-checks.json` contains all 17 matching archived packet hashes.
`equipment-regeneration-diff.log` is empty because non-writing equipment generation matches every checked-in byte.
`test-collection-check.json` records 21 directly collected quest-action tests; the root focused runner also collected 21.
The docs selection is `tests.test_docs_audit tests.memory_bank_tools`; the root inventory contains 20 tests.
The exact audit output, papercut proof and remote result lines go to `docs-audit.log`, `papercut-check.log` and `remote-tests.log`.
These logs stay outside the checkout. Test results do not require a later edit to the tested documentation snapshot.

No code, test instrument, pinned baseline or canonical checkout file changes in this slice.

## Review resolution

The rows cover every finding from both reviews. Original incident lines remain verbatim, including historical paths.
Metadata and handoff paths are repo-relative. Host paths remain only where the paths are the incident evidence or machine inputs.

| Finding | Decision | Checked evidence and result |
| --- | --- | --- |
| A1: entry 050 probe repair | Applied | `ad5bbdfd` adds the rich-text `sizeHint()` branch after word wrap; `tests/ui_flows/qt_text_fit.py:58` retains it. Entry 050 is fixed. Its merge trap also has guidance. |
| A2 / B9: checkout-specific cache guidance | Applied | Removed “and absent from this worktree”. Dated host observations and added check-before-relying language for the archive, jq, cache and pyflakes shim. |
| B1: entries 004/018 and current ugrep wrapper | Applied documentation; rejected current-host assertion | Both entries are documented. A fresh `zsh -ic` reports `/usr/bin/grep`, BSD grep 2.6.0-FreeBSD, prints `aaa` for the reported regex, and finds no ugrep command. Guidance records the historical ugrep trap conditionally. `review-resolution-probes.json` retains the output. |
| B2: entry 023 | Applied | `8f70a917` landed on 2026-09-27, before the 2026-10-01 discrepancy. Reclassified as documented at `memory-bank/techContext.md:396`. Current counts agree; the historical wrong-checkout cause remains a hypothesis. |
| B3: entries 007/021/044/050 | Applied with A1 | `tools/worktree_guard.py:377` defaults to `main`. Added explicit `--start-point <family-branch>` or plain-merge guidance. Entries 007/021/044 are documented; entry 050 is fixed for the probe and also cites the guidance. |
| B4: disposable worktree paths | Applied | Removed this worktree prefix from archive metadata and this audit. Exact original incidents retain their paths. Promotion evidence paths remain absolute. |
| B5: entry 030 | Applied | The cited test opens four other cards at 720 × 560. Returned the occurrence to open because the exact Fremennik Isles case at both reported heights lacks proof. |
| B6: entries 006/020 | Applied | Added `User-Agent: AnkiScape parity audit` guidance that excludes personal identity. Both occurrences are documented. The existing audit client already uses that identity. |
| B7: entries 047/038 | Applied | A fresh PyQt6 probe confirms icon aliasing; documented the copy rule. The Java reader still parses a repeated flag as an integer; returned entry 038 to open. |
| B8: entry 003 | Applied | Kept the open line unchanged. The open-cause section cites `06324e44` and the byte-identical equipment probe. Quest generation still needs proof. |
| B9: other host observations | Applied | The four host observations now say “as of 2026-10-02” and require checks before reliance. Historical host evidence remains in `environment-checks.json`. |
| B10: ranked handoff and Crafting status | Applied | Copied the full ranked list below with repo-relative paths. Checked `1fc5cb70` and `075e90a9` on `goal/pass15b-logic-followups`; the repair is not yet on `main`. |

Review evidence is in the same absolute evidence directory: `review-resolution-probes.json`, `review-resolution-inventory.json`,
`review-resolution-papercut-check.log`, `review-resolution-docs-audit.log`, `review-resolution-docs-count.log`,
`review-resolution-remote-tests.log` and `review-resolution-commit.log`.
These logs describe the final documentation snapshot. Remote verification must run after the last documentation edit.

## Ranked fix slices — 2026-10-02

The reviewed triage leaves seven open records with thirteen causes. Seven causes share the cleanup-emitter record.
Base: `60d7bd83`. Run commands from the assigned repository checkout.

The rank uses observed work cost. It is not a measured runtime estimate.
Source checks and repeated catalog work cost most. Silent HUD failures conceal the next diagnostic step.

Scope: these are proposed slices. This triage changes no code.
Keep source-blocked actions blocked until qualified evidence permits each action. Do not relax tests or gates to claim closure.
Use the owner for source decisions. Do not invent period rules.
Each implementation slice must use its assigned checkout and the unchanged remote test runner.

| Rank | Cause | Open record | Cost evidence | User interface change |
| --- | --- | --- | --- | --- |
| 1 | Quest catalog generation reads mutable external sources | Entry 003 | Two records report unrelated stat rewrites and repeated output splices | No; preserve the checked-in catalog bytes |
| 2 | Oronwen cannot repair the mourner trousers | Entry 001 | Source qualification and failed full-catalog closure | Yes; a quest stage gains a real action |
| 3 | The clockwork penguin has no construction action | Entry 001 | Source qualification and failed full-catalog closure | Yes; a quest stage gains a real action |
| 4 | Telegrab cannot supply the quest water-channel key | Entry 001 | Source qualification and failed full-catalog closure | Yes; a quest stage gains a real action |
| 5 | Crumble Undead cannot record the boneguard action | Entry 001 | Source qualification and failed full-catalog closure | Yes; a quest stage gains a real action |
| 6 | The Silvthrill-rod enchant action is absent | Entry 001 | Source qualification and failed full-catalog closure | Yes; a quest stage gains a real action |
| 7 | No action collects evergreen sap | Entry 001 | Source qualification and failed full-catalog closure | Yes; a quest stage gains a real action |
| 8 | No action enchants the quest emerald preparation | Entry 001 | Source qualification and failed full-catalog closure | Yes; a quest stage gains a real action |
| 9 | HUD failures retain stale content without diagnostics | Entry 048 | A flow test can hide the real projection failure | Yes; clear failed content and expose a controlled error state |
| 10 | Crafting asset repair awaits integration | Entry 055 | A second fetch recovered the period revision; 1fc5cb70 and 075e90a9 repair this on goal/pass15b-logic-followups, not yet main | Yes; future icon selection changes |
| 11 | Slayer quick finishers have no purchase path | Entry 002 | The combat branch exists, but menu fixtures cannot reach the unlock | Yes; the reward shop gains the purchase |
| 12 | Repeated --id flags raise a raw exception | Entry 038 | A source probe failed without a CLI usage error | No |
| 13 | Expanded Fremennik Isles card lacks exact fit proof | Entry 030 | The earlier screenshots showed 84 px of horizontal scroll at both heights | Unknown until the exact probe runs |

## Shared acceptance rules

Use the exact worktree as the command directory. Collect each slice selection before its remote run.

```
python3 run_tests.py --count tests.test_quest_action_proofs
python3 tools/audit_docs.py
python3 tools/memory_bank/move_papercuts.py check 60d7bd83
```

For a remote run, use the count just collected as the literal `--expected-tests` value. No selected test can skip.
Use the plain lane for backend behavior. Use the Qt lane for widget behavior.
Every user interface change also needs the required PinchTab visual check. Check visible text for clipping.
Do not close an emitter from a catalog-only proof. The real action must emit its proof.

## 1. Quest generation must reproduce the retained catalog

Files: `tools/build_pre_eoc_quest_catalog.py`, `tools/combat/quest_stat_sources.py`, `tools/combat/quest_stat_sources.json`, `generated/quest_catalog_generated.py`, `tests/test_pre_eoc_quest_catalog_builder.py`.

Pin the external NPC and wiki inputs that supply the retained catalog. Eliminate unexplained output drift.
Equipment generation already reproduces its file exactly; it needs no new repair.
Acceptance: two runs with the same retained inputs must reproduce every checked-in byte and leave no unrelated combat-stat diff.

```
python3 tools/build_pre_eoc_quest_catalog.py
git diff --exit-code -- generated/quest_catalog_generated.py
python3 tools/build_pre_eoc_quest_catalog.py
git diff --exit-code -- generated/quest_catalog_generated.py
python3 run_tests.py --count tests.test_pre_eoc_quest_catalog_builder tests.test_quest_catalog
```

Run the unchanged selected tests remotely with the collected count. Retain input hashes and both output hashes.

## 2. Oronwen cannot repair the mourner trousers

Quest: `mournings_end_part_i`, stage `3`. Required proof: `Have Oronwen repair the mourner trousers`.

Files: `logic/shop/services.py`, `data/quest/catalog_overrides.py`, `data/quest/stage_cleanups.py`, `data/quest_action_proof_data.py`, `logic_pure/quest_action_proofs.py`, `tests/test_quest_action_proofs.py`.

Obtain qualified period evidence for this action and its exact inputs, gates, consumption and output.
Add the action at the existing runtime seam. Keep earlier quest-stage gates intact.
Acceptance: a real review action at this stage must emit the exact proof and clear this blocker.
A fixture without the required inputs must refuse the action and emit no proof.
Review undo must restore consumed items and remove the proof. An unrelated action must not emit this proof.
The full-catalog emitter check must stop listing this exact quest, stage and proof tuple.

```
python3 run_tests.py --count tests.test_quest_action_proofs
python3 tools/audit_item_reachability.py --json
```

Run the selected tests remotely with the collected count. Preserve a runtime trace for each acceptance case.
The reachability audit must preserve unrelated results. It does not replace the runtime proof.

## 3. The clockwork penguin has no construction action

Quest: `cold_war`, stage `2`. Required proof: `Build the clockwork penguin on a crafting table 3`.

Files: `data/construction_data.py`, `runtime/runtime_actions_production.py`, `data/quest/stage_cleanups.py`, `data/quest_action_proof_data.py`, `logic_pure/quest_action_proofs.py`, `tests/test_quest_action_proofs.py`.

Obtain qualified period evidence for this action and its exact inputs, gates, consumption and output.
Add the action at the existing runtime seam. Keep earlier quest-stage gates intact.
Acceptance: a real review action at this stage must emit the exact proof and clear this blocker.
A fixture without the required inputs must refuse the action and emit no proof.
Review undo must restore consumed items and remove the proof. An unrelated action must not emit this proof.
The full-catalog emitter check must stop listing this exact quest, stage and proof tuple.

```
python3 run_tests.py --count tests.test_quest_action_proofs
python3 tools/audit_item_reachability.py --json
```

Run the selected tests remotely with the collected count. Preserve a runtime trace for each acceptance case.
The reachability audit must preserve unrelated results. It does not replace the runtime proof.

## 4. Telegrab cannot supply the quest water-channel key

Quest: `spirits_of_the_elid`, stage `2`. Required proof: `Cast Telegrab for the water channel puzzle`.

Files: `runtime/runtime_actions_magic.py`, `data/magic_data.py`, `data/quest/stage_cleanups.py`, `data/quest_action_proof_data.py`, `logic_pure/quest_action_proofs.py`, `tests/test_quest_action_proofs.py`.

Obtain qualified period evidence for this action and its exact inputs, gates, consumption and output.
Add the action at the existing runtime seam. Keep earlier quest-stage gates intact.
Acceptance: a real review action at this stage must emit the exact proof and clear this blocker.
A fixture without the required inputs must refuse the action and emit no proof.
Review undo must restore consumed items and remove the proof. An unrelated action must not emit this proof.
The full-catalog emitter check must stop listing this exact quest, stage and proof tuple.

```
python3 run_tests.py --count tests.test_quest_action_proofs
python3 tools/audit_item_reachability.py --json
```

Run the selected tests remotely with the collected count. Preserve a runtime trace for each acceptance case.
The reachability audit must preserve unrelated results. It does not replace the runtime proof.

## 5. Crumble Undead cannot record the boneguard action

Quest: `enakhras_lament`, stage `5`. Required proof: `Cast Crumble Undead during the boneguard fight`.

Files: `runtime/runtime_actions_magic.py`, `logic_pure/logic_pure_quest.py`, `data/quest/stage_cleanups.py`, `data/quest_action_proof_data.py`, `logic_pure/quest_action_proofs.py`, `tests/test_quest_action_proofs.py`.

Obtain qualified period evidence for this action and its exact inputs, gates, consumption and output.
Add the action at the existing runtime seam. Keep earlier quest-stage gates intact.
Acceptance: a real review action at this stage must emit the exact proof and clear this blocker.
A fixture without the required inputs must refuse the action and emit no proof.
Review undo must restore consumed items and remove the proof. An unrelated action must not emit this proof.
The full-catalog emitter check must stop listing this exact quest, stage and proof tuple.

```
python3 run_tests.py --count tests.test_quest_action_proofs
python3 tools/audit_item_reachability.py --json
```

Run the selected tests remotely with the collected count. Preserve a runtime trace for each acceptance case.
The reachability audit must preserve unrelated results. It does not replace the runtime proof.

## 6. The Silvthrill-rod enchant action is absent

Quest: `in_aid_of_the_myreque`, stage `6`. Required proof: `Enchant sapphire for the Myreque preparations`.

Files: `runtime/runtime_actions_magic.py`, `data/magic_data.py`, `data/quest/stage_cleanups.py`, `data/quest_action_proof_data.py`, `logic_pure/quest_action_proofs.py`, `tests/test_quest_action_proofs.py`.

Obtain qualified period evidence for this action and its exact inputs, gates, consumption and output.
Add the action at the existing runtime seam. Keep earlier quest-stage gates intact.
Acceptance: a real review action at this stage must emit the exact proof and clear this blocker.
A fixture without the required inputs must refuse the action and emit no proof.
Review undo must restore consumed items and remove the proof. An unrelated action must not emit this proof.
The full-catalog emitter check must stop listing this exact quest, stage and proof tuple.

```
python3 run_tests.py --count tests.test_quest_action_proofs
python3 tools/audit_item_reachability.py --json
```

Run the selected tests remotely with the collected count. Preserve a runtime trace for each acceptance case.
The reachability audit must preserve unrelated results. It does not replace the runtime proof.

## 7. No action collects evergreen sap

Quest: `the_eyes_of_glouphrie`, stage `3`. Required proof: `Collect a bucket of sap from an evergreen tree`.

Files: `runtime/runtime_actions_utility.py`, `data/quest/catalog_overrides.py`, `data/quest/stage_cleanups.py`, `data/quest_action_proof_data.py`, `logic_pure/quest_action_proofs.py`, `tests/test_quest_action_proofs.py`.

Obtain qualified period evidence for this action and its exact inputs, gates, consumption and output.
Add the action at the existing runtime seam. Keep earlier quest-stage gates intact.
Acceptance: a real review action at this stage must emit the exact proof and clear this blocker.
A fixture without the required inputs must refuse the action and emit no proof.
Review undo must restore consumed items and remove the proof. An unrelated action must not emit this proof.
The full-catalog emitter check must stop listing this exact quest, stage and proof tuple.

```
python3 run_tests.py --count tests.test_quest_action_proofs
python3 tools/audit_item_reachability.py --json
```

Run the selected tests remotely with the collected count. Preserve a runtime trace for each acceptance case.
The reachability audit must preserve unrelated results. It does not replace the runtime proof.

## 8. No action enchants the quest emerald preparation

Quest: `legacy_of_seergaze`, stage `5`. Required proof: `Cast Enchant Level 2 Jewellery for the emerald preparations`.

Files: `runtime/runtime_actions_magic.py`, `data/magic_data.py`, `data/quest/stage_cleanups.py`, `data/quest_action_proof_data.py`, `logic_pure/quest_action_proofs.py`, `tests/test_quest_action_proofs.py`.

Obtain qualified period evidence for this action and its exact inputs, gates, consumption and output.
Add the action at the existing runtime seam. Keep earlier quest-stage gates intact.
Acceptance: a real review action at this stage must emit the exact proof and clear this blocker.
A fixture without the required inputs must refuse the action and emit no proof.
Review undo must restore consumed items and remove the proof. An unrelated action must not emit this proof.
The full-catalog emitter check must stop listing this exact quest, stage and proof tuple.

```
python3 run_tests.py --count tests.test_quest_action_proofs
python3 tools/audit_item_reachability.py --json
```

Run the selected tests remotely with the collected count. Preserve a runtime trace for each acceptance case.
The reachability audit must preserve unrelated results. It does not replace the runtime proof.

## 9. A failed HUD update must expose the failure

Files: `ui/ui.py`, `core/debug.py`, `tests/test_review_hud.py`.

Keep the Anki review safe. Replace the silent projection failure with a logged error and a controlled visible state.
Acceptance: after a valid card, force `ReviewHUD.set_data` to raise. The old card must disappear or show an explicit unavailable state.
The error must appear in the diagnostic log. The next valid projection must recover without an Anki restart.
The review itself must continue. No unrelated exception paths belong in this slice.

```
python3 run_tests.py --count tests.test_review_hud
```

Run the selected tests in the remote Qt lane and retain the forced-error trace.

## 10. Crafting asset fetches must select period art

Files: `tools/fetch_crafting_assets.py`, `tools/fetch_assets.py`, `tests/test_fetch_assets.py`.

Commits `1fc5cb70` and `075e90a9` already pin the client identity and cutoff on `goal/pass15b-logic-followups`.
The repair is not yet on `main`. Integrate that repair before writing another implementation.
The existing repair uses `AnkiScape parity audit` and ends the default window at `2012-11-19T23:59:59Z`.
Acceptance: a mocked wiki response with period and newer revisions must select only the period revision.
An empty period response must fail explicitly. No output or provenance file can change on a dry run.
The outgoing request must use the specified project User-Agent.
A retained Fremennik round-shield canary must resolve the 2010-03-26 revision, not the 2026-08-24 revision.

```
python3 run_tests.py --count tests.test_fetch_assets
uv run tools/fetch_crafting_assets.py --dry-run --item "Fremennik round shield"
git diff --exit-code -- crafteditems assets_provenance.json
```

Run the selected tests remotely with the collected count. Do the mocked non-writing cases before the network canary.

## 11. Slayer quick finishers need a real reward purchase

Files: `ui/ui.py`, `logic/slayer_logic.py`, `data/combat/slayer/slayer_finishers.py`, `tests/ui_flows/test_slayer_progress.py`, `tests/combat/test_encounter_lifecycle.py`.

Use the period 400-point reward and the existing Smoking Kills gate. Keep the backend purchase and menu work explicit.
Acceptance: before Smoking Kills, the menu must refuse the purchase. With 399 points, it must refuse without mutation.
With the prerequisite and 400 points, the menu must set `slayer_quick_finishers_unlocked` and debit exactly 400 points.
A second purchase must refuse without a second debit. A chained encounter must activate the finisher through that purchased flag.
Undo must obey the existing reward-purchase contract. Do not set the flag directly in the end-to-end purchase fixture.

```
python3 run_tests.py --count tests.ui_flows.test_slayer_progress tests.combat.test_encounter_lifecycle
```

Run the selected tests in the remote Qt lane with the collected count. Retain the purchase and chained-fight trace.

## 12. Invalid repeated ID flags need a usage error

Files: `tools/query_openrs2_cache_definitions.sh`, `tools/OpenRs2CacheDefinitionSearch.java`.

Acceptance: invoke the command with repeated `--id` flags against a disposable cache fixture.
The command must report a CLI usage error instead of `java.lang.NumberFormatException`.
The supported form with one `--id` and multiple numeric IDs must still return each requested definition.
The probe must leave the cache unchanged. Retain the exact commands, exit statuses and output.

## 13. Prove the expanded Fremennik Isles card fits

Files: `tests/ui_flows/test_bank_quest_fit.py`, `ui/ui_tab_quests.py`.

Use the reported quest state and expand The Fremennik Isles card. Run at 720 × 540 and 720 × 560.
Acceptance: each visible horizontal scrollbar must have maximum 0, and visible text must fit without clipping.
Retain screenshots, the quest state and the geometry output for both heights.
Change the interface only if the probe finds a defect. Keep the test instrument unchanged in this documentation slice.
