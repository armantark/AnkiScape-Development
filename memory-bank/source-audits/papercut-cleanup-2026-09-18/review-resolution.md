# Review resolution

## First independent review

Opus reviewed the supplied maintenance diff without tools. The raw review is retained in `review-a.txt`. It did not cover the worktree guard or the inventory checker. Root handles those in a separate review.

- The remote report reader uses the exact report path recorded before launch. No caller selects the latest `plain-*.report`. Focused completion does not substitute for full-gate acceptance. A separate run-name scheme adds no safety to the actual consumer.
- `run_tests.py` imports the real `aqt.qt` when available. The Qt command uses the Qt interpreter and offscreen environment; it does not install plain stubs. Actual focused Qt verification remains required.
- The pending record protects an unfinished process, not a test result. Reconciliation reads that exact completion report before sync. It does not retry a lane or select a different scope. A new focused run cannot clear an unresolved full run.
- `RemoteTestHostTests.setUp` redirects the mirror lock and derived pending record into a temporary directory. Failure fixtures do not touch the real runner state.
- Promotion selectors affect displayed evidence only. `_run_check` passes the raw lines and actual return code to its validator. `plain_only` still selects the allowed check set.
- All module-surface pins remain unchanged. Runtime asset imports and both interpreter digests require MacBook proof before acceptance.
- Root added the existing E402 annotation to the Hunter import. All other `FetchOutcome` consumers either branch on `skipped_existing` or now print `existing`. Provenance writes still receive resolved `ImageInfo`, never skipped metadata.
- The suggestion to skip an existing directory was rejected. A directory is not a valid asset file. The fetcher now rejects that target before network access, with a non-mutation canary.
- The quality author received the confirmed relative-package and dotted-import defects, eager parsing concern and complexity finding. The final quality report records their resolution.

## Simplification decisions

- Removed a redundant conditional around the remote command builder.
- Passed the shared progress filter directly to each lane. Its optional limit still supports existing reachability summaries.
- Removed the extra test of `unittest.subTest` behavior; retained the two diagnostic scopes and all assertions.
- Removed redundant Hunter exclusions from the test. The complete shared-map disjointness assertion remains.
- Removed the unused fake trim backend from the invalid-target canary. The test requires backend selection never to occur.
- Split the inventory check into source coverage and whole-inventory validation. New functions stay below the fixed complexity limit.

The static audit's conservative handling of unknown ancestry remains a deliberate limit. Root does not accept a source claim merely because the author or reviewer asserts it.

## Guard and inventory review

Opus reviewed the guard, inventory checker and failure canaries through scoped read-only file access. The complete response is in `review-b.txt`.

- Accepted the qualified-branch finding. Normalize `refs/heads/` once at the lease entry point. The before fixture creates the wrong branch; the candidate selects the existing short branch name. Duplicate-branch refusal still occurs before pool allocation.
- Retained refusal when a marker disappears between enumeration and reading. A blind `FileNotFoundError` continuation would also hide uncertain entries. A harmless retry is preferable to detaching a checkout whose evidence ownership is uncertain.
- Kept the inventory counter checks. Their current positive counts make the suggested comparison change equivalent; it removes no caller step.

## Conditional ancestry review

The real target-level-order caller imports its harness inside `try`. A unique source binding must resolve through that container without executing product code. The scope-aware walk now returns actual binding nodes and stops at class and function bodies. The caller's redundant `unittest.TestCase` base is removed.

Opus found exception aliases and match captures stored as AST string fields. Root reproduced the false acceptance, accepted the finding and verified the narrow repair. Alternate imports, handler assignments, exception aliases and pattern captures fail closed. The complete review is in `quality-conditional-review.txt`; the author report and root rerun results are beside it.

The auditor remains a static approximation. It does not execute import conditions or interpret Python generally. Rare assignments inside definition expressions remain outside this repair. Full runtime discovery remains required and was not replaced by static evidence.

Root reran 37 inert tooling tests and the 16 affected MacBook Qt tests, all with zero skips. The final merged candidate still requires the exact full-gate receipt. No source-gate receipt was issued for `8898f8780213c265b693a28b992ee8fbc903e938`: its two lanes passed but its nested selector in the review notes failed the documentation audit. The original notes and gate log remain compressed without byte changes.
