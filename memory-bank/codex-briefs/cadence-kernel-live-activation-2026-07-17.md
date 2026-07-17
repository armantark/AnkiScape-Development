# Implementation prompt — activate the cadence kernel

Continue from the current AnkiScape repository state. Do not restart the cadence
work from its old phase plan: inspect what is already live, what remains shadow-only,
and what is still using pre-kernel behavior.

## Outcome

Finish the live cadence-kernel activation so sourced pre-EOC XP/hour and
one-action-per-card use one coherent exchange rate:

- `R = 1000` eligible successful reviews per balancing-hour at action multiplier 1.
- Ordinary Combat advances exactly **6 game ticks (3.6 simulated seconds) immediately**
  per eligible successful review at multiplier 1.
- Source-ready skilling routes use their declared `rate_limited`,
  `embedded_probability`, or `passthrough` contracts live.
- Every implemented XP-bearing review handler is exhaustively classified. No skill
  may remain outside the kernel merely because it was absent from the original
  six-skill shadow adapter.
- The shipped behavior is live by default. Preserve an explicit rollback flag whose
  off path is byte-for-byte and RNG-for-RNG identical to the current legacy path.
- No gameplay mechanic may read the wall clock.

This is a real activation, not another telemetry-only or shadow phase.

## Read before editing

Follow `AGENTS.md`, then read every Memory Bank file it requires. At minimum inspect:

- `memory-bank/cadence-kernel-contract-2026-07-13.md`
- `memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`
- `memory-bank/simulation-time-boundary-2026-07-16.md`
- `memory-bank/combat-design-grill-2026-06-23.md`
- `memory-bank/systemPatterns.md`
- `memory-bank/activeContext.md`
- `cadence_kernel.py`
- `cadence_shadow.py`
- `combat_data.py`
- `runtime_actions.py`
- `logic_pure.py`
- storage, settings, dispatch, undo, telemetry, and relevant tests

Audit `git status`, the full dirty diff, recent commits, and all worktrees first.
Preserve other threads' dirty changes. If concurrent implementation requires a
worktree, create it only through `python3 tools/worktree_guard.py add ...`; never put a
second add-on checkout beneath `addons21`. Integrate finished work back deliberately
and verify the canonical checkout contains it.

## Settled live mechanics

### Combat

1. Do **not** accumulate six-tick credits and release a 50-tick burst every eight or
   nine reviews. That would produce several apparently dead cards followed by a lumpy
   kill/death/drop transaction. Resolve six ticks immediately on every eligible
   successful review.
2. Do **not** globally redefine `COMBAT_BURST_TICKS`. The old 50-tick constant anchors
   unrelated recovery and effect assumptions. Introduce an explicit live
   per-review combat cadence and audit every former 50-tick coupling.
3. An action multiplier `M` advances `6 * M` combat ticks in the same review
   transaction.
4. Combat encounters persist across reviews. A fresh encounter retains the current
   opening attack behavior; later reviews continue the same attack schedule instead
   of granting another free opening attack.
5. Persist all state needed to make chunked combat continuous, including:
   - player and enemy attack countdown/phase;
   - per-enemy curse-ramp progress;
   - fractional/residual special-attack regeneration;
   - Prayer drain progress and combat status/effect clocks;
   - any familiar, poison, auto-eat, auto-flee, ammunition, rune, or temporary-effect
     state whose result depends on elapsed combat ticks.
6. Six consecutive six-tick calls against one uninterrupted encounter must match one
   continuous 36-tick simulation for attack scheduling, damage opportunities, Prayer
   drain, special regeneration, poison/status progression, supplies, and RNG order,
   except at an explicitly documented review-boundary control.
7. A kill, death, flee, bank-run boundary, or other terminal result ends that review.
   Do not bank unused ticks and do not start a second ordinary kill in the same review.
