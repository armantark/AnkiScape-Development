# Shipped-skills gap re-audit — 2026-07-09, pass 4

## Scope and classification rule

This mandatory fresh pass ran after `craft-held-mould-pipe-gates` merged and the transcription lane drained. Three independent read-only comparisons covered all 11 shipped review skills plus generic live item/object handlers on current `main` against the local 2011Scape rev 667 checkout at `/Users/ArmanTarkhanian1/Downloads/game-main`.

Direct source-backed rows with an already-settled AnkiScape representation enter the automatic transcription lane. Live emulator mechanics whose faithful review-action representation requires new spatial, temporary-level, equipment-charge, or acquisition design are parked as `needs_grill` under the prompt's design-question rule. Combat and Prayer remain out of scope.

## New safe transcription batches

- `mine-gilded-pickaxe-source-levels`: restore Gilded steel, adamant, and rune pickaxes to the source's live level-1 requirement. `PickaxeType.kt:75-97` supplies the values and `Mining.kt:35-44,178-183` consumes them directly; `mining_data.py:301-304` currently invents 6/31/41 normalization.
- `craft-clay-ring-mould-gate`: add the non-consumed Ring mould requirement to the existing unfired clay-ring row. `clay_ring.plugin.kts:5-36` supplies the binding, and the settled held-item semantics from ledger item 31 make this mechanical.
- `smith-dragon-square-shield`: add the exact level-60, 70-XP combination of Shield left half 2366 and Shield right half 2368 into Dragon sq shield 1187 from `dragon_sq_shield.plugin.kts:6-59`.

All three skills are independent and may run in parallel. The Crafting row explicitly depends on the already-merged held-mould semantics.

## Newly parked owner-design gaps

- `wc-canoe-shaping`: four live canoe shaping rows exist, but AnkiScape lacks outputless XP Utility and world-spatial travel state. Owner must choose shaping-only versus shaping-plus-travel and the action/state representation.
- `artisan-skill-potion-runtime`: live Crafting and Fletching potions grant exact +3 current-level boosts, but no shared noncombat temporary-level/decay contract exists. Owner must define persistence, decay, UI, gating, and undo without reusing Combat-only state blindly.
- `skilling-brawling-gloves-runtime`: live charged/location-sensitive multipliers span Mining, Smithing, Woodcutting, Fishing, Cooking, and Firemaking. Owner must define Wilderness/location mapping, acquisition/equipment, charges, UI, and undo as one shared design.

Dwarven stout was not added: its single faithful action necessarily mixes Mining/Smithing boosts with Constitution and melee-stat changes, so a partial skilling-only port would violate the no-Combat constraint.

## Coverage with no further safe gap

- Mining: core rock/tool/runtime rows are complete after the newly queued gilded-level correction.
- Woodcutting: all 11 trees, nine axes, Inferno-adze behavior, and nest mechanics are represented; canoe shaping is parked.
- Fishing: all 28 fish rows and live spot/tool bindings are represented; cave eel remains the existing stub.
- Smithing: nine smelting and 157 generated forging rows remain exact; Dragon square shield assembly is the newly queued generic handler.
- Crafting: skill-directory families are complete after ledger items 22, 24, 30, and 31; the generic clay-ring handler supplies the one new gate.
- Fletching: all live action families are represented; only the shared potion-state decision remains.
- Firemaking: 13 log rows, Inferno-adze behavior, and 11 light-source pairs are represented; existing activity stubs and shared brawling-gloves design remain.
- Cooking: all 52 cooking rows and live gutting, seaweed, and prep actions are represented.
- Runecrafting: standard/combination runes, pouches, and active tiaras are represented; spatial routing remains outside the review-action abstraction.
- Hunter: game-main has no Hunter runtime skill implementation; existing `needs_grill` families cover the absence.
- Herblore: 31 clean herbs, 31 unfinished potions, 104 finished potions, pestle preparation, vial filling, and swamp-toad preparation are represented.

## Verification

After the final held-mould merge, `python3 run_tests.py` completed successfully: **973 tests passed, 157 skipped**. Main had no tracked or present `.gap-review` artifact. No Combat or Prayer implementation was changed by this audit.
