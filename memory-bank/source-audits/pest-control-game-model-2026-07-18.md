# Pest Control game model

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-settled win/loss engine (shared assault); full loop contract and
period corroboration remain harvest work.**

## Pinned Darkan evidence

`darkan-world-server` commit `26634568374a1b83b98b04413a191cfba205a758`,
`src/main/java/com/rs/game/content/minigames/pest/PestControl.java`:

- 20-minute game timer (1,200 seconds), ending early when all portals die or
  the Void Knight dies;
- four portals; LP 2,000 at Novice and 2,500 at Intermediate/Veteran;
- staggered portal shield unlocks (`unlockPortal`, scheduled 30 ticks after
  each trigger; the exact unlock cadence needs reconciliation);
- loss when the Void Knight dies: no reward at all;
- a zeal gate: Darkan withholds all reward below 750 accumulated contribution
  points;
- win reward: `combat level × 100` coins plus commendations of 3 / 5 / 7 by
  lander tier; and
- per-tier pest ID pools, per-portal spawn caps, and dedicated Shifter,
  Splatter, Spinner, and Brawler behavior classes.

Darkan is a lead, not a closed fact (its cache base is rev 727 and it can
invent); every number above still needs the ordinary corroboration gate
against a pinned pre-cutoff wiki revision and the dated caches. The 3/5/7
commendation values in particular must be checked against the period record
before they ship.

## Owner-settled model (2026-07-18): shared assault

Solo Pest Control uses the fixed-competent-crowd family pattern with the
crowd sharing the assault:

- The crowd both damages the currently active portal and holds pests off the
  Void Knight, each at a bounded rate applied inside the same atomic review
  reducer as the player's action. No individual crowd actors, positions, or
  background loops are simulated.
- The player's reviews are live six-tick Combat slices against the current
  portal front (portal plus its guarding pests as one visible aggregate,
  following the Troll Invasion pattern), or a defense diversion that relieves
  knight pressure instead.
- Attested portal LP stays real. The crowd's contribution — not rescaled
  portal numbers — closes the solo gap, and the game lands in an event-scaled
  review budget following the Fishing Trawler precedent.
- Loss stays real: ignoring defense while pest pressure runs high can kill the
  knight, ending the game with the source loss consequence (no coins, no
  commendations).
- The zeal gate is trivially satisfied by playing, because reviews are always
  contribution. This is recorded as a labeled AnkiScape abstraction: the
  source penalty targeted loafing players, and AnkiScape has no loafing state.

## Remaining harvest work

1. Pin the nearest pre-cutoff `Fishing Trawler`-grade wiki revision for Pest
   Control and corroborate: lander combat-level tiers, commendation values,
   the coin reward, the zeal/damage requirement, portal shield timing, and
   the 20-minute cap.
2. Reconcile pest-role behavior (Spinners healing portals, Shifters
   teleporting, Brawlers blocking, Splatters exploding, Defiler/Torcher
   ranged pressure on the knight) into the aggregate front and knight-pressure
   terms; record what each role contributes rather than simulating actors.
3. Derive the event-scaled review budget from the source game shape and
   record it as `provisional/<source>` if the period record cannot attest it.
4. Harvest the complete commendation reward shop. Direct-XP purchase rows are
   XP-multiplying rewards and stay hidden until the cadence invariant accounts
   for them, per the settled packet decision 12-B.
5. Void Knight equipment, herb/mineral/seed packs, and the Call to Arms
   familiar special (parked behind this activity in
   `summoning-familiar-teleports-2026-07-16.md`) attach to this activity once
   its runtime exists.
