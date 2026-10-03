# Progress

This log keeps the current month. Earlier months rotate into `memory-bank/archive/` on the first session of each month; May to August 2026 is in [the May–August progress archive](archive/progress-2026-05-to-08.md), and the rotated September 2026 sections are in [the September progress archive](archive/progress-2026-09.md).

## Pass 15 owner notes — eight slices, 2026-09-30 to 2026-10-01

Ten notes from `~/Downloads/ankiscape notes.rtfd` (Pass 15, 2026-09-15 to 2026-09-30); rulings `design-thread-queue.md` §4.28, brief `codex-briefs/pass15-owner-notes-handoff-2026-09-30.md`. Opus 5.5 authored every slice at the owner's request; Kimi K3 reviewed five diffs and GPT-6.1 Sol the other three after Kimi's 5-hour limit (`403 You've reached your 5-hour usage limit`). Integration branch `goal/pass15-integration`.

- Finisher notice (`goal/pass15-finisher-notice`, 54196a1d, 416c2a86): "Wear Spiked gauntlets to finish" on its own amber HUD line; one event-log line per encounter, marked on the encounter record after the review found a missed warning on a new spawn and a repeat on Gargoyle regeneration.
- Bank trip target switch (ccba1926, e830d5b4, 01457f45): a target switch cancels a pending trip for another target.
- Fishing guide levels (a526d1b1): one guide row per fish at its own level; slimy eel 28; 2012 eel and frog spawn spots; the Lumbridge "Eel of Fortune" deed now counts a Raw cave eel.
- Silverlight and quest fights (9a2b4fc2, 9d03bf68, f244471b): every equippable quest reward is wearable (equipment count 994 to 1049); quest fights take ordinary ticks per review; Delrith needs a wielded Silverlight; the HUD names the boss.
- Barcrawl steps (a953836b): ten automatic stages at 2012 prices (208 coins); the shop drink rows and proofs are gone; quest-blocked dialogs list one reason per line.
- Belt tools (7bca9f86): the 2012 tool belt is one constant and one predicate for quests, Farming and Vinesweeper; ten bare-ground spade digs and the period exceptions stay held; the Bank Toolbelt panel lists the belt.
- Shop locks and purchase (1d401116, 5e3000e4): locked shops sort last, dim and name their reason; a purchase chip under Buy, green for success, amber for a refusal.
- Skill target search (eda7c2ed, 06fa2da4): every Skills-tab target list has the Combat search bar through `ui/ui_target_search.py`.

Merge repair (42adb030): eight module-surface digests, the root Qt digest and the equipment count re-pinned on the merged tree; the locked-shop wrap test fixed to a 240 px list because the test host's font fit the longest label (`382 not greater than 392`). First merged gate on a22202c6 failed only on those pins, that test, and three video status pages (fixed on main at 6637e281). Second gate on 231cdd1a with `--remote-lanes`: plain `Ran 5097 tests in 471.671s`, `OK (skipped=558)`; offscreen Qt `Ran 5097 tests in 686.769s`, `OK (skipped=5)`; documentation, test-quality, reachability, worktree, diff and papercut checks passed. Landed on main as 231cdd1a on 2026-10-01 01:30; the owner must restart Anki to load it.

Second level, not fixed: the combat chips line "Kills: N · Trains ..." clips at 192 px beside Bank run for aggressive and controlled styles on main today; Phoenix Lair still asks for Knife, Secateurs and Tinderbox in the bank; the flat target list clips long locked-row labels behind a horizontal scrollbar; skill guide rows dim only by level, not by quest lock; Count Draynor's garlic, Spiked gauntlets price, Do No Evil and Fremennik Isles purchase proofs, 90 of 293 quest encounters without stats.

## Carried-overlay forced-restock cleanup — 2026-10-02

