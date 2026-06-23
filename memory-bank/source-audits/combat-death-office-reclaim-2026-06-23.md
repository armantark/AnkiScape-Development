# Combat Death Office Reclaim Audit - 2026-06-23

## Scope

Implement the next Combat V1 death/recovery slice from
`memory-bank/combat-design-grill-2026-06-23.md`: stacked PvM deaths must not
silently overwrite an active AnkiScape grave, and gear that falls out of the
active grave path must be reclaimable from Death's Office for Coins.

## Source Evidence

| Field | Evidence |
| --- | --- |
| Primary 2011Scape source | `game/src/main/kotlin/gg/rsmod/game/action/PlayerDeathAction.kt` |
| 2011Scape finding | Player death restores skills, returns the player to a home/instance-exit tile, sets lifepoints to maximum, and invokes the player-death plugin hook. The local 2011Scape checkout does not include a full gravestone/item-retention plugin. |
| Equal implementation source | `src/main/java/com/rs/game/content/death/GraveStone.java`, `src/main/java/com/rs/game/content/death/DeathOfficeController.java`, `src/main/java/com/rs/game/model/entity/player/Player.java`, and `src/main/java/com/rs/game/content/interfacehandlers/ItemsKeptOnDeath.java` in local Darkan/2012scape |
| Darkan finding | PvM death computes kept/dropped item slots, resets inventory/equipment, returns kept items, and either creates a `GraveStone` for dropped items or drops them directly. Creating a new gravestone for a player finishes the old one and adjusts its items' remaining public/delete time. The death controller presents a Death Office respawn/hub flow before calling `sendPVEItemsOnDeath`. |
| AnkiScape design source | Combat grill decisions 14-16 and 99 |
| AnkiScape adaptation | AnkiScape currently risks equipped items only. The active grave remains the five non-Again review recovery path. A second Combat death while that grave is active moves the prior grave items into flat `death_office` state before creating the new grave. Reclaim returns office-held items to inventory after consuming Coins. |

## Implemented Contract

- `combat_grave.items` remains the active five-review recovery list.
- `death_office.items` is an additive flat save field for collapsed/expired
  grave items waiting on paid reclaim.
- A stacked death moves any active grave items into Death's Office before the
  new death's equipped items become the active grave.
- Death's Office reclaim is intentionally a small AnkiScape bridge fee of 100
  Coins per item until a source-backed value table is audited.
- Reclaim returns items to inventory, not equipment, matching the existing
  AnkiScape grave recovery behavior and avoiding forced re-equips.

## Exclusions

- Wilderness item-retention behavior remains deferred.
- Source exact Death's Office fee scaling is not implemented in this slice.
- Prayer-based grave blessing/repair is deferred with Prayer proper.
- Wall-clock grave expiry is not modeled; review progress and stacked deaths
  are the active AnkiScape loss/reclaim paths for now.
