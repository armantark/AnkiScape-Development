# Progress

## What Works
- AnkiScape loads as an Anki add-on.
- The local working copy is intended to live outside the AnkiWeb-managed numeric folder.
- The local working copy is now initialized as a git repository on `main`.
- Review answers can award XP for the active skill.
- Command-Z/Anki undo now rolls back review-awarded XP/items by restoring the changed game-state keys paired with that answer.
- Mining, Woodcutting, Fishing, Smithing, Crafting, Fletching, Firemaking, Cooking, and Runecrafting exist.
- Rune Mysteries exists as a review-driven Quest action that unlocks Runecrafting.
- The Quest catalog now contains 194 pre-EOC quest rows: all RuneScape quests available before the 2012-11-20 EOC cutoff, with Recipe for Disaster split into its 10 subquests. It is generated from source-backed RuneScape Wiki old revisions plus local 2011Scape journal text where available.
- Items are stored in a shared inventory/bank.
- Level-up and achievement flows exist.
- Review HUD, floating XP, floating widget, main menu, stats, bank, settings, and achievements are present.
- Tests cover a meaningful portion of pure logic, migrations, settings, hooks, UI calculations, and integration smoke behavior.
- A backend skill registry exists for current and planned 2011-era skills.
- A pure review-action registry exists for levelled skills plus no-XP Utility/Activities aliases, without adding Utility as a fake skill.
- An Anki-free `runtime_actions.py` module owns review-action handler bodies and handler-keyed readiness checks, while `__init__.py` keeps hooks, global state, undo snapshots, UI/save callbacks, and thin compatibility wrappers.
- A pure target-row metadata contract exists for Mining, Woodcutting, Fletching, Firemaking, Fishing, Smithing, Crafting, Cooking, Runecrafting, and Utility/Activities, so Skills-hub row labels, tooltips, icons, groups, sort order, and lock reasons are generated before Qt renders them.
- A pure achievement metadata contract owns achievement definitions, difficulty order, grouped achievement rows, and progress counts while preserving the existing completed-achievement name save contract.
- A backend item manifest exists for current ores, logs, fish, food, runes/access items, gems, bars, crafted items, Fletching outputs/materials, and Utility/Crafting pilot materials.
- Storage defaults and migrations can seed registered item keys while preserving existing/custom inventory entries.
- Review eligibility and level-up key lookup are registry-backed for current review skills.
- `tools/fetch_assets.py` can fetch one item icon on demand from OSRS first and RS3 second, with retries, polite User-Agent handling, dry-run/force safety, optional square PNG normalization, and provenance output.
- Fletching exists as the first expanded playable skill: registry metadata, save defaults/migration keys, target panel, item manifest outputs/materials, pure processing logic, runtime review dispatch, and scraped output/material icons are in place.
- A project-local Cursor skill, `.cursor/skills/ankiscape-skill-expansion/`, captures the repeatable workflow for future skill/action expansion.
- Crafting/Utility backend rework is in place: no-XP Utility/Activities, corrected Crafting pottery/spinning/silver-bolt pilot data, a source audit, action-multiplier-compatible reward handling, migration coverage, and undo-safe review handling.
- Crafting/Utility frontend is in place: Utility/Activities is a no-XP Skills-hub category with batch tooltips and `on_set_utility` persistence; Crafting tooltips show output/batch; the HUD speaks the Utility no-XP state; Settings group into Gameplay/Notifications/Floating Widget/Developer with a clamped Actions-per-review control. Covered by offscreen Qt tests.
- Utility/Activities has a dedicated icon set: each existing activity exposes an `icon_path` backed by `activityicons/` assets, and the Qt list falls back to output-item art if an activity icon is missing.
- Feathers now have one legitimate non-dev source: `Scavenge chicken feathers` is a no-XP Utility/Activities bridge that grants `28 Feather` per successful action tick without opening Combat, shops, coins, or GE.
- Firemaking v1 is in place: source-backed `firemaking_data.py`, stable `current_firemaking` target IDs, storage config version 12 migration/defaults, review-scale lighting chances, implicit tinderbox behavior, source XP, `Ashes x1`, achievements, assets, and Artisan hub/Stats/Bank/HUD support.
- Fishing v1 is in place: source-backed `fishing_data.py`, stable `current_fishing` method IDs, storage config version 13 migration/defaults, review-scale catch chances, ordered mixed-output rolls, success-only material consumption, hidden Strength/Agility side XP for Barbarian fish, generic Fishing achievements, dedicated fish/material assets, a `fish` item category, and Gathering hub/Stats/Bank/HUD support.
- Cooking v1 is in place: source-backed `cooking_data.py`, stable `current_cooking` target IDs, storage config version 14 migration/defaults, review-scale cook/burn chances, burn failures that consume raw inputs and produce burnt items, generic Cooking achievements, beef/bear sinew secondary targets, dedicated Cooking assets, a `food` item category, grouped Cooking target UI, grouped Utility/Activities prep UI, and confirmed Bank `Discard all` for every item.
- Runecrafting v1 is in place: source-backed `runecrafting_data.py`, stable `current_runecrafting` target IDs, storage config version 15 migration/defaults, Rune Mysteries quest unlock with 250 Runecrafting XP, standard/combination rune crafting, tiara binding, Wicked hood claim/feed access with no Runecrafting level claim gate, pouch capacity/degradation, Binding necklace charge counter, achievements, dedicated assets, a `runecrafting` item category, grouped Runecrafting target UI, Quests tab, Bank Claims, Stats/Bank/HUD support, action multiplier support, and undo rollback.
- Hunter v1 is in place: source-backed `hunter_data.py`, stable `current_hunter` target IDs, storage config version 18 migration/defaults, bird snaring, butterfly netting, deadfall, box trapping, net trapping, falconry, magic box, and Puro-Puro/world impling rows, generic Hunter achievements, dedicated assets, a `hunter` item category, grouped Hunter target UI, quest/route-precedent locks, Stats/Bank/HUD support, action multiplier support, and undo rollback.
- Hunter now has a temporary supply acquisition bridge: `Buy Hunter supplies` is a one-shot no-XP Utility/Activities row that spends `500 Coins`, grants reusable Hunter gear plus starter jars, and automatically switches AnkiScape off after the successful review. Hunter targets now distinguish reusable `tools` from consumed `requirements`, so snares/nets/traps gate methods without being deleted while jars, logs, and magic boxes still consume on successful catches.
- Review-action telemetry and shared probability normalization are in place as of 2026-06-20. Storage config version 19 seeds and migrates `player_data["action_telemetry"]`; runtime records started actions for every skill/action family, including dry RNG attempts and Cooking burns; probabilistic source-chance helpers now share the AnkiScape review adapter. At Lv 18, the big-net mackerel row now has about a 37.7% catch chance per action tick instead of about 24.7%.
- The full quest reward surface now carries generated item rewards, source-backed journal/checklist stages, and structured XP lamp rewards. Lamp rewards are flattened into Bank Claims with preserved skill options/minimum levels; implemented skill XP is granted immediately and unimplemented skill XP parks in `pending_skill_exp_rewards`.
- The quest stage-gate surface now has broad generated/focused coverage. The
  pre-EOC catalog builder emits machine-readable stage blockers from
  quest-wide item, tool, item-alternative, and combat fields, and focused
  source-backed rows in `quest_data.py` close quests whose details are only in
  local 2011Scape/Darkan quest behavior. Current coverage is 194/194 quests
  with at least one stage requirement, 554 stage rows, 92 produced-inventory
  rows, 174 quests with item/tool/option blockers, and 120 quests with combat
  blockers. Combat blockers are hard locked by default through
  `quest_combat_config.resolver_enabled = False`;
  they do not silently complete while combat is unimplemented. Resolver-enabled
  combat now has 179/284 source-backed NPC stat rows after local
  2011Scape-first, Darkan/2012scape exact name+level enrichment, identical
  duplicate-source acceptance, focused override enrichment, and focused
  conflict resolution for area-specific Darkan combat sources, including the
  local 2011Scape Skeleton Warlock focused override for The Restless Ghost,
  Demon Slayer's focused Delrith stage row, generated Darkan rows such as
  Elvarg and Earth Elemental, plus Priest in Peril's Monk of Zamorak and Troll
  Stronghold's Dad. Witch's House now supersedes that combat-only proof with a
  full 12-stage Darkan-backed chain for Door key, Magnet, Cheese, witch patrol,
  Leather gloves, Backroom key, four experiment forms, Ball pickup, and Harvey
  hand-in. The style-aware resolver pass also
  accepts source-backed magic/ranged rows with zero melee Strength, adding
  H.A.M. mage, The Void Stares Back Torcher/Defiler, and The Elder Kiln
  TokHaar-Xil. The Darkan `beasts.txt` fallback then raised generated coverage
  by filling exact/unambiguous missing attack/defence/magic/ranged values for
  TokTz-Ket-Dill's Lava monster and Nomad's Requiem's Nomad, while still
  leaving melee rows without sourced Strength blocked. Combat quantities now
  resolve one enemy per Quest review: written-number source rows such as
  "Two Lava monsters", "Five Ice Trolls", and "Three Earth Elementals" are
  extracted by the catalog builder, partial progress is stored in
  `quest_combat_encounter_counts`, and the old `quest_combat_encounters`
  completed-id list is written only after the required quantity is fully
  defeated. Focused name-shape replacements now make Heroes' Quest's Entrana
  Fire Bird, Spirits of the Elid's Black/White/Grey golems, and Another Slice
  of H.A.M.'s H.A.M. ranger resolver-ready. A Soul's Bane now has sourced
  action/combat stage splits for the rage, fear, confusion, hopelessness, and
  Tolna rooms, and Death to the Dorgeshuun's Senior H.A.M. guard x3 row is
  resolver-ready. Demon Slayer now has a focused nine-stage replacement for the
  coin, bucket water, bones, Silverlight keys, Silverlight, Delrith, and
  incantation flow. Dragon Slayer now has a focused 16-stage replacement for the
  Oziach/Guildmaster setup, anti-dragon shield, Melzar's Maze combat, three
  Crandor map pieces, Oracle item door, Lady Lumbridge purchase/repair, Ned
  route, Elvarg combat, and final Oziach report. Shield of Arrav now has
  source-backed Phoenix Gang and Black Arm Gang route variants, Jonny the beard
  and Weaponsmaster combat gates, route-specific shield/certificate halves, and
  a partner half-certificate combine gate before King Roald's 1,200-coin
  completion reward. Fight Arena now has a 12-stage Darkan chain for Khazard
  disguise, Khali brew, cell keys, mandatory arena fights, and Lady Servil.
  Witch's House now has a 12-stage Darkan chain for keys, Magnet, Cheese, patrol,
  gloves, experiment forms, Ball pickup, and Harvey. Merlin's Crystal now has an
  8-stage Darkan/local-2011Scape chain for the round-table investigation, crate
  route, Sir Mordred, Morgan/wax, black candle, bread-to-Excalibur, ritual,
  crystal smash, and Arthur report; Thrantax is an action/dialogue gate rather
  than invented combat. Dwarf Cannon now has an 11-state Darkan-backed
  noncombat chain for rail repairs, Gilob's remains, the goblin hideout route,
  Lollk rescue, toolkit/cannon repair, Nulodion's parts, and Captain Lawgof's
  final recommendation. A generated-catalog parser follow-up now uses token-safe
  NPC name matching instead of raw substring matching, adds the safe
  `Poisonous Spider` -> `Poison Spider` alias, handles plural source text such
  as `Guardians of Armadyl`, and parses level-prefixed rows such as `Lvl 2
  Goblins`. Temple of Ikov's Guardians of Armadyl and Observatory Quest's
  Poisonous Spider are now resolver-ready from local source data; the generated
  Dwarf Cannon Goblins row is no longer live because stronger Darkan quest
  evidence says combat is none. Fishing Contest, Gertrude's Cat, Clock Tower,
  Monk's Friend, Tribal Totem, and Scorpion Catcher now have local
  Darkan-backed focused stage chains for their item transforms, route/action
  gates, and the Scorpion Catcher jailer fight. Sheep Herder now has a local
  Darkan-backed focused chain for poisoned sheep feed, Doctor Orbon clothing,
  cattleprod/tool routing, and all four sheep-bone incinerations. Biohazard now
  has a local Darkan-backed 13-stage chain for Jerico/Omart wall routing, Bird
  feed and Pigeon cage production/use, rotten apple stew poisoning, Doctors'
  gown production, the level 13 Mourner and Distillator recovery, Elena's reagent
  vials, chemist Touch paper, errand-boy smuggling, Priest gown x2 Guidor entry,
  and Elena/King Lathas report actions. Heroes' Quest now has a source-backed
  13-stage chain for Blamish oil/oily fishing rod prep, lava eel, Ice gloves,
  Fire feather, Black Arm/Phoenix candlestick route variants, armband exchange,
  and the final Achietties proof hand-in while preserving strict 56 quest point,
  quest prerequisite, and skill start locks. 105 combat rows remain statless
  and explicitly blocked.
