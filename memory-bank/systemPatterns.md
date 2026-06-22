# System Patterns

## Architecture Snapshot
The add-on is a small Python package loaded by Anki. It separates pure game contracts from Anki-aware orchestration for review dispatch, runtime actions, target rows, and achievements, though some skill behavior still lives in UI, storage, stats, and icon-registration surfaces.

## Important Modules
- `__init__.py`: runtime orchestration, global player state, review hooks, answer handling, menu callbacks, save/HUD/UI bridge callbacks, and compatibility review-action wrappers.
- `runtime_actions.py`: Anki-free runtime review-action handlers and handler-keyed can-start checks for Mining, Woodcutting, Fishing, Hunter, Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Quests, and Utility/Activities. It mutates `player_data` through a callback/context contract supplied by `__init__.py`.
- `constants.py`: item data, skill source data, image paths, XP table, and compatibility exports.
- `logic_pure.py`: pure helpers for XP/level math, probabilities, crafting, Utility/Activities, mining, woodcutting, fishing, hunter, smithing, quests, claims, and runecrafting operations.
- `logic.py`: Anki-aware level-up and achievement checks plus probability wrappers.
- `storage.py`: Anki config persistence.
- `storage_pure.py`: default player shape and migrations.
- `skill_registry.py`: pure skill catalog for current and planned skills, including stable IDs, categories, save keys, and review eligibility.
- `action_registry.py`: pure review-action dispatch metadata. It resolves levelled skills and no-XP Utility/Activities to handler keys without adding Utility as a fake skill.
- `target_metadata.py`: pure target-row metadata for the Skills hub. It builds labels, tooltips, icon paths, enabled/current state, groups, sort order, and lock reasons for Mining, Woodcutting, Fletching, Firemaking, Fishing, Hunter, Smithing, Crafting, Cooking, Runecrafting, and Utility/Activities without creating Qt widgets.
- `achievement_metadata.py`: pure achievement definitions, difficulty order, grouped row view models, and progress-count helpers while preserving the legacy completed-achievement name contract.
- `hunter_data.py`: source-backed Hunter target data. It uses 2011.rs guide rows for levels/XP/rewards, local 2011Scape cache item names/ids for storage keys, and local 2012scape/Darkan Hunter code only as mechanics/id parity because the local 2011Scape checkout has no Hunter mechanics plugin.
- `item_registry.py`: pure item manifest helpers for current economy items, including stable IDs, storage keys, categories, assets, and source/license notes.
- `equipment_data.py`: generated worn-equipment contract for Smithing armour/weapons and Mining bonus gear, including slots, combat gates, two-handed flags, attack speed, and combat bonuses.
- `quest_catalog_generated.py`: generated pre-EOC quest catalog. Do not edit manually; regenerate it with `tools/build_pre_eoc_quest_catalog.py`.
- `quest_data.py`: Quest definitions, hand-audited overrides, generated quest item rewards, XP lamp claim definitions, and completion-unlock rules for skill targets.
- `ui.py`: Qt dialogs, HUD, menu, stats, bank, achievements, and settings.
- `hooks.py`: centralized hook registration and dry-run planning.
- `injectors.py` and `deck_injection_pure.py`: floating widget / deck browser injection helpers.

## Current Skill Flow
1. Anki shows a review card and the add-on marks review state.
2. The user shows the answer, then answers with an eligible ease.
3. `on_answer_card` calls `on_good_answer` if the current skill is active and XP has not already been awarded.
4. `__init__.py` resolves the handler key and calls `runtime_actions.py` through a `RuntimeActionContext`; runtime handlers call pure helpers, update `player_data`, check levels/achievements through callbacks, save, and refresh UI.

