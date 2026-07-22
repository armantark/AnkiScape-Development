# Pest Control game model

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-settled win/loss engine (shared assault); the cutoff game and
reward tables are source-closed for a horizontal implementation.**

## Cutoff period closure — 2026-07-21

The literal wikitext of `Pest Control`, oldid `6571065`, timestamp
`2012-11-18T04:51:21Z`, establishes:

- the safe-activity boundary and prohibition on pets, cannons, and familiars;
- Novice / Intermediate / Veteran landers at combat levels `40` / `70` / `100`;
- four portals, `2,000` portal LP on Novice and `2,500` on the higher landers;
- a `2,000`-LP Void Knight, `500` LP restored per destroyed portal, victory by
  destroying all portals or keeping the knight alive for twenty minutes, and
  loss when the knight dies;
- the source participation gate of `500` damage, with a repaired gate or
  barricade counting as `50` damage;
- half ordinary combat XP while playing, with the page's separate portal-XP
  note;
- coins equal to `combat level × 10`, not Darkan's `× 100`; and
- `2` / `3` / `4` commendations for the three landers, not Darkan's `3` / `5`
  / `7`.

Source:

- <https://runescape.wiki/w/Pest_Control?oldid=6571065>

The literal wikitext of `Void knight commendations`, oldid `6441647`,
timestamp `2012-10-19T04:44:16Z`, establishes the `500`-point wallet cap, the
exact combat-XP formula and bulk bonuses, the complete equipment table, the
`10`-point eight-charge Void seal, `30`-point herb pack, `15`-point mineral and
seed packs, and four `2`-point familiar charms. It also establishes the shared
Void-equipment gate of Attack / Strength / Constitution / Ranged / Defence /
Magic `42` and Prayer `22`.

Source:

- <https://runescape.wiki/w/Void_knight_commendations?oldid=6441647>

2011Scape rev-667 `data/cfg/items.yml` corroborates the charged item family:
Void seal `(8)` through `(1)` are IDs `11666` through `11673`, use the neck
slot, are untradeable, and carry `+1` stab/slash/crush/magic/ranged defence and
`+1` Summoning defence.

For horizontal breadth, the Void seal is the smallest exact reward row that
also exercises a distinct Pest Control mechanic: direct purchase, eight
persisted charges, and an in-game area attack that does not satisfy the
participation gate. The rest of the exact catalog is data depth, not another
state transition.

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

## Remaining implementation work

1. Reconcile pest-role behavior (Spinners healing portals, Shifters
   teleporting, Brawlers blocking, Splatters exploding, Defiler/Torcher
   ranged pressure on the knight) into the aggregate front and knight-pressure
   terms; record what each role contributes rather than simulating actors.
2. Derive the event-scaled review budget from the source game shape and
   record it as `provisional/<source>` if the period record cannot attest it.
3. Void Knight equipment beyond the representative Void seal,
   herb/mineral/seed packs, and the Call to Arms
   familiar special (parked behind this activity in
   `summoning-familiar-teleports-2026-07-16.md`) attach to this activity once
   its runtime exists.

## Horizontal pure substrate — 2026-07-21

`pest_control_data.py` and `pest_control_logic.py` now close the isolated pure
state machine while the shared runtime/UI files remain owned by the concurrent
Circus batch. This is implementation progress, not a claim that Pest Control
is live yet.

- One game is a disclosed twelve-review event: three consequential shared-
  assault beats per source portal. The source twenty-minute duration is not
  converted through the wall clock.
- Novice crowd portal damage is `900` per beat; Intermediate and Veteran use
  `1,120`. The four aggregate fronts apply Brawler obstruction (`85%` crowd
  damage), Spinner healing (`120` portal LP), Defiler/Torcher knight pressure,
  and Shifter/Splatter breakthrough pressure. The corresponding knight-
  pressure rows are `250/300/425/500` LP.
- Defending relieves `400` pressure and receives the source repair-equivalent
  `50` contribution. A Void-seal discharge relieves `300`, consumes exactly
  one of its eight persisted charges, and adds no participation contribution.
- These rate rows are `provisional/oldid-6571065`: they preserve the source
  roles and real LP while producing the owner-settled attack/defence tradeoff.
  They are deliberately not represented as historical server values.
- Portal attacks use the live six-tick Combat kernel at the source half-XP
  multiplier. Safe player death leaves the team game running; knight death,
  explicit departure, or event expiry pays nothing.
- Wins pay the source `combat level × 10` coins and `2/3/4` commendations,
  capped at `500`. The representative ten-commendation reward is a period
  Void seal `(8)` whose complete `11666–11673` charge/equipment family is
  registered by the data module.

Fourteen focused pure tests cover the period tables, state repair, lander and
session gates, follower exclusion, automatic and explicit policies, crowd
progress, defence loss avoidance, all-out-assault loss, Again, safe death,
half-rate Combat integration, reward cap, charge preservation, and forfeit.
