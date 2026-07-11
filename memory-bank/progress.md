# Progress

## Current Baseline — 2026-07-10

AnkiScape has moved beyond its original four-skill prototype. The live foundation is broad enough that progress is now tracked by completion programs rather than sequential v1 phases.

Canonical status:

- `memory-bank/completion-audit-2026-07-10.md`
- `memory-bank/completion-audit.json`
- `memory-bank/future-work-kanban.md`
- `memory-bank/gap-backlog.json`

Historical implementation detail remains in dated source audits and status artifacts; it is intentionally not duplicated here.

## Implemented Review Skills

- Gathering: Mining, Woodcutting, Fishing, Hunter.
- Artisan: Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Herblore.
- All use stable targets, flat save state, review dispatch, inventory mutation, telemetry, undo, assets/provenance, Skills hub UI, Stats/Bank/HUD integration, and test coverage.

## Partial Combat Skills

Unified Combat already trains:

- Attack
- Strength
- Defence
- Constitution
- Ranged
- Magic

The engine includes weapon-aware styles/attack types, standard bows/arrows, standard elemental combat spells, runes/staff substitution, supplies/loadouts, HP/food, stat potions, poison/antipoison, special energy scaffolding, drops, kill counts, equipment, death/graves/Death's Office, safe recovery, quest combat, target risk previews, carried inventory, banking, and undo.

These six remain planned in `skill_registry.py` because their independent complete skill surfaces and full parity breadth do not yet exist.

## Missing Skills

- Prayer — partial design grill, no live skill loop.
- Summoning.
- Construction.
- Farming.
- Agility.
- Dungeoneering.
- Slayer.
- Thieving.
- Magic also remains incomplete as a full skill because only its combat slice is live.

Every wholly missing skill requires a deep grill; see the canonical Kanban.

## Quests

- 194 pre-EOC catalog rows, with Recipe for Disaster split into subquests.
- Strict starts, prerequisites, quest points, rewards/pending future-skill XP, stage requirements, produced/consumed items, action blockers, branch variants, quest combat integration, availability filters, and many focused hand-audited replacements are live.
- This is coverage scaffolding. Full fidelity still requires quest-by-quest stages, branches, transformations, combat, rewards, journals, unlocks, and missing-skill dependencies.

## Systems That Work

- Skills hub and shared target metadata/renderers.
- Utility/Activities and material processing.
- Bank, carried inventory, target-local Advanced layouts, presets, bank runs, drop mode, and undo.
- Equipment and Combat setup.
- NPC Shops, prices, shared stock, services/actions, player sells, market clock, and shop undo.
- Bank Claims and pending skill XP rewards.
- Achievements and Stats.
- Review HUD, floating XP, level-up/achievement feedback, settings, and review action multipliers.
- Item registry, asset scraping/provenance, source generators, quest/source audit tooling, and OpenRS2 cache queries.

## Latest Parity Additions

- Lava eel Cooking (`a3cb89e`).
- Overload mixing and explicit RS3 asset sourcing (`28359a7`).
- Cannonball Smithing with quest/mould/carried-layout/undo behavior (`fefca70`).
- Cannonball-aware Smithing generator (`e64269c`).
- Mould-aware Crafting fixtures and tanning icon contract repair (`5b13ff2`).

## Detailed Existing-Skill Backlog

`memory-bank/gap-backlog.json` is authoritative for the eleven registered skills. At the completion audit:

- 22 cards merged.
- 12 design-settled/source-waiting.
- Four split-scope.
- One parked Farming seed.
- One pending source verification.
- One partially reopened/source-waiting.
- One post-cutoff rejection.
- One product-scope rejection.

Do not promote a waiting card by guessing values. Split a proven sub-slice from a blocked family when appropriate.

## Not Yet Complete

- Eight wholly missing skill loops plus full Magic.
- Full combat/equipment/enemy/boss/instance breadth.
- Quest-by-quest fidelity across all 194 rows.
- Activities, minigames, D&Ds, reward currencies/shops, and timed events.
- GE and broad acquisition closure.
- Achievement diaries, clue scrolls, collection tracking, and one-time world rewards.
- Global level-1-to-99 and economy pacing.
- Release-readiness and public/private distribution decision.

## Test Baseline

After the 2026-07-10 overnight pass:

- `python3 run_tests.py`: 998 passed, 160 skipped.
- Full offscreen Qt discovery: 998 passed.

Test counts are historical snapshots, not permanent assertions; current runs outrank this note.
