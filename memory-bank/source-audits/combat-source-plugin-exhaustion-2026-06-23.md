# Combat source plugin exhaustion audit - 2026-06-23

## Scope

After the TzHaar-Ket implementation pass, the local 2011Scape NPC definition
tree was scanned for plugin files containing `NpcCombatStats`:

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions`

The scan compared source filenames referenced by `COMBAT_ENEMY_DATA` against all
local plugin files with combat stats.

## Result

- Implemented source filenames referenced from `COMBAT_ENEMY_DATA`: 93
- Unimplemented local `NpcCombatStats` plugin files under the scanned source
  tree: 0

This exhausts the current local source-plugin row-copying pass for ordinary
Combat targets. It does not mean every possible RuneScape enemy is modeled.
Future Combat expansion now needs new mechanics or source surfaces rather than
more direct local `NpcCombatStats` imports.

## Remaining Combat Expansion Boundaries

- Enemy Ranged and enemy Magic strategies for rows whose behavior cannot be
  represented as melee attacks.
- Slayer/task/access gates and Slayer as a full gameplay loop.
- Quest and route-sensitive combat rows that belong behind stage-aware quest
  blockers or the shared quest combat resolver.
- Dragonfire, cannon, Prayer, player poison, specials, Wilderness risk, and
  other non-row systems identified in `memory-bank/combat-design-grill-2026-06-23.md`.
- External or later-source enemies not present as local 2011Scape
  `NpcCombatStats` plugins.
