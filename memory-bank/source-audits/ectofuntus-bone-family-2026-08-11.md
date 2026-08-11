# Ectofuntus bone family audit — 2026-08-11

Status: **implemented with one registered selector placeholder and one open item-identity mapping**.
Cutoff: `2012-11-20T00:00:00Z`.

## Goal

This slice gives each selected bone an authentic acquisition route.
It also completes each matching Ectofuntus grinding and worship route.

## Bone values

Darkan uses a `4.0x` multiplier for Ectofuntus Prayer experience points (XP).
The burial and Ectofuntus values are in the following table.

| Bone | Item ID | Burial Prayer XP | Ectofuntus XP |
| --- | ---: | ---: | ---: |
| Burnt bones | `528` | `4.5` | `18` |
| Jogre bones | `3125` | `15` | `60` |
| Shaikahan bones | `3123` | `25` | `100` |
| Zogre bones | `4812` | `22.5` | `90` |
| Fayrg bones | `4830` | `84` | `336` |
| Raurg bones | `4832` | `96` | `384` |
| Ourg bones | `4834` | `140` | `560` |
| Frost dragon bones | `18830` and `18832` | `180` | `720` |

## Bonemeal identities

The following table records each live grinding identity.

| Bone item | Bonemeal item |
| --- | --- |
| Burnt bones `528` | Burnt bonemeal `4258` |
| Jogre bones `3125` | Jogre bonemeal `4271` |
| Shaikahan bones `3123` | Shaikahan bonemeal `5615` |
| Zogre bones `4812` | Zogre bonemeal `4852` |
| Fayrg bones `4830` | Fayrg bonemeal `4853` |
| Raurg bones `4832` | Raurg bonemeal `4854` |
| Ourg bones `4834` | Ourg bonemeal `4855` |
| Frost dragon bones `18832` | Frost dragon bonemeal `18834` |

## Exact sources

The primary server record is Darkan commit `a2568b880390ef697b1b17e825fdef7868bed67f`.

Darkan `Burying.java:33-64` records the bone identities and burial XP.
Darkan `Ectofuntus.kt:20-31,91-132,250-276` records the grinding and worship routes.

The following dated RuneScape Wiki revisions give independent period evidence.

| Subject | Old revision ID |
| --- | ---: |
| Burnt bones | `6351913` |
| Jogre bones | `6130165` |
| Shaikahan bones | `6132621` |
| Zogre bones | `6135269` |
| Fayrg bones | `6105617` |
| Raurg bones | `6541406` |
| Ourg bones | `6356815` |
| Frost dragon bones | `6515919` |
| Ectofuntus `4.0x` multiplier | `6544994` |

## Zogre Prayer XP correction

Canonical `main` shipped a player-visible Zogre bones defect.
`data/prayer_data.py:63` gave Zogre bones `12.5` Prayer XP at base commit `1cf43931`.
This branch corrects the value to `22.5` Prayer XP.
The corrected Ectofuntus reward is `90` Prayer XP.

The game-main value in `BoneData.kt:22` dissents at `12.5` Prayer XP.
Three independent records support `22.5` Prayer XP.

- Darkan `Burying.java:49` gives `22.5`.
- Zogre bones oldid `6135269`, lines 21 and 45, gives `22.5`.
- Zogre Flesh Eaters oldid `6441901` gives `22.5`.

This correction fixes existing gameplay.
It is not only support for new content.

## Acquisition routes

Four combat targets now give guaranteed bone drops.

| Target | Level | Guaranteed drop |
| --- | ---: | --- |
| Zogre | `44` | One Zogre bones item and one Ogre coffin key |
| Jogre | `53` | One Jogre bones item |
| The Shaikahan | `83` | One Shaikahan bones item |
| Frost dragon | `166` | One Frost dragon bones item |

Burnt bones use a ground-spawn collection action.
An Ogre coffin key opens one weighted coffin result.
The coffin can give Zogre, Fayrg, Raurg, or Ourg bones.

The Shaikahan route uses a karambwan-poisoned Steel spear.
The slice adds the exact `Steel spear (kp)` item and preparation action.

## Registered placeholder

This slice adds one registered placeholder.

| Placeholder | Live value | What settles it |
| --- | --- | --- |
| `bone_sources.ogre_coffin_selector_weights` | Zogre `63`, Fayrg `14`, Raurg `6`, Ourg `3`, and non-bone `39`. The table has `125` slots. | Ogre coffin key oldid `6381645` gives expected bone counts per 100 keys. It does not expose the server selector. A period coffin routine or a qualified cutoff sample must replace the weights. The same source must identify the `39` non-bone slots. |

No placeholder controls the bone IDs, burial XP, bonemeal IDs, or Ectofuntus multiplier.

## Open Frost dragon identity mapping

Two period item IDs have the name Frost dragon bones: `18830` and `18832`.
No recovered period source maps one ID to the Asgarnian Ice Dungeon route.
No recovered period source maps the other ID to the Daemonheim route.

The record preserves both IDs.
The live combat and Grand Exchange route uses tradeable item `18832`.
The one-to-one route association stays open.

A period drop routine with a location key can settle this mapping.
A dated source that names both route-specific item IDs can also settle it.

## Exclusions

This slice excludes four nearby cases.

- Wyvern bones are complete on sibling branch `goal/breadth-2026-08-11`.
- General Graardor drops separate Ourg bone identity `14793`.
- The coffin route uses Ourg bones item `4834`, not item `14793`.
- Burnt bones are ground spawns. Burning ordinary bones cannot create them.
- Unobtainable Frost dragon bone spawns do not supply a live route.

## Reachability result

The branch base at `1cf43931` had this result:

```text
1556 actions; 2573 reachable items; 102 orphan inputs; 101 blocked actions
```

The implemented worktree has this result:

```text
1559 actions; 2590 reachable items; 86 orphan inputs; 85 blocked actions
```

The slice adds three actions and seventeen reachable items.
It removes sixteen orphan inputs and unblocks sixteen actions.

All eight selected bones have routes.
All eight matching bonemeal items have routes.
None of these sixteen items is in `orphan_inputs`.

The audit exits with status `1` while unrelated blocked actions remain.
This command contract does not invalidate the reported figures.

## Verification

The owner ran the complete plain lane in this worktree.

```text
Ran 4069 tests in 226.099s
OK (skipped=496)
```

The runtime check confirmed all four combat targets.
Each target gives its guaranteed bone drop.
The Zogre also gives one Ogre coffin key.
