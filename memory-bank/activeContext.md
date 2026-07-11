# Active Context

## Current Focus

Prayer and Magic both shipped on 2026-07-11 (commits `ed1327b` and `24fbafd`), each implemented in full from its closed contract by a delegated build and independently verified before commit. The Construction deep grill closed the same day; `memory-bank/construction-skill-contract-2026-07-11.md` is Construction's implementation-ready contract and queues as the next build. Construction is the first skill sourced primarily from Darkan (game-main has no Construction), with its two behavior gaps (burner lighting, flatpack crafting) wiki-pinned and handed off to the restoration loop.

Use these as the current handoff sources:

1. `memory-bank/future-work-kanban.md` — canonical forward-work board.
2. `memory-bank/completion-audit-2026-07-10.md` — human-readable completeness analysis.
3. `memory-bank/completion-audit.json` — machine-readable 25-skill and cross-system ledger.
4. `memory-bank/gap-backlog.json` — detailed shipped-skill subledger and settled grill decisions.
5. `memory-bank/pre-eoc-source-verification-standard.md` — permanent evidence contract.

## Current Truth

- `skill_registry.py` has 13 complete review skills (Prayer and Magic joined on 2026-07-11), five partial Combat-trained skills, and seven planned skill definitions.
- Attack, Strength, Defence, Constitution, and Ranged use the explicit partial-surface contract; quest gates/rewards recognize them as trainable without pretending that they own full standalone skill surfaces.
- Summoning, Construction, Farming, Agility, Dungeoneering, Slayer, and Thieving are wholly missing skill loops.
- The 194-row quest catalog and stage-gate engine are scaffolding. Presence is not full quest parity.
- NPC Shops are live. The fake GE design is locked and parked until broader skill/item coverage.
- The detailed shipped-skill gap ledger currently has 22 merged cards; Grenwall is explicitly source-blocked after its pinned revision failed to prove exact reward probabilities.
- The live item graph currently finds 267 orphan action inputs. The canonical breakdown and command live in `memory-bank/source-audits/item-reachability-audit-2026-07-11.md`.

## Most Recent Completed Work

The 2026-07-11 implementation pass landed both closed contracts as delegated builds, each independently re-verified before its commit:

- Prayer (`ed1327b`): prayer_data.py with per-row citations; bury/scatter/Ectofuntus (~9 bones per review)/hosted gilded altar with the 1-10-review house-finding roll; two-tick drain, curse ramps, Soul Split/Deflect EV translation; named combat presets with per-target pins (storage v29); Knight Waves as an 8-review landmark; 42 assets with provenance.
- Magic (`24fbafd`): magic_data.py with 94 noncombat targets across Standard/Ancient/Lunar; uncapped 40%/60% alchemy against cached values with elemental-staff substitution; combat roster gap-fill (god spells behind a five-review Mage Arena landmark, 16 Ancients, four Miasmics from Darkan); preset schema extended with spellbook/autocast/Vengeance/Dream/Swap (storage v30); the curated three casual controls; 122 assets with provenance.

Notable conservative resolutions recorded in the delegated reports: Rapid Renewal restores at the pinned 65/230 rather than the emulator's 60/240; no Ancient bonemeal was invented; the Prayer renewal gradual-restore formula was omitted as unproven; Miasmic spells ship with authentic data but no invented NPC attack-speed effect; Bones to Peaches stays visible but gated behind a future Mage Training Arena activity.

The 2026-07-10 overnight pass implemented and committed three fully evidenced sub-slices:

- Lava eel Cooking: level 53, 30 XP, never burns.
- Overload mixing: level 96, five three-dose extremes plus clean torstol, 1,000 XP, four Vials returned.
- Cannonball Smithing: level 35, Dwarf Cannon gate, one Steel bar plus retained Ammo mould, four Cannonballs, 25.6 XP.

It also made Smithing regeneration preserve cannonballs and repaired stale offscreen UI contracts for held moulds and tanning icons. That historical pass ended at 998 tests on each surface.

