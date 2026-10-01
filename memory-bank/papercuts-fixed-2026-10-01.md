# Papercuts fixed — 2026-10-01

## The plural name QuestDefinition.stages denotes an integer count, making it easy for a probe to mistake it for the iterable stage-requirement rows; the

Disposition: fixed.

Evidence: goal/papercuts-misc: 3b8075b8, 2fd69c54, 74abdf7c, 90f8cd97, 21432c32, 5eff351c, 5734241f, simplified in 3d64a27f, 06324e44, 4b61a82b, 1106344f. Triage cause: The plural name QuestDefinition.stages denotes an integer count, making it easy for a probe to mistake it for the iterable stage-requirement rows; the model has no explanation distinguishing these fields.

- 2026-08-26 23:28 PDT — A quest predicate probe treated `QuestDefinition.stages` as iterable, but it is an integer stage count; effective requirement rows live in `stage_requirements`.

## The owner requested a clean break between sequential test lanes, so the remaining gates were intentionally not run.

Disposition: record_only.

Evidence: The entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:4 records an owner interruption, not a failed gate or tooling defect. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/archive/progress-2026-05-to-08.md:421 explicitly confirms that the sequential gate task was stopped for the requested clean break; line 427 confirms that Qt and the later gates did not run for that reason. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/handoffs/orchestrator-lessons-2026-08-30.md:134 also records the remaining gates as unrun. This is a one-time intentional pause with no removable cause.

- 2026-08-30 08:55 PDT — The owner requested a clean break while the first sequential papercut gate was between lanes; the task stopped after plain passed 4,526 tests in 251.013 seconds with 513 skips, so record Qt and both later gates as unrun rather than failed.

## The module-surface digest included an object's defining module, so extracting Magic functions into another file changed engine and root digests despit

Disposition: fixed.

Evidence: Commit dbd95a94208e6c570475491278dc8acab4d71ebf, verified as an ancestor of the current checkout, removed defining-module names from published object identity. The fix remains in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/module_surface.py:40-48. Regression coverage remains in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_module_surface.py:90-128: moving the defining module preserves the dump, while member names, qualified names, signatures and data still affect identity. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/fable-handoff-2026-09-21/step4-summary.md:3 records matching digest outputs for the preserved Magic candidate and its pre-extraction baseline after this fix. This resolves the digest cause, not the separate owner decision about adopting the still-unmerged Magic candidate. No tests were rerun during this read-only triage.

- 2026-09-18T19:01:01.031137+00:00 Full source gate `16559` for Magic `a8137bab2566b45e52585c580794a84563241b7e` failed plain run `plain-1789757256-04017593`: `Ran 5693 tests in 615.277s`, `FAILED (failures=2, skipped=1366)`. `test_first_wave_digests` expected engine `886cde5a31bb852ed696e8018c8954e707fff86c56dc0fc65633fd1b2f76f8c6`, actual `ce360383f420a4bd22595f8e7ee8af3ad4cb9c7c069a86ad355a1f82dc074d79`; `test_root_initializer_digest_under_qt` expected root `c81943a0fc224bafcefc85a0fa3bd1a1c6bc242b73c2c9949d65efa8e1bcf030`, actual `2040bdd3887ef471b0aa1fcfbb4031180bccbfb458e4b46161a42eed7781b366`. Complete original log is retained losslessly under `memory-bank/source-audits/combat-magic-wrap-up-2026-09-18/`. Source branch is preserved, not accepted; no pin or source repair is made during the requested pause wrap-up.

## Two Rulesync source files declare root: true with targets: ['*'], so both match codexcli and claudecode. Rulesync rejects multiple root rules per targ

Disposition: fixed.

Evidence: goal/papercuts-misc: 3b8075b8, 2fd69c54, 74abdf7c, 90f8cd97, 21432c32, 5eff351c, 5734241f, simplified in 3d64a27f, 06324e44, 4b61a82b, 1106344f. Triage cause: Two Rulesync source files declare root: true with targets: ['*'], so both match codexcli and claudecode. Rulesync rejects multiple root rules per target; successful skill generation does not resolve the rules-generation error.

- 2026-09-23T19:12:00-0700 Design progress skill: `rulesync generate` in a scratch copy printed "Multiple root rulesync rules found for target 'codexcli': .rulesync/rules/native-anki-verification.md, .rulesync/rules/worktree-location.md" yet still wrote the skill files; skills generation is not blocked by it.

## Focused remote runs require an exact --expected-tests count, but authors lacked a convenient collect-only count and executed local tests to obtain it.

Disposition: fixed.

Evidence: Commit 284d3332f6c7816b5eefa433dba97991295737c1 added collect-only --count. Verified the current implementation in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/run_tests.py:136-145 and :212-214: it prints the selected count and returns before test execution, without the --list ID cap. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/README-tests.md:37-52 documents counting locally and passing the result as --expected-tests. Existing regression coverage at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_papercut_tools.py:585-609 checks overlapping selectors, bypassing the ID cap, and no test execution. These tests were inspected, not run during this read-only triage.

- 2026-09-26T09:22:34-0700 — Runner-sync review follow-up: to learn the exact count for `--expected-tests` I ran `python3 -m unittest -v tests.test_promotion_gate tests.test_memory_bank_queue_packet` locally (`Ran 46 tests in 207.020s`), which the brief forbids and which cost 3.5 minutes; the runner needs an exact count but offers no MacBook-side way to list a selection's tests, so count with a collect-only listing instead of a local run.

## Git grep was run from a linked checkout against a log outside that checkout. Shared evidence lives under the canonical Git directory; --no-index does 

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: Git grep was run from a linked checkout against a log outside that checkout. Shared evidence lives under the canonical Git directory; --no-index does not remove Git's path boundary, and evidence inspection lacks a documented working command.

- 2026-09-26T09:57:04-0700 — Live-tree sync commit evidence inspection: git grep --no-index refused the external reachability log with "fatal: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-tools-live-tree-sync-2026-09-25/audit-item-reachability.log: '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-tools-live-tree-sync-2026-09-25/audit-item-reachability.log' is outside repository at '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-tools-live-tree-sync-2026-09-25'"; retry with an explicit evidence work-tree exited 1 without output. Retained the implementation-stage audit result without claiming a fresh audit.

## An optional search returns exit 1 when nothing matches; chaining a required inspection after it with && incorrectly makes that inspection conditional 

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: An optional search returns exit 1 when nothing matches; chaining a required inspection after it with && incorrectly makes that inspection conditional on finding a match.

- 2026-09-26T19:19:30-07:00 — Stale-gate review verification: the optional active-runner probe `ps -axo pid=,command= | grep '[t]ools/run_remote_tests.py'` returned exit 1 with no matches and skipped the reader-reference search chained with `&&`; keep optional process probes separate from required checks.

## A repository search used a regex with mismatched parentheses instead of a valid expression or fixed-string matching. The evidence does not establish a

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: A repository search used a regex with mismatched parentheses instead of a valid expression or fixed-string matching. The evidence does not establish a ugrep-specific defect: native macOS grep also rejects an unmatched escaped closing parenthesis.

- 2026-09-26T14:16-0700 — Test-tools cleanup slice: `grep -rn` here is ugrep, which rejected a basic regex containing `\)` with 'error at position 57 ... mismatched ( )'; use `grep -F` or separate patterns.

## The dispatch brief confused a verdict's source papercut line_no with the physical line number in verdicts.json, directing the reader to a different ca

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: The dispatch brief confused a verdict's source papercut line_no with the physical line number in verdicts.json, directing the reader to a different cause class.

- 2026-09-25T15:51-07:00 — Cleanup emitter slice: the brief cited 'verdicts.json, line 8', but JSON line 8 is `"class_key": "git-argument-order-misuse"`; the 8 is the papercuts.md line number, and the verdict itself sits at class_key `required-action-without-emitter` (JSON lines 46-49).

## The progress record cited a passing pinned-baseline run without retaining its corresponding raw log, leaving reviewers with only the earlier failing r

Disposition: fixed.

Evidence: The specific evidence gap was repaired and landed in commit d4880e2442187c7542662de18b6b7f5d60d00961. The corrected record now lives at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/archive/progress-2026-09.md:1859-1864: it distinguishes the historical failure from the rerun at 6197c8c0, cites the pinned log, and explicitly records review findings R2/R3 as addressed. Read /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-action-emitter-check-2026-09-25/plain-test_quest_action_proofs-pinned.log:2-7, which contains 'Ran 20 tests in 0.468s' and 'OK'. A fresh SHA-256 measurement is a449fe974359e655613ce60c3c1674b9d01545062021ae139eb5b19a56d2138f, exactly matching the corrected record at line 1863. This verifies repair of this entry's missing proof, not universal enforcement of log retention.

- 2026-09-26T09:12-07:00 — Cleanup emitter review follow-up: progress.md cited the pinned-baseline passing run ('Ran 20 tests in 0.414s', 'OK') but the evidence directory kept only the earlier failing 'plain-test_quest_action_proofs.log' ('FAILED (failures=1)'), so review finding R3 could not verify the claim; the run was repeated at 6197c8c0 and kept as 'plain-test_quest_action_proofs-pinned.log'. Save every cited run's log and SHA-256 when it runs.

## QtWebEngine's Chromium GPU/Skia renderer emits missing-mailbox diagnostics during offscreen DOM tests. The logs establish recurring renderer errors, n

Disposition: wont_fix.

Evidence: External owner (Owner: QtWebEngine/Chromium maintainers, with the remote Qt test-host maintainer providing reproduction evidence. Reproduce using a minimal offscreen QWebEngineView lifecycle on the pinned host and re); generic tooling outside this repo, not handed off.

- 2026-09-26T14:44:05-07:00 — JavaScript DOM fixture: the successful remote Qt run (`Ran 28 tests in 5.191s`, `OK`) emitted `SharedImageManager::ProduceSkia: Trying to Produce a Skia representation from a non-existent mailbox.` from `../../../qtwebengine/src/3rdparty/chromium/gpu/command_buffer/service/shared_image/shared_image_manager.cc:389`; raw stderr is in `remote-dom-final.log` under `ankiscape-promotion-evidence/goal-js-bridge-inert-tests-2026-09-26/`.

## The proposed tool and test widened already-over-limit top-level directories, triggering the slop gate's directory-file-count ratchet.

Disposition: fixed.

Evidence: Commit c2e17622 committed the tool under tools/memory_bank/ and its test under tests/memory_bank_tools/. Verified the current files: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/memory_bank/move_papercuts.py:1-20 contains the tool; /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/memory_bank_tools/test_move_papercuts.py:36-38 invokes that nested path. git ls-files confirms both nested files are tracked and neither tools/move_papercuts.py nor tests/test_move_papercuts.py is tracked. The reported placement problem is resolved; the directory ratchet is an intentional constraint, not a broken gate.

- 2026-09-25T16:25:51-07:00 — The papercut triage named the new tool `tools/move_papercuts.py`, but the slop gate on a temporary index exited 1 with `tests: 237 code files (was 236)` / `tools: 152 code files (was 151)` / `-> Create a cohesive subdirectory instead of widening this directory.`; the tool moved to `tools/memory_bank/` and its test to the new `tests/memory_bank_tools/` package. Triage fix designs should name a subdirectory for any new file under `tools/` or `tests/`.

## Unquoted separator words beginning with '=' trigger zsh's enabled EQUALS expansion before echo executes. The recurring failure comes from the agent sh

Disposition: wont_fix.

Evidence: External owner (Owner: fleet/agent-shell configuration maintainer. Disable EQUALS expansion in the noninteractive agent zsh startup or shell-launch wrapper, rather than adding another repository prose rule. Verify th); generic tooling outside this repo, not handed off.

- 2026-09-26T20:58:07-07:00 — Queue-records slice: `echo ======` between two sed commands in a zsh one-liner failed again with '(eval):1: ===== not found', the same leading-'=' expansion recorded at 2026-09-24T06:05:41; a prose rule has not stopped the repeat, so the agent shell or dispatch template should quote separators.

## Combining the output-check and digest-locking changes left Summoning's manifest publication on the unlocked writer despite a clean three-way apply.

Disposition: fixed.

Evidence: Commit 7aff2b89fa264a7536b8069f05e3644490fb7261 explicitly repairs this integration loss. Verified the current tree: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/generate_summoning_catalog.py:664-670 confines manifest comparison through write_or_check to --check mode; write mode sends only the catalog to write_or_check and publishes the manifest through save_source_digests. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/generation/source_digests.py:45-56 holds an exclusive lock across manifest read-modify-write and publishes by atomic replacement. The specific lost behavior is restored; a clean Git apply is still not a general guarantee of semantic correctness.

- 2026-09-27T02:24:10-0700 — Digest-race-on-proof integration: `git format-patch -1 --stdout fd92619c | git apply --3way` reported "Applied patch to 'tools/generate_summoning_catalog.py' cleanly." yet the result still published the Summoning manifest through the unlocked `write_or_check` path, because the base had already replaced the `save_source_digests` call; a clean three-way hunk can silently drop one side's behaviour, so read every "cleanly" file against both source commits.

## The integration resolver treated any occurrence of `<<<<<<<` as an unresolved conflict, so legitimate inline quotations in the historical papercut log

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: The integration resolver treated any occurrence of `<<<<<<<` as an unresolved conflict, so legitimate inline quotations in the historical papercut log triggered a bare AssertionError.

- 2026-09-27T02:25:30-0700 — Digest-race-on-proof integration: a conflict resolver asserting no `<<<<<<<` text anywhere failed with a bare `AssertionError` on `memory-bank/papercuts-fixed-2026-09-23.md`, whose lines 2561-2562 already quote conflict markers; check only marker lines at column zero.

## Git checkout overloads branch switching and file restoration: `git checkout 24347179 --` with no path switched to the commit instead of doing nothing,

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: Git checkout overloads branch switching and file restoration: `git checkout 24347179 --` with no path switched to the commit instead of doing nothing, detaching HEAD.

- 2026-09-27T02:48:36-0700 — Digest-race-on-proof review fix: a trailing `git checkout 24347179 --` with no path, meant as a no-op, detached HEAD at 24347179 ("HEAD detached at 24347179"); `git switch goal/generator-digest-race-on-proof-2026-09-27` reattached it with the working tree intact. Never pass a commit to `git checkout` without a path.

## After acquiring the mirror lock, the runner rejects an unresolved live remote lane immediately rather than waiting for that lane to finish; callers mu

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:31 — 2026-09-23T22:54:37-0700 (the pending-record portion). The earlier open entry at papercuts.md:31 records two syncs blocked by qt-1790225120-677f3cf4 until its report appeared, the same cause as this entry. Current tools/run_remote_tests.py:306-325 checks the pending lane once and raises 'previous remote lane is not confirmed stopped; sync blocked'; :655-657 invokes that check after acquiring the mirror lock. Commit a54b2be34943f6310c2c2fe236371f448c0c4618 added stopped-lane recovery but retained immediate rejection of live lanes, as tests/test_remote_test_host.py:474-510 confirms. The earlier entry at papercuts.md:29 instead describes a dead lane with no report, which is a distinct reconciliation case. memory-bank/papercuts-fixed-2026-09-28.md:97-107 previously grouped live-lane incidents under this entry; the current earliest-open-survivor rule selects line 31 instead.

- 2026-09-26T09:43:20-0700 — Upstream-spec review fix: run_remote_tests.py waited for the mirror lock, then exited 1 with 'error: previous remote lane has no completion report; sync blocked; pending record: /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.pending.json; run: plain-1790440867-be9d7f57' because another agent's run started at 09:41:07 between the lock release and this sync; the runner waits on the lock but not on the pending record, so the caller must poll for that file.

## The remote runner accepts a completion report before checking elapsed time and sleeps the full poll interval, allowing a lane that finishes after --ti

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: The remote runner accepts a completion report before checking elapsed time and sleeps the full poll interval, allowing a lane that finishes after --timeout to return success.

- 2026-09-25T16:00:42-0700 — Orphan-lane e2e: `tools/run_remote_tests.py ... --timeout 3` exited 0 instead of timing out, because the runner checks `--timeout` only after the report poll and a 5 s default `--poll-interval` sleep; the timeout proof needed `--timeout 2 --poll-interval 0.5`.

## The test located the PID-read command using only the substring ".pid ", which also matched the launch command's PID-file redirect and caused the asser

Disposition: fixed.

Evidence: Verified the current tree by reading and searching /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_remote_test_host.py. Line 236 requires both command.startswith("cat ") and ".pid " in command, excluding the nohup launch command. Git blame and git log -S attribute this predicate to commit a54b2be34 (Stop one lost test run from blocking every later test run). No tests were run during this read-only triage.

- 2026-09-26T14:41:12-07:00 — Orphan-lane review 2: the first focused run failed 1 of 82 with AssertionError in test_disconnected_launch_reconciles_same_run_and_preserves_failure because the pid-read lookup `".pid " in command` also matched the launch command, whose pid-file redirect reads `.pid <> `; the lookup now also requires `startswith("cat ")`.

## Intermittent hangs in macOS's system-wide, file-targeted /usr/sbin/lsof scan prevent reliable local inspection of lane and lock file holders. The unde

Disposition: wont_fix.

