# Papercuts fixed — 2026-10-17

## Documentation records and artifact retention repaired on main

Disposition: fixed.

Evidence: Main 8749ddc6 passed python3 tools/audit_docs.py before this batch (baseline-docs.log in the external batch evidence directory): 1014 Markdown and 458 HTML files; startup total 2982. The fixed 3000-line cap, local links, papercut bullets and HTML targets all passed. Commit 06480995 tracks memory-bank/status-updates/goal-pause-results-2026-10-03.mp4; a6ebdd30 tracks shared-cap-results-2026-10-03.mp4 and the exact pause text archive; ee15373e preserves the four merged historical entries; 77b2c1f7 moves the correction section into the dated fixed log discovered by the checker. Archive link corrections include d1043c69. These repair the recorded missing targets, malformed records and excess startup history; no product proof is inferred from documentation success.

- 2026-10-03T18:13:00Z — Queue-record repair gate inspection: the exact historical HTML references goal-pause-results-2026-10-03.mp4, but tools/promotion/snapshot.py clones committed files and links only .venv-qt; an ignored video copy does not reach the gate snapshot. Root must resolve artifact retention before promotion; the HTML and audit instrument remain unchanged.
- 2026-10-04T01:44:04.199850+00:00 Documentation checkpoint audit refused three new rows with papercut_without_bullet; corrected the three literal rows and normalized their queued entries before retry.
- 2026-10-07T02:34:28.571774+00:00 Documentation promotion at 3e714e2e15dba3281b46422ff6490b8821e798cf exited 2: `audit_docs (exit 1)`; `Documentation audit found 6 issue(s).` Exact reported targets include `memory-bank/papercuts.md:189: papercut_without_bullet` and `memory-bank/status-updates/shared-cap-results-2026-10-03.html:40: broken_html_target: shared-cap-results-2026-10-03.mp4`. No landing occurred; preserved full log at `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/3e714e2e15dba3281b46422ff6490b8821e798cf/documentation-gate-failure-2026-10-06/gate-3e714e2e.log`. Repair and a fresh gate wait for renewed allowance.
- 2026-10-07T04:17:55.964586+00:00 Exact pause archival first used `.md`; audit_docs exited 1 with four `broken_local_link` findings because the original links are relative to memory-bank. Root preserved the exact bytes as `memory-bank/archive/2026-10/handoffs/goal-pause-2026-10-06.txt` instead of modifying historical text.
- 2026-10-07T15:58:54.047346+00:00 Documentation update copied two bare timestamped proof notes and exceeded the fixed startup budget: papercut_without_bullet at memory-bank/papercuts.md:246 and :247; startup_line_budget_exceeded: 3002 startup lines must stay under 3000. Resolved probe/path/output frictions were moved verbatim to papercuts-fixed.md with valid bullets; rerun pending.
- 2026-10-07T18:25:22Z — Bounded acquisition notes pushed the startup audit to `3002 startup lines must stay under 3000: memory-bank/activeContext.md=69, memory-bank/progress.md=886, memory-bank/future-work-kanban.md=1580, memory-bank/goal-priority-matrix.md=221, memory-bank/loop-queue.md=0, memory-bank/papercuts.md=246`; rotated the exact historical October 3 checkpoint with a linked breadcrumb; fresh audit is pending.
- 2026-10-07T18:26:59Z — Moving the exact historical checkpoint required three relative-link changes: audit reported `memory-bank/archive/progress-2026-10-checkpoints.md:5: broken_local_link: plans/goal-2026-10-03.md`, `:8: broken_local_link: pickup-2026-10-03.md`, `:19: broken_local_link: archive/2026-10/handoffs/goal-pause-2026-10-03-evidence.md`; changed only the relocated link targets.
- 2026-10-07T19:36:00+00:00 Root documentation check rejected two appended friction entries as `papercut_without_bullet`; added the existing ledger bullet prefix and reran the fixed audit.
- 2026-10-07T21:35:51.020040+00:00 — Merging verified carried source with current acceptance records conflicted only in memory-bank/papercuts-fixed.md. Removed conflict markers and preserved all four distinct historical entries from both sides; merge commit ee15373e completed through normal hooks.
- 2026-10-08T00:26:00+00:00 Docs update hit `papercut_without_bullet` and `startup_line_budget_exceeded: 3003 startup lines must stay under 3000`; restored the required bullet and removed duplicated death-proof detail from activeContext.md, with the exact proof preserved in GOAL-BLOCKED.md and the source checkpoint.
- 2026-10-08T00:27:00+00:00 The first Docs budget repair still measured `3001 startup lines must stay under 3000`; measured all five files and removed two redundant activeContext.md paragraphs already preserved in the source checkpoint and dated progress records.
- 2026-10-14T09:52:33.762348+00:00 — Preflight record restructuring moved the historical activeContext paragraph into memory-bank/archive/progress-2026-10-checkpoints.md before rebasing its six local links. audit_docs.py returned six broken_local_link findings for source-audits/local-test-host-2026-10-14.md, plans/goal-2026-10-03.md, GOAL-BLOCKED.md, plans/goal-resume-2026-10-06.md, goal-priority-matrix.md and pickup-2026-10-03.md. The raw original is preserved with its digest; archive links now use the correct parent context. No product checks were replayed.
- 2026-10-15T05:22:56.903582+00:00 — Archiving the closed812e0ec1 summary left a relative link at its former depth: `memory-bank/archive/progress-landed-test-cleanup-2026-10-14.md:18: broken_local_link: source-audits/asset-cutoff-landed-2026-10-14.md`; docs exited1. The normal checkpoint commit still succeeded; record-only repair rebases the link and removes the trailing EOF blank reported by git diff --check, without replaying product checks.
- 2026-10-15T06:17:29.650258+00:00: Familiarisation docs audit refused `startup_line_budget_exceeded: 3002 startup lines must stay under 3000: memory-bank/activeContext.md=44, memory-bank/progress.md=808, memory-bank/future-work-kanban.md=1580, memory-bank/goal-priority-matrix.md=179, memory-bank/loop-queue.md=0, memory-bank/papercuts.md=391`; retain the same complete linked navigation archive used by the Restaurant slice, without changing the cap.
- 2026-10-15T08:09:19.259037+00:00: Quest records reached the unchanged startup limit exactly3000 lines after adding incident records. Archived only the already-landed October2–3 mirror implementation/review chronology, preserving every nonempty line and linking its current source-tool/papercut successors. Bounded progress excerpts also exceeded the aggregate output budget; archive preservation uses exact original bytes rather than truncated display. No audit limit changed.
- 2026-10-15T13:25:55.007027+00:00: Exact records gate 0ff58361043f3379c096f7b05e60e0239217eef3 returned2 after plain5376/597.794s/skipped580 and Qt5376/812.717s/skipped5 passed. Papercut checker reported four "lost:" entries because the corrected lines were in papercuts-fixed.md, outside its dated papercuts-fixed-*.md discovery. Move the complete correction section verbatim to papercuts-fixed-2026-10-15.md; keep the checker unchanged and retain both original lane results. No certificate or land is accepted.
- 2026-10-15T14:00:55.172435+00:00: The stock documentation audit returned1 after the required R21–24/review incidents were banked: "startup_line_budget_exceeded: 3013 startup lines must stay under 3000" (activeContext44, progress674, future-work-kanban1580, goal-priority-matrix184, loop-queue0, papercuts531). Preserve every incident and the fixed3000 cap. Move only the retired Rulesync verification history to a linked archive; current tracked AGENTS.md supersedes that removed mechanism. Original audit log: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/records-startup-history-move/records-startup-before-history-move-uitbbyuk.log.
- 2026-10-15T15:52:44.351254+00:00 — Integrating the independently reviewed preflight candidate into the source-record branch failed the unchanged documentation audit: `startup_line_budget_exceeded: 3001 startup lines must stay under 3000`, with activeContext45, progress567, future-work-kanban1580, goal-priority-matrix184, loop-queue0 and papercuts625. Original failure is retained in `records-integrated-startup-budget-tm1f35xb.log`; closed Equipment source history is preserved verbatim in a linked archive, with current work still owned by the matrix. No limit or incident content is removed.
- 2026-10-15T06:02:04.674462+00:00: Restaurant source docs audit refused `startup_line_budget_exceeded: 3005 startup lines must stay under 3000: memory-bank/activeContext.md=44, memory-bank/progress.md=808, memory-bank/future-work-kanban.md=1580, memory-bank/goal-priority-matrix.md=179, memory-bank/loop-queue.md=0, memory-bank/papercuts.md=394`; moved the complete closed navigation evidence to its linked archive, without changing the3000 cap.
- 2026-10-15T13:47:26.790086-07:00: Jad primary native record audit returned actual1: `startup_line_budget_exceeded: 3006 startup lines must stay under 3000: memory-bank/activeContext.md=52, memory-bank/progress.md=533, memory-bank/future-work-kanban.md=1580, memory-bank/goal-priority-matrix.md=184, memory-bank/loop-queue.md=0, memory-bank/papercuts.md=657`. The already accepted Familiarisationf2 history archive will be preserved by normal integration; no cap or incident is removed.
- 2026-10-15T09:02:40.588793+00:00 — Familiarisation exact gatea06454c4e14c3b4e0a5339ab6b893c94f3745391 returned actual2 after both full lanes passed; `startup_line_budget_exceeded: 3001 startup lines must stay under 3000`. The reviewed69-nonempty-line remote-mirror archive repairs records only; original product receipts remain accepted, native/visual/land remain false. Root recovery reads also exceeded output budgets; bounded projections replace full diff/log reads.
- 2026-10-15T13:14:57.945392-07:00: Familiarisation promotion docs audit refused `startup_line_budget_exceeded: 3007 startup lines must stay under 3000` (active48/progress529/kanban1580/matrix184/queue0/papercuts666). Preserve the complete26-line Automatic potion source history verbatim in its linked archive; do not change the3000 cap or any product proof.
- 2026-10-15T14:15:04.163041-07:00: Merged Jad record audit99229 actual1: `startup_line_budget_exceeded: 3000 startup lines must stay under 3000: memory-bank/activeContext.md=48, memory-bank/progress.md=507, memory-bank/future-work-kanban.md=1580, memory-bank/goal-priority-matrix.md=184, memory-bank/loop-queue.md=0, memory-bank/papercuts.md=681`. Preserve closed October7–8 proof paragraphs verbatim in a linked archive to unblock this named Jad merge; cap and open incidents stay intact.
- 2026-10-15T14:16:57.506328-07:00: Jad archive audit5619 actual1 found two `broken_local_link: source-audits/cleanup-source-checkpoint-2026-10-04.md` entries in memory-bank/archive/progress-landed-native-checkpoints-2026-10-07-08.md at5/7 after a directory move. Kept exact original paragraphs SHA256357bec16dbde66ebb5e2b33d58ac874f197b5dd7e8a803da40741b33bf49ce26 in native evidence and rebased only those two link targets; native checks were preserved.
- 2026-10-15: Named Tribal merged docs audit refused "startup_line_budget_exceeded: 3005 startup lines must stay under 3000" (activeContext48, progress501, future-work-kanban1580, matrix184, loop0, papercuts692). Historical October2 dragonfire source/metric/test receipts are retained verbatim in the linked archive with original SHA binding; current native obligations and cap3000 stay unchanged.

