# Juju vine secondaries, 2026-08-11

## Outcome

The Common jadinko Hunter route is live. It keeps the Marasamaw plant and gives one Withered vine on success. It can also give one vine-herb seed.

The Juju hunter potion recipe is live. The four vial doses are live consumables and Bob Barter can decant them. Each consumed dose gives a three-level Hunter boost and leaves the next dose.

The Hunter boost magnitude is a registered placeholder. No qualified period source states a Juju hunter player-drink boost magnitude.

## Scope

This slice changes Hunter data, Hunter runtime logic, potion registration, tests, and assets. It does not change `ui/ui.py`.

The evidence order was Darkan, OpenRS2 revision 727, game-main, OpenRS2 revisions 741 and 742, then dated wiki revisions.

## Pinned Common jadinko values

| Value | Registered value | Exact source |
| --- | --- | --- |
| NPC identity | Common jadinko, NPC `13119` | OpenRS2 revision 742, `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache`, NPC `13119` |
| Hunter level | `70` | Common jadinko oldid `6129379`, 2012-08-22 |
| Hunter XP | `350` | Common jadinko oldid `6129379`, 2012-08-22 |
| Trap | Reusable Marasamaw plant | Common jadinko oldid `6129379`; Jadinkos oldid `5917881`, 2012-07-10 |
| Primary output | One Withered vine | Common jadinko oldid `6129379`; Darkan `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/hunter/hunter_jadinko_common.json`, item `19971`, quantity `1` |
| Secondary family | A chance to give seeds | Common jadinko oldid `6129379`; Jadinkos oldid `5917881` |
| Seed selector | One of five vine-herb seeds | Darkan `hunter_jadinko_common.json`, `dropOne=true`, items `19897`, `19902`, `19907`, `19912`, and `19917` |
| Seed chance | `16/256` | Darkan `hunter_jadinko_common.json` |
| Catch curve | `rate1=128`, `rate99=256` | Registered placeholder `hunter.herblore_habitat_success_curves` |

OpenRS2 revision 742 pins the item identities and item flags.

| Item | ID | Stackable | Exchangeable |
| --- | ---: | --- | --- |
| Marasamaw plant | `19965` | No | Yes |
| Withered vine | `19971` | Yes | No |
| Erzille seed | `19897` | Yes | No |
| Ugune seed | `19902` | Yes | No |
| Argway seed | `19907` | Yes | No |
| Shengo seed | `19912` | Yes | No |
| Samaden seed | `19917` | Yes | No |

The five seed pages also pin the Common jadinko route:

- Erzille seed oldid `5780035`, 2012-06-19.
- Ugune seed oldid `6134455`, 2012-08-24.
- Argway seed oldid `5028737`, 2011-12-07.
- Shengo seed oldid `5035618`, 2011-12-09.
- Samaden seed oldid `5913077`, 2012-07-10.

## Pinned Juju hunter potion values

