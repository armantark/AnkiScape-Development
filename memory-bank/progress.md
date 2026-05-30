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
- Crafting/Utility backend rework is in place: no-XP Utility/Activities, corrected Crafting pottery/spinning/silver-bolt pilot data, a source audit, a central XP multiplier read path, migration coverage, and undo-safe review handling.

## What Is Not Built Yet
- Full action handler registry metadata beyond the current review handler map.
- Registry-driven Stats/Bank/HUD surfaces for skills beyond the original four.
- Combat.
- Registry-driven Stats/Bank/HUD surfaces (still hardcoded to the four skills).
- Formal balancing pass for long-term progression.
- A release-quality expansion spec.
- Backfilled provenance for the existing bundled assets.
- Frontend surfacing for Utility/Activities and the XP multiplier settings control.

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

## Next Milestone
Frontend handoff for Crafting/Utility: expose Utility/Activities, add no-XP and batch tooltips, remove Soft clay from the Crafting target panel, and add the Gameplay XP multiplier setting. Then registry-drive Stats/Bank/HUD and define source loops for feathers and arrowtips.
