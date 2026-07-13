# Progress

## Current Baseline — 2026-07-13

AnkiScape now has 15 complete skill surfaces, five partial Combat-trained skills, and five planned skills. Canonical live status is in `future-work-kanban.md`; the dated 2026-07-10 completion audit is a historical snapshot.

Phase 1 of the cadence kernel is complete on `main` at `b45aff0`. It
adds a dormant pure scheduler, additive config-v34 route residuals, the strict
off-by-default `ankiscape_cadence_kernel` flag, and exact save/load/undo and
flag-off RNG/output regression coverage. No skill behavior is routed or changed.

## Complete Skill Surfaces

- Gathering: Mining, Woodcutting, Farming, Fishing, Hunter.
- Artisan: Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Herblore, Construction.
- Support/combat-adjacent: Prayer and Magic.

These surfaces use stable IDs, flat save state, review or background dispatch as appropriate, inventory mutation, telemetry, undo, assets/provenance, Skills-hub UI, Stats/Bank/HUD integration, and focused tests.

## Partial Combat Skills

Unified Combat trains Attack, Strength, Defence, Constitution, and Ranged. They deliberately remain `partial` because they do not own independent Skills-hub review surfaces. Magic is complete: its noncombat and combat contracts both ship.

## Planned Skills

- Summoning
- Agility
- Dungeoneering
- Slayer
- Thieving

Each needs a closed product/source contract before implementation.

## Latest Closure

The Prayer polish closure adds:

- atomic material/method selection;
- owned gilded altars at 250/300/350% with once-per-stint marrentill;
- 26 five-state training-urn tiers across Mining, Cooking, Fishing, Woodcutting, Smithing, and Prayer;
- target-carried Bonecrusher and Ectoplasmator behavior;
- direct full-urn teleport with immediate persistence and independent LIFO undo;
- substitution-aware skilling and Combat repacks;
- exact Chivalry/Rigour/Augury/Piety Defence gates;
- distinct Bonemeal and Wyvern bonemeal identities plus Prayer/Super prayer restore behavior;
- explicit RS3 provenance for the two new passive icons.

The durable source/conflict record is `source-audits/prayer-altar-urn-passives-herblore-closure-2026-07-13.md`.

## Systems That Work

- Skills hub, target metadata/renderers, Stats, Bank, Equipment, HUD, settings, and achievements.
- Utility/Activities and material processing.
- Target-local carried inventory, Advanced layouts, bank runs, Keep/Drop, Combat loadouts, and undo.
- NPC Shops, shared stock, services/actions, player selling, market clock, and shop undo.
- Bank Claims and pending future-skill XP rewards.
- A 194-row pre-EOC quest catalog with stage gates and focused audited replacements; presence remains scaffolding, not full fidelity.
- Item registry, source generators, asset scraping/provenance, reachability audit, and OpenRS2 cache queries.

## Remaining Programs

- Five planned skill loops.
- Full Combat/equipment/enemy/boss/instance breadth.
- Quest-by-quest fidelity across all 194 rows.
- Activities, minigames, D&Ds, reward currencies/shops, and timed events.
- GE and broad authentic acquisition closure.
- Achievement diaries, clue scrolls, collections, and one-time world rewards.
- Global level-1-to-99/economy pacing and release-readiness.

## Verification Baseline

- Cadence Phase 1 targeted suite: 11 tests passing.
- `python3 -m unittest discover -s tests -q` on `main`: 1,209 tests passing, 187
  skips, three expected failures. The concurrent test-signal cleanup was
  extracted from `main` at `7f3c0a1` and does not affect this count.
- Focused Prayer/passive/urn/logic/combat/Construction/runtime/storage/integration/Farming: 626 tests passing.
- Independent backend audit superset: 663 tests passing.
- `python3 run_tests.py`: 1,198 tests passing, 187 skips, 3 expected failures.
- Full real offscreen Qt discovery: 1,198 tests passing, 3 expected failures.
- Reachability: 1,102 actions, 725 consumed items, 296 orphan inputs (151 root, 145 cascade).
- Compilation and `git diff --check`: clean.

Test counts are snapshots; current runs outrank this note.
