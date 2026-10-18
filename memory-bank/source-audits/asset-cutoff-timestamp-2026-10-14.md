# Historical image revisions require a timestamp — 2026-10-14

The source-confirmed C1/L1 repair rejects historical image rows whose timestamp is missing, empty or nonstring. It retains the configured cutoff and newest eligible revision. Nonhistorical lookup, request parameters, retries, original hashes and audit classifications stay unchanged. No artwork, existing UI or live provenance file changed.

The real fetch refusal test replaces only the network boundary and prevents a download from reaching live state. Baseline mainfdb1ac49 produced five failures across the two new tests, original exit1. Valid period/exact-cutoff selection and lookup without a cutoff remain positive controls. No full timestamp-format validation is claimed.

[Focused receipt](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-cutoff-timestamp/focused-qualified.json):27 actual tests in2.256s, no skips, original exit0 after fresh remote plain inventory. The two pre-existing Pillow normalization/validation tests are statically skipped in both plain and Qt environments and are excluded only from this focused selection. The original local29/2skip run and Qt inventory remain intact. The full gate retains all tests and its fixed skip rules. After the redundant empty-list cleanup, final local source passed the same27 supported cases in2.231s with no skips and original exit0; focused-final-local.json binds those bytes.

The removed type and empty-list checks were redundant: the candidate comprehension already admits dictionaries only, and an empty eligible selection already refuses empty imageinfo. Existing resolver, download, provenance and valid-image behavior stay covered by the surrounding suite.

Independent reviews, the exact merged gate with full remote lanes and official land remain pending. API-warning handling is a separate response-contract choice; this repair changes no warning policy. Native gameplay checks do not apply to this tooling-only change.
