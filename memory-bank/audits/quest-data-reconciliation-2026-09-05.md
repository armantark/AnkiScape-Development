# Quest data reconciliation

The quest split keeps the existing public interface and returns fresh item metadata on each call. The focused runtime checks passed in the plain and Qt environments before the final blank-line repairs. The author commit, full branch and repository gates, and exact merged-tree gate remain pending.

## Preserved state

The parent retained the complete dirty split in stash `26edc9cce80d09bb7bc1bc243defb040ee49e253`. Do not drop this stash.

| Reference | Value |
| --- | --- |
| Original split branch | `goal/split-quest-data-2026-09-02` |
| Original split HEAD | `0128255a0e3aa223a3d33b67c2d96f2115d9ad5a` |
| Stash tree for untracked files | `4af562cde28ce09d78deffeea251577e83bc613e` |
| Current branch | `goal/quest-data-reconciliation-2026-09-05` |
| Current HEAD and main baseline | `814b4d591df4525e0bda4a1f858baf6345ed4d38` |
| Original quest source SHA-256 | `825e9cc0ef5c16acab2f18e9842b9c7d90b4e3b84da9ad1700680cf4036c160e` |

Main and the original split HEAD contain the same original quest source bytes. The current changes have no commit yet.

The stash application left one conflict in `tests/test_quest_catalog.py`. The markers were `<<<<<<< Updated upstream`, `=======`, and `>>>>>>> Stashed changes`.

The author restored the entire file from main under owner rulings 44 and 47. Main already supplies the replacement scanner in `tests/quest_catalog/test_literal_mappings.py`.

## Final source layout

The public path remains `data/quest_data.py`. Its exports have the same 703 names and the original order.

The parts retain separate contracts, quest definitions, stage overrides, catalog assembly, ledger data, serializers, and reward projection. Each quest definition retains its existing module.

| Module | Purpose | Lines |
| --- | --- | ---: |
| `data/quest_data.py` | Public exports | 728 |
| `data/quest/stage_cleanups.py` | Complete original cleanup registry | 986 |
| `data/quest/sources.py` | Shared source registry | 963 |
| `data/quest/reward_items.py` | Fresh reward-item projection | 139 |

The cleanup registry replaces the `classic.py` and `later.py` partition. It contains the exact original annotated assignment, with all 74 entries in their original order.

The source registry replaces the single-child `sources/` package. It retains the existing source values and export declaration.

The split has 83 part files and one public facade. Every production module stays below 1,000 lines. The consolidations preserve each existing import path.

## Reward metadata ownership

The original reward function created a fresh metadata dictionary for each literal item on each call. The retained split exposed module-global metadata dictionaries through its return value.

The function now copies each fragment metadata dictionary into the result. All metadata values are immutable scalars or strings, so a shallow copy preserves the original ownership.

The private `_catalog_reward_items` helper contains the original catalog projection and a return statement. The public function applies authored additions, fresh fragment metadata, and the original non-item filter.

The author did not change the order of these operations. The authoritative complexity gate still must assess the new helper and the changed public function.

## Static evidence

The complete record is `memory-bank/evidence/quest-data-reconciliation-2026-09-05/static-reconciliation.json`.

- The record binds 90 source files with SHA-256 hashes.
- All 63 unchanged original definitions retain identical abstract syntax trees (ASTs).
- The reward function has the ownership repair and the catalog helper described above.
- The other adapter changes only the relative import in `claims_as_dict`.
- All 14 nonempty quest-ID mappings retain their key sets and value ASTs without duplicate keys.
- The 45 stage replacement entries retain their original order.
- The complete cleanup assignment retains its original AST and all 74 entries.
- The 39 reward fragments retain all 207 original rows, in the original order.
- The 703 public names retain the original export order.
- The explicit internal import graph has no cycle or import back into the facade.

The existing external diary cycle remains outside this change. This audit does not claim to remove it.

The following files remain byte-identical to main:

- `tests/test_quest_catalog.py`
- `tests/quest_catalog/test_literal_mappings.py`
- `tests/test_module_surface.py`
- `tools/module_surface.py`
- `run_tests.py`

## Authored tests

The new file is `tests/quest_catalog/test_split_contract.py`. It contains three tests:

