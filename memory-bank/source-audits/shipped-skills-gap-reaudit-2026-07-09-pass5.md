# Shipped-skills gap re-audit — 2026-07-09, pass 5

## Scope and classification rule

This mandatory fresh pass ran after `smith-dragon-square-shield` merged and the transcription lane drained. Four independent read-only comparisons covered all 11 shipped review skills on current `main` against the local 2011Scape rev 667 checkout at `/Users/ArmanTarkhanian1/Downloads/game-main`.

Direct source-backed behavior with an already-settled AnkiScape representation enters the automatic transcription lane. Emulator features represented only by static metadata, or whose faithful review-action representation requires missing historical values and owner design, remain `needs_grill`. Combat and Prayer stay out of scope.

## New safe transcription batch

- `rc-single-essence-trip-selection`: standard Air-through-Body crafting currently fills one action by spilling from Rune essence into Pure essence. `RunecraftAction.kt:120-128` instead selects the first valid essence item ID present, removes only that stack, and bases output and XP on it. The existing AnkiScape row order and test convention already settle Rune-essence-first priority, so the faithful correction is mechanical and does not require new design.

This item is pending for the next driver tick. Its scope preserves every altar, pouch, multiplier, output, and XP rule while adding a mixed-stock regression.

## Newly parked owner-design gaps

- `fm-barbarian-bow-lighting`: Otto dialogue and the Barbarian Skills book set/document a persistent unlock, but game-main has no bound bow-on-log action and no authoritative runtime eligibility or XP distinction. Historical sourcing and the training/unlock representation need owner approval.
- `cook-cooking-gauntlets-runtime`: game-main defines item 775 and its equipment metadata but contains no Cooking implementation for affected fish or burn-rate thresholds. Historical data, acquisition/conversion, equipment state, persistence, UI, and undo all need owner decisions.

## Coverage with no further new gap

- Mining: all 14 live rocks, 15 pickaxes, essence switching, Dragon-pickaxe bonus, incidental/glory gems, and Varrock-armour outputs are represented. Existing Living Rock, brawling-gloves, boost, routing, guild, quest, and acquisition decisions were not duplicated.
- Woodcutting: all 11 trees, nine axes, Inferno-adze behavior, and bird-nest drop/open tables are represented. Canoes remain the existing `wc-canoe-shaping` stub.
- Fishing: all 28 fish rows and every distinct live tool/spot binding are represented. Cave eel and activity/current-level systems remain previously classified items.
- Smithing: all nine smelting rows, 157 forge rows, and Dragon square shield assembly reproduce the live source.
- Crafting: all skill-directory, furnace, generic combination, and clay-ring families are represented. Existing documented abstractions are not omissions.
- Fletching: all live whittling, stringing, feathering, arrow, and crossbow-combination rows are represented. Existing javelin and shared runtime stubs were not duplicated.
- Firemaking: all direct log and light-source bindings are represented; only the newly identified metadata-only Barbarian bow-lighting stub was added.
- Cooking: all direct cooking, gutting, seaweed, and preparation bindings are represented; only the newly identified metadata-only gauntlet stub was added.
- Runecrafting: standard, combination, pouch, and active-tiara bindings are otherwise represented; the one mixed-essence behavioral mismatch entered the transcription lane.
- Hunter: game-main has no Hunter runtime skill/action tree. The existing tracking/pitfall/snare and habitat/Jadinko stubs already cover that absence.
- Herblore: 31 clean herbs, 31 unfinished potions, 104 finished potions, pestle preparation, vial filling, and swamp-toad preparation remain represented. Existing potion-state design is already parked cross-skill.

## Verification

The Smithing merge was reviewed and approved after removing unrelated generated equipment drift. On current `main`, `python3 run_tests.py` completed successfully with **983 tests passed and 157 skipped**. Main had no tracked or present `.gap-review` artifact. No Combat or Prayer implementation was changed by this audit.
