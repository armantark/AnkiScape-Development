# Due bank-trip initialization

Status: parent-verified focused and differential runtime checks passed in plain and Qt lanes. The source commit is `33c138e1cc82aac5edab16dcad8670394cbce6f0` on `goal/carried-new-bank-trip-2026-09-08`, based on main `6dacde5486c72e73ca170c039bf8207dec22ac81`. Full source and promotion gates remain pending. This branch is not accepted on main.

## Responsibility

`_initialize_due_bank_trip` initializes a newly due trip. It consumes run energy credit before the duration roll and applies an outbound altar teleport after the roll. It preserves the live player dictionary and returns the travel profile, review cost, route phases and teleport flag. The caller retains admission, active-trip progression, action dispatch, bank gates, transaction rollback and saves.

The focused tests cover credit, RNG and teleport order; player identity; zero-duration travel; fractional rounding; and a nonmatching teleport. Existing whole-overlay tests cover manual travel, full-credit waiver, new altar travel and an already outbound route.

The differential comparator checks the complete baseline and candidate overlay results. It retains player data, seeded RNG state and draw history, and ordered callback snapshots. The nine routes cover moving trips, partial credit, full waiver, rejected actions, no trip, active travel, altar travel with and without a teleport, and Winter Storage rejection. It requires both value equality and exact pickle-byte equality.

## Accepted evidence

The parent measured seven focused tests per lane, zero skips and 0.001 seconds per lane. Each comparison passed all nine routes. Full payload inspection verified RNG snapshots, callback events and live player identity. The Winter Storage handler saw eight special points; rejection restored twenty. All source guards and local source checks matched the 905 pinned inventory entries. The fixed static ratchets also passed.

Evidence is in `memory-bank/evidence/carried-new-bank-trip-2026-09-08/`:

- `runtime-retention-index.json` identifies every retained runtime file, exact run identity, original hash and stored hash.
- `accepted-runtime/parent-runtime-verification.json.gz` records the parent's complete payload verification with a restricted unpickler.
- `parent-static-retention.json` identifies the fixed-instrument measurements and raw results.
- `source-inventory.json.gz` binds the source, data, configuration and frozen baseline.
- `product-review-resolution.json` and `comparator-review-resolution.json` record review decisions and source evidence.
- `runtime-protocol-bindings.json` and `runtime-protocol-command-proposal.json` identify the retained one-job protocol and exact commands.

Historical preparation records remain in the evidence directory. They do not replace the accepted scope stated here.

## Manual verification and remaining gates

The parent owns all remote execution. Before promotion, complete the full source and promotion gates against the exact branch source. Keep the shared mirror lock and pending-run identity rules in force.

For an interactive check in Anki, request a mining bank trip with partial run energy credit and verify that travel begins before the next action. Repeat with full credit and verify that the action can proceed without travel reviews. Start a runecrafting trip with a pending Wicked hood altar teleport and verify that only the outbound phase is skipped. Continue an existing outbound trip and verify that its progress remains correct. These interactive checks are instructions, not a claim of completed visual acceptance.
