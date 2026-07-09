# Shipped-skills gap re-audit — 2026-07-09

## Scope and rule

This is the mandatory fresh completeness pass after the transcription lane drained. It compares the 11 shipped review skills against the local, read-only 2011Scape rev 667 checkout at `/Users/ArmanTarkhanian1/Downloads/game-main`. A row is a transcription candidate only when game-main supplies both authoritative data and a runtime binding. Static metadata without an action binding is not auto-filled.

## Result

Two new transcription batches were added to `memory-bank/gap-backlog.json`:

- `craft-runtime-remainder`: five glassblowing rows, the Slayer ring, two Silvthrill silver rows, roots-to-crossbow-string spinning, and the nine milestone capes. Each is reached by a game-main action/plugin, not merely declared in an enum.
- `mine-inferno-adze-tool`: `PickaxeType.INFERNO_ADZE` is a live Mining tool with item 13661, level 41, and three ticks between rolls, but AnkiScape still classifies it as deferred. It depends on the already-merged Woodcutting Inferno adze item work.

## Evidence by skill

- Cooking: all 52 `CookingData` rows are represented.
- Fishing: all 28 `Fish` rows are represented. `FishingTool.BARB_HARPOON` is not referenced by any `FishingSpot`, so its standalone enum row is not a transcription action. The already-ledgered cave-eel binding remains a stub.
- Smithing: the checked-in generator output matches `smithing_data.py` exactly (166 recipes).
- Crafting: Gem, Tanning, Leather, and Battlestaff source families are complete. Runtime inspection confirmed the omitted rows listed in `craft-runtime-remainder`. `PotteryData.NOT_URNS` is only a grouping wrapper and is not a craftable output.
- Fletching: source enum identifiers are represented globally; apparent per-file bolt misses were citation-path differences rather than absent actions. Full crossbow assembly and javelins remain the existing stub.
- Firemaking: all 13 source log rows are represented; bonfires, pyres, and beacons remain existing stubs.
- Runecrafting: standard runes, combination runes, and AnkiScape's tiara targets are represented. Only five entries are active in game-main's `Tiara.values`; commented entries were not treated as missing transcription work.
- Woodcutting: all 11 source tree rows and nine source axe rows are represented, including the merged Inferno adze behavior.
- Mining: all source rock rows are represented. The Inferno adze is the one live `PickaxeType` still excluded from the active AnkiScape pickaxe table.
- Hunter: game-main has no implemented Hunter action tree; the existing Hunter items remain stubs.
- Herblore: 31 clean-herb, 31 unfinished-potion, and 104 finished-potion rows match the 31 `HerbData` and 104 `PotionData` source entries.

No Combat or Prayer implementation was inspected for expansion or changed by this audit.
