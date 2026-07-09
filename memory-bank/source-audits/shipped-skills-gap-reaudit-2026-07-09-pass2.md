# Shipped-skills gap re-audit — 2026-07-09, pass 2

## Scope and classification rule

This is the mandatory fresh pass after `craft-runtime-remainder` merged and the transcription lane drained again. Three independent read-only audits compared all 11 shipped review skills on current `main` against the local 2011Scape rev 667 checkout at `/Users/ArmanTarkhanian1/Downloads/game-main`. A row is a transcription only when game-main supplies a live runtime binding plus authoritative data. Static, commented, unbound, or emulator-absent content remains a `needs_grill` stub.

## New transcription batches

- `craft-combinations-polished-buttons`: the generic item-combination plugin registers all 40 `CombinationData` rows. Fourteen belong to Fletching; of the 26 Crafting-default rows, only `STUDDED_BODY` and `DRAGONSTONE_AMULET` were present. The same pass found the live level-3, 5-XP Buttons polishing action.
- `fletch-crossbow-assembly`: the first 14 `CombinationData` rows are live stock/limb and stringing actions for seven crossbow tiers. It depends on the Crafting combination batch so shared conventions land first. Javelin construction remains a separate stub because game-main has no construction binding for it.
- `cook-runtime-extras`: `gut_fish.plugin.kts` live-binds all three leaping-fish gutting actions with exact success formulas, outputs, XP, and offcut probabilities; `seawead_cooking.plugin.kts` live-binds Seaweed to Soda ash for 1 XP.
- `herb-pestle-remainder`: all 31 `PestleAndMortarData` rows are runtime-bound, while AnkiScape represented seven. The same source check found item 6810 is canonically `Bonemeal`, not the invented storage key `Wyvern bonemeal`.
- `mine-runtime-glory-variants`: `Mining.kt` explicitly grants the 1/86 gem chance to charged, trimmed, and duplicate-ID Amulet of glory variants. AnkiScape omitted the trimmed display variants and cited the wrong plain-name source ID.

## Coverage with no additional gap

- Woodcutting: all 11 trees, nine axes, Inferno-adze behavior, and nest mechanics are represented.
- Fishing: every runtime-bound `FishingSpot` to `FishingTool` pair is represented; standalone unbound rows remain already-classified stubs.
- Smithing: the generator reproduces all nine smelting and 157 forging rows exactly.
- Firemaking: all 13 runtime-bound log rows are represented; bonfires, pyres, and beacons remain existing stubs.
- Runecrafting: all 13 standard runes, 12 combination runes, four pouch tiers, and five active `Tiara.values` rows are represented. Commented tiaras are not transcription rows.
- Hunter: game-main has no Hunter action tree; its missing families remain existing stubs.
- Herblore: the 31 clean-herb, 31 unfinished-potion, and 104 finished-potion tables otherwise match source.

No Combat or Prayer implementation was expanded or changed by this audit.
