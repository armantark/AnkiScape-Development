# Barbarian Assault role model

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-settled, period horizontal tables source-closed, and horizontal
breadth level one live end to end.**

## Evidence position

Darkan has no Barbarian Assault implementation, so the contract leans on a
pinned pre-cutoff wiki revision plus dated-cache corroboration.

## Owner-settled model (2026-07-18)

- Scope (settled with the cooperative-tier triage): the player plays one role
  per wave; a simulated competent team covers the other roles at bounded
  rates. All four roles are playable because Penance gear costs points in all
  four.
- **Calls are auto-followed** inside the resolved action. Attacker reviews are
  live six-tick Combat slices using the currently called style; defender,
  collector, and healer reviews are duty beats honoring the current call.
  This is a labeled AnkiScape abstraction: the source call test measured
  real-time attention between two humans, which has no analogue when every
  action is an answered card. No call-match prompt and no invented miss roll.
- What survives translation: role duties, wave pressure and progression,
  per-role point economy, and the wave-10 Penance Queen as a live encounter.

## Period horizontal harvest — 2026-07-21

The following literal pre-EOC wikitext revisions now close the smallest honest
mechanic-complete data slice:

- `Barbarian Assault`, oldid `6288360`, timestamp
  `2012-09-24T04:51:33Z`: safe activity, mandatory Captain Cain tutorial,
  ten sequential waves, five-player/four-role shape, and Honour-point or horn
  reward choice.
- `Barbarian Assault/Gameplay`, oldid `6288484`, timestamp
  `2012-09-24T05:21:46Z`: exact Fighter/Ranger/Healer/Runner rosters and
  Fighter/Ranger level, LP, and max-hit rows for waves 1–10; role calls and
  duties; safe wave restart on death/leave; penalty shapes; wave-10 Queen
  appearance; the Collector → Healer → Attacker → Defender → Collector Omega
  chain; and eight required egg launches.
- `Rewards (Barbarian Assault)`, oldid `6316912`, timestamp
  `2012-09-29T08:02:25Z`: the wave 1–9 role formulas, the exact wave-10
  `80` selected-role plus `5` in each other role award, role-level costs,
  complete period armour costs, and `100` points in
  every role for Runner boots without a Queen-kill requirement.
- `Penance Queen`, oldid `5795133`, timestamp `2012-06-21T10:22:41Z`:
  level `209`, `2,500` LP, safe death/restart, `130` maximum hit, normal-attack
  immunity, roughly `300+` damage per Omega egg, the four-role handoff chain,
  and the fixed wave-10 point award.
- `Penance fighter`, oldid `5807126`, timestamp
  `2012-06-22T13:54:23Z`, and `Penance ranger`, oldid `5807125`, timestamp
  `2012-06-22T13:53:48Z`, corroborate the wave-varying combat identities,
  LP, max hits, role restriction, and called-style vulnerability.
- `Runner boots`, oldid `6367883`, timestamp `2012-10-08T06:01:12Z`, proves
  the `100` points in every role price, no Queen requirement, Defence `40`,
  non-tradeable/non-stackable identity, zero weight, and complete bonuses.

OpenRS2 rev-742 item `10552` corroborates Runner boots, `Wear`, and the period
name. 2011Scape rev-667 `data/cfg/items.yml` item `10552` supplies the unchanged
feet-slot, Defence-40, attack/defence/strength equipment block.

## Disclosed AnkiScape translation

- Waves 1–9 use one answered-card duty beat each. The active Attacker beat is
  one live six-tick aggregate-front Combat slice; the fixed competent team
  completes the remaining work. Collector, Defender, and Healer each resolve
  their sourced called duty without an invented miss roll.
- Wave 10 uses one ordinary-Penance duty beat followed by eight persistent
  Omega-egg beats. Each productive beat represents the active role's link in
  the complete sourced CHAD handoff while the competent team covers the other
  links. The bounded `313` LP egg value is the smallest integer that preserves
  the sourced `2,500` LP and eight-egg kill; it is an AnkiScape event-scaling
  value, not a claimed server roll.
