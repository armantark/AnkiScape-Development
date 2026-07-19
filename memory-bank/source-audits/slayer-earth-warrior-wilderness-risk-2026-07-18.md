# Slayer Earth warrior Wilderness-risk closure

Date: 2026-07-18  
Status: **implemented and verified on `main`; no owner-facing design fork**

## Evidence boundary

The ordinary Earth warrior's identity, level, stats, attack cadence, Slayer XP,
and drop tables remain grounded in the already-live
`other/earth_warrior_level_51.plugin.kts` import recorded by
`combat-enemy-roster-gap-audit-2026-07-07.md`. The Vannaka pool audit places the
ordinary assignment in the Wilderness:
`slayer-vannaka-pool-2026-07-17.md`, Earth warriors row.

PKer frequency is not source-static NPC data. It depended on live player
behavior, so an exact cutoff rate is `source_blocked`. The owner-approved Combat
contract resolves that uncertainty instead of pretending otherwise:

- `combat-design-grill-2026-06-23.md`, decisions 65–67: rare visible bounded
  ambush abstraction, equipment-risk preview, explicit opt-in, and Wilderness
  death retention;
- the same contract, decisions 70–73: leaving or switching away resets a
  Wilderness encounter, and the UI exposes a distinct Wilderness-risk state;
- `source-audits/parity-deviation-ledger-2026-07-06.md`: the already-shipped
  cross-context abstraction uses a 1% trigger and a uniform 1–249 LP hit under
  a declared 250-LP maximum.

This closure therefore labels 1%/250 LP as an AnkiScape abstraction. It does not
claim that either value was a fixed RuneScape PKer statistic.

## Implemented mapping

- `combat_data.py` marks Earth warrior with a `wilderness_risk` contract:
  1% after each successful Combat review, 250-LP declared maximum, and three
  unskulled equipment keeps.
- The ordinary Earth-warrior review resolves first. A triggered ambush then
  deals one uniform 1–249 LP hit and resets the monster encounter. Failed Anki
  answers still do nothing, and the action remains one undoable review
  transaction.
- A fatal ambush keeps the three highest-value equipped items. Active Protect
  Item adds one keep. Other equipped items are permanently removed; ordinary
  inventory and the active carried-pack view remain; no new grave is created.
  Full skull/PvP state remains deferred, so the executable target is explicitly
  unskulled.
- Surviving ambushes may consume the configured combat food at the normal
  auto-eat boundary. They do not create wall-clock state or a persistent PKer.
- A successful safe-skill review clears carried Wilderness encounter progress.
- `combat_session.py` owns a process-local confirmation fingerprint. The Qt
  selector records it only after showing current kept/lost equipment, and the
  runtime refuses to advance Wilderness Combat without it. Restarting Anki
  clears the process state; changing equipment, Protect Item, skull assumption,
  chance, or maximum hit changes the fingerprint and requires a fresh warning.
- The target row shows `Wilderness risk`, chance, maximum hit, kept/lost counts,
  and the no-grave consequence before selection.

## Deliberate limits

This does not implement full PvP, skull acquisition/timers, teleblocks, escape
routes, player archetype loadouts, looters, or ground items. Those are broader
Wilderness/PvP systems. The one-hit ambush is the explicit bounded abstraction
that preserves meaningful equipment risk without inventing a second combatant
or using wall-clock gameplay.

## Verification

- Focused pure/runtime/metadata/Slayer suite: **402 tests passed**.
- Focused real offscreen Qt confirmation checks: **2 tests passed**.
- Complete non-Qt suite: **1,628 tests passed; 215 skipped; zero failures or
  errors**.
- Complete real offscreen Qt menu suite: **211 tests passed**.
- `tools/audit_slayer_readiness.py`: Vannaka advances from 26/35 to **27/35**;
  Earth warriors no longer appear in the blocker ledger.

The bounded read-only Codex Workflows reviewer produced no review material.
Run `a81e1616-7bc0-47a5-ae4f-68b18dc31f5a` failed after 89,349 processed
tokens and three tool calls with the new terminal signature
`provider emitted no startup event within 30s`; the root agent independently
performed the code review and verification rather than treating the failed leaf
as evidence.

The final documentation, test-quality, reachability, diff, and worktree checks
are recorded in
`memory-bank/status-updates/slayer-earth-warrior-wilderness-results-2026-07-18.html`
(<https://73amt4x2o23l.postplan.dev>).
