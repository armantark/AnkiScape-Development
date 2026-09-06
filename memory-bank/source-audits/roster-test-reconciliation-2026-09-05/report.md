# Roster test split reconciliation

The split preserves the complete roster test contract. Shared checks, dragon families, Slayer families and finishers now have separate modules. The asset test uses a literal timestamp table and resolves the repository through `pkg_alias.__file__`. All other moved test methods retain their normalized ASTs.

## Scope and preservation

The source baseline is `814b4d591df4525e0bda4a1f858baf6345ed4d38` on branch `goal/roster-test-reconciliation-2026-09-05`. The parent preserved the incoming work in stash `1a34588b994e4fead010127412b1b84d57e4f27f` before reconciliation. The historical July audit and every unrelated measuring-test pin and assertion remain unchanged.

`static-preservation-proof.json` records the complete source test-ID map, source hashes and asset expectations. The independent Opus review accepted the split. Its unchanged response and the parent's dispositions are retained separately from the later runtime reports. The helper-coverage, quote-style, seam and direct-execution suggestions did not require changes to this contract.

The source mapping includes a leading `tests.` prefix. Runtime discovery omits that prefix. The capture applies this explicit mapping on both sides; it does not remove or duplicate tests. Owner sections 44, 47 and 48 in `../../handoffs/design-to-impl-rulings-2026-08-13.md` define the layout, move-aware comparison and domain boundaries.

## Measured runtime evidence

The parent ran each phase through the canonical serialized MacBook runner. The retained driver reports identify the exact commands, source hashes, interpreter lanes and remote report paths.

| Phase | Successful jobs | Result |
| --- | ---: | --- |
| Baseline | 4 | Plain and Qt discover 5,567 tests and execute all 36 original roster tests with no skips. |
| Measurement | 64 | Both lanes preserve mapped discovery and all roster tests; five split-module payloads and 25 asset canaries run in each lane. |
| Final pins | 16 | Both lanes preserve discovery, run all 36 roster tests, run the five measuring tests, and reproduce all measured split-module payload bytes. |

Each phase also has a separate source-hash canary report. The deliberate mismatch stops before any test subprocess launches. All three driver records report PASS.

The five measuring tests have one exact expected skip in each outer lane: `test_root_initializer_is_reported_as_unavailable_without_aqt` invokes an inner plain interpreter. No other test skip is accepted. The final source report binds 804 paths. The parent independently verified the complete named outcomes, discovery mapping, raw streams and full payloads before authorizing retention.

The asset canaries use disposable fixtures. The retained cases cover missing images, missing provenance, wrong titles, exact timestamps including both retained 2014 pins, the strict steel-dragon cutoff, and the nested repository anchor. They do not change the real assets or provenance file.

## Pin approval and review provenance

The parent approved only the replacement of the old roster digest entry with the five measured split-module entries. The before and after measuring files, approval JSON, capture scripts, bindings and operational manifest are retained with the reports. The final measuring-file SHA-256 is `058e6eed749ee8a9eb9052e9d3e6dd18fdac2a14e5595bcc18c93bfa1dfa5193`.

Opus session 19221 supplied the pre-capture independent review. The parent supplied the post-capture independent verification. These are separate reviewers and events; no second Opus review is claimed. `evidence/roster/operations/parent-verification-provenance.json.gz` records that attribution and the parent-reported execution identifiers.

## Remaining acceptance

Integration status: **blocked by the documentation gate**. The source split, runtime captures and pin adaptation are proven within their recorded scope.

The focused captures and pin adaptation pass. This report does not claim a full promotion gate, final complexity-hook acceptance, native UI acceptance or publication. Those remain with the parent. Source, roster and measuring bytes stayed frozen during evidence retention.

The documentation audit reports two `dangling_test_selector` errors in the unchanged historical file `../combat-enemy-roster-step1-data-report-2026-07-07.md`, lines 99 and 100. They reference the old roster module. The historical audit is preserved byte-for-byte as required; this report does not claim the documentation gate passes. The changed audit notes have no reported documentation issues.

No gate change is authorized. The proposed blanket exclusion of `text` fences was rejected because those fences can contain current runnable commands as well as historical output. Any narrower historical-evidence rule requires an explicit owner contract that preserves live command checks. The measuring instrument and historical output remain unchanged.

## Retained evidence

`evidence/roster/manifest.json` binds every retained report and supporting file to both its original bytes and deterministic gzip representation. Each decode was compared byte-for-byte with its source; gzip modification time is zero. The baseline, measurement and final phases each retain their source canary and complete positive report. The original author report is retained as a dated freeze record.

`evil-tree-diagnostic.md` closes the separate suspected availability defect without a product change. Its evidence has its own manifest under `evidence/evil-tree/`.
