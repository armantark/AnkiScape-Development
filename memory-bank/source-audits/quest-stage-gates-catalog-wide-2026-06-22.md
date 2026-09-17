# Quest Stage Gates Catalog-Wide Source Audit - 2026-06-22

## Status

This pass broadens the stage-gate model across the generated pre-EOC quest
catalog, but it still does not complete minute-detail parity for every quest.
The important change is that the generator now preserves machine-readable
quest-wide item/tool/alternative requirements and combat encounter rows from
pre-EOC `Quest details` fields instead of leaving those facts only in prose.

Coverage from `python3 tools/audit_quest_stage_gate_coverage.py`:

- 194 total pre-EOC quest rows.
- 179 quests with at least one machine-readable stage requirement.
- 331 generated/runtime stage requirement rows.
- 163 quests with item, tool, or item-alternative blockers.
- 112 quests with combat blockers.
- 274 combat encounter rows.
- 15 combat encounter rows matched local 2011Scape NPC combat stats.

Follow-up note: `memory-bank/source-audits/quest-stage-no-stage-closure-2026-06-22.md`
closed the explicit no-stage list later on 2026-06-22. The current audit tool
state after that follow-up is 194/194 quests with at least one
machine-readable stage requirement, 382 runtime stage rows, 119 quests with
combat blockers, and 0 quests without stage requirements.

## Source Policy Used

- Primary catalog fields are pinned RuneScape Wiki revisions before the
  2012-11-20 EOC cutoff.
- Journal stage placement still prefers local 2011Scape quest-stage source when
  available, then quick-guide checklist lines, then walkthrough prose.
- Local 2011Scape NPC definition files under
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions`
  are used to enrich generated combat encounters with hitpoints, attack,
  strength, defence, magic, ranged, attack speed, attack style, and defensive
  bonuses when a name/level match is available.
- OSRS sources were not used for this pass.

## Backend Changes

- `tools/build_pre_eoc_quest_catalog.py` now extracts `items` and
  `kills`/`combat` from pre-EOC `Quest details` templates.
- Generated stage requirements can express:
  - `required_inventory`
  - `required_inventory_options`
  - `required_tools`
  - `combat_encounters`
- The parser skips recommended/optional/not-required item and combat prose where
  it can identify that safely, and it models simple coin/item alternatives such
  as `Beer or 2 coins`.
- `quest_data.py` deserializes generated stage rows into
  `QuestStageRequirement` and richer `QuestCombatEncounter` rows.
- `logic_pure.py` adds a global
  `player_data["quest_combat_config"]["resolver_enabled"]` switch. It defaults
  to `False`, so all incomplete combat encounters fail closed as
  `combat_locked` blockers. The follow-up resolver contract in
  `memory-bank/source-audits/quest-combat-resolver-contract-2026-06-22.md`
  adds the first stat-backed write path, but no-stats rows still remain blocked.
- Storage config version 20 seeds and migrates `quest_combat_config`,
  `quest_combat_encounters`, `quest_stage_actions`, and `quest_route_states`.

## Frontend Changes

- The Quests tab continues to consume the backend lifecycle states:
  `can_start`, `in_progress`, `blocked_at_stage`, `completed`, and `locked`.
- Generated combat blockers surface through the same compact current-stage
  blocker display used by The Knight's Sword item blockers.
- A Qt/offscreen test now proves Demon Slayer displays the generated combat lock
  and disables the quest action while combat is globally disabled.

## Explicit Remaining Gaps

This pass is not the final "every quest down to the most minute detail" goal.
The generated layer is catalog-wide, but it is still quest-wide source-field
extraction, not a completed hand audit of every stage action.

Known gaps:

- The 15-row no-stage list from this pass was closed by
  `memory-bank/source-audits/quest-stage-no-stage-closure-2026-06-22.md`.
  Do not reopen those rows merely because this earlier note lists the prior
  state.
- Exact per-stage placement still needs manual/source-backed audit for many
  quests. The generator infers item stages from journal text and otherwise uses
  a conservative stage row; it does not prove minute-by-minute quest scripting.
- Combat is represented as hard blockers and optional battle metadata. The
  first resolver contract can complete current-stage stat-backed encounters,
  but most generated encounters still cannot legitimately pass because they
  lack local NPC stats or quest-specific combat mechanics.
- Route-specific branches, partner requirements, cat/companion state, subquest
  choices, quest-specific item transformations, and action-family requirements
  remain backlog items unless already captured by a hand override.

## Manual Anki Test Instructions

Use a throwaway Anki profile or back up the current AnkiScape save first.

1. Open AnkiScape and go to the Quests tab.
2. Start Cook's Assistant with no Bucket and no Empty pot. Confirm the quest is
   startable but current progress is blocked with missing item reasons.
3. Add Bucket and Empty pot to the save/inventory, resume Cook's Assistant, and
   confirm the quest can progress and still awards its generated item rewards
   only on completion.
4. Start Demon Slayer and set its progress to the Delrith stage in a test save.
   Confirm the quest card shows `Blocked: Combat locked until battle support is
   enabled: Delrith level 27`, the action button is disabled, and Hide unable to
   start does not hide the started quest.
5. Confirm The Knight's Sword still blocks at Thurgo without Redberry pie,
   consumes the pie when supplied, blocks later on Blurite ore plus two Iron
   bars, and awards 12,725 Smithing XP only on valid completion.
6. Do not enable `quest_combat_config.resolver_enabled` in a live save until the
   remaining combat stat enrichment and combat-simulation scope are acceptable
   for that save.

## Verification

- `python3 -m unittest tests.test_quest_catalog tests.test_logic tests.test_storage_pure`
- `python3 -m unittest tests.test_runtime_actions tests.test_integration_smoke`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_stage_blockers_without_hiding_started_quests tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_demon_slayer_item_stage_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_lists_stage_items_before_knights_sword_start`
- `python3 tools/audit_quest_stage_gate_coverage.py`

