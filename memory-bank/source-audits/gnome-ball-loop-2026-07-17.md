# Gnome Ball at the pre-EOC cutoff

Date: 2026-07-17

Status: **period structure pinned; three-review match grouping owner-settled;
scoring and tackle rolls remain open.**

## Pinned evidence

The literal wikitext of `Gnome Ball`, oldid `6404371`,
`2012-10-14T14:19:59Z`, establishes:

- the members activity is dangerous rather than safe;
- the player wins after scoring five goals against the gnome team;
- a shot may score or miss;
- gnome tackles cause LP damage;
- passing to green-armoured winger gnomes is optional;
- throwing the ball awards Ranged XP, while goals award both Ranged and
  Agility XP;
- the first through fifth goals award `4/5/6/7/5` XP in each goal skill, and
  the fifth adds a `25 XP` completion bonus; and
- after winning, the referee supplies a gnomeball, but another is not awarded
  while the previous reward remains carried; banking it permits another.

Source:

- <https://runescape.wiki/w/Gnome_Ball?oldid=6404371>

The revision was resolved and inspected as literal wikitext with
`tools/wiki_parity.py`. It does not state the scoring probability, tackle
probability, tackle damage, pass effects, or throw XP values needed for a
complete implementation.

## Owner-settled AnkiScape grouping

A match is three successful-review beats:

1. the opening beat resolves goals one and two;
2. the middle beat resolves goals three and four; and
3. the final beat resolves goal five, the completion bonus, and the referee
   reward.

Each beat is one bounded match slice, not an NPC simulation. It may narrate
passes, missed shots, and tackles, but it stores only the current beat, current
score, and player LP effects. The slice completes its named scoring milestone
unless the player's ordinary dangerous-activity death handling aborts the
match. No teammate, opponent, pathing, possession, or field state is advanced
between reviews.

This grouping deliberately preserves a short opening, escalation, and distinct
fifth-goal payoff while avoiding both a five-review throwaway minigame and a
single opaque match roll. The source goal XP is awarded at the beat containing
that goal. Any sourced throw XP must be folded into that same bounded result
rather than creating invisible per-throw replay.

An `Again` before a successful beat advances ordinary world state but does not
invent a tackle or score. Leaving explicitly abandons the match; ordinary death
also ends it. Undo restores the prior beat, score, LP, XP, and reward state
together.

The referee's gnomeball remains a real inventory reward. It is withheld while
one is carried, while banking the existing ball permits another source-shaped
reward on a later win.

## Still open for source harvest

- Resolve or mark `source_blocked` the scoring chance, tackle chance, tackle
  damage, passing effects, and throw XP.
- Reconcile the dangerous-activity death exit and equipment restrictions
  against independent period-lineage evidence.
- Corroborate the goal XP ladder, fifth-goal bonus, and gnomeball reward
  behavior.
- Fetch the ball, activity, and result assets from period evidence.
