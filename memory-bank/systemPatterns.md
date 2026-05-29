# System Patterns

## Architecture Snapshot
The add-on is a small Python package loaded by Anki. It separates some pure game logic from Anki-aware orchestration, but skill behavior is still partly hardcoded across constants, UI, storage, and review-answer routing.

## Important Modules
- `__init__.py`: runtime orchestration, global player state, review hooks, answer handling, menu callbacks, and skill-specific action dispatch.
- `constants.py`: item data, skill source data, image paths, XP table, and achievements.
- `logic_pure.py`: pure helpers for XP/level math, probabilities, crafting, mining, woodcutting, and smithing operations.
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

## Architectural Pressure
Adding many skills by copying the current pattern would increase duplication in:
- skill selection UI
- stats rendering
- storage defaults and migrations
- answer dispatch
- achievement definitions
- icon/image registration
- tests

The next major refactor should continue moving action behavior behind registry metadata. Skill and item identity now exist in pure backend modules; UI, achievements, and the remaining runtime dispatch map are still transitional.

## Compatibility Pattern
Persisted Anki config is the stable boundary. Schema changes should go through `storage_pure.py` migrations and keep existing user data intact.
