# Project Brief

## Project

AnkiScape is a Python Anki add-on that turns eligible card reviews into a lightweight, persistent pre-EOC RuneScape progression layer. Reviews can advance skills, combat, quests, items, achievements, shops, and world/economy clocks without replacing Anki's study flow.

## Goal

Reach a coherent “complete AnkiScape” rather than accumulating disconnected v1 slices. The canonical scope and work routing are:

- `memory-bank/future-work-kanban.md`
- `memory-bank/gap-backlog.json` as the closed historical record of gaps inside shipped skill families; the Kanban parity ledger owns its open rows
- dated completion audits as historical baseline evidence, not live registry truth

## Product Boundary

- Target RuneScape immediately before EOC, cutoff `2012-11-20`.
- Keep Anki review primary: one successful review is one sourced action by default.
- Preserve source base XP and tune Anki pacing separately.
- Use the 240-reviews-per-day global clock only for background/world/economy cadence.
- Use target-local inventory, equipment, risk, and options rather than global player location.
- Do not build a world map or standalone transportation network.
- Do not expose inert “coming soon” targets or rewards; content is visible only when it works end to end, except authentic player-state locks on working content.

## Foundation

- Complete skill surfaces, Combat-trained partial skills, and a partial Dungeoneering surface; `memory-bank/future-work-kanban.md` names the surfaces that are still missing or incomplete.
- Unified Combat with XP routing for Attack, Strength, Defence, Constitution, Ranged, and Magic.
- A pre-EOC quest catalog and stage-gate engine, treated as coverage scaffolding rather than full quest parity; `python3 tools/audit_quest_stage_gate_coverage.py` prints the census.
- Utility/Activities, Bank Claims, NPC shops/economy, equipment, carried inventory, achievements, undo, source tooling, assets/provenance, and full pure/Qt test suites.

## Success Criteria

- All 25 pre-EOC skills have complete loops or an explicit product exclusion.
- Quests, activities, bosses, economy, acquisition, collections, and rewards reach the same end-to-end standard.
- Every concrete value or gate follows `memory-bank/pre-eoc-source-verification-standard.md`.
- Saves migrate safely; review undo restores every mutation.
- Full pure and offscreen Qt suites stay green, with manual Anki QA for release candidates.
- A public release follows
  `memory-bank/public-release-lineage-and-license-2026-07-17.md`: distinct
  derivative identity, prominent original-creator credit, explicit compatible
  licensing, asset provenance closure, and a new AnkiWeb listing.
