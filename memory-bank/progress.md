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

## What Is Not Built Yet
- Full action handler registry metadata beyond the current review handler map.
- Playable skills beyond the current four.
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

## Known Technical Debt
- Existing skills are still hardcoded in multiple frontend/UI places.
- `constants.py` mixes paths, data tables, achievements, and progression constants.
- `__init__.py` owns too much runtime orchestration and skill dispatch.
- `ui.py` is large and mixes many dialogs/surfaces.
- The backend registry currently preserves flat save keys for safety; a deeper nested save model remains deferred.
- The runtime answer handler map is smaller but not yet a fully data-driven action engine.

## Current Status
Documentation seed completed as of 2026-05-27. The working copy has been moved to `addons21/ankiscape_fork` to avoid AnkiWeb update overwrites against the numeric upstream folder.

Backend registry foundation completed as an initial pass on 2026-05-29. The full unit/integration suite passes with 81 tests.

Frontend Skills-hub conversion completed on 2026-05-29: the per-skill top tabs collapsed into one registry-driven Skills hub, leaving the top bar for global sections only. Suite now passes with 87 tests (6 new `skill_hub` view-model tests).

Asset scraper CLI completed on 2026-05-29. Suite now passes with 92 tests, including mocked OSRS hit, OSRS miss/RS3 fallback, key/path resolution, skip-if-present, and dry-run coverage.

## Next Milestone
Harden the backend action contract, then add Fletching as the first new proof-point skill while preserving the current UI/UX.