1. Compare two reward projections, check distinct metadata objects, save an independent deep copy, mutate one result, and compare a new projection with that saved copy.
2. Import every part in a fresh native interpreter process without the facade. Map each package marker to its canonical package name.
3. Reject missing or extra public names, then compare the export order with the original order digest.

The export order digest is `52c2a717897772ebfd24a710e38aeec1d477ea615aafc364530e7c5d34d4de76`.

The parent executed all three tests in both environments through the serialized MacBook runner. All passed without skips. The author independently checked the retained raw outputs and source bindings.

## Independent review

The parent read the complete Opus review from session `21419`, which exited with status 0 and returned PASS. The exact raw review is retained in `memory-bank/evidence/quest-data-reconciliation-2026-09-05/reconciliation-review.txt.gz`.

Two small findings are applied. The reward module no longer imports unused IDs, sources, or item names. The metadata test saves a deep copy before mutation, so later shared mutation cannot change its expected result. Every per-row identity assertion remains.

The optional aggregate duplicate-export test is not added. Parent and group exports intentionally overlap; the exact public-surface check, export-order digest, and static definition checks retain the acceptance contract. The optional comment and runtime concern caused no additional source change. The focused runtime checks below passed after both repairs.

The static report records the preceding reviewed manifest, both review hashes, the dispositions, and all current source hashes. The review does not represent a runtime pass.

## Retained focused verification

The parent ran the approved packet in terminal session `53033` and reported exit status 0. The author copied only the four immutable report directories, checked every file against its remote hash, and independently checked the raw results. The parent then independently accepted those results.

The complete machine manifest is `memory-bank/evidence/quest-data-reconciliation-2026-09-05/runtime/manifest.json`. It retains all four reports, raw streams, execution scripts, source bindings, baseline archive manifest, and independent verification as exact gzip payloads. Each retained file has decoded and stored lengths and SHA-256 hashes.

The capture completed two baseline serializer jobs and 39 candidate jobs. Every job has matching source and part-inventory snapshots before and after execution. The candidate snapshots bind all 90 source files and all 83 quest part paths. The baseline checks also verify the complete 6,133-file main archive before and after capture.

| Check | Plain environment | Qt environment |
| --- | --- | --- |
| Three new split tests | 3 passed, no skips | 3 passed, no skips |
| Complete quest tests, including the new tests | 111 passed, no skips | 111 passed, no skips |
| Existing measurement tests | 5 run, 1 expected skip | 5 run, 1 expected skip |
| Test discovery | 5,570 IDs, exactly 3 additions | 5,570 IDs, exactly 3 additions |
| Ownership assertion canaries | 3 intended assertions caught | 3 intended assertions caught |

The measurement skip is `test_root_initializer_is_reported_as_unavailable_without_aqt`, with the exact reason `root initializer requires aqt; use the offscreen Qt interpreter`. The measuring tests retain both internal interpreter cases in each outer environment.

All 23 required public payload files match the approved baseline byte for byte, including their strict digest footers. All six serialized quest tables match a fresh main baseline in each environment. Discovery preserves the original 5,567 IDs in order and adds only the three new split tests.

Both remote source-mismatch canaries exited with status 2 before any runtime job and produced no results file. The local source canary recorded zero remote commands. The six ownership canaries reached the intended assertions at lines 4, 26, and 29 and preserved the original fragment storage.

Both environments resolve to the same Python 3.14.6 binary. They verify plain and Qt environments, not different Python versions.

## Final layout repair

The normal author commit in terminal session `73083` was rejected by the layout gate. The parent approved seven blank-line insertions and one removal across five source files. The focused evidence above remains bound to the earlier bytes.

The separate record `memory-bank/evidence/quest-data-reconciliation-2026-09-05/layout-equivalence.json` gives each tested and final source hash. All nonblank lines and attribute-free ASTs match. The direct layout check passed. The other 85 bound files remain unchanged; the retained static and runtime manifests are unmodified. Full branch and promotion gates must test the final exact bytes before landing.

## Remaining gates

1. Review this evidence-retention delta and create the normal author commit.
2. Run the full branch and repository gates, including the authoritative complexity gate for the reward function and its helper.
3. Compose other approved quest changes only after their separate verification.
4. Run the gate on the exact merged tree.

The source split has no separate blanket hold for native UI checks. The parent owns the remaining runtime work.

The old source directories retain pre-existing ignored bytecode caches. The author removed only the approved source files and recorded the directory-removal failure in `memory-bank/papercuts.md`.
