# Progress

## What Works
- AnkiScape loads as an Anki add-on.
- The local working copy is intended to live outside the AnkiWeb-managed numeric folder.
- The local working copy is now initialized as a git repository on `main`.
- Review answers can award XP for the active skill.
- Mining, Woodcutting, Smithing, and Crafting exist.
- Items are stored in a shared inventory/bank.
- Level-up and achievement flows exist.
- Review HUD, floating XP, floating widget, main menu, stats, bank, settings, and achievements are present.
- Tests cover a meaningful portion of pure logic, migrations, settings, hooks, UI calculations, and integration smoke behavior.
- A backend skill registry exists for current and planned 2011-era skills.
- A backend item manifest exists for current ores, logs, gems, bars, and crafted items.
- Storage defaults and migrations can seed registered item keys while preserving existing/custom inventory entries.
- Review eligibility and level-up key lookup are registry-backed for the current four skills.
- `tools/fetch_assets.py` can fetch one item icon on demand from OSRS first and RS3 second, with retries, polite User-Agent handling, dry-run/force safety, optional square PNG normalization, and provenance output.
- Fletching exists as the first backend pilot skill: registry metadata, save defaults/migration keys, item manifest outputs, pure processing logic, and runtime review dispatch are in place.

## What Is Not Built Yet
- Full action handler registry metadata beyond the current review handler map.
- Frontend-visible playable skills beyond the current four.
- Combat.
- Registry-driven Stats/Bank/HUD surfaces (still hardcoded to the four skills).
- Formal balancing pass for long-term progression.
- A release-quality expansion spec.
- Backfilled provenance for the existing bundled assets.

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

## Next Milestone
Frontend handoff for Fletching: add the target-list panel, make it visible in the Skills hub, then make Stats/Bank/HUD registry-driven enough for new skills to appear cleanly.