The 2026-07-11 closure pass added the partial/complete/planned skill contract, direct partial-skill quest/action XP and pending-XP migration, the acquisition reachability audit, and a repair for the Woodcutting nest → empty nest → crushed nest chain.

The 2026-07-11 Prayer grill session finished the design: all methods (bury, scatter, Ectofuntus at ~9-bones-per-review grinding, hosted gilded altar with free burners behind a 1–10-review house-finding roll), the EV prayer/curse combat translation with the four-step uptime policy, prayer points/drain/restore, the Rapid Restore analog, and UI placement. The Chaos Temple Wilderness bone altar was struck as OSRS-2018 contamination. Owner decisions this session: Ectofuntus "slow grinder" pacing, free hosted burners with self-supplied herbs deferred to Construction, and — on second pass — prayer selection/uptime folding into a named combat preset system (bundling supply loadout and pack mode) with per-target override, instead of raw per-target checkboxes. The chaos-altar strike was re-verified: both pre-EOC temple pages are recharge-only, and the offering altar is OSRS 7 Dec 2017.

The 2026-07-11 Magic grill session (same day, after Prayer) settled the full Magic continuation: uncapped full-parity alchemy with elemental-staff substitution on noncombat casts, teleports as pure training casts (no invented travel hooks), all three spellbooks (Ancients/Lunar wiki-pinned, quest-gated) with implicit book state and a strict per-preset/per-stint no-mixing rule, Spellbook Swap preserved as the single sanctioned no-mixing exception, Dream as a review-cost between-fight heal policy, and a casual-mode answer to checkbox creep: the pack-mode dial derives prayer/uptime/Vengeance/swap choices and casual mode surfaces exactly three toggles (prayers on/off, contextual autocast picker, Dream thrift). Every edge-case spell got an explicit disposition: a salvage ledger (Bake Pie, Humidify, Magic Imbue, Superglass/Tan Leather/String Jewellery/Plank Make, Hunter Kit, Crumble Undead, Monster Examine readout, telegrab→Wine of Zamorak), a pure-cast bucket, a strictly-other-player not_applicable bucket, and a Livid Farm deferral.

Current verification baseline: 1,031 pure tests and 1,031 full offscreen Qt tests passing, with 166 expected non-Qt skips in the pure interpreter.

## Decision Boundaries

- Full pre-EOC cutoff: `2012-11-20`.
- Pinned wiki/Wayback establish period behavior; period caches establish client identity/config; 2011Scape and Darkan require reconciliation.
- Darkan may be an explicit wait dependency for hidden server behavior. The local restoration checkout is moving and should not be treated as a stable final baseline until a milestone is declared.
- Do not re-grill decisions already closed in `memory-bank/gap-grill-decisions-2026-07-10.md`.
- The Prayer grill is closed; `memory-bank/ankiscape-skill-expansion.md` is its implementation contract. Do not re-grill it — the remaining items there are mechanical source extractions.
- The Magic grill is closed; `memory-bank/magic-skill-contract-2026-07-11.md` is its implementation contract. Do not re-grill it — the remaining items there are mechanical source extractions.
- The Construction grill is closed; `memory-bank/construction-skill-contract-2026-07-11.md` is its implementation contract. Do not re-grill it — the remaining items there are mechanical source extractions.
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

1. Implement Construction from `memory-bank/construction-skill-contract-2026-07-11.md`, or begin the next missing-skill grill (Farming or Summoning) when the owner is available.
2. Close reachability roots only through their authentic owning skills, activities, Combat drops, quests, shops, spawns, claims, and item actions.
3. When Darkan reaches a stable restoration milestone, rerun Grenwall, quest, missing-skill, and special-activity audits against the changed source surface.

## Verification Contract

- Pure/data/unit/integration/end-to-end tests for behavior changes.
- Offscreen Qt tests for UI changes.
- Full `python3 run_tests.py` and full offscreen suite before feature closure.
- Manual Anki review instructions for user-facing behavior.
- Pre/post status artifacts for normal complex work.
