# System Patterns

## Architecture Snapshot
The add-on is a small Python package loaded by Anki. It separates some pure game logic from Anki-aware orchestration, but skill behavior is still partly hardcoded across constants, UI, storage, and review-answer routing.

## Important Modules
- `__init__.py`: runtime orchestration, global player state, review hooks, answer handling, menu callbacks, and skill-specific action dispatch.
- `constants.py`: item data, skill source data, image paths, XP table, and achievements.
- `logic_pure.py`: pure helpers for XP/level math, probabilities, crafting, Utility/Activities, mining, woodcutting, and smithing operations.
- `logic.py`: Anki-aware level-up and achievement checks plus probability wrappers.
- `storage.py`: Anki config persistence.
- `storage_pure.py`: default player shape and migrations.
- `skill_registry.py`: pure skill catalog for current and planned skills, including stable IDs, categories, save keys, and review eligibility.
- `item_registry.py`: pure item manifest helpers for current economy items, including stable IDs, storage keys, categories, assets, and source/license notes.
- `ui.py`: Qt dialogs, HUD, menu, stats, bank, achievements, and settings.
- `hooks.py`: centralized hook registration and dry-run planning.
- `injectors.py` and `deck_injection_pure.py`: floating widget / deck browser injection helpers.

## Current Skill Flow
1. Anki shows a review card and the add-on marks review state.
2. The user shows the answer, then answers with an eligible ease.
3. `on_answer_card` calls `on_good_answer` if the current skill is active and XP has not already been awarded.
4. Skill-specific branches call pure helpers, update `player_data`, check levels/achievements, save, and refresh UI.

## Existing Skill Patterns
- Gathering skills use success probabilities and selected resource data.
- Processing skills consume inventory and produce output items.
- All skills use the shared `EXP_TABLE` and per-skill `*_level` / `*_exp` fields.
- Inventory is a single dictionary shared across ores, logs, gems, bars, and crafted items.
- The backend registry preserves current flat save keys while centralizing skill identity. This is deliberate: Anki config is the stable boundary, so registry-driven defaults are safer than a nested save migration right now.
- The item registry uses existing inventory storage names as `storage_key` values. Stable item IDs can support future UI/action metadata without breaking current saves.
- Review dispatch now resolves a registry `review_handler_key` before calling the runtime handler map. This keeps display names, save keys, and handler identity connected without requiring a large action-engine rewrite.
- Fletching is the first staged expansion skill to complete backend + target-panel rollout. It uses stable recipe IDs for save/UI selection, because multiple recipes can produce the same inventory item (for example, several log tiers all output arrow shafts).
- Fletching material-only inputs such as feathers and arrowtips are registered as item-manifest `material` entries. They are inventory-safe now, but still need explicit source loops before the economy is complete.
- Utility/Activities are backend actions, not skills. They use stable activity IDs in `UTILITY_ACTIVITY_DATA`, mutate inventory through pure helpers, award zero skill XP, and can batch up to an inventory-sized cap when they represent fast material preparation.
- Crafting recipe data stores source XP only. Runtime reward handling reads `ankiscape_xp_multiplier`, clamps it, and applies it after the pure action returns base XP but before level-up checks.
- Woodcutting now has a focused source-data module (`woodcutting_data.py`) rather than only ad hoc `constants.py` rows. Its stable target IDs are persisted in `current_tree`, while inventory uses real item output names such as `Logs` and `Oak logs`.
- Gathering tool progression is starting with a hybrid model: source tool items remain ordinary registered items for future acquisition/trading, but review logic can also resolve bound toolbelt IDs. Existing saves get a bound Bronze hatchet so introducing tool requirements does not brick Woodcutting. Reuse this for Mining pickaxes if the pattern holds.
- Source game tick odds should not be copied directly into review odds. Woodcutting stores 2011Scape low/high chance plus hatchet ratio, then applies an Anki-tuned adapter in pure logic so one review action remains the pacing unit.
- Random no-XP Utility actions can need special pure helpers. `Open bird nests` is the first example: it is a Utility/Activities action, but it consumes any known nest subtype and rolls source contents instead of using a fixed `requirements -> output_item` recipe.
- Review rewards are paired with Anki undo via `gui_hooks.state_did_undo`. When an eligible answer changes game state, the runtime records the original values for only the changed `player_data` keys; undo restores those values and saves config so Command-Z does not leave XP/items ahead of the card schedule.

## Architectural Pressure
Adding many skills by copying the current pattern would increase duplication in:
- skill selection UI
- stats rendering
- storage defaults and migrations
- answer dispatch
- achievement definitions
- icon/image registration
- tests

The next major refactor should continue moving target-list metadata and action behavior behind registry metadata. Skill and item identity now exist in pure backend modules; UI, achievements, and the remaining runtime dispatch internals are still transitional.

## Skill Expansion Workflow
Use the project skill at `.cursor/skills/ankiscape-skill-expansion/SKILL.md` before adding or expanding any skill, Utility/Activity, target chain, item economy slice, or achievement set. It encodes the repeatable workflow: source audit first, playable scope cut, registry/item data, asset scraping, pure mechanics, UI surfacing, achievement patterns, tests, manual Anki checks, and memory updates.

## Compatibility Pattern
Persisted Anki config is the stable boundary. Schema changes should go through `storage_pure.py` migrations and keep existing user data intact.

Review-answer side effects must follow Anki's undo semantics. If a future skill mutates new `player_data` keys during an answer, the generic snapshot diff should catch them; if a future system writes outside `player_data`, it needs its own undo-aware rollback path.

## UI Gotcha: nested-closure name collisions in `show_main_menu`
`show_main_menu` is a very large function that defines many nested helpers (one per tab/section). All of these are locals of the *same* scope, so two sections defining a helper with the same name (e.g. `_select_skill`) silently rebind it — the later definition wins, and earlier callers route into the wrong function with no error. This caused the Skills-hub panel to ignore clicks (the Stats tab's `_select_skill` shadowed the hub's). Mitigation: prefix section-scoped helpers with their section (`_select_hub_skill`, etc.), and prefer the offscreen Qt behavior test to catch misrouted handlers. Longer term, splitting these sections into their own builder functions/classes would remove the shared scope entirely.
