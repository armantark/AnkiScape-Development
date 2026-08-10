# Brewing input acquisition — 2026-08-09

Backlog scope: acquire Ale yeast and make Barley malt for the already-live
brewing family.

Status: implemented. No placeholder or owner decision is required.

## Evidence and reconciliation

- RuneScape Wiki `Barley malt` oldid `6207311`, dated
  `2012-09-07T05:05:49Z`, states that cooking one Barley on a range produces
  one Barley malt and awards no Cooking XP.
- RuneScape Wiki `Barley` oldid `5434668`, dated
  `2012-03-28T17:32:12Z`, independently gives the same range conversion and
  zero-XP result. The source presents a direct conversion, so the live action
  cannot burn or fail.
- RuneScape Wiki `Ale yeast` oldid `4227753`, dated
  `2011-05-03T04:36:27Z`, states that Blandebir in Keldagrim fills an empty
  pot for 25 Coins. Its period dialogue also permits filling every available
  pot, which supports the existing batchable shop-service contract.
- Darkan's Forgettable Tale implementation corroborates Empty pot `1931`, Ale
  yeast `5767`, and the 25-Coin exchange at
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/forgettable_tale_of_a_drunken_dwarf/ForgettableTaleState.kt:25`
  and
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/forgettable_tale_of_a_drunken_dwarf/ForgettableTaleOfADrunkenDwarf.kt:317`.
- The period item identities are Barley `6006`, Ale yeast `5767`, and Barley
  malt `6008`. All three are non-stackable. Their exchangeability is preserved
  in the shared item registry.

## Live implementation

- `Malt barley` is a level-1 row in the established Cooking `Brewing` group.
  One review consumes one Barley, produces one Barley malt, awards no XP, and
  uses the normal materials, carried-inventory, telemetry, persistence, and
  review-undo paths.
- Blandebir is a provider in the established Shop service surface. One unit
  consumes one Empty pot and 25 Coins and produces one Ale yeast. The quantity
  control fills as many pots as the requested quantity, available pots, Coins,
  and inventory capacity allow. The established Keldagrim route wall requires
  starting The Giant Dwarf, matching the other live Keldagrim providers. The
  existing direct-action undo path restores every input and output atomically.
- The shared Cooking runtime no longer emits a misleading `+0 XP` feedback
  event for authentic zero-XP success actions.
- The reachability ledger now resolves Barley malt through
  `Cooking:malt_barley` and Ale yeast through
  `Shop service:blandebir_fill_ale_yeast`.

## Assets and UI scope

- The new rows reuse existing cutoff sprites: `shopitems/barley.png` is
  `28 x 30` from `2011-11-17T20:57:16Z`,
  `farmingitems/barley_malt.png` is `32 x 32` from
  `2011-08-10T00:57:59Z`, and `cookingitems/ale_yeast.png` is `25 x 28` from
  `2011-08-10T00:57:52Z`. All are RGBA, provenance-recorded, and already
  normalized.
- This slice adds rows to the established Cooking selector and Shop service
  provider. It adds no surface, control, layout, or interaction pattern, so a
  separate Kimi/Fable taste pass is not required.

## Manual Anki check

1. Open Skills, Artisan, Cooking, and expand Brewing. Confirm `Malt barley
   (Lvl 1)` has an icon and says it cannot burn or fail.
2. Carry one Barley, select the row, and answer a card. Confirm it becomes one
   Barley malt without an XP popup.
3. Use Anki Undo and confirm the Barley is restored and the malt is removed.
4. Before starting The Giant Dwarf, confirm Blandebir is locked with the route
   requirement. Start the quest, select Blandebir, and request two fills while
   carrying two Empty pots and at least 50 Coins. Confirm the preview and result
   preserve exact pot, Coin, and Ale yeast quantities.
5. Use the Shop history undo and confirm the transaction reverses atomically.

## Explicit omissions

- Metarialus's five-Ecto-token Ale yeast route is valid period catalog depth,
  but it is not required to make the brewing mechanics reachable and remains
  a later breadth-depth slice.
- This slice does not expand the ale recipe catalog or change the existing
  mature-ale abstraction.
- Native Anki interaction is not claimed by automated offscreen Qt coverage.

## Verification

- Focused data, pure logic, runtime, shop, reachability, and Anki review-undo
  coverage passes 645 plain tests. The two focused real offscreen Qt selector
  and service tests pass.
- Re-running `tools/generate_npc_shop_data.py --services-only` preserves exact
  SHA-1 hashes for all three generated outputs.
- Full plain discovery passes 3,986 tests in 211.266 seconds with 486 expected
  skips. Full real offscreen-Qt discovery passes the same 3,986 tests in
  515.812 seconds with three intentional skips.
- Documentation passes across 541 Markdown and 431 HTML files. Test quality
  finds 3,952 methods across 180 files, zero hard issues, and 19 existing
  structural-clone groups.
- Reachability records 1,544 actions, 2,347 reachable items, 164 known orphan
  inputs, and 184 unresolved actions. This slice resolves both of its target
  inputs without adding an orphan.
- Compilation, tracked JSON, diff, asset normalization, and worktree-safety
  checks pass. Native Anki interaction is not claimed.