## Cache CLI arguments and index lookup repaired

Disposition: fixed.

Evidence: Commit b4e9a6ad repairs numeric argument parsing and explicit index lookup in tools/OpenRs2CacheDefinitionSearch.java. tests/test_papercut_tools.py:814 OpenRs2DefinitionArgumentTests executes the synthetic disk-cache CLI, including multi-ID mode and malformed arguments. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-03T13:33:32-07:00 — S12 final F3 API verification: the root brief assumed Store.getIndex(int), but the actual installed core2.0.5 Store API exposes getIndex(IndexType) and getIndices() only; root corrected the lookup to one explicit getId() value and getIndices()[indexId].
- 2026-10-03T13:54:26-07:00 — S12 F3 incident qualifier for 2026-10-03T13:33:32-07:00: there is no Store.getIndex(int) overload; getIndex(IndexType) and getIndices() were the APIs considered for this lookup, not a complete inventory of Store methods.

## Source image queries and historical timestamp complexity repaired

Disposition: fixed.

Evidence: Commit da02e004 preserves named query parameters in tools/fetch_assets.py:382 and places its HTTP regressions in tests/historical_assets/test_fetch_assets_source_urls.py:65. Commit 812e0ec1 reuses validated historical timestamps and removes the redundant empty-imageinfo branch. The exact Crumble Undead SHA1 repair is documented in memory-bank/audits/source-url-query-repair-2026-10-03.md:17. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-02T20:34:14-07:00 — Period-icon verification: `tools.fetch_assets._download_source_bytes` raised `Downloaded bytes did not match the API SHA1 for File:Crumble Undead icon.png.` after `_source_image_url` nested `format=original` inside `source`; the exact provenance URL returned a PNG of 297 bytes with expected SHA-1 `263b75038c03b742bdfa93843623f38a656896b7`, and its normalized bytes match the worktree candidate. General URL rewriting is outside this emitter slice; raw source is in `asset-period-confirmed-final.log` and `period-source-final.png` in the slice evidence folder.
- 2026-10-03T19:01:16.909341+00:00 Source URL slice commit: slop-gate refused `tests: 237 code files (was 236)` because the directory already exceeds 40 files; move the cohesive HTTP suite into existing `tests/historical_assets/`, preserving the gate. During repair, a guessed fixture read returned `sed: tests/historical_assets/test_source_ledger.py: No such file or directory`; use the discovered `test_fetch_2012_icons.py` path instead. Final new selector is `tests.historical_assets.test_fetch_assets_source_urls`.
- 2026-10-14T03:51:23.889660-07:00 — S15 correction commit refused by installed slop-gate: period_image_info and both _period_image_info functions measured cyclomatic16 (was13), above cap15. Reuse each validated timestamp in ImageInfo rather than decoding the same field twice; no cap or hook change. Preserve original successful canary/proof receipts and recheck final source metrics.
- 2026-10-14T22:56:41.453772+00:00 — Historical timestamp repair commit refused: slop-gate reported `HttpWikiClient::query_image_info` cognitive16 (was15), above15. Remove the redundant empty-imageinfo branch already covered by empty eligible selection; retain every timestamp/type/cutoff guard and every fixed limit.

