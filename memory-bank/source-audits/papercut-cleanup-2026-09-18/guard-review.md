# Worktree lifecycle independent verification

Measured at 2026-09-19T09:18:10-07:00.

## Verdict

No actionable safety regression found in the assigned worktree lifecycle repair. The reviewed source is unchanged by SHA-256 from the start of review. No checkout file was edited. Only this report and the requested `/tmp` canary/evidence files were retained.

Checkout: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/4/ankiscape_fork`.
Baseline commit used for differential proof: `ff44ddf641abdc7b7325c97351744972e9592b4d`.

## Source findings

- `tools/worktree_guard.py:165-173,189`: duplicate branch detection examines Git worktree branch records before Treehouse allocation. Both short branch names and `refs/heads/` forms are covered by the repository test. The independent baseline comparison detects the prior allocation behavior.
- `tools/worktree_guard.py:237-259`: marker inspection reads records without stale recovery. Fresh held markers, old unlocked markers, malformed JSON, malformed UTF-8, missing record fields, relative worktree paths, unreadable marker files, directory enumeration failure, and a dangling marker-directory symlink refuse before detach/return. Refused marker bytes remain unchanged. A genuinely absent directory permits normal return.
- `tools/promotion/locking.py:118,125-126` and `tools/worktree_guard.py:296-311`: release opts out of stale-lock recovery. The temp-lock canaries prove contended old and unreadable owners are neither rewritten nor signalled. Coordination remains held for lease validation, detach, and return, and releases after failure.
- `tools/worktree_guard.py:262-288,304-306`: dirty work and absent, wrong, empty, duplicated, inactive, malformed, or relative-path pool lease data stop before detach. The valid return still supplies `--force --if-lease-id lease-1` to the fake final Treehouse call.
- The retained root-owned `/tmp/ankiscape-papercut-pool-status-2026-09-18.json` was read without a fresh pool operation. Its 16 rows confirm the expected list shape and `path`, `status`, `lease_id` fields. All retained status values are `leased`. This is contract evidence from the retained root result, not a new live status claim.

## Executed checks

1. `python3 -B -m unittest tests/promotion/test_worktree_release.py tests.test_worktree_guard.WorktreeGuardTest -v`: 20 tests passed, zero failures/errors/skips, exit 0. Output retained in `/tmp/ankiscape-papercut-guard-tests-2026-09-19.log`. This selects the inert WorktreeGuardTest class; PreservedRefTest and native-session tests were intentionally excluded.
2. `16 baseline/current differential canaries`: all pass, with all actual `subprocess.run`, `os.kill`, and `locking.kill_process_tree` calls blocked inside each temp fixture. Current candidate refuses every negative case before fake allocation/detach/return, while baseline admits the repaired failure cases. Both versions refuse dirty work and permit the two positive cases. Marker bytes remain exact.
3. `lizard -C 15 -w tools/worktree_guard.py tools/promotion/locking.py tests/test_worktree_guard.py tests/promotion/test_worktree_release.py`: exit 0, no warnings.
4. `complexipy -mx 15 --snapshot-ignore --failed tools/worktree_guard.py tools/promotion/locking.py tests/test_worktree_guard.py tests/promotion/test_worktree_release.py`: exit 0, `No functions were found with complexity greater than 15.`
5. Baseline versions of the three existing files were copied into a temporary directory and analyzed using the same `lizard -C 15 -w` and `complexipy -mx 15 --snapshot-ignore --failed` settings. Both returned 0 with no violations. The new release-test file has no baseline.

No actual lease allocation/return, process kill, real promotion-marker write, product import/execution, remote call, browser/native action, Git/index mutation, config change, commit, push, hook bypass, sibling-task message, skill install, or goal resumption occurred.

## Differential cases

`duplicate_branch`, `fresh_marker`, `stale_marker`, `malformed_marker`, `unreadable_marker`, `contended_coordination`, `dirty`, `wrong_lease`, `empty_lease`, `missing_lease`, `missing_lease_id`, `duplicate_lease`, `relative_status_path`, `dangling_marker_directory`, `missing_marker_directory`, `valid_return`.

Runner: `/tmp/ankiscape-papercut-guard-canaries-2026-09-19.py`.
Evidence: `/tmp/ankiscape-papercut-guard-canaries-2026-09-19.json`.

Rerun with the exact command below. It performs one read-only `git show` of the frozen baseline and uses temporary paths/fake adapters for all canaries.

```sh
env -u QT_QPA_PLATFORM PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/ankiscape-papercut-guard-canaries-2026-09-19.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/4/ankiscape_fork'
```

## Simpler equivalent implementation

No material simplification found that preserves the contract. Reusing the existing shared coordination lock with one explicit recovery flag is smaller than a second locking mechanism. The three release precondition helpers expose distinct safety conditions and keep the mutation sequence short. The separate marker reader is necessary because `active_gate_records` performs stale recovery and deletes markers. Lease status preflight and Treehouse's final `--if-lease-id` check protect different boundaries and are not redundant.

This proves the guard's decision/order contract with inert adapters; root still owns any real promotion/integration run. Direct unmanaged Treehouse calls remain outside this guard's coordination protocol.

## Unchanged source hashes

| File | SHA-256 at initial read and report time |
| --- | --- |
| `tools/worktree_guard.py` | `1aa9f11dad40fd6eb5a2422a81b401fadb130a1438f9d0cb33a5b988567a8183` |
| `tools/promotion/locking.py` | `84f3dd29e0bc36bfa8ed3efefae4bd505dc61169041f8132d0d0d120bef25f13` |
| `tests/test_worktree_guard.py` | `50a9066a492acece73e3ca88974747bb79ab5449d675ed786368575d83d718d5` |
| `tests/promotion/test_worktree_release.py` | `728408b7f9553068cb570ec9e686da17ab40173de867e2daf8e98816495e6a0e` |

## Friction recorded in review

- 2026-09-19T09:18:10-07:00: An overly broad memory-bank read returned `Warning: truncated output (original token count: 273962)`; the aggregate tool result also reported `Warning: truncated output (original token count: 35572)`. All safety-relevant source and diff sections were subsequently read in bounded focused calls; no conclusion depends on the omitted text.
- 2026-09-19T09:18:10-07:00: Initial convention searches guessed absent paths: `pyproject.toml`, `.pre-commit-config.yaml`, `tools/audit_module_surface.py`, `tests/promotion/test_locking.py`, `tools/check_module_surface.py`, `tools/__init__.py`, and `AGENTS.md`; commands reported `No such file or directory`. Repository inventory plus root's explicit installed lizard/complexipy directions resolved the paths. No install or config edit followed.

Historical memory was consulted only for the canonical-checkout safety boundary (`MEMORY.md:57-57`, rollout `01a09e58-77ff-7b91-9b9d-c20d3c9af535`); all safety conclusions above use current source or executed inert evidence.

Root retained the original report in `guard-review.md.gz`. The command above uses the equivalent file-path selector because the documentation audit treats the nested module selector as a dangling test-method reference.