- Completing the active Quest review now pops a `Quest complete` modal after rewards are applied and Quest training is switched off, matching the stop-point behavior used for depleted material actions.
- Bank Claims render as a compact Bank-tab action inbox: eligible rewards show icon/title/metadata/action rows, locked rewards collapse into a dark-mode-safe summary that names the primary current blocker, claimed rewards disappear into a caught-up state, and the inbox is capped above the inventory list.
- Quest target locks include logical route precedents when the current generic row effectively represents a locked region route: Priest in Peril gates Morytania-flavored slimy eel/snail rows, The Fremennik Isles gates Neitiznot-flavored yak/arctic pine rows, and Shilo Village gates the current generic `gem_rocks` Mining target.
- Crafting backend parity foundation is in place: source-backed `crafting_data.py`, stable `current_craft` recipe IDs, corrected 2011Scape XP values, live input-starved high/dependency targets, storage config version 11 migration, and no XP-bearing Crafting batching.
- Crafting frontend grouping/assets are in place: the Skills-hub Crafting panel groups stable recipe IDs by family, persists collapsed families, shows owned material counts, guards disabled-row clicks, and resolves the fetched `crafteditems/` icon set.
- Woodcutting backend parity is in place: 2011Scape target/hatchet/bird-nest source data, stable target IDs, real log item outputs, toolbelt-aware hatchet RNG, Ivy no-output XP, bird nest drops, no-XP nest-opening Utility, and storage migration from legacy tree-named logs.
- Woodcutting frontend/assets are in place: target rows show friendly names, tool requirements, Ivy/no-output notes, bird-nest Utility access, and fetched log/hatchet/nest art with graceful gaps only for rare unresolved egg assets.
- Mining backend parity is in place: 2011Scape target/pickaxe source data, stable target IDs, real output item names, toolbelt-aware pickaxe resolution, source-shaped Mining probabilities, weighted sandstone/granite/gem-rock outputs, incidental gem drops with no Mining XP, Varrock-armour extra output, amulet-of-glory gem chance, explicit Mining item tradability metadata, and storage migration from legacy display-name `current_ore` values.
- Review pacing can run multiple game action ticks per successful card via `Actions per review` (1x-10x). This replaces the old XP-only multiplier semantics: XP, items, material use, gathering rolls, and Utility batches now scale together, while Anki undo rolls back the whole multi-action review as one reward.
- Smithing backend parity is in place: source-generated `smithing_data.py`, unified `SMITHING_DATA` smelt/forge recipes, all 9 bars, all 157 forge rows from `BarProducts.kt`, stable `current_smith` recipe IDs, storage config version 9, canonical `Adamant bar`/`Rune bar` names, forged item manifest registration, runtime review dispatch through the unified pure Smithing helper, and source-shaped iron smelt failure. Iron bars use the local 2011Scape 50% to 80% success curve over Smithing levels 15 to 45, consume ore on failure, and record `smelt_fail` telemetry; other furnace bars stay deterministic.
- Equipment backend is in place: generated `equipment_data.py` covers Smithing armour/weapons plus Mining bonus gear, `player_data["equipment"]` replaces `owned_equipment`, combat level defaults are scaffolded, pure equip/unequip/stat-total helpers exist, and runtime exposes `on_equip_item` / `on_unequip_slot` for the Equipment tab.
- Equipment frontend is in place: the main menu has a dedicated Equipment tab, right-click Equip/Unequip menus, slot placeholder icons, stat totals, and bonus/requirement tooltips.
- Combat V1 ordinary training is in place. `combat_data.py` seeds the first
  source-backed enabled enemies (Chicken, Rat, Giant rat, Cow), melee attack
  styles, food healing values, and combat drop items from local 2011Scape
  source paths. `apply_combat_burst_pure()` simulates bounded 0.6s-tick combat
  bursts from `Actions per review`, caps each successful review at one kill,
  persists player/enemy lifepoints, applies source-shaped melee accuracy/max-hit
  formulas, awards damage-based Attack/Strength/Defence/controlled/Constitution
  XP, rolls guaranteed and per-table drops, consumes configured auto-eat food,
  and snapshots the result for undo-safe review transactions. Combat appears as
  a synthetic Skills-hub action with target and attack-style controls, HUD
  lifepoint/target state, runtime dispatch/telemetry/save handling, storage
  defaults/migration, and focused unit/integration/offscreen Qt coverage.
- Combat recovery/loadout foundation is in place. Storage config version 22
  adds additive flat fields for `combat_supply_loadout`,
  `combat_special_attack_energy`, `combat_stat_drains`,
  `combat_status_effects`, and `combat_recovery_progress`. Auto-eat now consumes
  from a finite carried food loadout, not the whole Bank mid-fight; fresh
  targets, kills, and safe noncombat recovery can refill that loadout from the
  configured food priority. Safe noncombat reviews apply one rollback-safe
  recovery packet per card, healing or decaying lifepoints by 100, regenerating
  10 special-attack energy per 50 review ticks, recovering stat drains one
  level per 100 safe ticks, advancing simple grave recovery, and exposing food
  readiness in Combat target tooltips.
- Combat bootstrap now includes a source-backed Tutorial Island starter kit as a
  one-time Bank Claim. Generic `item_bundle` claims grant the source bundle
  through the existing Bank Claims UI, storage config version 23 seeds the flat
  claim flag for existing saves, and `combatitems/` now holds fetched Wooden
  shield/Tinderbox icons through `COMBAT_ITEM_IMAGES`.

