# Active Context

## Current Focus
Protect the local fork before any large expansion. The agreed direction is to augment the existing add-on, not rebuild it first.

## Recent Decision
The next meaningful engineering step should be a skill-registry refactor. That refactor should preserve the current four skills while making future skills cheaper and safer to add.

The add-on folder has been renamed from the AnkiWeb ID `1808450369` to `ankiscape_fork` so public AnkiWeb updates do not overwrite local work.

Backend registry implementation has started on `main` in a local git repository. The first backend pass adds pure skill and item registry modules, keeps existing flat save keys for safety, and wires review eligibility/level-up/storage defaults through registry metadata without changing the visible UI.

Asset-fetch tooling now exists as a standalone developer CLI at `tools/fetch_assets.py`. It is not imported by the add-on runtime. It resolves one item icon at a time from the official RuneScape wikis, prefers OSRS with RS3 fallback, supports registry-key path resolution, normalizes PNG output when fetching, and records provenance.

Fletching is now playable in the Skills hub and has had its first data-accuracy hardening pass. The target list uses stable recipe keys, includes tiered arrow-shaft yields, headless arrows, metal arrows through rune, and unstrung shortbows. Fletching output/material icons live under `fletcheditems/` and are recorded in `assets_provenance.json`.

Review-answer XP/items now respect Anki undo. The runtime records changed `player_data` keys for each successful review reward and restores them when Anki emits `state_did_undo`, fixing the Command-Z case where the card was undone but XP remained.

A project-local Cursor skill now exists at `.cursor/skills/ankiscape-skill-expansion/`. Use it before any future skill/action expansion so source audit, assets, target items, Utility/Activities, achievements, tests, and memory updates happen consistently instead of being rediscovered each time.

Crafting/Utility backend rework is now complete. `Soft clay` is no longer a Crafting XP target; no-XP Utility/Activities handle `Clay -> Soft clay` in batches up to 28. The audited Crafting pilot now includes pottery shaping/firing, wool spinning, bowstring spinning, and silver bolts (unf). A backend XP multiplier read path exists under `ankiscape_xp_multiplier`, with source XP preserved in recipe data and scaling applied only at reward time.

Woodcutting 2011Scape **frontend** pass is complete. The Skills-hub tree list now renders stable target IDs as friendly display names + level, shows output/base-XP/best-usable-hatchet/source in tooltips, distinguishes level vs "no usable hatchet" lock reasons (via `can_chop_woodcutting_target_pure` + `best_woodcutting_axe_pure` over `player_data["toolbelt"]`), and flags Ivy inline as "— XP only" (no logs). `Open bird nests` is surfaced as a visible no-XP Utility/Activities row, locked until a nest is held (`can_open_bird_nests_pure`). The legacy `show_stats`/`show_tree_selection_dialog` were de-landmined for the ID schema (real log item names + display names + missing-icon guards). Known follow-up: the `assets` task (log/Achey/Hollow/Ivy/hatchet/nest icons) is still pending — the UI degrades gracefully to iconless rows until then.

Depletion handling for processing skills: when a Crafting target or Utility activity runs out of its required materials, the runtime now names the *specific* missing item (e.g. "Pot" reports a missing "Unfired pot", not the Soft clay the player has plenty of) and switches the active skill off (`current_skill -> "None"`) via `_deactivate_current_skill`, instead of re-raising the same error on every card. The player re-picks a target from the menu to resume. Error dialogs also force the style's standard warning glyph so macOS stops substituting the host app's "folder" icon.

The Crafting/Utility **frontend** pass is now also complete. Utility/Activities is surfaced as a synthetic, visually-distinct Skills-hub category (it is deliberately *not* a registry XP skill — no level/exp keys — and is routed through `_UTILITY_SKILL_NAMES` + `current_utility`). Its target list shows batch + "no Crafting XP" tooltips and persists the active activity via a new `on_set_utility` callback bridged in `__init__`. Crafting tooltips now show output qty / batch size; Soft clay no longer appears as a craft target. The review HUD recognizes the active Utility activity and states it earns no XP. Settings are reorganized into Gameplay / Notifications / Floating Widget / Developer, with a clamped XP-multiplier spin under Gameplay writing `ankiscape_xp_multiplier`.

