# Future Work Kanban

Status: 2026-06-23

Use this board as the handoff source for near-term AnkiScape follow-up threads. It captures the current owner priorities after the Crafting/Fletching/Smithing parity pass.

## Current Decisions

- Arrowtips are not an unresolved source gap. They are smithable through Smithing.
- Feathers are no longer an unresolved Fletching input gap. P2 added a
  no-XP Utility/Activities bridge, `Scavenge chicken feathers`, on 2026-06-15.
- The NPC shop system and the Grand Exchange are valid future economy
  candidates, but neither is a high-priority next step. NPC shops are tracked
  separately in `memory-bank/npc-shop-design-seed.md`; the parked GE design
  remains in `memory-bank/fake-grand-exchange-design.md`.
- Dependency-heavy Crafting acquisition loops are intentionally deferred for now.
- Special Mining and Woodcutting content should stay parked for now.
- Firemaking v1 is complete as a separate skill-expansion thread; bonfires and fire spirits are deferred 2012 pre-EOC extension content.
- Fishing v1 is complete as a separate Gathering skill-expansion thread; Dungeoneering fish, Fishing Trawler, quest-only fish, Fish Flingers, and real shop/GE material sourcing are deferred system slices.
- Review-action telemetry and shared review-odds normalization are complete as of 2026-06-20. Future balancing work should use `player_data["action_telemetry"]` / `summarize_action_telemetry_pure` and tune the shared adapter first, not per-skill one-off Fishing odds.
- Fletching source integration is complete as of 2026-06-19. Do not re-add the
  old tiered arrow-shaft pilot rows; local 2011Scape only whittles normal logs
  into arrow shafts. Broad arrows/bolts are implemented behind the
  `broad_fletching` ability lock, and Barbarian Fishing uses the same
  `unlocked_abilities` substrate via `barbarian_fishing`. Crossbow limb
  attachment/stringing, enchanted bolts, and comp ogre bow stringing remain
  excluded unless a future audit finds live source evidence for the specific
  action and owner skill.
- Runecrafting v1 is complete as a separate Artisan skill-expansion thread; Magic Imbue, Wicked hood daily resources/teleports/reclaim, Abyss routing/abyssal creatures, talisman sourcing, and broader rune economy routes are deferred system slices.
- Hunter v1 is complete as a separate Gathering skill-expansion thread. The
  local 2011Scape cache/snapshot supplied item names/ids, but not a local Hunter
  mechanics plugin, so v1 uses 2011.rs guide rows plus local 2012scape/Darkan
  mechanics/id parity. Tracking trails, pitfall trapping, rabbit snaring,
  barehand catches, Herblore Habitat/Jadinkos, grenwall herb drops, and
  Regicide-start partial-route modeling are deferred system slices.
- Quest-lock registry and full pre-EOC quest catalog completed on 2026-06-17, with route-precedent locks added on 2026-06-18, Quests-tab availability filters added on 2026-06-19, and stage-aware quest blockers completed across all 194 catalog quests on 2026-06-22. The Knight's Sword is the start-vs-finish proof case, Dwarf Cannon proves source-backed false-positive combat removal with a noncombat stage chain, the local Darkan batch for Fishing Contest, Gertrude's Cat, Clock Tower, Monk's Friend, Tribal Totem, and Scorpion Catcher proves focused item/action/route replacements for quests whose generated detail rows are too broad, Sheep Herder proves stage-local noncombat disposal gates for poisoned sheep feed, clothing/tools, and four sheep-bone incinerations, Plague City/Waterfall Quest prove mid-quest reward correction plus future-skill pending XP through detailed stage chains, Biohazard proves a longer West Ardougne route/item/combat/smuggling chain with the Mourner hard-blocked unless combat resolving is enabled, Heroes' Quest proves a long branch-and-proof chain with strict start locks, stage-local lava eel/Fire feather/armband proof items, Black Arm/Phoenix route variants, and no forced Jailer route, and the final all-catalog pass proves every quest now has machine-readable current-stage blockers rather than a start-only completion path. Do not redo the priority gates, the 194-row catalog, the completed filter surface, or the completed focused quest replacements; use `memory-bank/quest-unlock-audit-2026-06-17.md`, `memory-bank/source-audits/quest-all-catalog-stage-gate-final-2026-06-22.md`, and the focused quest source audits for future route/location, stage-aware, or combat-aware quest work.
- Quest-stage status artifacts were paused during the owner-requested all-quest
  update. Source-audit markdown and Memory Bank maintenance still continue as
  normal project guidance; create new visual status artifacts only when the
  owner explicitly asks for one or the next scoped feature requires it.
- Combat V1 implementation is complete as of 2026-06-23 for the first
  source-backed ordinary-combat slices: Chicken, Rat, Spider, Giant rat, Giant
  spider, Cow, Cow calf, Ram, Highwayman, and Seagull are selectable Combat
  targets; review bursts simulate 50 source ticks per
  `Actions per review` step; melee attack styles route damage XP into Attack,
  Strength, Defence, shared controlled XP, and Constitution; auto-eat consumes
  real food; drops follow the imported guaranteed/multi-table/quantity-range semantics; the
  Combat hub and HUD surface target/style/lifepoint state; and storage defaults
  persist combat state. The recovery/loadout foundation now adds finite carried
  food, safe-boundary loadout refills, review-tick special-energy regeneration,
  stat-drain recovery scaffolding, status-effect save hooks, and Combat tooltip
  food readiness. Use `memory-bank/combat-design-grill-2026-06-23.md` plus
  `memory-bank/source-audits/combat-v1-implementation-2026-06-23.md` before
  expanding Combat. Next Combat work should widen source-backed enemies,
  complete ranged/magic/ammo/rune routing, add player-facing loadout controls,
  improve grave/Death's Office recovery, and migrate quest combat gates onto
  the same engine instead of reopening the completed design grill.
- The Tutorial Island starter kit bridge is complete as of 2026-06-23. It uses a
  one-time `tutorial_island_starter_kit` Bank Claim with generic `item_bundle`
  support and grants only the source-backed tutorial handout items. See
  `memory-bank/source-audits/combat-tutorial-starter-kit-2026-06-23.md`.
- Cow calf, Ram, Highwayman, and Seagull are now implemented ordinary Combat targets as of
  2026-06-23. They were chosen first because their local 2011Scape rows have
  complete stats, simple guaranteed drops, death handlers, attack speed, and no
  quantity-range or nested-table runtime requirements. Spider and level-2 Giant
  spider are now implemented too after adding charm assets and Combat
  `quantity_range` support. Highwayman now uses that range support for Iron
  bolts x2-12 and registers Cape as a source-backed equipment drop. Goblins,
  Barbarians, Farmers, Al-Kharid warriors, and higher-risk spider variants need
  wider item/drop-table, variant, access, or special-mechanic support.