## Chronology moved from systemPatterns.md — 2026-09-16

### Quest stage and branch rollout

Original line range: 428-643.

- Stage-aware quest requirements live in `QuestDefinition.stage_requirements` data, serialized by `quests_as_dict()` and enforced by pure helpers in `logic_pure/logic_pure.py`. Use `quest_current_stage_blockers_pure()` / `quest_current_stage_blocker_reasons_pure()` for display, `can_progress_quest_pure()` for review readiness, and `apply_quest_progress_pure()` for stage advancement and stage-local consumed/produced items. The first proof case is The Knight's Sword: Mining 10 remains a start requirement, Redberry pie is consumed at Thurgo's stage, Blurite ore plus two Iron bars are consumed at the later Thurgo materials stage, and the 12,725 Smithing XP reward fires only on valid completion. A later 2011Scape starter batch added `produced_inventory` for quest intermediates such as Druidic Ritual enchanted meats, Pirate's Treasure chest key/message, and Vampyre Slayer stake/stake hammer. A follow-up intermediate batch added `start_inventory` and source-backed produced/consumed chains for Rune Mysteries, The Restless Ghost, and Lost City, including Ghostspeak amulet, Muddy skull, Air talisman, Research package, Research notes, Dramen branch, and Dramen staff. Demon Slayer is now a Darkan-backed focused replacement: it uses a nine-stage internal model so bucket water, 25 bones, three Silverlight keys, Silverlight, Delrith, and the incantation all gate at their source-backed stages before completion. Dragon Slayer is now a Darkan/local-2011Scape-backed focused replacement: 32 quest points remains the start lock, then Oziach, Guildmaster, anti-dragon shield, Melzar's Maze combat, Wormbrain's paid map piece, Oracle items, Crandor map assembly, Lady Lumbridge purchase/repair, Ned's route, Elvarg, and the Oziach report are separate current-stage gates. `QuestStageRequirement.variant` now models mutually exclusive route rows on the same stage; rows with no variant are mandatory, and route-matched variant rows are the only branch rows that can block, consume, produce, or resolve combat. Shield of Arrav proves this with Phoenix Gang and Black Arm Gang branches, Jonny the beard and Weaponsmaster combat gates, route-specific shield/certificate halves, and the partner half-certificate combine stage. Fight Arena now proves a Darkan-backed non-branch replacement where disguise production/equipment, Khali brew purchase/consumption, key theft/use, mandatory arena fights, and the Lady Servil return are stage gates rather than start locks. The Quests tab may show "Used during quest" item requirements before start, but those items must not block starting unless the source says they are start requirements.
- Branch and co-op quest decisions use structured `QuestDefinition.choices`, not fake inventory requirements. `quest_current_stage_choices_pure()` reports unresolved player choices, `apply_quest_route_choice_pure()` writes the selected route to flat `quest_route_states`, and started quests expose a `quest_choice` blocker until the choice is made. Shield of Arrav, Heroes' Quest, Temple of Ikov, Hazeel Cult, and The Void Stares Back are the current choice-backed coverage set. Shield/Heroes single-player co-op pieces are contextual contacts: Black Arm Shield no longer asks for manual Phoenix-partner key actions, Shield certificate merging consumes only the player's own duplicate half, and Heroes' Phoenix mansion route no longer requires a manual Black Arm partner action. Heroes' Quest inherits the Shield of Arrav route when it exists, with a fallback stage-9 choice for older saves. Hazeel Cult no longer grants both branch artifacts as unconditional completion rewards.
- Witch's House now supersedes its earlier two-row combat proof with a full
  12-stage Darkan-backed chain: potted-plant Door key, door entry, cupboard
  Magnet, Cheese/Magnet mouse-hole mechanism, witch patrol route, Leather gloves
  electric gate, fountain Backroom key, shed door, four experiment forms, Ball
  pickup, and Harvey hand-in. Cheese is consumed at the mouse stage, Ball is
  consumed only at Harvey, and 6,325 Constitution XP remains pending until that
  skill exists.
