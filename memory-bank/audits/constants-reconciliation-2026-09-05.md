# Constants domain split reconciliation, 2026-09-05

## Frozen author scope

The integration combines preserved split `0246e1fc0306d558648b511ca79813e01e46b036` with main `814b4d591df4525e0bda4a1f858baf6345ed4d38` on `goal/constants-reconciliation-2026-09-05`. The original split branch and driver branch `goal/promote-queue-runner-2026-09-05` at `9fcac099f9cb171353be6e683d5823f78c8644c3` remain preserved. The only merge conflict was `tests/test_module_surface.py`. Its complete existing measuring module matches main's AST after removing only the two added split tests and export-order pin. This preserves every current digest and module entry, including activity actions.

The repaired layout has 16 standalone part modules plus the package initializer. The static part-import graph is acyclic. No root-globals rebinding, function reconstruction, or facade dependency was introduced. The static evidence records the current 21 source hashes. These are source claims, not runtime results.

## Exact moves and adaptations

All six original function definitions retain identical normalized ASTs. `_asset_slug` moves to `core/constants_parts/skill_assets.py`; the other five remain in the facade. The report records their current source and destination lines. These function matches do not make every top-level statement an identical move.

- `core/constants_parts/paths.py:9` uses one more parent directory and a private `os` import because the module moved down one directory.
- `core/constants_parts/activity_updates.py` owns `DEFAULT_UTILITY_ACTIVITY`, the complete original 30-row `UTILITY_ACTIVITY_DATA` literal, and all subsequent updates. Both assignments match main's AST exactly. The module is 819 lines. `activity_base.py` and the row-copying adaptation are removed.
- `core/constants_parts/quest_items.py:5` owns the original quest-item projection assignment, with an AST identical to main. The facade imports its public name at the prior binding position, and `activity_assets` imports the same object privately. This keeps standalone asset assembly complete and removes the duplicate producer call. The shared owner is an import seam; the facade does not fill the standalone module's map.
- The equipment helpers in `skill_assets.py` retain the original 20 pre-diary statements and three post-diary statements after explicit normalization of the local equipment name and imported base alias. Facade lines 55–58 retain source precedence: pre-diary sources, diary equipment, post-diary sources, then item projection. The helper scopes and calls are adaptations. Their placement remains in `skill_assets.py`; this repair adds no further equipment-module split.
- The equipment/image order changes. Main runs the quest, combat-item, and combat-enemy image blocks at lines 1894–1957 before equipment assembly at 1958–1982. The candidate assembles equipment at facade lines 55–58 and imports `activity_assets` at line 60. Direct AST name checks find no equipment-map reads in those image blocks and no image-map reads in the equipment helpers. This supports the ordering decision but does not prove transitive producer behavior; exact runtime equality remains required.
- The export manifest retains main's 562 statically collected public names in their original order. The facade's resolved static public-name set matches that manifest. The public `re` import stays for compatibility. Comments beside the shared Crafting, Utility, Quest, and Combat maps identify their filling modules and explain why the declarations remain in place.

## Independent review dispositions

Opus session `46703` returned ACCEPT with findings for the preceding source snapshot. Its exact raw output is retained as `../evidence/constants-reconciliation-2026-09-05/reconciliation-review.txt.gz`; the static report records its original path and raw and stored hashes. It is not a fresh acceptance of these repairs.

The duplicate-projection finding is resolved through the independent `quest_items` owner. The suggested facade-side image loop was rejected because a standalone asset import would then have incomplete quest images. The 13/17 activity split is replaced with the single original literal. The export test now rejects missing pinned names and extra public names before checking the unchanged order digest. The standalone loop excludes `__init__.py`, so it no longer creates a second package module object. The compatibility import and shared-map comments are added, and the assembly-order adaptation is recorded above. The optional per-part invariant was not added: the bounded standalone and complete public-surface checks remain the acceptance contract.