## Existing Skill Patterns
- Gathering skills use success probabilities and selected resource data.
- Processing skills consume inventory and produce output items.
- All skills use the shared `EXP_TABLE` and per-skill `*_level` / `*_exp` fields.
- Inventory is a single dictionary shared across ores, logs, gems, bars, and crafted items.
- The backend registry preserves current flat save keys while centralizing skill identity. This is deliberate: Anki config is the stable boundary, so registry-driven defaults are safer than a nested save migration right now.
- The item registry uses existing inventory storage names as `storage_key` values. Stable item IDs can support future UI/action metadata without breaking current saves.
- Review dispatch now resolves an `action_registry.review_action_handler_key` before calling the matching `runtime_actions.py` handler. Thin public `on_<skill>_answer` wrappers remain for compatibility and direct tests. This keeps display names, save keys, Utility aliases, handler identity, and runtime mutation logic connected without requiring a large action-engine rewrite.
- Skills-hub target lists now consume `target_metadata.TargetRowMetadata` rows. The Qt layer uses one shared `QListWidget` renderer for Mining, Woodcutting, Fletching, Firemaking, Fishing, and the flat list cases, plus one shared grouped `QTreeWidget` renderer for Smithing, Crafting, Cooking, Runecrafting, and Hunter. The pure row metadata owns labels, tooltips, icon paths, group ids, sort keys, current state, enabled state, and lock reasons; Qt only renders rows, persists group expansion where applicable, and guards disabled-row clicks.
- Achievement definitions now live behind `achievement_metadata.py`. `constants.ACHIEVEMENTS` stays as a legacy export for `logic.py`, old tests, and any add-on code that reads the dict shape, while UI code consumes row/progress helpers instead of reconstructing grouped achievement state.
- Fletching is the first staged expansion skill to complete backend + target-panel rollout. It uses stable recipe IDs for save/UI selection, because multiple recipes can produce the same inventory item (for example, several log tiers all output arrow shafts).
- Fletching material-only inputs such as feathers and arrowtips are registered as item-manifest `material` entries. Arrowtips are sourced through Smithing, and feathers have a temporary no-XP Utility bridge (`scavenge_chicken_feathers`) until Combat chicken drops and/or GE exist.
- Utility/Activities are backend actions, not skills. They use stable activity IDs in `UTILITY_ACTIVITY_DATA`, mutate inventory through pure helpers, award zero skill XP, and can batch up to an inventory-sized cap when they represent fast material preparation.
- Utility/Activities can also represent one-shot acquisition bridges while the full shop/GE interface is deferred. These activities declare an `outputs` mapping instead of a single `output_item`, can set `deactivate_after_run = True`, and the runtime switches AnkiScape off after the successful review so the action multiplier cannot repeat the purchase inside the same card.
- Utility/Activities should stay outside `skill_registry.py` unless they gain real level/XP semantics. Runtime dispatch handles them through `action_registry.py` and the handler key `utility`, while the UI may still surface them as a synthetic Skills-hub category.
- Utility/Activities now have a small row-icon contract: each existing `UTILITY_ACTIVITY_DATA` entry can expose an `icon_path` pointing at a dedicated `activityicons/<activity>.png` asset. The Qt target list prefers that activity-level icon and falls back to the old output-item image map if the path is missing. This keeps no-XP activity presentation first-class without adding Utility to the skill registry or changing reward logic.
- Crafting recipe data stores source XP only. Runtime reward handling awards base XP per action tick; review pacing is controlled by the actions-per-review multiplier rather than by inflating a single action's XP.
- Crafting now follows the source-data-module pattern at the backend layer (`crafting_data.py`). `current_craft` stores stable recipe IDs, inventory stores real item names, and the data intentionally includes live input-starved recipes so missing acquisition loops light up later without reshaping the recipe. XP-bearing Crafting ignores recipe `batch_size`; only no-XP Utility/Activities batch material prep.
- Woodcutting now has a focused source-data module (`woodcutting_data.py`) rather than only ad hoc `constants.py` rows. Its stable target IDs are persisted in `current_tree`, while inventory uses real item output names such as `Logs` and `Oak logs`.
- Fishing now follows the source-data-module pattern (`fishing_data.py`) as a Gathering skill. Its stable method IDs are persisted in `current_fishing`, while inventory uses real output item names such as `Raw crayfish`, `Raw salmon`, and `Raw shark`. Mixed-output rows preserve source order during rolls, consumable material is removed only after a successful catch, and Barbarian fish side XP updates hidden Strength/Agility state without exposing those skills in the UI yet.
- Fletching now follows the source-data-module pattern (`fletching_data.py`) as
  an Artisan processing skill. Stable target IDs are persisted in
  `current_fletch`, while inventory uses real output and material item names.
  `constants.FLETCHING_DATA` is only a compatibility export. Fletching target
  metadata carries group/sort data for the shared grouped `QTreeWidget`
  renderer. Common reusable tools remain ambient; only level, materials, and
  generic target unlocks gate rows.
