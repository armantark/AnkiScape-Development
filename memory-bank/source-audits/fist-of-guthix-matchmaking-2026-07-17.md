# Fist of Guthix matchmaking at the pre-EOC cutoff

Date: 2026-07-17

Status: **opponent selection and round-role order settled; simulated population
distribution remains an AnkiScape abstraction.**

## Pinned evidence

The literal wikitext of `Fist of Guthix`, oldid `6472973`,
`2012-10-25T21:14:22Z`, states:

- players enter a waiting room and wait for the game to match them with an
  opponent;
- the game is one-versus-one and has two rounds;
- the first-round hunter and hunted roles are assigned randomly;
- the roles swap for the second round and stats are restored; and
- players are paired randomly regardless of Combat level, including extreme
  mismatches.

Source:
<https://runescape.wiki/w/Fist_of_Guthix?oldid=6472973>, inspected as literal
wikitext with `python3 tools/wiki_parity.py content "Fist of Guthix"`.

## AnkiScape consequence

Opponent selection is not an owner design fork. Starting a match automatically
draws one simulated opponent from a period-shaped population and preserves that
opponent across both role-swapped rounds. Casual and Advanced modes cannot
choose opponent strength. The exact population distribution is not proven by
this page and must be source-audited or recorded as a labeled bounded
abstraction before implementation.

## Owner-settled review-native tactic

The source gives the hunted player a real risk/reward choice: standing nearer
the centre gains charges faster but increases exposure, while teleport houses
and portals improve evasion at the cost of charging time and, for portals,
charges. AnkiScape preserves that agency as one stance selected before the
hunted round:

- **Centre:** maximize charge gain and accept maximum exposure.
- **Hybrid:** balance charging and evasion.
- **Evasive:** favor houses and portals, accepting reduced charge gain.

Casual selects the stance from the generated matchup. Advanced selects it
explicitly. Reviews resolve tactical exchange slices within the stance; they do
not expose movement-by-movement controls.

## Cadence reconciliation — 2026-07-18

“Complete tactical exchanges” is presentation, not a separate combat action
unit. The cutoff source grants damage-based Combat XP, including half normal
Magic XP while using the supplied runes, so every active round advances through
the live Combat reducer:

- one successful review advances `6 × M` immediate ticks;
- opponent LP, attack phases, charges, stance, temporary supplies, and round
  state persist;
- the hunted stance changes charge gain and exposure inside those ticks;
- a kill, hunted-round endpoint, role swap, match completion, or forfeit ends
  the review without spending unused ticks in the next phase; and
- temporary runes and match state remain activity-owned, while Combat XP uses
  the ordinary tick-level award path with the sourced FoG modifier.

No opponent pathing or crowd simulation is added. This correction preserves the
settled stance decision while preventing the activity exemption from bypassing
Combat cadence.