## API warnings now reach diagnostics without losing valid results

Disposition: fixed.

Evidence: Commit 69a22761 emits API warnings from tools/fetch_assets.py:206. tests/test_fetch_assets.py:105 and :125 exercise silent controls, payload preservation and warning propagation through both the downloader and cutoff auditor. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-14T11:42:56.353089+00:00 — S15 Opus review O6: `tools/fetch_assets.py` HttpWikiClient and `tools/audit_asset_cutoff.py` accept a MediaWiki response with API warnings when query data is also present. The four unsupported `iidir` callers are repaired; general warning handling is a separate second-level follow-up, with no refusal claim or measuring-instrument change in S15.

## Mirror runner ordering and registration fixtures repaired

Disposition: fixed.

Evidence: Commit 21e3d5ca repairs FIFO runner registration; memory-bank/archive/progress-remote-mirror-2026-10-02.md:3 records its landed implementation. tests/promotion/test_remote_mirror_priority.py:129 drives real processes and locks, including queued arrivals and registration contention; registration notices distinguish queue and turnstile waits. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-03T12:20:21-07:00: S01 scoped Opus runner draft registered normals under the gate turnstile; disposable real-process gate-arrival canary rejected SHA-256 19b8fefb8105f144cf2a497e95111732c3514355aeeac890488f192152143e0c with actual_acquisition_order [later:acquired, older:acquired] and AssertionError: later normal overtook older normal behind a waiting gate; raw proof /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-03-codex-resume/runner-fairness-evidence/rejected-gate-arrivals.log.
- 2026-10-03T12:30:47-07:00: S01 ticket-range first fixture pass reported Ran 10 tests in 1.363s, FAILED (failures=7): the registration lock used a blocking probe on a free lock, so step workers paused before registering, and the existing waiting-gate fixture expected every contender at .turnstile instead of the serialized .queue wait site; changed the free registration probe to nonblocking and retained precise per-site notices plus gate-first/release assertions. Raw proof /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-03-codex-resume/runner-fairness-evidence/focused-first-green.log.
- 2026-10-03T13:02:40-07:00 — S01 Astra accepted P2 fixture race: parent-held queue byte 0 forced all 3 owned concurrent runner registrations to report registration-blocked, then the wrapper mislabeled registration contention waiting-queue; deterministic test failed with AssertionError: mirror.queue path not found in Remote mirror busy; waiting without a deadline for turnstile mirror.turnstile. Exact raw paths, owned PIDs and failed trace retained in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-03-codex-resume/runner-fairness-evidence/registration-race-red-trace.log; production source SHA-256 459ae0721b61e26591ab6389a201ad9cf0fbdf45eb5f710d3e861bbe475c9166 remains unchanged. S01/S13 original incidents remain open until promotion.