Evidence: External owner (Owner: macOS workstation maintenance and Apple's system lsof implementation, outside this repository. Diagnose the intermittent file-target scan on a disposable canary with a hard deadline and collect); generic tooling outside this repo, not handed off.

- 2026-09-26T15:33:28-0700 — Orphan-lane review 3: on this Mac (macOS 26.6), `timeout 60 /usr/sbin/lsof -w -F pfa -- /tmp/pidmark` hung until `timeout` killed it (`real 1m0.258s`, exit 124), and `-b` instead failed with `lsof: status error on /tmp/pidmark: Resource temporarily unavailable`; only `lsof -a -p <pid>` answered, so the lane process scan can be exercised only on the MacBook.

## An interrupted focused-proof session leaves no durable handoff that pairs the current selection and expected test count with the proof's pending or co

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: An interrupted focused-proof session leaves no durable handoff that pairs the current selection and expected test count with the proof's pending or completed status.

- 2026-09-26T20:40:32-0700 — Orphan-lane review 3 follow-up: the dispatch found the scan, reader, zsh and deadline repair uncommitted in the worktree, and its last focused run (`review3-focused-plain.log`) had passed `Ran 83 tests` but exited 1 on `error: remote focused lane false pass: tests=83, skipped=0; expected exactly 81 tests and no skips`, so nothing recorded whether that repair was proven; an interrupted slice should leave its exact expected count beside its pending proof.

## Active remote-lane log and completion-report polls omit SSH deadlines, allowing a connected but stalled SSH subprocess to block indefinitely while hol

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: Active remote-lane log and completion-report polls omit SSH deadlines, allowing a connected but stalled SSH subprocess to block indefinitely while holding the mirror lock.

- 2026-09-27T01:52:30-0700 — PRE-EXISTING (Grok review of the orphan-lane branch): `_stream_remote_run`'s log poll and in-loop report poll call `_ssh` with no deadline, so an SSH session that stalls after connecting holds the mirror lock until it returns; only stop, liveness and the reconcile report read have the 90-second deadline.

## A concurrent process temporarily rewrote the tracked asset-audit checkpoint and restored it while another agent inspected checkout isolation; the insp

Disposition: record_only.

Evidence: The entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:26 explicitly says the second status/diff check was clean without intervention. A contemporaneous entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-09-23.md:3067-3071 records the asset audit rewriting this same report and then restoring it. The current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/audit_asset_cutoff.py:4-7 documents checkpoint writes, lines 39-43 select this report, and lines 91-99 atomically replace it. Fresh read-only git status and diff checks for the report returned no output. This entry records a resolved observation of another process's work, not a persistent checkout-isolation failure or an erroneous write by the inspecting agent.

- 2026-09-23T17:56:00-07:00: While confirming checkout isolation, the live canonical checkout briefly reported " M memory-bank/source-audits/post-cutoff-asset-revisions-2026-08-21.json" from another concurrent process; a second read-only status and diff check showed it clean without any edit from this slice.

## Ad hoc Radon JSON readers used a malformed comprehension and incorrect function filtering instead of a shared metric extractor.

Disposition: fixed.

Evidence: Commit 9ba05589e22e6ef60a95dff3ac21b4fdd7874ddf added /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/maintenance/function_metrics.py. Current lines 61–65 delegate metric extraction to slop-gate, including halstead_by_function; lines 70–79 select named functions and reject missing or ambiguous instrument entries rather than silently filtering incorrectly. The delegated parser in /Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py:195–208 reads Radon's nested functions mapping with a bound name variable. Checked-in regression coverage at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/maintenance/test_function_metrics.py:61–84 checks selected-function output and Halstead values. Source inspection only; tests were not executed during this read-only triage.

- 2026-09-24T01:29:55Z: Agility metric remeasurement first used a faulty Radon JSON comprehension (NameError: name 'name' is not defined) and filtered output incorrectly; corrected both parsers before recording metrics.

## The probe imported the add-on's data directory as a top-level package, omitting the stable ankiscape package alias required by its relative imports.

Disposition: fixed.

Evidence: The supported bootstrap already exists and is documented in active development guidance. Commit 13b3edde4 added /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/techContext.md:37, which instructs tests and direct probes to import pkg_alias before ankiscape.* modules; lines 72-73 repeat the direct-probe guidance (commit ff0e4be8d). /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/pkg_alias.py:1-10 explains the folder-independent alias, and lines 36-42 install it without executing Anki's initializer (introduced in commit 8dea34b25). /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/quest/dependencies.py:7 uses a three-dot package-relative import, explaining why the unsupported from data.quest import ledger fails. The recorded remedy, import pkg_alias followed by from ankiscape.data.quest import ledger, matches the existing documented contract; no additional compatibility import path is needed.

- 2026-09-23T19:25:12-0700 Quest catalog loader slice: `python3 -c "from data.quest import ledger"` from the worktree root failed with 'ImportError: attempted relative import beyond top-level package'; the data package loads only as `import pkg_alias` then `from ankiscape.data.quest import ledger`.

## A dead remote test lane left a pending record without a completion report, and the runner required that report before allowing another sync.

Disposition: fixed.

Evidence: Commit a54b2be34943f6310c2c2fe236371f448c0c4618 fixes this dead-lane case. In /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:306-336, reconciliation checks lane liveness and clears a confirmed-stopped lane's pending record even when its completion report is absent; lines 328-329 explicitly log that outcome. New launches record pid_path at lines 504-509. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_remote_test_host.py:532-545 covers reconciliation without a report when an unrelated process has reused the exited leader's PID. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/remote-test-host.md:81-86 documents automatic dead-lane reconciliation and the manual boundary for legacy records without a readable process group. The entry explicitly says there was no process, unlike the still-live-lane waiting issue at papercuts.md:20. Files and commit were inspected read-only; no tests were run.

- 2026-09-23T19:52:04-0700 Quest catalog loader slice: after acquiring the mirror lock, my runs exited 1 with 'previous remote lane has no completion report; sync blocked' for another slice's run qt-1790216520-05d98288, whose remote log had stopped at 106802 bytes with no report and no process; the pending record was later replaced by qt-1790218056-39765fc4 and I requeued.

## The shop access-lock refactor added private functions in logic/shop/state.py without initially re-exporting them through logic/shop_logic.py, violatin

Disposition: fixed.

Evidence: Commit 1a6c21795b2c25e1b2866034c25b41a5dd4100d2 added explicit same-name re-exports. The current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/shop_logic.py:55-64 contains `_sanitize_market_clock as _sanitize_market_clock` and the other extracted helpers. Read-only AST comparison found no functions defined in logic/shop/state.py missing from the aggregator's imports. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/shops/test_module_boundaries.py:19-33 continues to enforce complete re-export coverage and object identity, including private helpers.

- 2026-09-23T19:23:24-0700 Shop access-lock slice: `tests/shops/test_module_boundaries.py` requires `logic/shop_logic.py` to re-export every function defined in `logic/shop/state.py`, private helpers included (`AttributeError: module 'ankiscape.logic.shop_logic' has no attribute '_sanitize_market_clock'`); a plain re-export adds one vulture `unused import` finding per name, and the repo's `name as name` form avoids them.

## Focused verification still obtains its expected test count from local discovery, separately from the MacBook's interpreter and synced snapshot. The sp

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: Focused verification still obtains its expected test count from local discovery, separately from the MacBook's interpreter and synced snapshot. The specific reason for the recorded 758-versus-760 discrepancy remains unproven. The separate orphaned-pending-lane problem has since been repaired.

- 2026-09-23T22:54:37-0700 — A local `run_tests.py --list` count gave 758 IDs for the 15 plain-lane distraction-handler modules, but the MacBook ran 760, so the focused runner refused an all-green run with "remote focused lane false pass: tests=760, skipped=0; expected exactly 758 tests and no skips"; separately, a stale pending record for another agent's run qt-1790225120-677f3cf4 blocked two syncs with "previous remote lane has no completion report; sync blocked" until that run wrote its report.

## The pinned runtime facade retains TROLL_INVASION_REPAIR_MODE as an implicit re-export. Vulture treats the import as unused when the changed-file snaps

Disposition: fixed.

Evidence: goal/papercuts-misc: 3b8075b8, 2fd69c54, 74abdf7c, 90f8cd97, 21432c32, 5eff351c, 5734241f, simplified in 3d64a27f, 06324e44, 4b61a82b, 1106344f. Triage cause: The pinned runtime facade retains TROLL_INVASION_REPAIR_MODE as an implicit re-export. Vulture treats the import as unused when the changed-file snapshot lacks another reference to that name, so removing a redundant handler guard exposes a finding even though deleting the facade export would change its public surface.

- 2026-09-23T21:30:36-0700 — Dropping the runtime Troll Invasion repair-mode guard (the logic already ignores steps outside productive repair) made the slop gate report `runtime/runtime_actions_activities.py: unused import 'TROLL_INVASION_REPAIR_MODE' (90% confidence)`: vulture counts a name as used across all changed files, so a pre-existing stray re-import turns into new dead code, and removing it would move the pinned module-surface digest; kept the guard as a named steps rule instead.

## Generated shop tables are serialized onto single physical lines, so an ordinary grep prints the entire catalog for a single match. The existing bounde

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: Generated shop tables are serialized onto single physical lines, so an ordinary grep prints the entire catalog for a single match. The existing bounded-search helper is not referenced in the repository's agent startup guidance.

- 2026-09-24T00:16:41-0700 — `grep -n "wilderness" data/shop_data.py` returned 1.9MB because the generated shop table keeps whole rows on single lines; pipe such greps through `cut -c1-300` or grep narrower keys.

## Focused remote runs wait indefinitely for the shared mirror lock, but callers can launch the runner under a bounded foreground Bash call. The queue wa

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: Focused remote runs wait indefinitely for the shared mirror lock, but callers can launch the runner under a bounded foreground Bash call. The queue wait can exhaust that call's timeout before test execution starts.

- 2026-09-24T00:53:15-0700 — The one-test focused Qt proof (`--select test_cape_tradeability.CapeTradeabilityRuntimeTest.test_buy_sell_persist_in_real_anki_collection --expected-tests 1`) waited about 15 minutes on `/Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock` for 6.542s of execution and outlived the 600s Bash cap; launch remote runs in the background from the start.

## New helpers need a gate-compatible home, but crowded directories, oversized modules, and the root's import ratchet are not exposed through a discovera

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: New helpers need a gate-compatible home, but crowded directories, oversized modules, and the root's import ratchet are not exposed through a discoverable placement check before authors choose a destination.

- 2026-09-24T00:26:32-0700 — Root prayer/feedback cleanup: the natural home for both new pure helpers was full (`logic/` has 87 code files, over the gate's 40-file cap; `logic/review_strip_logic.py` and `logic_pure/logic_pure.py` are over 1,000 lines), and the root's import fan-out forbids any new edge unless the new module's own imports are a subset of the root's, so both helpers went to `core/` and import `sanitize_prayer_selection_pure` through `logic_pure.logic_pure`.

## A GNU-style \b word-boundary expression was used with macOS BSD sed, which silently completed without matching the identifier. Completing that rename 

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: A GNU-style \b word-boundary expression was used with macOS BSD sed, which silently completed without matching the identifier. Completing that rename with Python resolved the immediate task but did not prevent recurrence.

- 2026-09-24T04:34:34-0700 — Root review-helpers slice: `sed -i '' 's/\bcatalog_requirement_item_names\b/.../g'` on macOS exited 0 and changed nothing, because BSD sed has no `\b` word boundary; the rename went through Python `re.sub` instead.

## The retained equivalence probe lacked a recorded invocation identifying its input tree and deterministic hash seed.

Disposition: fixed.

Evidence: Commit 6500d39f33ae4f94d020345b3bb9aec9a126e618 recorded the invocation in memory-bank/progress.md:1503. That record is now preserved at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/archive/progress-2026-09.md:2166 after archive commit eec78432. It explicitly gives `PYTHONHASHSEED=0 python3 probe.py <tree>`, identifies the baseline as a git archive snapshot of 0f67a3f6, and identifies the evidence directory containing probe.py. Read the retained /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-shop-services-2026-09-24/probe.py:6-7: the argument is inserted into sys.path before importing pkg_alias. The same evidence directory also retains before-snapshot-path.txt with the exact snapshot path from the papercut. The invocation is documented in the checked-in evidence index rather than a companion file, but the information that required rediscovery is now recorded.

- 2026-09-24T05:14:14-0700 — Shop services review fix: the evidence directory kept `probe.py` but not its invocation, so re-running it meant rediscovering the `git archive` snapshot `/var/folders/rt/xd67_cfj3jg9pkgkc0jnhk300000gr/T/tmp.BpvmnlpK3V/base-0f67a3f6`, that the import root is the tree holding `pkg_alias.py`, and `PYTHONHASHSEED=0`; record the exact probe command next to the probe.

## Differential probes serialize hash-seed-dependent dictionary insertion order without pinning the Python processes' hash seed, producing false differen

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: Differential probes serialize hash-seed-dependent dictionary insertion order without pinning the Python processes' hash seed, producing false differences between identical code.

- 2026-09-24T05:30:33-0700 — Agility handler cleanup: an out-of-tree before/after probe that JSON-dumps `player_data` differed at the first scenario between two runs of identical code, because `default_player_data(ORE_DATA, ITEM_DEFINITIONS)` builds `inventory` in an order that changes with the per-process hash seed; running both sides with `PYTHONHASHSEED=0` made them byte-identical.

## The combat roster is populated in two modules: combat_data builds the base registry, but importing core.constants adds the bone-source enemies by muta

Disposition: fixed.

Evidence: goal/papercuts-misc: 3b8075b8, 2fd69c54, 74abdf7c, 90f8cd97, 21432c32, 5eff351c, 5734241f, simplified in 3d64a27f, 06324e44, 4b61a82b, 1106344f. Triage cause: The combat roster is populated in two modules: combat_data builds the base registry, but importing core.constants adds the bone-source enemies by mutating that same dictionary. Standalone roster probes therefore depend on import order.

- 2026-09-24T05:43:44-0700 — Combat burst settlement cleanup: `len(COMBAT_ENEMY_DATA)` is 199 after importing `ankiscape.data.combat_data` alone and 203 once `ankiscape.core.constants` is imported, because `core/constants_parts/activity_updates.py:406` adds the bone-source enemies (`frost_dragon`, `jogre`, `shaikahan`, `zogre`); a roster count taken without the constants import is four short.

## The differential probe serialized callback arguments with default=repr, so process-specific function addresses entered the behavior digest. The probe 

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: The differential probe serialized callback arguments with default=repr, so process-specific function addresses entered the behavior digest. The probe was corrected locally, but the repository has no active guidance for avoiding this serialization error in future probes.

- 2026-09-24T06:21:15-0700 — Review-answer hook cleanup: an out-of-tree before/after probe that hashed `json.dumps(..., default=repr)` of traced call arguments differed in all 3000 scenarios between two trees with identical behaviour, because `repr` of `_open_activities_sheet` and `_open_farming_sheet` embeds a per-process address (`<function _open_activities_sheet at 0x10bf96c40>`); stripping ` at 0x[0-9a-f]+` from reprs made the digests byte-identical.

## The agent used a foreground fixed-delay sleep to wait for background work, which the harness intentionally blocks. Repository waiting guidance does no

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: The agent used a foreground fixed-delay sleep to wait for background work, which the harness intentionally blocks. Repository waiting guidance does not state this restriction or give a supported completion-wait recipe.

- 2026-09-24T06:21:15-0700 — Review-answer hook cleanup: waiting for four background probe processes with `sleep 60; pgrep ...` was refused by the agent harness (`Blocked: sleep 60 followed by: ...`); `until [ "$(pgrep -f answer_probe | wc -l | tr -d ' ')" = "0" ]; do sleep 5; done` waits without the block.

## Combat behavior tests patch private names on the engine module, coupling helper placement to test implementation rather than gameplay behavior.

Disposition: fixed.

Evidence: goal/papercuts-misc: 3b8075b8, 2fd69c54, 74abdf7c, 90f8cd97, 21432c32, 5eff351c, 5734241f, simplified in 3d64a27f, 06324e44, 4b61a82b, 1106344f. Triage cause: Combat behavior tests patch private names on the engine module, coupling helper placement to test implementation rather than gameplay behavior.

- 2026-09-24T06:40:03-0700 — Combat burst enemy-turn cleanup: the burst's enemy attack selection and its ordinary hit roll cannot move out of `logic_pure/logic_pure_combat_engine.py`, because `tests/test_brawling_gloves.py:216` patches `_combat_select_enemy_attack_pure` and `tests/test_castle_wars.py:188` and `tests/combat/test_player_attack_rolls.py:71` patch `_combat_roll_damage_lifepoints` on the engine module, and the roller cannot move to a lower module either without making the Castle Wars comment ("patched on the module that defines it") wrong.

## The inherited carried-overlay differential probe generates no coloured-feather alternatives or actual Custom potion layouts, so identical output does 

Disposition: fixed.

Evidence: Already prevented on main: existing tests catch both overlay mutations (verified by deliberate breakage in the goal/papercuts-misc simplification review).

- 2026-09-25T15:07:10-0700 — Carried overlay third cleanup: the inherited 12000-scenario overlay probe (`probe.py`, SHA-256 `4be86d954401fa5206a5f8e3af87e1becb26aa76bfe7ac5ea696eb4c993e3a4d`) never seeds Fletching material alternatives or a Custom potion layout, so replacing `carried_materials = view if view else layout if advanced else {}` with `carried_materials = view` changed 0 of 96000 reviews; only a remote run of the 543 brief tests on the mutated worktree caught it, in `test_fletching_handler_and_carried_overlay_consume_selected_coloured_feathers` (`AssertionError: False is not true`).

## Manually recounting selected test IDs with regex grep interpreted the selector's trailing dot as a wildcard and double-counted matches across selector

Disposition: fixed.

Evidence: Verified the current tree. Commit 28b48067ae32149f7bb2a1ff94d5a307d36b3886 added an authoritative 'Matching tests: N' total to --list; /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/run_tests.py:216-229 still reports that total directly from selected_ids. Commit 284d3332f6c7816b5eefa433dba97991295737c1 additionally added --count; run_tests.py:28-30 selects the union of matching IDs and :212-214 prints its count without grep or the listing cap. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/README-tests.md:37-47 documents this deduplicated count, and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:609-615 directs --expected-tests users to it. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_papercut_tools.py:585-609 covers overlapping selectors and selections above the listing cap. These tools and instructions remove the need for the error-prone manual recount; tests were inspected, not run.

- 2026-09-25T15:07:10-0700 — Carried overlay third cleanup: counting focused tests with one `grep -ci "<selector>"` per selector over the `run_tests.py --list` output summed to 553, because grep reads the selector's trailing `.` as a wildcard, so `test_agility.` also matched 10 `test_direct_action_undo_seam` methods named `test_agility_…`; the list file held 543 unique IDs, which is the count `--expected-tests` needs (use `grep -F`).

## The ad hoc snapshot checksum command used whitespace-delimited xargs, which split asset filenames containing spaces into nonexistent paths.

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: The ad hoc snapshot checksum command used whitespace-delimited xargs, which split asset filenames containing spaces into nonexistent paths.

- 2026-09-25T15:50:55-0700 — Carried overlay fourth cleanup: comparing the two `git archive` snapshot trees with `find . -type f | xargs shasum -a 256` failed on `./trees/Split Arctic pine logs.png` (`shasum: ./trees/Split: No such file or directory`), because the asset name has spaces; use `find -print0 | xargs -0`.

## Focused remote runs test a launch-time snapshot, but the runner and operator guidance do not explicitly warn that later edits require a new run before

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: Focused remote runs test a launch-time snapshot, but the runner and operator guidance do not explicitly warn that later edits require a new run before claiming final-tree verification.

- 2026-09-25T15:20:07-0700 — Combat burst player-attack cleanup: a docstring edit made two minutes after starting `tools/run_remote_tests.py` was not in the tested tree, because the runner syncs once at the start (`Sync: 3.390s (finished)`) and then ran for 186 s; the focused run (`Ran 1716 tests in 178.980s`, `OK`) had to be repeated on the final tree.

## The repository provides no supported Python lint command, so agents try unavailable global pyflakes/ruff installations and then rediscover the useful 

Disposition: fixed.

Evidence: goal/papercuts-misc: 3b8075b8, 2fd69c54, 74abdf7c, 90f8cd97, 21432c32, 5eff351c, 5734241f, simplified in 3d64a27f, 06324e44, 4b61a82b, 1106344f. Triage cause: The repository provides no supported Python lint command, so agents try unavailable global pyflakes/ruff installations and then rediscover the useful Ruff selection for the combat facade.

- 2026-09-25T16:41:04-0700 — Combat burst set-up cleanup: neither `pyflakes` nor `ruff` is installed for `/opt/homebrew/bin/python3` (`No module named pyflakes`, `command not found: ruff`); `uvx ruff check --select F821,F841` worked, and the engine carries more than 100 F811 redefinitions from its re-export blocks, so only undefined and unused-local checks are useful there.

## Ad hoc Markdown record appends leave a trailing blank separator at EOF, so the final whitespace check fails and requires manual normalization.

Disposition: wont_fix.

Evidence: A trailing blank line in progress.md is already caught by `git diff --check` before commit; a second append tool for it was removed as a duplicate (goal/papercuts-quality-tools d5b56ec0).

- 2026-09-26T09:44:58-0700 — Combat burst sixth cleanup: the final documentation check reported `memory-bank/progress.md:1368: new blank line at EOF.`; normalize the appended record to one terminal newline before the final diff check.

## A whitespace-delimited string is passed as an argument list under zsh, which does not word-split unquoted variable expansions. The metrics command con

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: A whitespace-delimited string is passed as an argument list under zsh, which does not word-split unquoted variable expansions. The metrics command consequently receives one combined pathname instead of separate inputs.

- 2026-09-26T13:24:03-0700 — Combat burst sixth cleanup (resumed): a zsh command stored three file paths in one string variable `F="a b c"` and passed `$F`, which zsh does not word-split, so the metrics script received one nonexistent path, skipped it and printed nothing with exit 0; use an array `F=(a b c)` and `"${F[@]}"`.

## A name-based completion waiter searches full command lines with pgrep -f, so the shell running the waiter matches its own probe-name pattern and keeps

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: A name-based completion waiter searches full command lines with pgrep -f, so the shell running the waiter matches its own probe-name pattern and keeps the loop alive after the probes exit.

- 2026-09-26T13:38:12-0700 — Combat burst sixth cleanup (resumed): a background waiter `until ! pgrep -f burst_probe >/dev/null; do sleep 5; done` never ended, because `pgrep -f` matched the waiter's own zsh command line, which contains `burst_probe`; the probes had finished at 13:29 and the waiters ran until killed at 13:38. Wait on the probe's output file instead.

## Repeated manual entry of an absolute worktree path introduced a typo in the username component. Reusing a verified path solved it within that session,

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: Repeated manual entry of an absolute worktree path introduced a typo in the username component. Reusing a verified path solved it within that session, but the reuse procedure is not in the repository's worktree instructions.

- 2026-09-26T14:19:54-07:00 — A repeated absolute worktree path was mistyped as `/Users/ArmanTarkhanianian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-combination-runecrafting-pack-2026-09-26`; the tool refused with `Failed to create unified exec process: No such file or directory (os error 2)` before execution. The verified path is now stored once in the tool session and reused for every command.

## Combined local audits are launched as a foreground Bash command even though the sequence can exceed the foreground timeout. The missing piece is a doc

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: Combined local audits are launched as a foreground Bash command even though the sequence can exceed the foreground timeout. The missing piece is a documented, persistent background execution path, not a failing audit.

- 2026-09-26T15:47:52-0700 — Combination Runecrafting review-fix audits exceeded the Bash foreground cap: `Command did not complete within its 120s timeout and was moved to the background (ID: bsbjd3l4o).`; the audit sequence continued, with output in `review-fix-checks.log` in the branch evidence directory.

## Papercut archival accepts a closure claim without resolution evidence, so an interrupted task can incorrectly move unresolved entries into a fixed log

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: Papercut archival accepts a closure claim without resolution evidence, so an interrupted task can incorrectly move unresolved entries into a fixed log.

- 2026-09-26T13:20:00-07:00 — Minigame XP finish: the paused author had appended its six open Minigame XP papercuts to papercuts-fixed-2026-09-23.md although none was fixed; they were moved back here verbatim.

## The disposable /tmp probe added tests/ to sys.path instead of the checkout root containing pkg_alias.py.

Disposition: fixed.

Evidence: Existing operator guidance covers this exact out-of-tree import failure. Commit ff0e4be8d063c683130843affcf5b77ef28700cb, 'Tooling: eliminate recurring repository papercuts', supplies /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/techContext.md:72-73: import pkg_alias for direct ankiscape.* probes and set PYTHONPATH="$PWD" for a harness outside the checkout. Line 37 also explicitly identifies the repository root as the sys.path entry. Verified the root helper at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/pkg_alias.py:1-10 and the existing root insertion at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/run_tests.py:180-182. The September entry repeats an already-documented invocation mistake; no missing helper or production import defect was found.

- 2026-09-26T14:53:27-07:00 — Minigame XP review fix: a one-off /tmp probe that did `sys.path.insert(0, "tests")` then `import pkg_alias` failed with 'ModuleNotFoundError: No module named 'pkg_alias'' because pkg_alias.py lives at the repository root, not under tests/; put the repository root on sys.path.

## Focused module selection included an intentionally skipped test, so the zero-skip remote gate rejected the run. Authors previously lacked a collect-on

Disposition: fixed.

Evidence: Commit 284d3332f6c7816b5eefa433dba97991295737c1 added skip-aware collect-only inventory. In the current tree, /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/run_tests.py:96-106 prints each statically skipped test ID and reason; lines 212-214 invoke it for --count. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/README-tests.md:37-56 documents this preflight and the unchanged zero-skip requirement. The intentional Great Orb hold remains at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_achievement_diary_ledger_wiring.py:602-605; the fix makes it visible before selecting the module rather than removing the hold. A read-only, in-memory probe of the current inventory helper with the actual decorator reason printed the exact held test ID and Great Orb reason without executing tests. Regression coverage for method/class skip inventory exists at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_papercut_tools.py:611-644.

- 2026-09-26T13:25:35-0700 — Prayer Off potions slice: selecting the whole `test_achievement_diary_ledger_wiring.` module for a focused plain run was refused with `error: remote focused lane false pass: tests=990, skipped=1; expected exactly 990 tests and no skips`, because `test_real_blood_altar_tablet_checks_diary_before_next_teleport` carries an unconditional `@unittest.skip` pending the owner's Great Orb ruling; select that module's tests by name instead.

## The low-life-point quest death fixture used a constant 0.5 RNG roll, allowing Count Draynor to miss instead of exercising the death path.

Disposition: fixed.

Evidence: Commit da09a13d28dc2be2c501e97f11bfd88bb34961b5 (Keep automatic fleeing on for ordinary fights after a quest fight) contains the corrected fixture. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/combat/test_quest_auto_flee.py:61-73 tests both auto-flee preferences with combat_lifepoints=1, uses rng=lambda: 0.0 at line 67, and asserts died=True and fled=False at lines 70-71. The current tree matches the committed correction. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_combat_engine.py:524-550 confirms that a zero roll lands against positive accuracy and yields at least one life point of damage for a damaging hit. No test execution was needed to establish that the named fixture error has been removed.

- 2026-09-26T09:49:48-07:00 — Quest auto-flee repair: the death fixture used `rng=lambda: 0.5`, so Count Draynor missed and both subcases failed `self.assertTrue(result["died"])` with `AssertionError: False is not true`; use deterministic landed-hit rolls for the low-life-point death path.

## The test-quality audit recognizes assertion helper calls only when the called name starts with `assert`, so conventional private `_assert_…` helpers f

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: The test-quality audit recognizes assertion helper calls only when the called name starts with `assert`, so conventional private `_assert_…` helpers falsely trigger `assertion_free_test`.

- 2026-09-26T13:37:55-0700 — Undo equipment handoff: `audit_test_quality.py` counts only calls whose name starts with `assert`, so three tests that delegate to a `_assert_…` helper reported `assertion_free_test: … test contains no assertion or assertion helper call` (`hard issues: 3`); name shared test helpers `assert_…` without the leading underscore.

## Local and remote test runners use different paths and selector syntax, and the counting workflow lacked explicit guidance about that distinction.

Disposition: fixed.

Evidence: Commit 28b48067a added counting instructions to the remote runner's --expected-tests help, explicitly showing the root-level command `python3 run_tests.py --list <selectors>` and saying `same selectors bare, without --select`. Commit 284d3332f6c7816b5eefa433dba97991295737c1 updated that command to --count. The current guidance remains in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:609-615. Reading both parsers and running both --help commands confirmed that this guidance is exposed: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/run_tests.py:128-135 defines positional selectors, while tools/run_remote_tests.py:605-607 defines repeated --select. The counting instructions now address both mistakes recorded in this entry without adding compatibility aliases.

- 2026-09-26T14:55:15-0700 — Undo equipment review fix: counting tests with `tools/run_tests.py --list` failed with `can't open file '.../tools/run_tests.py'` (the runner is at the repo root), and `run_tests.py --list --select A --select B` exited 2 with `unrecognized arguments: --select --select ...`; run_tests.py takes bare positional selectors, only run_remote_tests.py takes `--select`.

## Targeted reads and optional shell globs were constructed from guessed filenames rather than discovered paths. The filename-discovery helper exists, bu

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: Targeted reads and optional shell globs were constructed from guessed filenames rather than discovered paths. The filename-discovery helper exists, but its guidance is buried in optional context rather than the standard startup instructions.

- 2026-09-26T21:26:06Z — Winter Storage read-only diagnosis: guessed paths `tests/test_carried_new_bank_trip.py` and `logic/thieving_logic.py` returned `No such file or directory`, and optional shell globs returned `no matches found`; `rg --files` located `tests/runtime_actions/test_carried_new_bank_trip.py` and `logic_pure/logic_pure_thieving.py`.

## The review workflow does not run the authoritative diff-aware slop gate before approval, so complexity regressions can be discovered only when the rev

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: The review workflow does not run the authoritative diff-aware slop gate before approval, so complexity regressions can be discovered only when the reviewed tree is committed.

- 2026-09-27T02:50:23Z — Winter Storage commit: the pre-commit slop gate refused the reviewed inline Thieving check (`run_answer_with_carried_overlay 82 (was 79)` cyclomatic, `88 (was 87)` cognitive); any added branch in that already-over-limit function fails, so the check moved into the named `_winter_storage_rejected` helper. Reviews do not run the gate, so they can approve a tree the commit then refuses.

## Combined repository file reads produce more text than the tool can display, hiding useful evidence behind output truncation.

Disposition: fixed.

Evidence: Already prevented on main: tools/run_logged.py keeps full output and exit status (ff0e4be8).

- 2026-09-26T15:35:38-07:00 — Barbarian lap-bonus investigation: combined repository reads exceeded the tool output budget and returned `Warning: truncated output (original token count: 15881)` and `Warning: truncated output (original token count: 6855)`; capture broad reads under `.git/ankiscape-promotion-evidence/goal-barbarian-lap-bonus-2026-09-26/` and inspect bounded excerpts.

## A file-wide textual rename of self._player() also changed calls belonging to an unrelated test class with a different fixture.

Disposition: fixed.

Evidence: The erroneous lifecycle calls are absent from the current tree. Commit d1f9573400b5eac9158d84e0d61b670bb2126c40 added the shared _gloved_cook helper and its runtime/direct-action callers without changing CookingGauntletLifecycleTests. In /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_cooking_gauntlets.py:28 the cooking fixture is _gloved_cook; lines 249–257 retain the lifecycle class's separate _player fixture, and its call at line 260 still uses self._player(). Git blame confirms that the lifecycle fixture and call remain from commit 13d334df3. The reported accidental replacement was corrected before landing.

- 2026-09-26T20:00:55-0700 — Cooking glove swap review: `sed -i '' 's/self\._player(/_gloved_cook(/g'` over the whole of tests/test_cooking_gauntlets.py also rewrote CookingGauntletLifecycleTests, which has its own `_player`; scope a rename to the class's line range.

## Module-surface hashing includes imported public names, so an implementation-only module-level import changes a pinned API digest. The guard reports th

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: Module-surface hashing includes imported public names, so an implementation-only module-level import changes a pinned API digest. The guard reports the hash mismatch without explaining this import-scope constraint.

- 2026-09-26T20:14:51-0700 — Cooking glove swap review: adding one module-level import (`cooking_gauntlets_beneficial_pure`) to root `__init__.py` moved `ROOT_QT_DIGEST` from `74044844e6abb546bc2d895f337ec92c0afe66ddc9002931d65dc12256cd5f4e` to `2e5215cda8083cbdc84fb049fd06d4360f75f8d9bb9527677f28868f86e11352` (test_root_initializer_digest_under_qt); a slice that must keep the root surface imports inside the function that uses the name.

## The agent passes an unquoted glob-shaped grep option to zsh; zsh's NOMATCH expansion aborts before grep executes.

Disposition: wont_fix.

Evidence: External owner (Owner: fleet's agent-shell/tooling maintainer. Add a quote-aware Bash pre-execution guard in fleet that rejects unquoted wildcard-bearing grep options with a concrete correction such as --include='*.p); generic tooling outside this repo, not handed off.

- 2026-09-26T14:13:30-0700 — Reward transaction failure slice: in zsh an unquoted `grep -rn ... --include=*.py .` aborts with `(eval):1: no matches found: --include=*.py` before grep runs, because zsh expands the glob itself; quote it as `--include='*.py'`.

## Missing Anki source-location guidance led an agent to search the entire filesystem instead of the existing local aqt installation, exceeding the comma

Disposition: fixed.

Evidence: goal/papercuts-misc: 3b8075b8, 2fd69c54, 74abdf7c, 90f8cd97, 21432c32, 5eff351c, 5734241f, simplified in 3d64a27f, 06324e44, 4b61a82b, 1106344f. Triage cause: Missing Anki source-location guidance led an agent to search the entire filesystem instead of the existing local aqt installation, exceeding the command timeout.

- 2026-09-26T14:14:55-0700 — Reward transaction failure slice: looking for Anki's `aqt/reviewer.py` with `find / -path "*/aqt/reviewer.py"` hit the 60 s command cap; the pinned copy is already in the worktree at `.venv-qt/lib/python3.13/site-packages/aqt/reviewer.py`.

## The agent placed --no-index after the file operands, but Git requires this option before non-option arguments; startup guidance does not document that

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: The agent placed --no-index after the file operands, but Git requires this option before non-option arguments; startup guidance does not document that requirement.

- 2026-09-26T14:28:21-0700 — Reward transaction failure slice: `git diff <a> <b> --no-index --stat` fails with `fatal: option '--no-index' must come before non-option arguments`; write `git diff --no-index --stat <a> <b>` (or use `cmp`).

## Red-proof mutations and restoration are separate manual operations, so an interrupted or incomplete proof can leave mutant production code while progr

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: Red-proof mutations and restoration are separate manual operations, so an interrupted or incomplete proof can leave mutant production code while progress notes still describe the fixed version.

- 2026-09-26T20:14:39-0700 — Reward transaction failure slice: a review round's red-proof mutant of `on_answer_card` (the ungated rollback) was found in the worktree (evidence copy `review2-keep__init__.py` holds the gate, both stamped 15:58:28), while progress.md already reported the gated fix as green; restore the fixed file with `cp` + `cmp` in the same command as the red run.

## Using lowercase `path` as a zsh loop variable overwrites the special array tied to `PATH`, removing executable lookup. This is an agent-shell invocati

Disposition: wont_fix.

Evidence: External owner (Owner: fleet agent-shell/hook tooling. Add a shell-aware pre-execution guard under /Users/ArmanTarkhanian1/fleet/config/claude/hooks and register it for the applicable shell tool. Reject zsh assignmen); generic tooling outside this repo, not handed off.

- 2026-09-26T16:03:16-0700 — Undo-history review-fix reader search used `for path in ...` in zsh, overwriting the special array tied to `PATH`; later commands failed with `(eval):1: command not found: tail`, `(eval):1: command not found: rg`, `(eval):1: command not found: head`, and `(eval):1: command not found: git` (exit 127). Retried with `changed_file`; no repository-level guard prevents this shell-variable collision.

## An ad hoc completion waiter used select.kqueue() as a context manager, but that type provides close() and neither __enter__ nor __exit__. The failure 

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: An ad hoc completion waiter used select.kqueue() as a context manager, but that type provides close() and neither __enter__ nor __exit__. The failure was in the extra waiter, not the remote test runner.

- 2026-09-26T16:09:36-0700 — Undo-history review-fix completion wait assumed `select.kqueue` was a context manager; the read-only waiter exited 1 with `TypeError: 'select.kqueue' object does not support the context manager protocol (missed __exit__ method)`. The remote test driver and its completion monitor remained active.

## The implementation brief named slop-gate limits without a discoverable hook location or a repository command for measuring functions, prompting an unn

Disposition: fixed.

Evidence: Verified the current tree and git blame. Commit 9ba05589e documents the installed hook location in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/README-tests.md:10 and adds /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/maintenance/function_metrics.py:27, which resolves that location automatically. The tool delegates measurements to the actual gate and explicitly reports halstead_difficulty at lines 61–68. Commit 3feb597b7 updates /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/codex-briefs/pass15-owner-notes-handoff-2026-09-30.md:39–41 to name Halstead difficulty and direct authors to this tool. Read-only git configuration inspection confirms core.hooksPath points to /Users/ArmanTarkhanian1/fleet/config/git/hooks; its pre-commit hook invokes slop_gate.py. Gate discovery and function measurement no longer require searching the filesystem or interpreting raw radon output.

- 2026-09-26T14:04:00-0700 — Thieving fight-back slice: the brief names the pre-commit slop gate limits but not where it lives; the repo `.git/hooks/pre-commit` only runs `tools.promotion.landing_freeze_hook`, and a `find / -name slop_gate.py` hit the 120 s tool cap; the gate is `~/fleet/config/git/hooks/slop_gate.py` (via `core.hooksPath`), runnable before a commit with a temporary `GIT_INDEX_FILE` copy plus `git add -A`, and its 80 limit is Halstead difficulty, not volume.

## The passphrase-protected SSH key was absent from the local ssh-agent during the recorded runs, preventing BatchMode authentication; this was machine c

Disposition: record_only.

Evidence: The original incident is recorded at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:71 (2026-09-27T00:27:20-0700). Current read-only checks show the interruption has cleared: `ssh-add -l` lists an ED25519 identity, and `ssh -o BatchMode=yes -o ConnectTimeout=10 armans-macbook-pro true` exits successfully. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:35-36 uses those same BatchMode and connection-timeout options. The entry therefore records a past SSH-agent interruption, with no remaining authentication failure demonstrated and no repository code fix warranted.

- 2026-09-27T00:27:20-0700 — Undo bank handlers: every `tools/run_remote_tests.py` run stopped before sync with `error: remote plain prerequisites failed with exit 255; stdout: ''; stderr: 'ArmanTarkhanian@armans-macbook-pro: Permission denied (publickey,password,keyboard-interactive).'`; `ssh -v` showed `Server accepts key: ~/.ssh/id_ed25519`, but that key is passphrase-protected, `ssh-add -l` said `The agent has no identities.` and `ssh-add --apple-load-keychain` loaded none, so BatchMode cannot sign until the owner runs `ssh-add ~/.ssh/id_ed25519` on this Mac.

## The historical Mogre ruling cites a mutable kanban line number, and the current kanban still presents the already-implemented miniquest as an outstand

Disposition: fixed.

Evidence: goal/papercuts-misc: 3b8075b8, 2fd69c54, 74abdf7c, 90f8cd97, 21432c32, 5eff351c, 5734241f, simplified in 3d64a27f, 06324e44, 4b61a82b, 1106344f. Triage cause: The historical Mogre ruling cites a mutable kanban line number, and the current kanban still presents the already-implemented miniquest as an outstanding dependency.

- 2026-09-27T01:45:29-0700 — Ledger review round: `memory-bank/handoffs/design-to-impl-rulings-2026-08-13.md` §12.5 (lines 544 and 557) cites `future-work-kanban.md:1065` ("kanban line 1065") for the Mogre `DEPENDENCY: QUEST` rule, but line 1065 now sits inside the Fish Flingers card; the Mogre card is `future-work-kanban.md:610-618`, and its `DEPENDENCY: QUEST` sentence (line 612) predates the miniquest landing at `9b933084`.

## Unquoted literal arguments undergo zsh expansion before execution: leading '=' separators trigger command-path expansion, and --include=*.md triggers 

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:16 — 2026-09-26T20:58:07-07:00 (separator expansion); :64 — 2026-09-26T14:13:30-0700 (unquoted include glob). Preserve both existing survivors.. The current open log repeats both causes independently: line 16 records the identical `echo ======` failure '(eval):1: ===== not found'; line 64 records unquoted --include=*.py failing with '(eval):1: no matches found: --include=*.py'. Changing the include extension to .md does not change the cause. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-09-28.md:278 and :293 explicitly designate those same entries as the surviving records, including a previous composite entry with both failures. The supplied line 73 introduces no additional cause.

- 2026-09-28T09:47-07:00 — Native-route records slice: `echo ======` between two commands in a zsh one-liner failed again with '(eval):1: ===== not found' (third record of this zsh `=` expansion), and `grep -rn ... --include=*.md` failed with '(eval):1: no matches found: --include=*.md' because zsh globbed the unquoted pattern; quote both.

## Papercut conservation was not enforced during promotion, allowing a merge to leave the same entry both open and fixed; deleting the open copy then vio

Disposition: fixed.

Evidence: Commit f72b1723c4cb41302d52c7df6768b90d96aa33c0 is an ancestor of current HEAD and adds the missing promotion check. Verified /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/promotion/lane_execution.py:223-240 runs move_papercuts.py check against the candidate's merge base with main, and :448-452 records failure. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/promotion/contract.py:18-30 requires papercuts in full-gate evidence; /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/promotion/landing.py:35-39 rejects incomplete evidence. Regression coverage at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/promotion/test_papercut_gate_check.py:46-74 covers open-and-fixed entries, lost entries, and valid archival moves (read, not executed). The historical duplicate was preserved by moving its open copy, as recorded in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-09-28.md:7-9. A read-only check at triage time returned 'No papercut line lost since HEAD; no open papercut is also fixed.'

- 2026-09-28T09:51:12-0700 — Papercut triage 2026-09-28: at main `279be965` `python3 tools/memory_bank/move_papercuts.py check HEAD` already failed with `open and fixed: 2026-09-21T19:19:42-07:00: Full native-repair gate …`, because the 2026-09-25 triage archived the bare line while the move-tool landing (`c2e17622`) gave the open copy its bullet, and the merge kept both; no landing check runs `move_papercuts.py check`, so the conflict reached main, and the hand deletion that `systemPatterns.md:116-118` gives for a failed move then made `check HEAD` report the line as `lost:` because the base held two copies. Moving the open copy with the tool passed.

## The inherited differential overlay probe lacks a directed scenario combining a live-cadence admission that changes a profile, a Winter Storage spend, 

Disposition: fixed.

Evidence: Already prevented on main: existing tests catch both overlay mutations (verified by deliberate breakage in the goal/papercuts-misc simplification review).

- 2026-09-28T10:30:37-0700 — Carried overlay fifth slice: the inherited overlay probe (`probe.py`, 12000 x 8 reviews) changed 0 of 96000 reviews when a Winter Storage rollback skipped the cadence restore, because no probe scenario pairs a live-cadence admission that writes a profile with a Winter Storage use; a byte-identical probe result alone does not cover the rollback's cadence step.

## A targeted mutation proof ran the entire local test suite rather than the affected tests, exceeding the Bash foreground timeout. The testing guide exp

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: A targeted mutation proof ran the entire local test suite rather than the affected tests, exceeding the Bash foreground timeout. The testing guide explains selectors but does not tell agents to scope mutation checks.

- 2026-09-29T10:49:00-0700 — Combat-state sanitizer cleanup: the local full-suite mutation check exceeded the Bash 600-second cap and moved to background task `bos7z2zrn`; use a focused selection for mutation proof instead of running the entire plain suite locally.

## An ad hoc temporary-index gate wrapper captured an exit code in zsh's read-only status parameter, so the wrapper failed instead of returning the gate 

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: An ad hoc temporary-index gate wrapper captured an exit code in zsh's read-only status parameter, so the wrapper failed instead of returning the gate result.

- 2026-09-29T10:50:00-0700 — Combat-state sanitizer cleanup: the temporary-index slop-gate wrapper assigned zsh’s read-only `status` parameter and exited with `(eval):9: read-only variable: status`; use a neutral result variable such as `rc`.

## Mutation checks ran from an ad hoc rsync scratch copy rather than a complete guarded worktree, introducing asset omissions and inconsistent /tmp versu

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: Mutation checks ran from an ad hoc rsync scratch copy rather than a complete guarded worktree, introducing asset omissions and inconsistent /tmp versus /private/tmp path identity into the test results.

- 2026-09-29T10:53:08-0700 — Combat-state sanitizer cleanup: the scratch full-suite mutation proof was invalid (`Ran 5053 tests in 782.200s`, `FAILED (failures=36, errors=115, skipped=549)`) because tests compared `/tmp/ankiscape-combat-state-repair-mutation` with macOS-resolved `/private/tmp/...` paths and the rsync scratch lacked asset path fidelity; use the canonical safe worktree plus focused selectors for mutation checks.

## A search pattern beginning with '--' is passed as a positional ripgrep argument, so ripgrep parses the pattern as an option. The documented repository

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: A search pattern beginning with '--' is passed as a positional ripgrep argument, so ripgrep parses the pattern as an option. The documented repository search helper has the same defect when forwarding patterns.

- 2026-09-29T10:36:47-0700 — Combat respawn-reset slice: `rg -n "--select|select.*startswith|test_name" tools/run_remote_tests.py` treated the pattern as an option and failed with `rg: unrecognized flag --select|select.*startswith|test_name`; pass `--` before a search pattern that starts with `--`.

## The resumed review relied on a persisted shell working directory, so a relative documentation-audit command selected the canonical checkout instead of

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: The resumed review relied on a persisted shell working directory, so a relative documentation-audit command selected the canonical checkout instead of the slice worktree.

- 2026-09-29T11:37:47-0700 — Combat respawn-reset review follow-up: the first documentation audit ran from the canonical checkout because the resumed shell's working directory reset there, so it audited 875 Markdown and 454 HTML files instead of the slice; use the worktree path explicitly for every resumed command.

## The evidence-only target-lock generator used a fixed skill list that omitted Woodcutting, so Bush Snake's skill gate prevented the generated cases fro

Disposition: fixed.

Evidence: Verified the retained generator at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-target-lock-reasons-2026-09-29/differential.py:155-157: it unions the baseline skills with each enemy's skill_requirements and populates the corresponding player levels. Lines 190-191 assert that every quest-gated target reaches a quest-state read. Commit cd8ad29f688ad8c3df0f9f79fca141b4c4b76cbc recorded the correction in memory-bank/progress.md; that text now resides at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/archive/progress-2026-09.md:3242-3253. The retained historical differential-report.log:4-6 reports complete quest-gate coverage, includes bush_snake, and ends with Differential equivalence: OK. These are inspected historical results, not a new test run.

- 2026-09-29T14:18:53-07:00 — Target-lock differential: the coverage assertion failed with `AssertionError: ['bush_snake']` because generated players omitted Bush Snake’s `woodcutting_level` and stopped at `Woodcutting level 10`. The generator now derives skill keys from each real target’s `skill_requirements` before asserting every quest-gated target reaches its quest-state read.

## The agent supplied an unsupported W_placeholder field to Bash. Tool-schema validation correctly rejected the calls before execution; this is invalid t

Disposition: wont_fix.

Evidence: External owner (Owner: the external agent harness / Claude Code tool-call authoring layer. Constrain generated arguments to the advertised tool schema, and regenerate schema-rejected calls using only supported fields); generic tooling outside this repo, not handed off.

- 2026-09-29 14:39 PDT: Recording the final lane process and a later fixture lookup failed before execution with ``InputValidationError: Bash failed due to the following issue: An unexpected parameter `W_placeholder` was provided``; the tool schema blocked both calls, and the fixture lookup was moved to `Read` rather than another shell invocation.

## The long-running disposable comparator keeps its case counters in memory and emits no progress on successful cases, so the persisted log cannot identi

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: The long-running disposable comparator keeps its case counters in memory and emits no progress on successful cases, so the persisted log cannot identify the active case or distinguish forward progress from a stall.

- 2026-09-29 14:48 PDT: The disposable PvM death differential stayed CPU-active while its stdout log had no intermediate case count; it emitted only the final `Differential: cases=43858; differences=0; exception_cases=2467; random_draws=0`. Long comparator probes need persisted progress/checkpoints so a stalled case can be distinguished from a slow run; process sampling and a bounded benchmark are saved in this slice’s evidence directory.

## Markdown backticks embedded in an inline shell command are parsed as shell syntax before the Python completion assertions can run. Saving one probe as

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: Markdown backticks embedded in an inline shell command are parsed as shell syntax before the Python completion assertions can run. Saving one probe as a Python file avoids that invocation but does not prevent the command-authoring pattern from recurring.

- 2026-09-29 14:59 PDT: The final local completion command failed before execution with ``(eval):41: parse error near `"$R"'``; moved the Python completion assertions into a disposable evidence input file so Markdown backticks no longer pass through the shell command wrapper.

## The disposable combat-preview comparator copied and recursively instrumented complete enemy and equipment catalogs for every generated player state, i

Disposition: fixed.

Evidence: Verified the retained comparator, not just the papercut's claim. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-combat-preview-2026-09-29/differential.py:102 copies only player state for ordinary comparisons; lines 222–223 supply only the actual enemy row and equipped-item records for generated cases. Lines 224–225 retain separate full/default-catalog checks for every target. The saved differential-after.log:22 reports completion with cases=30253, catalog targets=203, differences=0. Commit eec784326 preserves the documented reduced-catalog method and completed result at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/archive/progress-2026-09.md:3324–3327. The specific probe overhead was already removed; this is not an outstanding production defect.

- 2026-09-29 14:54 PDT — Combat-preview differential canary: copying and recursively instrumenting the full enemy and equipment catalogs per generated state made the baseline probe slow. Stopped it after the harness canaries passed, before a complete baseline result; generated cases now use the actual target row and equipped-item records, with full/default-catalog checks retained for every target.

## The generated differential corpus supplied combat_auto_eat_food=None, an intentionally malformed selection whose existing preview behavior is to raise

Disposition: record_only.

Evidence: The entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:87 records the same exception on both base and slice and already separates malformed-state checks from list-valued value checks. Current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_combat_food.py:69-71 still iterates the supplied value directly. The intentional contract is explicit in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/combat/test_preview_food.py:100-122, which distinguishes missing, empty, and None selections and expects TypeError for None. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/combat/compare_preview_food.py:133-138 likewise declares selection:none an expected builtins.TypeError outcome; both files originate in commit d87e51be. This line records a one-time confirmation of deliberately preserved malformed-input behavior, not an unresolved automation failure.

- 2026-09-29 14:58 PDT — Generated combat-preview states reached an expected malformed-input exception (already pinned by `tests.combat.test_preview_food.PreviewFoodAvailabilityTest.test_missing_empty_and_none_food_selections_remain_distinct`): active target `menaphite_thug`, `combat_auto_eat_food=None`, `logic_pure/logic_pure_combat_food.py:69` raises `TypeError: 'NoneType' object is not iterable` on both base and slice. Replacing only the None selection with `[]` returns `Fighting`. The malformed-state differential preserves the failure; the value-focused corpus uses list-valued food selections. No production behavior was changed.

## The combat enemy registry depends on import initialization: importing core.constants mutates the base combat_data registry to add bone-source enemies,

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:39 — 2026-09-24T05:43:44-0700. The earlier open entry at memory-bank/papercuts.md:39 records the same missing frost_dragon, jogre, shaikahan, and zogre caused by importing combat_data without core.constants. The current tree still performs COMBAT_ENEMY_DATA.update(bone_source_enemies_as_dict()) at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/constants_parts/activity_updates.py:406, imported by /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/constants.py:38. Entry 88 reports correcting one verification utility's initialization context, not removing the shared cause. Keep line 39 as the earliest open survivor.

- 2026-09-29 15:18 PDT — Final combat-preview coverage probe raised `AssertionError` at `set(counts) == set(COMBAT_ENEMY_DATA)`: importing `combat_data` alone yields 199 targets and omits `frost_dragon`, `jogre`, `shaikahan`, `zogre`. Importing normal game constants and the combat engine first yields 203 targets and exact differential coverage. The verification utility now uses the same initialization context as the real differential; no production or test code changed.

## File reads used guessed filenames and directories instead of discovering existing repository paths first.

Disposition: duplicate.

Evidence: Same cause as memory-bank/papercuts.md:59 — 2026-09-26T21:26:06Z. The entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 records the same cause: guessed Winter Storage paths returned `No such file or directory`, then `rg --files` located the actual files. It predates line 89's 2026-09-29 14:52:47 PDT entry. Current path discovery confirms the survivor's files at tests/runtime_actions/test_carried_new_bank_trip.py and logic_pure/logic_pure_thieving.py; it also finds tests/test_module_surface.py and root-level pkg_alias.py rather than line 89's guessed paths.

- 2026-09-29 14:52:47 PDT — Winter Storage cleanup: guessed paths `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-winter-storage-combat-2026-09-29/tests/test_module_surface_contract.py`, `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-winter-storage-combat-2026-09-29/tests/test_logic_pure_combat_split.py` and `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-winter-storage-combat-2026-09-29/core/player_data.py` caused `No such file or directory (os error 2)`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-winter-storage-combat-2026-09-29/tests/pkg_alias.py` also returned `No such file or directory`. Use find/rg to locate existing filenames before targeted reads.

## The capacity rollback fixture added loot to carried_inventory without adding matching ownership to inventory, so the legitimate bank-ownership clamp r

Disposition: fixed.

Evidence: Commit 545f0d5e3 corrected the fixture. Verified in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/combat/test_winter_storage.py:86-88: the same 30-item loot mapping now updates both inventory and carried_inventory. Lines 93-97 assert rejection and preservation of all player fields and relevant object identities. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_combat_supplies.py:652 still clamps carried counts to ownership as intended; the malformed regression fixture no longer exists.

- 2026-09-29 14:56:43 PDT — Winter Storage regression fixture put 30 Loot entries only in carried_inventory; baseline returned True because _combat_carried_slot_counts clamps carried items against inventory. gap-tests-before.log: Ran 4 tests in 0.001s / FAILED (failures=1), AssertionError: True is not false. Populate bank ownership as well before checking capacity rollback.

## The differential probe raised SystemExit(0) at module scope, so runpy.run_path terminated the sensitivity caller before mutation assertions ran.

Disposition: fixed.

Evidence: Verified the retained probe, not just the progress report: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-winter-storage-combat-2026-09-29/differential.py:236-238 now guards SystemExit with __name__ == '__main__' and asserts no differences when loaded by runpy. The adjacent differential-sensitivity.py:45-53 asserts changed > 0 for every mutation before its final success message. The adjacent differential-sensitivity.log:8-15 contains every mutation result and the final 'Differential sensitivity: OK' message; differential-sensitivity-early-exit.log ends before those checks. Commit 545f0d5e3326d8715db3379de3748b8a082edda3 records the completed sensitivity evidence in memory-bank/progress.md:3353, now preserved at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/archive/progress-2026-09.md:3353. The corrected scripts are retained local .git evidence, not tracked source; the original early-exit cause no longer exists in the named runner.

- 2026-09-29 15:05:56 PDT — Winter Storage sensitivity runner: runpy executed the differential script’s top-level SystemExit(0), ending the caller before mutation checks despite exit 0. differential-sensitivity-early-exit.log lacks sensitivity lines. Guard the standalone exit with __name__ == "__main__" and require each sensitivity assertion.

## The differential probe's directed fixtures did not combine a multi-item Coins stack with a Coins priority, so removing stack protection produced no ob

Disposition: fixed.

Evidence: Verified the corrected probe at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-winter-storage-combat-2026-09-29/differential.py:137-141: both one-item and two-item Coins stacks have matching inventory ownership and an explicit ["Coins"] priority. differential-sensitivity.py:45-52 requires every mutation to produce a difference; the saved differential-sensitivity.log:12 reports 'Sensitivity: stack protection: 2 differences across 91 directed cases' (historical output inspected, not rerun). Durable behavior coverage landed in commit 545f0d5e3326d8715db3379de3748b8a082edda3, confirmed as an ancestor of dd788d72. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/combat/test_winter_storage.py:9,22,33-47 verifies prioritized two-item Coins remain carried; lines 50-59 verify single-item Coins can be selected; lines 63-74 verify Coins-only priority rejects the two-item stack without changing the player. The named coverage gap no longer exists.

- 2026-09-29 15:06:33 PDT — Winter Storage differential sensitivity correctly stopped at AssertionError: stack protection: directed cases had a multi-item Coins stack without a Coins priority, so the stack-filter mutation was invisible to the canary. Added explicit one-item and two-item Coins-priority cases; no production code changed.

## Unquoted optional glob patterns are expanded by zsh before the search tool runs; an unmatched pattern aborts the command with `no matches found`.

Disposition: duplicate.

Evidence: Same cause as memory-bank/papercuts.md:64 — 2026-09-26T14:13:30-0700. Read the current open log. Line 93's `tests/test_logic_pure*` and `tools/check*` failures have the same cause as line 64's unquoted `--include=*.py` failure: zsh rejects the unmatched glob before the search executes. Line 64 is the earliest matching open entry by timestamp (2026-09-26T21:13:30Z), preceding the related line 59 entry at 2026-09-26T21:26:06Z.

- 2026-09-29 15:42 PDT: Finisher cleanup searches used optional zsh globs and stopped with `(eval):1: no matches found: tests/test_logic_pure*` and `(eval):1: no matches found: tools/check*`; use `rg --glob` over known directories instead of shell-expanded optional paths.

## The focused selector was constructed from an assumed TestCase name: CombatLogicTests does not exist; the actual class is CombatLogicTest. The runner c

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: The focused selector was constructed from an assumed TestCase name: CombatLogicTests does not exist; the actual class is CombatLogicTest. The runner correctly rejects the selector, but its refusal does not explain how to discover IDs without knowing the class name.

- 2026-09-29 15:43 PDT: Focused finisher listing guessed `CombatLogicTests` and reported `No unambiguous unittest ID matched: test_combat_logic.CombatLogicTests.test_mutated`; resolve class and method names from `rg` before constructing the selection.

## An unquoted wildcard argument reaches zsh's filename expansion before the search program; an unmatched pattern aborts the command before rg or grep ru

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:64 — 2026-09-26T14:13:30-0700. The target entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:95 reports zsh rejecting memory-bank/item-reachability* before rg runs. Line 64 records the same shell-expansion cause and exact error `(eval):1: no matches found: --include=*.py`; its timestamp precedes the other matching open entry at line 59 (2026-09-26T21:26:06Z). Further repeats appear at lines 73, 93, 97, 117, and 132. Inspected /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:42-71 and :109-125: a glob-free filename discovery helper already exists, introduced by ff0e4be8d063c683130843affcf5b77ef28700cb on 2026-08-08, but the subsequent open incidents demonstrate that its availability alone has not prevented this command-construction failure.

- 2026-09-29T14:10:11-07:00 — Shaikahan route discovery: zsh rejected the unmatched memory-bank/item-reachability* glob before rg ran; use quoted patterns and directory roots.

## Repository file paths were guessed instead of discovered before targeted reads.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 — 2026-09-26T21:26:06Z. The entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:96 has the same cause as the earlier open entry at line 59: guessing flat test paths that do not exist, then resolving actual paths with rg --files. Read-only checks confirmed /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_karambwan_cooking.py is absent. Existing karambwan cooking assertions are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_cooking_data.py:54-87. The survivor's actual nested path, /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/runtime_actions/test_carried_new_bank_trip.py, also exists.

- 2026-09-29T14:10:48-07:00 — Route-test discovery guessed tests/test_karambwan_cooking.py; that file does not exist. Search actual test paths before reading.

## Repository discovery used guessed filenames and shell-expanded optional globs before locating existing paths.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 — 2026-09-26T21:26:06Z. The earliest matching open entry, papercuts.md:59, records both guessed module/test paths returning `No such file or directory` and optional shell globs returning `no matches found`, resolved with `rg --files`. Entry :97 repeats that same discovery cause with different filenames. The existing tools/repo_search.py:42-51 supports filename discovery from directory roots, and :121-125 rejects missing paths with a discovery hint; this helper is not enforced on direct shell searches, so its existence does not establish that the recurring cause is fixed.

- 2026-09-29T14:11:18-07:00 — Route discovery guessed runtime/runtime_actions_quest.py and logic_pure/logic_pure_shop.py and used an unmatched data/npc_shop* glob; switched all discovery to rg on existing directory roots.

## The probe guessed repository module paths and exported names instead of discovering the current files and symbols before use; this is a discovery fail

Disposition: duplicate.

Evidence: Same cause as memory-bank/papercuts.md line 59 — 2026-09-26T21:26:06Z. At current HEAD b0f410bf, /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 is the earliest open entry recording guessed repository paths failing before rg --files located the real modules. Line 98 repeats that cause with runtime_actions_helpers.py and an unverified import name. The current tree defines THIEVING_TARGETS in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/thieving_data.py:195; searching core/constants.py found no THIEVING_DATA, and enumerating runtime files found runtime_actions_shared.py but no runtime_actions_helpers.py. Correct data already exists; the shared remedy is verified path and symbol discovery before reads or probes.

- 2026-09-29T14:13:38-07:00 — Supply probe imported nonexistent THIEVING_DATA from core/constants.py and guessed runtime_actions_helpers.py; use THIEVING_TARGETS from the data module and discovered paths.

## Ad hoc supply probes guessed registry export names instead of inspecting the owning module's declarations.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:98 — 2026-09-29T14:13:38-07:00. The earlier open entry at papercuts.md:98 records the same supply-probe failure: importing guessed THIEVING_DATA instead of the declared THIEVING_TARGETS. The current tree declares THIEVING_TARGETS in data/thieving_data.py:195 and FARMING_CROPS/FARMING_PATCHES in data/farming_data.py:471 and :593; the Farming names FARM_CROPS/FARM_PATCHES are absent. These are the same missing symbol-discovery step, not separate production defects.

- 2026-09-29T14:14:39-07:00 — Farming supply probe guessed FARM_PATCHES/FARM_CROPS; the module exports FARMING_PATCHES/FARMING_CROPS instead. Inspect exported symbols before probes.

## Local and remote test runners use different selector syntax: run_tests.py accepts positional selectors, while tools/run_remote_tests.py accepts repeat

Disposition: duplicate.

Evidence: Same cause as memory-bank/papercuts.md line 58 — 2026-09-26T14:55:15-0700. The earlier open entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:58 records the same local invocation failure, including `unrecognized arguments: --select --select ...`. The target entry remains at line 100. Current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/run_tests.py:128-135 defines positional selectors and line 175 calls parse_args(); no --select option is defined. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:605-608 defines repeated --select flags. Preserve line 58 as the earliest entry for this cause.

- 2026-09-29T14:19:06-07:00 — Focused local route run used the remote runner --select flag; run_tests.py requires bare selectors.

## The Trio/Shaikahan route fixture chose Earth warrior as a Steel spear producer without satisfying the target's Wilderness confirmation, so the runtime

Disposition: fixed.

Evidence: Verified the current tree and git blame: commit e64c0cc8bb175e4da64cf1a5bb196c11b72d2fad changed the committed route fixture to collect Steel spears from hobgoblin_unarmed. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_bone_sources.py:575-576 sets the combat rolls and explicitly selects that non-Wilderness producer in test_review_route_earns_trio_and_shaikahan_bone_with_both_gates. The fixture no longer selects Earth warrior for this step.

- 2026-09-29T14:20:09-07:00 — Route fixture selected Earth warrior, whose real Wilderness confirmation correctly blocked combat; use the non-Wilderness Hobgoblin Steel spear producer instead.

## The route fixture incorrectly treated quest-lock rejection as a new combat result, even though the runtime rejects the target before calling the comba

Disposition: fixed.

Evidence: Commit e64c0cc8bb175e4da64cf1a5bb196c11b72d2fad contains the corrected fixture, verified in the current tree and by git blame. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_bone_sources.py:583-586 now asserts the 'Complete Tai Bwo Wannai Trio' feedback, no Shaikahan encounter, and no Shaikahan bones; it does not expect combat_last_result to change on rejection. This matches /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions_combat.py:521-538, which returns on locked reasons before the combat-kernel calls at lines 548-565.

- 2026-09-29T14:21:36-07:00 — Route fixture expected combat_last_result to change on a quest lock; the real runtime rejects before the combat kernel and retains the last fight result. Assert lock feedback and no new encounter instead.

## Papercut creation relies on hand-written appends, which can omit the required '- ' prefix; the documentation audit detects the mistake only afterward.

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: Papercut creation relies on hand-written appends, which can omit the required '- ' prefix; the documentation audit detects the mistake only afterward.

- 2026-09-29T14:27:05-07:00 — Documentation audit rejected new papercut lines with papercut_without_bullet; normalized this slice's timestamped entries to the required bullet form.

## Trio relied on a star import for TAI_BWO_WANNAI_TRIO_MONKEY_NPC_SOURCE even though that constant was intentionally excluded from sources.__all__, prod

Disposition: fixed.

Evidence: Commit e64c0cc8b added the explicit import now present at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/quest/definitions/members/tai_bwo_wannai_trio.py:6, confirmed by git blame and reading the current file. The encounter uses that binding at line 91. Grep confirms the constant is defined at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/quest/sources.py:604 and is absent from the explicit __all__ beginning at line 894, so the direct import fixes the missing binding without widening aggregate exports. No tests were run for this read-only triage.

- 2026-09-29T14:38:49-07:00 — Monkey binding local proof: run_tests.py reported “No unambiguous unittest ID matched” because the star import omitted the new source constant, causing a NameError during discovery. Trio needs a direct import; adding the binding to sources.py __all__ instead leaks a new public name into the fixed aggregate exports.

## The wrong-weapon route proof treated a rejected review as a new combat result, although the equipment gate prevents the encounter from starting and le

Disposition: fixed.

Evidence: Verified the current test and its git blame. Commit e64c0cc8bb175e4da64cf1a5bb196c11b72d2fad implements the correct proof in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_bone_sources.py:595-600: it asserts the 'Equip a karambwan-poisoned spear' feedback, absence of a Shaikahan encounter, no bone, and the unchanged Iron scimitar, without interpreting the stale combat_last_result. Lines 606-613 equip Steel spear (kp), perform the first valid Shaikahan review, verify the result's target_id, and check full-health initialization by accounting for damage, remaining life points, and healing. This existing test prevents the mistaken assertion described by the papercut; retaining the preceding result on rejection is not itself the defect.

- 2026-09-29T14:40:19-07:00 — Shaikahan wrong-weapon proof: the real runtime rejects equipment before starting combat, retaining the preceding Jogre result (player_damage 600). Assert the equipment-lock feedback and absent encounter, then measure full-health initialization on the first correctly equipped review.

## A long local audit sequence exceeded the Bash tool's 120-second foreground window and continued automatically in the background.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:52 — 2026-09-26T15:47:52-0700. Read the target entry and the open log. Line 106 (2026-09-29T14:54:25-07:00) records the post-pin audit moving to background task bml724kq7 after 120s. Earlier open line 52 (2026-09-26T15:47:52-0700) records the same cause for another local audit sequence: `Command did not complete within its 120s timeout and was moved to the background (ID: bsbjd3l4o).` Both commands continued; the later entry adds advice not to launch a duplicate, not a distinct failure cause.

- 2026-09-29T14:54:25-07:00 — Post-pin local audit sequence exceeded the 120s foreground window and the tool moved it to background task bml724kq7; leave that existing command running instead of duplicating the audit.

## The Monkey source constant was added to aggregate exports, changing the quest facade; the intended Monkey combat data also changed pinned public-value

Disposition: fixed.

Evidence: Commit e64c0cc8bb175e4da64cf1a5bb196c11b72d2fad landed the direct import at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/quest/definitions/members/tai_bwo_wannai_trio.py:6, retained the binding at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/quest/sources.py:604 without adding it to __all__ at line 894, and updated the Monkey-related module-surface pins. Read-only AST inspection confirms the constant is absent from both sources.py and quest_data.py __all__. Commit 42adb030cb1b61fe0be072cc13344fefcd196954 subsequently refreshed the merged-tree pins, present at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_module_surface.py:15–35. This verdict is based on current source and commit inspection, not a new full test run.

- 2026-09-29T15:07:51-07:00 — Final plain lane failed 10 fixed export/surface checks: adding TAI_BWO_WANNAI_TRIO_MONKEY_NPC_SOURCE to sources.py __all__ leaked a quest-facade export; the nine remaining digest failures were later isolated to the intended Monkey data values. Keep the binding out of aggregate exports and import it directly in Trio; do not change those instruments without permission.

## An optional search returns exit 1 when no matches exist; chaining an independent required command with && silently prevents that command from running.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:9 — 2026-09-26T19:19:30-07:00. Read the open log. Line 9 records a no-match grep exiting 1 and skipping an independent reader-reference search chained with &&. Line 108 records the same shell short-circuit cause, with rg and a papercut append. Line 118 records another recurrence. Line 9 is the earliest open entry for this cause.

- 2026-09-29T15:08:34-07:00 — Source-import convention search returned no matches (rg exit 1), so an &&-chained papercut append did not run; record evidence independently of an expected no-match search.

## Intended Monkey quest-data changes invalidated value-inclusive module-surface baselines, while the slice's fixed-instrument rule initially blocked reg

Disposition: fixed.

Evidence: Commit e64c0cc8bb175e4da64cf1a5bb196c11b72d2fad is an ancestor of current HEAD; its diff regenerates the affected FIRST_WAVE_DIGESTS entries and ROOT_QT_DIGEST in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_module_surface.py. The current baseline table remains at lines 15-35. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/archive/progress-2026-09.md:4274-4280 records resolution of the permission conflict, the isolated Monkey-field causality proof, and generated baseline updates without changes to checking logic. Reading /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/module_surface.py:133-139,301-309 confirms that complete public data values still enter the digest; the instrument was not weakened. This entry's baseline conflict has been resolved, not left for a fixer.

- 2026-09-29T15:31:00-07:00 — Corrected export proof still failed nine fixed data-surface checks: module_surface.py hashes complete public quest-data values, not just export names. A disposable in-memory removal of only the Monkey fields restored all four plain pins exactly; keep the fixed instruments unchanged and escalate the pin-update permission conflict.

## An unbounded, broadly scoped repository search exceeds the tool output budget; the re-pin subject is incidental to the failure.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:61 — 2026-09-26T15:35:38-07:00. The target entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:110 records a broad search producing 65.4KB. The earlier open entry at line 61 records combined repository reads exceeding the output budget and recommends bounded excerpts. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-09-28.md:342-350 already groups broad searches and batched reads under this same survivor, including an unbounded progress.md search. Existing advice at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/techContext.md:40-49 and optional bounds in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:74-106 do not prevent direct unbounded searches, so this is not a separate re-pin defect or a verified fix. The output size is quoted from the incident, not newly measured.

- 2026-09-29T16:05:11-07:00 — Re-pin precedent search used broad surface/re-pin alternatives across progress and tooling and produced 65.4KB of output; bound this search by the cited commit and dated section before expanding context.

## The count-checking probe assumed run_tests.py --list includes its summary in stdout, but stdout contains only test IDs and the summary is written to s

Disposition: fixed.

Evidence: Commit 284d3332f6c7816b5eefa433dba97991295737c1 added a dedicated stdout count interface after this entry. Verified in the current tree: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/run_tests.py:96-106 prints the --count summary to stdout and skip diagnostics to stderr; lines 136-144 explicitly document the streams. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/README-tests.md:37-48 directs count callers to --count and states that --list retains ID-only stdout. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:610-615 also directs expected-count collection to --count. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_papercut_tools.py:601-609 verifies the separated count stdout contract. Legacy --list still writes its summary to stderr; the permanent remedy is the documented dedicated count interface, not changing the listing stream.

- 2026-09-29T16:24:49-07:00 — Runnable surface-selection listing failed with AssertionError: run_tests.py writes Matching tests: 8 to stderr, so listing.stdout.rstrip().endswith('Matching tests: 8') misses the measured count. Preserve stdout and stderr before checking the count.

## Repository discovery used assumed headings and file paths before bounded lookup, producing missing-file errors and oversized search output.

Disposition: duplicate.

Evidence: Same cause as memory-bank/papercuts.md:59 — 2026-09-26T21:26:06Z — Winter Storage read-only diagnosis. The open survivor at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 records guessed test paths failing until rg --files located the actual files. The same cause is explicitly grouped under 'Paths and globs used before they were discovered' in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-09-28.md:207-209, which retains that survivor. Entry 112's additional output-overflow symptom is already represented by the open entry at papercuts.md:61 (2026-09-26T15:35:38-07:00). Inspected tools/repo_search.py:42-71, 74-106, and 111-125: bounded filename/content search and missing-path guidance already exist; memory-bank/techContext.md:40-49 documents discovery before content reads. Their existence does not establish a new fix for agents bypassing discovery.

- 2026-09-29 16:45 PDT — Focused tooling slice: the brief’s proposed-heading text did not match the numbered bold heading in progress.md; broad searches overflowed the tool output, and guessed flat test paths failed with `No such file or directory (os error 2)`. Locate headings and test filenames with bounded name searches before reading content.

## A review searched an assumed module filename before discovering the actual file or imported symbol, so rg received a nonexistent path.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 — 2026-09-26T21:26:06Z. The earlier open entry at papercuts.md:59 records the same cause: guessed repository paths returned `No such file or directory`, and `rg --files` found the real locations. Entry 113 repeats that discovery failure with `tools/promotion/test_summary.py` and `No such file or directory (os error 2)`. Reading the current tree confirms that TestSummary is defined at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:100 and parse_unittest_summary at line 135; the entry does not identify a defective parser or missing intended module.

- 2026-09-29 17:50 PDT — Focused tooling review guessed tools/promotion/test_summary.py and rg returned `No such file or directory (os error 2)`; parse_unittest_summary and TestSummary are defined in tools/run_remote_tests.py. Search the imported symbol before guessing a module path.

## A one-off contract-check probe assumed a saved, human-labelled exit record was a bare integer; the add-on and its maintained tooling were not the fail

Disposition: record_only.

Evidence: The saved record at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-test-inventory-tooling-2026-09-29/list-before.exit:1 is exactly `List before exit: 2`. The adjacent review-fix/contract-check-format-fault.log:24–28 reproduces the original int(read_text()) failure. The corrected review-fix/check_contract.py:76 extracts the field with .split(': ', 1)[1], and review-fix/contract-check.log:24–25 records unchanged capped-list behavior and `Contract check: PASS`. These are disposable evidence files under .git, not maintained repository tooling: git ls-files finds no check_contract, list-before, or contract-check files, and searches of tools/ and tests/ find no corresponding parser. This records a resolved, one-time probe mistake, not an outstanding repository defect or a committed prevention fix. No other open entry matches this cause.

- 2026-09-29 17:58 PDT — Focused tooling contract check parsed list-before.exit as a bare integer, but the saved record is `List before exit: 2`; int() raised `ValueError: invalid literal for int() with base 10: 'List before exit: 2\n'`. Read the saved record format before parsing it; the corrected probe parses the labelled exit field.

## The ad hoc handoff verifier treated every unittest summary in a combined raw log as the outer run, although disposable child processes also emit summa

Disposition: fixed.

Evidence: goal/papercuts-runner: 6c80d2ba, a5794c12, simplified in 6eea943d, a82e850a, 0b5ee1a4, 0287cdc7. Triage cause: The ad hoc handoff verifier treated every unittest summary in a combined raw log as the outer run, although disposable child processes also emit summaries. The corrected extraction remains only in an untracked evidence script, not in reusable repository guidance.

- 2026-09-29 18:02 PDT — Progress proof compared every `Ran` line in the fault-red raw log with the outer-run handoff, but the log also contains disposable child summaries (`Ran 1 test in 0.000s`); the check raised `AssertionError`. Compare the final outer summary, not all nested summaries, and keep complete child output in the raw log.

## Unbounded repository discovery exceeded the tool output budget; guessing an optional search root added a missing-path error.

Disposition: duplicate.

Evidence: Same cause as memory-bank/papercuts.md:61 — 2026-09-26T15:35:38-07:00. The open survivor at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:61 records combined repository reads exceeding the same output budget. Entry 116 repeats this cause with `Output too large (82.6KB)` during progress/papercut discovery. The `.claude` error is an additional guessed-root discovery mistake, not evidence that a cleanup-rules file should exist. Checked /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:26-31,74-106,115-125: the existing helper validates paths and bounds results and columns. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/techContext.md:42-49 documents discovery of exact paths before bounded content searches, but these safeguards do not constrain raw broad commands. Preserve the earlier open entry rather than dispatch another fix for the same discovery failure.

- 2026-09-29T16:50:43-07:00 — Function-metrics tooling discovery: the broad progress/papercut search exceeded the tool output limit (`Output too large (82.6KB)`), and a chained directory search guessed absent `.claude` (`rg: .claude: IO error for operation on .claude: No such file or directory (os error 2)`); bounded searches found the triage at `memory-bank/progress.md:4096` and checked-in rules under `.rulesync/rules/`. No repository cleanup-rules file exists.

## An agent used a guessed, unmatched pathname glob before discovering actual files. zsh rejected the glob before the command ran, so the chained local r

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 — 2026-09-26T21:26:06Z. The earlier open entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 records guessed paths and optional shell globs failing with `no matches found`, the same cause as line 117. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-09-28.md:461-466 already consolidates equivalent pathname-glob failures into that survivor. Read /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:42-51,112-125: bounded filename discovery and missing-path guidance exist, but callers can still bypass them; this is not proof that the recurring cause is fixed.

- 2026-09-29T16:52:05-07:00 — Function-metrics agreement lookup: zsh rejected guessed `logic_pure/model/combat_model*.py` with `(eval):1: no matches found: logic_pure/model/combat_model*.py`; the chained optional local red run never started. The required remote red run completed independently; use named files or bounded discovery rather than an unverified shell glob.

## An optional no-match search returns exit 1 and, when chained with &&, prevents a required follow-up command from running.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:9 — 2026-09-26T19:19:30-07:00. The open entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:9 records an optional grep probe returning exit 1 with no matches and skipping the required reader-reference search chained with &&. Line 118 records the same control-flow mistake with rg, followed by a missing log because the inventory command never ran. Line 108 also repeats this cause. Line 9 is the earliest matching open entry; the different search targets do not change the cause.

- 2026-09-29T16:58:27-07:00 — Function-metrics neighbour discovery: optional `rg -l 'audit_papercut_inventory' tests` found no matches (exit 1), so a following `&&` inventory never ran and reading `final-focused-inventory.log` failed with `No such file or directory`; the repeat showed that optional discovery must not be a success prerequisite for required checks. Required commands now run independently, with their own saved status.

## A shell wrapper assigned to zsh's read-only `status` parameter while capturing a command's exit code, causing the wrapper to fail after the check comp

Disposition: duplicate.

Evidence: Same cause as memory-bank/papercuts.md:77 — 2026-09-29T10:50:00-0700. The current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:77 already records a temporary-index wrapper assigning zsh's read-only `status` parameter and failing with `(eval):9: read-only variable: status`. Line 119 records the same variable collision with `(eval):1: read-only variable: status`; the different wrapper and error line number do not change the cause. Line 77 is the earliest open entry for this cause.

- 2026-09-29T17:57:03-07:00: Preparing the review papercut-conservation evidence trailer failed after the check ran: `(eval):1: read-only variable: status`; zsh reserves `status`, so evidence command exit capture uses Python subprocess instead.

## A papercut was appended without the required '- ' bullet prefix, causing the documentation audit to reject the entry.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:103 — 2026-09-29T14:27:05-07:00. The earlier open entry at memory-bank/papercuts.md:103 records the same missing-bullet failure and exact diagnostic 'papercut_without_bullet'. The selected entry at line 120 repeats that cause while quoting the separate shell error recorded at line 119. tools/audit_docs.py:237-241 confirms that any nonempty papercut line not starting with '#' or '- ' produces 'papercut_without_bullet'. Correcting this particular line does not remove the recurring append-format cause.

- 2026-09-29T17:57:52-07:00: Appending the review shell-friction note without the required bullet failed the documentation audit: memory-bank/papercuts.md:103: papercut_without_bullet: 2026-09-29T17:57:03-07:00: Preparing the review papercut-conservation evidence trailer failed after the check ran: `(eval):1: read-only variable: status`; zsh reserves `status`, so evidence command exit capture uses Python subprocess instead. The bullet prefix is corrected; the failing audit log is preserved in `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-function-metrics-tooling-2026-09-29/review-docs-pre-lane-before-bullet-fix.log`.

## The S2 helper was initially re-exported through a new dependency edge from runtime_actions.py, increasing an already over-limit import fan-out and tri

Disposition: fixed.

Evidence: Commit ccba19269e5f0050b45f626d46d3d255653ece39 corrected the helper placement and export chain. The current tree defines drop_superseded_bank_run_requests_pure in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions_carried_overlay.py:419, re-exports it through the existing overlay import at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions_carried.py:444-447, and extends the existing carried-facade import at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions.py:507-528. The commit diff adds the helper name to those existing import lists, not a new module import. This removes the dependency-edge increase described in the entry; the gate remains intact.

- 2026-09-30T22:34:46-07:00: Pass 15 S2 commit refused by slop-gate: `slop-gate: import fan-out above 25 was introduced:` / `runtime/runtime_actions.py: fan-out 120 (was 119)`, because `__init__.py` reaches runtime helpers only through `runtime_actions.X` and a new re-export block named a submodule `runtime_actions.py` did not import yet. Add a new runtime helper to a submodule the `runtime_actions_carried` facade already re-exports, and extend the existing import lists instead.

## The S2 review fix extended a bank-trip preservation pin inside an oversized test file, triggering slop-gate's file-growth ratchet.

Disposition: fixed.

Evidence: Commit 01457f45642689a63634f13934ae69b3872e959d, verified as an ancestor of HEAD, removed test_bank_request_survives_reviews_on_another_surface from /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_runtime_actions.py and folded its behavior into the focused test. The current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/runtime_actions/test_bank_run_request_target.py:79-92 starts a quest, executes a quest review, and asserts that the unrelated queued bank trip survives without activity. Reading the original file at lines 5535-5559 and searching both files confirms that the old pin is absent. The specific oversized-file extension recorded in this entry has been removed; the ratchet remains intentional.

- 2026-09-30T22:55:00-07:00: Pass 15 S2 review-fix commit refused by slop-gate: `slop-gate: code files above 1000 lines were grown:` / `tests/test_runtime_actions.py: 5942 lines (was 5935)`, because the brief ordered a pin change inside that file. A brief that names a pin in an oversized test file means move or fold the pin into the slice's focused test file; extending it in place cannot land.

## Linked worktrees share the repository's stash stack; an unqualified `git stash pop` can therefore restore a different author's newer stash during para

Disposition: wont_fix.

Evidence: Generic shell, git, Python or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge. Triage cause: Linked worktrees share the repository's stash stack; an unqualified `git stash pop` can therefore restore a different author's newer stash during parallel work. Worktree isolation does not isolate stash entries.

- 2026-09-30T22:35:00-07:00 — Pass 15 S3 load-bearing proof: `git stash push -- <file>` / `git stash pop` in a linked worktree uses the stash list shared by every worktree of the repo (seven entries from other branches, `stash@{0}`..`stash@{6}` once mine was popped), so with eight slice authors running at once a `pop` can restore another agent's entry. Copy the file aside and copy it back instead of stashing.

## Slice guidance lists oversized product files but does not explicitly include test files or explain how to update pins in oversized tests without growi

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: Slice guidance lists oversized product files but does not explicitly include test files or explain how to update pins in oversized tests without growing those files. The slop-gate correctly applies its line-growth ratchet to tests too.

- 2026-09-30T22:34:30-07:00 — Pass 15 S3 line budget: the brief's capped-file list omits tests, but slop-gate's 1000-line ratchet (`FILE_LINES_MAX` in `~/fleet/config/git/hooks/slop_gate.py`) also counts `tests/test_logic.py` (12506), `tests/test_main_menu_widget.py` (19883) and `tests/test_target_metadata.py` (2460); new eel assertions moved into the small `tests/test_fishing_data.py` to stay flat.

## Top-level deletion from a returned player-state dictionary does not propagate through the runtime's dict.update merge; completed quest encounters must

Disposition: fixed.

Evidence: Commit 9a2b4fc240812fd6825502cd9539d46ff8f01b51 implements the required empty-value assignment at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_quest.py:1384 and only restores an encounter for an unfinished fight at line 1393. The runtime still merges and saves the result at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions_production.py:1265-1269, so the explicit assignment is necessary and correct. The same commit adds the real-runtime multi-review regression at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_combat_quest_gate.py:427-449, including the assertion at line 448 that the live player dictionary contains an empty quest_combat_encounter after the kill; returning a dictionary with that key popped would fail this assertion after earlier reviews populated it. Verified current source and git blame; tests were not run. The entry already records correcting the truncated manual search with an AST walk; head limiting search output is not a repository defect that needs a separate code change.

- 2026-09-30T23:03:30-07:00 — Pass 15 S4: popping a key from the dict a pure function returns does not clear it in the save, because the runtime merges with `player_data.update(new_data)`; clear state by assigning an empty value. Also, `grep ... | head -30` hid 20 of 21 `apply_quest_combat_encounter_pure(..., stop_after_first_kill=...)` test call sites; an AST walk over call keywords found them all.

## A space-separated scalar is passed as one argument under zsh, which does not word-split unquoted parameter expansions. This is the same cause as the e

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:49 — 2026-09-26T13:24:03-0700. The earliest matching open entry is papercuts.md:49: F="a b c" reached the metrics tool as one path, with arrays and "${F[@]}" identified as the remedy. A read-only /bin/zsh -f probe confirmed that $SEL containing two dotted selectors produces one argument. In /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/run_tests.py:128-135 and 203-205, positional selectors are resolved individually; lines 79-84 produce the reported refusal without a shell-specific hint. The appended metrics-runtime observation is independently represented by open entries at papercuts.md:128, 131 and 137. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/maintenance/function_metrics.py:58-65 still measures the complete source snapshot through the fleet instruments. This verdict consolidates the repeated shell-argument cause, not a claim that the analyzer runtime is fixed.

- 2026-09-30T23:13:00-07:00 — Pass 15 S4 focused run: a selector list held in a shell variable reached `run_tests.py` as one argument under zsh (`No unambiguous unittest ID matched: bar_crawl.test_quest_route bar_crawl.test_quest_ui ...`), because zsh does not word-split unquoted `$SEL`; `$(cat selectors.txt)` splits. Also, `function_metrics.py` on `ui/ui.py` runs past the 120-second tool cap, so run it in the background.

## Cognitive-complexity measurement reanalyzes the complete ui/ui.py source through complexipy even when only one import or function is relevant; the sam

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:137 — 2026-09-30T22:37:00-07:00 (the ui/ui.py measurement exceeding the tool timeout). The earliest timestamped open report of this full-file measurement bottleneck is papercuts.md:137; lines 127 and 131 also record it. Verified the shared implementation: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/maintenance/function_metrics.py:54-64 copies the entire source file and calls gate.cognitive_by_function(snapshot). /Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py:175-192 runs complexipy over that snapshot, and lines 853-863 materialize complete staged and HEAD files and analyze both for commits. This establishes a common cause rather than merely similar timeout symptoms. The recorded durations were not remeasured; no expensive analyzer or commit was run.

- 2026-10-01T00:20:00-07:00 — Pass 15 S4 review fix: committing a one-line import move in `ui/ui.py` held the pre-commit hook about 15 minutes (00:00 to 00:20), because `/Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py` runs `complexipy` over the whole 29,292-line file; the Bash call hit its 300s cap and went to background, so budget for it or wait on the hook PID instead of the tool timeout.

## Qt's stock wrapped-row size hint uses a width larger than the painted text area and omits item side padding, causing Shop labels to be elided or rows 

Disposition: fixed.

Evidence: Verified fixing commit 1d401116f10b846df7417e770fdea2136b483376 and the current tree. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_tab_shop_widgets.py:17-29 defines WrappedRowDelegate and calculates the size hint using viewport width minus both side paddings. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_tab_shop.py:109-116 enables wrapping, installs this delegate, and uses the same ROW_SIDE_PADDING in the item stylesheet. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/ui_flows/test_shop_locks_and_purchase.py:83-98 checks narrow-list row boundaries and sufficient height for wrapped labels. Tests were inspected, not executed.

- 2026-09-30T22:31:00-07:00: Wrapping the Shop list rows (`setWordWrap(True)`, horizontal scroll off) still elided boundary rows such as "Keldagrim Stonemason · Requires starting The Giant ..." and cut the second line of others, because the stock size hint wraps at a layout width (396) wider than the painted row (392) and ignores the `QListWidget::item` side padding; `visualItemRect` then showed row 228 ending at 295 while row 229 began at 281. `WrappedRowDelegate` in `ui/ui_tab_shop_widgets.py` sizes rows at the viewport width minus the padding.

## The text-fit helper equates a QPushButton's preferred style size with the minimum space needed to render its text. Capped-width Qty buttons therefore 

Disposition: fixed.

Evidence: goal/papercuts-misc: 3b8075b8, 2fd69c54, 74abdf7c, 90f8cd97, 21432c32, 5eff351c, 5734241f, simplified in 3d64a27f, 06324e44, 4b61a82b, 1106344f. Triage cause: The text-fit helper equates a QPushButton's preferred style size with the minimum space needed to render its text. Capped-width Qty buttons therefore produce false clipping defects, and the shop test preserves those defects as its baseline.

- 2026-09-30T22:29:00-07:00: `text_fit_defects` on `shopTransactionPanel` reports "'1' is clipped in PyQt6.QtCore.QSize(44, 25)" (also '5', '10', '50', and 'All' in QSize(50, 25)) although the offscreen screenshot shows each Qty label whole: the helper compares `QPushButton.sizeHint()`, which carries the style's minimum button width, against a width capped by `setMaximumWidth`. The S7 widget test compares defects with and without the chip instead of asserting an empty list.

## The function-metrics CLI accepts a uniquely named nested function during AST validation, although the gate's cognitive instrument does not expose that

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: The function-metrics CLI accepts a uniquely named nested function during AST validation, although the gate's cognitive instrument does not expose that closure separately. It runs the full-file instruments before discovering the unsupported selection, then reports a generic missing-entry error instead of identifying the enclosing measurable function.

- 2026-09-30T22:40:00-07:00 — Measuring the Skills-tab target builders in ui/ui.py with `python3 tools/maintenance/function_metrics.py --output /tmp/s8_metrics_ui.json ui/ui.py _build_combat_list ...` ran past the 600 s tool cap and then exited 2 with `function_metrics.py: error: _build_combat_list: expected one cognitive entry from slop-gate, found 0`: complexipy reports only top-level functions, so the closures inside `show_main_menu` are measurable only as `show_main_menu` itself, and the gate's ratchet compares that one entry against HEAD.

## An unquoted grep --include=*.py argument is expanded by zsh before grep starts, causing `(eval):1: no matches found: --include=*.py`.

Disposition: duplicate.

Evidence: Same cause as memory-bank/papercuts.md:64 — 2026-09-26T14:13:30-0700. The open entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:64 records the same unquoted grep argument, identical error, and correction `--include='*.py'`. It precedes the target entry at line 132, timestamp 2026-09-30T22:17:20-07:00. Inspected /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:34-39 and :109-116: the helper avoids shell globs but does not guard ad hoc grep commands; its latest change, db14782b on 2026-08-11, predates both incidents and is not evidence that this recurring cause was removed.

- 2026-09-30T22:17:20-07:00 — Pass 15 S5 fact check: `grep -rn "vendor_action" --include=*.py .` failed under the agent shell with `(eval):1: no matches found: --include=*.py`, because zsh expands the unquoted glob before grep sees it; quote it as `--include='*.py'`.

## Fetching pinned revision text through the RuneScape Wiki article endpoint can return bot-check HTML instead of wikitext; revision-content retrieval sh

Disposition: fixed.

Evidence: The repository already provides the preventive API route in commit 271bcd264eeab637e25a4aa44a4d7ba558d76e14. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/wiki_parity.py:44 selects https://runescape.wiki/api.php; lines 94–104 fetch content by revision ID through action=query and prop=revisions; lines 143–145 expose that route through content --revid. Its documented specific-revision command is at lines 24–25. The local research recipe at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.claude/skills/ankiscape-skill-expansion/wiki-parity-scrape.md:23 explicitly says to use this tool rather than re-derive curl/JSON calls, and lines 35–36 show the revision-ID command. These files were read and the API implementation was verified against git blame. The entry itself records that the API returned the requested revision text. The external article endpoint's bot check is not removed, but the existing tool and instructions prevent reliance on that endpoint for this task.

- 2026-09-30T22:56:49-07:00 — Pass 15 belt-tools source check: `curl "https://runescape.wiki/w/Tool_belt?oldid=6538396&action=raw"` returned a 42 KB "Please wait" bot-check HTML page instead of wikitext; the MediaWiki API (`/api.php?action=query&prop=revisions&revids=6538396&rvprop=content&rvslots=main&format=json`) returned the revision text directly.

## The command assumes an unquoted scalar expansion splits into separate arguments, but zsh preserves the scalar as one argument. Consequently, `set -- $

Disposition: duplicate.

Evidence: Same cause as memory-bank/papercuts.md:49 — 2026-09-26T13:24:03-0700. The earlier open entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:49 records the same zsh scalar word-splitting assumption when passing file paths to a metrics script. Entries at lines 127, 134, and 137 repeat this cause. A read-only `/bin/zsh -f` probe of `set -- $spec` with `spec="file fn fn"` returned `argument_count=1 first_argument=file fn fn`. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/maintenance/function_metrics.py:99-100 requires a file argument followed by one or more function arguments, explaining the recorded argparse error.

- 2026-09-30T22:56:49-07:00 — Pass 15 belt-tools metrics loop: `for spec in "file fn fn"; do set -- $spec` does not word-split in zsh, so `tools/maintenance/function_metrics.py` got no function names (`error: the following arguments are required: functions`); call it once per file instead.

## The test treated an inventory key's presence as item ownership, but fresh-save inventory includes registered items with quantity zero.

Disposition: fixed.

Evidence: Commit 7bca9f86c corrected the belt-tools ownership assertions. In /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_logic.py:8189 the test creates a fresh save; line 8230 checks Fishing rod with assertEqual(druidic["inventory"].get("Fishing rod", 0), 0), and line 8242 does the same for Chisel. Git blame attributes line 8230 to that commit. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/storage_pure.py:461-465 confirms registered inventory keys default to zero. A search of the current tests found no assertNotIn ownership checks for Fishing rod or Chisel.

- 2026-09-30T22:56:49-07:00 — Pass 15 belt-tools tests: `default_player_data` lists every registered item at 0, so `assertNotIn("Fishing rod", data["inventory"])` fails on a fresh save; assert `data["inventory"].get(name, 0) == 0` for "not owned".

## Tracked status pages referenced local MP4 files excluded from Git, so clean remote checkouts lacked the media and audit_docs reported broken_html_targ

Disposition: fixed.

Evidence: Commit 6637e28176284e73259d3f13e7300e26f4705694 removed the affected pages from tracking and added explicit exclusions at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/status-updates/.gitignore:2-4, including pass15-plan-2026-09-30.html. Commit d7469c9a79e606cf18658a83af0114dc60b40733 added the results-page exclusion at line 5. Current git check-ignore confirms the plan and results exclusions; git ls-files confirms all four excluded pages are untracked. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/audit_docs.py:93-101 excludes ignored untracked files from its document inputs, preventing the recorded remote audit failure.

- 2026-10-01 01:04 Pass 15 gate: committing status artifacts that embed a <video> fails audit_docs on the remote host ('broken_html_target: pass15-plan-2026-09-30.mp4') because the status-artifact render script gitignores *.mp4; artifacts with a video stay local, listed in memory-bank/status-updates/.gitignore.

## The function-metrics helper accepts only globally unique bare function names and forbids evidence beside the measured source, but its errors do not ex

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: The function-metrics helper accepts only globally unique bare function names and forbids evidence beside the measured source, but its errors do not explain a usable workflow or the gate's identity limitations. Repeated-method targets therefore trigger retries that cannot succeed.

- 2026-09-30T22:37:00-07:00: Measuring Pass 15 finisher functions with `tools/maintenance/function_metrics.py`: a base copy kept beside the evidence file under `/tmp/pass15-shots/finisher-notice/` was refused with `--output must be outside the worktrees and measured source directory`, `set_data` in `ui/ui.py` cannot be measured at all (`expected one function definition, found 14`; `ReviewHUD.set_data` finds 0), and measuring one `ui/ui.py` function ran past the 300 s tool cap. A zsh `for spec in "file fn"; set -- $spec` loop does not word-split and produced a misleading `error: file must be an existing Python source file`.

## The slice brief omits oversized test files from its capped-file list, although slop-gate's 1000-line no-growth ratchet also applies to tests.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:124 — 2026-09-30T22:34:30-07:00. Read the current open log. Line 124 explicitly records the same brief omission and test-file ratchet, names both tests/test_main_menu_widget.py and tests/test_target_metadata.py, and describes relocating new assertions to a focused test file. Its timestamp precedes line 138's 2026-09-30T22:46:00-07:00. Line 122 records another instance at 2026-09-30T22:55:00-07:00, later than the survivor. Moving this slice's assertions avoids the refusal but does not independently resolve the briefing omission.

- 2026-09-30T22:46:00-07:00: Pass 15 finisher slice: slop-gate's 1000-line growth refusal also covers test files (`tests/test_main_menu_widget.py` 19903, `tests/test_target_metadata.py` 2465 lines); the slice brief lists only product files, so new assertions moved to `tests/ui_flows/test_slayer_progress.py` before the commit.

## Parallel slices append checklist entries at the same location, but the tracked merge policy does not cover memory-bank/play-checklist.md. The workarou

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: Parallel slices append checklist entries at the same location, but the tracked merge policy does not cover memory-bank/play-checklist.md. The workaround exists only in this checkout's untracked Git metadata.

- 2026-10-01 00:22 Pass 15 integration: seven slices each appended to memory-bank/play-checklist.md at the same spot, so git merge-tree reported content conflicts in that file for 3 of 8 merges; added 'memory-bank/play-checklist.md merge=union' to .git/info/attributes beside the existing papercuts union line.

## The standing contract's documentation-only Qt exemption does not distinguish slice verification from landing authorization. The landing tool correctly

Disposition: fixed.

Evidence: goal/papercuts-quality-tools: 9c48b073, 7602e258, c302fd86, 6bba4d49, 6c30ff8b, 51386a97, c39c77f9, 1398ecc7, simplified in b84058d8, db86c461, d5b56ec0, 01bab391, e3deff07, 41a0dc8d. Triage cause: The standing contract's documentation-only Qt exemption does not distinguish slice verification from landing authorization. The landing tool correctly requires a full gate, but an agent following the exemption can complete a plain-only gate before discovering that its receipt cannot authorize landing.

- 2026-10-01 02:10 October rotation: promotion_gate.py run --plain-only passed on docs-only 82a870c6, but land refused it: 'Landing refused: evidence for 82a870c6... did not pass every full-gate check'; the contract's documentation-only exception does not reach landing, so docs-only batches still need the Qt lane.

# Staged papercuts from 2026-09-05, closed 2026-10-01

These entries sat in `memory-bank/pending/*-papercuts-2026-09-05.md` and never reached `papercuts.md`. A per-entry triage on 2026-10-01 (main eb9fcb90) closed every one; the pending files are removed. Each entry keeps its source file and line.

## A read-only progress probe treated the runner's transient pending record as a durable status file. Normal completion deletes that record, so an unlock

Disposition: fixed.

Evidence: goal/papercuts-staged ad1741ea: tools/run_remote_tests.py says the pending record is temporary and prints the exact run's log and report paths.

Source: memory-bank/pending/complexity-recovery-papercuts-2026-09-05.md line 3 at main eb9fcb90

- 2026-09-06T05:27Z: The parent attempted a read-only progress snapshot as remote Qt completed; the pending record was already removed and `read_text` raised `FileNotFoundError: [Errno 2] No such file or directory: '/Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.pending.json'`. Reconcile the completion log when the pending record disappears; do not assume it persists between observations. No remote command ran or retry was needed.

## A branch-history audit used `git log --all`, which also traverses T3 checkpoint refs and floods the output with non-branch history. The repository has

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/complexity-recovery-papercuts-2026-09-05.md line 4 at main eb9fcb90

- 2026-09-06T05:29Z: The first scoped move-history query used `git log --all`, which included hundreds of `refs/t3/checkpoints` entries and truncated the output. Restrict this audit to `--branches` or immutable accepted commits.

## The complexity-inventory reconciliation included below-threshold raw rows outside the audit scope, causing an unnecessary AST lookup for a duplicated 

Disposition: fixed.

Evidence: Commit 91c394170dd94d832bddeb0824c32843703926f9 retained the corrected inventory. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/exposed-complexity-2026-09-05.md:92 explicitly limits the inventory to above-threshold functions. The current archived recovery-script.py.gz has `if not above(row): continue` at decompressed line 96. Reading the current archived complete-function-inventory.json.gz verified zero below-threshold inventory rows and no inclusion of `_on_main_menu._on_main_menu._apply_achievement_diary_command._change` among raw_metric_names. The original raw measurement remains preserved with CCN 2 and null cognitive/Halstead values; the correction restores scope rather than rewriting evidence or claiming Lizard's naming behavior was fixed.

Source: memory-bank/pending/complexity-recovery-papercuts-2026-09-05.md line 6 at main eb9fcb90

- 2026-09-07: Reconciliation initially included below-threshold Lizard rows; its duplicated nested name `_on_main_menu._on_main_menu._apply_achievement_diary_command._change` did not uniquely match the AST. Restored the retained audit's above-threshold raw-row scope; no metrics rerun or evidence replacement.

## The complete complexity inventory initially omitted ast_sha256 and retained raw metric rows from its provisional candidates, so the verifier's field l

Disposition: fixed.

Evidence: Commit 91c394170dd94d832bddeb0824c32843703926f9 contains the corrected complete-function-inventory.json.gz. Read-only verification confirmed that all 56 snapshot rows and all 5 provisional candidate rows contain nonempty ast_sha256 and raw_metric_rows. The retained archive is byte-identical to the committed file. In /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/91c394170dd94d832bddeb0824c32843703926f9/memory-bank/evidence/exposed-complexity-2026-09-05/complete-function-inventory.json.gz, decompressed lines 1931–1932, 1964–1965, 1998–1999, 2040–2041, and 2072–2073 contain the corrected fields for every provisional row. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/evidence/exposed-complexity-2026-09-05/SUMMARY.md lines 4–6 document the archive location and producer lookup.

Source: memory-bank/pending/complexity-recovery-papercuts-2026-09-05.md line 8 at main eb9fcb90

- 2026-09-07: Parent evidence verifier checked all 56 snapshot rows, then raised `KeyError: 'ast_sha256'` because the 5 provisional rows lacked that field. Added the same AST identity and retained raw metric rows to provisional evidence; original compressed measurements remain unchanged.

## After an interruption, the driver treated a previously returned tool process handle as still resumable instead of first checking persisted results. A 

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/complexity-recovery-papercuts-2026-09-05.md line 9 at main eb9fcb90

- 2026-09-07: After the interrupted run, root attempted to resume stale process 2951 and received `Unknown process id`; reconcile persisted outputs before assuming a process remains resumable.

## Consumer inspection guessed repository filenames instead of discovering existing paths before reading.

Disposition: fixed.

Evidence: Commit ff0e4be8d063c683130843affcf5b77ef28700cb added the existing repository path resolver. Verified /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:42-71 implements bounded filename discovery, :113 exposes --names, and :121-125 rejects missing paths with an explicit discovery hint. Commit db14782b6 documents this remedy in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-08-11.md:54-62. A read-only invocation of the resolver confirmed it locates tests/test_crafting_data.py, logic_pure/logic_pure_production.py, and tests/test_logic.py, the replacement paths recorded in the entry. The entry itself states that discovery now precedes reads; no new resolver is needed.

Source: memory-bank/pending/cut-gem-tradeability-implementation-papercuts-2026-09-05.md line 3 at main eb9fcb90

- 2026-09-05T21:03:36.723525+00:00: Initial consumer inspection guessed nonexistent `tests/test_crafting.py`, `logic/crafting_logic.py`, and `tests/test_logic_pure.py`; `rg --files` and symbol searches located `tests/test_crafting_data.py`, `logic_pure/logic_pure_production.py`, and `tests/test_logic.py`. File discovery now precedes reads.

## Unbounded text searches over decoder-evidence JSON print full classpath arguments and exhaust the tool-output budget.

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/cut-gem-tradeability-implementation-papercuts-2026-09-05.md line 5 at main eb9fcb90

- 2026-09-05T21:32:25.354550+00:00 — Decoder evidence inspection emitted an oversized full classpath from JSON and truncated the tool output (17,767 tokens in the rg result). Read only selected JSON keys and bound string lengths for subsequent evidence inspection.

## The shared SSH wrapper retried remote command failures as though every nonzero exit were a transport failure.

Disposition: fixed.

Evidence: Commit ef6f38018119a21e9c81065c84d7017ee0da5c03 fixed the retry policy. Verified the current tree: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:202-205 raises SSHCommandError immediately unless the operation is explicitly repeat-safe and the exit code is 255. The reported exit 1 therefore cannot be replayed. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_remote_test_host.py:177-190 covers immediate failure without another execution or sleep; lines 193-210 cover bounded transport retries. The unavailable aqt environment was expected according to the entry. The accompanying guessed catalog key was a one-time verification mistake, not evidence of a broken catalog or another persistent tool defect.

Source: memory-bank/pending/cut-gem-tradeability-implementation-papercuts-2026-09-05.md line 7 at main eb9fcb90

- 2026-09-05T21:35:52.354028+00:00 — Driver report, 2026-09-05: full baseline plain root snapshot exited 1 with `module_surface: cannot import '__init__.py': No module named 'aqt'`, an expected unavailable environment per existing tests; shared `_ssh` retried that non-transport failure three times. Later read-only catalog verification used guessed key `cut_redtopaz` and raised `KeyError: 'cut_redtopaz'`; parent is resolving the actual key from the normalized row.

## New cut-gem regression coverage grew shared test modules past the slop-gate line limit. Separately, retaining raw Qt stderr as text exposed a trailing

Disposition: fixed.

Evidence: Commit 83bcb01b9e8eaef50eaf7c4660307bb0c9e3d07f landed the repaired coverage in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/item_tradeability/test_cut_gem_tradeability.py:18,61,132. Current symbol searches find the three gem methods only there, not in the three oversized fixture modules; the commit's numstat confirms those fixture modules were not changed. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/cut-gem-tradeability-implementation-2026-09-05.md:231-249 documents the baseline restoration and cohesive test placement. Lines 227-229 document lossless deterministic gzip storage of the warning; decompressing focused.stderr.gz directly from that commit confirms the original trailing space survives without being tracked as whitespace-bearing text. Commit 4147d0ae9f88da6ee010cbb51bacbd76efd7e3c3 subsequently archived the raw evidence outside the checkout, with the current recovery contract at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/cut-gem-tradeability-implementation-2026-09-05/SUMMARY.md:3-8. The specific rejected changes and text-evidence cause no longer exist in the tree; the line-limit gate remains intentionally enforced.

Source: memory-bank/pending/cut-gem-tradeability-implementation-papercuts-2026-09-05.md line 9 at main eb9fcb90

- 2026-09-05T21:47:21.703750+00:00 — Preparing the attributable commit: `git diff --cached --check` found one trailing space in the exact retained Qt warning at `memory-bank/source-audits/cut-gem-tradeability-implementation-2026-09-05/mbp/focused.stderr:4`. The prior tracked-only check did not include this new evidence file. Normal commit then exited 1 with `slop-gate: code files above 1000 lines were grown:` and `tests/test_grand_exchange_logic.py: 1039 lines (was 996)`, `tests/test_integration_smoke.py: 9526 lines (was 9460)`, `tests/test_main_menu_widget.py: 20000 lines (was 19987)`, followed by `Split along module seams (a cohesive unit per file), not at an arbitrary line count.` No commit was created or amended.

## The cut-gem regression module was initially placed directly in the already-capped tests directory, so repairing file-length violations exposed the dir

Disposition: fixed.

Evidence: The recorded placement violation was repaired, not bypassed. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/pending/cut-gem-tradeability-implementation-papercuts-2026-09-05.md:13 records moving the module into tests/item_tradeability/. I read the current module at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/item_tradeability/test_cut_gem_tradeability.py:17-18 and verified that the package marker is tracked and the root-level tests/test_cut_gem_tradeability.py is not tracked. Commit 83bcb01b9e8eaef50eaf7c4660307bb0c9e3d07f adds the package marker and gem module, explicitly incorporates original repair commit 797bbf45, and is an ancestor of current HEAD. The global directory-width gate remains intentional; this entry's offending placement no longer exists.

Source: memory-bank/pending/cut-gem-tradeability-implementation-papercuts-2026-09-05.md line 11 at main eb9fcb90

- 2026-09-05T22:22:10.455109+00:00 — The next normal commit attempt, after the reviewed cohesive test repair and MacBook verification, exited 1 with `slop-gate: code files were added to directories already at 40 files:`, `tests: 238 code files (was 237)`, and `Create a cohesive subdirectory instead of widening this directory.` The earlier file-length gate had hidden this later directory-width boundary. HEAD remained `6438d42256236992b10d921d4cca920293b55d93`; no commit was created or amended, and no gate was bypassed.

## This entry is a repair-progress note documenting the gem test's relocation, not a separate failure or recurring source of friction.

Disposition: record_only.

Evidence: The entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/pending/cut-gem-tradeability-implementation-papercuts-2026-09-05.md:13 records the solution to the preceding directory-width rejection. Its only unfinished item was package discovery. Commit 83bcb01b9e8eaef50eaf7c4660307bb0c9e3d07f committed the package marker and gem regression module, which remain in the current tree. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/cut-gem-tradeability-implementation-2026-09-05.md:316-334 records subsequent successful package execution and discovery verification. The historical comparison.json inspected through git show confirms discovery of the gem methods without removing existing IDs. There is no additional cause to fix in this progress entry.

Source: memory-bank/pending/cut-gem-tradeability-implementation-papercuts-2026-09-05.md line 13 at main eb9fcb90

- 2026-09-05T22:23:26.001884+00:00 — The directory-width repair moves the byte-identical 158-line gem test into `tests/item_tradeability/` with an empty package marker. This is the shared item-tradeability domain boundary for gem and cape regression coverage; it avoids widening the capped `tests` directory or routing trading behavior into an unrelated skills bucket. No path-dependent `__file__`, `ROOT`, or `Path` reference exists in the moved module. Package discovery remains pending.

## An optional, unverified pathname glob was passed to zsh; an unmatched glob aborts the command before the search tool runs.

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 — 2026-09-26T21:26:06Z. The pending entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md:3 records `no matches found: data/gem*`. The earliest matching entry currently open in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 records the same optional-glob failure and discovery remedy. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-09-28.md:207-209 already groups guessed paths and unmatched optional globs under that survivor. Read /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:109-125 and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/techContext.md:42-49: safe filename discovery exists, but callers can still bypass it; this is not evidence that the cause is fixed.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 3 at main eb9fcb90

- 2026-09-05T20:30:57.212984+00:00: Initial optional path `data/gem*` failed under zsh with `no matches found: data/gem*`; use `rg --files` before optional path selection.

## Unbounded text searches print entire generated single-line dictionaries; limiting matching line counts does not limit their size.

Disposition: fixed.

Evidence: Verified existing protection from commit ff0e4be8d063c683130843affcf5b77ef28700cb. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:14-23 excludes giant catalogs by default, :83-88 passes --max-columns, and :115-116 sets bounded result and column defaults. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/techContext.md:42-49 directs agents to use this helper for content searches. A read-only verification searched 'Jade|Red topaz' in data/shop_data.py with --include-large --max-results 5 --max-columns 300; output contained only '[Omitted long matching line]' notices, not the generated mappings. Raw grep can still bypass the protection, but a documented, working repository tool already prevents this output flood.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 4 at main eb9fcb90

- 2026-09-05T20:30:57.213180+00:00: A name search through generated one-line maps produced truncated output of 613024 tokens. Exact-key AST reads now inspect the two selected storage keys and avoid dumping unrelated item mappings.

## Historical MediaWiki revision queries combine multiple titles with rvstart, which only supports a single page; the repository helper neither rejects c

Disposition: fixed.

Evidence: goal/papercuts-staged e48189ad, c74cd43c: tools/wiki_parity.py rejects piped titles before any request and raises on a MediaWiki API error.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 5 at main eb9fcb90

- 2026-09-05T20:31:51.660379+00:00: A combined historical MediaWiki query for Jade and Red topaz returned HTTP success with API `invalidparammix`: revision-bound parameters may only be used on a single page. Preserved the exact error response and changed to one title per request.

## The agent guessed source filenames before discovering existing repository paths; neither guessed filename exists, and the always-loaded project instru

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 6 at main eb9fcb90

- 2026-09-05T20:36:44.627740+00:00: Two guessed source paths failed with `rg: tools/scrape_grand_exchange_period.py: IO error for operation on tools/scrape_grand_exchange_period.py: No such file or directory (os error 2)` and `rg: logic/grand_exchange.py: IO error for operation on logic/grand_exchange.py: No such file or directory (os error 2)`. `rg --files` identified `tools/generate_ge_period_data.py` and `logic/grand_exchange_logic.py`.

## The agent guessed the documentation-audit script path instead of using the repository's documented command.

Disposition: fixed.

Evidence: Verified the current tree: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/README.md:93-99 documents `/opt/homebrew/bin/python3 tools/audit_docs.py`; the command at line 96 was introduced by commit e5672371a0b3de9995c7fcd429eaaacf5c10af2e, before this incident. Read /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/audit_docs.py:1-14 and confirmed the actual audit implementation exists at the documented path. The entry itself records successful discovery of that command. No matching open entry was found in memory-bank/papercuts.md.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 7 at main eb9fcb90

- 2026-09-05T20:38:39.230365+00:00: Documentation audit was first invoked with the nonexistent path `tools/docs/audit_doc_refs.py` and failed with `[Errno 2] No such file or directory`; the repository command is `python3 tools/audit_docs.py`, resolved with `rg --files tools`.

## Line-count-bounded source reads are not size-bounded: a generated dictionary can occupy one enormous line, so a short line range can overflow the tool

Disposition: fixed.

Evidence: goal/papercuts-staged d80f92f1, 2eae3388: tools/repo_search.py --line-range caps line width and count.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 8 at main eb9fcb90

- 2026-09-05T20:47:49.725203+00:00: A small source-line range crossed generated one-line maps and produced truncated output of 633924 tokens. Remaining source-key inspection uses AST node selection and bounded excerpts; no generated map is printed in full.

## The agent attempted to read a guessed helper path before discovering the actual filename and location; pkg_alias.py is at the repository root, not und

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 — 2026-09-26T21:26:06Z. Verified the root helper at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/pkg_alias.py:1-18; tools/pkg_alias.py does not exist. The earliest open entry for reading guessed paths before discovery is papercuts.md:59, which records nonexistent paths resolved with rg --files. The existing archive at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-09-28.md:207-214 groups this same cause under that survivor and specifically includes an incorrect tests/pkg_alias.py lookup. This staged September 5 entry predates the open survivor but was never added to the open log; it should be consolidated with that existing cause rather than trigger a separate helper relocation or import fix.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 9 at main eb9fcb90

- 2026-09-05T20:52:07.643298+00:00: The alias helper was initially read as `tools/pkg_alias.py`, which does not exist; `rg --files` located the root `pkg_alias.py`. The source binding uses the actual root file and matching Git blob.

## Raw HTTP-header evidence was staged as text, exposing its intentional CRLF, trailing spaces, and terminal blank lines to Git normalization and whitesp

Disposition: fixed.

Evidence: Verified commit 83bcb01b9e8eaef50eaf7c4660307bb0c9e3d07f stores all five affected headers as .headers.gz; its cut-gem manifest binds stored and decompressed hashes and lengths at lines 88–92, 105–109, 132–136, 149–153, and 166–170. The current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/cut-gem-tradeability-source-2026-09-05.md:190–194 documents byte-preserving deterministic gzip. The same commit adds /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/cape-tradeability-2026-09-05/fetch_sources.py:17–27 and :63–64, which gzip header bytes before retention. Commit 4147d0ae9f88da6ee010cbb51bacbd76efd7e3c3 later removes the cut-gem payloads from the checkout; its current SUMMARY.md:3–7 records the external recovery locations and digest manifest. The problematic plaintext payloads are no longer in the tree.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 10 at main eb9fcb90

- 2026-09-05T20:55:08.622905+00:00: Staging five raw `.headers` files reported `CRLF will be replaced by LF the next time Git touches it`; staged whitespace checks reported `trailing whitespace.` on literal `HTTP/2 200 ` and `new blank line at EOF.`. Staging was reversed before any commit. All five exact original payloads were preserved with deterministic gzip, and references plus manifest were updated; no Git configuration or attributes were changed.

## A clean new-file comparison can make `git diff --no-index --check` exit 1 without diagnostics; treating every nonzero status as a whitespace failure p

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 11 at main eb9fcb90

- 2026-09-05T20:55:38.496818+00:00: `git diff --no-index --check /dev/null <new file>` returned exit 1 with no diagnostics for a clean new-file difference. The untracked-file whitespace check accepts 0 or 1 only when stdout and stderr are empty; it does not treat the normal diff exit as a whitespace failure.

## The retained provenance checker used insufficient top-level blank lines and inline compound statements, so the normal commit hook correctly rejected n

Disposition: fixed.

Evidence: Commit 83bcb01b9e8eaef50eaf7c4660307bb0c9e3d07f contains the formatted checker. Current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/cut-gem-tradeability-2026-09-05/cache-input-binding-check.py has the required blank lines at lines 6–7, 10–11, and 15–16, and separate loop/conditional statements at lines 29–39. A fresh read-only pycodestyle check selecting E301,E302,E303,E305,E306,E701,E702,E703 returned exit status 0 with no violations. The hook rejection was valid; the offending formatting no longer exists.

Source: memory-bank/pending/cut-gem-tradeability-papercuts-2026-09-05.md line 12 at main eb9fcb90

- 2026-09-05T20:57:53.262865+00:00: The normal commit hook rejected retained `memory-bank/source-audits/cut-gem-tradeability-2026-09-05/cache-input-binding-check.py`: `slop-gate: PEP 8 layout violations were introduced:` with `E302 x1 (was 0)`, `E305 x1 (was 0)`, `E701 x3 (was 0)`, and `E702 x8 (was 0)`. No commit was created. The checker was formatted with identical AST, and its manifest hash was updated; no hook was bypassed.

## Combining entire core Memory Bank documents in one dispatcher-contract read exceeded the tool output budget; contract discovery needs heading searches

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 1 at main eb9fcb90

- 2026-09-05: Initial dispatcher-contract read combined large core Memory Bank files and truncated at 271708 tokens; subsequent reads use exact ruling sections and bounded source ranges.

## An unquoted optional path glob was expanded by zsh before the search command ran; no path matched tests/split*, so zsh aborted.

Disposition: fixed.

Evidence: The tree already provides a glob-free discovery tool and operator guidance. Commit ff0e4be8d063c683130843affcf5b77ef28700cb introduced /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:42-52, which lists files through rg --files and filters names in Python without shell expansion. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/techContext.md:42-49 directs agents to use this tool or discover exact paths with rg --files first. Commit db14782b6680bbb4cccaa80a710c0d7aeb638f8d documents this same cause and remedy in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts-fixed-2026-08-11.md:44-52. A read-only invocation of repo_search.py with pattern 'split', the existing tests directory, and --names succeeded. The recorded command bypassed the existing guardrail; this verdict does not claim that arbitrary unquoted zsh globs are now safe.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 2 at main eb9fcb90

- 2026-09-05: Dispatcher source search used unquoted `tests/split*` under zsh and failed with `zsh:4: no matches found: tests/split*`; use `rg --files` before path filters.

## The Firemaking reviewer test expected a successful burn while leaving the action's random roll uncontrolled, making its inventory assertion nondetermi

Disposition: fixed.

Evidence: Commit 307002127772a6031fae3815a1c17716086fb72d contains the fix, which remains in the current tree. In /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/runtime_actions/test_dispatcher_state.py:75-84, the test saves the RNG state and installs successful_roll(), which advances the original RNG and returns 0.0. Line 95 asserts the expected inventory; line 107 verifies that the RNG changed before undo; lines 115-118 perform undo and verify restoration of the original RNG state. Verified by reading the current file and inspecting git blame and the committed file; no tests were executed during this read-only triage.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 3 at main eb9fcb90

- 2026-09-05: First MBP dispatcher-state focused run executed 4 tests in 1.537s and failed the new Firemaking case with `AssertionError: {'Logs': 2} != {'Logs': 1, 'Ashes': 1}`; its action roll was uncontrolled. Supply a deterministic successful roll while advancing the real RNG, and assert the RNG changed before testing undo.

## The remote mirror excluded .venv-qt without recreating the repo-local interpreter link required by the root-surface tests, so the Qt guard skipped and

Disposition: fixed.

Evidence: Commit 716bb369a3dde829ea63a16e142af76bd1d889f3, verified as an ancestor of HEAD, repaired both causes. Current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:356-371 recreates the remote-local .venv-qt link after rsync; lines 395-397 require an executable Qt interpreter before either lane. Current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/__init__.py:333 retains the restored BIG_CHINCHOMPA_UTILITY_ID and EVIL_TREE_UTILITY_ID exports. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_remote_test_host.py:676-723 contains the repeated-sync canary that verifies the interpreter link and executes it. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/remote-surface-guard-2026-09-05.md:9-16 records the historical digest discrepancy as exactly those missing exports, not a serializer or pin defect. Classification is based on current source and commit inspection; no tests were executed in this read-only triage.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 4 at main eb9fcb90

- 2026-09-05: MBP root-surface tests silently skipped under the full Qt environment because `repo/.venv-qt/bin/python` is absent: `Qt interpreter is not installed` and `root initializer requires aqt; use the offscreen Qt interpreter`. An unchanged canonical-basename baseline with the expected symlink executes the test and fails with measured `fa36126b7ddff3d7d7d6582f80a12000d811533689fe3330e4e3864bb8641732` versus pinned `2625d3d2bb6110c0faee0a33863cf1bf8e921fe0591460eed25d071bec85e26d`; driver owns instrument diagnosis.

## An optional test-family path was passed as an unquoted shell glob before discovering existing filenames. When no file matched, zsh aborted before the 

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:59 — 2026-09-26T21:26:06Z. The entry reports `zsh:1: no matches found: tests/test_toolbelt*.py`. The earliest open entry for optional-path discovery, memory-bank/papercuts.md:59 (2026-09-26T21:26:06Z), records the same failure and recommends `rg --files`. Existing triage in memory-bank/papercuts-fixed-2026-09-28.md:207-209 explicitly keeps that entry as the survivor; lines 220 and 227 archive equivalent optional test-family glob failures as duplicates. tools/repo_search.py:42-71 already provides filename discovery without shell expansion, and memory-bank/techContext.md:42-49 documents it, but later open repetitions at papercuts.md:93 and :117 show that merely having this optional helper has not removed the cause.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 6 at main eb9fcb90

- 2026-09-05T18:31:41.591254+00:00: Coverage-fixture search used zsh glob tests/test_toolbelt*.py and failed with `zsh:1: no matches found: tests/test_toolbelt*.py`; use rg file filters for optional test families.

## File discovery guessed module paths instead of locating current files after package splits.

Disposition: fixed.

Evidence: Existing discovery guardrails cover this cause; the obsolete paths were not restored. Commit ff0e4be8d063c683130843affcf5b77ef28700cb added /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:42-71 (--names discovery) and :121-125 (missing-path diagnostic directing callers to search an existing parent). /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/techContext.md:42-49 documents moved-file discovery and listing exact paths before content searches; lines 48-49 were added by f63538435. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_papercut_tools.py:226-241 covers moved-file discovery. A read-only invocation of the existing helper successfully located logic_pure/logic_pure_construction.py, logic/flash_powder_factory_logic.py, and logic/inventory_pure.py in the current tree.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 7 at main eb9fcb90

- 2026-09-05T18:44:47.348991+00:00: Coverage-fixture searches guessed stale monolithic paths `logic/construction_logic.py`, `logic/rogues_den_logic.py`, and `logic_pure/inventory_pure.py` and received missing-file errors. Definitions now live in `logic_pure/logic_pure_construction.py`, `logic/flash_powder_factory_logic.py`, and the inventory package; use repository-wide definition searches before selecting files.

## The headless dispatcher-state fixture assumed ITEM_DEFINITIONS was exported by the add-on module and allowed the real level-up path to reach an unavai

Disposition: fixed.

Evidence: Commit 30700212 (Give dispatcher state one explicit owner before relocation) contains both corrections, verified by reading the current fixture and git blame. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/runtime_actions/test_dispatcher_state.py:15 imports ITEM_DEFINITIONS directly from ankiscape.core.constants; lines 33–35 replace only core.logic.show_level_up_dialog with a capture callback. The current test uses the directly imported constant at lines 358, 579, 613, and 641 rather than accessing self.addon.ITEM_DEFINITIONS. These changes remove both causes recorded in the entry.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 8 at main eb9fcb90

- 2026-09-05T18:49:03.474957+00:00: First expanded state suite on MBP ran 11 tests in 3.385s with 4 errors: three `AttributeError: module 'ankiscape_dispatcher_state_test' has no attribute 'ITEM_DEFINITIONS'` from the new fixture and one `NameError: name 'QDialog' is not defined` from the real level-up code reaching the intentionally absent Qt UI. The fixture now imports ITEM_DEFINITIONS from constants and captures only the terminal level-up dialog while retaining both XP and level-up dispatchers.

## The expanded dispatcher-state fixture used an invalid Fish Flingers command and checked inventory instead of Temple Trekking state; failed subcases al

Disposition: fixed.

Evidence: Verified the current tree and git blame. Commit 307002127772a6031fae3815a1c17716086fb72d contains all corrections in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/runtime_actions/test_dispatcher_state.py:357 (enter_fish_flingers), :362 and :380 (assert the temple_trekking state changes), and :374 (clear direct_action_undo_stack at each subcase entry). These match the current production behavior in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/fish_flingers_logic.py:565-566 and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/temple_trekking_logic.py:417-424. No test execution was needed to verify that the recorded fixture mistakes are absent.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 9 at main eb9fcb90

- 2026-09-05T18:50:43.183247+00:00: Expanded state suite second run: `Ran 11 tests in 3.625s`, `FAILED (failures=6)`. Two fixture mistakes caused the failures: Fish Flingers command is `enter_fish_flingers` (`Unknown Fish Flingers action.` for `enter`), and Temple Trekking pouch preparation changes `temple_trekking.pouch_charges` rather than an already-held inventory item. The latter failed before undo and left four cascading stack-length failures (`2 != 1`, `3 != 1`, `4 != 1`, `5 != 1`). Subcases now clear the fixture stack at entry so failures stay independent.

## Fixture filename discovery printed matches from the full source manifest, including staged product paths, instead of restricting the lookup to fixture

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 11 at main eb9fcb90

- 2026-09-05: Native fixture discovery searched the full source manifest for Python paths and truncated at 18445 tokens; filtering out staged product paths returned the fixture evidence filenames directly.

## A source read guessed a module path instead of locating the existing definition; utility handling is not implemented in logic/utility.py.

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 12 at main eb9fcb90

- 2026-09-05: Native utility discovery guessed `logic/utility.py` and received `No such file or directory (os error 2)`; use the existing root definition or repository-wide symbol lookup.

## An unquoted optional wildcard is expanded by zsh before the discovery command runs; with no matching path, zsh aborts with `no matches found: tools/RE

Disposition: duplicate.

Evidence: Same cause as /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md:64 — 2026-09-26T14:13:30-0700. The staged entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md:13 records the same pre-command unmatched-glob failure as the open entry at papercuts.md:64. Line 64 is the earliest timestamped matching entry currently in the open log; line 59's 2026-09-26T21:26:06Z is later. A quoted `rg --files` filter found no tools/README* files. Later open entries at lines 93, 95, 97 and 117 show that switching one lookup to rg did not eliminate the cause.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 13 at main eb9fcb90

- 2026-09-05: Static-check command lookup used optional `tools/README*` and zsh returned `no matches found: tools/README*`; file discovery now uses `rg --files tools` before filtering.

## The initial draft kept per-function report summarization inside main and added a test module to the capped tests root, triggering the existing complex

Disposition: fixed.

Evidence: Verified commit 307002127772a6031fae3815a1c17716086fb72d and the current tree. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/dispatcher/state_coverage.py:54-66 contains the extracted summarize_functions method, called by main at line 107. The committed regression module resides at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/runtime_actions/test_dispatcher_state_coverage.py:11, not the tests root. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/dispatcher-state-restructure-2026-09-05.md:229-232 explicitly records both hook-required adjustments and states that no hook was bypassed. The entry describes a draft rejection already corrected in the landed code, not a defective gate.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 14 at main eb9fcb90

- 2026-09-05: Normal draft commit rejected by slop-gate: `tools/dispatcher/state_coverage.py: main 21 (new)` exceeded cognitive complexity 15, and `tests: 238 code files (was 237)` exceeded the directory cap. Moved the utility test into the existing runtime_actions test package and extracted function-report summarization from main; no instrument or hook threshold changed.

## Report extraction left an extra blank line between class methods in tools/dispatcher/state_coverage.py, causing the E303 pre-commit rejection.

Disposition: fixed.

Evidence: Commit 307002127772a6031fae3815a1c17716086fb72d contains the corrected spacing in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/dispatcher/state_coverage.py:52-54: frame_name ends at line 52, exactly one blank line follows, and summarize_functions starts at line 54. The current file retains this spacing. A read-only AST/line-gap check found no excess blank-line gaps between adjacent class methods. The original entry at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md:15 also records removal of the extra blank line.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 15 at main eb9fcb90

- 2026-09-05: The next normal commit attempt rejected `tools/dispatcher/state_coverage.py: E303 x1 (was 0)` after report extraction added two blank lines between methods; removed the extra blank line.

## The module-surface CLI prints both the hashed payload header and an unhashed digest footer with the MODULE_SURFACE prefix, so a broad startswith('MODU

Disposition: wont_fix.

Evidence: tools/module_surface.py is retired under owner ruling 4.30.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 16 at main eb9fcb90

- 2026-09-05T20:15:41.944023+00:00: Driver root-payload verification initially failed its assertion because broad `startswith('MODULE_SURFACE')` filtering included the `MODULE_SURFACE_SHA256:` summary digest line. Use the exact `MODULE_SURFACE module=` header and `NAME ` rows; this was not a candidate payload mismatch and did not require rerunning the candidate.

## The documentation audit treated a valid dotted reference to a nested test module as a dangling test selector because its known-selector set included t

Disposition: fixed.

Evidence: Commit fc14c8f971e33b506c0319d71943850d0d8a9971 fixes this cause. Verified in the current tree: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/audit_docs.py:130-132 discovers nested test files and adds each dotted module name to the known selectors. The exact referenced file, /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/runtime_actions/test_dispatcher_state_coverage.py, still exists, so tests.runtime_actions.test_dispatcher_state_coverage is now recognized. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_docs_audit.py:40-65 provides regression coverage accepting an existing nested module while rejecting a missing module and a stale method. Verified by reading code and commit; did not run tests because the test helper creates files and initializes temporary git repositories.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 17 at main eb9fcb90

- 2026-09-05T20:15:41.944023+00:00: Final evidence documentation audit flagged `dangling_test_selector: tests.runtime_actions.test_dispatcher_state_coverage` for the executed module reference; wrote the actual test file path `tests/runtime_actions/test_dispatcher_state_coverage.py` instead.

## The ad hoc evidence verifier assumed all manifest artifacts were gzip instead of selecting verification from each artifact's declared hash fields. The

Disposition: wont_fix.

Evidence: One-off check of one historical packet whose artifact is missing; no current tool writes gzip_sha256 manifests.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 18 at main eb9fcb90

- 2026-09-05T20:16:03.957502+00:00: Driver evidence verification assumed every manifest artifact was gzip after plaintext artifacts had been added and raised `gzip.BadGzipFile: Not a gzipped file (b'..')`. Dispatch verification by each artifact's declared `gzip_sha256` versus `sha256` fields; this was not an evidence defect.

## The byte-exact Qt coverage log was staged as plaintext, so the trailing space in the emitted font warning triggered Git's whitespace check.

Disposition: fixed.

Evidence: Commit 3c401d0cf9349271f38aefca8582cb39afd2b645, verified as an ancestor of current HEAD, replaced final-coverage.txt with final-coverage.txt.gz and recorded compressed/plaintext hashes in manifest-final.json lines 4–8. Current documentation at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/dispatcher-state-restructure-2026-09-05.md lines 352–365 explains the byte-preserving fix. Read-only verification of the committed gzip confirms timestamp 0 and exact equality with the original log from 24b7597b165900c4b89ed10da9fdd4a854064db2: 1,786 decoded bytes, SHA-256 3e006e3838bd6daea48690a62ba135bf24eddfdb4812299d5cfeab03408ae926. Neither plaintext nor gzip remains in the current checkout; /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/evidence/dispatcher-state-2026-09-05/SUMMARY.md lines 3–8 records subsequent out-of-tree evidence retention. The offending plaintext representation is no longer present.

Source: memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md line 19 at main eb9fcb90

- 2026-09-05T20:19:00.063769+00:00: `git diff --cached --check` reported `memory-bank/source-audits/evidence/dispatcher-state-2026-09-05/final-coverage.txt:1: trailing whitespace.` in the raw Qt font warning. Normal commit hooks nevertheless passed and created `24b7597b165900c4b89ed10da9fdd4a854064db2`. A separate evidence-packaging commit stores the unchanged log bytes as deterministic gzip (level 9, timestamp 0), updates manifest formats, and preserves the original plaintext SHA-256 `3e006e3838bd6daea48690a62ba135bf24eddfdb4812299d5cfeab03408ae926`; no log stripping, hook bypass, or MBP rerun.

## The agent assumed git merge treats `-F -` as standard input, as git commit does; git merge instead tries to read a file literally named `-`.

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/goal-driver-promotion-papercuts-2026-09-05.md line 3 at main eb9fcb90

- 2026-09-05 22:33:15 UTC: While preparing the queue promotion merge, `git merge --no-ff 774cecb1173ceddd5c55124dad40f8e5fc6062d1 -F -` returned exit `129` with `error: could not read file '-'`. No merge occurred. The supported sequence `git merge --no-ff --no-commit` followed by `git commit -F -` with a heredoc succeeded without skipping hooks.

## Gem evidence was located by guessing a pooled worktree rather than using a worktree-independent evidence location; the read targeted cape pool 9 inste

Disposition: fixed.

Evidence: Commit 4147d0ae9f88da6ee010cbb51bacbd76efd7e3c3 archived this evidence in the shared Git common directory and added /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/cut-gem-tradeability-implementation-2026-09-05/SUMMARY.md:4-8 with the recovery path, producer lookup, and digest index. Both named artifacts are mapped to producer 83bcb01b9e8eaef50eaf7c4660307bb0c9e3d07f in the retained manifest (lines 4 and 34). Read-only verification confirmed both files exist beneath /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/83bcb01b9e8eaef50eaf7c4660307bb0c9e3d07f/memory-bank/source-audits/cut-gem-tradeability-implementation-2026-09-05/mbp/ and match the manifest: summary.json SHA-256 c681339c15b871c7a86f36962d113388458bba569c03f795c249e71845c55da7; code-hashes.json SHA-256 36e901e1b3053eb5a77c36493f2c12898a355ad4bcf7c1d2ee7ac9d6ab93d562. Retrieval no longer requires choosing the gem or cape pool.

Source: memory-bank/pending/goal-driver-promotion-papercuts-2026-09-05.md line 4 at main eb9fcb90

- 2026-09-05 22:33:15 UTC: While locating gem surface evidence, a read used cape pool 9 instead of gem pool 14 and returned `No such file or directory (os error 2)` for `memory-bank/source-audits/cut-gem-tradeability-implementation-2026-09-05/mbp/summary.json` and `memory-bank/source-audits/cut-gem-tradeability-implementation-2026-09-05/mbp/code-hashes.json`; the retained cape owner snapshot supplied the exact MacBook baseline path.

## A cross-worktree read reused the source checkout as the root for a queue-owned file instead of resolving the queue worktree explicitly.

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/goal-driver-promotion-papercuts-2026-09-05.md line 5 at main eb9fcb90

- 2026-09-05 22:35:20 UTC: A combined source read looked for `memory-bank/goal-priority-matrix.md` in source pool 15 and returned `No such file or directory (os error 2)`; that file belongs to queue pool 1. Subsequent orchestration resolves named worktree roles explicitly before file reads instead of inheriting the last working directory.

## The driver guessed promotion filenames and used an unmatched shell glob instead of resolving existing repository paths.

Disposition: fixed.

Evidence: The current tree documents the promotion entrypoints in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/systemPatterns.md:826-827: tools/promotion_gate.py owns verification and landing, and tools/run_remote_tests.py owns remote lane commands. Those lines are attributed to commit 038157f68d65ff073637444f41747e657285934d. The existing safe discovery helper, introduced by ff0e4be8d, accepts directory roots and --names and gives a missing-path recovery hint at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/repo_search.py:111-125. I read the helper and both actual promotion files, then ran a read-only --names search over the tools directory; it exited successfully and located tools/run_remote_tests.py and tools/promotion/lane_execution.py without shell globs. The relevant repository documentation and discovery tool therefore already cover this friction.

Source: memory-bank/pending/goal-driver-promotion-papercuts-2026-09-05.md line 6 at main eb9fcb90

- 2026-09-05 22:59:51 UTC: While locating MacBook promotion checks, the driver guessed `tools/*mbp*` and received `no matches found: tools/*mbp*` from zsh; the guessed `tools/promotion/checks.py` and `tools/promotion/gate.py` paths also did not exist. `rg --files` resolved the actual files as `tools/run_remote_tests.py` and `tools/promotion/lane_execution.py`.

## Codex's connected-MacBook thread retrieval returned empty items for a completed turn whose execution and final result were persisted in the session tr

Disposition: wont_fix.

Evidence: External and generic: Owner: the Codex connected-thread connector maintainer, outside AnkiScape. Repair read_thread's retrieval of persisted completed-turn items and verify against the recorded task/turn identifiers. Add c

Source: memory-bank/pending/goal-native-verifier-papercuts-2026-09-05.md line 3 at main eb9fcb90

- 2026-09-05 12:20 PDT: `read_thread` reported zero items for completed MacBook task turn `01a07303-7c1c-74b3-ad12-480e404c84c5`. Direct read of `/Users/armantarkhanian/.codex/sessions/2026/09/05/rollout-2026-09-05T11-55-01-01a072ec-928c-73f0-99ea-d316edefd44b.jsonl` proved the prompt, command, final answer, and `task_complete` were persisted at lines 243, 250, 255–256, and 258. The task completed at `2026-09-05T19:20:22.865Z` in `19499` ms; this was a retrieval gap, not lost execution. Inspect the exact persisted result before retrying a supposedly empty task.

## Native launch preparation depended on evidence addressed by an old disposable /private/tmp session path, rather than a durable, retrievable launch-pro

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/goal-native-verifier-papercuts-2026-09-05.md line 4 at main eb9fcb90

- 2026-09-05 12:20 PDT: Native preparation found `/private/tmp/ankiscape-native-tab-final.utu7VD` but none of its five recorded evidence files (`execution_notes.txt`, `product_prelaunch_proof.txt`, `canary2_process_proof.txt`, `helper_source.py`, `product_seed_player_data_source.json`). Helper hash `e41f01225cefc5d2ab9c0dc9fc11a9df37f5f5a9218dc5975534c1544c2f8385` could not be verified. The old path is not a reusable launch proof.

## A single documentation fetch failed to resolve docs.ankiweb.net; the entry does not establish a persistent DNS fault or a repository defect.

Disposition: record_only.

Evidence: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/pending/goal-native-verifier-papercuts-2026-09-05.md:5 records the 2026-09-05 12:13 PDT error `curl: (6) Could not resolve host: docs.ankiweb.net` and says reading the installed Anki 26.5 parser established `-b/--base` and `-p/--profile`. The entry is also present in commit b4d769fb. Repository search found this host/error only in that historical entry, not in a fetch implementation; the current open papercut log has no matching DNS entry. This is an isolated failed lookup with a completed local-source investigation, not evidence of an ongoing fault to fix.

Source: memory-bank/pending/goal-native-verifier-papercuts-2026-09-05.md line 5 at main eb9fcb90

- 2026-09-05 12:13 PDT: The MacBook documentation request returned `curl: (6) Could not resolve host: docs.ankiweb.net`. Reading the installed Anki 26.5 parser established `-b/--base` and `-p/--profile` without a network retry or app launch.

## The merge command treated `-F -` as a literal filename; unlike `git commit -F -`, this form does not read the merge message from standard input. The s

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/goal-native-verifier-papercuts-2026-09-05.md line 6 at main eb9fcb90

- 2026-09-05T12:40:34-07:00: The driver reported that `git merge -F -` was rejected with `error: could not read file -`; `git merge -F /dev/stdin` with a HEREDOC worked. Use the successful explicit input path for this non-interactive merge-message flow.

## Asset verification has no explicit entry-point map in the testing guide, so the driver guessed a nonexistent tools/verify directory and zsh rejected i

Disposition: fixed.

Evidence: goal/papercuts-staged 8e3bd89a: README-tests.md names the asset check entry points.

Source: memory-bank/pending/goal-queue-maintenance-papercuts-2026-09-05.md line 3 at main eb9fcb90

- 2026-09-05: While checking asset coverage, the driver guessed `tools/verify/*.py` and received `zsh:1: no matches found: tools/verify/*.py`. The actual full-lane entry points are `run_tests.py` and unittest discovery under `tests`. Asset normalization and provenance checks are in the full suite; these slices contain no asset edits. Do not run a broad asset network audit for this check.

## The native actor's execution context rejected sandbox initialization before the canary probe ran: /usr/bin/sandbox-exec exited 71 with "sandbox-exec: 

Disposition: wont_fix.

Evidence: External and generic: Owner: the native actor execution-runtime maintainer and MacBook host administrator, outside this repository. Re-run a disposable sentinel-only canary in the original native actor tool context and com

Source: memory-bank/pending/goal-queue-maintenance-papercuts-2026-09-05.md line 4 at main eb9fcb90

- 2026-09-05: The driver reported that the native sandbox canary completed with `/usr/bin/sandbox-exec` exit `71` before the probe and exact stderr `sandbox-exec: sandbox_apply: Operation not permitted`. Evidence on the MacBook: `/private/tmp/ankiscape-sandbox-canary.NbIxze/canary-evidence.json`. Ordinary sentinel read/write passed; both recorded hashes were unchanged; no Anki launch or profile access occurred. Native workflows are integration-blocked by sandbox initialization failure in the native actor’s tool context, not pending approval. Read-only diagnosis is checking scope; this evidence does not establish OS-wide unavailability. Full headless promotion continues.

## Ad hoc non-interactive SSH process queries assume Homebrew ripgrep is on the remote shell's PATH; the recorded shell could not resolve bare `rg`.

Disposition: wont_fix.

Evidence: Generic git, shell, SSH, or harness behavior with no repository defect; owner rule: no prose rule for generic knowledge.

Source: memory-bank/pending/goal-queue-maintenance-papercuts-2026-09-05.md line 5 at main eb9fcb90

- 2026-09-05T12:58:38-07:00: The driver’s non-interactive SSH command `ps -eo pid,etime,args | rg 'unittest|run_tests.py'` returned exit `127` with `zsh:1: command not found: rg`. The remote PATH lacks `rg`; use `/opt/homebrew/bin/rg` only after verifying it exists, or use Python filtering.

## The authoritative goal priority matrix existed only in an unpromoted worktree, so the driver could not find it in the canonical checkout.

Disposition: fixed.

Evidence: Commit 2f27d206647b51398408110cadacd484b2555c89 added memory-bank/goal-priority-matrix.md and is an ancestor of the inspected HEAD (git merge-base --is-ancestor exited 0). The file now exists in the canonical checkout: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/goal-priority-matrix.md:3-9 defines authority and current queue reconciliation; lines 15-19 contain the current selection table. Commit 953d5197f refreshed the authority text at lines 5 and 7. Current startup guidance at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/activeContext.md:7 directs work to this canonical matrix. The original pool-only lookup problem is therefore resolved; neither an alternative implementation-priority-matrix.md nor a blocker file is needed to locate the queue.

Source: memory-bank/pending/goal-queue-maintenance-papercuts-2026-09-05.md line 6 at main eb9fcb90

- 2026-09-05T13:57:14-07:00: The driver looked for nonexistent canonical `memory-bank/implementation-priority-matrix.md` and `memory-bank/GOAL-BLOCKED.md`, then `memory-bank/goal-priority-matrix.md`. The authoritative current matrix is not yet promoted and exists at `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/1/ankiscape_fork/memory-bank/goal-priority-matrix.md`; use that exact path for the current queue.

## The agent guessed the documentation auditor's filename instead of using the repository's documented entry point.

Disposition: fixed.

Evidence: Verified the current tree rather than relying on the entry's correction. /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/README.md:93-99 explicitly documents `/opt/homebrew/bin/python3 tools/audit_docs.py`; git blame attributes the command at line 96 to e5672371a0b3de9995c7fcd429eaaacf5c10af2e. The September README rewrite, 1263beeb3c03a48418d4af9f9bac567aa21ed611, retains it under the Documentation audit heading. Read /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/audit_docs.py:1-2 and verified its CLI entry point at lines 267-284. The promotion gate also invokes the correct filename directly in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/promotion/lane_execution.py:386-394. An authoritative documented command and an automated invocation already exist; adding an alias for the guessed filename is unnecessary.

Source: memory-bank/pending/remote-surface-guard-papercuts-2026-09-05.md line 3 at main eb9fcb90

- 2026-09-05T18:34:53.700090+00:00: Static validation used the guessed script tools/audit_memory_bank_docs.py, which does not exist; the repository entry point is tools/audit_docs.py.

## An agent supplied an optional filename pattern as an unquoted zsh operand. With NOMATCH enabled, zsh rejected tools/pre_commit* before the search comm

Disposition: wont_fix.

Evidence: External and generic: Owner: Fleet agent-shell/harness maintainer. Add a command preflight that detects unquoted wildcard search operands before execution and directs the caller to filename discovery over an existing direc

Source: memory-bank/pending/remote-surface-guard-papercuts-2026-09-05.md line 4 at main eb9fcb90

- 2026-09-05T18:34:53.700266+00:00: An optional tools/pre_commit* search operand triggered `zsh:1: no matches found: tools/pre_commit*`; use rg --files filters for optional families.

## The SSH wrapper retried every nonzero exit, treating deterministic unittest failures as transport failures and replaying the test command.

Disposition: fixed.

Evidence: Commit ef6f38018119a21e9c81065c84d7017ee0da5c03 replaced unconditional SSH retries with repeat-safe, exit-255-only retries. Verified current /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/run_remote_tests.py:189-205: arbitrary commands default to repeat_safe=False, and non-255 failures raise immediately even when repeat_safe=True. Lines 487-495 capture the test exit in an atomic completion report; lines 513-517 launch once and reconcile a disconnected launch without replay; lines 535-551 return the recorded exit as data. Regression coverage exists in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tests/test_remote_test_host.py:177-210 for no replay on remote failures and :212-239 for preserving a failed test result after a disconnected single launch. Tests were inspected, not executed.

Source: memory-bank/pending/remote-surface-guard-papercuts-2026-09-05.md line 5 at main eb9fcb90

- 2026-09-05T18:37:28.996175+00:00: Calling `_ssh` directly for a failing focused unittest command reran the test command three times under the transport retry wrapper. Focused commands now capture the test result in a remote report and return it as data so transport retries do not mistake assertion failures for connection failures.

## The guarded lease command always emits JSON but its CLI help does not explain that output contract; supplying the familiar --json flag produces only a

Disposition: fixed.

Evidence: goal/papercuts-staged 37a59f50: worktree_guard.py lease --help says the last stdout line is JSON.

Source: memory-bank/pending/remote-surface-guard-papercuts-2026-09-05.md line 6 at main eb9fcb90

- 2026-09-05T19:01:11.412149+00:00: Driver worktree lease command supplied an extra `--json` flag and failed with `error: unrecognized arguments: --json`; the wrapper already emits JSON, and retrying without the flag succeeded.

## The MacBook native task-creation interface rejected the requested custom model override. Removing only the effort override still rejected gpt-6-astra,

Disposition: wont_fix.

Evidence: External and generic: Owner: the fleet maintainer and MacBook native task/remote desktop harness maintainer, not AnkiScape. Inspect the receiving task-creation interface's advertised model IDs and effort capabilities. Repa

Source: memory-bank/pending/remote-surface-guard-papercuts-2026-09-05.md line 7 at main eb9fcb90

- 2026-09-05T19:01:11.412149+00:00: Driver MBP native task creation with gpt-6-astra and low failed with `could not validate reasoning effort "low" for model "gpt-6-astra"`; model-only then failed with `could not validate model "gpt-6-astra"`. Creation without overrides succeeded; the configured remote model remains unverified.

## Adding separate imports for two activity constants grew the already-capped root module and its import fan-out, so slop-gate rejected the commit.

Disposition: fixed.

Evidence: Commit 716bb369a3dde829ea63a16e142af76bd1d889f3 (2026-09-05) repaired the rejected change by extending the existing runtime_actions import rather than introducing dependencies. Verified the commit diff and the current tree: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/__init__.py:333 imports BIG_CHINCHOMPA_UTILITY_ID and EVIL_TREE_UTILITY_ID alongside RuntimeActionContext on the existing line. Both constants remain available from /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions.py:362,365. The rejected import approach is absent; the gate itself is an intentional constraint, not a defect requiring removal.

Source: memory-bank/pending/remote-surface-guard-papercuts-2026-09-05.md line 8 at main eb9fcb90

- 2026-09-05T19:03:54.101497+00:00: Normal commit was rejected by slop-gate: `__init__.py: 6251 lines (was 6249)` and `fan-out 114 (was 112)`. The two public constants already exist in the imported runtime_actions module, so the repair now extends that existing import instead of adding two dependencies. Root size and fan-out remain unchanged. No commit was amended and no hook was bypassed.
