# Slayer Troll registry conflict — 2026-07-19

Status: **implementation stopped; owner-visible contract/code conflict**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Conflict

The settled Slayer architecture does not permit one generic representative to
certify a broad assignment category:

- `slayer-skill-contract-2026-07-15.md`, owner decision 1, says broad
  assignments such as Trolls remain categories and every qualifying Combat
  enemy carries explicit stable family membership;
- `source-audits/slayer-chaeldar-pool-2026-07-17.md` describes the Troll family
  obligation as explicit ordinary mountain, ice, river, and undead variants;
  and
- `source-audits/slayer-chaeldar-registry-2026-07-18.md` says the complete
  source-reconciled 34-family registry is executable and that future Combat
  rows have declared stable identities.

Current code does not satisfy those records. `slayer_data.py` declares:

```python
SlayerFamily(
    "trolls",
    "Trolls",
    ("troll",),
    source=CHAELDAR_AUDIT_SOURCE,
)
```

Readiness treats that one target ID as the complete family. Adding a single
`COMBAT_ENEMY_DATA["troll"]` row would therefore remove the blocker and certify
Trolls even though the other source-attested qualifying variants have no
stable membership or Combat target.

This is not a missing source value within an otherwise settled row. It is a
direct mismatch between the owner-settled broad-category contract, the pool
audit's explicit variant boundary, the registry audit's completeness claim,
and the executable registry/readiness model.

## Emulator lead and limit

Darkan
`src/main/java/com/rs/game/content/skills/slayer/TaskMonster.java:41`, current
lineage through commit `6efa6c817ccf576b5bde1664ce9a3737065ff7bd`, declares
Trolls through the display-name fragments `"troll"`, `"kraka"`, `"stick"`,
`"pee hat"`, and `"dad"`.

That row cannot resolve the conflict:

- substring matching is explicitly rejected by the settled AnkiScape
  contract;
- the named trolls mix ordinary, quest, and special-context identities; and
- it does not provide the stable mountain/ice/river/undead membership ledger
  required by the period pool audit.

## Stop boundary

No Troll Combat row, family expansion, readiness override, source audit, asset,
or test was implemented. The source queue stopped before choosing a
representative or silently expanding the registry.

The owner must identify which existing record is wrong or explicitly authorize
the contract-faithful correction path. Until then:

- `trolls:combat_target` remains blocked;
- Chaeldar remains hidden at 25/34; and
- Vyrewatch and Warped-tortoise work is left untouched so this conflict is not
  buried underneath later batches.
