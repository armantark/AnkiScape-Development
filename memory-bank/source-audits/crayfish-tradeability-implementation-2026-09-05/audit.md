# Cooked Crayfish tradeability implementation

Status: the bounded implementation and regressions are written. Parent-owned focused tests pass in plain and Qt lanes. The parent-produced semantic proof accounts for all 23 required payloads, and discovery adds only the new custody test. Independent measurement and repair review is accepted, and the five approved digest expectations and two map-count expectations are applied. The parent verified the exact instrument-only diff and authorized the normal author commit. Full-suite tests, native manual acceptance, and promotion remain pending.

## Behavior and scope

Ordinary cooked Crayfish `13433` is declared tradeable in `data/cooking_data.py`. The existing catalog can therefore admit it using the already-present cache exchangeability and value. The curated GE writer adds only Crayfish guide price `45`, four-hour buy limit `10000`, and complete price provenance for Exchange oldid `6570435`, timestamp `2012-11-18T03:19:45Z`, displayed price date `03:19, November 18, 2012 (UTC)`, item ID `13433`, and value `5`.

The accepted source packet is `../crayfish-tradeability-source-2026-09-05/audit.md`, committed as `57da350b85e419d6824dbbc1a01ed95d5bac5600`. The unmarked item oldid `5517594` supplies direct player-tradeability Yes. Dated cache queries corroborate identity and client flags. Neither decoder output nor the current cache-name table is used to invent a player-tradeability predicate.

The only cooking-module edit is the `False` to `True` flag for exact tuple `(13433, ...)`. Exact byte comparison after reversing that flag recovers the baseline module hash. Raw crayfish `13435`, Burnt crayfish `13437`, Crayfish cage `13431`, all other item flags, the level-1 recipe, 30 XP, raw/cooked/burnt outputs, cooking odds, healing, values, and stacking are unchanged. There is no UI implementation change or new feature.

## Generated-data custody

The existing `tools/generate_ge_period_data.py:write_generated` wrote the curated maps. Its module imports standard-library code and the existing `pkg_alias` namespace installer. The author inspected that installer before loading the writer with `runpy`; it does not execute the add-on initializer. The writer call imported no production submodule and called no network or harvest function.

`generated-map-delta.json` records the exact AST comparison: all prior map entries are preserved, the global source is unchanged, and only the Crayfish price, limit, and provenance keys are added. The parent separately checked every map entry and approved the resulting test counts after independent measurement review. `approved-instrument-edits.json` records the two map-count updates and five measured surface digest updates.

## Regressions and pending verification

The existing Cooking metadata test verifies the exact cooked item ID and true flag, with raw and burnt IDs/false flags retained. The existing live GE catalog test checks the real registered row, guide price `45`, value `5`, limit `10000`, complete price provenance, the unchanged raw-item catalog identity/price/limit, and continued exclusion of Burnt crayfish. The Cooking extra-item false flag for Raw crayfish does not control its final registry entry: Fishing registers that storage key first.

The single new custody regression is `tests/item_tradeability/test_crayfish_tradeability.py`. It uses the real cooking data and real GE catalog. One raw Crayfish produces one cooked item for 30 XP under a successful roll. The test then checks sell escrow, simulated fill, collectible coins, collection, buy escrow, simulated fill, collectible item, and final collection. The original ingredients are unchanged by the pure cooking call, and the final inventory contains the cooked item with the starting coin balance. Fixed draws select a stable market path; they are not changes to market behavior.

The existing `test_logic.py` remains byte-identical. Its cooking test supplies the established call pattern, while the new case belongs in the cohesive `item_tradeability` package. An empty package marker follows the existing `tests/runtime_actions/` convention and avoids growth in the oversized generic logic-test module.

The author performed only Python syntax/AST checks, the exact single-flag reversal check, generated-map comparisons, source-file hashes, and unchanged-source-packet checks. `static-change-proof.json` lists the focused unittest IDs and all changed Python hashes. The author ran no unittest, audit command, production import, native UI action, Java decoder, network request, or remote synchronization. The parent owns the runtime captures described below.

The corrected three focused tests pass in both plain and Qt environments, with no skips. Both discovery lists preserve all 5562 baseline IDs and add the new custody method once, for 5563 IDs. The parent executed the semantic proof over all 23 required payloads: 9 changed and 14 are byte-identical. Reversing only the ordinary Crayfish tradeability field in cooking-derived metadata and exported item definitions, and removing its new Qt root GE catalog row, restores every complete baseline body exactly. Shop extra-item metadata and carried/activities item definitions expose the same flag change. Opus accepted this measurement and the raw-item assertion repair, with the packet limits and parent resolution recorded in `opus-measurement-review-resolution.md`.

`tests/test_grand_exchange_data.py:test_generated_period_rows_are_registered_and_cutoff_safe` now asserts the measured map counts `1438` and `1754`. Exactly five digest constants in `tests/test_module_surface.py` match the verified payload bodies. Reversing those five constants and the two counts recovers each entire pre-edit test file byte for byte. All other assertions, skip behavior, digest expectations, and audit thresholds are unchanged. The final instrumented source is not described as passing its full suite.

## Parent-owned manual flow

