# AnkiScape goal handoff to the MacBook Pro

Saved: 2026-10-14 01:24:49 UTC (2026-10-13 Pacific time).

## Start here

Continue this goal on the MacBook Pro (MBP). The owner asked the local agent to stop new work and save this handoff.

The goal remains active. This handoff does not claim completion, a global blocker, or a pause.

Read `memory-bank/goal-text-2026-10-13.md` for the exact goal text. Its final paragraph overrides the earlier blocker-as-success sentence.

Use `memory-bank/goal-priority-matrix.md` for the work order. Use current `AGENTS.md` and `memory-bank/README.md` for project rules and discovery.

## Source and ownership

The local canonical checkout was clean at `7f2b9efbec7a87d8079e8ae2ecd3b476a6f76a51` during this handoff:

`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`

The Root source checkout uses branch `goal/test-log-io-2026-10-13`, based on that main commit:

`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/promote-runner-fairness-2026-10-03`

The handoff commit contains these notes, the exact goal text, and a prepared regression test. Read its final revision with `git rev-parse HEAD`.

The Root documentation branch remains `codex/ernest-poison-pickup-2026-10-08` at `229e002e`:

`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/promote-tools-docs-2026-09-27b`

No agent owns the test mirror or GUI. The last source review leaf completed. No proof process remains active from this turn.

Confirm the real Git checkout and preserved refs after the owner moves the task. Do not use the rsynced test mirror as a Git checkout.

The small transfer packet also contains `goal-branches.bundle`. It preserves the I/O branch, the Tribal Totem branch, and the Root documentation branch.

Run `git bundle verify` before an import. The bundle requires the main history through `7f2b9efb`. Keep existing divergent refs unchanged.

The packet does not replace the full local proof archive. Preserve that archive on the original host and obtain needed receipts from it.

Do not repeat successful checks because their original files remain on the original host.

The existing MBP test mirror is `/Users/armantarkhanian/ankiscape-remote-test-host/ankiscape_fork`. The mirror has disposable files.

Keep the canonical add-on as the only enabled AnkiScape checkout under `addons21`. Use the existing worktree guard for worktree operations.

## Immediate unfinished unit: test I/O

The owner asked for bounded test artifacts and fewer SSD reads and writes.

The existing remote runner reads the complete log on every poll. The independent Sol source review recommends report-only polls.

`tests/promotion/test_remote_poll_deadlines.py` now contains `test_wait_reads_complete_log_once_after_report_and_stop`.

The test uses real shell reads from disposable files. It requires no live-log read, a confirmed stop, and one complete final-log read.

Only the regression test exists. Root did not change the runner. Root did not execute this regression or obtain a failure receipt.

The completed MBP inventory returned `Matching tests: 4` for `tests.promotion.test_remote_poll_deadlines`. Its original receipt reports exit status 0.

The existing evidence directory is:

`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/goal-resume-2026-10-06/reset-70/test-log-io-2026-10-13`

It contains `baseline-inventory.receipt.json` and `baseline-inventory.log`. There is no baseline execution, candidate pass, review acceptance, or promotion certificate.

1. Preserve and inspect the inventory receipt.
2. Obtain the baseline failure before the runner edit.
3. Remove repeated full-log reads from `tools/run_remote_tests.py`.
4. Preserve complete output after `stop_pending_lane()` confirms the stop.
5. Preserve report deadlines, SSH retries, stop failures, exact counts, skips, and exit-code checks.
6. Update the existing deadline and transport tests for report-only polls.
7. Obtain focused checks and an independent cross-lineage review.
8. Use the exact full promotion gate before the official land command.

The relevant existing tests are `tests/test_remote_test_host.py`, `tests/promotion/test_remote_poll_deadlines.py`, and `tests/maintenance/test_remote_storage.py`.

The existing test file `tests/test_remote_test_host.py` exceeds the growth ratchet. Keep its net line growth at zero.

Inspect `test_stream_reloads_log_after_completion_report_appears` near line 983. Its canned SSH sequence includes the live-log read.

Keep the late-completion refusal. Keep the unresolved-run refusal after a report-poll failure. Print the complete final output once.

Report-only polls delay console output until completion. Timeout diagnostics remain in the exact remote log announced at launch.

Do not create another runner, checker, retention layer, or audit. Use the current proof wrapper and tools.

## Existing storage protections

Main already contains the storage changes. Independent APFS clones prevent full byte copies for native apps, add-ons, and launch snapshots.

New proof subprocess files have a 256 MiB limit. Retained packets have a 256 MiB file limit and a 1 GiB packet limit.

Eligible remote success reports expire after seven days. Retention also limits eligible reports to 128 groups and 64 MiB.

Failures, unresolved runs, unknown files, pins, open files, native packets, Git state, and exact acceptance stores remain protected.

