# Shop package split: focused verification passed

Status: independent review and the fresh package capture passed. Full branch
gates, a normal author commit, and exact merged-tree verification remain pending.
No landing is claimed. Owner §§53.1/55 require the real-reviewer manual pass for
dispatcher/item 2/2c answer-path work; this behavior-preserving module split has
no blanket native hold.

The base is `814b4d591df4525e0bda4a1f858baf6345ed4d38` on
`goal/shop-domain-split-2026-09-05`, in pooled worktree 5. The product and test
files remain frozen at the 38 source bindings in this audit's manifest.

## Scope and ownership

The existing public facade stays at `logic/shop_logic.py`. Its implementation
parts form a package with an empty initializer.

| File | Role | Functions | Lines |
| --- | --- | ---: | ---: |
| `logic/shop_logic.py` | Public facade, views, transactions, and rollback | 14 | 611 |
| `logic/shop/__init__.py` | Empty package initializer | 0 | 0 |
| `logic/shop/state.py` | State, migration, access, stock, history, and counters | 39 | 613 |
| `logic/shop/services.py` | Services, vendor actions, potions, and flasks | 18 | 658 |

The facade imports `.shop.state` and `.shop.services`. The parts use `...` to
reach the same external packages. Services imports `.state`. Neither part has a
function-local import or a reverse facade import. All 71 original function
bodies and constant expressions remain exact. Each function keeps its real
implementation globals; public metadata assignments retain their original
module names. No wrapper, digest-pin change, UI change, or source-value change
is included.

The test changes name the package imports and actual service owner. The sole
new test remains the boundary regression; no existing test ID changes.

## Static and independent review evidence

The evidence directory is `shop-package-split-2026-09-05/`.
`package-delta-static-proof.json` verifies the path/import substitutions and empty
initializer against the reviewed flat snapshot. `static-author-proof.json`
verifies all original functions, constants, public metadata, global names,
proof-writer ownership, and exact reconstruction of the original source.
`module-ownership.json` records current paths and function locations.

The exact static script is retained as `static-proof-script.py.txt`.
`package-delta.diff.gz` contains the complete flat-to-package delta;
`product-and-tests.diff.gz` contains the complete product/test diff from the
original base. Both archives decode to their exact original bytes.

Independent Opus review `17784` exited `0` with `PASS` and no required fixes.
Its complete text is retained in `independent-opus-review.txt`. The parent also
verified all 71 function ASTs and read the full import/test-owner delta. The
optional note about the nonrecursive storage scan is outside this pure move:
neither moved part writes `activity_session`, so this change loses no such
coverage. No source change follows that note.

## Fresh package capture

Capture `73051` exited `0` with `PASS`. Its immutable report is:

```text
/Users/armantarkhanian/ankiscape-remote-test-host/reports/shop-package-split-oyfvtlm2
```

The read-only copy completed in session `47391` at
`/tmp/shop-package-split-oyfvtlm2`. Independent local validation and the parent's
separate verification both passed.

| Evidence | Plain | Offscreen Qt |
| --- | ---: | ---: |
| Exact focused tests | 24 passed, 0 skipped | 24 passed, 0 skipped |
| Surface tests | 5 run, 1 permitted skip | 5 run, 1 permitted skip |
| Ordered discovery | 5,567 to 5,568 | 5,567 to 5,568 |
| Complete baseline payloads | 11 byte-identical | 12 byte-identical |

The sole permitted skip is
`test_module_surface.ModuleSurfaceTest.test_root_initializer_is_reported_as_unavailable_without_aqt`,
with the exact reason `root initializer requires aqt; use the offscreen Qt interpreter`.
That test probes the inner plain interpreter in both outer lanes. The validator
checks its identity and reason, not the outer lane. All old discovery IDs remain
in order, with only the boundary regression added.

All 29 jobs finished with exit `0`. All 58 raw stream hashes and byte lengths
match their records. Every job preserves all 38 source bindings before and after
execution. All 23 complete payloads match the original baseline bytes, including
the body, digest footer, file hash, and byte length. Retained baseline inputs
also match at the start and end of the capture.

`remote-report/` preserves all 67 raw files. Large JSON records and raw streams
use gzip; every decoded file was compared with its original bytes.
`report-retention.json` maps each original file to its retained path and records
both hashes and byte lengths. The report contains 126,944,415 original bytes and
12,247,400 retained bytes.

`driver-terminal-receipt.json` retains the parent's driver result.
`independent-local-validation.json` retains the independent file manifest and
checks; `independent-validator.py.txt` retains its exact script.
`parent-verification.json` identifies the parent's separate review and checks.

The capture, driver, and bindings are retained exactly as executed in
`capture-script.py.txt`, `driver-script.py.txt`, and `capture-bindings.json`.
The driver uses the canonical lock, pending reconciliation, preflights, verified
upload, one sync, and one canonical launch. The parent's repeat local canary is
retained byte-for-byte in `driver-local-canary.json`: the wrong expected hash
stopped before runner import, lock acquisition, or any remote command, while all
38 source bindings stayed unchanged. Earlier reported canary provenance remains
separate from this retained raw repeat.

## Historical evidence and remaining gates

The 81 records in `shop-domain-split-2026-09-05/` remain byte-identical historical
flat-layout evidence. They include capture `9829`, review `97188`, and the normal
commit `22501` rejection: `logic: 89 code files (was 87)`. Those records do not
verify the package layout. The pre-capture package audit and prepared capture
plan remain preserved as historical records; capture `73051` supplies the current
runtime evidence.

Complete the full branch gates and normal audits after the author commit, then
run exact merged-tree verification before landing. Do not bypass the directory
cap or other hooks. The rejected flat-layout index requires final owned paths to
be staged after review; this retention pass did not stage or commit anything.

The retained-proof repair stays separate. This base keeps the proof-store mention
count at 24; that repair changes it to 25. Parent integration must retain both the
service-owner path and the repair's behavior/count change, then verify the
composed tree. Pool15 relocation remains frozen and was not changed here.
