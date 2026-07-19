# Slayer Mutated-jadinko Combat source audit — 2026-07-19

## Decision

Do not implement Mutated jadinkos yet. The settled pool records and period
evidence require baby, guard, and male variants, while the executable registry
contains only the baby. That authority conflict is recorded separately in
`../audits/slayer-mutated-jadinko-registry-conflict-2026-07-19.md`.

The family is independently source-blocked even if its registry is later
reconciled: Darkan explicitly marks every combat definition `nostats`, no
available period-lineage implementation supplies the five executable combat
levels, and the guaranteed-drop quantities conflict with the cutoff pages.
Those are content values, not hidden rolls, so they cannot be estimated.

## Period authority

RuneScape Wiki `Mutated jadinko`, oldid
[`5578778`](https://runescape.wiki/w/Mutated_jadinko?oldid=5578778),
timestamp `2012-05-07T16:04:54Z`, closes the family identity:

| Variant | Combat | Slayer | Styles | Whip vine |
|---|---:|---:|---|---|
| Baby | 90 | 80 | Melee, Magic | No |
| Guard | 145 | 86 | Melee, Magic | Yes |
| Male | 201 | 91 | Melee, Magic | Yes |

The nearest useful individual pre-cutoff revisions close the visible combat
envelopes:

- `Mutated jadinko baby`, oldid
  [`6530640`](https://runescape.wiki/w/Mutated_jadinko_baby?oldid=6530640),
  timestamp `2012-11-04T07:42:28Z`: 1,270 LP, 127 Slayer XP, Slayer 80,
  six-tick Melee/Magic attacks, 170 maximum, non-aggressive, and guaranteed
  Mutated vine plus Excrescence in quantities 1–2 each;
- `Mutated jadinko guard`, oldid
  [`6573186`](https://runescape.wiki/w/Mutated_jadinko_guard?oldid=6573186),
  timestamp `2012-11-18T08:03:40Z`: 2,030 LP, 213 Slayer XP, Slayer 86,
  six-tick Melee/Magic attacks, 279 maximum, non-aggressive, and guaranteed
  Excrescence 2–5 plus Mutated vine 2–6; and
- `Mutated jadinko male`, oldid
  [`6530643`](https://runescape.wiki/w/Mutated_jadinko_male?oldid=6530643),
  timestamp `2012-11-04T07:46:39Z`: 2,800 LP, 308 Slayer XP, Slayer 91,
  six-tick Melee/Magic attacks, 385 melee maximum, non-aggressive, and
  guaranteed Excrescence 4–6 plus Mutated vine 6–10.

The guard page also states that protection prayer prompts the alternate attack
style and that blocked reach can bid nearby vines to attack. Those mechanics
are period-attested but are not activated while the required combat rows are
blocked.

## Cache and implementation evidence

The rev-727 and rev-742 caches agree on:

| ID | Name | Option |
|---:|---|---|
| 13820 | Mutated jadinko baby | Attack |
| 13821 | Mutated jadinko guard | Attack |
| 13822 | Mutated jadinko male | Attack |

The caches prove identities and interactions, not server combat levels.

Darkan current lineage at commit
`a601324ee04849372d4dc5822a0e531ac0ac6f26` contains:

- `data/npcs/combatdefs/uncategorized/mutated_jadinko_baby (nostats).json`;
- `data/npcs/combatdefs/uncategorized/mutated_jadinko_guard (nostats).json`;
- `data/npcs/combatdefs/uncategorized/mutated_jadinko_male (nostats).json`.

The definitions were introduced at commit
`6a5048b96aeeb7f594ba700d9fcc3df4a43adfd5`. They corroborate the three LP
values, maxima, melee lead, passive aggression, and 59-tick respawn, but all
three filenames explicitly disclose the missing-stat boundary and none has a
`combatLevels` object.

Darkan also supplies variant-specific ordinary-drop files and charm leads:

- baby `6-14-2-1`;
- guard `5-3-2-8`; and
- male `8-4-4-14`.

The ordinary files cannot be activated wholesale. Each encodes one to three
Mutated vines and one to three Excrescences as guaranteed rows, conflicting
with the cutoff quantities above for all three variants. The independent
game-main tree contains no Mutated-jadinko combat definition.

## Source-blocked fields

For every variant:

- Attack level;
- Strength level;
- Defence level;
- Magic level; and
- Ranged level.

The ordinary selector also requires a source-faithful reconciliation rather
than importing Darkan's conflicting guaranteed quantities. Combat level is not
a license to reverse-engineer the five missing levels.

## Readiness and next evidence

Sumona remains hidden at 20/37. Implementation requires both:

1. a superseding authority note reconciling the settled three-variant family
   with the executable registry and per-variant Slayer gates; and
2. period-lineage combat levels plus a reconciled drop selector for each
   activated variant.

No creative owner-design gap was opened; this is an authority conflict and a
source dependency.