- Cooking now follows the source-data-module pattern (`cooking_data.py`) as an Artisan skill. Its stable target IDs are persisted in `current_cooking`, while inventory uses real raw/cooked/burnt item names. Cooking failures are productive inventory mutations: the raw input is consumed, the source burnt item is added, and no XP is awarded. Source low/high chances stay in data and are adapted to review-scale probabilities in pure logic.
- Runecrafting now follows the source-data-module pattern (`runecrafting_data.py`) as an Artisan skill. Its stable target IDs are persisted in `current_runecrafting`, while inventory uses real rune/access item names. Rune Mysteries quest state, Bank Claims, Wicked hood fed-altars, pouch degradation, and Binding necklace charges are explicit flat side-state keys in `player_data`. Quests are review actions through `action_registry.py`, not fake skills in `skill_registry.py`.
- Hunter now follows the source-data-module pattern (`hunter_data.py`) as a Gathering skill. Its stable target IDs are persisted in `current_hunter`, while inventory uses canonical cache item names such as `Red feather`, `Kebbit claws`, `Imp-in-a-box (2)`, `Gourm' impling jar`, and `Ess' impling jar`. The local 2011Scape cache/snapshot is treated as identity evidence, not a mechanics implementation; 2011.rs guide rows supply levels/XP/rewards, and local 2012scape/Darkan Hunter code supplies mechanics/id parity. Hunter outputs are first-class `hunter` bank items, while jars/traps such as `Butterfly jar`, `Impling jar`, and `Magic box` remain material items. Quest locks cover completion gates and narrow route precedents only; partial-route access such as Regicide-start content stays in notes until a route model exists.
- Hunter separates reusable gear from consumables. `requirements` are deleted only on successful catches; `tools` are bank/inventory gates that remain after a catch. Current reusable gates cover bird snares, box traps, butterfly nets for butterfly/Puro-Puro rows, and small fishing net plus rope for tree-net rows. The temporary `Buy Hunter supplies` Utility bridge spends `500 Coins` for a source-backed starter/restock bundle, then turns itself off after one review. A richer shop interface remains a later economy/UI pass.
- The broad quest catalog is generated, not hand-maintained. `tools/build_pre_eoc_quest_catalog.py` produces a 194-row pre-EOC catalog by real release order, with Recipe for Disaster split into separate subquests. Each row should carry source oldids, strict prerequisites, point/XP/item rewards, lamp rewards, and source-backed journal stages. Hand-audited overrides belong in `quest_data.py` when local 2011-era evidence is stricter than current wiki data.
- Quest starts are strict. A quest with incomplete prerequisite quests or unimplemented required skills must be impossible to start. Completion XP for implemented skills is granted immediately; XP for unimplemented skills is stored in `pending_skill_exp_rewards` and applied by migration when the skill becomes implemented.
- Quest-list availability should flow through `quest_availability_state_pure()`, not ad hoc UI checks. Its states are `can_start`, `in_progress`, `blocked_at_stage`, `completed`, and `locked`. `locked` means the quest cannot start; `blocked_at_stage` means a started quest is waiting on current-stage inventory, tools, actions, routes, or combat. Keep that separation: stage requirements are not start locks.
- Stage-aware quest requirements live in `QuestDefinition.stage_requirements` data, serialized by `quests_as_dict()` and enforced by pure helpers in `logic_pure.py`. Use `quest_current_stage_blockers_pure()` / `quest_current_stage_blocker_reasons_pure()` for display, `can_progress_quest_pure()` for review readiness, and `apply_quest_progress_pure()` for stage advancement and stage-local consumed/produced items. The first proof case is The Knight's Sword: Mining 10 remains a start requirement, Redberry pie is consumed at Thurgo's stage, Blurite ore plus two Iron bars are consumed at the later Thurgo materials stage, and the 12,725 Smithing XP reward fires only on valid completion. A later 2011Scape starter batch added `produced_inventory` for quest intermediates such as Druidic Ritual enchanted meats, Pirate's Treasure chest key/message, and Vampyre Slayer stake/stake hammer. A follow-up intermediate batch added `start_inventory` and source-backed produced/consumed chains for Rune Mysteries, The Restless Ghost, and Lost City, including Ghostspeak amulet, Muddy skull, Air talisman, Research package, Research notes, Dramen branch, and Dramen staff. Demon Slayer is now a Darkan-backed focused replacement: it uses a nine-stage internal model so bucket water, 25 bones, three Silverlight keys, Silverlight, Delrith, and the incantation all gate at their source-backed stages before completion. Dragon Slayer is now a Darkan/local-2011Scape-backed focused replacement: 32 quest points remains the start lock, then Oziach, Guildmaster, anti-dragon shield, Melzar's Maze combat, Wormbrain's paid map piece, Oracle items, Crandor map assembly, Lady Lumbridge purchase/repair, Ned's route, Elvarg, and the Oziach report are separate current-stage gates. `QuestStageRequirement.variant` now models mutually exclusive route rows on the same stage; rows with no variant are mandatory, and route-matched variant rows are the only branch rows that can block, consume, produce, or resolve combat. Shield of Arrav proves this with Phoenix Gang and Black Arm Gang branches, Jonny the beard and Weaponsmaster combat gates, route-specific shield/certificate halves, and the partner half-certificate combine stage. Fight Arena now proves a Darkan-backed non-branch replacement where disguise production/equipment, Khali brew purchase/consumption, key theft/use, mandatory arena fights, and the Lady Servil return are stage gates rather than start locks. The Quests tab may show "Used during quest" item requirements before start, but those items must not block starting unless the source says they are start requirements.
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
  `quest_data.py`
  deserializes them into the same `QuestStageRequirement` contract used by hand
  overrides. `logic_pure.py` treats consumed option groups as current-stage
  blockers and consumes the first satisfied option group when the stage
  advances. Produced inventory is not a blocker by itself; it is the
  source-backed item state created by a successful current-stage transition.
  `quest_data.py` then combines generated rows, hand-authored stage rows,
  focused replacement rows, and focused addition rows; use replacements when
  generated data conflicts with stronger 2011Scape/Darkan evidence, and use
  additions when a source-backed quest action exists but the generated item or
  combat parser cannot infer it. The current audit reports 194/194 quests with
  at least one stage requirement, and the Priest in Peril focused override
  fixes its generated stage-61/prose-parser row into nine source-backed stages.
  The 2011Scape starter batch then replaced bad generated rows for Cook's
  Assistant, Imp Catcher, Druidic Ritual, Pirate's Treasure, and Vampyre Slayer.
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
  clothing is bought mid-quest, cattleprod/clothing are required tools, and the
  four coloured sheep bones are consumed at the incineration stage. Plague City
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
  Black Dragon rows. The live audit now reports 194/194 quests with stage
  requirements, 1,107 stage rows, 174 quests with item/tool blockers, 190 quests
  with action blockers, 18 quests with route blockers, 120 quests with combat
  blockers, 104 produced-inventory rows, and 185/288 resolver-ready combat rows.
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
- Generated combat quantity rows should preserve source quantities. Numeric
  prefixes, `xN` suffixes, "at least N", and written quantities through ten
  are parsed in `tools/build_pre_eoc_quest_catalog.py`; do not collapse rows
  such as "Two Lava monsters" or "Five Ice Trolls" to a single combat
  completion.