1. Use a disposable profile and the parent's approved fixture setup. Record the starting raw Crayfish and Coins. Keep the new item's GE market state empty when checking the initial guide price.
2. Open Cooking and use the existing Cook raw crayfish target. Verify its level, inputs, and displayed XP are unchanged. Complete a successful cook and record the raw-item decrease, one cooked output, and 30 XP. A burn follows the existing behavior and is not evidence of a tradeability failure.
3. Open the GE and verify exactly one ordinary cooked Crayfish row, the initial guide price `45`, and limit `10000`. Verify Raw crayfish retains its existing row (item `13435`, initial guide `58`, limit `20000`) and Burnt crayfish remains absent. Inspect the visible name, quantities, and provenance-related display for clipping or ellipses.
4. Sell one cooked Crayfish. Confirm inventory removal into escrow, review-driven filling, coins remaining collectible until collection, and no duplicate item or coin grant. Buy one back and check coin escrow, filled item custody, and collection using the actual displayed execution prices. Market prices may move during reviews; the source guide price is not a promise that every execution remains at 45.
5. Complete the parent's native acceptance and post-merge gates before promotion. This document supplies instructions only; none of these manual steps is marked passed.

## Review boundary

The source branch remains preserved. This implementation branch has an accepted initial independent static review and parent-owned focused runtime evidence. The parent verified the exact instrument edits and authorized the normal author commit. Full-suite and native acceptance remain pending. Source acceptance and focused tests do not establish full product acceptance or close the remaining tradeability cohort.

## Independent static review

`opus-implementation-review.txt` retains the complete raw review. Opus accepted the static implementation and found no correctness, test-quality, or unrequested-complexity issue in the product/test diff. Its one non-blocking documentation finding is resolved in `opus-implementation-review-resolution.md`. The review does not establish runtime execution, approve new count or digest expectations, or provide native, full-suite, or promotion acceptance.

## Baseline correction for the raw-item assertion

The parent runtime capture `/tmp/crayfish-verification-ka1h3fbf` failed the new `assertNotIn("Raw crayfish", GE_ITEM_CATALOG)` expectation at `tests/test_grand_exchange_data.py:193`. The complete normalized Raw crayfish catalog row is identical in that capture and `/tmp/cut-gem-baseline-6438d422`: exact ID `13435`, guide price `58`, value `5`, buy limit `20000`, and Fishing ownership. The plain and Qt constant exports both confirm the same owner and true final registry flag. Both captured catalogs omit Burnt crayfish. `raw-crayfish-baseline-evidence.json` retains the selected structured rows and full input hashes.

The assumption confused the separate Cooking extra-item dictionary with the final registry. `core/item_registry.py` registers Fishing output rows before extra items and keeps the first occurrence of each storage key. The Fishing row therefore owns Raw crayfish despite the later Cooking extra-item false flag. The test now checks its unchanged exact ID, price, and limit. Only the incorrect new raw-item expectation changed; the Burnt absence assertion remains. The repair left product files, other tests, pins, and count instruments unchanged. The corrected test passed the parent-owned rerun in both lanes. This correction is not covered by the earlier static review's claim of no test-quality findings; the separate measurement review accepted it. The subsequent approved instrument changes are recorded separately.

## Retained parent runtime evidence

`mbp/failed-capture/` preserves the original FAIL JSON records and both large failed-focus stderr streams as deterministic gzip. That capture reported the incorrect new Raw crayfish absence assertion and an extra empty plain root baseline control. Those records remain unchanged. The empty plain root control is outside the 23 required payloads and is explicitly bound in the later semantic proof.

`mbp/focused-recheck/` preserves the corrected rerun from local `/tmp/crayfish-focused-recheck-6bfy75jk` and remote `/Users/armantarkhanian/ankiscape-remote-test-host/reports/crayfish-focused-recheck-6bfy75jk`. Both lanes ran the exact three named tests in `0.001s`, with `OK` and no skips. All four commands exited zero. All eight stdout/stderr hashes match the checkpoint, and the seven bound product/test/runner hashes match before and after that rerun and the author checkout before instrument edits. Both corrected discovery streams are byte-identical to the original capture.

`mbp/semantic-proof.json` is the exact parent-produced PASS record, SHA256 `63469a6c3cd7072133ca92526420ec7c71459a7ab7efaca528c9b9ef7daa6eda`. Its exact script bytes are archived as deterministic `.py.gz` evidence under `mbp/scripts/`. The proof records the 23 required payloads, 9 changed payloads, 14 byte-identical payloads, full-body reversal checks, and the exact discovery increase from 5562 to 5563 in both lanes. The author retained and checked these records without executing the proof or project runtime.

`mbp/retention.json` binds each retained record to its original path, raw bytes/hash, stored bytes/hash, and remote path where applicable. It also binds every full baseline/candidate surface stream by path and hash. The complete bodies remain in the parent's local and remote reports rather than being duplicated in Git. The initial failure, semantic proof, and corrected focused pass are separate evidence sets. None is described as full-suite, native, or promotion acceptance.

## Final instrumented source

`final-instrumented-source.json` binds the final seven changed Python files plus the runner and surface tool. The earlier source hashes remain unchanged inside their original capture records. Their passing focused run applies to the corrected tests before the two count updates and five digest updates. The product data and custody test are unchanged by these instrument edits. The parent independently reversed the five digest constants to the exact baseline surface-test bytes and the two counts to the corrected GE-test hash, then authorized the normal author commit. No full-suite, native, or promotion pass is inferred from this static update.

## Historical script storage

The four scripts in `mbp/scripts/` are immutable historical evidence snapshots stored as deterministic `.py.gz` archives. Their decompressed bytes and original SHA256s are unchanged. The normal author commit initially failed because slop-gate evaluated the plain snapshots as newly added runnable code; `author-commit-hook-rejection.txt` preserves that output. `script-evidence-storage.json` verifies the storage-only correction. The original `/tmp` scripts, raw reports, product files, tests, and hook configuration were not changed. A new normal commit awaits the parent's storage review.
