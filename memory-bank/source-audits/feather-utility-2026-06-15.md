# Feather Utility Source Audit

## Status

P2 feather source completed on 2026-06-15. This is a narrow Utility/Activities
bridge for Fletching, not the final Combat or Grand Exchange source.

## Primary Sources

Local 2011Scape rev 667 source under `/Users/ArmanTarkhanian1/Downloads/game-main`:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/ranged_instructor.plugin.kts`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/chicken_level_1.plugin.kts`
- `data/cfg/items.yml`

## Source Facts

- The Lumbridge Ranged instructor explains the Fletching chain as: smith arrow
  heads, get feathers from chickens, add feathers to arrow shafts to make
  headless arrows, then add arrow heads.
- The chicken drop table has guaranteed `Bones` and `Raw chicken`, plus a main
  feather table: 64/128 slots for `Feather x5`, 32/128 slots for `Feather x15`,
  and 32/128 slots for no feather drop.
- `items.yml` item id `314` is `Feather`, tradeable, with the examine text
  "Used for fly fishing."

## Implemented AnkiScape Route

`UTILITY_ACTIVITY_DATA["scavenge_chicken_feathers"]` is a no-XP Utility/Activities
action:

- Display: `Scavenge chicken feathers`
- Requirements: none
- Output: `Feather x1`
- Batch size: `28`
- Review result: one successful activity action grants `28 Feather`
- Source note: temporary scavenging bridge from the chicken feather source until
  Combat drops and/or the Grand Exchange exist.

## Scope Decisions

- No Combat was added.
- No shop, coin, or GE behavior was added.
- No `Bones` or `Raw chicken` side drops were added, even though they are in the
  chicken drop table, because that would open Prayer/Cooking/combat inventory
  commitments outside P2.
- Fletching recipe definitions were not changed. Arrowtips remain owned by
  Smithing.

## Future Replacement

When Combat exists, chicken kills should become the source-faithful feather
route and can include the full chicken drop table. When the GE exists, feathers
can also become a tradable market item. This Utility action can then be removed,
left as a low-friction scavenging route, or rebalanced.