- Quest combat encounters fail closed through one global flat save config:
  `player_data["quest_combat_config"]["resolver_enabled"]`. It defaults to
  `False`, so incomplete encounters produce `combat_locked` blockers instead of
  silently progressing. When the resolver is enabled, current-stage encounters
  still require source-backed NPC stats for the encounter's attack style and a
  player combat level at least as high as the encounter level before
  `apply_quest_combat_encounter_pure()` can resolve combat. Combat quantities
  are per-enemy progress, not group-complete flags: one Quest review increments
  `player_data["quest_combat_encounter_counts"][quest_id][encounter_id]`, and
  only when the count reaches the sourced `QuestCombatEncounter.quantity` does
  the runtime write the completed encounter id into
  `player_data["quest_combat_encounters"]` for compatibility with older saves.
  Existing saves that already have the completed id still satisfy the blocker.
  Encounters missing stats remain blocked as `combat_missing_stats`; this keeps
  the global switch from turning no-stats prose rows into completable fights.
  Focused `quest_data.py`
  stage-addition combat rows may carry local 2011Scape NPC stats directly when
  the source path is recorded, and the catalog generator may enrich generated
  encounters from local source data in strict precedence order: 2011Scape NPC
  definitions first, then Darkan/2012scape combat definitions keyed by exact
  NPC name plus combat level. Darkan duplicates can be accepted only when all
  captured battle stats/configs agree; conflicting duplicates stay statless.
  The Restless Ghost Skeleton Warlock is the focused override proof case;
  Demon Slayer's Delrith is now a focused Darkan stage replacement, Dragon
  Slayer's Elvarg proves the generated Darkan fallback, and Elemental Workshop's Earth Elemental proves the identical
  duplicate-source path, while Priest in Peril's Monk of Zamorak and Troll
  Stronghold's Dad prove focused conflict resolution from area-specific Darkan
  quest/combat sources. Witch's House first proved a focused replacement can
  split an ambiguous generated fight into four resolver-ready Darkan-backed
  forms; its current full-stage replacement keeps those forms at stage 9 after
  keys, Magnet, Cheese, patrol, glove, and shed-door gates.
  Focused combat replacements may also expand one generated row into multiple
  source-backed encounters without replacing the quest's other stage
  requirements; Spirits of the Elid's generic `Golem x3` row now expands into
  Black, White, and Grey golems while preserving its generated item/tool rows.
  Resolver readiness is attack-style aware: magic encounters require
  hitpoints, defence, and magic; ranged encounters require hitpoints, defence,
  and ranged; melee/unknown encounters require hitpoints, attack, strength, and
  defence. A complete melee fallback handles inconsistent style metadata such
  as TokHaar-Mej, but hitpoints-only Darkan files still stay blocked until
  style-critical combat stat evidence exists. H.A.M. mage, The Void Stares
  Back's Torcher/Defiler, and The Elder Kiln's TokHaar-Xil prove the
  style-aware generated path. The Darkan `developer-information/beasts.txt`
  fallback may fill missing or zero generated Darkan combatdef attack,
  defence, magic, and ranged values only when the combatdef has an exact ID
  match or an unambiguous name/level identity and the merged payload satisfies
  the same attack-style-aware resolver contract. It must not infer melee
  Strength from beast metadata, and `npc_stats_source` should mention
  `beasts.txt` only when a beast value actually contributed to the generated
  payload. Darkan combatdefs without `combatLevels` may still become
  resolver-ready when their hitpoints/configs plus an exact name/level
  `beasts.txt` signature satisfy the style-aware contract; multi-id combatdefs
  must be merged per matched name/level so one dungeoneering file cannot smear
  stats across unrelated levels. TokTz-Ket-Dill's Lava monster, Nomad's
  Requiem's Nomad, Forgiveness of a Chaos Dwarf's Chaos dwarf hand cannoneer,
  The Blood Pact's Caitlin, Love Story's Pit scabarite, and Salt in the Wound's
  Forgotten mage/ranger prove these paths. Focused name-shape replacements now
  make Heroes' Quest's Entrana Fire Bird and Another Slice of H.A.M.'s
  H.A.M. ranger resolver-ready from Darkan combat sources. A Soul's Bane proves
  that a focused full-stage replacement can remove bad generated anger-room
  combat rows, keep the rage room as a required-action gate, and split later
  Darkan-backed room fights into multi-count enemies. Death to the Dorgeshuun's
  Senior H.A.M. guard proves focused generated-row replacement can preserve a
  historical quantity while mapping to a local Darkan NPC/combatdef identity.
  Shield of Arrav adds route-specific Jonny the beard and Weaponsmaster
  encounters with Darkan resolver stats while keeping both routes blocked by
  the global combat config until battle support is enabled. Fight Arena adds
  Bouncer as a Darkan resolver-ready focused stage row while keeping the
  Khazard ogre and Khazard scorpion blocked as missing-stats encounters because
  their available Darkan combatdefs carry hitpoints/max-hit metadata but no
  style-critical melee stats. Merlin's Crystal adds Sir Mordred as a
  Darkan-stat-backed resolver encounter while treating Thrantax as a ritual
  action instead of an invented battle. The generated combat parser now also
  resolves safe historical-name mismatches for Temple of Ikov's Guardians of
  Armadyl and Observatory Quest's Poisonous Spider. When stronger local quest
  source says a generated combat row is a false positive, replace the live stage
  chain instead of carrying the false row: Dwarf Cannon proves this by replacing
  generated level-2 Goblins with a Darkan-backed noncombat chain and `combat:
  None.` Scorpion Catcher then adds a source-backed level 39 jailer combat gate
  from Darkan quest and combatdef evidence while keeping the other scorpion
  catches as route/action gates. Heroes' Quest now adds Ice Queen and Grip
  source-backed resolver rows while keeping Ice Queen lair access as a route
  blocker rather than the old generated Jailer assumption. Shilo Village now
  splits Nazastarool into three focused sourced forms, Legends' Quest preserves
  Nezikchened as a three-kill encounter, The Feud adds Tough guy, and Recipe for
  Disaster: Freeing Sir Amik Varze adds a resolver-ready Black Dragon while the
  Evil Chicken stays missing-stats blocked. Current stat coverage is 185/288
  combat rows; the remaining 103 statless rows
  are classified by
  `tools/audit_quest_combat_stat_gaps.py` and remain active quest debt.
  Historical RuneScape Wiki monster pages are now audited by
  `tools/audit_quest_historical_wiki_combat_stats.py` as a separate source tier:
  LP, max hit, and attack-style prose are useful metadata, but they must not be
  counted as resolver-ready hidden combat stats. The 2026-06-22 pass found 77
  metadata-only pages, 32 rows without monster metadata, and 0 remaining rows
  with resolver-ready historical-wiki hidden stats.