The existing isolated-import test rejects a part that loads the constants facade, including during helper calls. Its equipment case requires a separate assembled map and an unchanged source map. Its activity-assets case requires the shared quest-owner identity. The export test checks that the facade exposes that same quest object. All existing count and catalog assertions remain. Both embedded subprocess scripts were parsed, not executed.

## Retained MacBook verification

The parent ran the reviewed capture in session `44711` and copied both reports in session `78219`, which exited with status 0. The positive report is `/tmp/constants-verification-4zvp5lvc`. The rejected-source report is `/tmp/constants-verification-cm93gyaa`.

The complete retained evidence is `../evidence/constants-reconciliation-2026-09-05/runtime/manifest.json`. It binds 99 retained files. The raw content totals 126,846,993 bytes; the stored content totals 12,474,244 bytes. Every compressed file was decompressed and compared with its original bytes. This retention pass did not run project code or use the MacBook.

The positive capture passed all 35 jobs. All 21 source hashes match the reviewed snapshot before and after every job. The 70 stdout and stderr files match their recorded byte counts and SHA-256 hashes. The current local source files still match that snapshot.

Both named split tests passed without skips in each interpreter lane. The complete measuring selection ran seven tests in each lane, with one expected skip each: `root initializer requires aqt; use the offscreen Qt interpreter`. The existing interpreter helper retains both internal interpreter cases; the outer Qt lane does not remove the plain-interpreter skip.

All 23 complete public-surface files match the approved baseline in `/tmp/cut-gem-baseline-6438d422`, byte for byte. Each strict footer also matches the hash of its complete body. The retained candidate files also serve as the baseline bytes because this retention pass directly compared the original files and proved equality; the manifest records both source identities. No measuring pins changed.

Discovery contains 5,569 test IDs in each lane, compared with 5,567 baseline IDs. The only additions are the two named constants tests. Removing those additions preserves the exact baseline order. The original discovery streams are retained.

All six ownership canaries passed: the facade-presence, base-map alias, and base-map mutation fixtures each reached the intended `AssertionError` at embedded-script lines 4, 20, and 25 in both lanes. Each fixture reported that the original base map remained unchanged.

The local source guard reported `Frozen source bindings changed; no remote commands launched` and a remote-command count of 0. The remote wrong-source capture reported `Source hash mismatch; no runtime commands launched`, a subprocess count of 0, and no `results.json`. The parent recorded capture exit status 2. This retention pass independently verified the report content and absence of the results file; it did not repeat either canary.

## Final source review

Opus session `64197` reviewed the repaired source and returned PASS with exit status 0. The parent read the complete result and accepted that there were no defects. The exact raw output is retained as `../evidence/constants-reconciliation-2026-09-05/final-repairs-review.txt.gz`; `final-repairs-review.json` records its hashes and dispositions.

The optional notes require no product change. The compatibility import remains. The missing/extra export checks and all 23 exact public-payload comparisons retain the surface contract. The Clue-scroll direct lookup preserves the existing behavior.

The final repaired-source review is complete. The parent also independently compared all 99 retained runtime files with their originals and verified all 21 current source hashes. The original runtime manifest remains unchanged as the retention snapshot.

## Remaining acceptance

The static report remains frozen at SHA-256 `62570531c49eab9fc59e88ab1f107720e6a95b15c83211db3d34094244ff0565`. It records the exact allowed name normalization. The owner requirements are §48 at `handoffs/design-to-impl-rulings-2026-08-13.md:2914`, §47 at `:2881`, and §53 at `:3136`: named domain seams, standalone modules, explicit treatment of adapted bodies, and no rebinding into another module's globals.

The targeted verification and accepted source review do not replace full branch and repository gates, native verification, or the exact merged-tree gate. These remain pending. The parent reviewed the retained evidence manifest and authorized the normal author commit. The parent owns the mirror and all runtime execution. This document records the pre-commit state; no local project imports, tests, UI, remote access, or promotion ran in this retention pass.
