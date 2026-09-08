# Wyvern breath preparation

Status: static authoring only. The parent assigned P5 at `afae5ee6f736607bbe0937c1e682e959a14c0ca3`. Its composition gate was pending at assignment. No main acceptance is claimed. This leaf did not run tests, product imports, guards, discovery, AST checks, metrics, audits, restoration checks, runtime, network commands, or Git mutations. The parent owns all checks, remote state, commits, and merges.

The private helper calculates breath damage and returns the existing event. The caller keeps attack selection, the earlier dragonfire draw, shield protection resolution, the unprotected counter, the delay update, and event order. Existing values and conversion rules are unchanged. No new test fixture or data value is needed. The focused selection reuses the four kernel/runtime methods and the review undo/replay method. No UI file changed.

The comparator plans nineteen real-data cases: six shields, four unprotected or ineffective-antifire states, four protection-prayer combinations, an ordinary attack, and protected/unprotected legacy and resumed cadence. Each case records complete returned values, RNG state and draws, and full pickle bytes. It checks player, enemy, and equipment input nonmutation. Explicit route expectations require damage, protection count, the complete event, step count, and live delay remainders. Legacy cadence must lack the live remainder field. Equality alone is insufficient. These expectations have not run.

The manifest binds the full baseline, full candidate, complete reversible patch, and the source inventory. The inventory covers tracked Python/JSON files and the new probe/guard plus both snapshots. Its trusted hash comes from the manifest. The guard uses the existing pre-import canary pattern: correct preflight, four wrong-pin/source cases, `-O`, and `PYTHONOPTIMIZE=0`, with product import sentinels. External interpreter and dependency provenance remains parent-owned. Freeze the sources before the first guard; any source change requires a new freeze and new proof.

Diff-only simplification: the product change needs one helper and one caller replacement. There is no public API, class, shared framework, new mechanic, or remote driver. The helper returns the existing event so it needs no second delay return value. Existing focused tests carry direct assertions; the differential reuses their fixtures and the existing recorded RNG. No additional abstraction was identified for removal during author review. Independent review remains pending.

The parent must first review the complete product and operational packets, verify all bindings, inspect the full diff, and run the installed syntax/layout/metric ratchets and forward/reverse patch restoration. These are proposed checks, not completed evidence. Normal hooks, both full lanes, exact merged-tree gates, and programme native acceptance remain open. The commands below are payloads for the authorized host, not permission to sync or launch it.

```sh
python3 -B tools/combat/check_wyvern_breath_guards.py --candidate-sha256 9b1265b5600971f8a6927773d5e840595fa1864ccb3459979471d5b3522db585 --inventory-sha256 bafb3e85e96bcff10bba3934fbf98ad09527a9f84fb9a726617f2f3980f60534 > /tmp/ankiscape-wyvern-breath-guards-2026-09-07.json
python3 -B -c 'import gzip; from pathlib import Path; Path("/tmp/ankiscape-wyvern-breath-baseline-2026-09-07.py").write_bytes(gzip.decompress(Path("memory-bank/evidence/combat-wyvern-breath-2026-09-07/baseline-engine.py.gz").read_bytes()))'
python3 -B run_tests.py --verbosity 2 SkeletalWyvernKernelTests SkeletalWyvernReviewUndoTests
python3 -B tools/combat/compare_wyvern_breath.py --baseline /tmp/ankiscape-wyvern-breath-baseline-2026-09-07.py --candidate-sha256 9b1265b5600971f8a6927773d5e840595fa1864ccb3459979471d5b3522db585 --inventory memory-bank/evidence/combat-wyvern-breath-2026-09-07/source-inventory.json.gz --inventory-sha256 bafb3e85e96bcff10bba3934fbf98ad09527a9f84fb9a726617f2f3980f60534 --output /tmp/ankiscape-wyvern-breath-comparison-2026-09-07.json
```

Require all seven guard cases with no product import, all five focused methods with zero skips, and all nineteen named comparison cases in each authorized lane. Retain raw logs and reports. Require value equality, byte equality, route success, and the exact source inventory before and after each run. Neither this note nor a prepared command proves those outcomes.

## Parent operational review correction

The original review packets remain unchanged. The correction packet contains the operational changes against those reviewed sources. Preflight now measures loaded product modules before reporting absence. Guard rows retain actual exceptions, stdout, stderr, and subprocess return codes; failed assertions include those rows. In-process runs label their return code as null because no subprocess ran.

Source tracing gives three RNG draws for a live breath: player miss, enemy selector, and breath damage. Resuming for the next tick adds no attack and retains three cumulative draws. Legacy cadence attacks at ticks zero and four, then selects and rolls breath at tick six, for four draws. The ordinary control lands both attacks and rolls both damage values, plus the selector, for five draws. Its enemy damage is 1 LP, the existing minimum for a landed ordinary attack. These are proposed explicit expectations, not measured results. The same full comparison and guard acceptance conditions still apply. No engine or test source changed during this correction.

## Module placement correction

After parent review, the unchanged helper moved into `logic_pure/logic_pure_combat_specials.py`. The engine imports it after its existing dependencies. The baseline engine has no dependency on the new module; the candidate module imports only existing model/state helpers. The complete product patch includes creation and reverse removal of the new file. The static scope includes that file against an absent baseline. Earlier packets, failed static reports, and raw independent review are preserved. Probe, guard, and test logic did not change. No correction checks have run.

## Parent runtime acceptance

The parent accepted runtime session `50115`, exit `0`. Both lanes ran all five focused methods with zero skips. The parent verified all nineteen ordered comparison cases per lane, complete pickle byte equality, explicit RNG totals, and every actual route payload against its full expectation. All eight source guards retained identical complete 1,077-entry maps before and after; four completion reports exited zero, and current local sources matched the same inventory. The complete original output directory and console are retained as deterministic gzip files with original paths, sizes, and hashes in `runtime-acceptance.json`. The parent independently verified all 38 retained files, 17,907,290 original bytes, every stored and decoded size/hash, and original byte identity. This leaf ran no runtime and changed no source. Full programme gates, composition, and native acceptance remain parent-owned.
