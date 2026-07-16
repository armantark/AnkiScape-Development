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

## Light-source extension — implemented 2026-07-09

`content/mechanics/lightsource/LightSource.kt` defines 11 raw-to-lit item pairs
with Firemaking requirements: 596→594 (1), 36→33 (1), 38→32 (1), 4527→4531
(4), 4532→4534 (4), 4522→4524 (12), 4535→4539 (26), 4548→4550 (49),
4701→4702 (49), 9064→9065 (49), and 5014→5013 (65). The rows are represented
as one-item, zero-XP Utility / Activities transformations with the tinderbox
implicit. Inventory labels include raw/lit state and, for the two same-name
Candle lantern variants, their cache ID, so no source states collide.

`light_source.plugin.kts` registers every lit product's `extinguish` option and
reverses that exact item pair. AnkiScape models all 11 inverse transforms with
no Firemaking gate, as in the source. It deliberately omits the Lumbridge Swamp
Caves region guard, dark-zone interface opening, and drop protection because
the add-on has no world-location, darkness, or ground-item model. Existing
checked-in sibling sprites are reused; no assets were fetched.

## Deferred Follow-Up

Bonfires/fire spirits should be treated as a future Firemaking extension. A good
future slice would start with a small design note that decides how batch feeding,
XP bonus, fire-spirit rewards, Cooking boost, temporary-health warmth, and
review-action multiplier behavior interact with Anki undo.

## Lantern item-state correction — 2026-07-16

The original light-source extension preserved distinct labels but copied two
incorrect raw IDs from game-main's `LightSource.kt`: an empty candle-lantern
frame (4527) was treated as directly lightable, and an empty oil lantern (4535)
was treated as fuelled. The producer graph also collapsed unfinished, empty,
fuelled-unlit, and lit items back onto the cache display name. Because
AnkiScape inventories are name-keyed, that made most lantern actions
unreachable and made the bullseye-lens recipe consume a lens while returning
the same inventory key.

The corrected identities are pinned by the rev-667 item config, the local
combination rows, Darkan commit `fab9b065dbf753e50e298eff8500256edf31fd75`,
and period wiki revisions:

- Candle lantern, oldid 5962978, 2012-07-20: 4527 empty frame, 4529/4532
  candle-inserted unlit states, and 4531/4534 lit states.
- Oil lamp, oldid 6359041, 2012-10-06: 4525 empty, 4522 fuelled-unlit, and
  4524 lit.
- Oil lantern, oldid 5372911, 2012-03-13: 4535 empty, 4537 fuelled-unlit, and
  4539 lit. The period page supplies Crafting level 26; game-main's level 50
  combination row conflicts and is not used.
- Bullseye lantern (empty), oldid 6524183, 2012-11-03: 4544 unfinished metal
  frame, 4546 lens-fitted empty, 4548 fuelled-unlit, and 4550 lit.
- Sapphire lantern, oldid 6092552, 2012-08-14: 4700 empty, 4701
  fuelled-unlit, and 4702 lit. Swapping a cut sapphire into the empty bullseye
  returns the ordinary lantern lens.
- Lamp oil, oldid 6241595, 2012-09-13: swamp tar is distilled in the lamp-oil
  still and used to fill an empty lamp or lantern.

Local implementation convergence:

- `CombinationData.kt` maps 4544 + lens to 4546, 4546 + emerald lens to 9064,
  and 4522 + lantern frame to 4537.
- Darkan `src/main/java/com/rs/game/content/world/LightSource.java` binds the
  light actions to 4529, 4522, 4537, 4548, and 4701 rather than the empty
  states.
- Darkan `data/npcs/drops/pickpocketing/pp_cavegoblin.json` drops 4537 and
  4548, confirming that the cave-goblin rewards are fuelled-unlit items.

### AnkiScape translation

Lamp-oil preparation is one zero-XP Utility / Activities review: the line says
that the player distils swamp tar and fills the selected empty light source,
consumes one swamp tar, and outputs the exact fuelled-unlit item. This flattens
the still interaction without introducing wall-clock time. Candle insertion is
the same one-review, zero-XP preparation shape. Lighting and extinguishing stay
separate one-review transformations so every state and undo boundary remains
legible.

Twenty-two distinct inventory sprites were fetched through
`tools/fetch_firemaking_assets.py`; `assets_provenance.json` records the modern
wiki file source used only for artwork. The gameplay identities and values come
from the period evidence above, not from the modern asset pages.

The same local light-source implementation maps Mining helmet 5014 to lit
Mining helmet 5013. Both states retain the source equipment block, head slot,
bonuses, Defence classification, and separate artwork. Exact-state registration
uses the equipment category rather than leaving these wearable items as generic
materials.

Save migration preserves every previously collapsed inventory key. The old
generic Mining helmet is also renamed while equipped, and touched Miltog stock
rows plus their rollback records are canonicalized by stable shop-row ID. Some
old name-keyed saves are intrinsically ambiguous: a generic Oil lamp could have
represented either cache ID 4522 or 4525. Migration resolves that legacy key to
the empty 4525 state, matching the old Crafting output and preserving the full
preparation chain; new acquisitions preserve the exact cache state.
