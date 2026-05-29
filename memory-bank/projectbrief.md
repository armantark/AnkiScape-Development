# Project Brief

## Project
AnkiScape is a Python Anki add-on that adds a lightweight idle-RPG layer to card review. Each eligible answer can award skill XP, items, achievements, and level progress while staying inside Anki's normal review flow.

## Current Goal
Preserve the existing add-on and augment it rather than rebuilding from scratch. The near-term architectural goal is to make the four existing skills more data-driven before adding many more skills or combat.

## Scope
- Keep the current Anki review hook, floating XP, HUD, menu, bank, stats, achievements, and settings behavior working.
- Refactor hardcoded skill handling into a skill/action registry before expanding content.
- Add noncombat skills before combat so the shared model proves itself on simpler loops.
- Treat Melvor Idle as conceptual overlap only: inspiration for idle-RPG progression, not a product or mechanics blueprint to copy.

## Non-Goals
- Do not replace Anki with a standalone game shell.
- Do not build real-time combat as the first expansion milestone.
- Do not copy Melvor Idle content, structure, names, balancing, or UI wholesale.

## Success Criteria
- Card review remains fast and unobtrusive.
- Existing saves migrate safely.
- Tests cover pure game logic, storage migrations, hooks, UI gating, and integration smoke paths.
- New skills can be added mostly by data/config plus small action handlers, not by scattering new branches across the codebase.
