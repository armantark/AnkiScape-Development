# Progress

## What Works
- AnkiScape loads as an Anki add-on.
- The local working copy is intended to live outside the AnkiWeb-managed numeric folder.
- The local working copy is now initialized as a git repository on `main`.
- Review answers can award XP for the active skill.
- Command-Z/Anki undo now rolls back review-awarded XP/items by restoring the changed game-state keys paired with that answer.
- Mining, Woodcutting, Fishing, Smithing, Crafting, Fletching, and Firemaking exist.
- Items are stored in a shared inventory/bank.
- Level-up and achievement flows exist.
- Review HUD, floating XP, floating widget, main menu, stats, bank, settings, and achievements are present.
- Tests cover a meaningful portion of pure logic, migrations, settings, hooks, UI calculations, and integration smoke behavior.
- A backend skill registry exists for current and planned 2011-era skills.
- A pure review-action registry exists for levelled skills plus no-XP Utility/Activities aliases, without adding Utility as a fake skill.
- A pure flat target-row metadata contract exists for Mining, Woodcutting, Fletching, Firemaking, Fishing, and Utility/Activities, so their Skills-hub rows are generated as shared metadata before Qt renders them.
- A backend item manifest exists for current ores, logs, fish, gems, bars, crafted items, Fletching outputs/materials, and Utility/Crafting pilot materials.
- Storage defaults and migrations can seed registered item keys while preserving existing/custom inventory entries.
- Review eligibility and level-up key lookup are registry-backed for the current four skills.
- `tools/fetch_assets.py` can fetch one item icon on demand from OSRS first and RS3 second, with retries, polite User-Agent handling, dry-run/force safety, optional square PNG normalization, and provenance output.
- Fletching exists as the first expanded playable skill: registry metadata, save defaults/migration keys, target panel, item manifest outputs/materials, pure processing logic, runtime review dispatch, and scraped output/material icons are in place.
- A project-local Cursor skill, `.cursor/skills/ankiscape-skill-expansion/`, captures the repeatable workflow for future skill/action expansion.
- Crafting/Utility backend rework is in place: no-XP Utility/Activities, corrected Crafting pottery/spinning/silver-bolt pilot data, a source audit, action-multiplier-compatible reward handling, migration coverage, and undo-safe review handling.
- Crafting/Utility frontend is in place: Utility/Activities is a no-XP Skills-hub category with batch tooltips and `on_set_utility` persistence; Crafting tooltips show output/batch; the HUD speaks the Utility no-XP state; Settings group into Gameplay/Notifications/Floating Widget/Developer with a clamped Actions-per-review control. Covered by offscreen Qt tests.
- Utility/Activities has a dedicated icon set: each existing activity exposes an `icon_path` backed by `activityicons/` assets, and the Qt list falls back to output-item art if an activity icon is missing.
- Feathers now have one legitimate non-dev source: `Scavenge chicken feathers` is a no-XP Utility/Activities bridge that grants `28 Feather` per successful action tick without opening Combat, shops, coins, or GE.
- Firemaking v1 is in place: source-backed `firemaking_data.py`, stable `current_firemaking` target IDs, storage config version 12 migration/defaults, review-scale lighting chances, implicit tinderbox behavior, source XP, `Ashes x1`, achievements, assets, and Artisan hub/Stats/Bank/HUD support.
- Fishing v1 is in place: source-backed `fishing_data.py`, stable `current_fishing` method IDs, storage config version 13 migration/defaults, review-scale catch chances, ordered mixed-output rolls, success-only material consumption, hidden Strength/Agility side XP for Barbarian fish, generic Fishing achievements, dedicated fish/material assets, a `fish` item category, and Gathering hub/Stats/Bank/HUD support.
- Crafting backend parity foundation is in place: source-backed `crafting_data.py`, stable `current_craft` recipe IDs, corrected 2011Scape XP values, live input-starved high/dependency targets, storage config version 11 migration, and no XP-bearing Crafting batching.
- Crafting frontend grouping/assets are in place: the Skills-hub Crafting panel groups stable recipe IDs by family, persists collapsed families, shows owned material counts, guards disabled-row clicks, and resolves the fetched `crafteditems/` icon set.
- Woodcutting backend parity is in place: 2011Scape target/hatchet/bird-nest source data, stable target IDs, real log item outputs, toolbelt-aware hatchet RNG, Ivy no-output XP, bird nest drops, no-XP nest-opening Utility, and storage migration from legacy tree-named logs.
- Woodcutting frontend/assets are in place: target rows show friendly names, tool requirements, Ivy/no-output notes, bird-nest Utility access, and fetched log/hatchet/nest art with graceful gaps only for rare unresolved egg assets.
- Mining backend parity is in place: 2011Scape target/pickaxe source data, stable target IDs, real output item names, toolbelt-aware pickaxe resolution, source-shaped Mining probabilities, weighted sandstone/granite/gem-rock outputs, incidental gem drops with no Mining XP, Varrock-armour extra output, amulet-of-glory gem chance, explicit Mining item tradability metadata, and storage migration from legacy display-name `current_ore` values.
- Review pacing can run multiple game action ticks per successful card via `Actions per review` (1x-10x). This replaces the old XP-only multiplier semantics: XP, items, material use, gathering rolls, and Utility batches now scale together, while Anki undo rolls back the whole multi-action review as one reward.
- Smithing backend parity is in place: source-generated `smithing_data.py`, unified `SMITHING_DATA` smelt/forge recipes, all 9 bars, all 157 forge rows from `BarProducts.kt`, stable `current_smith` recipe IDs, storage config version 9, canonical `Adamant bar`/`Rune bar` names, forged item manifest registration, and runtime review dispatch through the unified pure Smithing helper.
- Equipment backend is in place: generated `equipment_data.py` covers Smithing armour/weapons plus Mining bonus gear, `player_data["equipment"]` replaces `owned_equipment`, combat level defaults are scaffolded, pure equip/unequip/stat-total helpers exist, and runtime exposes `on_equip_item` / `on_unequip_slot` for the Equipment tab.
- Equipment frontend is in place: the main menu has a dedicated Equipment tab, right-click Equip/Unequip menus, slot placeholder icons, stat totals, and bonus/requirement tooltips.

