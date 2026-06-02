# Progress

## What Works
- AnkiScape loads as an Anki add-on.
- The local working copy is intended to live outside the AnkiWeb-managed numeric folder.
- The local working copy is now initialized as a git repository on `main`.
- Review answers can award XP for the active skill.
- Command-Z/Anki undo now rolls back review-awarded XP/items by restoring the changed game-state keys paired with that answer.
- Mining, Woodcutting, Smithing, and Crafting exist.
- Items are stored in a shared inventory/bank.
- Level-up and achievement flows exist.
- Review HUD, floating XP, floating widget, main menu, stats, bank, settings, and achievements are present.
- Tests cover a meaningful portion of pure logic, migrations, settings, hooks, UI calculations, and integration smoke behavior.
- A backend skill registry exists for current and planned 2011-era skills.
- A backend item manifest exists for current ores, logs, gems, bars, crafted items, Fletching outputs/materials, and Utility/Crafting pilot materials.
- Storage defaults and migrations can seed registered item keys while preserving existing/custom inventory entries.
- Review eligibility and level-up key lookup are registry-backed for the current four skills.
- `tools/fetch_assets.py` can fetch one item icon on demand from OSRS first and RS3 second, with retries, polite User-Agent handling, dry-run/force safety, optional square PNG normalization, and provenance output.
- Fletching exists as the first expanded playable skill: registry metadata, save defaults/migration keys, target panel, item manifest outputs/materials, pure processing logic, runtime review dispatch, and scraped output/material icons are in place.
- A project-local Cursor skill, `.cursor/skills/ankiscape-skill-expansion/`, captures the repeatable workflow for future skill/action expansion.
- Crafting/Utility backend rework is in place: no-XP Utility/Activities, corrected Crafting pottery/spinning/silver-bolt pilot data, a source audit, action-multiplier-compatible reward handling, migration coverage, and undo-safe review handling.
- Crafting/Utility frontend is in place: Utility/Activities is a no-XP Skills-hub category with batch tooltips and `on_set_utility` persistence; Crafting tooltips show output/batch; the HUD speaks the Utility no-XP state; Settings group into Gameplay/Notifications/Floating Widget/Developer with a clamped Actions-per-review control. Covered by offscreen Qt tests.
- Woodcutting backend parity is in place: 2011Scape target/hatchet/bird-nest source data, stable target IDs, real log item outputs, toolbelt-aware hatchet RNG, Ivy no-output XP, bird nest drops, no-XP nest-opening Utility, and storage migration from legacy tree-named logs.
- Mining backend parity is in place: 2011Scape target/pickaxe source data, stable target IDs, real output item names, toolbelt-aware pickaxe resolution, source-shaped Mining probabilities, weighted sandstone/granite/gem-rock outputs, incidental gem drops with no Mining XP, Varrock-armour extra output, amulet-of-glory gem chance, explicit Mining item tradability metadata, and storage migration from legacy display-name `current_ore` values.
- Review pacing can run multiple game action ticks per successful card via `Actions per review` (1x-10x). This replaces the old XP-only multiplier semantics: XP, items, material use, gathering rolls, and Utility batches now scale together, while Anki undo rolls back the whole multi-action review as one reward.
- Smithing backend parity is in place: source-generated `smithing_data.py`, unified `SMITHING_DATA` smelt/forge recipes, all 9 bars, all 157 forge rows from `BarProducts.kt`, stable `current_smith` recipe IDs, storage config version 9, canonical `Adamant bar`/`Rune bar` names, forged item manifest registration, and runtime review dispatch through the unified pure Smithing helper.

## What Is Not Built Yet
- Full action handler registry metadata beyond the current review handler map.
- Combat.
- Formal balancing pass for long-term progression.
- A release-quality expansion spec.
- Backfilled provenance for the existing bundled assets.
- A dedicated icon set for Utility/Activities (activities currently reuse `crafteditems/` material art; the hub row falls back to the achievement icon).

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
- The runtime answer handler map now uses registry handler keys, but target-list metadata and handler internals are still partly hardcoded.

## Current Status
Documentation seed completed as of 2026-05-27. The working copy has been moved to `addons21/ankiscape_fork` to avoid AnkiWeb update overwrites against the numeric upstream folder.

Backend registry foundation completed as an initial pass on 2026-05-29. The full unit/integration suite passes with 81 tests.

Frontend Skills-hub conversion completed on 2026-05-29: the per-skill top tabs collapsed into one registry-driven Skills hub, leaving the top bar for global sections only. Suite now passes with 87 tests (6 new `skill_hub` view-model tests).

