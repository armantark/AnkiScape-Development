# Ectofuntus bone family audit — 2026-08-11

Status: **integrated with two registered hidden-value placeholders, tested access gates, and one open item-identity mapping**.
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
Darkan `Ectofuntus.kt:20-31,91-132,193-247,250-276` records the grinding and worship routes.

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
| Frost dragon (Dungeoneering) | `5794845` |
| Ectofuntus `4.0x` multiplier | `6544994` |

Raurg bones oldid `6541406`, line 26, gives a Zombie impling quantity of `2-3`.
Darkan `data/npcs/drops/zombie_impling.json:84-86` at the pinned commit gives exactly `2`.
Darkan does not confirm the upper endpoint of `3`.

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

## Access gates

The generic Combat surface has no map or free-form location selector, so ordinary
location context remains flattened while real access walls stay executable.

- Zogres are the Jiggig-area route opened during `Zogre Flesh Eaters`. Zogre
  oldid `6547569` and Zogre Flesh Eaters oldid `6441901` are the pinned
  target/area and quest records; stage-one prose says the guard removes the
  barricade before the player enters the zogre-infested area. Both selector and
  combat kernel therefore require the quest to have started, not completed.
- The Shaikahan is in the eastern Karamja jungle. Tai Bwo Wannai Trio oldid
  `6529797` lists the ability to fight it as a completion unlock, and The
  Shaikahan oldid `6552714` independently preserves the location and weapon
  method. The target therefore requires completed `Tai Bwo Wannai Trio` and
  separately keeps the continuous karambwan-poisoned-spear equipment gate.
- Jogres are ordinary Karamja jungle and Pothole Dungeon creatures. Jogre oldid
  `6240856` establishes the ordinary location record without a quest wall, so
  the target records Karamja context but deliberately remains quest-ungated.

Main commit `225c9c67` already registers quest IDs `zogre_flesh_eaters` and
`tai_bwo_wannai_trio` in `generated/quest_catalog_generated.py`; the integration
reuses those exact save-state keys instead of inventing parallel access flags.
Legends' Quest is not used: it governs the separate Kharazi-jungle context, not
these eastern-Karamja creatures.

## Registered placeholders

This slice carries two genuine registered placeholders for hidden values that
period gameplay had but the recovered record does not expose.

| Placeholder | Live value | What settles it |
| --- | --- | --- |
| `bone_sources.ogre_coffin_selector_weights` | Zogre `63`, Fayrg `14`, Raurg `6`, Ourg `3`, and non-bone `39`. The table has `125` slots. | Ogre coffin key oldid `6381645` gives expected bone counts per 100 keys. It does not expose the server selector. A period coffin routine or a qualified cutoff sample must replace the weights. The same source must identify the `39` non-bone slots. |
| `bone_sources.frost_dragon_generated_levels` | Attack, Strength, Defence, Magic, and Ranged are all `213`. | The period Frost dragon existed with a real combat stat block, but Darkan marks the recovered level-166 definition `nostats` and reconstructs `213` through its checked-in `generateLevels` routine. An authentic period combat definition or server routine with the five core levels replaces it. |

Neither placeholder invents a mechanic absent from the period game. No
placeholder controls the bone IDs, burial XP, bonemeal IDs, or Ectofuntus
multiplier.

## Open Frost dragon identity mapping

The rev-727 cache gives two item definitions named Frost dragon bones.
Item `18832` is exchangeable. Item `18830` is not exchangeable.

Frost dragon bones oldid `6515919`, lines 29-30, says both Frost dragon types always drop one named item.
Frost dragon (Dungeoneering) oldid `5794845`, lines 19, 27, and 37, also names the item.
Neither old revision gives an item ID.

The live normal Frost dragon always drops exchangeable item `18832`.
`data/bone_sources_data.py:88-90,116` and `generated/grand_exchange_period_generated.py:3676` record this implementation.
Item `18830` has no live route.

No recovered period source maps either ID to the Asgarnian Ice Dungeon or Daemonheim route.
The live implementation does not settle the period item-to-route mapping.

A period drop routine with a location key can settle this mapping.
A dated source that names both route-specific item IDs can also settle it.

## Exclusions

This slice excludes four nearby cases.

- Wyvern bones are complete on sibling branch `goal/breadth-2026-08-11`.
- General Graardor drops separate Ourg bone identity `14793`.
- The coffin route uses Ourg bones item `4834`, not item `14793`.
- Burnt bones are ground spawns. Burning ordinary bones cannot create them.

## Reachability result

The original branch record below was produced by the superseded permissive
instrument and must not be used as a current baseline:

```text
1556 actions; 2573 reachable items; 102 orphan inputs; 101 blocked actions
```

Re-measurement after merging current main commit `e444dfd2`, with the corrected
quest-branch audit instrument at `tools/audit_item_reachability.py` SHA-256
`99042e4d583338c56ef72534f37581f9051c0c35fc197f5b09bdcff86a12877b`, gives:

```text
main:        1568 actions; 2248 reachable items; 100 orphan inputs; 103 blocked actions; 1099 seed items
integration: 1571 actions; 2266 reachable items;  84 orphan inputs;  87 blocked actions; 1104 seed items
```

The corrected result is therefore plus three actions, plus eighteen reachable
items, minus sixteen orphan inputs, minus sixteen blocked actions, and plus five
seed items. Comparing the named route sets shows eighteen gross additions and
zero gross removals. The additions are the eight selected bones, their eight
matching bonemeal items, `Ogre coffin key`, and `Steel spear (kp)`.

The legacy bones commit had silently removed the owner-settled `Ancient bones`
material and The Restless Ghost's five-bone reward. This integration restores
both from current main. `bury_ancient_bones` remains a live 200-XP target, while
Ancient bones deliberately have neither an Ectofuntus nor gilded-altar route.
That restoration also keeps `_migrate_ancient_gilded_target` safe: its migrated
`bury_ancient_bones` destination exists. The audit does not list Ancient bones
as a new route because current main already contains the same quest reward and
burial target.

The access-gate fix does not change those aggregate figures: Zogre and
Shaikahan drops are still legitimate combat seed routes once Zogre Flesh Eaters
has started and Tai Bwo Wannai Trio is complete, while Jogre remains an ordinary
ungated Karamja route.

The audit exits with status `1` while unrelated blocked actions remain.
This command contract does not invalidate the reported figures.

## Verification

The complete pre-gate-fix plain lane below is historical. A fresh full lane is
required after the Ancient-bones restoration and current-main merge.

```text
Ran 4128 tests in 360.389s
OK (skipped=498)
```

The runtime check confirmed all four combat targets.
Each target gives its guaranteed bone drop.
The Zogre also gives one Ogre coffin key.