- A productive Queen beat includes competent-team healing. An `Again` beat
  advances no egg and applies `65` LP of disclosed bounded Queen pressure;
  death is safe and restarts all of wave 10, matching the source consequence.
- Casual picks the role with the lowest current wallet before each wave.
  Advanced keeps the selected role. Calls are auto-followed as already settled.
- The regular-wave wallet award follows the source formula: competent-team
  role contributions sum into team points, and the active role contribution is
  counted again as the player's individual component. Optional Healer LP-restored
  bonus points are later performance depth; the horizontal row uses sourced
  Healer kills only and invents no healing amount.
- Queen eligibility is persisted as one non-stacking credit because the period
  shop says a Queen kill is required per eligible item and kills do not stack.
  Runner boots exercise the four-wallet purchase without consuming that credit.

## Live horizontal closure — 2026-07-22

`barbarian_assault_data.py`, `barbarian_assault_logic.py`, and the shared
runtime now implement and verify:

- mandatory one-time tutorial, persistent activity ownership, Casual and
  Advanced role policy, all ten waves, four wallets, safe death
  and wave restart, explicit leave, and prior Combat-target restoration;
- live six-tick Attacker combat, idle/Again semantics, persistent Queen LP and
  egg count, eight-step terminal victory, exact wave-10 points, Queen credit,
  and complete-run counters; and
- period Runner boots identity, equipment bonuses, material ownership, exact
  four-wallet purchase, and insufficient-points failure.

A 2026-07-22 independent integration-readiness audit also reproduced and
closed two persistence-boundary defects before shared wiring: entry now refuses
to overwrite an existing Combat encounter, and malformed saved data cannot
reach the Queen phase before wave 10. Both repairs have focused regressions.

Schema 77 now owns migration and repair. The generic Utility review dispatcher,
telemetry, cadence ledger, activity-session arbitration, direct-action undo,
and whole-review undo all preserve the ten-wave/eight-egg boundary. The
Activities-only card exposes the tutorial, Casual/Advanced role plan, four
wallets, wave/Queen progress, Runner-boots purchase, selection, and explicit
leave. Normalized cutoff Omega-egg and Runner-boots art, immutable provenance,
and reproducible fetch/render tools are live.

Focused pure, runtime, migration, cadence, registry, direct-undo, Combat/
Familiarisation, and real offscreen Qt interaction checks pass. Ordinary full
discovery executes 2,433 methods with 307 declared dependency skips and no
failure; real offscreen Qt executes 2,435 methods with one skip and no failure.
Root inspected the 1200×760 ready and Queen dark-palette renders. The requested external taste
pair was unavailable without weakening provider boundaries: Kimi's external
repository-data transfer was denied by the execution policy, Opus could not
refresh local Claude authentication, and Fable remained reserved. This is a
recorded QA availability gap, not a product-design gap. Native Anki control
could not start its local bridge, so no native-card claim is made.

## Explicit source blocks and omissions

- No pinned period source found in this pass states the ordinary Attacker
  Combat-XP multiplier. The aggregate front therefore records no Combat XP
  pending a qualifying source; this is not presented as a historical zero.
- No pinned period page found in this pass states the maximum stored Honour
  points per role. Wallet persistence therefore uses only a technical integer
  sanitizer and presents no historical cap; the exact cap remains
  `source_blocked` data depth.
- The older contract's candidate level-5 Combat gate did not survive the
  pinned activity, basics, gameplay, Fighter, or Ranger pages. Captain Cain's
  tutorial is the only sourced horizontal entry gate. A concrete Combat gate
  remains `source_blocked` rather than inferred.
- Full role upgrades, penance armour, horn potential, weapon paints, trident,
  and gamble tables are period-attested catalog depth. They do not introduce a
  new wave, role, failure, currency, Queen, or purchase state transition beyond
  the representative Runner boots row.
