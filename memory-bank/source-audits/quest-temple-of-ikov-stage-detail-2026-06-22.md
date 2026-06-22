# Temple of Ikov Stage Detail Audit - 2026-06-22

## Scope

Source-backed focused replacement for `temple_of_ikov`, replacing the generated
start-flattened item/combat row with machine-readable current-stage gates.

## Sources

- Local 2011Scape item identity:
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`
- Local 2011Scape guardian chamber spawns:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/spawns/spawns_10650.plugin.kts`
- Darkan quest implementation:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/templeofikov/TempleOfIkov.java`
- Darkan dungeon objects/routes:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/templeofikov/IkovDungeon.java`
- Darkan Fire Warrior damage rule:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/templeofikov/FireWarrior.java`
- Darkan Lucien and dialogue branches:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/templeofikov/LucienVarrockMob.java`
  and the `dialogues/*TempleOfIkov.java` files under the same quest folder.
- Darkan NPC combat stats:
  `data/npcs/combatdefs/uncategorized/fire_warrior_of_lesarkus.json`,
  `data/npcs/combatdefs/uncategorized/guardian_of_armadyl/guardian_of_armadyl_(45).json`,
  and `data/npcs/combatdefs/uncategorized/lucien/lucien_(14) (noanims).json`.
- Historical wiki cross-check:
  `https://runescape.wiki/w/Temple_of_Ikov?oldid=6538747`.

## Implemented Backend

- `quest_data.py` now overrides `temple_of_ikov` with 11 stages and 12
  requirement rows because stages 9 and 10 have Lucien/Guardian variants.
- Strict startability remains separate from finishability: the only start skill
  lock is Thieving 42. The light source, knife, bow, limpwurt roots, lever, ice
  arrows, pendants, Staff of Armadyl, and combat are current-stage blockers.
- Lucien's start dialogue produces `Pendant of lucien` through
  `start_inventory`; because Thieving is not implemented yet, tests use
  already-started saves for stage progression and keep the start lock strict.
- The Fire Warrior stage requires `Ice arrows` plus one yew/magic/dark bow
  option, then blocks on `Fire Warrior of Lesarkus` level 84 until combat is
  resolved.
- Winelda's lava route consumes 20 `Limpwurt root` at the correct stage.
- Guardian branch produces `Armadyl pendant`, then blocks on `Lucien` level 14.
- Lucien branch blocks on one `Guardian of Armadyl` level 45 before producing
  `Staff of armadyl`, then consumes the staff at the final hand-in.
- Completion grants the sourced `Shiny key` reward and the historical 10,500
  Ranged XP plus 8,000 Fletching XP.

## Implemented Frontend/Test Surface

- No custom frontend code was required; the existing Quests tab displays the new
  current-stage blockers through data-driven `blocked_at_stage` labels.
- Added Qt/offscreen coverage for the Fire Warrior bow-option blocker.
- Added asset registration and provenance-backed icons for the Temple quest
  items and bow variants, including the disambiguated `Lever` icon alias.

## Known Gaps

- Darkan blocks taking the Staff of Armadyl while any Guardian has line of sight;
  2011Scape spawns five Guardians in the chamber. AnkiScape models this as one
  required Guardian encounter because the exact minimum kill count is
  line-of-sight dependent rather than a fixed source-backed quantity.
- Full combat simulation remains gated behind the existing resolver config; the
  stage rows block rather than silently completing unresolved fights.
- Thieving is not implemented, so a new Temple of Ikov start remains locked even
  with `thieving_level` present. Already-started saves can still be progressed by
  the stage layer.

## Manual Anki Test Instructions

1. Open Anki with this add-on enabled, open the AnkiScape menu, and confirm
   Temple of Ikov is still unable to start while Thieving is not implemented.
   This verifies the strict start lock remains separate from stage gates.
2. In a disposable profile/save, seed an already-started Temple of Ikov state at
   progress 7 with `Ice arrows x1` and no yew/magic/dark bow. Open the Quests
   tab and confirm the row is `blocked_at_stage`, shows the missing bow option,
   and the quest action is disabled.
3. Add one compatible bow, leave combat unresolved, and confirm the row now
   shows the Fire Warrior combat lock rather than completing the stage.
4. Seed `quest_combat_encounters["temple_of_ikov"]` with
   `temple_of_ikov_fire_warrior_of_lesarkus_84`, answer one successful review,
   and confirm progress advances only to the Winelda stage.
5. Seed progress 10 on the Lucien route with `Staff of armadyl x1`, answer one
   successful review, and confirm the staff is consumed, `Shiny key x1` is
   awarded, quest points increment once, Fletching XP is applied once, and Ranged
   XP is stored as pending until Ranged exists.
6. Repeat the final check through the Guardian route by seeding the Armadyl
   pendant and Lucien combat flag; confirm completion is still one-time and does
   not also require the Staff hand-in.
7. Use Anki undo after one successful quest review and confirm inventory,
   progress, quest points, pending rewards, and combat flags roll back with the
   normal review snapshot.