- Completed quest reviews intentionally turn Quest training off and show a modal `Quest complete` stop-point dialog through the same centralized warning-dialog helper used by material depletion. Keep that paired with the existing floating completion gain so the player sees both immediate feedback and a clear action stop.
- XP lamps from quest rewards are flattened into Bank Claims. Preserve the source amount, quantity, skill option set, and minimum level, but use one consistent `Choose skill` claim flow instead of copying every historical quest-specific lamp/chatbox interface.
- Bank Claims are a compact action inbox above the Bank inventory, not an item category. The frontend should render eligible rows only, summarize locked rewards, hide claimed rewards behind the all-caught-up state, and cap the rows to keep the inventory list as the main scroll surface.
- The Wicked hood claim is intentionally gated by Rune Mysteries only in AnkiScape. Do not re-add a Runecrafting level 5 claim gate; historical 2012 evidence shows that level prompt was not a reliable hard claim requirement, and the hood's actual altar use still remains constrained by Runecrafting target gates.
- Generic target unlock locks are still exported as `QUEST_UNLOCK_RULES` for
  compatibility, but the rule shape supports both `quest_completed` and
  `ability_unlocked` requirements. This registry feeds Mining, Fishing,
  Cooking, Firemaking, Runecrafting, Fletching, and Utility/Activities lock
  reasons. Route/location gates normally stay out of global locks, but can be
  flattened to logical quest precedents when the current generic row effectively
  represents that locked route: Shilo Village gates `gem_rocks`, Priest in Peril
  gates Morytania-flavored slimy eel/snail rows plus Hunter `catch_swamp_lizard`,
  The Fremennik Isles gates Neitiznot/yak/arctic pine rows, As a First Resort
  gates Hunter `catch_wimpy_bird`, Eagles' Peak gates Hunter `catch_ferret`, and
  Rocking Out gates Hunter pirate implings. Ability gates are flat
  `player_data["unlocked_abilities"]` ids, currently including
  `broad_fletching` and `barbarian_fishing`.