Asset scraper CLI completed on 2026-05-29. Suite now passes with 92 tests, including mocked OSRS hit, OSRS miss/RS3 fallback, key/path resolution, skip-if-present, and dry-run coverage.

Fletching frontend slice completed on 2026-05-29. The backend pilot's `visible_in_skill_hub` gate is now open: Fletching appears under Artisan with its own target panel (`_build_fletch_list`), level/material gating via `can_fletch_item_pure`, active-skill gating + warning, an `on_set_fletch` callback wired through `__init__`, and a live-availability slot (`fletch_btn`, optional 3rd arg to `refresh_skill_availability`). Skill icon fetched from the OSRS wiki `(detail)` variant via `tools/fetch_assets.py`. Covered by a new offscreen Qt test. NOTE: backend data gap — per-tier arrow-shaft yields (oak 30, willow 45, ... redwood 105) and the feather/arrowtip chain are not modeled yet; shortbow (u) recipes are accurate.

Skills-hub click bug fixed on 2026-05-29. Introduced an offscreen Qt behavior-test loop (`.venv-qt` with `aqt`, `QT_QPA_PLATFORM=offscreen`) that builds the real dialog and drives the widgets — no Anki restart needed. `tests/test_main_menu_widget.py` asserts that selecting Woodcutting and Artisan -> Crafting updates the panel. The core `run_tests.py` suite (95 tests) skips these when `aqt` is absent.

Fletching backend pilot completed on 2026-05-29. Fletching is backend-playable but hidden from normal Skills-hub mode pending frontend target-list work. Suite passes with 99 tests, including pure Fletching logic, storage defaults/migration, registry visibility/dispatch metadata, item manifest coverage, integration review handling, and offscreen Qt menu behavior.

Fletching data and asset hardening completed on 2026-05-29. Recipe targets now use stable keys, model per-log arrow-shaft yields, add headless arrows and bronze-through-rune arrows, include Fletching materials in inventory defaults, and scrape 21 normalized PNG icons into `fletcheditems/` with provenance. Suite passes with 100 tests via `.venv-qt` unittest discovery.

Review undo rollback completed on 2026-05-29. `state_did_undo` restores the `player_data` keys changed by the latest review reward so undoing an answered card also removes the associated XP/items. Suite passes with 105 tests.

AnkiScape skill expansion project skill created on 2026-05-29. It documents the required workflow for source audits, scope cuts, data modeling, asset scraping, mechanics, UI, achievements, tests, manual Anki checks, and memory updates.

Crafting/Utility backend rework completed on 2026-05-29. `Soft clay` moved out of Crafting XP data into batched no-XP Utility/Activities; audited Crafting pilot actions now cover pottery shaping/firing, ball of wool, bow string, and silver bolts (unf). New icons for wool, flax, ball of wool, bow string, and silver bolts (unf) were fetched with provenance. Suite passes with 117 tests in both `python3 run_tests.py` and the offscreen Qt unittest loop.

Woodcutting backend parity completed on 2026-06-01. `woodcutting_data.py` captures the local 2011Scape source audit; `TREE_DATA` now uses stable IDs and real output item names; Fletching consumes real log keys; storage config version is 7 with legacy log/target migration and bound Bronze hatchet seeding; bird nests can drop from Woodcutting and open through no-XP Utility. Core and offscreen Qt suites pass with 134 tests.

Mining backend parity completed on 2026-06-01. `mining_data.py` captures the local 2011Scape source audit plus the scoped simple historical targets; `ORE_DATA` now uses stable IDs and real output item names; storage config version is 8 with legacy target migration, bound Bronze pickaxe seeding, and an empty `owned_equipment` collection; the item manifest now carries `tradeable` and minimal equipable metadata. `python3 -m unittest discover -s tests` passes with 154 tests (18 skipped).

Review action multiplier completed on 2026-06-01. Runtime reads the new `ankiscape_review_action_multiplier` setting, falls back to the legacy XP multiplier key, and executes integer action ticks per eligible review with aggregate feedback and one undo snapshot. Settings now show a simple `Actions per review` +/- spinner. `python3 run_tests.py` passes with 165 tests (26 skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passes with 165 tests.

Smithing 2011Scape backend parity completed on 2026-06-01. `python3 run_tests.py` passes with 172 tests (26 skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passes with 172 tests.

## Next Milestone
Frontend/assets handoff for Smithing parity: expose the full `SMITHING_DATA` table in the Skills hub, grouped by Furnace/Anvil, persist `current_smith`, show level/material gates from backend data, and fetch/wire icons for Blurite bar plus important forged outputs where practical.
