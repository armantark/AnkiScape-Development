# Slayer Vyrewatch registry conflict — 2026-07-19

Status: **recorded for the design/authority thread; runtime unchanged**.

## Conflict

The settled Slayer contract says broad assignments remain categories with
explicit stable membership. The cutoff Vyrewatch page says a Vyrewatch task
may be completed with Vyrewatch, Vyreladies, Vyrelords, or Vampyre juvinates.
The Chaeldar, Sumona, Duradel/Lapalok, and Kuradal pool audits preserve that
multi-variant boundary.

Current `slayer_data.py` instead declares:

```python
SlayerFamily(
    "vyrewatch",
    "Vyrewatch",
    ("vyrewatch",),
    ...
)
```

Readiness treats that one target as the complete family. Adding only
`COMBAT_ENEMY_DATA["vyrewatch"]` would therefore certify a broad task while
three source-attested alternative identities remain absent from the stable
family ledger.

Darkan's `TaskMonster.java:133` is not a resolution. It uses display-name
fragments for `"vyrewatch"`, `"vyrelord"`, and `"vyrelady"`, omits the
cutoff Juvinate alternative in that row, and relies on the substring matching
which the settled AnkiScape contract explicitly rejects.

## Stop boundary

No family expansion, readiness override, Combat row, asset, or test was
implemented. The independent Vyrewatch source audit is recorded at
`../source-audits/slayer-vyrewatch-combat-2026-07-19.md`.

The design/authority thread needs to identify the superseding stable variant
ledger or explicitly correct the registry audit's completeness claim. Until
then `vyrewatch:combat_target` remains blocked and no single representative may
certify the family.
