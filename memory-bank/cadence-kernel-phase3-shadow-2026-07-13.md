# Cadence Kernel Phase 3 Shadow Closure — 2026-07-13

## Outcome

Phase 3 observes the existing Mining, Woodcutting, Fishing, Hunter, Cooking,
and Firemaking adapters behind `ankiscape_cadence_kernel`. It records the live
outcome and the kernel proposal side by side. It does not route live XP, loot,
inventory, success, or failure through the kernel.

The complete runtime catalog contains 175 routes. Twenty-four have compatible
pinned pre-cutoff XP/hour evidence and produce proposals; 151 are retained in
the report as `source_blocked`. Combat and Thieving were not changed.

## State and Undo Decision

The frozen plan proposed an external JSONL observer. Implementation instead uses
`player_data["cadence_shadow"]`, a dedicated instrumentation namespace separate
from dormant live `player_data["cadence_profiles"]`. This is the smallest way to
satisfy the cadence contract's atomic save/load/undo requirement: an Anki review
undo restores the gameplay outcome, shadow residual, and aggregate together.

The flag-on save can therefore contain additional instrumentation bytes. The
verified invariant is stricter where gameplay matters: flag on and off have the
same per-review gameplay projection, XP, loot, callback sequence, dormant live
cadence state, and final RNG state. Shadow state can never seed live residuals.

## Adapter Rules

- Mining, Woodcutting, Fishing, and Hunter advance independent exact low/high
  source-rate profiles. A ranged source stays a range and may report a split.
- Cooking and Firemaking reuse the random value already drawn by the live
  handler, compare it to the authentic source success probability, and draw no
  extra random value. Their five sourced routes explicitly declare
  `cap_one_action` and bypass residual scheduling.
- Mining iron also declares `cap_one_action` because its upper source envelope
  exceeds `R = 1000` successful actions per balancing-hour.
- Every completed attempt reaches the existing central action recorder once.
  The shadow recorder is lazy and exception-contained so instrumentation cannot
  make a live action fail.

## Source Boundaries

The reporter enumerates every live route, even when no proposal is defensible.
Notable fail-closed decisions include:

- ordinary Mining gold is not concentrated gold;
- runite coins/hour is not XP/hour;
- mixed leaping fish is not a sturgeon-only rate;
- the quoted rocktail 48,000 XP/hour includes urns and is displayed but never
  decomposed into a cadence-setting base rate;
- black warlock barehand evidence is not applied to the net route;
- all remaining routes without compatible pinned evidence are
  `source_blocked`, not filled from modern or inferred values.

Run the full catalog with:

```bash
uv run python tools/cadence_shadow_report.py --catalog
```

Run accumulated observations from an exported player-data JSON object with:

```bash
uv run python tools/cadence_shadow_report.py --input /absolute/path/player.json
```

Both commands accept `--format json` for machine-readable exact fraction pairs.

## Verification

- Focused cadence/runtime/integration/parity suite: 176 tests, three expected failures.
- Full non-Qt discovery: 1,219 tests, 187 environment skips, three expected failures.
- Full real offscreen Qt discovery: 1,219 tests, three expected failures.
- Fixed-seed end-to-end exercise: 16 real reviews for one route in each of the
  six adapters, comparing every per-review gameplay projection and callback
  sequence plus final RNG state with the flag on and off.
- Source-blocked live proof: 16 runite reviews produced six ore, 750 Mining XP,
  and 46,875 observed XP/hour while creating no cadence residual.
- Review undo restores the complete pre-review player-data snapshot, including
  removal or rollback of shadow residuals and aggregates.
- Compilation, protected-file diff, and whitespace checks are clean.

The repository's three expected failures remain unchanged. They are deliberate
parity sentinels, not Phase 3 regressions.

## Manual QA

1. Leave `ankiscape_cadence_kernel` false, answer cards for one route in each of
   the six skills, and confirm normal XP, loot, and UI behavior.
2. Enable the flag and repeat with the same targets. Confirm normal visible
   gameplay remains unchanged.
3. Exercise one source-ready route and one blocked route, export player data,
   and run the observed reporter. The ready row must show live and proposed
   XP/hour; the blocked row must show live XP/hour and `source_blocked` without a
   residual profile.
4. Undo the most recent answer in Anki. Re-export and confirm both the gameplay
   mutation and the matching shadow observation rolled back together.
5. Disable the flag again. Existing shadow history may remain inert in the save,
   but new reviews must not advance it.