8. Again/failed answers advance the established world/passive consumers but perform
   no combat tick, player attack, enemy attack, poison combat tick, foreground
   resource use, XP, death, or encounter progress. They disengage the encounter for
   safe-boundary automation while preserving the wounded enemy and its combat phase
   for re-engagement. Do not silently heal or reset the enemy.
9. Preserve one-review atomicity: Anki undo must restore encounter phase, LP, status,
   Prayer, special energy and residuals, supplies, familiar state, XP, drops, kill and
   Slayer progress, death/grave state, cadence state, and telemetry together.
10. Quest combat remains a collapsed, non-repeatable quest-stage action rather than a
    new multi-review combat UI. Document its cadence exemption and prove it cannot
    become a repeatable XP or loot faucet. Do not use its existing 500-tick constant as
    the ordinary Combat cadence.

The old contract's claim that Combat advances about six ticks per review while
retaining a hidden 50-tick tactical decision tranche is contradictory. Replace it
with the immediate six-tick model. The review boundary already supplies the tactical
decision boundary; automatic safety behavior runs inside each six-tick slice.

### Skilling profiles

- `rate_limited`: use the exact deterministic integer/rational residual scheduler.
  When it emits, perform the declared opportunity. Do not also apply the removed
  square-root adapter, an authentic success/depletion roll, a bank delay, or another
  cadence gate when the sourced rate already includes that factor.
- `embedded_probability`: admit exactly one attempt per eligible successful review,
  apply the authentic outcome probability, and apply no kernel admission gate.
- `passthrough`: retain one action/attempt per eligible successful review.
- `source_blocked`: retain current live behavior and keep the row visibly classified;
  do not manufacture source precision merely to route it through the kernel.
- Respect each provenance row's `includes` metadata. XP/action, urns, banking,
  dropping, success, depletion, and other modifiers must be counted exactly once.
- Only the selected route advances. Switching preserves inactive route residuals.
- Never promote shadow credit into live cadence state. Initialize/sanitize live state
  independently so enabling the feature cannot release a backlog of shadow actions.
- Keep `cadence_wait`, `attempt_failure`, and `success_with_risk` distinct in both UI
  feedback and telemetry.

### Whole-addon coverage — no silent skills

The original shadow adapter covers only Mining, Woodcutting, Fishing, Hunter,
Cooking, and Firemaking. That is an implementation checkpoint, not the intended
product boundary.

Build one auditable cadence-coverage matrix for every implemented review skill and
every other XP-bearing foreground review route. Validation must fail when a new
implemented review handler lacks a declaration. Each route must name:

- its live mode;
- its exact source/profile row or honest `source_blocked` reason;
- whether success, depletion, banking, travel, batching, or modifiers are already
  included;
- its action multiplier behavior;
- its undo boundary;
- whether the flag-off path uses a distinct legacy implementation.

Cover at least the complete current registry:

- Mining, Woodcutting, Fishing, Hunter, Cooking, and Firemaking: migrate every
  source-ready shadow row to live behavior; retain explicit blocked rows.
- Thieving: preserve and reconcile the already-live canary rather than implementing
  a second scheduler beside it.
- Smithing, Crafting, Fletching, Runecrafting, Herblore, Prayer, Magic,
  Construction, Agility, and Summoning: classify every selectable route, not merely
  the default target. `passthrough` is valid only when one review really represents
  the approved action unit; `source_blocked` is valid only with a recorded reason.
- Seed the matrix with the deterministic period rows already present in
  `tools/sourced_xp_rates.py`: High Alchemy, superheating mithril, dragonhide bodies,
  elemental battlestaves, Ardougne urn crafting, and gilded-altar dragon bones.
  Activate compatible live targets using those exact rates and `includes` metadata;
  do not leave them stranded as evidence used only to justify `R`.
- Attack, Strength, Defence, Constitution, Ranged, and combat Magic inherit
  ordinary Combat's six-tick cadence and must not add a second admission gate.