The four large equivalence dumps contain audited complete captures. Existing compaction already shares duplicate bytes through APFS clones.

Do not delete these captures from a `du` total. Do not claim logical file totals equal unique physical storage.

Use bounded file discovery and projected fields. Avoid full recursive inventories, whole-file dumps, repeated hashes, and repeated successful product runs.

## Prepared Tribal Totem unit

Preserve branch `goal/tribal-totem-recovery-2026-10-13` at `9928e1213e50c090d437c528312567fd07fb5d21`.

Product commit `b6a7789398df5ae6c18888743528160b42a297c7` corrects lost Address label and Totem recovery, and mansion action order.

The original focused receipt reports 41 Qt tests with no skips. The original Opus review approves the exact product diff.

The original full gate passed all nine checks on `9928e121`. These source checks remain authoritative.

The original certificate SHA-256 is `e7f4717de4aec08ed82216192499ac8a84f3075921f57e47677f7d46fe5d924b`.

The dedicated native task saved the queue entry in commit `5c72155`. It created no case, profile, GUI session, or source transfer.

Native and visual acceptance remain false. Tribal Totem has not landed. Preserve current main changes during later integration.

The evidence directory is:

`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/goal-resume-2026-10-06/reset-70/tribal-totem-recovery-2026-10-13`

Read the original `accepted/retention-manifest.json` and `source/retention-manifest.json`. Do not repeat successful product checks for bookkeeping.

## Native queue and standing authorization

Use the dedicated task “Verify AnkiScape in native Anki”:

`01a0c67a-3e19-76c2-804c-65d993c9dddc` on `remote-control:env_e_6a684c98946c8321ba89026140dd59e4`.

Its project path is `/Users/armantarkhanian/Documents/ankiscape-testing`.

The owner gave standing authorization for prepared checks to that task and required screen-use notices to “Restore Darkan content fidelity”.

The owner authorized all future reviews and review-packet exports. Do not ask again for ordinary reviews or these two authorized message routes.

Other sibling messages and source-harvest doorbells require their own authorization. Do not broadcast runtime or tool updates.

Keep one GUI owner. If the MBP is unavailable, add prepared manual checks to the existing queue and continue independent work.

Keep the original startup and literal saved-Undo-to-pre-Good-LIVE criteria. Do not substitute saved-to-saved comparisons or coerce values.

The original Salt case failed startup and closed unaccepted. Do not retry that closed case or extend the unanswered Salt-only proposal.

Historical failure status is UNVERIFIED in newer main records. That wording does not waive the native task's last confirmed strict holds.

Reuse all existing queued packets and receipts. The current matrix, native brief, and existing goal plan own the complete queue.

## Next source unit after I/O

Gunnar’s Ground has a complete source analysis. Its artwork and post-quest Crafting consumer remain unfinished.

The ordinary Gold ring cannot substitute for Gunnar’s ring. Existing named asset/provenance searches found no Gunnar quest artwork.

Retained literal sources exist in the Darkan memory bank at:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/gunnars-ground-final-pre-eoc-oldid-6387575.json`

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/gunnars-ground-build727-oldid-5977399.json`

Oldid `6387575` is dated 2012-10-12 and has no Combat beta template. Preserve the source hierarchy and qualifications.

Dororan owns the post-quest jewellery. The three tasks grant Crafting XP once, in ruby, dragonstone, then onyx order.

These tasks use effective levels 42, 72, and 90. The tasks consume no player jewellery and produce no player jewellery.

Current `CraftingRecipe` requires an output. `apply_crafting_pure` always adds an output and cannot advance a once-only task sequence.

`output_qty=0` becomes one. A missing output falls back to the target ID. Do not use either workaround.

`handle_crafting_answer` has effective-level gates and review XP, but no once-only sequence for Dororan.

`crafting_target_rows` always shows an output. A new XP-only task must not advertise a false item.

Missing implementation is work to complete, not an external blocker. Do not ship a narrow substitute or mandatory-Haakon-only repair.

The migrated expansion skill still describes a retired 2011 baseline. The binding source standard requires the cutoff 2012-11-20.

Do not change that cutoff or reinterpret modern OSRS art as period proof. Do not repair skills as part of this goal handoff.

## Delivery rules

Use at most 70% shared Codex quota after the reset. The quota is a ceiling, not a target.

Finish and land current authorized units before unrelated cleanup. Keep complete player paths and all reserved owner decisions.

Keep existing UI outside scope without recorded authorization. New feature UI needs the required taste review.

Commit atomically through normal hooks. Never push, force, hard-reset, change Git config, or skip hooks.

Do not weaken tests, audits, caps, source qualifications, or pinned baselines. Use official promotion commands.

Give concrete updates: what now works, what landed, and the exact next check. Do not report unmeasured whole-goal percentages.

Keep this local agent idle after the handoff. Resume substantive work on the MBP after the owner moves the task.

