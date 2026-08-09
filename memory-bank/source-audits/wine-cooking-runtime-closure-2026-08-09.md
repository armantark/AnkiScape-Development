# Make wine Cooking runtime closure — 2026-08-09

Backlog id: `cook-karambwan-family`

Status: implemented and verified. This audit closes only the settled wine
sub-slice; poisonous and thoroughly cooked karambwan remain separate depth
work under the same backlog row.

## Evidence and reconciliation

- RuneScape Wiki `Jug of wine` oldid `6151933`, dated
  `2012-08-27T16:10:12Z`, pins one Grapes plus one Jug of water, level 35
  Cooking, a Jug of wine on success, a Jug of bad wine on failure, 200 Cooking
  XP only on success, and an automatic ten-second fermentation after the
  unfermented intermediate.
- The owner-settled contract in
  `memory-bank/gap-grill-decisions-2026-07-10.md` maps that automatic wait to
  one atomic review action. The unfermented state is conceptual inside the
  transaction and is never persisted or driven by wall time.
- OpenRS2 rev-742 and Darkan `WineMaking.java:25-29` agree on Jug of water
  `1937`, Grapes `1987`, unfermented wine `1995`, Jug of wine `1993`, and Jug
  of bad wine `1991`. Rev-742 also pins all five as non-stackable, Jug of
  water/Grapes/Jug of wine as exchangeable, and unfermented wine/Jug of bad
  wine as non-exchangeable.
- The period page does not expose the hidden success roll. Darkan
  `WineMaking.java:15-23` reconstructs a 60% floor, `Cooking level / 68` above
  that floor, and guaranteed success at level 68. The live value is registered
  as `cooking.wine_success_curve`; it is not promoted to a period fact.

## Live implementation

- `Make wine` is an ordinary level-35 row in the existing grouped Cooking
  selector. One review consumes one Grapes and one Jug of water.
- Success produces one Jug of wine and awards 200 base Cooking XP. Failure
  produces one Jug of bad wine, awards no XP, records `bad_wine` telemetry,
  and does not increment the ordinary burn counter.
- Selection, material gating, carried inventory, persistence, cadence routing,
  achievements, telemetry, and Anki review undo use the existing Cooking
  paths. The regression suite proves the bad-wine branch restores both inputs
  and removes the output atomically on Anki Undo.
- The row tooltip names both outputs, the source-level requirement, the live
  success chance, the two materials, and the no-XP bad outcome. This is one new
  row in an established selector, not a new UI surface, control, layout, or
  interaction pattern, so it does not require a separate Kimi/Fable taste pass.

## Assets

- Grapes, Jug of water, and Jug of wine reuse existing normalized item art.
- No wiki file revision for `Jug of bad wine.png` exists before the gameplay
  cutoff. The oldest available OSRS upload, timestamped
  `2019-08-13T06:18:04Z` with SHA-1
  `576bb1401f191575a7b9db3fb22444299fca9eb4`, is pinned strictly as visual art.
  It proves no mechanic or period value.
- `tools/fetch_cooking_assets.py` reproduces that exact visual fallback through
  an explicit item-only cutoff while all other Cooking art retains the
  pre-EOC cutoff. The normalized `25 x 28` RGBA sprite is tight-cropped and
  provenance-recorded.

## Manual Anki check

1. Open Skills, Artisan, Cooking at level 35 or higher.
2. Expand Brewing and confirm `Make wine (Lvl 35)` has an icon and lists both
   the good and bad outputs.
3. Carry one Grapes and one Jug of water, select the row, and answer cards.
   Confirm each review immediately produces wine or bad wine without a timer.
4. Confirm wine awards 200 base Cooking XP, bad wine awards none, and both
   consume exactly one pair of inputs.
5. Use Anki Undo and confirm inputs, output, XP, telemetry, carried state, and
   random state return atomically.

## Explicit omissions

- The exact period success curve remains a registered placeholder.
- The automatic ten-second source wait is deliberately flattened into the
  review action; there is no wall-clock fermentation or persisted unfermented
  item between reviews.
- This slice does not implement karambwan, karambwanji, a winery activity, a
  new shop route, or any quest parity.

## Verification

- Focused data, pure logic, runtime, integration undo, placeholder, asset, and
  real offscreen Qt coverage passes 464 broad focused tests, 14 exact closure
  tests, and 1 Qt target-row test.
- Full plain discovery passes 3,977 tests in 261.850 seconds with 486 expected
  skips. Full real offscreen Qt discovery passes the same 3,977 tests in
  586.298 seconds with 3 intentional skips.
- Documentation passes across 539 Markdown and 431 HTML files. Test quality
  finds 3,943 methods across 180 files, zero hard issues, and 19 existing
  structural-clone groups.
- Reachability records 1,539 actions, 2,342 reachable items, 167 known orphan
  inputs, and 187 unresolved actions. This slice adds one action and one
  reachable output without adding an orphan.
- Compilation, tracked JSON, deterministic asset resolution, asset
  normalization, diff, and worktree-safety checks pass.
- Native Anki interaction is not claimed. Computer Use returned `The Mac is
  locked and automatic unlock could not unlock it. Ask the user to unlock the
  Mac manually before continuing.` before exposing the application state.
