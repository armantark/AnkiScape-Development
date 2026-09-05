# Prevent repeated remote test launches

Status: focused MacBook tests on the final source hashes passed, the isolated process canary passed, and independent review corrections are accepted. Full branch and post-merge promotion gates remain pending. The driver owns all MacBook operations and promotion. No local tests, real SSH commands, rsync, browser operations, commits, or changes outside this worktree were performed by the author for this implementation.

## Failure and boundary

At baseline `1932b3c07b5dd8bdb598889f2f503607ac92b791`, `tools/run_remote_tests.py` routed every SSH command through a helper that retried all nonzero return codes up to `NETWORK_ATTEMPTS = 3`. The detached launch included `rm -f` for the same log and report paths. A failed command could therefore execute repeatedly. An SSH disconnect after remote execution could repeat the detached launch and remove evidence. An unresolved worker could outlive the local mirror lock, then overlap a later sync.

SSH return code `255` does not prove that the remote command did not execute. The local OpenSSH manual states that SSH returns the remote command status or `255` for an error. The repair therefore defaults every SSH operation to one attempt, preserves its return code and both output streams in the error, and permits bounded retries only for explicitly repeat-safe reads and setup. The rsync command and its existing retry policy are unchanged.

## Prepared behavior

Before launch, the runner exclusively creates and fsyncs `~/Library/Caches/ankiscape-remote-test-host.pending.json` beside the existing mirror lock. It records the exact run ID, remote log path, and remote report path. There is one launch attempt and no report or log deletion. A launch return code of `255` enters read-only polling of that same run. Other launch failures, exhausted polling retries, interrupted local execution, and timeouts retain the record.

Under the same caller-held mirror lock, `_sync` first reads an existing pending run's report, before mkdir, rsync, or link setup. This covers both CLI invocations and direct helper calls. Missing, malformed, and out-of-range completion reports block sync. A valid exit status from `0` through `255` confirms completion and permits record removal, including when the previous test failed. The report and log remain remote; errors print the exact paths and a read-only inspection command. Rerunning the runner reconciles completion automatically before it can sync. A pending run with no report remains blocked; the implementation does not infer that a worker is dead or delete stale state. This updates the unresolved-worker behavior described in `memory-bank/remote-test-host.md`; coordination remains local to dispatchers sharing this machine's lock and pending file.

## Verification prepared for the driver

`tests/test_remote_test_host.py` adds subprocess-fake coverage for one-shot command failures, bounded repeat-safe SSH retries, one disconnected launch returning the real test failure and log, and persistent blocking across a second invocation and a direct `_sync` call after launch, polling, or timeout failure. These checks retain the real `_sync` and fake only subprocess and rsync transport; they assert that blocked calls cannot reach mkdir, rsync, link setup, or launch. It also checks that missing and invalid reports retain the guard and a valid failed-test report releases it. All tests isolate the pending file in temporary directories. The existing sync seam accepts the explicit repeat-safe argument.

Static verification: both modified Python files parse with `ast.parse`; no imports or test execution were used. The exact runner diff preserves `_run_with_retries`, `_rsync_command`, `_remote_lane_command`, all host paths, test-count floors, and the remote surface guard. Focused runtime evidence is retained below. Full branch and post-merge promotion checks remain pending.

Focused selector: `tests.test_remote_test_host.RemoteTestHostTests`. The driver ran the complete existing module, including its original rsync and interpreter-link canaries, on the MacBook within the approved isolated harness. The separate process canary proved that the pending guard blocks a second sync before a shared-mirror run.

## Papercut

- 2026-09-05 21:48:11 UTC: While assembling the retry test, static inspection found a mixed parenthesized `with` form; it was corrected before AST parsing. No runtime command or test was attempted.

## Independent review corrections

The parent accepted F1 and F2 from the Opus review at `/tmp/ankiscape-remote-single-launch-review-opus-2026-09-05.txt` (review process `48442`). F1 identified that outer `KeyError` and `TypeError` catches could hide programming errors. The outer handler now uses the baseline exception set. Reconciliation instead checks that the pending JSON is an object with nonempty string `run_id`, `log_path`, and `report_path` values; invalid records fail closed with the exact pending-file path. The existing guard test includes malformed JSON, wrong container shapes, missing fields, and invalid field values, and retains the real sync boundary.

F2 identified incomplete manual recovery guidance for a run that never produced a completion report. Errors now require the driver to reconcile the exact run and confirm there is no active worker or in-flight launch before manually clearing its pending record. Absence of a log or report alone is not proof that no worker exists. Automatic clearing remains limited to a valid completion report; no deletion or stale-run recovery control flow was added. F3 was optional and did not change implementation or tests.

The driver verified the corrected code with the focused module and process canary documented below. Full promotion verification remains the driver's responsibility.

## Retained MacBook evidence

The companion directory [remote-test-single-launch-2026-09-05](remote-test-single-launch-2026-09-05/manifest.json) retains the driver's copied raw logs, result records, canary source, and raw Opus review. The manifest records each original path, raw byte count, raw SHA256, and stored SHA256. Log, review, and historical canary-source files are deterministic gzip copies; decompression reproduces the source bytes without trimming. The raw Opus review describes the pre-correction state; the accepted F1/F2 resolutions above and final source hashes identify the verified state.