- Merlin's Crystal is an 8-stage Darkan/local-2011Scape focused replacement. It
  keeps quest-used items out of start locks, routes through the round-table
  investigation and Catherby crate, resolves Sir Mordred as a source-backed
  combat encounter, then gates Morgan questioning, Bucket/Insect repellent wax,
  Bucket of wax to Black candle, Bread to Excalibur, Bat bones/Black candle plus
  Tinderbox, Excalibur crystal smash, and King Arthur report at their current
  stages. Stage 8 is the completed state, so the ritual, crystal smash, and
  Arthur report all live on stage 7. Thrantax is intentionally an action/dialogue
  gate, not a combat gate, because local Darkan binds him through ritual dialogue.
- Generated combat source matching is token-safe, not raw substring based.
  `tools/build_pre_eoc_quest_catalog.py` supports explicit aliases such as
  `Poisonous Spider` -> `Poison Spider`, and singularizes plural source names as
  full tokens only. Temple of Ikov's generated `Guardians of Armadyl` row now
  resolves to Darkan's level 45 `Guardian of Armadyl` combatdef, and Observatory
  Quest's `Poisonous Spider` resolves to local 2011Scape's level 31 `Poison
  Spider`. This also prevents false positives such as `Bear` matching `Johnny
  The Beard`. `Lvl 2 Goblins` now parses as `Goblins`, but remains a
  missing-stats blocker because the local goblin source has ID-dependent
  attack/defence expressions.
