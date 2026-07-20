# Dungeoneering starter harvest — 2026-07-20

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Scope: source-close the owner-ratified Frozen solo starter expedition far
enough to build its backend substrate without representing the skill as live.
The owning design is
`memory-bank/dungeoneering-design-contract-2026-07-18.md`.

## Pinned period record

All Wiki claims below were read from literal revision wikitext.

| Page | oldid | UTC timestamp | Proven here |
| --- | ---: | --- | --- |
| Dungeoneering | 6579699 | 2012-11-19T02:31:37Z | 60 floors, six themes, closed session economy, solo support, level `2f-1`, size grids/room maxima, death respawn, bind ladder/loadouts/ammo, payout order |
| Dungeoneering floors | 6542025 | 2012-11-08T00:49:39Z | Frozen 1–11, Abandoned I 12–17, Furnished 18–29, Abandoned II 30–35, Occult 36–47, Warped 48–60 and their level bands |
| Dungeoneering/Prestige | 6516987 | 2012-11-01T21:57:13Z | prestige is `max(current, previous)`, same-theme replay substitution, base XP averages active-floor and prestige-floor XP |
| Complexity | 6555542 | 2012-11-14T19:37:17Z | levels 1–6, skill unlock groups, penalties `50/45/40/35/30/0%`, forced guide mode at C1, skill doors at C5+ |
| Ring of kinship/Classes | 6190515 | 2012-09-03T19:30:40Z | 12 roles, four categories, one active worn role, tier 1–10 effect tables, upgrade costs, one reset/refund |
| Dungeoneering/Bosses | 6398065 | 2012-10-14T01:46:52Z | complete Frozen boss names, level gates, and floor ranges |
| Dungeoneering/Doors | 6325508 | 2012-09-30T17:22:57Z | guardian/key/skill semantics, feasible critical path, bonus over-level doors, `required level × 5` skill XP, qualitative failure damage |
| Dungeoneering/Skills | 4632782 | 2011-08-15T21:54:34Z | ordinary skills participate inside floors |
| Dungeoneering/Fishing | 5812989 | 2012-06-23T16:17:51Z | Raw heim crab at Fishing 1 for 9 XP |
| Dungeoneering/Cooking | 6457563 | 2012-10-23T01:30:20Z | Heim crab at Cooking 1 for 22 XP and 20 LP; fish cooking at C2+ |
| Dungeoneering/Herblore | 6555616 | 2012-11-14T20:45:41Z | Druidic Ritual/C5+ gate, Valerian clean row, Weak ranged potion recipe/level/34 XP |
| Coal bag | 6283103 | 2012-09-22T22:36:07Z | 4,000 tokens, Dungeoneering/Mining 35, one owned, 27 Coal, manual/bank fill, bag-first smelting, no degrade |
| Daemonheim Rewards | 6297239 | 2012-09-25T21:01:33Z | tokens are one per ten raid XP rounded down; reward catalog and Coal bag row |

The starter resource proof chain is `Raw heim crab → Heim crab`. The quarantined
Herblore proof chain is `Grimy valerian → Valerian potion (unf) → Weak ranged
potion`; its period-stated clean and finished values agree with the existing
Daemonheim rows.

## Cache identity

Rev 742 (`2012-11-07`) and rev 727 (`2012-07-24`) both contain:

- item `18339`, `Coal bag`, with Inspect/Withdraw/Destroy options;
- item `15707`, `Ring of kinship`, with party, wear, teleport, customise, and
  destroy options; and
- role variants `18817`–`18828` in the exact Tank-through-Artisan order.

The caches prove identities/options only. They do not prove costs, effects, or
server rolls.

## Reconciled implementation evidence

Darkan commit `e1cf61bf26ffdda8d1e08437af3c79c021f7c880` and its frozen audit
`memory-bank/audit/evidence/static/dungeoneering-floor-tiers-target-contract.json`
independently agree on the floor bands, `2f-1` level rule, complexity
penalties, prestige maximum/average, same-theme substitution, and
`floor(final XP / 10)` tokens. Darkan remains reconstruction evidence, not a
substitute for the period pages above.

## Implemented substrate

- `dungeoneering_data.py` owns the exact floor, size, complexity, bind, kinship,
  Frozen-boss, door, proof-chain, and Coal-bag tables.
- `dungeoneering_logic.py` owns pure level/floor/theme/bind helpers, prestige
  substitution, explicit-input payout arithmetic, Frozen-boss eligibility,
  and the seeded small-floor session graph.
- The graph's default eight-room budget is
  `provisional/owner-approved-review-translation`: the period source proves a
  4×4 grid with at most sixteen and usually fewer rooms, while the contract
  explicitly authorises a provisional per-floor review budget.
- One room on the revealed frontier resolves per call. Death increments the
  counter and returns the session to the start room without erasing resolved
  rooms or the revealed frontier. No wall clock is used.
- Dungeoneering remains `planned` in `skill_registry.py`; no incomplete player
  surface or zero-XP floor was exposed.

## Honest blockers

1. **Active/prestige floor-XP curve — `source_blocked`.** Period Winterface and
   formula/talk history describe the inputs and ordering but do not publish the
   numeric floor function. Darkan's cubic function has no independent
   period-lineage corroboration and is not shipped as historical.
2. **Death coefficient — `source_blocked`.** Death respawn and a significant XP
   penalty are proven; Darkan's ten-percent-per-death coefficient is not
   independently closed. The pure payout helper therefore requires an explicit
   caller-supplied multiplier and defaults only to the no-death identity.
3. **Exact generated room-count distribution — `source_blocked`.** The period
   maximum and "usually fewer" statement are proven. The eight-review starter
   budget is clearly labelled product translation rather than RuneScape fact.
4. **Skill-door failure probability and damage — `source_blocked`.** The period
   page proves that failures can deal moderate-to-severe damage, but not the
   rate or LP magnitude.
5. **Weak magic potion conflict.** The period Herblore oldid states 21 XP,
   while the quarantined game-main-backed row currently stores 23 XP. The
   starter uses the independently agreeing Weak ranged chain instead; the
   conflicting row was not silently rewritten.
6. **Live UI quality gate.** A new Dungeoneering surface requires both Kimi K3
   and Fable taste review plus a fully restarted native Anki check. This backend
   batch creates no new UI.

These are source or external-review blockers, not unresolved owner design
questions. No entry was added to the design-gap ledger.

## Verification

- Focused data, pure-session, Herblore, and registry integration coverage:
  70 tests passed.
- Complete non-Qt discovery: 1,896 tests passed in 49.0 seconds with 248
  expected environment skips.
- Test-quality, documentation, compile, diff, and guarded-worktree audits pass.
  The reachability audit intentionally exits nonzero for its existing backlog
  and confirms the unchanged ledger: 1,268 actions, 1,889 reachable items, 284
  orphan inputs, and 302 blocked actions.
- No Qt or native-Anki pass is claimed for this batch because it adds no live
  UI, registry surface, asset, or runtime hook.
- Results:
  `status-updates/dungeoneering-starter-backend-results-2026-07-20.html`;
  mobile copy: `https://pgbwaae8lohy.postplan.dev`.

## Workflow record

Read-only Workflow `e94e4f58-23be-4ef0-83ab-da2867f7b4c5` produced no usable
result. One Sol-high leaf hit its 240-second inactivity limit; two other leaves
did not establish useful sessions and were canceled after more than ten
minutes. The primary independently reproduced every accepted claim above.