## Existing preflight diagnostic and hermetic fixture repairs

Disposition: fixed.

Evidence: Commit 02e61b51 makes silent nonzero child exits identify the failing gate; tests/maintenance/test_slop_gate_preflight.py:91 resolves the temporary repository path before deriving expected paths. SlopGatePreflightChildTests tests nonzero silent exits and preserves child output/index bytes. This batch makes no preflight or promotion-gate edit. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-02T21:09:33-0700: While checking the blocking mirror-lock slice, `python3 tools/maintenance/slop_gate_preflight.py` returned exit 1 with no stdout or stderr; raw log `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-gate-mirror-priority-2026-10-02/blocking-slop-preflight.log`; the recheck reported `E303 x1 (was 0)` and cognitive complexity `RemoteMirrorPriorityTest::test_old_runners_cannot_starve_a_waiting_gate 21 (new)`; those source issues were corrected and the unchanged preflight passed, but the original silent refusal remains unexplained.
- 2026-10-15T08:09:23.140291-07:00 — Hermetic preflight fixture expected /var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T paths, but git rev-parse --path-format=absolute --git-path hooks/slop_gate.py returned /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T paths; focused-execution ran 7 tests with failures=2, actual exit 1. Resolve the disposable repository path before deriving its expected gate path; no product behavior changed.