- `tools/build_pre_eoc_quest_catalog.py` also emits generated quest-wide
  stage blocker rows from pre-EOC `Quest details` item and combat fields.
  Generated rows can carry `required_inventory`, `required_inventory_options`,
  `consumed_inventory`, `consumed_inventory_options`, `produced_inventory`,
  `required_tools`, and `combat_encounters`; option groups must preserve
  alternatives instead of flattening them into separate hard requirements.
  The outer option tuple is conjunctive and each inner tuple is disjunctive:
  `((A, B),)` means A or B, while `((A,), (B,))` means A and B.
  `quests_as_dict()` emits each inner group as a tuple of item-count mappings;
  reachability tooling must merge those mappings within the group instead of
  passing the whole tuple to the flat item-count parser. Focused callers can
  also pass the native dataclass tuple-pair shape, so audit parsers must preserve
  both representations.
  When the source predicate needs mixed family quantities, a compound bundle,
  an excluded family member, worn equipment/follower/performed state, or an equivalent-item
  capability that the schema cannot express, remove the false item gate and
  report the missing predicate instead of narrowing valid source paths.
  `data/quest_data.py`
  deserializes them into the same `QuestStageRequirement` contract used by hand
  overrides. `logic_pure/logic_pure.py` treats consumed option groups as current-stage
  blockers and consumes the first satisfied option group when the stage
  advances. Produced inventory is not a blocker by itself; it is the
  source-backed item state created by a successful current-stage transition.
  `data/quest_data.py` then combines generated rows, hand-authored stage rows,
  focused replacement rows, and focused addition rows; use replacements when
  generated data conflicts with stronger 2011Scape/Darkan evidence, and use
  additions when a source-backed quest action exists but the generated item or
  combat parser cannot infer it. `tools/audit_quest_stage_gate_coverage.py` reports every catalog quest with
  at least one stage requirement, and the Priest in Peril focused override
  fixes its generated stage-61/prose-parser row into nine source-backed stages.
  The 2011Scape starter batch then replaced bad generated rows for Cook's
  Assistant, Imp Catcher, Druidic Ritual, Pirate's Treasure, and Vampyre Slayer.
  Quest-only products must be produced by earlier quest stages before a later
  hand-in consumes or requires them; Cook's Assistant proves this by producing
	  Super large egg, Top-quality milk, and Extra fine flour in stages, with only
	  Bucket and Empty pot acting as external inventory blockers. Common items
	  bought or obtained as part of the same quest should be action-modeled instead
	  of shown as quest-wide inventory gates; easy deterministic steps belong in
	  `auto_actions` so review progression records them without blocking, while
	  true player/manual gates stay in `required_actions`. Vampyre Slayer's Blue
	  Moon Inn talk/beer path is the proof case, while its Stake and Stake hammer
	  are produced by Dr Harlow.
	  `tools/audit_quest_local_item_gates.py` enforces the narrow invariant that
	  quest-wide `Used during quest` requirements must not list items produced by
	  that same quest or granted by its `start_inventory`. The 2026-06-24 sweep
	  removed those misleading broad gates from The Restless Ghost, Ernest the
	  Chicken, Pirate's Treasure, Dragon Slayer, Witch's House, Heroes' Quest,
	  Fight Arena, and Rune Mysteries while preserving their current-stage blockers.
	  The same produced-item rule now protects Clock Tower rat poison/cogs, Monk's
	  Friend blanket, Dwarf Cannon railings/remains/Nulodion items, Sheep Herder
  cattleprod/bones, and Biohazard's rotten apple. Partner-supplied quest items
  should follow the same
  principle without pretending the player already owns the item: Shield of
  Arrav's Black Arm weapon-store key is modeled as Phoenix-partner action gates
  that produce the key and crossbows when the stage advances. Generated rows
  that misclassify route/location/skill/prose text as inventory or tools belong
  in the focused cleanup layer in `data/quest_data.py`, not in start locks or
  direct edits to `generated/quest_catalog_generated.py`.
  The 2011Scape intermediate batch then replaced The Restless Ghost, Rune
  Mysteries, and Lost City with local source-backed item/action/route/combat
  chains. The Demon Slayer focused replacement then moved bucket water, bones,
  Silverlight keys, Silverlight, Delrith, and incantation requirements out of a
  broad generated combat row. The early Darkan stage batch then replaced Goblin
  Diplomacy, Ernest the Chicken, and Black Knights' Fortress with source-backed
  item/action chains, and `logic_pure._has_quest_tool()` now lets quest-required
  tools be satisfied by worn equipment for disguise stages. Dragon Slayer then
  replaced its broad generated row with source-backed gates for the anti-dragon
  shield, map pieces, Oracle items, Lady Lumbridge repair, Ned route, and Elvarg
  report. Shield of Arrav then replaced the generated branch prose with a
  route-variant stage chain for Phoenix Gang and Black Arm Gang, including
  partner half-certificate exchange as a finish-stage gate instead of a start
  lock. Fight Arena then replaced generated all-in-one requirements with a
  12-stage Darkan-backed chain for Khazard disguise production/equipment,
  Jeremy/lazy guard actions, Khali brew purchase/consumption, cell-key
  production/use, Khazard ogre, Khazard scorpion, Bouncer, and Lady Servil
  reward. Witch's House then superseded the old combat-only proof with a
  12-stage Darkan-backed chain for keys, Magnet, Cheese, witch patrol, Leather
  gloves, experiment forms, Ball pickup, and Harvey hand-in. A local Darkan
  quest-stage batch then replaced Fishing Contest, Gertrude's Cat, Clock Tower,
  Monk's Friend, Tribal Totem, and Scorpion Catcher with focused item/action/
  route chains. It proves that generated detail rows should be replaced when
  local quest handlers provide finer item transformations: fishing pass and
  trophy stages, milk bucket and doogle sardine stages, Clock Tower cog
  placement, Cedric supply stages, RPDT label/totem stages, and scorpion-cage
  stages all advance independently instead of being flattened into start locks.
  Sheep Herder then proves the same pattern for noncombat animal-disposal
  quest stages: poisoned sheep feed is produced and retained, Doctor Orbon's
  clothing is bought mid-quest, the cattleprod and coloured sheep bones are
  produced before later stages require or consume them, and the clothing remains
  a reusable tool gate. Plague City
  then proves that generated item rewards can be narrowed when stronger local
  stage evidence produces a quest item mid-quest: the gas mask is produced by
  Alrena and only `A magic scroll` remains a final item reward. Waterfall Quest
  proves that future combat-skill XP rewards stay structured in
  `pending_skill_exp_rewards` while the stage chain still handles book/key,
  Glarial item, rune, amulet, and urn gates. Biohazard then proves the same
  focused replacement pattern on a longer route chain: Jerico/Omart wall
  routing, Bird feed and Pigeon cage production/use, rotten-apple stew poisoning,
  Doctors' gown production, the level 13 Mourner, Distillator recovery, Elena's
  reagent vials, chemist Touch paper, errand-boy smuggling, Priest gown x2 for
  Guidor, and Elena/King Lathas reports are all current-stage gates. Heroes'
  Quest then proves a long branch-and-proof replacement: Blamish oil and oily
  fishing rod preparation, raw/cooked lava eel handling, Ice Queen/Ice gloves,
  Entrana Fire feather, Black Arm/Phoenix route-variant candlestick rows,
  armband exchange, and final Achietties proof items are current-stage gates.
  The Ice Queen lair access is a route blocker rather than a mandatory Jailer
  combat row because the source allows a Dusty key route or Agility shortcut.
  Family Crest then proves a source-backed long item-transformation chain where
  cooked fish, perfect gold ore/bars, perfect ruby jewellery, crest pieces,
  Johnathon's antipoison, Chronozon's blast-spell combat, and the final Family
  crest hand-in all gate at their current stages while Crafting 40, Magic 59,
  Mining 40, and Smithing 40 remain start locks. Temple of Ikov then proves a
  true ending branch: the Fire Warrior requires ice arrows plus one compatible
  bow option, Winelda consumes 20 Limpwurt roots, the Guardian route produces an
  Armadyl pendant and requires Lucien combat, and the Lucien route requires a
  Guardian encounter before the Staff of Armadyl is consumed at the final hand-in.
  Holy Grail and Tree Gnome Village then prove focused replacement rows can
  correct generated false positives and source-only unlocks: Holy Grail removes
  the false Brimhaven requirement, keeps Excalibur as the Black Knight Titan
  stage tool, splits Magic whistle/Holy grail production and consumption before
  the final King Arthur hand-in, and Tree Gnome Village consumes six logs,
  models tracker actions, two Khazard commanders, the Khazard warlord, orb/orbs
  hand-ins, and Gnome amulet reward while leaving spirit tree access as an
  unlock. A final all-catalog pass then made generated stage rows fail closed
  with source-backed action/checkpoint blockers for every pre-EOC catalog quest,
  fixed generated combat heading false positives, preserved prefix quantities
  such as `3x Warped terrorbirds` and `4x Living rock brawler`, split Shilo
  Village's Nazastarool into three sourced forms, set Legends' Quest's
  Nezikchened to three kills, and added focused resolver-ready Tough guy and
  Black Dragon rows. A 2026-06-23 cleanup pass then removed generated
  pseudo-inventory blockers such as Lletya, Oronwen, Tears of Guthix cavern,
  Crafting table 3, Agility Pyramid, Rimmington, Love Story, Thieving, Mining,
  Monkey Madness route items, generated teleport/tablet travel text, literal
  quest-name blockers, generated spell names, broad Food/Armour checklist text,
  and other parser-shaped blockers from inventory/tool fields. Rat Catchers now
  makes rat poison from Hooknosed Jack's ingredients during its stage, Dwarf
  Cannon completion now leaves a represented Ammo mould source for later
  cannonball and quest gates, bucket-of-sap uses are action gates, Within the
  Light's keys/crystal puzzle objects are action-gated, and The Fremennik
  Isles yak-hide armour/round shield prep is modeled as current-stage actions.
  The census (quests, stage rows, item, tool, action, route, and combat
  blockers, produced-inventory rows, resolver-ready combat rows) comes from
  `python3 tools/audit_quest_stage_gate_coverage.py`; the figures move with
  every quest slice, so this file does not carry them.
  This is all-catalog machine-readable stage-gate coverage, not proof of
  minute-detail historical simulation for every quest.
  Use
  `tools/audit_quest_stage_gate_coverage.py`,
  `memory-bank/source-audits/quest-stage-gates-catalog-wide-2026-06-22.md`, and
  `memory-bank/source-audits/quest-stage-no-stage-closure-2026-06-22.md`, plus
  `memory-bank/source-audits/quest-priest-in-peril-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-2011scape-starter-stage-batch-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-2011scape-intermediate-stage-batch-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-demon-slayer-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-early-darkan-stage-batch-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-dragon-slayer-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-shield-of-arrav-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-fight-arena-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-witchs-house-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-merlins-crystal-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-dwarf-cannon-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-generated-combat-name-matching-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-local-noncombat-stage-batch-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-sheep-herder-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-plague-city-waterfall-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-heroes-quest-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-family-crest-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-holy-grail-tree-gnome-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-all-catalog-stage-gate-final-2026-06-22.md`
  before claiming a quest-stage pass is complete.