Woodcutting backend parity is now complete. Source data lives in `woodcutting_data.py` and is audited against local 2011Scape rev 667 source. Woodcutting now uses stable target IDs (`tree`, `oak`, `ivy`, etc.), real output item keys (`Logs`, `Oak logs`, `Bark`), source-shaped Anki-tuned chop probabilities, hybrid tool resolution from bound toolbelt IDs plus owned hatchet items, and rare bird nest subtype drops. Existing saves migrate legacy target names and tree-named inventory keys into the new shape; Redwood is removed as OSRS-only content. `Open bird nests` is a no-XP Utility/Activities backend action that opens up to 28 source nests into inert seed/ring/egg contents for future systems.

Mining 2011Scape **frontend** pass is now complete. The Skills-hub ore list (`_build_ore_list`) mirrors the Woodcutting tree-list pattern: rows render stable target IDs as friendly `display_name` + level with the ID on `UserRole`, tooltips show output / base XP / best-usable-pickaxe / source, and lock reasons split level vs "no usable pickaxe" via `can_mine_target_pure` + `best_mining_pickaxe_pure` over `player_data["toolbelt"]`. Variable-output rocks (Sandstone, Granite, Gem rocks) are flagged `— variable output` inline and list their weighted items in tooltips; essence shows `— Pure essence at Lvl 30+`. Coal/Gold tooltips note that the `concentrated` deposits are deliberately deferred. `owned_equipment` was intentionally left backend-only (no toolbelt/equipment UI). Bank/Stats were already registry-driven on real item names; only the unwired legacy `show_ore_selection_dialog` icon fallback was de-landmined for output-less rocks. Seven offscreen Qt tests cover Mining rows in `tests/test_main_menu_widget.py`. Known follow-up: the Mining `assets` pass (blurite/pure essence, normal+gilded pickaxes, sandstone/granite/gem-rock output icons) is still pending — rows degrade gracefully to icon-less until then.

Mining backend parity is now complete. Source data lives in `mining_data.py`: stable target IDs (`rune_essence`, `iron`, `gem_rocks`, etc.), real output item keys, source low/high Mining chances, respawn-time data, pickaxe metadata, weighted sandstone/granite/gem-rock outputs, incidental gem drops, and minimal backend-only owned equipment for Mining bonuses. Storage config version is 8 and migrates legacy display-name `current_ore` values while preserving existing inventory item names. The item manifest now records `tradeable` plus minimal equipable metadata; Mining-specific non-tradable decisions include Blurite ore, Inferno adze, and Varrock armour. Dragon pickaxe is normalized to item 15261 because local `PickaxeType.kt` references 15259 but `items.yml` marks 15261 as the tradeable "Used for mining" item.

## Key Product Decision
The project can borrow broad inspiration from idle-RPG progression, including Melvor Idle-like long-term loops, but should not copy Melvor's concrete content, balancing, UI, or structure (because it is inferior to RuneScape, but combat is an interesting carryover). The Anki review loop remains the core mechanic.

The target economy is now a compressed 2011-era RuneScape-style skill set adapted to Anki. Categories are Combat, Gathering, Artisan, Support, plus a visible Utility/Activities bucket for material-only no-XP actions. Magic remains one skill with separate combat and noncombat action families.

Roadmap direction: add an optional fake Grand Exchange-style market later so the default experience does not have to be fully ironman. The GE **design is now fully grilled and parked** in `memory-bank/fake-grand-exchange-design.md` (engine = hidden true-price + stochastic fill model with no persisted order book; GP = convenience-abundant, gated by buy limits + market clock, never sells XP; undo rolls back the market tick via deterministic RNG + per-tick delta snapshot; 8 slots, partial fills, OSRS price improvement, 40-action buy-limit windows, 240-action guide-price days capped +/-5%, alch-anchored seeding). It is intentionally **blocked on item-economy breadth**: the GE only earns its keep once many more tradable items exist.