- Utility/Activities can now be grouped by `group` metadata in the Qt tree when an action family gets large. Cooking prep uses this to separate gathering, material processing, container/opening, and Cooking prep actions while staying outside the XP skill registry.
- Mining now follows the same source-data-module pattern (`mining_data.py`). Its stable target IDs are persisted in `current_ore`, while inventory continues to use real item output names such as `Iron ore`, `Pure essence`, `Sandstone (10kg)`, and `Uncut opal`.
- Smithing now follows the source-data-module pattern too (`smithing_data.py`). It is the first skill with two XP-bearing stations under one skill: smelt and forge are both recipes in `SMITHING_DATA`, selected by stable `current_smith` IDs, while `BAR_DATA` is only a compatibility view for old smelt-only UI paths. Runtime uses one pure processing helper for both stations and keeps hammer/tool requirements implicit; level and inventory materials are the only backend gates. Iron bar smelting is the only source-backed random smelt action: after a valid action starts it consumes `Iron ore`, then either produces `Iron bar` and XP or records a `smelt_fail` telemetry failure with no output/XP. Other smelt bars and forge rows stay deterministic unless a source audit proves another post-start failure.
- Gathering tool progression is starting with a hybrid model: source tool items remain ordinary registered items for future acquisition/trading, but review logic can also resolve bound toolbelt IDs. Existing saves get a bound Bronze hatchet so introducing tool requirements does not brick Woodcutting. Reuse this for Mining pickaxes if the pattern holds.
- The hybrid toolbelt pattern now covers Mining too. Toolbelt remains tools-only (`bronze_hatchet`, `bronze_pickaxe`, etc.). Passive/equipable bonuses live outside toolbelt in `player_data["equipment"]`; Mining bonus logic reads the worn `neck`/`body` slots rather than passive ownership.
- Reusable tools are not automatically visible just because the source action has one. Fishing deliberately keeps rods, nets, cages, pots, vessels, and harpoons implicit in labels, tooltips, gating, and assets. Visible progression remains limited to Woodcutting hatchets and Mining pickaxes unless a future design explicitly promotes another tool family.
- Equipment now has both backend and Qt surfaces. `equipment_data.py` is generated from checked-in Smithing data plus local 2011Scape `items.yml`; storage keeps a flat `equipment` mapping (slot -> item name); pure helpers own gate/swap/stat-total rules; runtime callbacks feed a dedicated Equipment tab with right-click Equip/Unequip. Combat gates are real `*_level` checks even though combat training is not implemented yet.
- Source game tick odds should not be copied directly into review odds. Probabilistic review skills preserve audited source chance data, then pass the source roll chance through the shared `normalize_review_success_probability_pure` adapter so one Anki review action remains the pacing unit. Firemaking can still apply its separate target-tier cap because source Firemaking odds mostly vary by player level rather than log tier.
- Item tradability is now explicit in `ItemDefinition.tradeable`, seeded from source data for Mining additions. Do not infer GE eligibility from category alone; future economy work should consult item metadata and document source anomalies (for example Dragon pickaxe 15259/15261 and Varrock armour 4).
- `food` is now a first-class item category for cooked/prepared/burnt Cooking items. Burnt Cooking items are intentionally registered as non-tradeable junk in this fork even though RuneScape player-to-player tradability is historically weird, because future AnkiScape GE/trading will not distinguish marketing from trading.
- Random no-XP Utility actions can need special pure helpers. `Open bird nests` is the first example: it is a Utility/Activities action, but it consumes any known nest subtype and rolls source contents instead of using a fixed `requirements -> output_item` recipe.
- Review rewards are paired with Anki undo via `gui_hooks.state_did_undo`. When an eligible answer changes game state, the runtime records the original values for only the changed `player_data` keys; undo restores those values and saves config so Command-Z does not leave XP/items ahead of the card schedule.
- Review pacing is now an integer **actions-per-review** multiplier, not an XP-only scalar. Runtime reads `ankiscape_review_action_multiplier` (falling back to the old `ankiscape_xp_multiplier` key), executes up to N normal action ticks inside one eligible review, aggregates floating feedback, and records one undo snapshot for the whole review. Gathering skills spend N independent probability rolls; processing and Utility/Activities stop cleanly when materials run out before an extra sub-action.
- Every started review action should record durable telemetry in `player_data["action_telemetry"]`. The stable row key is `skill_id:action_id`; rows track attempts, successes, failures, expected successes, dry streaks, output counts, and failure kinds. Blocked actions such as missing materials or insufficient level do not count as attempts, but dry RNG outcomes, Cooking burns, and iron smelt failures do save telemetry.

