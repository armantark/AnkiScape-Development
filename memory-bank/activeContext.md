# Active Context

## Current Focus
Protect the local fork before any large expansion. The agreed direction is to augment the existing add-on, not rebuild it first.

## Recent Decision
The next meaningful engineering step should be a skill-registry refactor. That refactor should preserve the current four skills while making future skills cheaper and safer to add.

The add-on folder has been renamed from the AnkiWeb ID `1808450369` to `ankiscape_fork` so public AnkiWeb updates do not overwrite local work.

Backend registry implementation has started on `main` in a local git repository. The first backend pass adds pure skill and item registry modules, keeps existing flat save keys for safety, and wires review eligibility/level-up/storage defaults through registry metadata without changing the visible UI.

Asset-fetch tooling now exists as a standalone developer CLI at `tools/fetch_assets.py`. It is not imported by the add-on runtime. It resolves one item icon at a time from the official RuneScape wikis, prefers OSRS with RS3 fallback, supports registry-key path resolution, normalizes PNG output when fetching, and records provenance.

Fletching backend pilot is complete. Fletching is backend-playable through registry review metadata and flat save keys, but intentionally hidden from the normal Skills hub until the frontend target panel is added. The first Fletching slice consumes logs into arrow shafts and unstrung bows only; no bowstrings, arrows, Ranged, or combat dependencies yet.

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
- Fletching is backend-playable but frontend-hidden. The next frontend handoff must add a target list and visible Skills-hub surfacing before normal users can train it through the menu.
- Utility/Activities are intentionally no-XP, so the UI must make that tradeoff obvious before exposing them broadly.
- The asset scraper records provenance, but existing asset provenance is still unaudited until icons are re-fetched or manually cataloged.

## Next Recommended Work
1. (Backend) Fletching data accuracy in `constants.py`: per-tier arrow-shaft yields (normal 15 / oak 30 / willow 45 / maple 60 / yew 75 / magic 90 / redwood 105; levels 1/15/30/45/60/75/90; XP 5/10/15/20/25/30/35) verified on the OSRS wiki. Needs disambiguated target keys since every tier outputs the same `Arrow shaft` item. Then add the feather/arrowtip chain (headless arrows -> arrows). Shortbow (u) recipes are already accurate.
2. (Backend) Optionally pass `can_fletch_any_item` (3rd arg) to `refresh_skill_availability` from the review hook so Fletching auto-enables mid-review like Smithing/Crafting; the frontend slot already supports it.
3. Make Stats/Bank/HUD registry-driven (still hardcoded to the four original skills; Fletching does not yet surface there) so new skills appear automatically.
4. Add Utility/Activities if bowstring/flax dependencies become necessary.
5. Only then design combat and Slayer task layering.

## Frontend Handoff Status
The first frontend slice is done: the consolidated menu now uses a global top bar (Skills, Bank, Stats, Achievements, Settings) and a registry-backed Skills hub (`skill_hub.py` view-model + `ui.show_main_menu` three-pane category/skill/target layout). Developer mode reveals planned skills as disabled entries. Skills-hub click routing is fixed and now covered by an offscreen Qt behavior test. Fletching is now a fully playable hub skill (target panel, gating, `on_set_fletch`, OSRS `(detail)` icon), completing the backend pilot's frontend handoff.

## Testing Workflow Note
UI-behavior regressions in the menu/HUD should be exercised with the offscreen Qt loop (`.venv-qt` + `aqt`, `QT_QPA_PLATFORM=offscreen`, see `tests/test_main_menu_widget.py`) before falling back to a manual Anki restart. Enable `ANKISCAPE_DEBUG=1` (or Developer Mode) and tail `ankiscape_debug.log` to read the `hub.*` navigation trace.

## Handoff Notes
- Backend work means Python game logic, storage, migrations, and tests.
- Frontend work means Qt dialogs/HUD/menu/stats/bank UX and any injected web UI.
- Split backend and frontend planning explicitly when implementation starts, because model choice may differ by side.
