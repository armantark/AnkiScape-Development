# Summoning familiar-effects source audit (2026-07-17)

Scope: implement only ordinary familiar effects whose pre-EOC behavior maps
cleanly onto existing AnkiScape substrates. Cutoff: 2012-11-20.

## Pinned period sources

- **Summoning familiars**, oldid
  [6579789](https://runescape.wiki/w/Summoning_familiars?oldid=6579789),
  2012-11-19 04:08:58 UTC.
- **Void shifter**, oldid
  [5919199](https://runescape.wiki/w/Void_shifter?oldid=5919199),
  2012-07-11 05:39:06 UTC.
- **Arctic bear**, oldid
  [6333537](https://runescape.wiki/w/Arctic_bear?oldid=6333537),
  2012-10-02 13:09:02 UTC.

The complete familiar table closes five invisible skill boosts: Lava titan
adds 10 to Mining and Firemaking, Arctic bear adds 7 to Hunter, Granite lobster
adds 4 to Fishing, and Beaver adds 2 to Woodcutting. These boosts affect
success calculations, not the player's visible level or level-gated unlocks.

The same period family evidence closes Bunyip's passive heal at 20 life points
every 15 seconds. It does not decide how densely that real-time benefit should
resolve against AnkiScape's per-exchange Combat damage. The initial one-heal-per-
card closure was calibrated against the shipped 50-tick Combat review and became
too dense when the live cadence contract moved ordinary Combat to six ticks.
The owner resettled the abstraction as an exact residual: each answered card,
including Again, adds six effect ticks; reaching 25 heals 20 LP, subtracts 25,
and retains the remainder. Familiar lifetime decay remains separately
card-calibrated.

Void shifter's period escape occurs when nonlethal damage leaves the player
below 10% life points. AnkiScape reuses the existing Combat interruption
boundary: the encounter ends visibly, while genuinely lethal damage still
continues through ordinary death and grave handling. No cooldown is invented.

## Implemented boundary

- Mining, Firemaking, Hunter, Fishing, and Woodcutting accept a separate
  familiar-adjusted roll level while retaining the base level for eligibility.
- Bunyip healing remains part of the global answered-card Summoning world tick,
  including Again, but is due only when its six-per-card residual reaches the
  sourced 25-tick threshold. It grants 20 LP up to the ordinary maximum and
  never reads wall-clock time. The code still needs this cadence integration;
  the currently shipped implementation heals on every card.
- Void shifter is evaluated after a nonlethal incoming Combat hit and before
  the next exchange.
- Pack yak Winter Storage remains governed by its separate source/owner audit.

## Explicitly parked

The remaining combat attacks, special-scroll effects, foraging tables and
cadences, and most familiar teleports remain `source_blocked` or
dependency-blocked. They do not receive plausible substitutes. Spirit graahk's
already-sourced route profile remains the one ordinary teleport exception;
Daemonheim familiars remain wholly owned by the future Dungeoneering session
economy.
