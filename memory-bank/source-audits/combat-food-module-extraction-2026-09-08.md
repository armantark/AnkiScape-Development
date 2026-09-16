# Combat food module extraction — 2026-09-08

## Acceptance state

The parent accepted the isolated focused and differential runtime proof. The branch remains uncommitted at this checkpoint. The full source gate, exact merged-tree gate, native programme acceptance, and main landing remain pending.

The candidate uses baseline commit `6dacde5486c72e73ca170c039bf8207dec22ac81`. The working branch is `goal/combat-preview-food-2026-09-08`.

## Module boundary

The new `logic_pure/logic_pure_combat_food.py` module owns five definitions that moved without source or abstract syntax tree changes:

- `_DEFAULT_COMBAT_AUTO_EAT_FOOD`
- `_combat_consume_auto_food`
- `_combat_loaded_food_count`
- `_combat_banked_auto_food_count`
- `_combat_auto_eat_food_available`

The model re-exports the default tuple and consumption helper. The supplies module re-exports all five former surfaces. Every namespace that exposed these definitions at the baseline keeps the same object identity.

The new `_combat_preview_food_available` helper extracts the baseline engine's inline preview loop. Only the food module and engine expose this helper. The supplies module does not add a new preview-helper export.

The new module imports only `Mapping`, `COMBAT_FOOD_DATA`, and three existing state helpers. The checked dependency graph adds no cycle. The new module has 112 lines, below the 1,000-line growth cap. The `logic_pure` package has 27 Python files, below the 40-file directory cap.

The new test stays in the existing `tests/combat` package. That directory has eight Python files, below the installed 40-file directory cap.

## Review and static proof

The boundary validator proves five exact relocations and the preserved baseline export set. It also proves the preview loop became one helper call without changing the surrounding preview statements.

The final Opus review accepted the product boundary after the parent resolved its concerns. The corrected comparator preflight passed with no product imports. The 34.642-second temporary-index slop check covered the selected product and test paths, but omitted the archived source copies.

The first full staged slop gate therefore failed in 42.253 seconds because six archived `.py` files were evaluated as new code. Those exact source bytes now use deterministic gzip storage with stored and decoded bindings, and the previous raw archive manifest remains preserved. The same full staged gate then passed in 37.564 seconds with empty stdout and stderr.

The cached diff check then exposed context-space lines in nine retained raw prompt and diff files. Those nine files now also use deterministic gzip storage with exact decoded bindings. All eight pre-change manifest snapshots remain preserved byte-for-byte. A new unpinned storage overlay owns the current gzip mappings without changing the historical manifests.

The focused set has nine tests. Four existing tests cover consumption, loaded and banked food, auto-flee, and refill. Five narrow tests cover preview-food behavior and the preserved export identities.

## Parent runtime acceptance

| Lane | Run ID | Accepted result |
| --- | --- | --- |
| Plain focused | `plain-1788896592-6b36c0ba` | 9 tests, 0 skips, 0.002 seconds |
| Plain differential | `plain-1788896628-a8430591` | 15 cases passed |
| Qt focused | `qt-1788896684-cbc79c52` | 9 tests, 0 skips, 0.002 seconds |
| Qt differential | `qt-1788896707-9a1e7c54` | 15 cases passed |

Both differential lanes match complete baseline return or exception values. They also match full pickle bytes and the structure from the restricted unpickler. All route expectations pass, and all player, enemy, and equipment inputs remain unchanged.

All four jobs use the same 1,218-entry source inventory. The parent verified equal remote maps and raw guard bytes before and after each job. Every local-after inventory matches the current source bytes.

The retained packet contains all 42 original runtime files. They total 6,023,586 bytes before compression and 2,352,403 stored bytes. Each gzip entry binds the original and stored byte counts and SHA-256 hashes. See `memory-bank/evidence/combat-food-module-2026-09-08/runtime-acceptance.json`.

## Failed fixture attempt

The first plain differential job exited `1` because `risk:safe-threshold` retained `constitution_level=1`. The preview capped the requested 100 lifepoints to 10, so the case could not enter the authored `Safe` route.

All 15 baseline and candidate results still matched in that failed job. All 15 pickle byte strings also matched. The correction added only `constitution_level=10` to that comparator case and kept the `Safe` expectation.

The original failed files remain under `memory-bank/evidence/combat-food-module-runtime-attempt-1-2026-09-08`. The complete pre-correction candidate and evidence packet remains under `memory-bank/evidence/combat-food-module-pre-fixture-fix-2026-09-08`.

## Remaining gates

The parent must complete the root review and create a normal branch commit. The full source gate requires that clean commit. The parent must then merge the exact commit into composition tree I, run the exact post-merge gate, and land the accepted composition on main. This behavior-preserving split needs no new owner approval step.

Native programme acceptance remains pending as a separate programme check. It is not a blanket pre-landing hold for this split.

This acceptance does not claim a full test lane, a merge result, native behavior, or main completion.