## First Resort chopping fixture supplies non-rock random draws

Disposition: fixed.

Evidence: Commit 2f4e6eb5 repairs tests/runtime_actions/test_first_resort_opening.py; the ordinary-chopping handoff test now supplies deterministic non-rock draws after the guaranteed chops. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-08T03:28:49.245064+00:00 First Resort focused fixture initially exhausted RNG draws to default 0.0 and triggered strange-rock replacement: test_ordinary_chopping_supplies_exact_handoff_and_later_reviews_stay_held failed AssertionError: 7 != 8; Ran 49 tests in 7.979s, FAILED (failures=1). Only the fixture supplied non-rock draws after guaranteed chops; final49 passed, no production harvesting change.

## Ghostspeak alternatives and legacy item migration repaired

Disposition: fixed.

Evidence: Commits a9e2e756 and 148d78cb repair the Fenkenstrain Ghostspeak OR group and retain bounded legacy-item migration in core/storage_pure.py; coverage lives in tests/runtime_actions/test_fenkenstrain_opening.py and tests/test_storage_migration_extra.py. The later stage-2 purchase source hold is separate and remains open. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-08T04:23:53.928534+00:00 Fenkenstrain focused45 first execution returned1: Ran45 in11.332s, FAILED(failures=4). Removing only stale Amulet of ghostspeak from generated OR options left mandatory Cramulet in a separate group. Author removes both original alternatives and adds one Ghostspeak amulet/Cramulet OR group; original red6/Ran6 in0.526s FAILED(failures=7) and failed focused logs retained, fresh inventory follows, no test/instrument weakening.
- 2026-10-13T21:22-07:00 Ghostspeak fix commit: renaming `_migrate_legacy_crafting_item_references` to `_migrate_legacy_item_references` in core/storage_pure.py made slop-gate report the existing function as "(new)" with cyclomatic 17 and cognitive 36, so a pure rename must also bring the function under the limits; the test had to move from tests/test_storage_pure.py (2285 lines, any growth blocked) to tests/test_storage_migration_extra.py.

## Local transport canary placement and credential-safe assertions repaired

Disposition: fixed.

Evidence: Commits 4369fc75 and 53811fa6 move the local-host tests into tests/promotion/test_local_test_host.py, force the direct-run canary to refuse before sync, and use a safe boolean leak assertion. memory-bank/source-audits/local-test-host-2026-10-14.md:6 records the canary repair; :9 records the protected original credential-bearing evidence and redacted copy. Accepted source/gate receipts there are reused, without rerunning transport against the shared mirror.

