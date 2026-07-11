# Active Context

## Current Focus

Autonomous completion closure, continuing the repo-wide audit with truthful partial-skill status and machine-readable item acquisition reachability.

Use these as the current handoff sources:

1. `memory-bank/future-work-kanban.md` — canonical forward-work board.
2. `memory-bank/completion-audit-2026-07-10.md` — human-readable completeness analysis.
3. `memory-bank/completion-audit.json` — machine-readable 25-skill and cross-system ledger.
4. `memory-bank/gap-backlog.json` — detailed shipped-skill subledger and settled grill decisions.
5. `memory-bank/pre-eoc-source-verification-standard.md` — permanent evidence contract.

## Current Truth

- `skill_registry.py` has 11 complete review skills, six partial Combat-trained skills, and eight planned skill definitions.
- Attack, Strength, Defence, Constitution, Ranged, and Magic use the explicit partial-surface contract; quest gates/rewards recognize them as trainable without pretending that they own full standalone skill surfaces.
- Prayer, Summoning, Construction, Farming, Agility, Dungeoneering, Slayer, and Thieving are wholly missing skill loops.
- Magic needs a full skill continuation beyond its live standard combat spell ladder.
- The 194-row quest catalog and stage-gate engine are scaffolding. Presence is not full quest parity.
- NPC Shops are live. The fake GE design is locked and parked until broader skill/item coverage.
- The detailed shipped-skill gap ledger currently has 22 merged cards; Grenwall is explicitly source-blocked after its pinned revision failed to prove exact reward probabilities.
- The live item graph currently finds 267 orphan action inputs. The canonical breakdown and command live in `memory-bank/source-audits/item-reachability-audit-2026-07-11.md`.

## Most Recent Completed Work

The 2026-07-10 overnight pass implemented and committed three fully evidenced sub-slices:

- Lava eel Cooking: level 53, 30 XP, never burns.
- Overload mixing: level 96, five three-dose extremes plus clean torstol, 1,000 XP, four Vials returned.
- Cannonball Smithing: level 35, Dwarf Cannon gate, one Steel bar plus retained Ammo mould, four Cannonballs, 25.6 XP.

It also made Smithing regeneration preserve cannonballs and repaired stale offscreen UI contracts for held moulds and tanning icons. That historical pass ended at 998 tests on each surface.

The 2026-07-11 closure pass added the partial/complete/planned skill contract, direct partial-skill quest/action XP and pending-XP migration, the acquisition reachability audit, and a repair for the Woodcutting nest → empty nest → crushed nest chain.

Current verification baseline: 1,001 pure tests and 1,001 full offscreen Qt tests passing, with 160 expected non-Qt skips in the pure interpreter.

## Decision Boundaries

- Full pre-EOC cutoff: `2012-11-20`.
- Pinned wiki/Wayback establish period behavior; period caches establish client identity/config; 2011Scape and Darkan require reconciliation.
- Darkan may be an explicit wait dependency for hidden server behavior. The local restoration checkout is moving and should not be treated as a stable final baseline until a milestone is declared.
- Do not re-grill decisions already closed in `memory-bank/gap-grill-decisions-2026-07-10.md`.
- Resume the partial Prayer grill in `memory-bank/ankiscape-skill-expansion.md`; do not restart it.
- Each wholly missing skill needs its own deep grill before implementation.
- Activities/minigames use Utility/Activities at the platform level, but each family needs a dedicated grill and complete reward/state/source contract.
- Global level-1-to-99 time balancing waits until all skills and major methods are present.

## Current Risks

- Treating generated quest rows or modern emulator code as proof of fidelity.
- Allowing the moving Darkan restoration to create repeated merge/re-audit churn.
- Reopening settled product decisions instead of resolving source facts autonomously.
- Adding visible disabled stubs rather than end-to-end content.
- Letting old Memory Bank changelogs outrank live registries and the canonical board.

## Next Recommended Work

1. Resume and finish the Prayer deep grill, or begin another missing-skill grill when the owner is available.
2. Close reachability roots only through their authentic owning skills, activities, Combat drops, quests, shops, spawns, claims, and item actions.
3. When Darkan reaches a stable restoration milestone, rerun Grenwall, quest, missing-skill, and special-activity audits against the changed source surface.

## Verification Contract

- Pure/data/unit/integration/end-to-end tests for behavior changes.
- Offscreen Qt tests for UI changes.
- Full `python3 run_tests.py` and full offscreen suite before feature closure.
- Manual Anki review instructions for user-facing behavior.
- Pre/post status artifacts for normal complex work.