- P0 review-action dispatch cleanup is complete as of 2026-06-15: `action_registry.py` resolves skill and Utility/Activities handler keys, and runtime can-start checks are handler-keyed. Do not repeat this dispatch slice.
- P0 flat target-list metadata cleanup is complete as of 2026-06-16, grouped target-tree metadata cleanup is complete as of 2026-06-19, runtime handler extraction is complete as of 2026-06-19, and achievement metadata/final handler-plumbing cleanup is complete as of 2026-06-19: `target_metadata.py` drives Mining, Woodcutting, Fletching, Firemaking, Fishing, Smithing, Crafting, Cooking, Runecrafting, and Utility/Activities row labels, tooltips, icon paths, groups, sort order, enabled/current state, and lock reasons before Qt renders them; `runtime_actions.py` owns review-action mutation bodies and handler-keyed can-start checks; `achievement_metadata.py` owns achievement definitions, grouping, and progress helpers while preserving the legacy save/name contract. The current P0 architecture board is closed; do not continue P0 by default unless the owner names a new concrete architecture boundary.
- Utility and Activities have their own icon set for current rows, including the Fishing bait bridge.

## Priority Board

### P0 - Existing Skill Architecture And Old Debt (Complete)

User story: As a future skill implementer, I want existing skill and activity behavior to be driven by registry metadata and shared action plumbing, so adding the next skill does not require editing scattered UI, runtime, and review-dispatch branches.

Why now: The repo has enough real skills to reveal recurring pressure in skill selection UI, target-list metadata, stats rendering, action dispatch, icon registration, storage shape, and achievements. Cleaning this up before the next broad skill makes every future expansion cheaper.

Backend scope:

- Audit current Mining, Woodcutting, Fishing, Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Quests, and Utility/Activities paths.
- Continue moving action behavior and target-list metadata behind registries instead of per-skill hardcoding.
- Keep the current flat save format unless a specific refactor proves it must change.
- Preserve current XP, item, undo, and review behavior.

Frontend scope:

- Remove hardcoded skill assumptions only where the backend contract can already describe the screen.
- Keep existing visual behavior stable unless the refactor explicitly supports a cleaner display contract.
- Leave clear handoff notes if backend metadata is ready but the UI migration should happen separately.

Acceptance criteria:

- Existing Mining, Woodcutting, Fishing, Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Quest, and Utility flows behave the same after the refactor.
- The review answer path still resolves actions through the intended handler key.
- Existing tests pass, and targeted tests cover any changed registry/action dispatch behavior.
- Future skill or Firemaking-extension threads have fewer places to edit than the previous broad skill-expansion threads.