The driver executed the complete `tests/test_remote_test_host.py` module in an isolated copied harness outside the shared mirror. Plain Python ran 16 tests in 0.221s; Qt Python ran 16 tests in 0.472s. Both exited `0`, reported `OK`, and had no skips. The retained `results.json` binds these runs to runner SHA256 `5de9414af35bb4688810d7d3f9b3331b205988b74a30706de6eca07af2de5e42` and test SHA256 `e23e183f8a4d4eba3717e69023b11753491ebd5abf1cc32892469cc85c322463`.

The driver also executed the process canary retained as `process-canary.py.gz` on the MacBook with exit `0`. Its source SHA256 is `617e451340c4063090016bc09fb0e4fd096fad3a2b96b3370e4cc31ffda50bd4`. Run `plain-1788646300-b5c5fe9f` recorded exactly one worker start, blocked copying while pending, and released the same run after its completion report returned `0`. Two syncs completed, one before launch and one after completion. The worker had an eight-second alarm. All canary paths were temporary and the driver reports they were cleaned; the shared mirror was not used.

The canary injected exit `255` after an actual local detached shell launch. It did not make a network SSH connection and does not demonstrate a naturally occurring SSH disconnect. It verifies the one-shot recovery path with a real background process and real local shell and rsync operations. This evidence does not imply that any orphan worker was present on the shared mirror.

Only the focused module and isolated process canary are complete. Full branch and post-merge gates remain pending. Native UI testing is unnecessary for this pure CLI tool change.

- 2026-09-05: While locating the documentation checker, a guessed `tools/promotion_controller.py` and `.pre-commit-config.yaml` lookup returned `No such file or directory (os error 2)`. The actual checker was resolved from `tools/promotion/lane_execution.py` as `tools/audit_docs.py`.

Evidence-freeze checks: `python3 tools/audit_docs.py` passed for 655 Markdown and 445 HTML files; `git diff --check` passed. Python source parsing and retained-artifact hashes were checked without running tests.

## Commit-hook repair

- 2026-09-05 22:20:33 UTC: The authorized new commit was rejected by slop-gate with the exact output below. No commit was created; no hook was skipped and no amendment was attempted.

```text
slop-gate: cyclomatic complexity above 15 was introduced:
  memory-bank/pending/remote-test-single-launch-2026-09-05/process-canary.py: main 16 (new)
  -> Simplify the control flow (consolidate branches, use a table or early returns); do not split into trivial helpers to game the number.
slop-gate: cognitive complexity above 15 was introduced:
  memory-bank/pending/remote-test-single-launch-2026-09-05/process-canary.py: main 22 (new)
  tests/test_remote_test_host.py: RemoteTestHostTests::test_unresolved_run_blocks_next_sync_after_launch_poll_or_timeout_failure 17 (new)
  -> Flatten the nesting: invert conditions, return early, or lift the inner loop body to a named function that earns its name.
```

The parent authorized retaining the already-executed historical canary as deterministic gzip evidence, using the same raw-byte preservation rule as the logs and review. Its raw SHA256 remains `617e451340c4063090016bc09fb0e4fd096fad3a2b96b3370e4cc31ffda50bd4`; the manifest records the renamed artifact and stored hash. The canary source was not edited or represented as newly executed code.

The parent also authorized flattening only the deepest diagnostic assertion loop into four explicit assertions for the pending-file path, run ID, log path, and report path. All four checks remain. The new test SHA256 is `43926d19b0542ec04c03d1e7dcdf29520e5a47c2f7180f90ddd6b75e13febd8b`; runner SHA256 remains `5de9414af35bb4688810d7d3f9b3331b205988b74a30706de6eca07af2de5e42`. The retained focused logs still attest the prior `e23e183f8a4d4eba3717e69023b11753491ebd5abf1cc32892469cc85c322463` test bytes. The driver completed the focused module rerun on both MacBook interpreters before authorizing a new commit attempt, as retained below.

## Final focused qualification after hook repair

The [repair evidence manifest](remote-test-single-launch-2026-09-05/repair-43926d19/manifest.json) retains a separate copy of the MacBook rerun logs and result record, without replacing the earlier historical evidence. Driver session `25446` completed with exit `0`. Plain Python ran 16 tests in 0.201s; Qt Python ran 16 tests in 0.439s. Both reported `OK` with no skips.

The copied result record and current file bytes match runner SHA256 `5de9414af35bb4688810d7d3f9b3331b205988b74a30706de6eca07af2de5e42` and test SHA256 `43926d19b0542ec04c03d1e7dcdf29520e5a47c2f7180f90ddd6b75e13febd8b`. These are the final qualified runner and test hashes. The earlier process canary remains applicable to the unchanged runner bytes; it is explicitly an injected local-process fault, not a natural network SSH failure. Full branch and post-merge gates remain pending.

- 2026-09-05: The driver attempted canonical `rg --files tools/dispatcher`, which returned `rg: tools/dispatcher: IO error for operation on tools/dispatcher: No such file or directory (os error 2)`. The follow-up unquoted `tools/dispatcher/surface*` returned `zsh:1: no matches found: tools/dispatcher/surface*`. Existing surface helpers are elsewhere; no mutation or runtime occurred.