## What Is Not Built Yet
- Full target-list/action metadata beyond the current review-action dispatch registry and the flat target-row metadata contract. Grouped Smithing/Crafting target trees still need their own metadata seam if they are refactored.
- Combat training and combat encounters.
- Real acquisition loops for dependency-heavy Crafting inputs such as dragonstone, onyx, hides, molten glass, battlestaff orbs, and some weaving/spinning materials.
- Formal balancing pass for long-term progression.
- A release-quality expansion spec.
- Backfilled provenance for older bundled assets that predate the current scraper/provenance workflow.
- Firemaking bonfires and fire spirits; they are pre-EOC but intentionally deferred as a separate extension.
- Fishing Dungeoneering fish, Fishing Trawler outputs, quest-only fish, Fish Flingers, and a real shop/GE material economy; they are intentionally deferred as separate systems rather than folded into ordinary Fishing v1.

## Frontend Progress
- The main menu top bar now holds global sections only: Skills, Bank, Stats, Achievements, Settings. The four per-skill top tabs were removed.
- A registry-driven Skills hub replaces them: category filter -> skill list -> target list. Categories/skills come from `skill_hub.build_skill_hub`, backed by `skill_registry`.
- Normal mode shows only playable skills; developer mode additionally surfaces the planned catalog as disabled entries.
- Active-skill selection (Train/Stop training), Smithing/Crafting availability gating, and the live `refresh_skill_availability` hook are preserved through the hub's per-skill panel.
- Skills-hub clicks now correctly drive the target panel. A closure name collision (`_select_skill` redefined by the Stats tab in the same `show_main_menu` scope) had been shadowing the hub handler; the hub helper is now `_select_hub_skill`. Covered by offscreen Qt behavior tests.

## Known Technical Debt
- Existing skills are still hardcoded in multiple frontend/UI places.
- `constants.py` mixes paths, data tables, achievements, and progression constants.
- `__init__.py` owns too much runtime orchestration and skill dispatch.
- `ui.py` is large and mixes many dialogs/surfaces.
- The backend registry currently preserves flat save keys for safety; a deeper nested save model remains deferred.
- The runtime answer handler map now uses registry handler keys, but grouped target-list metadata and handler internals are still partly hardcoded.
- The runtime answer path now uses `action_registry.py` for Skill/Utility handler-key resolution and a handler-keyed can-start map, but the individual handler bodies still live in `__init__.py`.
- Flat target rows now use `target_metadata.py`, but grouped Smithing/Crafting trees still carry local row-building logic because parent rows and expand/collapse state need a separate contract.
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

## Next Milestone
Use `memory-bank/future-work-kanban.md` for the current prioritized follow-up plan:

- Continue P0 only for a new architecture slice: grouped Smithing/Crafting target-tree metadata or further `__init__.py` decomposition. The review-action dispatch and flat target-row metadata slices are done.
- Later candidate: GE v1, only after explicit reprioritization, starting from `memory-bank/fake-grand-exchange-design.md`.
- Parked: dependency-heavy Crafting acquisition loops and special Mining/Woodcutting content.
- Fishing follow-ups: Dungeoneering fish, Fishing Trawler, quest-only fish, Fish Flingers, and real shop/GE material sourcing, only if explicitly prioritized.
- Firemaking-specific follow-up: bonfires/fire spirits, only if explicitly prioritized.
