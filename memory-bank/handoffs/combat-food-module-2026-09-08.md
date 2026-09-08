# Combat food module handoff

## Goal

Land the combat food module without a behavior change. Keep all old import surfaces and preview results exact.

## Context

Use branch `goal/combat-preview-food-2026-09-08`. Its baseline is `6dacde5486c72e73ca170c039bf8207dec22ac81`.

The new module contains five unchanged food definitions. It also contains one helper from the old inline preview loop.

The parent accepted the plain and Qt focused proof. The parent also accepted both differential lanes.

## Completed proof

The focused set passed nine tests in each lane. Each lane had zero skips and took 0.002 seconds.

The differential set passed 15 cases in each lane. Complete values, pickle bytes, route results, and input state match.

All source guards use the same 1,218-entry inventory. The before and after bytes match in all four jobs.

The installed directory-cap check covers the actual locations. `logic_pure` has 27 Python files, and `tests/combat` has eight.

The first full staged slop gate failed because six historical source copies were stored with a `.py` suffix. They now use deterministic gzip storage with exact stored and decoded bindings. The previous raw archive manifest remains preserved. The same full staged gate passes with empty stdout and stderr. The cached diff check then exposed context-space lines in nine retained raw prompt and diff files. Those files now also have deterministic gzip bindings. All eight pre-change manifest snapshots remain preserved, and a new unpinned storage overlay owns the current mappings.

The runtime packet retains 42 files. See `memory-bank/evidence/combat-food-module-2026-09-08/runtime-acceptance.json`.

## Required next steps

1. Keep the product, test, comparator, and harness files frozen.
2. Complete the root review of the final branch diff and evidence.
3. Create one normal hook-respecting branch commit.
4. Run the full source gate against that clean commit.
5. Review every gate result against the frozen source inventory.
6. Merge the exact commit into composition tree I.
7. Run the exact post-merge gate.
8. Land the accepted composition on main without a new owner approval step.
9. Track native programme acceptance as a separate programme check.

## Limits

The current proof covers focused and differential behavior plus the full staged slop gate. It does not cover the post-commit full source gate or the merged tree.

Native programme acceptance remains pending. It does not block this behavior-preserving split from the normal landing workflow.

The first failed comparison is historical evidence. Do not delete it or replace its expected `Safe` route.

Do not run another fixture correction. The accepted comparator has only one added input: `constitution_level=10`.
