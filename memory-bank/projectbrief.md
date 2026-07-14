# Project Brief

## Project

AnkiScape is a Python Anki add-on that turns eligible card reviews into a lightweight, persistent pre-EOC RuneScape progression layer. Reviews can advance skills, combat, quests, items, achievements, shops, and world/economy clocks without replacing Anki's study flow.

## Current Goal

Reach a coherent “complete AnkiScape” rather than accumulating disconnected v1 slices. The canonical scope and work routing are:

- `memory-bank/future-work-kanban.md`
- `memory-bank/gap-backlog.json` for detailed gaps inside shipped skill families
- dated completion audits as historical baseline evidence, not live registry truth

## Product Boundary

- Target RuneScape immediately before EOC, cutoff `2012-11-20`.
- Keep Anki review primary: one successful review is one sourced action by default.
- Preserve source base XP and tune Anki pacing separately.
- Use the 240-reviews-per-day global clock only for background/world/economy cadence.
- Use target-local inventory, equipment, risk, and options rather than global player location.
- Do not build a world map or standalone transportation network.
- Do not expose inert “coming soon” targets or rewards; content is visible only when it works end to end, except authentic player-state locks on working content.

## Current Foundation

- Sixteen complete skill surfaces, five partial Combat-trained skills, and four planned skills.
- Unified Combat with XP routing for Attack, Strength, Defence, Constitution, Ranged, and Magic.
- A 194-row pre-EOC quest catalog and stage-gate engine, treated as coverage scaffolding rather than full quest parity.
- Utility/Activities, Bank Claims, NPC shops/economy, equipment, carried inventory, achievements, undo, source tooling, assets/provenance, and full pure/Qt test suites.

## Success Criteria

- All 25 pre-EOC skills have complete loops or an explicit product exclusion.
- Quests, activities, bosses, economy, acquisition, collections, and rewards reach the same end-to-end standard.
- Every concrete value or gate follows `memory-bank/pre-eoc-source-verification-standard.md`.
- Saves migrate safely; review undo restores every mutation.
- Full pure and offscreen Qt suites stay green, with manual Anki QA for release candidates.
