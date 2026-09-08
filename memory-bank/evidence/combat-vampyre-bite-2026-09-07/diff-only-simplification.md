# Diff-only simplification record

Scope: the reviewed product-and-tests.patch plus the bounded operational correction. This is a source/diff reading, not an executed metric or behavior check.

- Engine helper and caller: one transaction helper with six inputs and three return values. The existing drain implementation remains the only data mutation mechanism. The original outer gate, aggregate counters, LP updates and combat ordering remain in the caller. No extra class, model, compatibility path or repeated player-roll calculation was introduced. No further deletion is justified by the accepted boundary.
- Focused tests: three methods share the existing real-player fixture and catalog. The methods cover distinct draw, selection and cap/floor behavior. Existing tests and assertions are untouched. No fixture framework was added.
- Comparator: full return/RNG/input evidence is intentional. The correction computes each pickle once, then reuses its exact bytes for equality and storage. Guards use the existing per-file mechanism for the already-bound baseline; no duplicate unreachable baseline or candidate canary was added. Five negative rows plus the separate positive preflight remain bounded.

Parent Opus review 61588 accepted semantics and minimality. Product and tests are frozen. Operational corrections and the proposed static script await parent review/execution. No metric, test, guard or runtime was executed by this author.

Operational packet: The driver reuses the reviewed P13 lifecycle, source guards, durable writes and pending ownership. P3 changes only the source binding, selector list, case contract and gzip decoding. No alternate runner, retry framework, product abstraction or dependency was added. The new compression canary covers the actual format difference. Static measurements remain a parent execution step.
