# Slayer Mutated zygomite Combat closure — 2026-07-18

## Disposition

Both ordinary Mutated zygomites are now executable Combat targets. The slice
closes the last ordinary Slayer finishing-blow family without exposing or
renormalizing an incomplete Slayer-master pool.

## Accepted period facts

RuneScape Wiki `Mutated zygomite`, oldid `6530349`, timestamp
`2012-11-04T01:56:40Z`, establishes:

- level 74 / 650 LP / 65 Slayer XP and level 86 / 750 LP / 75 Slayer XP;
- Slayer 57 and Zanaris-only access;
- `Pick fungi` as the reveal interaction;
- magical melee up to 88 LP and an occasional ranged spore attack around
  140 LP;
- reduction below 20 LP before one Fungicide-spray charge is spent;
- ten spray charges and a full refill from one Fungicide canister;
- guaranteed Ashes and the visible qualitative drop families.

Lost City oldid `6564063`, timestamp `2012-11-16T19:00:23Z`, establishes
Zanaris access through Lost City. The live target therefore requires Slayer 57
and completed Lost City. The occasional spore attack's frequency is not
present in a period-valid source and remains `source_blocked`; it is not
invented.

## Local reconstruction evidence

Darkan's level-74 and level-86 combat definitions independently converge on
650/750 LP, maximum hit 88, all-five combat stats at 65/75, magical attack
accuracy, passive aggression, and respawn delay 59:

- `data/npcs/combatdefs/uncategorized/mutated_zygomite/mutated_zygomite_(74).json:1-30`
- `data/npcs/combatdefs/uncategorized/mutated_zygomite/mutated_zygomite_(86).json:1-30`

`data/npcs/drops/mutated_zygomite.json` supplies independent numeric
probabilities. Where its quantities conflict with the higher-tier period page,
the period quantity wins. The accepted rows are therefore explicitly
reconciled probabilities, not claimed period-exact rates. Fungicide, Anagogic
ort, Coins, Spin ticket, and any row whose identity or quantity cannot be
reconciled are not assigned false exact rates. Guaranteed Ashes is exact.
Fungicide is the necessary acquisition route for the period-proven canister
reload mechanic, but no exact rate survives; its period `Common` label is
represented by a conservative labeled `1/8` abstraction. Anagogic ort, Coins,
and Spin ticket remain omitted.

Darkan's `MutatedZygomite.java:34-76` confirms the `Pick` transformation and
item-gated conditional-death family, but its inherited ten-percent threshold
and non-consumption semantics conflict with the period page. Those lower-tier
details are rejected. The live implementation uses the period-exact
`1–19 LP`, spends exactly one charge, preserves the remaining spray dose, and
turns an empty spray plus one loaded canister into a nine-charge spray on the
same finishing action.

## Review-native implementation

- The two target rows retain distinct levels, LP, stats, and Slayer XP.
- The encounter note flattens the world interaction to one line: pick the
  fungi, then fight normally.
- Manual and quick finishers share the same atomic charged-item transition.
- A bank refill loads one highest-dose spray. An empty spray plus canister is
  restored to ten charges at the bank; spare canisters use remaining pack
  slots after the selected safety loadout.
- Dose variants are real non-stackable, non-tradeable cache items `7421–7431`;
  Fungicide is item `7432`.
- Both targets use the period file revision of `Mutated zygomite icon.png`
  (`2011-11-26T10:07:23Z`). Fungicide uses its period file revision. No
  pre-cutoff per-dose spray sprite series was recoverable, so all dose states
  share the existing spray silhouette and remain distinct in text/state.

No wall-clock time is used.

## Verification contract

Regression coverage must prove both access gates, both target variants, the
19/20-LP boundary, dose preservation, `1 → 0`, empty-plus-canister reload,
quick-finisher parity, bank-pack capacity, runtime dispatch, registry identity,
provenance, and the real offscreen Qt action/tooltip/icon surfaces.
