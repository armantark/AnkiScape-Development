# Active Context

## Current Focus
Protect the local fork before any large expansion. The agreed direction is to augment the existing add-on, not rebuild it first.

## Recent Decision
The next meaningful engineering step should be a skill-registry refactor. That refactor should preserve the current four skills while making future skills cheaper and safer to add.

The add-on folder has been renamed from the AnkiWeb ID `1808450369` to `ankiscape_fork` so public AnkiWeb updates do not overwrite local work.

Backend registry implementation has started on `main` in a local git repository. The first backend pass adds pure skill and item registry modules, keeps existing flat save keys for safety, and wires review eligibility/level-up/storage defaults through registry metadata without changing the visible UI.

Asset-fetch tooling now exists as a standalone developer CLI at `tools/fetch_assets.py`. It is not imported by the add-on runtime. It resolves one item icon at a time from the official RuneScape wikis, prefers OSRS with RS3 fallback, supports registry-key path resolution, normalizes PNG output when fetching, and records provenance.

## Key Product Decision
The project can borrow broad inspiration from idle-RPG progression, including Melvor Idle-like long-term loops, but should not copy Melvor's concrete content, balancing, UI, or structure (because it is inferior to RuneScape, but combat is an interesting carryover). The Anki review loop remains the core mechanic.

The target economy is now a compressed 2011-era RuneScape-style skill set adapted to Anki. Categories are Combat, Gathering, Artisan, Support, plus a visible Utility/Activities bucket for material-only no-XP actions. Magic remains one skill with separate combat and noncombat action families.

## Current Risks
- Skill behavior is still spread through hardcoded branches and dictionaries.
- Adding many skills before refactoring would likely multiply duplication.
- Combat could sprawl if started before noncombat action patterns are generalized.
- Anki config migration mistakes could affect persisted player progress.
- Running both the upstream `1808450369` copy and the local `ankiscape_fork` copy at the same time could double-register menus/hooks.
- The backend registry is only the first layer; the Qt menu is still per-skill/top-tab oriented and will overload once many skills become playable.
- Utility/Activities are intentionally no-XP, so the UI must make that tradeoff obvious before exposing them broadly.
- The asset scraper records provenance, but existing asset provenance is still unaudited until icons are re-fetched or manually cataloged.

## Next Recommended Work
1. Finish backend registry hardening around action handler metadata and any remaining hardcoded dispatch.
2. Add Fletching as the first proof-point Artisan skill: logs to arrow shafts and unstrung bows only. With the Skills hub now registry-driven, a new playable Artisan skill should appear in the hub mostly from registry data plus a target-list builder.
3. Make Stats/Bank/HUD registry-driven (they are still hardcoded to the four skills) so new skills surface there automatically.
4. Add Utility/Activities after the first Fletching slice if bowstring/flax dependencies become necessary.
5. Only then design combat and Slayer task layering.

## Frontend Handoff Status
The first frontend slice is done: the consolidated menu now uses a global top bar (Skills, Bank, Stats, Achievements, Settings) and a registry-backed Skills hub (`skill_hub.py` view-model + `ui.show_main_menu` three-pane category/skill/target layout). Developer mode reveals planned skills as disabled entries.

## Handoff Notes
- Backend work means Python game logic, storage, migrations, and tests.
- Frontend work means Qt dialogs/HUD/menu/stats/bank UX and any injected web UI.
- Split backend and frontend planning explicitly when implementation starts, because model choice may differ by side.
