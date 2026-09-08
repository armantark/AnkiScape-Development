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

## Source acceptance and integration

Root accepted food source `d87e51be3ee770bbf19284ab3136538a8e816c93`, source gate `87718`, exit 0 and all eight checks at `2026-09-08T14:41:23-07:00`, after reading the complete log and receipt. Root-reported plain results: 5,612 tests in 572.395s with 1,367 skips; Qt: 5,612 tests in 1102.668s with 5 skips. The source is being merged into pre-merge integration `afca8a37` with poison, KEEP, and death-prayer. The combined gate, canonical-main promotion, and native acceptance remain pending; main remains `1bf2cfe2fa77cea2bb24528c6844d7473b1c2d12`. This documentation resolution did not rerun any gate.

Keep product, tests, comparator, harness, and historical evidence frozen. Root owns the normal merge commit, exact combined gate, promotion, and separate native programme acceptance.

## Limits

The current proof covers focused and differential behavior, the full staged slop gate, and the committed source gate. It does not establish acceptance of the merged tree.

Native programme acceptance remains pending. It does not block this behavior-preserving split from the normal landing workflow.

The first failed comparison is historical evidence. Do not delete it or replace its expected `Safe` route.

Do not run another fixture correction. The accepted comparator has only one added input: `constitution_level=10`.