## What Is Not Built Yet
- Full action metadata beyond the current review-action dispatch registry, runtime handler contract, target-row metadata contract, and achievement metadata contract.
- Combat follow-ups beyond V1 ordinary training: broader source-backed enemy
  import, ranged/magic/ammo/rune combat routing, richer assets, food/potion/
  ammo/rune loadout controls, confirmation UX for dangerous targets, full
  Death's Office recovery and stacked-death handling, and migrating quest combat
  gates from the lightweight resolver onto the shared combat engine. Broad
  non-Smithing combat equipment import/equip support is also still open; Wooden
  shield is currently claimable but not proof that all shield mechanics are done.
- Full quest-stage minute-detail parity. The generator now preserves broad
  quest-wide source fields, but exact per-stage placement, override merge/source
  reconciliation, route flags, required action flags, partner/branch state,
  quest-specific item transformations, and broad combat stat enrichment are
  still tracked in
  `memory-bank/source-audits/quest-stage-gates-catalog-wide-2026-06-22.md`,
  `memory-bank/source-audits/quest-combat-resolver-contract-2026-06-22.md`, and
  `memory-bank/source-audits/quest-style-aware-combat-resolver-2026-06-22.md`,
  `memory-bank/source-audits/quest-darkan-beast-stat-fallback-2026-06-22.md`,
  and
  `memory-bank/source-audits/quest-a-souls-bane-dorgeshuun-combat-split-2026-06-22.md`, and
  `memory-bank/source-audits/quest-demon-slayer-stage-detail-2026-06-22.md`, and
  `memory-bank/source-audits/quest-shield-of-arrav-stage-detail-2026-06-22.md`, and
  `memory-bank/source-audits/quest-merlins-crystal-stage-detail-2026-06-22.md`, and
  `memory-bank/source-audits/quest-generated-combat-name-matching-2026-06-22.md`, and
  `memory-bank/source-audits/quest-local-noncombat-stage-batch-2026-06-22.md`, and
  `memory-bank/source-audits/quest-sheep-herder-stage-detail-2026-06-22.md`, and
  `memory-bank/source-audits/quest-plague-city-waterfall-stage-detail-2026-06-22.md`, and
  `memory-bank/source-audits/quest-biohazard-stage-detail-2026-06-22.md`, and
  `memory-bank/source-audits/quest-heroes-quest-stage-detail-2026-06-22.md`.
- Real acquisition loops for dependency-heavy Crafting inputs such as dragonstone, onyx, hides, molten glass, battlestaff orbs, and some weaving/spinning materials.
- Full long-term balancing pass and a dedicated telemetry/stats UI.
- A release-quality expansion spec.
- Backfilled provenance for older bundled assets that predate the current scraper/provenance workflow.
- Firemaking bonfires and fire spirits; they are pre-EOC but intentionally deferred as a separate extension.
- Fishing Dungeoneering fish, Fishing Trawler outputs, quest-only fish, Fish Flingers, and a real shop/GE material economy; they are intentionally deferred as separate systems rather than folded into ordinary Fishing v1.
- Cooking follow-ups that need broader systems: cleaner Farming/Combat/shop/GE acquisition routes for some prep ingredients, and any recipe families not represented in the local `CookingData.kt` table.
- Runecrafting follow-ups that need broader systems: Magic Imbue, Wicked hood daily essence/runes/teleports/reclaim, Abyss routing/abyssal creatures, talisman sourcing, and broader rune economy routes.
- Hunter follow-ups that need broader systems: tracking trails, pitfall trapping, rabbit snaring, barehand catches, Herblore Habitat/Jadinkos, grenwall herb drops, and richer partial-route modeling for Regicide-start content.
- A compelling shop/GE interface is still not built. The Hunter supply row is deliberately a narrow bridge, not a final shopping UX or economy model.

## Frontend Progress
- The main menu top bar now holds global sections only: Skills, Bank, Stats, Achievements, Settings. The four per-skill top tabs were removed.
- A registry-driven Skills hub replaces them: category filter -> skill list -> target list. Categories/skills come from `skill_hub.build_skill_hub`, backed by `skill_registry`.
- Normal mode shows only playable skills; developer mode additionally surfaces the planned catalog as disabled entries.
- Active-skill selection (Train/Stop training), Smithing/Crafting availability gating, and the live `refresh_skill_availability` hook are preserved through the hub's per-skill panel.
- Skills-hub clicks now correctly drive the target panel. A closure name collision (`_select_skill` redefined by the Stats tab in the same `show_main_menu` scope) had been shadowing the hub handler; the hub helper is now `_select_hub_skill`. Covered by offscreen Qt behavior tests.

## Known Technical Debt
- Some existing skill assumptions still live in frontend/UI surfaces outside the target-row renderers, especially stats, icons, and large menu sections.
- `constants.py` still mixes paths, data tables, and progression constants.
- `__init__.py` still owns Anki orchestration, menu callback wiring, and review transaction coordination, though review-action mutation bodies and duplicated can-start/handler maps now live outside it.
- `ui.py` is large and mixes many dialogs/surfaces.
- The backend registry currently preserves flat save keys for safety; a deeper nested save model remains deferred.
- The runtime answer path now uses `action_registry.py` for Skill/Utility handler-key resolution and `runtime_actions.py` for handler-keyed can-start checks plus review mutation bodies; broader action metadata is still incomplete.
- Flat and grouped target rows now use `target_metadata.py`; Qt still owns rendering, group expansion persistence, and click handling.
- Achievements now use `achievement_metadata.py`; future achievement additions should go through that contract instead of rebuilding grouped UI state by hand.
- The current future-thread priority board lives in `memory-bank/future-work-kanban.md`.

## Current Status
Documentation seed completed as of 2026-05-27. The working copy has been moved to `addons21/ankiscape_fork` to avoid AnkiWeb update overwrites against the numeric upstream folder.

Backend registry foundation completed as an initial pass on 2026-05-29. The full unit/integration suite passes with 81 tests.

Frontend Skills-hub conversion completed on 2026-05-29: the per-skill top tabs collapsed into one registry-driven Skills hub, leaving the top bar for global sections only. Suite now passes with 87 tests (6 new `skill_hub` view-model tests).

Asset scraper CLI completed on 2026-05-29. Suite now passes with 92 tests, including mocked OSRS hit, OSRS miss/RS3 fallback, key/path resolution, skip-if-present, and dry-run coverage.

Fletching frontend slice completed on 2026-05-29. The backend pilot's `visible_in_skill_hub` gate is now open: Fletching appears under Artisan with its own target panel (`_build_fletch_list`), level/material gating via `can_fletch_item_pure`, active-skill gating + warning, an `on_set_fletch` callback wired through `__init__`, and a live-availability slot (`fletch_btn`, optional 3rd arg to `refresh_skill_availability`). Skill icon fetched from the OSRS wiki `(detail)` variant via `tools/fetch_assets.py`. Covered by a new offscreen Qt test. Historical note: per-tier arrow-shaft yields and the feather/arrowtip chain were still incomplete at this point; later passes added the Fletching chain and Smithing-owned arrowtips.

Skills-hub click bug fixed on 2026-05-29. Introduced an offscreen Qt behavior-test loop (`.venv-qt` with `aqt`, `QT_QPA_PLATFORM=offscreen`) that builds the real dialog and drives the widgets — no Anki restart needed. `tests/test_main_menu_widget.py` asserts that selecting Woodcutting and Artisan -> Crafting updates the panel. The core `run_tests.py` suite (95 tests) skips these when `aqt` is absent.

Fletching backend pilot completed on 2026-05-29. Fletching began backend-playable behind the registry; its frontend target list later landed and is now visible in normal Skills-hub mode. The original suite passed with 99 tests, including pure Fletching logic, storage defaults/migration, registry visibility/dispatch metadata, item manifest coverage, integration review handling, and offscreen Qt menu behavior.

Fletching data and asset hardening completed on 2026-05-29. Recipe targets now use stable keys, model per-log arrow-shaft yields, add headless arrows and bronze-through-rune arrows, include Fletching materials in inventory defaults, and scrape 21 normalized PNG icons into `fletcheditems/` with provenance. Suite passes with 100 tests via `.venv-qt` unittest discovery.

