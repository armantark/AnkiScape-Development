# Big Chinchompa review-native contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period structure pinned; discovery and aggregate communal pressure
settled; action-unit grill still active.**

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

## Still-open action unit

The period jar and moth tiers are real, but AnkiScape must choose whether a
successful review catches one moth or resolves a complete fifteen-moth
catch-and-feed circuit. This is the active owner fork. The final choice must
state multiplier, event-boundary, `Again`, and undo behavior before the
contract closes.