- Farming remains a background/queued simulation with its established answered-card
  clock and is explicitly cadence-exempt; do not force it into foreground admission.
- Planned Slayer and Dungeoneering do not need fake live handlers. Record how their
  future XP-bearing actions attach to this coverage contract so their implementations
  cannot bypass it.

Also inventory XP-bearing quest stages and no-XP Utility/Activity review actions.
Classify intentional exemptions such as collapsed, non-repeatable quest combat.
Do not silently treat an activity as one balancing-hour model merely because it is
not listed in `skill_registry.py`.

The implementation is incomplete if its final report names only Combat and the six
shadow skills. It must include the coverage matrix and prove that every current
review handler is either live through the kernel, intentionally passthrough, a
documented exemption, or source-blocked with current behavior preserved.

## Concrete defects to expect

Do not implement this as a constant replacement. The current combat engine appears to
reset `next_player_attack` and `next_enemy_attack` on every call, recompute curse ramps
from the current call's tick count, and floor special regeneration with an expression
equivalent to `int(ticks * 10 / 50)`. With six-tick calls those behaviors create free
attacks, repeatedly reset ramps, and prevent special energy from regenerating. Find and
fix every equivalent chunk-boundary defect.

Also audit:

- `TEMPORARY_EFFECT_TICKS_PER_ACTION = 50`;
- `SAFE_COMBAT_RECOVERY_TICKS = COMBAT_BURST_TICKS`;
- review-based rest/recovery calibration;
- bank-run review costs;
- combat encounter serialization/migration;
- familiar effects and Summoning safe boundaries;
- action-multiplier behavior;
- UI copy that still calls one review a 30-second burst;
- the feature flag, which currently appears to control shadow computation rather than
  live outcomes.

## Verification

Add only high-signal coverage. At minimum prove:

1. Explicit flag-off results and RNG consumption match the legacy path exactly.
2. The live/default path advances six combat ticks per successful review and `6 * M`
   at multiplier `M`.
3. Failed/Again answers advance no combat state and preserve the encounter.
4. A long chunked encounter is continuous across review boundaries; include different
   player/enemy attack speeds.
5. Special energy uses an exact residual, so accumulated six-tick slices equal the
   corresponding continuous tick total.
6. Prayer, poison/status, temporary effects, curse ramps, familiars, auto-eat/flee,
   death, drops, bank runs, and undo remain coherent.
7. A rational `n/d` profile emits exactly `n` opportunities in `d` assigned reviews,
   including opening-ready and switching behavior.
8. Rate-limited routes do not double-roll or double-charge baked-in conditions.
9. Embedded-probability routes retain one authentic attempt per review with no second
   cadence gate.
10. The XP/hour parity tests are updated so corrected expected failures become ordinary
    passing assertions, while `source_blocked` routes remain explicitly covered.
11. Quest combat remains non-repeatable and does not inherit ordinary six-tick UI or a
    repeatable 500-tick reward path.
12. A registry/dispatch coverage test fails if an implemented XP-bearing review handler
    has no cadence declaration, including handlers added after this migration.

Run focused unit and integration suites first, then the repository's required full
suite. Exercise the real offscreen Qt surfaces if settings, target feedback, or combat
HUD copy changes. Provide a concise manual QA checklist for Anki.

## Completion

Update the cadence contract to remove the stale shadow/phase-plan language and the
50-tick tactical contradiction. Update the required Memory Bank/status handoff with
the exact shipped behavior, migration, tests, and any honestly `source_blocked` rows.
Do not mark the work complete while any intended live adapter still only records shadow
telemetry.

Commit according to the repository rules without staging unrelated concurrent work.
Finish with:

- the exact live routes activated;
- a complete per-skill coverage matrix, including every passthrough, exemption, and
  source-blocked route intentionally unchanged;
- the combat continuity state added or migrated;
- focused, full-suite, Qt, and manual verification results;
- commit hash and canonical-checkout status;
- any genuine external blocker, with evidence.