Status 2026-06-19: Complete for the current P0 architecture board. Initial
backend dispatch, flat target-list metadata, grouped target-tree metadata,
runtime handler extraction, achievement metadata, and final duplicated
handler-plumbing cleanup are all done. No storage shape, XP, item, undo, action
multiplier, recipe data, target data, asset, frontend UI, achievement name,
completion-semantics, or quest rule behavior changed. Mining, Woodcutting,
Fletching, Firemaking, Fishing, Smithing, Crafting, Cooking, Runecrafting, and
Utility/Activities now share pure row-metadata contracts. Mining, Woodcutting,
Fletching, Firemaking, and Fishing use one Qt `QListWidget` renderer; Smithing,
Crafting, Cooking, and Runecrafting use one grouped `QTreeWidget` renderer.
`runtime_actions.py` owns review-action mutation bodies and handler-keyed
can-start checks; `achievement_metadata.py` owns achievement definitions,
difficulty grouping, and progress helpers; `__init__.py` keeps hooks, global
state, undo snapshots, UI/save callbacks, and thin compatibility wrappers.
Verification passed with `python3 run_tests.py` at 352 tests (84 skipped) and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` at
352 tests. Hunter was added later and now also participates in the same
runtime, target-row, achievement, item, and skill-registry patterns.

Future thread prompt:

```text
In the AnkiScape repo, use memory-bank/future-work-kanban.md as the source of truth. Do not continue P0 by default: the current architecture board is complete as of 2026-06-19 across review-action dispatch, flat target-list metadata, grouped target-tree metadata, runtime handler extraction, achievement metadata, and final duplicated handler-plumbing cleanup. Only reopen P0 if the owner explicitly names a new concrete architecture boundary and acceptance criteria. Keep backend and frontend work explicitly split, preserve the flat save model unless unavoidable, add targeted tests, update the Memory Bank, and commit the result.
```

### P1 - Quest Lock Registry And Copy-Forward Skill

Status 2026-06-17: Complete for the priority unlocks identified by
`memory-bank/quest-unlock-audit-2026-06-17.md`. Rune Mysteries, Lost City, Tai
Bwo Wannai Trio, Mourning's End Part II, Swan Song, Lunar Diplomacy, and Legacy
of Seergaze are now playable Quest rows. `QUEST_UNLOCK_RULES` owns the strong
completion gates for Mining rune essence, Runecrafting cosmic/astral/death/blood
targets, Fishing monkfish/karambwan, Shilo Village `gem_rocks`, and the narrow
route-precedent locks for Priest in Peril Morytania rows and The Fremennik Isles
Neitiznot/yak/arctic pine rows. Quest starts are strict: unimplemented
prerequisite quests or skills block starting rather than being approximated. XP
rewards for unimplemented skills are stored in
`pending_skill_exp_rewards` and auto-applied by migration once those skills are
implemented.

Status 2026-06-22: Stage-aware quest requirements now exist as a real backend
and frontend foundation, not just a future note. The Knight's Sword is the first
source-backed proof case: it preserves the Mining 10 start lock, shows
Redberry pie, Blurite ore, and two Iron bars as quest-used requirements before
start, blocks the current stage when those items are missing, consumes the pie
at Thurgo's stage, consumes the later materials at Thurgo's replica-sword stage,
and grants 12,725 Smithing XP only on legitimate completion. A follow-up
catalog-wide generator pass now extracts quest-wide pre-EOC item/tool/option
requirements and combat encounters into machine-readable stage blockers for
179/194 quest rows, with 112 quests carrying combat blockers. A no-stage
closure follow-up then added focused source-backed replacement/addition rows so
the audit reports 194/194 quests with at least one stage requirement and 119
quests carrying combat blockers. Combat is hard locked by the global flat save
config `player_data["quest_combat_config"]["resolver_enabled"] == False` until
combat support is explicitly enabled. A first resolver contract now writes one
current-stage stat-backed encounter id per Quest review via
`apply_quest_combat_encounter_pure()`, but only when local NPC stats exist and
the player's 2011Scape-formula combat level is high enough; no-stats combat
rows remain blocked. A focused follow-up enriched The Restless Ghost Skeleton
Warlock from local 2011Scape quest/object/NPC definitions, proving focused
`quest_data.py` additions can become resolver-ready without hand-editing the
generated catalog. A generator follow-up then added Darkan/2012scape combat-def
fallback parsing after local 2011Scape precedence, using exact unambiguous
name+level matches only and raising stat-backed combat coverage to 141/286
rows; Delrith and Elvarg are the proof cases. A combat-quantity follow-up now
parses written combat quantities in the generator and stores partial encounter
progress in `quest_combat_encounter_counts`, so multi-enemy rows require one
Quest review per sourced enemy before their compatibility id is written to
`quest_combat_encounters`. TokTz-Ket-Dill's sourced "Two Lava monsters" row is
the proof case. A second combat-stat follow-up
accepted exact duplicate Darkan rows only when all captured battle stats/configs
match and added focused override stats for Jogre and the Sea Troll Queen,
raising coverage to 147/286. This slice then fixed generated item-option
grouping across the catalog and resolved the conflicting Priest in Peril Monk
of Zamorak plus Troll Stronghold Dad rows with focused area-specific Darkan
quest/combat evidence, raising resolver-ready coverage to 149/286. The
Witch's House follow-up then replaced an ambiguous generated experiment row
with four source-backed Darkan form encounters, raising resolver-ready coverage
to 153/285. A style-aware resolver follow-up then taught the generator,
runtime, and audits to accept source-backed magic/ranged encounters with zero
melee Strength when `attack_style` is magic/range, while retaining a complete
melee fallback for inconsistent source style metadata. This added resolver-ready
H.A.M. mage, The Void Stares Back Torcher/Defiler, and The Elder Kiln
TokHaar-Xil rows, raising resolver-ready coverage to 157/285. The Darkan
beast-stat fallback follow-up then merged exact/unambiguous `beasts.txt`
attack/defence/magic/ranged evidence into generated Darkan combatdefs only when
those values fill missing or zero stats and the existing attack-style resolver
contract is satisfied. It makes TokTz-Ket-Dill's ranged Lava monster and
Nomad's Requiem's ranged Nomad rows resolver-ready while leaving melee rows
without sourced Strength blocked, raising resolver-ready coverage to 159/285.
The no-`combatLevels` beast-stat follow-up then allowed generated Darkan
hitpoints/config rows to merge exact name/level `beasts.txt` signatures, and
merged multi-id Darkan files per matched name/level only. It makes the Chaos
dwarf hand cannoneer, Caitlin, Pit scabarite, Forgotten mage, and Forgotten
ranger rows resolver-ready while leaving mismatched/ambiguous Fire monster,
Elder Kiln Lava monster, and Pit iron dragon rows blocked, raising
resolver-ready coverage to 164/285. The remaining 121 statless combat rows are
classified by `tools/audit_quest_combat_stat_gaps.py` as 51 Darkan hitpoints-only metadata
rows, 18 Darkan rows missing
style-critical resolver stats, 9 same-name/wrong-level rows, 16 no-local-source
rows, and 27 parser/variant-level rows. A focused replacement follow-up then
made generated name-shape rows source-backed without touching
`quest_catalog_generated.py`: Heroes' Quest's Entrana Fire Bird now uses local
Darkan `entrana_firebird.json`, Spirits of the Elid's generic `Golem x3` row
splits into Black, White, and Grey golems using Darkan enum/combatdef evidence,
and Another Slice of H.A.M.'s historical H.A.M. ranger row maps to Darkan's
level 30 H.A.M. Archer ranged combat payload. That raises resolver-ready
coverage to 169/287, with 118 statless combat rows remaining: 51 Darkan
hitpoints-only metadata rows, 18 Darkan rows missing style-critical resolver
stats, 9 same-name/wrong-level rows, 13 no-local-source rows, and 27
parser/variant-level rows. A focused full-stage A Soul's Bane replacement then
removed bad generated anger-room combat rows, kept the rage room as a
required-action gate, split the later Fear reaper/Confusion beast/Hopeless
creature/Tolna head fights into sourced Darkan multi-count combat gates, and
made Death to the Dorgeshuun's Senior H.A.M. guard x3 row resolver-ready from
local Darkan H.A.M. Guard stats. That slice's resolver-ready coverage was 174/283,
with 109 statless combat rows remaining: 51 Darkan hitpoints-only metadata rows,
18 Darkan rows missing style-critical resolver stats, 9 same-name/wrong-level
rows, 12 no-local-source rows, and 19 parser/variant-level rows. A Priest in
Peril focused full-stage replacement then removed its generated stage-61/prose
rows, corrected it to nine playable stages, added consumed alternative support
for the Salve essence step, moved the Temple guardian dog and Monk of Zamorak
combat gates to their real stages, and kept Wolfbane/1,406 Prayer XP behind
valid completion. A 2011Scape starter-quest batch then added
`produced_inventory` stage transitions and replaced bad generated rows for
Cook's Assistant, Imp Catcher, Druidic Ritual, Pirate's Treasure, and Vampyre
Slayer: Cook's Assistant produces its quest-only cake ingredients in quest
stages and only blocks on Bucket/Empty pot before the final hand-in consumes
them, Imp Catcher consumes only the four beads and no longer grants generated
coins, Druidic Ritual transforms raw meats into enchanted meats before Sanfew/Kaqemeex,
Pirate's Treasure produces Chest key and Pirate message, and Vampyre Slayer
produces stake/stake hammer, keeps garlic optional, resolves Count Draynor at
stage 3, consumes the stake after the battle gate, and requires the Morgan
report before Attack XP. A 2011Scape intermediate batch then added
`start_inventory` and replaced The Restless Ghost, Rune Mysteries, and Lost City
with local source-backed stage chains: Ghostspeak amulet and Muddy skull are
produced/consumed at the Restless Ghost stages, Rune Mysteries now grants Air
talisman at start and transforms it through Research package and Research notes
without false XP, and Lost City now routes through Shamus, Entrana, Tree spirit,
Dramen branch, and Dramen staff without duplicating the staff reward. A
Demon Slayer focused replacement then moved the quest out of the old broad
Delrith row: stage 1 consumes the coin, stage 3 consumes bucket water and
produces the drained key plus bucket, stage 4 consumes 25 bones and produces
Traiborn's key, stage 5 produces Rovin's key, stage 6 converts the three keys
into Silverlight, stage 7 requires Silverlight and Delrith, and stage 8
requires the incantation before the stage 9 completion marker. Post-slice audit
reports 401 stage rows, 80 focused rows, 321 generated rows, 283 combat
encounters, and 175 resolver-ready combat encounters, with 14
produced-inventory rows. The Temple guardian dog remains blocked as
`combat_missing_stats` after the global combat lock because Darkan supplies
hitpoints/max-hit/magic immunity but no nonzero attack/strength/defence payload.
A follow-up early Darkan stage batch then replaced Goblin Diplomacy, Ernest the
Chicken, and Black Knights' Fortress with focused source-backed stage chains:
Goblin mail hand-ins are consumed at their real stages, Ernest's fish food/poison
and machine parts are produced and consumed through Oddenstein's flow, and Black
Knights' Fortress uses the sourced 12 quest point start requirement plus
worn-equipment disguise support before the cabbage sabotage and Sir Amik report.
A Dragon Slayer focused replacement then moved Oziach/Guildmaster actions,
anti-dragon shield, Melzar's Maze combat, Wormbrain's paid map piece, Oracle
items, Crandor map assembly, Lady Lumbridge purchase/repair, Ned route, Elvarg,
and the final Oziach report into source-backed current-stage gates. Shield of
Arrav then added route-variant branch rows so Phoenix Gang and Black Arm Gang
requirements do not leak into each other: Jonny the beard and Weaponsmaster are
source-backed combat gates, route-specific shield/certificate halves are
produced and consumed at their real stages, and the partner half-certificate
exchange remains a finish-stage gate instead of a start lock. A Fight Arena
focused replacement then replaced generated all-in-one requirements with a
12-stage Darkan-backed chain: Khazard disguise production/equipment,
Jeremy/lazy guard actions, Khali brew purchase/consumption, cell-key
production/use, Khazard ogre, Khazard scorpion, Bouncer, and Lady Servil
reward. Ogre/scorpion remain missing resolver stats; Bouncer is resolver-ready;
General Khazard is optional. Post-slice audit reports 449 stage rows, 285
combat encounters, 177 resolver-ready combat encounters, 174 quests with
item/tool blockers, and 120 quests with combat blockers.
Witch's House then superseded the earlier two-row combat proof with a full
12-stage Darkan-backed replacement: potted-plant Door key, door entry, cupboard
Magnet, Cheese/Magnet mouse-hole mechanism, witch patrol route, Leather gloves
electric gate, fountain Backroom key, shed door, four experiment forms, Ball
pickup, and Harvey hand-in. The experiment forms were already resolver-ready, so
combat coverage stays 177/285; post-slice audit reports 458 stage rows, 42
produced-inventory rows, 285 combat encounters, 174 quests with item/tool
blockers, and 120 quests with combat blockers.
Merlin's Crystal then replaced generated front-loaded item/combat prose with an
8-stage Darkan/local-2011Scape chain: round-table investigation, Catherby crate
route, Sir Mordred combat, Morgan questioning plus beehive wax collection, black
candle exchange, Lady of the Lake/Port Sarim beggar bread test, and a final
stage-7 ritual/crystal/Arthur gate before the stage-8 completion marker. Bucket,
Bucket of wax, Black candle, Bread, Bat bones, and the ritual candle are consumed
or produced at their source-backed stages; Excalibur is produced during the quest
and retained. Thrantax remains a ritual dialogue/action gate because local Darkan
binds him through dialogue rather than combat. Post-slice audit reports 463 stage
rows, 46 produced-inventory rows, 285 combat encounters, 177 resolver-ready
combat encounters, 174 quests with item/tool blockers, and 120 quests with combat
blockers.
The generated combat parser/source-matching follow-up then made NPC name
matching token-safe, added the safe `Poisonous Spider` -> `Poison Spider` alias,
singularized plural source names only as whole tokens, and parsed level-prefixed
rows such as `Lvl 2 Goblins`. Temple of Ikov's Guardians of Armadyl and
Observatory Quest's Poisonous Spider are now resolver-ready from local source
data. At that point, Dwarf Cannon's level-2 Goblins row carried the right
display name and partial local 2011Scape source metadata, but remained blocked
because the source uses ID-dependent attack/defence expressions.
Post-slice audit reports 463 stage rows, 46 produced-inventory rows, 285 combat
encounters, 179 resolver-ready combat encounters, 174 quests with item/tool
blockers, 120 quests with combat blockers, and 106 statless combat rows.
Dwarf Cannon then added thirteen source-backed noncombat gate rows plus a 14th
completion state: Lawgof's railing grant, rail repairs, Lawgof report, Gilob's
remains pickup and hand-in, goblin hideout route, Lollk rescue, toolkit
production, cannon repair, Nulodion item grant and hand-in, and Lawgof's final
recommendation. This removes the false live Goblins combat row, sets Dwarf
Cannon's combat summary to `None.`, and registers the relevant quest item icons.
A local Darkan quest-stage batch then replaced generated/broad rows
for Fishing Contest, Gertrude's Cat, Clock Tower, Monk's Friend, Tribal Totem,
and Scorpion Catcher. It models fishing pass/fee/garlic/giant-carp/trophy
transforms, Gertrude's milk/doogle/kittens flow, Clock Tower rat poison and
cogs as quest-produced items before consumption, Monk's Friend blanket/Cedric
supplies, Tribal Totem RPDT label/totem flow, and Scorpion Catcher scorpion cage
plus the level 39 jailer combat gate.
Sheep Herder then replaced the generated quick-guide row with Darkan-backed
poisoned feed, Doctor Orbon clothing, cattleprod production, coloured sheep-bone
production/incineration, and Councillor Halgrive report gates.
Plague City and Waterfall Quest then replaced generated/broad rows with
Darkan-backed stage chains for gas-mask production, Edmond sewer entry,
Rehnison/Bravek prison access, hangover cure, warrant/key rescue, Baxtorian
book, Golrie, Glarial's tomb items, rune/amulet waterfall completion, and
pending Attack/Strength XP.
Post-slice audit reports 519 stage rows, 68 produced-inventory rows, 285 combat
encounters, 180 resolver-ready combat encounters, 174 quests with item/tool
blockers, 120 quests with combat blockers, and 105 statless combat rows.
Biohazard then added a 13-stage Darkan-backed chain for Jerico/Omart wall
routing, Bird feed and Pigeon cage production/use, rotten-apple stew poisoning,
Doctors' gown production, the level 13 Mourner, Distillator recovery, Elena's
reagent vials, chemist Touch paper, errand-boy smuggling, Priest gown x2 for
Guidor, and Elena/King Lathas reports. Heroes' Quest then replaced generated
front-loaded proof rows with a 13-stage source-backed chain for Blamish oil,
oily fishing rod, raw/cooked lava eel, Ice Queen/Ice gloves, Entrana Fire
feather, Black Arm/Phoenix candlestick variants, Thieves' armband, and the
final Achietties hand-in. The Ice Queen lair stays a route blocker rather than
a forced Jailer combat row because the source allows alternate access.
Family Crest then replaced generated front-loaded item/combat prose with a
16-stage source-backed chain for Caleb's cooked fish, Avan's perfect-gold ruby
jewellery, Boot/Witchaven perfect gold routing, Johnathon's antipoison,
Chronozon's all-four-blast-spell combat, crest-piece combination, and the final
Dimintheis hand-in. Temple of Ikov then replaced generated start-flattened item
and combat prose with an 11-stage, 12-row source-backed chain for Lucien's
pendant, light-source entry, web/Boots of lightness, lever and ice-arrow route,
Fire Warrior bow/ammo combat, Winelda's 20 limpwurt-root teleport,
Guardian/Lucien branch rows, Staff of Armadyl hand-in, Lucien combat, and Shiny
key reward. Holy Grail and Tree Gnome Village then replaced generated broad rows
with focused local Darkan stage chains: Holy Grail removes the false Brimhaven
item, keeps Excalibur as the Black Knight Titan stage tool, produces and
consumes Magic whistles/Holy grail at the correct stages, and stores Defence/
Prayer XP as pending rewards; Tree Gnome Village consumes six normal logs,
requires three tracker-coordinate actions, models two Khazard commander
encounters plus the Khazard warlord, consumes the orb/orbs hand-ins, and keeps
Spirit Tree access as an unlock rather than a bank reward. Post-Holy/Tree audit
reports 577 stage rows, 104 produced-inventory rows, 286 combat encounters, 181
resolver-ready combat encounters, 174 quests with
item/tool blockers, 120 quests with combat blockers, and 105 statless combat
rows.
The final all-catalog pass then updated generated stage rows so every catalog
quest has at least one source-backed current-stage gate, parser heading false
positives are skipped, prefix combat quantities are preserved, Shilo Village's
Nazastarool forms are split, Legends' Quest's Nezikchened quantity is sourced,
The Feud has a Tough guy combat row, and Recipe for Disaster: Freeing Sir Amik
Varze has a resolver-ready Black Dragon row. A quest-only item cleanup then
ensured same-quest products are produced before later stage consumption for
Cook's Assistant, Clock Tower, Monk's Friend, Sheep Herder, Biohazard, and Dwarf
Cannon, with a regression invariant for the stage graph. A 2026-06-23 follow-up
then fixed Shield of Arrav's Black Arm partner key handoff, removed
parser-shaped pseudo-inventory/tool blockers from generated rows, made Rat
Catchers produce rat poison from Hooknosed Jack's ingredients during the stage,
represented Dwarf Cannon completion as an Ammo mould source for later gates,
and removed the follow-up route/spell/quest-name/broad-checklist parser artifacts
from inventory/tool fields.
A later 2026-06-23 branch-choice pass added machine-readable `QuestDefinition`
choices plus UI buttons for Shield of Arrav, Heroes' Quest, Temple of Ikov,
Hazeel Cult, and The Void Stares Back. It keeps the single-player model
contextual: Shield/Heroes no longer require manual partner key/co-op actions,
Shield certificate merging consumes only the player's own route half, Heroes can
inherit the Shield route, Hazeel no longer grants both side artifacts
unconditionally, and started quests with unresolved choices block as
`quest_choice` instead of silently progressing.
Current audit output is 194/194 quests with stage requirements, 1,120 stage rows,
121 produced-inventory rows, 288 combat encounters, 185 resolver-ready combat
encounters, 174 quests with item/tool blockers, 190 quests with action blockers,
32 quests with route blockers, 120 quests with combat blockers, and 103 statless
combat rows.
The source-backed start-only completion bug class is closed across the catalog:
unfocused quests now stop on generated current-stage blockers instead of
silently completing. Full minute-detail historical simulation, exact generated
per-dialogue extraction, broader quest-item transformations, route flags,
partner/branch state, puzzle state, broad combat stat enrichment, and full
combat simulation remain future work; those gaps fail closed through blockers
and are tracked in
`memory-bank/source-audits/quest-all-catalog-stage-gate-final-2026-06-22.md`.
The low-reasoning subagent audit's impossible-item and parser-pseudo-item cases
are no longer live inventory blockers after the 2026-06-23 cleanup. Live sweeps
now report zero same-quest products required before production, zero route/skill
phrase blockers in inventory/tool fields, and zero literal quest-name blockers.
Remaining minute-detail backlog is source replacement for generated broad rows
and external/prerequisite item reclaim routes whose current-stage action
blockers are intentionally coarse. Do not silently remove real source-backed
item requirements just because acquisition is not implemented; convert only
audited parser text, partner handoffs, or same-quest products into action,
route, consumed, and produced stage data.

User story: As a future quest implementer, I want quest unlock rules recorded in
one auditable pattern, so adding Lost City, Swan Song, Tai Bwo Wannai Trio, and
similar gates does not require scattered per-skill guesswork.

Why now: Rune Mysteries proved a small Quest/Claim state model and revealed that
some existing targets already need quest gates, while others are only
location-route checks. Copying the wrong pattern would over-lock Cooking,
Smithing, and future acquisition routes.

Backend scope:

- Start from `memory-bank/quest-unlock-audit-2026-06-17.md`.
- Add quest definitions before adding gates.
- Prefer a small quest-lock registry for completion gates.
- Use `quest_completed_pure` for completion unlocks only.
- Keep route/location gates and quest-stage recipes out of global target locks
  until their state model exists, except when the current generic target
  effectively represents the locked route.
- First candidates: Rune Mysteries -> Mining `rune_essence`, per-altar
  Runecrafting gates, Swan Song -> `catch_monkfish`, and Tai Bwo Wannai Trio ->
  `catch_karambwan`.

Frontend scope:

- Surface quest lock reasons from backend target-row metadata after pure logic is
  in place.
- Preserve grouped Runecrafting row behavior while showing independent quest
  locks for standard rune, tiara, and hood-feed rows.
- Do not add bespoke route-gate UI; promoted route precedents should surface as
  normal disabled rows with concise quest-name tooltips.

Acceptance criteria:

- Quest completion locks block and unblock the intended targets without changing
  unrelated level/material/undo behavior.
- Cooking range checks and Doric's anvil checks are not copied into global
  Cooking or Smithing target locks.
- Target rows show quest names clearly when locked.
- Unit, integration, Qt, and manual smoke coverage prove at least one locked and
  one unlocked path per migrated skill family.

Legacy replacement prompt before the Witch's House full-stage replacement
(superseded by the current prompt below):

```text
In the AnkiScape repo, do not redo the 2026-06-17 priority quest-lock registry pass, the full pre-EOC quest catalog, the 2026-06-19 Quests-tab availability filters, the 2026-06-22 The Knight's Sword stage-gate proof slice, the catalog-wide generated blocker pass, the no-stage closure pass, the first quest-combat resolver contract, the combat-quantity count slice, the historical-wiki remaining combat stat audit, the Priest in Peril full-stage replacement, the 2011Scape starter batch for Cook's Assistant, Imp Catcher, Druidic Ritual, Pirate's Treasure, and Vampyre Slayer, the 2011Scape intermediate batch for The Restless Ghost, Rune Mysteries, and Lost City, the Demon Slayer focused stage replacement, the early Darkan stage batch for Goblin Diplomacy, Ernest the Chicken, and Black Knights' Fortress, the Dragon Slayer focused stage replacement, the Shield of Arrav route-variant focused replacement, the Fight Arena focused stage replacement, Merlin's Crystal, Dwarf Cannon, the local noncombat Darkan batch, or the Sheep Herder focused stage replacement. `quest_catalog_generated.py` already contains 194 pre-EOC quest rows available before the 2012-11-20 EOC cutoff, with Recipe for Disaster split into separate subquests, generated by `tools/build_pre_eoc_quest_catalog.py`; Rune Mysteries, Lost City, Tai Bwo Wannai Trio, Mourning's End Part II, Swan Song, Lunar Diplomacy, Legacy of Seergaze, Shilo Village, Priest in Peril route-precedent rows, and The Fremennik Isles route-precedent rows are current gates. Runtime quest data now reports 194/194 quests with at least one machine-readable stage requirement, 501 stage rows, produced-inventory stage transitions, quest-start inventory grants, required-action blockers, route blockers, route-variant branch rows, grouped item-option blockers, globally locked combat blockers, and a resolver-enabled path that resolves one sourced enemy per Quest review via `quest_combat_encounter_counts` before writing legacy completed encounter ids. Current combat stat coverage is 180/285 rows after local 2011Scape-first, Darkan/2012scape exact name+level generator enrichment, identical duplicate-source acceptance, focused Jogre/Sea Troll Queen stats, area-specific Monk of Zamorak/Dad conflict resolution, the focused Witch's House four-form replacement, the style-aware magic/ranged resolver/generated rows for H.A.M. mage, The Void Stares Back Torcher/Defiler, The Elder Kiln TokHaar-Xil, the conservative Darkan `beasts.txt` fallback for TokTz-Ket-Dill's Lava monster plus Nomad's Requiem's Nomad, the no-`combatLevels`/level-aware Darkan beast-stat fallback for Chaos dwarf hand cannoneer, Caitlin, Pit scabarite, Forgotten mage, and Forgotten ranger, focused name-shape replacements for Heroes' Quest Entrana Fire Bird, Spirits of the Elid Black/White/Grey golems, Another Slice of H.A.M.'s H.A.M. ranger, A Soul's Bane's Fear/Confusion/Hopelessness/Tolna split, Death to the Dorgeshuun's Senior H.A.M. guard quantity row, Lost City's local Tree spirit stats, Demon Slayer's Delrith focused stage row, Dragon Slayer's focused Elvarg plus Melzar's Maze rows, Shield of Arrav's Jonny the beard plus Weaponsmaster route fights, Fight Arena's Bouncer stage row, and Scorpion Catcher's jailer stage row; 105 statless rows remain blocked and classified by `tools/audit_quest_combat_stat_gaps.py`, including Fight Arena's Khazard ogre and Khazard scorpion. `tools/audit_quest_historical_wiki_combat_stats.py` checked those remaining rows against pinned historical RuneScape Wiki monster pages and found metadata-only pages or no monster metadata, so LP/max-hit/style prose must not be merged as combat-ready stats. `tools/audit_quest_stage_gate_coverage.py` reports the current exact coverage/gap set. The Quests tab filters completed quests, unable-to-start quests, Access, Difficulty, Length, and Timeline via `quest_availability_state_pure()`, and started quests can now surface `blocked_at_stage` for machine-readable stage blockers. Only reopen this area for remaining minute-detail per-stage extraction, source reconciliation, route/location gates, quest-item transformations, unresolved branch/partner state beyond the current Shield variant model, new quest-unlocked skill targets, remaining combat stat enrichment from a new source class, full combat simulation, reward/journal generator corrections, or source corrections. Preserve strict quest starts, keep stage requirements separate from start locks, keep combat globally locked by default, keep no-stats combat rows blocked even when the resolver is enabled, keep unimplemented-skill XP in pending_skill_exp_rewards, split backend/frontend work explicitly, add targeted tests plus Qt/manual smoke coverage, update the Memory Bank, and commit.
```

Current replacement prompt:

```text
In the AnkiScape repo, do not redo the 2026-06-17 priority quest-lock registry
pass, the full pre-EOC quest catalog, the 2026-06-19 Quests-tab availability
filters, the 2026-06-22 The Knight's Sword stage-gate proof slice, the
catalog-wide generated blocker pass, the no-stage closure pass, the first
quest-combat resolver contract, the combat-quantity count slice, the
historical-wiki remaining combat stat audit, the Priest in Peril full-stage
replacement, the 2011Scape starter batch, the 2011Scape intermediate batch, the
Demon Slayer focused stage replacement, the early Darkan stage batch, Dragon
Slayer, Shield of Arrav, Fight Arena, Witch's House, Merlin's Crystal, the
generated combat name-matching parser pass, or the Dwarf Cannon focused
noncombat replacement, or the local Darkan batch for Fishing Contest,
Gertrude's Cat, Clock Tower, Monk's Friend, Tribal Totem, and Scorpion
Catcher, the Sheep Herder focused stage replacement, the Plague City and
Waterfall Quest focused stage replacements, or the Biohazard focused stage
replacement, the Heroes' Quest focused stage replacement, or the Family Crest
focused stage replacement, the Temple of Ikov focused stage replacement, the
Holy Grail/Tree Gnome Village focused stage replacement, the final all-catalog
stage-gate pass, the quest-only item cleanup pass, or the branch/co-op choice
pass for Shield of Arrav, Heroes' Quest, Temple of Ikov, Hazeel Cult, and The
Void Stares Back. `quest_catalog_generated.py` already contains 194 pre-EOC
quest rows available before the 2012-11-20 EOC cutoff, with Recipe for Disaster
split into separate subquests, generated by `tools/build_pre_eoc_quest_catalog.py`.
Runtime quest data now reports 194/194
quests with at least one machine-readable stage requirement, 1,120 stage rows, 121
produced-inventory transitions, quest-start inventory grants, required-action
blockers, route blockers, route-variant branch rows, grouped item-option
blockers, globally locked combat blockers, structured `quest_choice` route
decisions, and a resolver-enabled path that resolves one sourced enemy per Quest
review via `quest_combat_encounter_counts` before writing legacy completed
encounter ids. Current combat stat coverage is
185/288 resolver-ready rows; 103 statless rows remain blocked and classified by
`tools/audit_quest_combat_stat_gaps.py`. `tools/audit_quest_historical_wiki_combat_stats.py` checked
remaining rows against pinned historical RuneScape Wiki monster pages and found
metadata-only pages or no monster metadata, so LP/max-hit/style prose must not
be merged as combat-ready stats. `tools/audit_quest_stage_gate_coverage.py`
reports the current exact coverage/gap set. The Quests tab filters completed
quests, unable-to-start quests, Access, Difficulty, Length, and Timeline via
`quest_availability_state_pure()`, and started quests can surface
`blocked_at_stage` for machine-readable stage blockers and compact route-choice
buttons. Only reopen this area
for remaining minute-detail per-stage extraction, source reconciliation,
route/location gates, quest-item transformations, finer per-side Hazeel/Void
stage detail, new quest-unlocked skill targets,
remaining combat stat enrichment from a new source class, full combat
simulation, reward/journal generator corrections, or source corrections.
Preserve strict quest starts, keep stage requirements separate from start locks,
keep combat globally locked by default, keep no-stats combat rows blocked even
when the resolver is enabled, keep unimplemented-skill XP in
pending_skill_exp_rewards, split backend/frontend work explicitly, add targeted
tests plus Qt/manual smoke coverage, update the Memory Bank, and commit.
```

### P1 - Utility And Activities Icon Set

User story: As a player, I want Utility and Activities rows to have purpose-built icons, so non-XP support actions feel intentional instead of like second-class placeholders.

Why now: Utility and Activities are already part of the active loop, but their presentation lags behind skill content. A small icon pass improves polish without reopening deferred acquisition systems.

Backend scope:

- Ensure Utility/Activities actions expose stable icon keys or item/category artwork paths.
- Avoid turning this into new gameplay logic unless the icon contract requires a small metadata addition.
- Record asset provenance in the Memory Bank or source audit notes.

Frontend scope:

- Add or wire icons for current Utility/Activities actions such as soft clay preparation, flax/wool gathering, nest opening, and related support rows.
- Keep icons visually distinct from skill icons while matching existing asset style and size.
- Add graceful fallbacks for missing icon paths.

Acceptance criteria:

- Utility/Activities rows resolve to their own icons in the UI.
- Existing skill and item art remains unchanged.
- Tests or lightweight verification cover the metadata path used by the UI.
- Provenance is recorded for new art or source-derived assets.

Status 2026-06-15: Complete. Existing Utility/Activities rows now carry a
purpose-built `icon_path` contract backed by dedicated `activityicons/` PNGs
for soft clay, wool, flax, and bird-nest opening. The Skills-hub target list
prefers those activity icons and falls back to existing output-item art when an
icon path is missing. No reward logic, storage shape, XP behavior, or new
gameplay system changed. Asset provenance is recorded in
`assets_provenance.json`; verification passed with `python3 run_tests.py` and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`.