## Architectural Pressure
Adding many skills by copying the current pattern would increase duplication in:
- skill selection UI
- stats rendering
- storage defaults and migrations
- answer dispatch
- icon/image registration
- tests

The current P0 architecture board now has backend modules for skill, item, review-action, runtime-handler, target-row, grouped target-tree, and achievement metadata. Remaining architecture pressure is lower-priority and mostly around stats rendering, icon/image registration, tests, and the large Anki/menu orchestration surface in `__init__.py` / `ui.py`.

## Skill Expansion Workflow
Use the project skill at `.cursor/skills/ankiscape-skill-expansion/SKILL.md` before adding or expanding any skill, Utility/Activity, target chain, item economy slice, or achievement set. It encodes the repeatable workflow: source audit first, playable scope cut, registry/item data, asset scraping, pure mechanics, UI surfacing, achievement patterns, tests, manual Anki checks, and memory updates.

## Compatibility Pattern
Persisted Anki config is the stable boundary. Schema changes should go through `storage_pure.py` migrations and keep existing user data intact.

Review-answer side effects must follow Anki's undo semantics. If a future skill mutates new `player_data` keys during an answer, the generic snapshot diff should catch them; if a future system writes outside `player_data`, it needs its own undo-aware rollback path.

## UI Gotcha: nested-closure name collisions in `show_main_menu`
`show_main_menu` is a very large function that defines many nested helpers (one per tab/section). All of these are locals of the *same* scope, so two sections defining a helper with the same name (e.g. `_select_skill`) silently rebind it — the later definition wins, and earlier callers route into the wrong function with no error. This caused the Skills-hub panel to ignore clicks (the Stats tab's `_select_skill` shadowed the hub's). Mitigation: prefix section-scoped helpers with their section (`_select_hub_skill`, etc.), and prefer the offscreen Qt behavior test to catch misrouted handlers. Longer term, splitting these sections into their own builder functions/classes would remove the shared scope entirely.

## UI Gotcha: dark-mode text colors (`palette(mid)` is NOT a text role)
Recurring bug: greyed/disabled/placeholder text rendered with `palette(mid)` / `QPalette.Mid` becomes **invisible in dark mode**, because `mid` is a frame/border role that resolves to a near-black grey. It has bitten the Skills-hub train button, the Smithing locked rows, and the Equipment empty slots. Fix at the root: `ui.dim_text_color(widget)` (for `setForeground`) and `ui.dim_text_css(widget)` (for stylesheet `color:`), which derive the color from the theme's real `Text` role and drop the alpha so contrast holds in both themes. `palette(mid)` is fine for borders only. Also prefer `palette(text)`/`palette(base)` over `buttonText`/`button` for button labels (the button face renders light on macOS dark mode). Enforced going forward by `.cursor/rules/qt-dark-mode-text.mdc` and the regression test `test_empty_slot_text_is_dark_mode_safe_not_palette_mid`. When changing UI colors, verify in dark mode, not just light.
