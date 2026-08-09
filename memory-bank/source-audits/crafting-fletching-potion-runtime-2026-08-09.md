# Crafting and Fletching potion runtime — 2026-08-09

## Result

The settled target-local potion contract is implemented for Crafting and
Fletching. Both families use the period +3 current-level boost, real vial and
flask dose identities, carried-inventory consumption, persistent temporary
levels, review undo, and the shared review-driven temporary-effect clock. No
wall-clock or market-clock input is used.

This closes `artisan-skill-potion-runtime` without a placeholder.

## Period mechanics and identities

- game-main `PotionType.kt:90-98` binds Crafting and Fletching to the same
  `r_skill` strategy. `PotionType.kt:282-317` applies that strategy to current
  level and defines it as exactly `3`.
- game-main `Potion.kt:158-178` defines the four-dose vial replacement chains.
- OpenRS2 cache `runescape-742-2012-11-07-openrs2-544-disk.zip`, queried with
  `tools/query_openrs2_cache.sh --id`, pins Crafting vials `14838/14840/14842/14844`,
  Fletching vials `14846/14848/14850/14852`, Crafting flasks `23459-23469`, and
  Fletching flasks `23471-23481`. Every row is non-stackable and has `Drink`.
- The same cache query exposed an adjacent identity collision: the existing
  Super prayer flask family incorrectly used the Fletching IDs. Its correct
  six-to-one-dose sequence is `23525/23526/23527/23528/23529/23530`.
- Wimpy bird oldid `5936660`, timestamp `2012-07-14T21:51:38Z`, identifies
  `Wimpy feather` as the catch loot and secondary Fletching-potion ingredient;
  its drop section gives `5 - 10`. The existing deterministic Hunter row now
  awards the sourced minimum five instead of its erroneous copied Stripy
  feather output, so the live recipe and every dose-container transition have
  a fresh-profile acquisition route.
- The period GE harvester resolves all eight exchangeable states against dated
  `Exchange:` revisions. Their prices are `1,125/1,414/1,918/7,208` for the
  three new Crafting vial states plus full flask, and `39/43/42/3,125` for the
  equivalent Fletching states. Every row has the period four-hour limit
  `1,000`; generated coverage rises to 1,430 prices and 1,746 buy limits.

The cache establishes item identity, options, and container state. It is not
used to infer the temporary-level timer.

## Review-time translation

The owner-settled contract in
`gap-grill-decisions-2026-07-10.md#cross-skill-crafting-and-fletching-potions`
requires one current level to restore per 100 game ticks and forbids direct
market-clock mapping. The already-live global temporary-effect clock in
`magic-skill-contract-2026-07-11.md:197-201` advances 50 game ticks per
successful 1x review before action dispatch. Reusing it yields one restored
level per two successful 1x reviews and lets a review that drinks the potion
complete its now-valid action. This is a review-driven translation, not a
wall-clock timer.

## Runtime boundary

- Each Crafting or Fletching target exposes a saved `Use ... potion (+3) when
  needed` control in its existing Details card.
- A dose is consumed only when the current level is below that target's
  requirement and all non-level action inputs are available.
- Casual carried mode reserves one real slot for the best available matching
  dose. Advanced mode never reaches into the bank: the player must include a
  matching potion in that target's saved carried layout. The target remains
  locked until both the saved layout permits a matching dose and the player
  owns one.
- Dose replacement stays in the active carried pack. Re-dosing occurs only
  after temporary-level restoration would otherwise block the next action.
- Direct Bank `Drink` uses the same pure boost and dose-replacement path.
- Schema 113 sanitizes temporary current levels, the shared residual tick
  counter, and target-local policies. The normal review snapshot deep-copies
  the nested state, so drinking, decay, replacement, outputs, XP, and policy
  changes remain atomic and undoable through their established action seams.

## Assets

All 20 family states use the standard normalized potion asset path. The
family-scoped fetcher now requires the pre-EOC cutoff
`2012-11-20T00:00:00Z`. Provenance pins vial uploads to 2010-09-24/25 and flask
uploads to 2012-02-07. The Hunter row reuses the existing normalized
`shopitems/wimpy_feather.png`, whose provenance is timestamped
`2010-04-28T03:59:15Z`. The all-family tight-alpha audit passes.

## Verification boundary

Focused coverage exercises exact IDs, direct drinking, dose replacement,
50+50-tick restoration, the +3 target window, Casual re-dosing, Advanced
no-bank-reach and target-lock behavior, no-dose loss on missing materials,
migration, registry coverage, the Wimpy-feather acquisition bridge, asset
provenance, and the real offscreen Qt target control.

Fable reproduced an invisible dark-mode checkbox indicator in the first render;
the corrected indicator has a visible palette border and green checked state.
Kimi K3 returned `SHIP` on the corrected interaction, copy, and hierarchy. Its
provider could not open local PNG paths directly, so that pass used the exact
root-inspected dark/light render transcript plus the bounded UI/test lines;
Fable and the root inspected the rendered pixels directly.

A fully quit and freshly relaunched native Anki 25.09.4 process registered one
deck-browser hook. The real injected button emitted one bridge dispatch and
opened exactly one WindowServer-visible `AnkiScape Menu`. The Mac was at the
login window, so native visual navigation into the Crafting Details card was
not claimed; the real offscreen Qt interaction test and corrected dark/light
renders cover that surface until an unlocked native session is available.

Final closure passes 3,939 tests in the plain runner with 483 expected
environment skips and 3,939 tests in real offscreen Qt with three intentional
skips. Test-quality scanning finds zero hard issues across 3,905 tests in 178
files. The deterministic graph contains 1,537 actions and 2,333 reachable items
with the known 168-orphan/188-blocked debt; `Wimpy feather`, both three-dose
potions, both four-dose potions, and both full flasks have concrete routes.
Documentation, compilation, tracked JSON, diff, provenance, tight-alpha asset,
and guarded-worktree checks pass.

## Explicit omissions

- Hunter and Agility potions are not added by this slice. Their item families
  exist in the period game, but their skill-specific target policies are not
  part of the settled Crafting/Fletching contract.
- This slice does not add exhaustive Herblore recipes for creating the potions.
  It supplies the shared boost substrate required before those catalog rows can
  become mechanically live.
- No hidden server selector, random value, or unrecovered period content is
  invented.