Future thread prompt:

```text
In the AnkiScape repo, use memory-bank/future-work-kanban.md as the source of truth. Work on P1: Utility and Activities icon set. Add a small, purpose-built icon contract and assets for existing Utility/Activities rows without adding new gameplay systems. Keep backend metadata and frontend display work explicitly split, verify the UI, update the Memory Bank, and commit the result.
```

### P2 - Feather Source For Fletching

Status 2026-06-15: Complete. `Scavenge chicken feathers` is a no-input,
no-XP Utility/Activities action that grants `28 Feather` per successful action.
It is source-backed by the local 2011Scape Ranged instructor and chicken drop
table, but deliberately omits Combat, shops, GE, bones, and raw chicken. See
`memory-bank/source-audits/feather-utility-2026-06-15.md`.

User story: As a Fletching player, I want a legitimate source for feathers, so arrow recipes can progress without seeded materials or a full economy feature.

Why now: Fletching is functional, and Smithing already supplies arrowtips. Feathers are the remaining obvious arrow-making input gap.

Backend scope:

- Pick one intentionally narrow feather source. A Utility/Activities action is the smallest likely path.
- Do not duplicate arrowtip acquisition, because Smithing already owns that loop.
- Keep this separate from broader Crafting acquisition loops unless the user reprioritizes them.

