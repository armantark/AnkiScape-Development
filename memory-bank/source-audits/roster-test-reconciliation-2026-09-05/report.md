# Roster test split reconciliation

The split preserves the complete roster test contract. Shared checks, dragon families, Slayer families and finishers now have separate modules. The asset test uses a literal timestamp table and resolves the repository through `pkg_alias.__file__`. All other moved test methods retain their normalized ASTs.

## Scope and preservation

The source baseline is `814b4d591df4525e0bda4a1f858baf6345ed4d38` on branch `goal/roster-test-reconciliation-2026-09-05`. The parent preserved the incoming work in stash `1a34588b994e4fead010127412b1b84d57e4f27f` before reconciliation. Every unrelated measuring-test pin and assertion remains unchanged. The complete historical July report is retained byte-for-byte; its readable copy now links the original unittest transcript as described below.

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

Integration status: **documentation representation corrected; documentation audit passed**. The source split, runtime captures and pin adaptation retain their recorded scope. This change does not establish full promotion-gate or native programme acceptance.

The earlier documentation audit reported two `dangling_test_selector` errors in the historical July report at lines 99 and 100. Its complete original bytes are now retained as [immutable evidence](SUMMARY.md), with the historical Git revision, blob, decoded hash and stored hash/length in [the binding](evidence/historical-july-report/SUMMARY.md). Only the fenced unittest transcript in the readable report is replaced by an evidence link; every other byte of its factual contents is preserved. The original command and output have not been rewritten.

The parent revised its earlier operational file freeze for this representation change. The earlier claim that this required a new owner decision was unsupported: no owner ruling prohibited relocating verbatim historical evidence. The unchanged checker continues to validate current source-audit selectors. No text-fence exemption, compatibility test, product edit or measuring-pin change is part of this correction. The earlier failing audit and all prior captured evidence remain unchanged. The unchanged documentation checker reports 662 Markdown files, 445 HTML files and zero issues; [the new receipt](evidence/historical-july-report/SUMMARY.md) retains that result. Full branch and exact merged-tree gates remain pending.

## Retained evidence

`evidence/roster/manifest.json` binds every retained report and supporting file to both its original bytes and deterministic gzip representation. Each decode was compared byte-for-byte with its source; gzip modification time is zero. The baseline, measurement and final phases each retain their source canary and complete positive report. The original author report is retained as a dated freeze record.

`evil-tree-diagnostic.md` closes the separate suspected availability defect without a product change. Its evidence has its own manifest under `evidence/evil-tree/`.
