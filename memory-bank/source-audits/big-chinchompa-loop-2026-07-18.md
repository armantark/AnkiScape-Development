# Big Chinchompa review-native contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period structure, discovery, aggregate communal pressure, action
unit, rewards, and cadence closed for implementation.**

## Pinned period evidence

`Big Chinchompa`, oldid `6538836` (`2012-11-06T10:56:45Z`), establishes:

- a safe, twice-daily Hunter D&D with no entry requirement beyond membership;
- a randomly located Nyriki at Hunter areas, synchronized event timing, and a
  direct portal route;
- a twenty-minute event that may end earlier when the communal Plutonial
  Chinchompa becomes full;
- joining an event already in progress with only its remaining opportunity;
- one supplied Moth jar holding at most fifteen moths;
- manual flying/branch catches plus Protea-flower attraction of the
  highest-level moth the player can catch;
- eight moth tiers at Hunter levels `1/13/26/39/52/65/78/91`, with exact
  catch XP `15/50/150/250/300/320/400/450` and points
  `1/2/5/8/12/15/18/21`;
- a personal 1,500-point event cap after which moth releases still grant
  Hunter XP;
- Competence points awarded at event resolution, capped at 20,000; and
- a reward shop containing five per-catch private-ground quota tickets,
  Protea flowers, swamp toads, flax, swamp tar, and direct Hunter XP at five XP
  per point.

`Moth jar`, oldid `6484579` (`2012-10-27T10:13:33Z`), independently confirms
the one-jar limit, fifteen-moth capacity, central emptying action, and Hunter XP.
`Protea flower`, oldid `6552181` (`2012-11-13T11:13:53Z`), independently
confirms automatic attraction and that it appears to attract the player's best
eligible moth. `Competence points`, oldid `6241664`
(`2012-09-13T10:20:35Z`), confirms the persistent currency and 20,000 cap.

Sources:

- <https://runescape.wiki/w/Big_Chinchompa?oldid=6538836>
- <https://runescape.wiki/w/Moth_jar?oldid=6484579>
- <https://runescape.wiki/w/Protea_flower?oldid=6552181>
- <https://runescape.wiki/w/Competence_points?oldid=6241664>

The pinned sources do not state the moth catch-success roll, catch rate,
Protea-attraction rate, communal fill formula, event-to-Competence conversion,
or exact effect of October 2012's noted rework. Those server values remain
`source_blocked` pending emulator and archive work.

## Discovery and event clock

Big Chinchompa reuses the shared answered-card world-event surface:

- two opportunities occur per 240-card simulated day;
- each discovery chooses and displays a source Hunter-area location;
- the Activity opens directly at that location with no travel review;
- the source twenty minutes use the rational answered-card world clock, never
  wall time; and
- entering late retains only the remaining event window.

Inactive events perform no background work. The next invoked world reducer
derives the current event phase arithmetically from the answered-card counter.

## One aggregate crowd lever

Communal fullness is real. Big Chinchompa reuses Shooting Stars' cumulative
S-curve arrival model: sparse initial discovery, rapid middle growth, then
saturation. The event stores only its current fullness and the shared
world-event population profile. Each answered-card boundary derives one bounded
aggregate crowd-pressure delta; it never creates, iterates, or persists
individual hunters.

The same saved Quiet / Normal / Busy world-population profile planned for
Shooting Stars supplies the S-curve ceiling and pressure here. Big Chinchompa
does not add another checkbox or activity-specific crowd control.

Big Chinchompa consumes the complete shared naturalized-population parameter
set. The answered-card world-day phase shifts the expected population; the
event seed then varies the crowd ceiling, S-curve midpoint, steepness, and
smooth `±10%` phase jitter within the global bounds. Cumulative arrivals and
fullness remain monotonic. This creates different plausible event rhythms
without storing hunters, replaying missed ticks, or adding another
player-facing control.

The event ends when either:

1. its twenty-source-minute answered-card window expires; or
2. aggregate player feeding reaches communal fullness.

Prompt entry therefore provides the best opportunity, while delayed entry or a
busy population can authentically shorten the session. Current fullness,
remaining review-clock opportunity, and the player's 1,500-point progress are
visible. No hidden population detail is computed merely to produce the status
line.

## Jar circuit and cadence

One successful review resolves one complete fifteen-moth jar circuit:

1. use the activity-local Moth jar and Protea flower;
2. catch fifteen moths of the highest tier allowed by the player's current
   Hunter level;
3. empty the jar into the Plutonial Chinchompa; and
4. atomically grant fifteen times that tier's exact Hunter XP and event points.

The circuit is a declared `activity_group`, not fifteen hidden cadence
admissions. At cadence multiplier `M`, resolve up to `M` whole jar circuits,
stopping before the next circuit if the source event clock or communal
fullness has ended the event. A circuit already admitted while the event is
active completes atomically even if its feeding reaches communal fullness.

The 1,500 personal point cap is not a terminal boundary. Further circuits
continue granting Hunter XP but no event points until the event ends, matching
the pinned source.

`Again` performs no player jar circuit and grants no XP or points, but the
answered-card world boundary still advances the event clock and aggregate crowd
pressure. On a successful review, the admitted player circuit resolves before
that boundary's crowd-pressure delta; a player who began a valid action is not
retroactively displaced by the aggregate crowd.

One undo restores the complete review transaction: player XP and points,
personal cap progress, communal fullness, event resolution, Competence points,
world-event clock, and cadence residuals. Crowd pressure is evaluated once per
review boundary, never once per moth.

The fifteen-moth grouping makes the source twenty-minute event meaningful at
AnkiScape's world-clock scale. It does not claim that a RuneScape jar always
took one fixed duration; it is the explicit owner-approved activity
abstraction.

## Rewards and private grounds

At event resolution, earned event points become Competence points one-for-one,
clamped to the source 20,000-point wallet cap. This is the smallest consistent
interpretation of the pinned reward language; if later server evidence proves a
different conversion, implementation replaces this row without changing the
session model.

The complete cutoff reward shop is a bespoke direct-command surface:

| Reward | Competence cost | Hunter requirement |
|---|---:|---:|
| Swamp lizard quota ticket | 4 | 29 |
| Carnivorous chinchompa quota ticket | 6 | 63 |
| Pawya quota ticket | 8 | 66 |
| Polar kebbit quota ticket | 15 | 70 |
| Grenwall quota ticket | 10 | 77 |
| Protea flower | 1 | 1 |
| Swamp toad | 12 | 1 |
| Flax | 2 | 1 |
| Swamp tar | 4 | 1 |
| Hunter XP | 1 | 1 |

Each Hunter-XP point grants the exact source five XP. Purchases consume no
review and are never cadence-multiplied.

Quota tickets unlock no duplicate catch logic. The private-ground variants
reuse their existing ordinary Hunter target, XP, loot, success, inventory, and
cadence contracts, with one matching ticket consumed atomically only when a
creature is successfully collected. Entering the private ground consumes
nothing. A failed attempt leaves the ticket intact.

## Implementation acceptance

The implementation pass must prove:

1. two events per 240-card day and the rational twenty-minute window;
2. late entry and aggregate S-curve early exhaustion;
3. constant-work naturalized population evaluation with no agent list;
4. one fifteen-moth circuit per activity kernel step;
5. exact level, XP, and point rows for all eight moth tiers;
6. continued Hunter XP after the 1,500-point cap;
7. terminal, multiplier, `Again`, save/load, and full undo behavior;
8. one-for-one event-to-Competence conversion and the 20,000 cap;
9. the complete cutoff reward shop; and
10. successful-catch-only quota-ticket consumption through ordinary Hunter
    targets.