Frontend scope:

- Surface the chosen feather source in Utility/Activities or wherever the backend action contract places it.
- Reuse the Utility icon work if it already exists; otherwise add a simple specific icon path or fallback.

Acceptance criteria:

- Feathers can be acquired through one non-dev route.
- Arrowtip production remains owned by Smithing.
- Fletching recipe definitions do not need source hacks or free-material assumptions.
- Undo/action multiplier behavior is tested if the source is an activity action.

Future replacement prompt:

```text
In the AnkiScape repo, do not redo P2 feather sourcing. Feathers already have the temporary Utility/Activities bridge `Scavenge chicken feathers`. Only revisit feathers when Combat chicken drops or the Grand Exchange is explicitly in scope; then decide whether to keep, remove, or rebalance the bridge route.
```

### P3 - NPC Shops V1 Candidate

User story: As a player, I want source-backed NPC shops, so tools, bait,
materials, and shop-only rewards can enter play through authentic RuneScape
interfaces instead of temporary Utility bridges.

Why later: The design is promising, but it needs a deliberate economy-state
model before implementation. It should not be folded into Hunter supply cleanup
or the parked GE by accident.

Backend-first scope:

- Use `memory-bank/npc-shop-design-seed.md`; grill the open design decisions
  before writing model code.
- Source shop stock, shared-inventory groups, prices, and shop rules from local
  2011Scape and local Darkan/2012scape, with historical wiki checks when they
  conflict heavily.
