# Crafting 2011Scape Source Audit

## Status

Backend parity foundation completed on 2026-06-03. Crafting now has a focused source-data module, `crafting_data.py`, keyed by stable recipe IDs while inventory remains keyed by real item names.

## Primary Sources

Local 2011Scape rev 667 source under `/Users/ArmanTarkhanian1/Downloads/game-main`:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/gems/GemData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/pottery/PotteryData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/pottery/AddRuneAction.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/spinning/SpinningData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/silver/SilverData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/jewellery/JewelleryData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/leather/LeatherData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/glassblowing/GlassData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/weaponry/BattlestaffData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/weaving/WeavingData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/combine/CombinationData.kt`
- `data/cfg/items.yml` for canonical display names and tradability.

## Implemented Backend Scope

`crafting_data.py` encodes live Crafting targets for the source-backed categories that matter to the AnkiScape economy now: gem cutting, pottery including representative urn flows, spinning, silver, jewellery including dragonstone/onyx, leather, glass, battlestaves, weaving, and selected Crafting combinations. All clear-source rows are ordinary runnable recipe data; there is no artificial hidden/locked state. If an input has no acquisition route yet, the target naturally reports missing materials until a future skill, drop, market, or Utility/Activity supplies the item.

Important corrected values from 2011Scape:

- Emerald cutting is 67.0 Crafting XP, not the legacy pilot's 67.5.
- Sapphire necklace is 55.0 Crafting XP, not the legacy pilot's 60.
- Ball of wool and Bow string are XP-bearing Crafting actions and therefore run one action per review. The old 28x batch behavior belongs only to no-XP Utility/Activities.

## Backend Decisions

- Stable recipe IDs now live in `current_craft`; legacy display names migrate through `LEGACY_CRAFTING_TARGETS`.
- `Soft clay` remains a no-XP Utility/Activity target and migrates to `current_utility = make_soft_clay`.
- Crafting tools/stations such as chisels, moulds, needles, furnaces, potter's wheels, ovens, looms, and glassblowing pipes remain implicit. They are source requirements but not gameplay objects yet.
- Semiprecious gem crush chances are documented in source but not modeled. One successful review represents one successful Crafting action.
- Dragonstone, onyx, battlestaff-orb, hide/tanning, molten-glass, root, and rune-dependent content is live but input-starved until acquisition systems exist.

## Tests

Coverage added/updated for stable IDs, corrected 2011Scape values, live input-starved dragonstone targets, legacy migration, no XP-bearing Crafting batching, item manifest registration, review dispatch, and undo-safe Utility regression coverage.

## Leather and Tanning Completion (2026-07-09)

`LeatherData.kt` is now complete in `crafting_data.py`: the lower-tier cowl,
vambraces, chaps, and coif; all snakeskin pieces; both yak-hide armour rows;
and the missing green, blue, red, and black dragonhide pieces use the source
level, XP, and leather-count values. The two Yak-hide armour source items share
one canonical display name, so their separate stable recipe IDs retain source
item IDs 10824 and 10822 while the name-keyed inventory exposes one item name.

`TanningData.kt` now drives all eight review-paced Utility tanning activities,
including both snake-hide source variants and all four dragonhide colours. The
two snake-hide item IDs share the same canonical display name in the source
cache; AnkiScape's name-keyed inventory therefore intentionally uses `Snake
hide` for both service rows while preserving their distinct 15- and 20-coin
source prices. Existing local leather art is reused for newly registered
outputs; no network asset fetch was performed.

## Runtime-bound remainder completion (2026-07-09)

`crafting_data.py` now also carries every remaining source row with a live
Crafting binding from the re-audit: five `GlassData` outputs, the
`JewelleryData.SLAYER_RING`, both `SilverData` rows, six separate root-input
`SpinningData.CBOW_STRING1` recipe IDs for the model's single-requirement
shape, and milestone capes 10 through 90. Output names and source item IDs are
pinned in focused tests. In particular, the source keeps ID 7637 as
`Silvthrill rod` but calls ID 13154 `Silvthril chain`. The source's `CRAFT_ROS`
unlock for Ring of slaying (8) and its all-skills milestone-cape gates are
retained as recipe notes because Crafting has no Slayer or cross-skill gate
model.

`PotteryData.NOT_URNS` remains omitted because it is a source grouping wrapper,
not an output row. The Crafting asset fetch now supplies item-specific pre-EOC
sprites and provenance for all new outputs; the sole title exception is the
canonical `Candle lantern`, whose published inventory file is `Candle lantern
(empty)`. No Beer glass, Unpowered orb, Gold ring, Silver sickle, or Cape of
legends substitute art is used for this runtime-bound remainder.

## Leather Thread Semantics (2026-07-09)

All 27 already-live `LeatherData` rows now require one `Thread` to be present;
`Needle` remains implicit under the settled toolbelt decision. `LeatherAction.kt`
removes the recipe leather first, then consumes exactly one Thread only when
`world.random(1..5) == 1`; the Crafting data/runtime path mirrors that ordering
with an injected deterministic roll. The carried processing overlay packs the
non-material presence item and reconciles Thread only when the action actually
consumes it, so a retained Thread does not disappear and Anki undo restores a
consuming roll. Thread had already been registered through its live acquisition
paths, so no new item ID or asset fetch was needed.

## Held Mould and Glassblowing Pipe Gates (2026-07-09)

All 29 live `JewelleryData` products, all nine `SilverData` rows, and all
eight `GlassData` glassblowing rows now carry exact non-consuming
`required_items` metadata. `JewelleryAction.kt:77-87` and
`SilverAction.kt:67-81` reject a craft without its row's mould, while their
action loops consume only bars/gems/extra inputs at `JewelleryAction.kt:50-59`
and `SilverAction.kt:36-47`. `GlassblowingAction.kt:61-69` similarly requires
the pipe and its loop consumes only Molten glass at `GlassblowingAction.kt:24-36`.

`MouldItems.kt:8-20` supplies the complete mould mapping. Jewellery mappings
are transcribed from `JewelleryData.kt:10-288`; silver mappings are transcribed
from `SilverData.kt:15-78`; and the pipe applies to every row in
`GlassData.kt:10-17`. The 14 source item IDs are registered as Crafting tools,
including input-starved Unholy, Demonic sigil, Chain link, Conductor, and Rod
clay moulds. Existing local mould/pipe assets are reused as fallbacks; no
network asset fetch occurred.

No new recipe rows were needed: this is metadata on the 46 already-live rows.
Needle, Chisel, and Tinderbox remain implicit toolbelt tools. Default mode
checks bank ownership; advanced carried mode puts the exact required mould or
pipe in the carried view and reconciliation leaves it there after a craft.
Focused data, pure readiness/apply, advanced-overlay reconciliation, item/icon,
and undo coverage passed (327 tests). The shell lacks a bare `python` command;
`/opt/homebrew/bin/python3 -c "import crafting_data"` passed.