- 2026-10-14T08:20:16.062364+00:00 — Local-host transport focused run started 2026-10-14 01:03:01 PDT: tests.maintenance.test_remote_storage.RemoteStorageTests.test_direct_runner_reaches_preflight_from_an_unrelated_working_directory used only fake ssh as its stop, so local transport passed real preflight and rsync --delete replaced /Users/armantarkhanian/ankiscape-remote-test-host/ankiscape_fork with run_tests.py and .venv-qt. Original failure: ModuleNotFoundError: No module named tools; Ran 109 tests in 161.874s, FAILED (failures=1). Root verified those two mirror entries, no pending record and no matching mirror test process. Fixed test forces distant-host refusal; original failure and 109-case final pass remain retained. Existing locked sync will restore the disposable mirror.
- 2026-10-14T08:24:18.206896+00:00 — Local-host source preflight and commit correctly refused a new tests/test_local_test_host.py: slop-gate: code files were added to directories already at 40 files: tests: 237 code files (was 236). Moved the unchanged module into existing cohesive tests/promotion/test_local_test_host.py; the fixed directory cap remains unchanged. Root attempted the commit after the failed preflight; the hook rejected the same defect. No hook bypass or successful product replay occurred.
- 2026-10-14T08:39:17.745080+00:00 — Local-host review found the original mutation-m3-runner-environment-leaks.log assertion printed CLAUDE_CODE_OAUTH_TOKEN and CLAUDE_CODE_MESSAGING_TOKEN values. Root preserved the original SHA-256 with mode 0600 under a mode 0700 evidence directory and made a redacted review copy; secret-evidence-reconciliation.json records the paths and hashes. The safe boolean assertion preserves leak detection without dumping os.environ. The first targeted inventory used an unsupported module:method selector and failed before execution; the failed pending receipt is retained and will be reconciled explicitly.

## Mogre schema repaired without relaxing the fixed roster

Disposition: fixed.

Evidence: memory-bank/source-audits/mogre-fixed-schema-source-2026-10-14.md:3 records the representation repair; tests/combat_roster/test_roster_contract.py:43 retains exact schema equality and passes on this main. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-14T22:22:22.165152+00:00 — Mogre full plain actual1:5336 tests623.664s, one failure580 skips. CombatEnemyRosterDataTest.test_new_enemies_have_required_schema reports extra key encounter_location for mogre; isolated same test is RED actual1 in0.001s. Source schema/context repair is pending; roster/lure baselines remain fixed.

## Familiarisation reducer and live-summon fixture repaired

Disposition: fixed.

Evidence: Commits ba47db34 and 2d544726 reuse the segment reducer at the independent world-tick boundary. tests/runtime_actions/test_familiarisation_fairness.py:32 supplies actual summoning points before invoking the real summon, and proves clocks across expiry and Undo. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-15T06:15:26.712415+00:00: Familiarisation metrics refused `advance_summoning_world_tick_pure: cognitive 24 > 15`; reuse the existing segment reducer behind the activity world-tick boundary, retaining independent clocks and the fixed15 limit.
- 2026-10-15T06:50:30.470513+00:00: Familiarisation live-clock fixture set summoning_level=99 but retained default summoning_points_current=1; summon_familiar_pure returned False at test_familiarisation_fairness.py:34. Supply valid points before the real summon.

## Jad prayer test complexity repaired with all assertions retained

Disposition: fixed.

Evidence: Commit d13418d3 splits the prayer-limit cases in tests/test_fight_caves.py:681; the focused FightCavesJadProtectionTests pass with the fixed complexity limits unchanged. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-15T08:11:17.945591+00:00: Normal Jad commit session97851 exited1: "slop-gate: cognitive complexity above 15 was introduced: tests/test_fight_caves.py: FightCavesJadProtectionTests::test_auto_protection_respects_unlocks_points_and_depletion 23 (new)". A test-only split preserves every assertion; fixed metrics now4/5 and5/8,52 focused cases pass. Original tool-result provenance retained; no invented original hook log or failure rerun. Reused the complete linked closed-mirror archive to keep startup records under the unchanged3000-line limit.