- Model shared stock by shared-shop group, not only by visible shop/NPC.
- Preserve buy/sell behavior, consumed Coins, item transfer, and undo-aware
  state changes.
- Treat location and quest locks as first-class shop access data.

Frontend follow-up scope:

- Add the Shop menu surface only after backend contracts are real.
- Show source-backed shop lists, stock rows, prices, owned Coins, buy and sell
  flows, and lock reasons.
- Keep temporary Utility bridges visible until the corresponding shop route is
  implemented and intentionally replaced.

Acceptance criteria:

- At least one audited shop family proves source-backed stock, dynamic prices,
  buy/sell flow, shared-stock persistence where relevant, and undo rollback.
- Shop state is covered by unit and integration tests before Qt work starts.
- Frontend work starts from a backend contract note, not guesswork.

Future thread prompt:

```text
In the AnkiScape repo, use memory-bank/future-work-kanban.md and memory-bank/npc-shop-design-seed.md. Work on P3 only if the owner has explicitly reprioritized NPC shops. Grill the open design decisions first, then implement backend-first: shop registry, shared-stock state, source-backed prices, buy/sell item transfer, access locks, undo-aware review snapshots, and tests. Leave a frontend handoff note before any Shop menu UI thread starts.
```

### P3 - Grand Exchange V1 Candidate

