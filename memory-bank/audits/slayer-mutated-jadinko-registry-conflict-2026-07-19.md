# Slayer Mutated-jadinko registry conflict — 2026-07-19

Status: **implementation stopped; owner-visible contract/code conflict**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Conflict

The newest settled Slayer pool records agree that Mutated jadinkos are a
three-variant assignment family:

- `source-audits/slayer-sumona-pool-2026-07-17.md` names baby, guard, and male
  identities with Slayer gates 80, 86, and 91;
- `source-audits/slayer-duradel-lapalok-pool-2026-07-17.md` preserves the same
  three identities and gates; and
- `source-audits/slayer-kuradal-pool-2026-07-17.md` preserves them again.

Current `slayer_data.py` instead declares:

```python
SlayerFamily(
    "mutated_jadinkos",
    "Mutated jadinkos",
    ("mutated_jadinko_baby",),
    required_slayer_level=80,
    source=SUMONA_AUDIT_SOURCE,
)
```

Readiness treats that single target as the complete family. Adding only
`COMBAT_ENEMY_DATA["mutated_jadinko_baby"]` would therefore certify the
settled three-variant assignment while guard and male remain absent, and the
family-level Slayer-80 gate cannot represent the settled 86/91 variant gates.

This is a direct authority/code conflict, not an invitation to infer a
registry correction.

## Period corroboration

RuneScape Wiki `Mutated jadinko`, oldid
[`5578778`](https://runescape.wiki/w/Mutated_jadinko?oldid=5578778),
timestamp `2012-05-07T16:04:54Z`, explicitly enumerates:

- Mutated jadinko baby, combat 90, Slayer 80;
- Mutated jadinko guard, combat 145, Slayer 86; and
- Mutated jadinko male, combat 201, Slayer 91.

Both the rev-727 and rev-742 caches independently contain all three Attackable
NPC identities as IDs 13820, 13821, and 13822.

Darkan's `TaskMonster.java` uses the display-name substring
`"mutated jadinko"`. That is useful family evidence but cannot resolve the
AnkiScape conflict because the settled contract requires explicit stable
membership rather than substring matching.

## Stop boundary

No family expansion, per-variant gate model, Combat row, asset, readiness
override, or test was implemented. The independent source boundary is recorded
at `../source-audits/slayer-mutated-jadinko-combat-2026-07-19.md`.

The authority thread must provide a superseding registry record that reconciles
the three settled variants with the executable family/gate schema, or explicitly
supersede the three pool records. Until then:

- `mutated_jadinkos:combat_target` remains blocked;
- Sumona remains hidden at 20/37; and
- one baby target must not certify the family.
