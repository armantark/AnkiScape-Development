# Slayer Spiritual-family registry conflict — 2026-07-19

Status: **authority conflict; implementation stopped**.  
Scope: Spiritual mages and Spiritual warriors in the hidden Sumona registry.

## Conflict

The newest settled master-pool records require four god variants for each
family:

- `source-audits/slayer-sumona-pool-2026-07-17.md`: Spiritual mages require
  Armadyl, Bandos, Saradomin, and Zamorak variants plus target-local
  alignment/aggression context. Spiritual warriors require the same four
  variants, with the additional Armadylian ranged/non-melee distinction.
- `source-audits/slayer-duradel-lapalok-pool-2026-07-17.md`: Spiritual mages
  again require all four variants and target-local context.
- `source-audits/slayer-kuradal-pool-2026-07-17.md`: Spiritual mages again
  require all four variants and target-local alignment/aggression context.

The executable registry does not encode those variant sets:

```python
SlayerFamily(
    "spiritual_mages",
    "Spiritual mages",
    ("spiritual_mage_saradomin",),
    required_slayer_level=83,
    readiness_features=("god_wars_context",),
    source=SUMONA_AUDIT_SOURCE,
),
SlayerFamily(
    "spiritual_warriors",
    "Spiritual warriors",
    ("spiritual_warrior_saradomin",),
    required_slayer_level=68,
    readiness_features=("god_wars_context",),
    source=SUMONA_AUDIT_SOURCE,
),
```

Source: `slayer_data.py:724-741`.

One Saradomin target could therefore certify each family even though the
owner-settled Armadyl, Bandos, and Zamorak identities and their target-local
alignment behavior are absent.

## Independent identity check

The dated rev-727 cache contains four attackable identities for each generic
name:

- Spiritual mages: NPCs 6221, 6231, 6257, and 6278;
- Spiritual warriors: NPCs 6219, 6229, 6255, and 6277.

The newer rev-742 exact-name query exposes only 6231/6278 for mages and
6229/6277 for warriors, so cache identity evolution also needs a source pass;
it is not permission to erase variants already required by the settled
contracts.

Darkan contains multiple combat definitions:

- Spiritual mage levels 120, 121, and 122;
- Spiritual warrior levels 115, 123, 125, and 134.

Its generic drop files do not settle how those definitions map to all four
owner-required variants or how target-local God Wars alignment is represented.

## Required authority correction

A newer Memory Bank authority record must explicitly do one of the following:

1. enumerate stable target IDs for all four required variants in both families;
   or
2. supersede the four-variant clauses and explicitly authorize a
   one-representative certification rule for these two families.

The current closed-design rule forbids the implementation thread from choosing
between those outcomes. No registry, Combat target, God Wars context, asset, or
test was changed.

Sumona remains hidden and unrenormalized at **20/37**. Both families retain
their `combat_target` blockers. This is an authority conflict, not a new
creative-design question.