Fletching source integration completed on 2026-06-19. The earlier per-log
arrow-shaft pilot rows were corrected back to the local 2011Scape source shape:
only normal logs make arrow shafts. Source-backed Fletching data now lives in
`fletching_data.py` with grouped rows for whittling, stringing, arrows,
feathering, bolts, darts, and specials; `constants.FLETCHING_DATA` remains an
imported compatibility export. The table includes short/long bow stringing,
crossbow stock carving, ogre shaft/flighted ogre rows, broad arrows/bolts,
dragon arrows/darts, bolt feathering, gem/pearl bolt-tip cutting, tipped bolts,
and mithril grapple attachment. Crossbow limb attachment/stringing, enchanted
bolts, and commented comp ogre bow stringing remain excluded. Generic target
unlock rules now support `quest_completed` and `ability_unlocked`, backed by
flat `unlocked_abilities`; broad Fletching and Barbarian Fishing use that path.
Fishing side XP moved to normalized `xp_rewards`, and runtime awards all reward
entries through existing flat exp/level keys. Fletching now renders through the
grouped target tree, and `tools/fetch_fletching_assets.py` fetched the generated
manifest into `fletcheditems/`. Verification: `python3 run_tests.py` passes with
363 tests (86 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passes with 363 tests.

Review undo rollback completed on 2026-05-29. `state_did_undo` restores the `player_data` keys changed by the latest review reward so undoing an answered card also removes the associated XP/items. Suite passes with 105 tests.

AnkiScape skill expansion project skill created on 2026-05-29. It documents the required workflow for source audits, scope cuts, data modeling, asset scraping, mechanics, UI, achievements, tests, manual Anki checks, and memory updates.

Crafting/Utility backend rework completed on 2026-05-29. `Soft clay` moved out of Crafting XP data into batched no-XP Utility/Activities; audited Crafting pilot actions now cover pottery shaping/firing, ball of wool, bow string, and silver bolts (unf). New icons for wool, flax, ball of wool, bow string, and silver bolts (unf) were fetched with provenance. Suite passes with 117 tests in both `python3 run_tests.py` and the offscreen Qt unittest loop.

Woodcutting backend parity completed on 2026-06-01. `woodcutting_data.py` captures the local 2011Scape source audit; `TREE_DATA` now uses stable IDs and real output item names; Fletching consumes real log keys; storage config version is 7 with legacy log/target migration and bound Bronze hatchet seeding; bird nests can drop from Woodcutting and open through no-XP Utility. Core and offscreen Qt suites pass with 134 tests.

Mining backend parity completed on 2026-06-01. `mining_data.py` captures the local 2011Scape source audit plus the scoped simple historical targets; `ORE_DATA` now uses stable IDs and real output item names; storage config version 8 handles legacy target migration and bound Bronze pickaxe seeding, and storage config version 10 later moved Mining bonus gear into worn `equipment`; the item manifest carries `tradeable` and minimal equipable metadata. `python3 -m unittest discover -s tests` passes with 154 tests (18 skipped).

Review action multiplier completed on 2026-06-01. Runtime reads the new `ankiscape_review_action_multiplier` setting, falls back to the legacy XP multiplier key, and executes integer action ticks per eligible review with aggregate feedback and one undo snapshot. Settings now show a simple `Actions per review` +/- spinner. `python3 run_tests.py` passes with 165 tests (26 skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passes with 165 tests.

Smithing 2011Scape backend parity completed on 2026-06-01. `python3 run_tests.py` passes with 172 tests (26 skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passes with 172 tests.

Equipment backend completed on 2026-06-02. `tools/generate_equipment_data.py` emits `equipment_data.py` from Smithing recipe metadata, 2011Scape `items.yml` equipment blocks, and Mining bonus items. Storage config version is 10 with `equipment` save state and combat defaults. `python3 run_tests.py` passes with 197 tests (37 skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passes with 197 tests.

Equipment frontend completed on 2026-06-02. The main menu now owns worn gear in a dedicated Equipment tab instead of a Bank placeholder, with slot icons, stat totals, right-click Equip/Unequip, disabled lock reasons, and tooltip coverage.

Crafting 2011Scape backend parity foundation completed on 2026-06-03. `python3 run_tests.py` passes with 212 tests (47 skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passes with 212 tests.

Crafting frontend grouping/assets completed on 2026-06-03. Current local verification on 2026-06-15: `python3 run_tests.py` passes with 230 tests (57 skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passes with 230 tests.

P0 review-action dispatch cleanup completed on 2026-06-15. `action_registry.py`
now resolves Mining, Woodcutting, Smithing, Crafting, Fletching, and
Utility/Activities aliases to review handler keys; `__init__.py` uses that
registry for answer eligibility/handler lookup, and multi-action readiness now
dispatches through a handler-keyed map instead of a long skill-name branch. No
storage migration or frontend visual change was needed. `python3 run_tests.py`
passes with 233 tests (57 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passes with 233 tests.

P0 flat target-list metadata cleanup completed on 2026-06-16. `target_metadata.py`
now produces pure `TargetRowMetadata` rows for Mining, Woodcutting, Fletching,
Firemaking, Fishing, and Utility/Activities. `ui.show_main_menu` renders those
rows through one shared `QListWidget` helper, preserving disabled-row click
guards, tooltips, icons, active-target highlighting, flat save keys, XP/item
math, action multiplier behavior, and undo rollback. Smithing and Crafting stay
on their grouped `QTreeWidget` builders for now. `python3 run_tests.py` passes
with 287 tests (69 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passes with 287 tests.

P0 grouped target-tree metadata cleanup completed on 2026-06-19. `target_metadata.py`
now also produces grouped `TargetRowMetadata` rows for Smithing, Crafting,
Cooking, and Runecrafting, including group ids, sort keys, icon paths,
current-target state, enabled state, and level/material/quest lock reasons.
`logic_pure.py` added Smithing and Crafting locked-reason helpers to match the
existing Cooking and Runecrafting quest-aware helpers. `ui.show_main_menu`
renders those grouped rows through one shared `QTreeWidget` helper while
preserving existing group role ids, Smithing/Crafting expand-state persistence,
Cooking/Runecrafting current-target auto-expand, tooltips, icons, and
disabled-row click guards. No save schema, recipe data, XP math, item rewards,
or quest rules changed. `python3 run_tests.py` passes with 345 tests (83
skipped), and the offscreen Qt discovery suite passes with 345 tests.

P0 runtime handler extraction completed on 2026-06-19. `runtime_actions.py`
now owns the review-action mutation bodies and handler-keyed readiness checks
for Mining, Woodcutting, Fishing, Smithing, Crafting, Fletching, Firemaking,
Cooking, Runecrafting, Quests, and Utility/Activities. `__init__.py` keeps
Anki hooks, global player state, review transaction/undo handling, menu
callback wiring, and thin `on_<skill>_answer` wrappers that pass a
`RuntimeActionContext`. No save schema, XP math, recipe/target data, item
rewards, quest rules, assets, or frontend UI changed. `python3 run_tests.py`
passes with 347 tests (83 skipped), and the offscreen Qt discovery suite passes
with 347 tests.

P0 achievement metadata and final handler-plumbing cleanup completed on
2026-06-19. `achievement_metadata.py` now owns the 105 achievement definitions,
the shared difficulty order, grouped row models, and progress-count helpers,
while `constants.ACHIEVEMENTS` remains a compatibility export for the legacy
dict shape used by achievement checks. The main menu Achievements tab and the
standalone achievement dialog render from the shared metadata helpers instead
of rebuilding difficulty buckets locally. `__init__.py` no longer keeps duplicate
per-skill can-start helpers or a private review-handler map; it resolves handler
keys through `action_registry.py` and calls `runtime_actions.py` directly. No
save schema, achievement names, completion semantics, XP math, item rewards,
quest rules, target metadata, or visual behavior changed. `python3 run_tests.py`
passes with 352 tests (84 skipped), and the offscreen Qt discovery suite passes
with 352 tests.

P2 feather source completed on 2026-06-15. Added `Scavenge chicken feathers` as
a no-input Utility/Activities action with a dedicated activity icon and
source-audit note. It grants `28 Feather` per successful action tick, awards no
skill XP, supports the action multiplier and Anki undo rollback, and leaves
Fletching recipes plus Smithing-owned arrowtips unchanged. `python3 run_tests.py`
passes with 240 tests (59 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passes with 240 tests.

P1 Utility/Activities icon set completed on 2026-06-15. Existing Utility rows
now resolve activity-level icons from `UTILITY_ACTIVITY_DATA["icon_path"]` into
`activityicons/`, with output-item art as the frontend fallback. The pass added
no new activities, acquisition loops, storage keys, or XP behavior. Asset
provenance is recorded for all four new row icons. `python3 run_tests.py` passes
with 235 tests (58 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passes with 235 tests.

Firemaking v1 completed on 2026-06-16. The skill is a current Artisan review
skill with 13 local-2011Scape burnable targets, success-only log consumption,
source XP, `Ashes x1`, item/icon registration, achievements, storage config
version 12, runtime review dispatch, action multiplier support, undo rollback,
and Qt target-list coverage. Bonfires/fire spirits are recorded as deferred
2012 pre-EOC extension content in
`memory-bank/source-audits/firemaking-2011scape-2026-06-16.md`.

Fishing v1 completed on 2026-06-16. The skill is a current Gathering review
skill with 15 live local-2011Scape `FishingSpot.kt` behaviors, stable
`current_fishing` IDs, output-first labels, source XP and min/max chance data,
ordered mixed-output rolls, material use only on successful catches, hidden
Strength/Agility side XP for Barbarian fish, storage config version 13,
achievements, assets, item/icon registration, Utility `Gather fishing bait`,
runtime review dispatch, action multiplier support, undo rollback, and Qt
target-list coverage. The source audit records that the 2011-to-pre-EOC wiki
gap adds no missing ordinary catch method for this v1; Stone fish, Fish Flingers,
cosmetics, Dungeoneering fish, and Fishing Trawler stay deferred. `python3 run_tests.py`
passes with 281 tests (69 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passes with 281 tests.

Cooking v1 completed on 2026-06-16. The skill is a current Artisan review skill
with 54 local-2011Scape Cooking targets, no-XP Utility prep bridges, stable
`current_cooking` IDs, source XP and low/high chance data, review-scale success
probabilities, raw consumption on both success and burn failure, burnt-item junk
outputs, storage config version 14, achievements, assets, item/icon
registration, runtime review dispatch, action multiplier support, undo rollback,
grouped Cooking and Utility target-list coverage, and confirmed Bank discard-all
for every item. The source audit is
`memory-bank/source-audits/cooking-2011scape-2026-06-16.md`.

Runecrafting v1 completed on 2026-06-17. The skill is a current Artisan review
skill with 61 local-2011Scape-backed targets, stable `current_runecrafting`
IDs, source XP, standard/combination/tiara/hood action families, Rune
Mysteries as a review-driven Quest action, Wicked hood as a one-time Bank
Claim, pouch capacity/degradation, Binding necklace state stored as
`item_charges["Binding necklace"]`, storage config version 15, achievements,
assets, item/icon registration, runtime review dispatch, action multiplier
support, undo rollback, and Qt coverage for Runecrafting, Quests, Bank Claims,
Stats, Bank, and HUD. The source audit is
`memory-bank/source-audits/runecrafting-2011scape-2026-06-17.md`.
`python3 run_tests.py` passes with 317 tests (79 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passes with 317 tests.

Hunter supply bridge completed on 2026-06-20. `hunter_data.py` now carries
reusable `tools` gates separately from consumed `requirements`, and
`Buy Hunter supplies` is registered as a one-shot Utility/Activities bridge
using source-backed Darkan shop stock plus a temporary `500 Coins` AnkiScape
bundle price. Utility pure logic, target metadata, runtime dispatch, and the
item manifest now support multi-output one-shot activities. Newly fetched Hunter
gear icons live in `hunteritems/` with provenance. The broader shop/GE UX is
still deferred. `python3 run_tests.py` passes with 377 tests (89 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passes with 377 tests.

Full pre-EOC Quest catalog second pass completed on 2026-06-17.
`tools/build_pre_eoc_quest_catalog.py` generates `quest_catalog_generated.py`
with 194 quest rows available before the 2012-11-20 Evolution of Combat cutoff,
counting Recipe for Disaster as 10 separate subquests. The generated catalog
uses cached RuneScape Wiki old revisions, local 2011Scape `QuestStage`
journals where available, quick-guide checklist stages for most quests, and a
source-page walkthrough fallback for Black Knights' Fortress so no quest ships
with generated placeholder journals. `quest_data.py` imports the generated
catalog, predeclares generated item rewards, and turns XP lamp rewards into
Bank Claims with preserved skill choices and minimum-level requirements.
Strict quest starts block on incomplete prerequisite quests and on
unimplemented required skills; XP rewards for unimplemented skills are parked
in `pending_skill_exp_rewards`. The Quests tab renders the full catalog as
collapsed sortable cards and sorts release order by real-game release order.
Shilo Village now gates the generic Mining `gem_rocks` target by owner choice
until a route/location model exists. Verification: `python3 run_tests.py`
passes with 336 tests (80 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passes with 336 tests.

Quest route-precedent follow-up completed on 2026-06-18. Priest in Peril now
gates Fishing `catch_slimy_eel`, Cooking slimy eel/snail rows, and Utility snail
gathering; The Fremennik Isles now gates Firemaking `arctic_pine_logs`, Cooking
`cook_yak`, and Utility `scavenge_raw_yak_meat`. This is a narrow exception to
the old route-gate caution: the lock is allowed when the current generic target
effectively represents the locked region route. Verification: `python3
run_tests.py` passed with 342 tests (83 skipped), and `QT_QPA_PLATFORM=offscreen
.venv-qt/bin/python -m unittest discover tests` passed with 342 tests.

Quest-list filtering completed on 2026-06-19. `quest_availability_state_pure()`
classifies quest cards as `can_start`, `in_progress`, `completed`, or `locked`,
and the Quests tab can now hide completed quests, hide quests unable to start,
and filter by Access, Difficulty, Length, and Timeline while preserving release
order and other existing sorts. Started quests remain `in_progress` under the
current review-driven quest model; start filters do not attempt to model future
mid-quest completion blockers. Verification: `python3 run_tests.py` passed with
366 tests (88 skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 366 tests.

Quest completion modal UX completed on 2026-06-22. `runtime_actions.handle_quest_answer()`
now shows a `Quest complete` dialog after a quest reaches its final stage,
reusing the same centralized warning-dialog path as material depletion while
preserving reward application, telemetry, save/refresh, floating completion
feedback, and `current_skill -> "None"`. Verification: `python3 -m unittest
tests.test_runtime_actions`, `python3 -m unittest tests.test_integration_smoke`,
`python3 run_tests.py`, and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m
unittest discover tests` all pass.

Quest stage-gate foundation completed on 2026-06-22. `quest_data.py` now has
structured `QuestStageRequirement` and `QuestCombatEncounter` models layered
through the override path, `logic_pure.py` exposes current-stage blocker helpers
and `can_progress_quest_pure()`, `runtime_actions.handle_quest_answer()` refuses
blocked quest reviews without applying rewards, and the Quests tab shows
`blocked_at_stage` reasons while preserving start-lock filters. The Knight's
Sword is the proof case: Mining 10 remains the only start lock, the Requirements
line lists Redberry pie, Blurite ore, and two Iron bars as used during the quest,
Redberry pie is consumed at Thurgo's stage, Blurite ore and Iron bars are
consumed at the later materials stage, and 12,725 Smithing XP only fires on
valid completion. Full all-quest stage parity, route/action extraction, and
combat blockers remain deferred in
`memory-bank/source-audits/quest-stage-gates-2026-06-22.md`. Verification:
`python3 run_tests.py` passed with 396 tests (91 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 396 tests.

Quest no-stage closure slice completed on 2026-06-22. `quest_data.py` now
combines generated stage rows with focused source-backed replacement/addition
rows so the audit reports 194/194 quests with at least one machine-readable
stage requirement. The slice closes the prior no-stage list, corrects Lost City
to the local/Darkan level 63 Tree spirit gate instead of the generated level
101 row, adds required-action blockers for source-backed delivery/puzzle/route
steps such as Rune Mysteries, The Restless Ghost, Deadliest Catch, Wolf Whistle,
Song from the Depths, Carnillean Rising, and Some Like It Cold, and keeps combat
globally fail-closed. Full minute-detail parity remains open: generated
per-stage extraction, quest-item transformations, route/puzzle/follower state,
combat stat enrichment, and full combat simulation still need more source
work. Focused verification passed with `python3 -m unittest
tests.test_quest_catalog tests.test_logic tests.test_runtime_actions
tests.test_integration_smoke`, four targeted Qt quest-tab tests, and
`python3 tools/audit_quest_stage_gate_coverage.py`.

Quest combat resolver contract slice completed on 2026-06-22. The global flat
save gate `quest_combat_config.resolver_enabled` still defaults closed, but
when enabled the Quest review action now resolves one stat-backed current-stage
combat encounter through `logic_pure.apply_quest_combat_encounter_pure()` before
normal quest progression can continue. The resolver uses the local 2011Scape
player combat-level formula, requires source-backed NPC hitpoints/attack/
strength/defence stats, distinguishes global lock, missing stats, underpowered
player, and battle-ready states, and writes completed ids into
`quest_combat_encounters` without advancing the quest stage on the same review.
The Quests tab can select a resolver-ready battle while keeping noncombat,
missing-stat, underpowered, and globally locked blockers disabled. This is not
full combat parity: broad NPC stat enrichment, hit chance/max-hit/equipment/
food/prayer/death simulation, and quest-specific mechanics remain deferred in
`memory-bank/source-audits/quest-combat-resolver-contract-2026-06-22.md`.

Quest combat quantity slice completed on 2026-06-22. The generator now parses
worded combat quantities into `quantity` rows, and runtime uses
`quest_combat_encounter_counts` so one Quest review resolves one enemy. For
example, TokTz-Ket-Dill's sourced "Two Lava monsters" row now remains blocked
after the first Lava monster and only writes
`quest_combat_encounters["toktz_ket_dill"] = ["toktz_ket_dill_lava_monster_47"]`
after the second. Stat coverage remains 159/285; the 126 statless rows are
still hard blockers, not completed content.
Verification: `python3 run_tests.py` passed with 436 tests (102 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 436 tests.

Quest combat stat enrichment follow-up completed on 2026-06-22. The Restless
Ghost Skeleton Warlock focused stage addition now carries local 2011Scape NPC
stats from `skeleton_warlock_lvl_11.plugin.kts`, with quest text and skull
object spawn behavior cited in `quest_data.py`. This proves focused override
combat rows can become resolver-ready without hand-editing
`quest_catalog_generated.py`: after the skull-search action flag is present,
the Quests tab shows `Blocked: Battle required: Skeleton warlock level 11` and
the Quest review writes `the_restless_ghost_skeleton_warlock` before stage
advancement. `python3 tools/audit_quest_stage_gate_coverage.py` then reported
16/286 combat encounters with local stats; the remaining statless rows were
explicit broad combat enrichment debt. Verification: `python3 run_tests.py`
passed with 406 tests (95 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 406 tests.

Quest Darkan combat stat enrichment follow-up completed on 2026-06-22. The
catalog generator now keeps local 2011Scape NPC definitions as the first source
for generated combat encounters, then falls back to Darkan/2012scape combatdef
JSON plus `developer-information/npcList.txt` for exact unambiguous NPC
name+combat-level matches. Ambiguous duplicate sources and wrong-level matches
stay statless, so the global combat resolver still blocks them as missing
stats. The proof cases are Demon Slayer's Delrith and Dragon Slayer's Elvarg,
while Lost City's level 63 Tree spirit and Elemental Workshop's level 35 Earth
Elemental remain blocked because the local sources do not provide safe exact
matches. `python3 tools/audit_quest_stage_gate_coverage.py` now reports
141/286 combat encounters with source-backed stats; the remaining 145 rows are
explicit combat stat/source reconciliation debt.

Quest identical combat-source enrichment follow-up completed on 2026-06-22.
The Darkan generator fallback now treats duplicate exact name+combat-level
sources as usable only when all captured battle stats/configs are identical,
and records every contributing source path in `npc_stats_source`. This makes
Elemental Workshop's Earth Elemental rows resolver-ready without accepting
genuine conflicts: Priest in Peril's Monk of Zamorak and Troll Stronghold's Dad
were then resolved with focused area-specific Darkan quest/combat evidence. The
focused override layer also gained Darkan-backed Jogre stats for Tai Bwo Wannai
Trio and Sea Troll Queen stats for Swan Song. The generator now preserves
`required_inventory_options` as independent option groups, so source rows such
as Goblin Diplomacy's dye alternatives do not become start locks or impossible
all-item requirements. `python3 tools/audit_quest_stage_gate_coverage.py`
reported 169/287 combat encounters with source-backed stats at that slice's
close after the Darkan
beast fallbacks and focused name-shape replacements; the remaining 118 rows are
classified by `tools/audit_quest_combat_stat_gaps.py` as 51 Darkan
hitpoints-only rows, 18 Darkan rows missing style-critical resolver stats, 9
same-name/wrong-level rows, 13 no-local-source rows, and 27
parser/variant-level rows.

Quest focused combat row-split follow-up completed on 2026-06-22. The focused
combat replacement layer in `quest_data.py` can now replace one generated
combat encounter with multiple source-backed encounters without replacing the
quest's other generated stage rows. Heroes' Quest's Entrana Fire Bird now uses
Darkan `entrana_firebird.json`, Spirits of the Elid's generated `Golem x3` row
splits into Black, White, and Grey golems from Darkan enum/combatdef evidence,
and Another Slice of H.A.M.'s historical H.A.M. ranger row maps to Darkan's
level 30 H.A.M. Archer ranged payload. Audit coverage is 169/287
resolver-ready combat rows with 118 statless rows still blocked; full
minute-detail quest parity remains open.

A Soul's Bane and Death to the Dorgeshuun combat-stage follow-up completed on
2026-06-22. A Soul's Bane now replaces bad generated anger-room combat rows with
a required-action rage meter gate, then splits the fear, confusion,
hopelessness, and Tolna rooms into sourced Darkan multi-count combat gates.
Death to the Dorgeshuun's generated `Senior guard x3` row now maps to
`Senior H.A.M. guard` with level 22 local Darkan combatdef stats. Current audit
coverage at that slice was 174/283 resolver-ready combat rows with 109 statless rows still
blocked; full minute-detail quest parity remains open.

Historical wiki combat-stat source-tier audit completed on 2026-06-22. The new
`tools/audit_quest_historical_wiki_combat_stats.py` checks the remaining 109
unresolved combat rows against pinned historical RuneScape Wiki monster pages
through the 2012-11-19 cutoff, with cached/retried API fetches. It found 77
metadata-only pages and 32 rows without monster metadata, but 0 rows with the
hidden resolver stats needed to unblock combat. `tools/audit_quest_combat_stat_gaps.py`
now treats unresolved combat debt as "not resolver-ready" rather than merely
"empty `npc_stats`", so future HP-only metadata cannot hide remaining blockers.
Fight Arena's Khazard scorpion/ogre are the Qt regression example: their
historical pages expose LP/style/max-hit only, so they stay blocked while
Bouncer remains resolvable.

Priest in Peril focused stage-detail slice completed on 2026-06-22. Backend:
`QuestStageRequirement` now supports `consumed_inventory_options`, the blocker
path treats those alternatives as current-stage item requirements, and stage
completion consumes whichever valid alternative group the player actually has.
`quest_data.py` replaces Priest in Peril's generated stage-61/prose-parser rows
with a nine-stage source-backed override from local 2011Scape plus Darkan:
Paterdomus door action, Temple guardian dog combat, King Roald report, Drezel
cell discovery, Monk of Zamorak key combat, monument key swap/cell unlock,
bucket/blessed-water coffin action, and 50 Rune essence or 25 Pure essence
Salve purification. Wolfbane dagger and 1,406 Prayer XP now fire only on valid
completion; Prayer XP remains in `pending_skill_exp_rewards` because Prayer is
not implemented as a live skill. Frontend: the existing Quests tab blocker
surface now shows the Priest in Peril essence blocker, with offscreen Qt
coverage. Post-slice audit reports 389 stage rows, 60 focused rows, 329
generated rows, 283 combat encounters, and 174 resolver-ready combat encounters.
Full all-quest minute-detail parity remains open. Source audit:
`memory-bank/source-audits/quest-priest-in-peril-stage-detail-2026-06-22.md`.
Verification: `python3 run_tests.py` passed with 459 tests (107 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 459 tests.

2011Scape starter quest stage batch completed on 2026-06-22. Backend:
`QuestStageRequirement` now supports `produced_inventory`, and
`apply_quest_progress_pure()` can add source-created quest items during a
successful current-stage transition. `quest_data.py` now replaces bad generated
rows for Cook's Assistant, Imp Catcher, Druidic Ritual, Pirate's Treasure, and
Vampyre Slayer through focused source-backed overrides: Cook consumes
top-quality milk, extra fine flour, and super large egg; Imp Catcher consumes
the four beads and no longer grants generated coins; Druidic Ritual transforms
raw meats into enchanted meats before Sanfew/Kaqemeex; Pirate's Treasure
produces Chest key and Pirate message; Vampyre Slayer keeps garlic optional,
produces stake/stake hammer from Dr Harlow, resolves Count Draynor at stage 3,
consumes the stake after the combat gate, and requires Morgan before awarding
Attack XP. Frontend: the existing Quests tab blocker surface now has offscreen
Qt coverage for the combined Cook's Assistant missing-ingredient blocker.
Post-slice audit reports 395 stage rows, 70 focused rows, 325 generated rows,
283 combat encounters, 174 resolver-ready combat encounters, and 4
produced-inventory rows. Full all-quest minute-detail parity remains open.
Source audit:
`memory-bank/source-audits/quest-2011scape-starter-stage-batch-2026-06-22.md`.
Verification: `python3 run_tests.py` passed with 463 tests (108 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 463 tests.

Demon Slayer focused stage replacement completed on 2026-06-22. Backend:
`quest_data.py` now replaces Demon Slayer's broad generated row with a
Darkan-backed nine-stage flow: coin at Gypsy Aris, bucket water and drained key,
25 bones for Traiborn, Captain Rovin's key, three keys converted into
Silverlight, Delrith fought with Silverlight, and the incantation action before
the completion marker. Silverlight is produced during the quest and is not
duplicated as a completion reward. Delrith uses Darkan combat stats and remains
globally locked unless `quest_combat_config.resolver_enabled` is true; supporting
Dark wizards are recorded as source detail until full battle metadata can model
non-required supporting attackers. Frontend: the existing Quests tab blocker
surface now shows Demon Slayer's bucket-water blocker at stage 3 and Delrith as
the stage 7 combat blocker. Assets: `questitems/silverlight.png` and
`questitems/silverlight_key.png` are registered with provenance. Post-slice audit
reports 401 stage rows, 80 focused rows, 321 generated rows, 283 combat
encounters, 175 resolver-ready combat encounters, 174 quests with item/tool
blockers, and 119 quests with combat blockers. Full all-quest minute-detail
parity remains open. Source audit:
`memory-bank/source-audits/quest-demon-slayer-stage-detail-2026-06-22.md`.
Focused verification passed:
`python3 -m unittest tests.test_quest_catalog tests.test_logic tests.test_runtime_actions tests.test_integration_smoke`
and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget tests.test_skill_and_item_registry`.
Required full-suite verification passed: `python3 run_tests.py` passed with 465
tests (108 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 465 tests.

Early Darkan quest stage batch completed on 2026-06-22. Backend: `quest_data.py`
now replaces generated rows for Goblin Diplomacy, Ernest the Chicken, and Black
Knights' Fortress with focused Darkan-backed stage chains. Goblin Diplomacy
consumes orange, blue, and regular goblin mail at their real hand-in stages;
Ernest the Chicken produces and consumes poisoned fish food, pressure gauge,
grimy key, rubber tube, and oil can through Oddenstein's machine-part flow; and
Black Knights' Fortress uses the sourced 12 quest point start requirement, worn
equipment support for the Iron chainbody/Bronze med helm disguise, the cabbage
cauldron sabotage, and the Sir Amik report before completion. Frontend: the
existing Quests tab blocker surface now has offscreen Qt coverage for Ernest's
Fish food/Poison blocker. Assets: quest-stage item icons for the new goblin mail
and Ernest machine-part blockers are registered with provenance. Shield of Arrav
was audited but remains deferred until route-bundle and partner-exchange state
can model Phoenix/Black Arm branches honestly. Post-slice audit reports 412
stage rows, 93 focused rows, 319 generated rows, 283 combat encounters, 175
resolver-ready combat encounters, 174 quests with item/tool blockers, and 119
quests with combat blockers. Full all-quest minute-detail parity remains open.
Source audit:
`memory-bank/source-audits/quest-early-darkan-stage-batch-2026-06-22.md`.
Focused verification passed:
`python3 -m unittest tests.test_logic tests.test_runtime_actions tests.test_integration_smoke tests.test_skill_and_item_registry`
and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget`.

Dragon Slayer focused stage replacement completed on 2026-06-22. Backend:
`quest_data.py` now replaces Dragon Slayer's generated quest-wide row with a
source-backed 16-stage chain: 32 quest points stays a start lock, Oziach and the
Guildmaster are action gates, Maze key and Anti-dragon shield are produced at
their real stages, Melzar's Maze resolves the sourced combat chain before
producing a `Map part`, Wormbrain uses the deterministic 10,000 coin paid route,
the Oracle door consumes `Wizard's mind bomb`, `Silk`, `Bowl (unfired)`, and one
of `Crayfish cage`/`Lobster pot`, the three `Map part` items become `Crandor
map`, the Lady Lumbridge consumes 2,000 coins plus planks/nails/hammer, Ned's
route consumes the map, Elvarg requires an Anti-dragon shield and produces
`Elvarg's head`, and final completion requires reporting to Oziach. Frontend:
the existing Quest tab blocker surface now has offscreen Qt coverage for the
Oracle item-option blocker and Elvarg's resolver-ready battle button. Assets:
quest-stage item icons for the new Dragon Slayer blockers are registered with
provenance. Post-slice audit reports 424 stage rows, 283 combat encounters, 175
resolver-ready combat encounters, 174 quests with item/tool blockers, and 119
quests with combat blockers. Full all-quest minute-detail parity remains open.
Source audit:
`memory-bank/source-audits/quest-dragon-slayer-stage-detail-2026-06-22.md`.
Focused verification passed:
`python3 -m unittest tests.test_quest_catalog.TestQuestCatalog.test_generated_catalog_stage_requirements_cover_items_and_combat`
`python3 -m unittest tests.test_logic.TestLogic.test_dragon_slayer_stage_gates_items_combat_and_completion_rewards`
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_dragon_slayer_oracle_item_option_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_dragon_slayer_elvarg_combat_gate_selection`
`python3 -m unittest tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`
Required full-suite verification passed: `python3 run_tests.py` passed with 471
tests (111 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 471 tests.

Shield of Arrav focused branch-stage replacement completed on 2026-06-22.
Backend: `QuestStageRequirement.variant` now supports mutually exclusive
current-stage route rows without moving finish-only blockers into start locks,
and `quest_data.py` replaces Shield of Arrav's generated branch prose with a
source-backed 12-stage chain. Phoenix Gang and Black Arm Gang are separate
route variants; Jonny the beard and the Weaponsmaster use Darkan combat stats;
Intel report, Weapon store key, Phoenix crossbows, shield halves, half
certificates, and the full certificate are produced/consumed at their real
stages; the opposite half-certificate remains a finish-stage partner exchange
gate; King Roald's valid completion reward is 1,200 coins. Frontend: the
existing Quests tab blocker surface now has offscreen Qt coverage for the
branch decision state. Assets: quest-stage item icons for Shield-specific items
are registered with provenance. Post-slice audit reports 440 stage rows, 285
combat encounters, 177 resolver-ready combat encounters, 174 quests with
item/tool blockers, and 120 quests with combat blockers. Full all-quest
minute-detail parity remains open, with 108 statless combat rows still blocked.
Source audit:
`memory-bank/source-audits/quest-shield-of-arrav-stage-detail-2026-06-22.md`.
Focused verification passed:
`python3 -m unittest tests.test_logic tests.test_quest_catalog tests.test_skill_and_item_registry`
and
`python3 -m unittest tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_resolves_shield_of_arrav_route_combat_gate`
and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_shield_of_arrav_route_branch_blockers`.
Required full-suite verification passed: `python3 run_tests.py` passed with 477
tests (112 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 477 tests.

Witch's House full-stage replacement completed on 2026-06-22. Backend:
`quest_data.py` now supersedes the earlier two-row Witch's House combat proof
with a 12-stage Darkan-backed chain: potted-plant Door key, door-entry action,
cupboard Magnet, Cheese/Magnet mouse-hole mechanism, witch patrol route, Leather
gloves electric gate, fountain Backroom key, shed-door action, four Witch's
experiment forms, Ball pickup, and Harvey hand-in. The quest remains startable
without Cheese, gloves, keys, Magnet, or Ball; Cheese and Ball are consumed at
their real stages, and the sourced 4 quest points plus 6,325 Constitution XP
fire only after Harvey receives the Ball. Frontend: the existing Quest tab
blocker surface now has offscreen Qt coverage for the mouse-hole missing
Cheese/action stage and the stage-9 experiment combat button. Assets:
`questitems/door_key.png`, `questitems/magnet.png`,
`questitems/backroom_key.png`, and `questitems/ball.png` are registered with
provenance. Post-slice audit reports 458 stage rows, 42 produced-inventory rows,
285 combat encounters, 177 resolver-ready combat encounters, 174 quests with
item/tool blockers, and 120 quests with combat blockers. Full all-quest
minute-detail parity remains open, with generated-row and combat-stat gaps still
tracked. Source audit:
`memory-bank/source-audits/quest-witchs-house-stage-detail-2026-06-22.md`.
Focused verification passed:
`python3 -m unittest tests.test_quest_catalog.TestQuestCatalog tests.test_logic.TestLogic.test_witchs_house_stage_gates_items_route_combat_and_reward tests.test_logic.TestLogic.test_witchs_house_experiment_forms_are_resolver_ready tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_blocks_witchs_house_mouse_puzzle_without_stage_item tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_resolves_witchs_house_first_form_combat_gate tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_blocks_witchs_house_mouse_puzzle_without_stage_item tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_resolves_witchs_house_first_form_before_stage_progress tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`
and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_witchs_house_mouse_stage_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_witchs_house_form_combat_gate_selection`.
Required full-suite verification passed: `python3 run_tests.py` passed with 485
tests (114 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 485 tests.

Dwarf Cannon focused stage replacement completed on 2026-06-22. Backend:
`quest_data.py` now replaces the generated level-2 Goblins combat blocker with
a Darkan-backed noncombat stage chain because the local quest handler says
combat is none. The quest has ten source-backed gates plus an 11th completion
state: six railings with a hammer, Lawgof repair report, Gilob's remains,
goblin hideout route, Lollk rescue, toolkit production, cannon repair, repaired
cannon report, Nulodion's ammo mould and notes, and Lawgof's recommendation.
The generated quest reward surface is preserved: one quest point and 750
Crafting XP fire only on valid completion. Assets for `Railing`, `Dwarf
remains`, `Toolkit`, `Nulodion's notes`, and `Ammo mould` are registered with
provenance. Post-slice audit reports 471 stage rows, 47 produced-inventory rows,
284 combat encounters, 179 resolver-ready combat encounters, 174 quests with
item/tool blockers, 119 quests with combat blockers, and 105 statless combat
rows. Full all-quest minute-detail parity remains open. Source audit:
`memory-bank/source-audits/quest-dwarf-cannon-stage-detail-2026-06-22.md`.

Local Darkan noncombat/low-combat quest-stage batch completed on 2026-06-22.
Fishing Contest now produces the fishing pass, consumes the contest fee/garlic,
uses fishing rod plus red vine worm or fishing bait for raw giant carp, and
turns raw giant carp into the trophy before completion. Gertrude's Cat now
models the Shilop/Wilough payment, Lumber Yard route, milk bucket, doogle
sardine, kittens, and Gertrude hand-in. Clock Tower now consumes rat poison and
the four cogs with bucket-of-water or ice-gloves handling. Monk's Friend now
consumes the blanket, jug of water, and logs at Brother Omad/Cedric stages.
Tribal Totem now models Wizard Cromperty, RPDT address-label handling,
Handelmort Mansion actions, and totem return. Scorpion Catcher now produces and
consumes the scorpion cage, route-gates all three scorpions, and gates the
Taverley Dungeon scorpion behind the level 39 jailer combat encounter. New quest
item icons were fetched with provenance. Post-slice audit reports 499 stage
rows, 56 produced-inventory rows, 285 combat encounters, 180 resolver-ready
combat encounters, 174 quests with item/tool blockers, 120 quests with combat
blockers, and 105 statless combat rows. Source audit:
`memory-bank/source-audits/quest-local-noncombat-stage-batch-2026-06-22.md`.
Required verification passed: `python3 run_tests.py` passed with 504 tests (117
skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest
discover tests` passed with 504 tests.

Sheep Herder focused stage replacement completed on 2026-06-22. Backend:
`quest_data.py` now replaces the generated quick-guide row with local
Darkan-backed stages for poisoned sheep feed, Doctor Orbon plague clothing, the
cattleprod route/tool gate, all four sheep-bone incinerations, and the final
Councillor Halgrive report. `Sheep feed` is required but not consumed because
the Darkan utility does not delete it, while red/green/blue/yellow sheep bones
are consumed at the incineration stage. Frontend work was limited to targeted
Quests-tab blocked-at-stage coverage. New quest item icons were fetched with
provenance. Post-slice audit reports 501 stage rows, 58 produced-inventory
rows, 285 combat encounters, 180 resolver-ready combat encounters, 174 quests
with item/tool blockers, 120 quests with combat blockers, and 105 statless
combat rows. Source audit:
`memory-bank/source-audits/quest-sheep-herder-stage-detail-2026-06-22.md`.

Plague City and Waterfall Quest focused stage replacements completed on
2026-06-22. Plague City now uses local Darkan-backed current-stage gates for
dwellberries producing the gas mask, Edmond's mud/sewer sequence, Jethick and
the Rehnisons, Bravek's hangover cure recipe, cure mixing with pestle-and-mortar
tooling, warrant production, prison-house access, Elena's cell key, and the
final Edmond report; the gas mask is no longer duplicated as a final reward.
Waterfall Quest now uses local Darkan-backed stage gates for Hudon, the
Baxtorian book, Golrie's old key and Glarial's pebble, Glarial's tomb amulet and
urn recovery, rune/amulet waterfall completion, and pending Attack/Strength XP
delivery while those combat skills are unimplemented. New quest item icons were
fetched with provenance, including disambiguated `Old key` and `Large old key`
entries for Darkan's two quest `A key` IDs. Frontend work was limited to targeted
Quests-tab blocked-at-stage coverage. Post-slice audit reports 519 stage rows,
68 produced-inventory rows, 285 combat encounters, 180 resolver-ready combat
encounters, 174 quests with item/tool blockers, 120 quests with combat blockers,
and 105 statless combat rows. Source audit:
`memory-bank/source-audits/quest-plague-city-waterfall-stage-detail-2026-06-22.md`.

Heroes' Quest focused stage replacement completed on 2026-06-22. Backend:
`quest_data.py` now replaces generated/broad rows with a Darkan-backed
13-stage chain for Achietties' challenge, Gerrant's Blamish snail slime,
Blamish oil mixing, oily fishing rod creation, raw/cooked lava eel handling,
Ice Queen/Ice gloves, Entrana Fire feather, Black Arm and Phoenix route variants,
ScarFace Pete's candlestick, Thieves' armband, and the final Lava eel/Fire
feather/armband hand-in. The quest keeps its strict start locks: 56 quest
points, Shield of Arrav, Lost City, Dragon Slayer, Merlin's Crystal, Druidic
Ritual, and the sourced Cooking/Fishing/Herblore/Defence/Mining levels.
Frontend work was limited to targeted Quests-tab blocked-at-stage coverage. New
quest item icons were fetched with provenance. Post-slice audit reports 542
stage rows, 85 produced-inventory rows, 284 combat encounters, 179
resolver-ready combat encounters, 174 quests with item/tool blockers, 120
quests with combat blockers, and 105 statless combat rows. Source audit:
`memory-bank/source-audits/quest-heroes-quest-stage-detail-2026-06-22.md`.

Family Crest focused stage replacement completed on 2026-06-22. Backend:
`quest_data.py` now replaces generated/broad rows with a Darkan-backed
16-stage chain for Caleb's cooked fish salad, Avan's perfect-gold ruby ring
and necklace, Boot/Witchaven perfect gold routing, Johnathon's antipoison,
Chronozon's all-four-blast-spell combat, crest-piece combination, and
Dimintheis' final Family crest hand-in. The quest keeps strict start locks for
Crafting 40, Magic 59, Mining 40, and Smithing 40; used-during items remain
stage blockers rather than start locks. Frontend work was limited to targeted
Quests-tab blocked-at-stage coverage. New quest item and gauntlet icons were
fetched with provenance. Post-slice audit reports 554 stage rows, 92
produced-inventory rows, 284 combat encounters, 179 resolver-ready combat
encounters, 174 quests with item/tool blockers, 120 quests with combat blockers,
and 105 statless combat rows. Source audit:
`memory-bank/source-audits/quest-family-crest-stage-detail-2026-06-22.md`.

Temple of Ikov focused stage replacement completed on 2026-06-22. Backend:
`quest_data.py` now replaces generated/broad rows with a Darkan-backed
11-stage chain for Lucien's pendant, light-source entry, web cutting and Boots
of lightness pickup, lava-bridge lever routing, ice-arrow gathering, trapped
Fire Warrior lever handling, Fire Warrior bow/ammo combat, Winelda's 20
limpwurt-root teleport, Guardian/Lucien route variants, and the final Staff of
Armadyl or Lucien combat ending. The quest keeps strict startability at Thieving
42 while keeping all used-during items and combat as current-stage blockers.
Frontend work was limited to targeted Quests-tab blocked-at-stage coverage. New
Temple quest item and bow-variant icons were fetched with provenance. Post-slice
audit reports 564 stage rows, 97 produced-inventory rows, 285 combat encounters,
180 resolver-ready combat encounters, 174 quests with item/tool blockers, 120
quests with combat blockers, and 105 statless combat rows. Source audit:
`memory-bank/source-audits/quest-temple-of-ikov-stage-detail-2026-06-22.md`.
Do not create `memory-bank/status-updates/` artifacts again until every quest in
the catalog is updated to the requested minute-detail parity level.

Combat V1 design grill completed on 2026-06-23. The completed artifact is
`memory-bank/combat-design-grill-2026-06-23.md`. It resolves the major design
branches for a full Combat implementation: one source-backed engine for ordinary
monsters, quest encounters, bosses, quantity rows, and phase/form chains; 50
ticks per `Actions per review`; atomic rollback; damage-based XP routing;
finite supply loadouts; auto-eat and review-tick recovery; PvM grave/Death's
Office recovery; Wilderness opt-in/loss rules; enabled runtime rows requiring
complete source-critical data; and explicit backend/frontend/assets/balance/
testing handoffs. No combat runtime code shipped in this documentation pass.

Hunter v1 completed on 2026-06-20. The skill is a current Gathering review
skill with 55 source-backed targets in `hunter_data.py`: bird snaring,
butterfly netting, deadfall, box trapping, net trapping, falconry, magic boxes,
and both Puro-Puro/world impling rows. The local 2011Scape cache supplied
canonical item names and ids, while 2011.rs guide rows supplied levels/XP and
local 2012scape/Darkan Hunter code supplied mechanics/id parity where the local
2011Scape checkout has no Hunter plugin. The implementation adds stable
`current_hunter` IDs, storage config version 18, review-scale Hunter success
probabilities, success-only material consumption, `hunter_success_count`
achievements, Hunter item/icon registration, quest locks for Eagles' Peak, As a
First Resort, Rocking Out, and Priest in Peril route precedent, grouped Hunter
target UI, Stats/Bank/HUD support, action multiplier support, and undo
rollback. Deferred Hunter systems are recorded in
`memory-bank/source-audits/hunter-2011scape-2026-06-20.md`. Verification:
`python3 run_tests.py` passed with 374 tests (89 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 374 tests.

## Next Milestone
Use `memory-bank/future-work-kanban.md` for the current prioritized follow-up plan:

- The current P0 architecture board is complete. Do not continue P0 by default;
  reopen architecture only if the owner names a new concrete acceptance boundary.
- Next default work can move back to content/polish/"fun stuff" using the
  parked and prioritized sections in the kanban.
- Later candidate: GE v1, only after explicit reprioritization, starting from `memory-bank/fake-grand-exchange-design.md`.
- Parked: dependency-heavy Crafting acquisition loops and special Mining/Woodcutting content.
- Fishing follow-ups: Dungeoneering fish, Fishing Trawler, quest-only fish, Fish Flingers, and real shop/GE material sourcing, only if explicitly prioritized.
- Firemaking-specific follow-up: bonfires/fire spirits, only if explicitly prioritized.
- Cooking follow-ups: broader source-backed acquisition routes for remaining prep materials, only if explicitly prioritized.
- Runecrafting follow-ups: Magic Imbue, Wicked hood daily resources/teleports/reclaim, Abyss routing/abyssal creatures, talisman sourcing, and broader rune economy routes, only if explicitly prioritized.
- Hunter follow-ups: tracking trails, pitfall trapping, rabbit snaring,
  barehand catches, Herblore Habitat/Jadinkos, grenwall herb drops, and
  partial-route modeling for Regicide-start content, only if explicitly
  prioritized.
- NPC shop follow-up: `memory-bank/npc-shop-design-seed.md` captures the
  intended separate Shop surface, source-backed stock/prices, shared inventories,
  buy/sell rules, and location/quest locks. Grill the open decisions before
  backend implementation.
- Combat V1 follow-up: `memory-bank/combat-design-grill-2026-06-23.md` is the
  completed design source. Implement only as a full-system Combat build: source
  audits, enabled enemy/equipment/drop registry, undo-safe tick engine, Combat
  tab, expanded supply loadout controls, death/grave/Death's Office,
  Wilderness risk, quest encounter integration, assets, targeted tests, Qt
  tests, and manual Anki QA. The first ordinary-combat slice and the recovery/
  carried-food foundation are already implemented; do not redo those.
- Quest-lock follow-up: `memory-bank/quest-unlock-audit-2026-06-17.md`
  records the completed 194-row pre-EOC catalog, implemented completion gates,
  route-precedent locks, the RFD subquest split, generated item/lamp rewards,
  and route/location checks that should stay ungated until a route model exists.
  Use it with `memory-bank/source-audits/quest-stage-gates-2026-06-22.md`
  before stage-aware partial unlocks, route/location gates, combat/action
  blockers, or new quest-unlocked skill targets.