| Value | Registered value | Exact source |
| --- | --- | --- |
| Recipe | Erzille potion (unf) plus Corrupt vine | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore/mixing/PotionData.kt`, `JUJU_HUNTING` |
| Herblore level | `54` | game-main `PotionData.kt`, `JUJU_HUNTING` |
| Herblore XP | `123.0` | game-main `PotionData.kt`, `JUJU_HUNTING` |
| Product | Juju hunter potion (3) | game-main `PotionData.kt`, `JUJU_HUNTING` |
| Dose 4 | Item `20023` | OpenRS2 revisions 727, 741, and 742; index 19, group 78, files 55-58 |
| Dose 3 | Item `20024` | OpenRS2 revisions 727, 741, and 742; index 19, group 78, files 55-58 |
| Dose 2 | Item `20025` | OpenRS2 revisions 727, 741, and 742; index 19, group 78, files 55-58 |
| Dose 1 | Item `20026` | OpenRS2 revisions 727, 741, and 742; index 19, group 78, files 55-58 |
| Container action | `Drink`, `Empty`, and `Drop` options | OpenRS2 revision 742 item definitions for `20023` through `20026` |
| Dose chain | Each dose leaves the next lower dose; dose 1 leaves a Vial | Shared potion registry contract and the four pinned dose identities |
| Hunter boost | Three current Hunter levels | Registered placeholder `potions.juju_hunter_boost`; Hunter potion oldid `6462616`, 2012-10-24, supplies the exact three-level fallback |

The OpenRS2 cache archives are:

- Revision 727, 2012-07-24, SHA-256 `ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8`.
- Revision 741, 2012-11-04, SHA-256 `61855e4c9f18e5ae25124277506c5b4d24317caf96f8e0a5cd1b06a037db7180`.
- Revision 742, 2012-11-07, SHA-256 `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`.

## Source conflict and owner ruling

Darkan `Potions.kt` refuses a player drink. Juju hunter potion oldid `6258636`, 2012-09-17, also says the player does not drink it.

The owner ruled that AnkiScape must make this potion drinkable with a Hunter boost. The period dose records have a `Drink` option, but they do not state the boost amount.

The slice therefore uses a registered three-level placeholder. This value matches the exact period Hunter potion boost.

## Registered placeholders

| ID | Live value | Why it remains unrecovered | What settles it |
| --- | --- | --- | --- |
| `hunter.herblore_habitat_success_curves` | `rate1=128`, `rate99=256` | The dated pages state the routes and rewards but no catch probability. | A period Marasamaw or tracker catch routine, or a qualified measured table. |
| `hunter.common_jadinko_seed_roll` | A `16/256` trigger and a uniform choice of five vine-herb seeds | Darkan reconstructs the hidden trigger and selector. The dated pages only state a chance. | A period Common jadinko drop routine or a qualified capture sample. |
| `potions.juju_hunter_boost` | Three Hunter levels | No qualified source states a Juju hunter player-drink boost magnitude. | A period player-drink routine or a dated source that states the exact magnitude. |

## Assets

The four Juju hunter vial assets are normalized and registered.

| Asset | Source timestamp | SHA-1 |
| --- | --- | --- |
| `herbloreitems/juju_hunter_potion_1.png` | `2011-11-23T05:34:56Z` | `c52275308aab8dcde076d78c2874a7793f2a08e9` |
| `herbloreitems/juju_hunter_potion_2.png` | `2011-11-23T05:35:07Z` | `2a4a87899f413261c37e448a26017d3e8dc692b2` |
| `herbloreitems/juju_hunter_potion_3.png` | `2011-11-23T05:34:46Z` | `fcb04ab0069fa02777e9a6ffb5189736762d19d3` |
| `herbloreitems/juju_hunter_potion_4.png` | `2011-11-23T05:35:17Z` | `170d078a532f7ad1c6dc557ac32fc72aac77cc50` |

The slice also registers normalized assets for the Marasamaw plant, Withered vine, and the five seed identities. `assets_provenance.json` records each file URL, image URL, hash, size, and timestamp.

## Runtime contract

One successful Common jadinko action keeps the Marasamaw plant. It gives 350 Hunter XP and one Withered vine.

The action makes one independent seed roll. A successful seed roll gives one seed from the five-item selector.

Runtime telemetry records the guaranteed output and the selected bonus seed. Review undo uses the same output record.

Juju hunter potion remains a Habitat reagent. It is also a drinkable potion. These roles are not exclusive.

## Reachability

The merge base is `0071218b`.

| Metric | Before | After | Change |
| --- | ---: | ---: | ---: |
| Actions | 1,556 | 1,561 | +5 |
| Reachable items | 2,573 | 2,574 | +1 |
| Orphan inputs | 102 | 105 | +3 |
| Blocked actions | 101 | 105 | +4 |

The slice adds the live Hunter action and the four potion consume actions. The graph still lacks some Habitat roots, such as the Marasamaw plant and Corrupt vine routes.

## Verification

Focused potion, placeholder, registry, runtime, and Bob Barter checks pass.

Full plain discovery passes:

```text
Ran 4057 tests in 211.908s
OK (skipped=494)
```

The final reachability audit reports:

```text
1561 actions; 2574 reachable items; 105 orphan inputs; 105 blocked actions
```

## Queue

`ui/ui.py` lines 1467-1470 apply skill availability as a one-way enable. A button stays enabled after the pure result becomes false.

The same pattern exists on nearby skill buttons. A separate slice must fix every skill button.

The Juju hunter boost placeholder is recoverable data-depth debt. A period player-drink routine or an exact dated statement settles it.