User story: As a normal-mode player, I want optional market access for tradable items, so missing acquisition loops can be softened without forcing every source chain to be implemented first.

Why later: The design is useful, but the current priority is architecture debt and small polish. GE should not crowd out existing-skill cleanup unless the owner explicitly moves it up.

Backend-first scope:

- Use `memory-bank/fake-grand-exchange-design.md`; do not re-grill the core design unless requirements change.
- Keep v1 local-only and deterministic.
- Implement tradability metadata, coins, offer storage, matching/tick behavior, and tests before frontend work.
- Avoid recipe-aware bulk buying and other economy conveniences in v1.

Frontend follow-up scope:

- Add a top-level GE section only after backend contracts are real.
- Include search, buy/sell offer creation, offer status, collect, and cancel flows.
- Keep Bankstanding as a Utility activity only if the backend needs it.

Acceptance criteria:

- GE behavior follows the parked design file.
- Backend tests prove offer creation, matching, cancellation, collection, persistence, and tick behavior.
- Frontend work starts from a backend contract note, not guesswork.

Future thread prompt:

```text
In the AnkiScape repo, use memory-bank/future-work-kanban.md and memory-bank/fake-grand-exchange-design.md. Work on P3 only if the owner has explicitly reprioritized the Grand Exchange. Implement backend first: tradability metadata, coins, local offer matching, storage, ticks, and tests. Do not build recipe-aware buying. Leave a frontend handoff note before any UI thread starts.
```

