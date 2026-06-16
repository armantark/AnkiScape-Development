# Firemaking 2011Scape Source Audit - 2026-06-16

## Scope Decision

Firemaking v1 implements the local 2011Scape rev 667 line-lighting loop only:
one selected burnable item, implicit tinderbox, one review action per lighting
attempt, XP on successful burn, and `Ashes x1` as the output.

Bonfires and fire spirits are historically pre-EOC 2012 content and therefore
technically compatible with AnkiScape's just-before-EoC model, but they are
deferred from this v1. They introduce a separate training method and reward
surface: batch log feeding, bonus Firemaking XP, fire-spirit reward rolls,
Cooking boost behavior, and temporary-health warmth. They should land as their
own Firemaking extension, not as hidden behavior inside ordinary log burning.

## Primary Local Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/firemaking/FiremakingData.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/firemaking/FiremakingAction.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/firemaking/firemaking.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`

## Source Rows

`FiremakingData.kt` defines the complete source-backed burnable table:

| Target ID | Item | Item ID | Level | XP |
| --- | --- | ---: | ---: | ---: |
| `logs` | Logs | 1511 | 1 | 40.0 |
| `achey_logs` | Achey tree logs | 2862 | 1 | 40.0 |
| `oak_logs` | Oak logs | 1521 | 15 | 60.0 |
| `willow_logs` | Willow logs | 1519 | 30 | 90.0 |
| `teak_logs` | Teak logs | 6333 | 35 | 105.0 |
| `arctic_pine_logs` | Arctic pine logs | 10810 | 42 | 125.0 |
| `maple_logs` | Maple logs | 1517 | 45 | 135.0 |
| `mahogany_logs` | Mahogany logs | 6332 | 50 | 157.5 |
| `eucalyptus_logs` | Eucalyptus logs | 12581 | 58 | 193.5 |
| `yew_logs` | Yew logs | 1515 | 60 | 202.5 |
| `magic_logs` | Magic logs | 1513 | 75 | 303.8 |
| `curly_root` | Curly root | 21350 | 75 | 161.6 |
| `cursed_magic_logs` | Cursed magic logs | 13567 | 82 | 303.8 |

`items.yml` confirms `Ashes` as item 592. It also confirms the input item IDs
above. `Cursed magic logs` are non-tradeable in the local item config, so
AnkiScape preserves that item metadata.

## Runtime Translation

`firemaking.plugin.kts` wires tinderbox-on-item, ground-item option, and
tinderbox-on-ground-item to `FiremakingAction.burnLog`. AnkiScape deliberately
models tinderbox as implicit because the add-on does not have a location/world
interaction layer, and introducing tinderbox inventory/toolbelt management would
be busywork without new gameplay choices.

`FiremakingAction.kt` removes one log when the action begins, repeatedly rolls a
lighting chance, spawns a fire on success, awards Firemaking XP, and later spawns
`Ashes x1` on the ground. AnkiScape translates that into one review-scale
attempt:

- if the player lacks level or the selected input item, the action cannot start;
- a successful attempt consumes one selected input, awards the source XP, and
  adds `Ashes x1` directly to inventory;
- a failed attempt consumes no input and awards no XP/items;
- quick-light timing, forced movement, map checks, fire objects, ground-item
  lifetime, and bank-area restrictions are out of scope for v1.

The source raw lighting roll uses `interpolate(low = 65, high = 513, level =
Firemaking level) > RANDOM.nextInt(255)`. `firemaking_data.py` stores those raw
low/high values, and `logic_pure.py` adapts them to AnkiScape's review cadence
with a tier curve so newly unlocked logs are slower while overlevelled logs
become comfortable.

## Added Assets

Fetched through `tools/fetch_firemaking_assets.py`, which uses the shared
`tools/fetch_assets.py` client and records provenance in
`assets_provenance.json`.

- `icon/firemaking_icon.png` from `Firemaking icon (detail).png`
- `firemakingitems/ashes.png`
- `firemakingitems/arctic_pine_logs.png`
- `firemakingitems/eucalyptus_logs.png`
- `firemakingitems/curly_root.png`
- `firemakingitems/cursed_magic_logs.png`

Normal logs, Achey logs, Oak logs, Willow logs, Teak logs, Maple logs, Mahogany
logs, Yew logs, and Magic logs reuse the existing Woodcutting log art.

## Deferred Follow-Up

Bonfires/fire spirits should be treated as a future Firemaking extension. A good
future slice would start with a small design note that decides how batch feeding,
XP bonus, fire-spirit rewards, Cooking boost, temporary-health warmth, and
review-action multiplier behavior interact with Anki undo.