## Restaurant integration discovery and storage import repaired

Disposition: fixed.

Evidence: Commit 80475a0f imports the farming helper module rather than its TestCase in tests/runtime_actions/test_gnome_restaurant_review_clock.py:7; the module imports migrate_loaded_data directly from core storage at :10. Both discovery and the migration-backed flow cases pass. Focused proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/papercut-batch-1/focused-final-receipt.json and focused-final.log, 107 tests, exit 0, no skips.

- 2026-10-15T05:59:46.531089+00:00: Restaurant integration discovery refused `Discovered 17 unittest IDs more than once:` because a TestCase class was imported into the new test module. Import the helper module and reference its class methods; original refused run is retained in restaurant-again-fairness/green-behavior.log.
- 2026-10-15T06:01:01.259642+00:00: Restaurant review-flow proof ran10 tests and found `AttributeError: module 'ankiscape_restaurant_review_clock' has no attribute 'migrate_loaded_data'`; use the existing storage migration import rather than guessing an entrypoint export. Product behavior assertions passed before this test-harness error.

## NPC source receipt labels reconciled

Disposition: fixed.

Evidence: Commit 55af7380 corrects completed source-guard receipt labels and stale priority nominations; memory-bank/source-audits/npc-shop-source-guard-landed-2026-10-15.md:3 records the exact accepted source and :5 the retained reconciled receipt packet. Original successful checks are reused.

- 2026-10-15T04:45:23-07:00 — Astra closure found completed source-guard no-op/check entries still status pending despite actual_exit0, and a priority row retained Four later names remain uninspected plus a superseded Firemaker nomination. Corrected only receipt labels/current row, retained35 reconciled files with the existing retainer, preserved old packet and all successful product proofs without replay.

## Dream and Workshop qualification corrections recorded

Disposition: fixed.

Evidence: memory-bank/source-audits/dream-and-workshop-iv-opening-boundaries-2026-10-15.md:5 explicitly preserves both source lines 72 and 76, and :7 gives the actual Workshop III prerequisite hold precedence. This closes the mistaken qualification verdicts only; both product/journal holds remain open.

- 2026-10-15T13:41:48.645307+00:00: R24 projection contained the real elemental_workshop_iii prerequisite, but the verdict skipped its retained owner hold and selected IV's later book-source question as first. This was a qualification error. Correction adds an explicit disposition for every actual IV prerequisite, with record/effect/first-unblock fields, rather than a new source/tool framework.
- 2026-10-15T14:21:57.765533+00:00 — Cross-lineage K3 review identified source line 72 as a separate required post-first-four-feed conversation. The initial review read that conversation as subsumed by the following Spirit encouragement. The final verdict records R1 and requires the owner-scope record to cover both lines 72 and 76. No product code or original qualification packet changed.

## Sawmill fixture migration and ledger binding repaired

Disposition: fixed.

Evidence: Main 8749ddc6: memory-bank/source-audits/sawmill-mbp-source-acceptance-2026-10-14.md:13 records the corrected fixture. /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/manual-sawmill-canonical-native-2026-10-15/canonical-case-2/seed_fixture.py:16 migrates after the Coins augmentation and before set_config. Commit 8749ddc6 binds native proof to the accepted source and canonical ledger rather than requiring excluded Memory Bank files in the shipped manifest. Original refused fixture and binding error remain preserved; accepted native evidence is reused.

- 2026-10-15T23:50:30.437824+00:00 — First Sawmill fixture refused startup at `bank_layout` with `startup_equal: false`, `native_accepted: false`, `reviews: 0`: Declared Coins augmentation followed the shipped helper migration. The saved Bank layout therefore omitted Coins; normal load reconciled it. Fixture preparation error, not a product-defect claim. Fixture/gameplay/owner-guard actual exits were0 and owner_unchanged true; original evidence remains at /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/manual-sawmill-canonical-native-2026-10-15/first-case-unaccepted.json.
- 2026-10-15T23:51:50.785331+00:00 — Sawmill native binding looked for the canonical ledger in the shipped source manifest and raised `KeyError: 'memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl'`; the freezer excludes Memory Bank records. Bind that ledger against the exact accepted/native Git revisions, and bind its generated Varrock runtime consumer against the shipped manifest. No product source changed.
