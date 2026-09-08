# Enemy prayer-drain extraction — 2026-09-08

## Result

The combat engine now delegates only the enemy prayer-drain calculation to the existing combat-specials module.

The helper accepts the enemy, raw enemy damage, and remaining prayer points. It returns `None` when the normalized base is not positive.

For an enabled drain, the helper returns the exact clamped integer. Zero remains a valid enabled result.

The caller retains the subtraction, the result counter, and the player-data write. The call stays after raw damage capture and before protection scaling.

No random-number call, mechanic, callback, context object, tuple contract, or user interface changed.

## Runtime proof

Plain and Qt each passed the same three focused tests in `0.002` seconds with zero skips.

The focused set covers disabled and enabled-zero boundaries, raw damage before protection, and the existing Tz-Kih route.

Plain and Qt each passed nine complete-output comparison cases against commit `6dacde5486c72e73ca170c039bf8207dec22ac81`.

All 18 comparison rows have equal return values and protocol-4 pickle bytes. Their random-number draws, route values, and input nonmutation checks also match.

The four remote run IDs are:

- `plain-1788845066-00afbbe6`
- `plain-1788845101-2b8311af`
- `qt-1788845160-738f446e`
- `qt-1788845183-43e01b01`

Every job exited zero. Each before and after guard matched the same 1,185-entry inventory with SHA-256 `248d5502a017d83e2a060a2041061a5acd442a8101200bea52029ac3de1a2850`.

The exact compressed runtime files and their original hashes are in `memory-bank/evidence/combat-prayer-drain-2026-09-08/runtime-retention-manifest.json`.

The parent independently read the completed evidence with a restricted unpickler. The retained verification is `memory-bank/evidence/combat-prayer-drain-2026-09-08/parent-runtime-verification.json.gz`.

## Remaining gates

The focused and differential runtime gates are closed for this branch.

The full source gate, composition gate, landing, and native programme acceptance remain pending.