Branch: `goal/carried-overlay-sixth-2026-10-02`; slice commit `d99ee5cb`; base main `60d7bd835c77b08f7040c67c77db4da7a233e648`.
Worktree: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-carried-overlay-sixth-2026-10-02`.
Evidence: [retained raw output](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/>). Nothing is copied into the repository.

The dispatcher delegates forced banking to `_bank_trip_forced`.
Its triggers are a manual request, a refillable processing shortage, or an Agility pack item the bank can restock.
The helper preserves short-circuit order and projects the Agility pack even on a manual request.
Actions, trips, inventory, messages, saves, and RNG behavior stay unchanged.
The review fixes change documentation and that helper's docstring only.

Historical slice metrics (CCN limit 15, cognitive limit 15, Halstead difficulty limit 80):

| Version / function | CCN | Cognitive | Halstead difficulty | NLOC |
| --- | ---: | ---: | ---: | ---: |
| Before / `run_answer_with_carried_overlay` | 66 | 66 | 8.25 | 189 |
| After / `run_answer_with_carried_overlay` | 57 | 61 | 8.038461538461538 | 173 |
| After / `_bank_trip_forced` | 10 | 5 | 3.0 | 21 |

The metric instruments exit 1 because the existing dispatcher exceeds the limits; the helper passes.
The slice grew the module from 968 to 977 lines, below the 1,000-line ratchet; the review docstring adds two lines.

Differential proof uses the frozen base overlay, copied inputs, and identical RNG seeds.
It compares return/exception, final state and dictionary order, callback arguments and snapshots, messages, saves, and RNG state.
It also compares directed forced-trip decisions and repack calls.
Counts: 12056 cases, comprising 56 directed and 12000 generated; 0 differences.
Outcomes: 11880 normal returns and 176 identical exceptions; all directed cases returned normally.
Directed coverage includes manual banking, processing shortages, Thread, belt tools, potion presence, Agility restocking, Keep/Drop, cadence, and Winter Storage rollback.
Raw pairs: [differential-cases.jsonl.gz](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/differential-cases.jsonl.gz>); source hashes and directed outcomes: [differential-result.json](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/differential-result.json>).

Focused inventories and both historical executions use the same nine selectors: 358 tests, zero runtime skips.
The full plain lane ran 5158 tests with 579 skips, leaving 4579 active tests.
Test-quality census: 5123 tests across 325 files, 0 hard issues, 32 structural clone groups.
No test, audit, pinned baseline, UI, Magic, Dream, or save format changed.

Each instrument below retains its exact command, result, exit code, raw log path, and SHA-256.
The before-run manifest is named `focused-before.json`; `focused-before.run.json` is absent.

- metrics-before: `python3 tools/maintenance/function_metrics.py --output '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/metrics-before.json' runtime/runtime_actions_carried_overlay.py run_answer_with_carried_overlay`; `run_answer_with_carried_overlay: ccn 66 > 15; cognitive 66 > 15`; exit `1`; [metrics-before.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/metrics-before.log>); sha256 `3291d47bf4e51689ca8a1dc0b0f936cd06b3e4f0b235c7d38cc5957f9a0c4828`.
- metrics-after: `python3 tools/maintenance/function_metrics.py --output '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/metrics-after.json' runtime/runtime_actions_carried_overlay.py run_answer_with_carried_overlay _bank_trip_forced`; `run_answer_with_carried_overlay: ccn 57 > 15; cognitive 61 > 15`; exit `1`; [metrics-after.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/metrics-after.log>); sha256 `9044c05e63cf56d48617293f4500c4894ce1a48bd13e135802e2442aae148f7c`.
- lizard-before: `/Users/ArmanTarkhanian1/.local/bin/lizard runtime/runtime_actions_carried_overlay.py`; `189     66   1071      3     223 run_answer_with_carried_overlay@746-968@runtime/runtime_actions_carried_overlay.py; 189     66   1071      3     223 run_answer_with_carried_overlay@746-968@runtime/runtime_actions_carried_overlay.py`; exit `1`; [lizard-before.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/lizard-before.log>); sha256 `59d96910861fa04ea302e4e4707c860a1fa87e73eae88f8c4253f5a947ef6844`.
- lizard-after: `/Users/ArmanTarkhanian1/.local/bin/lizard runtime/runtime_actions_carried_overlay.py`; `21     10    125      3      23 _bank_trip_forced@325-347@runtime/runtime_actions_carried_overlay.py; 173     57    985      3     207 run_answer_with_carried_overlay@771-977@runtime/runtime_actions_carried_overlay.py; 173     57    985      3     207 run_answer_with_carried_overlay@771-977@runtime/runtime_actions_carried_overlay.py`; exit `1`; [lizard-after.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/lizard-after.log>); sha256 `b59b934900465ba92e53ad45b1084dbb3986da2db126dad8c6b58653036fa9af`.
- differential: `PYTHONHASHSEED=0 python3 '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/differential.py' '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-carried-overlay-sixth-2026-10-02'`; `Differential: 12056 cases (56 directed, 12000 generated), 0 differences`; exit `0`; [differential.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/differential.log>); sha256 `44ac6db048fe1a4116ef95aee266b5de5e8f1bac57c8169f100901ae4b0a7f0f`.
- focused-before: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-carried-overlay-sixth-2026-10-02' plain --select test_runtime_actions. --select test_agility. --select test_urns. --select test_cadence_live. --select test_summoning_logic. --select runtime_actions.test_winter_storage_rollback. --select test_skilling_boost_logic. --select test_promotion_gate. --select test_memory_bank_queue_packet. --expected-tests 358`; `Ran 358 tests in 57.957s; OK`; exit `0`; [focused-before.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/focused-before.log>); sha256 `75e4c12a9284f8a40c5b8af8b4c81d024245cb1f55ec53288cc714537b2e93a5`.
- focused-after: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-carried-overlay-sixth-2026-10-02' plain --select test_runtime_actions. --select test_agility. --select test_urns. --select test_cadence_live. --select test_summoning_logic. --select runtime_actions.test_winter_storage_rollback. --select test_skilling_boost_logic. --select test_promotion_gate. --select test_memory_bank_queue_packet. --expected-tests 358`; `Ran 358 tests in 58.307s; OK`; exit `0`; [focused-after.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/focused-after.log>); sha256 `cb1296b5fcf6493bb249a76603ce65382693ea9563dfcb8729f4d7af89ec3ceb`.
- full-plain: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-carried-overlay-sixth-2026-10-02' plain`; `Ran 5158 tests in 446.584s; OK (skipped=579)`; exit `0`; [full-plain.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/full-plain.log>); sha256 `ca3e4a7f77e3509b85a6769be55b7fdbfc0965cffa7a22c447e5323d879e5041`.
- audit-docs-final: `python3 tools/audit_docs.py`; `Documentation audit passed.`; exit `0`; [audit-docs-final.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/audit-docs-final.log>); sha256 `2ce690c0d78847042e453fc95901b5852eee596700cd9ef1698c10fe1d5c00a9`.
- audit-test-quality: `python3 tools/audit_test_quality.py`; `5123 tests across 325 files; hard issues: 0; structural clone candidates: 32 groups`; exit `0`; [audit-test-quality.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/audit-test-quality.log>); sha256 `8f311b6ed1fd216255cf3a718557e35da9f6b5696e97d7e473e63a87ae2435bb`.
- audit-item-reachability: `python3 tools/audit_item_reachability.py --check --summary`; `1671 actions; 2354 reachable items; 161 orphan inputs; 246 blocked actions`; exit `0`; [audit-item-reachability.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/audit-item-reachability.log>); sha256 `8ae298a4e731ca7aa193b5a62b6cae20c3e6964de195f3d05d5365c0b3788057`.
- audit-worktree-guard: `python3 tools/worktree_guard.py audit`; `Worktree layout safe`; exit `0`; [audit-worktree-guard.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/audit-worktree-guard.log>); sha256 `cc6202cc6351917cf1a616a7e6260503ba977a2974a999173c9d89c038c3f572`.
- diff-check-final: `git diff --check`; `(no output)`; exit `0`; [diff-check-final.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/diff-check-final.log>); sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Count argv: `python3 run_tests.py --count test_runtime_actions. test_agility. test_urns. test_cadence_live. test_summoning_logic. runtime_actions.test_winter_storage_rollback. test_skilling_boost_logic. test_promotion_gate. test_memory_bank_queue_packet.`; `Matching tests: 358`; exit 0; [focused-inventory.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-carried-overlay-sixth-2026-10-02/focused-inventory.log>); sha256 `8ece6e54fc6c2e0dc97af2d18c234789dfd5dbb78ae6147b11b4762d3103dcd1`.
Reachability matches the fixed main baseline; archived historical counts and every pin remain unchanged.
The orchestrator must run both full lanes on the merged tree through the promotion gate.
Remaining dispatcher responsibilities and its existing over-limit complexity are outside this slice.
