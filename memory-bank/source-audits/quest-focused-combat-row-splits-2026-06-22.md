# Quest focused combat row splits - 2026-06-22

## Scope

This slice reduces generated combat rows that were blocked by parser/name-shape
issues, without editing `quest_catalog_generated.py` directly.

## Source-backed changes

- Heroes' Quest keeps the historical `Entrana Fire Bird (level 2)` row from
  <https://runescape.wiki/w/Heroes'_Quest?oldid=6534275>, and replaces the
  generated statless encounter with Darkan's local
  `data/npcs/combatdefs/uncategorized/entrana_firebird.json` payload. Darkan
  `developer-information/npcList.txt` identifies NPC id 6108 as
  `Entrana firebird (2)`.
- Spirits of the Elid keeps the historical `Three level 75 Golems` row from
  <https://runescape.wiki/w/Spirits_of_the_Elid?oldid=6326193>, but splits the
  generated generic encounter into Black golem, White golem, and Grey golem.
  Darkan `developer-information/enums.txt` enum 2791 ties those three NPCs to
  `Quest: Spirits of the Elid`, and local Darkan combatdefs supply resolver
  stats/configs for each named golem.
- Another Slice of H.A.M. keeps the historical `H.A.M. ranger (level 30)` row
  from <https://runescape.wiki/w/Another_Slice_of_H.A.M.?oldid=6548739>.
  Darkan names the ranged level 30 NPC `H.A.M. Archer` (NPC id 5859), with
  local combatdef `data/npcs/combatdefs/uncategorized/h.a.m._archer (noanims).json`
  and `developer-information/beasts.txt` backing the resolver payload.

## Implementation notes

- `quest_data.py` now allows one focused combat replacement to expand into
  multiple `QuestCombatEncounter` rows. This preserves the generated
  noncombat stage rows for the quest while replacing only the ambiguous combat
  encounter.
- The new data raises audit coverage from 164/285 to 169/287 resolver-ready
  combat rows. The row total increases because one generic Spirits golem row
  becomes three named golem encounters.
- The statless backlog is now 118 rows: 51 Darkan hitpoints-only metadata rows,
  18 Darkan rows missing style-critical resolver stats, 9 same-name/wrong-level
  rows, 13 no-local-source rows, and 27 parser/variant-level rows.

## Deferred

This is not full quest parity. Remaining work still includes exact per-stage
placement audits, route/branch/puzzle/follower state, quest-item
transformations, source reconciliation for ambiguous combat variants, and full
combat simulation.
