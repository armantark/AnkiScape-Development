# Due bank-trip initialization: prepared for parent review

Status: authoring and static source checks only. No product import, test, runtime, remote operation or author commit has run. Parent product review 78863 is in progress. The product and test sources are frozen for that review.

The source branch is `goal/carried-new-bank-trip-2026-09-08`, based on main `6dacde5486c72e73ca170c039bf8207dec22ac81`. `_initialize_due_bank_trip` owns only initialization of a newly due trip. It uses the existing context and returns the existing travel profile, review cost, route phases and outbound-teleport flag. The helper preserves energy credit consumption, conditional RNG, hood consumption, in-place player dictionary update and the travel record in the original order. The caller retains admission, active-trip behavior, cadence, Winter Storage, waiver, bank gates, rollback, repacking, handler execution, saves and UI.

Static evidence is under `memory-bank/evidence/carried-new-bank-trip-2026-09-08/`. `static-preparation.json` records source and packet hashes. The complete original trip block and helper body have identical attribute-free ASTs. Removing the helper, restoring the caller block and restoring the orphaned outer credit default reconstructs the entire baseline overlay byte for byte. Three authored Python files parse and compile as source without execution. `git diff --check` passed. No complexity score or runtime outcome is claimed.

`product-and-tests.patch` contains the bounded extraction and three new test methods. The tests exercise credit/RNG/teleport order and player identity; zero-duration trips with consumed or retained credit; and fractional rounding with a nonmatching teleport. Their numeric expectations are proposed fixtures, not measured results. Existing tests remain unchanged. The focused recipe adds four existing whole-overlay tests for manual travel, full-credit waiver, a new altar teleport and an already outbound route.

`comparison.patch` contains one whole-overlay comparison tool. It reuses the existing frozen-module loader, context fixture, callback tracer, RecordedRandom and Winter Storage rejection fixture. It stores complete results, player dictionaries, RNG state and ordered callback snapshots in exact pickle payloads. Both value equality and pickle-byte equality are required. The nine named routes cover moving/partial-credit/waived/rejected trips, no-trip and active-trip paths, altar travel with and without a teleport, and Winter Storage rejection rollback. Callback snapshots include handler entry/exit, RNG, saves, achievements and availability refresh. The stored rejection fixture also proves that the handler saw the spent special points and that rejection restored them.

The route RNG counts follow the source path. Moving mining and altar trips draw once during scheduling and do not run the handler that review. A full-credit waiver and a no-trip path draw only in the controlled handler. An active trip draws neither. The controlled handler deliberately draws once so accidental scheduling on an acting path changes both event order and RNG state. The rollback fixture keeps full recorded RNG state without an invented draw-count constant.

`source-inventory.json.gz` binds current tracked source/data/config files, all tracked project Python sources outside memory/config archives, the three authored sources and the frozen baseline gzip. `static-instrument-pins.json` retains the previously reviewed gate/tool identities for parent verification; the author did not run analyzers. `runtime-recipe.json` gives exact selectors, comparator arguments, output format and parent-owned lock/pending/retry requirements. It is not an execution wrapper. No new remote driver was added. Parent must retain each source guard, log, report and result before advancing, and review any failure before a retry. Full branch, composition and native acceptance remain separate.

Do not reopen the landed processing-accounting extraction, change other carried behavior, or touch the parallel prayer-drain worktree. Old P3 source/evidence remain unchanged.

Product review conditions are resolved in product-review-resolution.json. The exact annotation and credit assertion patch requires parent inspection. Runtime checks remain pending.

Comparator review resolution is retained in comparator-review-resolution.json. Only the direct context replacement was accepted; the RNG and import-path findings were rejected against source evidence. Runtime remains NOT_RUN.

## Parent-verified runtime acceptance

The parent completed the plain and Qt focused and differential jobs. Each focused lane passed seven tests with zero skips in 0.001 seconds. Each comparison passed nine ordered cases, exact full pickle bytes and values, RNG snapshots, callback events and live player identity. Winter Storage exposed eight special points to the handler and restored twenty after rejection. Each source guard and local source check matched all 905 inventory entries. The exact run identities, original reports and hashes are retained in runtime-retention-index.json.

The helper owns only newly due trip initialization: it consumes run energy credit before the duration roll and applies the outbound altar teleport after the roll. The caller retains active-trip progression, action dispatch and transaction rollback. Product review corrections add typed inputs/results and assert the consumed credit in the travel record. The comparator uses a seeded RNG fallback, preserving the full RNG state and draw history.

The full source and promotion gates remain pending. This branch is not accepted on main. The parent owns all remote execution; this author retained evidence and prepared the attributable branch commit.