Active priority (decided): **broaden the skill roster before resuming the GE.** Target is all remaining gathering skills (Fishing, Hunter, Farming; Mining/Woodcutting backend parity is done) and most basic artisan skills (Cooking, Firemaking next; Herblore, Runecrafting, Construction after). Each new skill goes through the `ankiscape-skill-expansion` project skill (source audit -> assets -> targets/recipes -> Utility/Activities -> achievements -> tests -> memory). The expanded item set produced by these skills becomes the GE's tradable universe when it is unparked.

## Current Risks
- Skill behavior is still spread through hardcoded branches and dictionaries.
- Adding many skills before refactoring would likely multiply duplication.
- Combat could sprawl if started before noncombat action patterns are generalized.
- Anki config migration mistakes could affect persisted player progress.
- Running both the upstream `1808450369` copy and the local `ankiscape_fork` copy at the same time could double-register menus/hooks.
- The backend registry is only the first layer; the Qt menu is still per-skill/top-tab oriented and will overload once many skills become playable.
- The asset scraper records provenance, but existing asset provenance is still unaudited until icons are re-fetched or manually cataloged.
- Future game state stored outside `player_data` must be made undo-aware; the current rollback is intentionally scoped to review reward mutations in `player_data`.

## Next Recommended Work
1. Expand the skill roster (current priority). Remaining gathering: Fishing, Hunter, Farming. Basic artisan: Cooking, Firemaking, then Herblore/Runecrafting/Construction. Use `.cursor/skills/ankiscape-skill-expansion/` for each.
2. Decide how arrowtips and feathers enter the economy: temporary developer-seeded items, Smithing outputs, Utility/Activities, or explicit shop/drop sources.
3. Extend Crafting beyond the curated pilot only after each dependency has a source loop.
4. Consider a small Utility/Activities icon set (currently the activity outputs reuse `crafteditems/` material art; the hub category/skill row falls back to the generic achievement icon).
5. Unpark the fake GE once the item economy is broad enough; resume from `memory-bank/fake-grand-exchange-design.md` (design is locked — do not re-grill the same decision tree).
6. Only then design combat and Slayer task layering.

## Frontend Handoff Status
The first frontend slice is done: the consolidated menu now uses a global top bar (Skills, Bank, Stats, Achievements, Settings) and a registry-backed Skills hub (`skill_hub.py` view-model + `ui.show_main_menu` three-pane category/skill/target layout). Developer mode reveals planned skills as disabled entries. Skills-hub click routing is fixed and now covered by an offscreen Qt behavior test. Fletching is now a fully playable hub skill (target panel, gating, `on_set_fletch`, OSRS `(detail)` icon), completing the backend pilot's frontend handoff.

The Crafting/Utility frontend handoff is also complete (see above): Utility/Activities surfaced as a no-XP hub category, Crafting target tooltips show batch/output, the HUD speaks the no-XP Utility state, and Settings carry the Gameplay XP-multiplier control. Pattern worth remembering: **non-XP "skills" (Utility/Activities) are injected at the ui view layer as a synthetic `CategoryView`/`SkillCardView`, not added to `skill_registry`**, so the XP registry stays honest (no fake level/exp keys). Reuse this approach for any future no-XP action family.

Mining needs a frontend handoff after the backend parity work: target rows should render `display_name`/`output_item` from `ORE_DATA`, show best usable pickaxe and lock reasons, label weighted output targets (sandstone/granite/gem rocks), and expose source notes without re-deriving source rules in Qt. A minimal compatibility patch keeps the existing hub list and stats panel usable with stable target IDs, but the polished Woodcutting-style UX is still pending.

## Testing Workflow Note
UI-behavior regressions in the menu/HUD should be exercised with the offscreen Qt loop (`.venv-qt` + `aqt`, `QT_QPA_PLATFORM=offscreen`, see `tests/test_main_menu_widget.py`) before falling back to a manual Anki restart. Enable `ANKISCAPE_DEBUG=1` (or Developer Mode) and tail `ankiscape_debug.log` to read the `hub.*` navigation trace.

## Handoff Notes
- Backend work means Python game logic, storage, migrations, and tests.
- Frontend work means Qt dialogs/HUD/menu/stats/bank UX and any injected web UI.
- Split backend and frontend planning explicitly when implementation starts, because model choice may differ by side.