### Parked - Crafting Dependency-Heavy Acquisition Loops

User story: As a player, I eventually want Crafting inputs to come from real source chains, but those chains should wait until their supporting systems are worth implementing.

Parked examples:

- Dragonstone and onyx supply.
- Leather and hide chains beyond current practical needs.
- Molten glass, battlestaves, orbs, roots, and rune-dependent flows.
- Any broader acquisition loop that mainly exists to support Crafting completeness.

Move out of parked only when:

- The owner explicitly reprioritizes the loop.
- A new skill makes the loop naturally useful.
- The GE implementation needs a specific tradable input classification.

Future thread prompt:

```text
In the AnkiScape repo, do not work on Crafting dependency-heavy acquisition loops unless the owner explicitly reprioritizes them. If reprioritized, start from memory-bank/source-audits/crafting-2011scape-2026-06-03.md, keep the scope to one source chain, and avoid broad economy or drop-table work.
```

### Parked - Mining And Woodcutting Special Content

User story: As a player, I eventually want special skilling content, but it should land after the supporting systems exist.

Parked examples:

- Mining concentrated coal/gold.
- Mining gem-rock Ring of wealth bonus.
- Shooting Stars.
- Woodcutting Inferno adze.
- Bird nest downstream uses that require Farming, Herblore, or broader loot systems.

Move out of parked only when:

- The owner explicitly reprioritizes special content.
- A supporting system such as Magic, Firemaking, Farming, Herblore, or a special reward framework is already in place.

Future thread prompt:

```text
In the AnkiScape repo, keep Mining and Woodcutting special content parked unless the owner explicitly reprioritizes it. If reprioritized, start from the relevant source audit in memory-bank/source-audits/ and implement one narrow special-content slice with tests and provenance notes.
```

## Completed - Firemaking V1

Status 2026-06-16: Complete. Firemaking is a current Artisan review skill with
13 local-2011Scape burnable targets, stable `current_firemaking` IDs, source XP,
success-only log consumption, `Ashes x1`, storage config version 12, achievements,
assets, and Skills hub/Stats/Bank/HUD support. See
`memory-bank/source-audits/firemaking-2011scape-2026-06-16.md`.

Bonfires and fire spirits are technically pre-EOC, but intentionally deferred
because they are a separate 2012 training method and reward system rather than
ordinary line-lighting behavior.

Future thread prompt:

```text
In the AnkiScape repo, do not redo Firemaking v1. It is already implemented as a current Artisan skill. Only revisit Firemaking if the owner explicitly asks for a follow-up such as bonfires/fire spirits; if so, treat that as a separate 2012 pre-EOC extension with its own batch-log, XP-bonus, fire-spirit reward, Cooking boost, warmth/temporary-health, multiplier, undo, UI, tests, and Memory Bank plan.
```

## Completed - Fishing V1

Status 2026-06-16: Complete. Fishing is a current Gathering review skill with
15 local-2011Scape `FishingSpot.kt` behaviors, stable `current_fishing` IDs,
source XP/chance rows, ordered mixed-output rolls, material use only on catch,
hidden Strength/Agility side XP for Barbarian fish, generic Fishing
achievements, fish/material assets, and Skills hub/Stats/Bank/HUD support. See
`memory-bank/source-audits/fishing-2011scape-2026-06-16.md`.

The 2011 snapshot-to-pre-EOC wiki check found no missing ordinary catch method
for this v1. Stone fish is quest-only, Fish Flingers is a D&D/reward surface,
Depth Charge Fishing is cosmetic, and Dungeoneering fish/Fishing Trawler are
older nonstandard systems. Treat all of those as separate future slices rather
than Fishing v1 gaps.

Future replacement prompt:

```text
In the AnkiScape repo, do not redo Fishing v1. It already implements local 2011Scape ordinary FishingSpot methods with source-backed data, assets, Utility fishing bait, undo-safe review handling, and Qt coverage. Only revisit Fishing if explicitly working on Dungeoneering fish, Fishing Trawler, quest-only fish, Fish Flingers, or real shop/GE material sourcing.
```

## Completed - Runecrafting V1

Status 2026-06-17: Complete. Runecrafting is a current Artisan review skill
with 61 local-2011Scape-backed targets, stable `current_runecrafting` IDs,
standard runes, combination runes, tiara binding, Wicked hood feeding, pouch
capacity/degradation, Binding necklace charge counters, generic achievements,
runecrafting assets, and Skills hub/Stats/Bank/HUD support. Rune Mysteries is a
review-driven Quest action, not a fake XP skill, and the Wicked hood is a
one-time Bank Claim after Rune Mysteries plus Runecrafting level 5. See
`memory-bank/source-audits/runecrafting-2011scape-2026-06-17.md`.

Magic Imbue, Wicked hood daily essence/runes/teleports/reclaim, Abyss routing
and abyssal creatures, talisman sourcing, and broader rune economy routes are
deferred system slices. Treat those as follow-ups rather than Runecrafting v1
gaps.

Future replacement prompt:

```text
In the AnkiScape repo, do not redo Runecrafting v1. It already implements local 2011Scape standard/combo/tiara Runecrafting, Rune Mysteries quest unlock, Wicked hood claim/feed access, Binding necklace charges, pouches, assets, undo-safe review handling, and Qt coverage. Only revisit Runecrafting if explicitly working on Magic Imbue, Wicked hood daily resources/teleports/reclaim, Abyss routing/abyssal creatures, talisman sourcing, or broader rune economy routes.
```
