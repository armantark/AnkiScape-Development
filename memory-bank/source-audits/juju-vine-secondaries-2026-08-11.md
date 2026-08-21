# Juju vine secondaries, 2026-08-11

## Outcome

The Common jadinko Hunter route is live. It keeps the Marasamaw plant and gives one Withered vine on success. It can also give one vine-herb seed.

The Juju hunter potion recipe is live. The four vial doses are drinkable and can be decanted by Bob Barter. Drinking consumes one dose, leaves the next-lower dose, applies no stat boost, and surfaces the sourced flavour message. The period game also defines the potion as an ingredient used on a Herblore Habitat flower patch, but this add-on ships no action that consumes a dose there or applies the attraction effect.

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

This Common jadinko transcription is not a complete disposition of Darkan's three seed subtables. The exhaustive ten-row sweep on `goal/herbs-reland-2026-08-19` owns the authoritative multi-table disclosure, including `hh_bush_seed` at `14/256` and `hh_blossom_seed` at `17/256`; this audit does not claim that the current Common row is complete.

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

| Value | Add-on or period-game value | Exact source |
| --- | --- | --- |
| Recipe | Erzille potion (unf) plus Corrupt vine | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore/mixing/PotionData.kt`, `JUJU_HUNTING` |
| Herblore level | `54` | game-main `PotionData.kt`, `JUJU_HUNTING` |
| Herblore XP | `123.0` | game-main `PotionData.kt`, `JUJU_HUNTING` |
| Product | Juju hunter potion (3) | game-main `PotionData.kt`, `JUJU_HUNTING` |
| Dose 4 | Item `20023` | OpenRS2 revisions 727, 741, and 742; index 19, group 78, files 55-58 |
| Dose 3 | Item `20024` | OpenRS2 revisions 727, 741, and 742; index 19, group 78, files 55-58 |
| Dose 2 | Item `20025` | OpenRS2 revisions 727, 741, and 742; index 19, group 78, files 55-58 |
| Dose 1 | Item `20026` | OpenRS2 revisions 727, 741, and 742; index 19, group 78, files 55-58 |
| Cache options | `Drink`, `Empty`, and `Drop` | OpenRS2 revision 742 item definitions for `20023` through `20026`; these client options establish the action but not its server-side effect |
| Player drink | Consumes one dose, leaves the next-lower dose (dose 1 leaves a Vial), applies no stat effect, and emits the flavour message | Darkan `Potions.kt:522,881-904`, supplying commit `afa87b9754de3bd9cf2fd5024ea903b00d99a798`; Juju hunter potion oldid `6258636`, 2012-09-17T16:04:30Z |
| Period-game Habitat ingredient use (not implemented) | The source game consumes one dose on the Herblore Habitat flower patch and applies the ten-minute attraction effect; this add-on has no corresponding action or effect | Darkan `FarmPatch.java:338-361`, supplying commit `4e46c05dbd88c44d2a25d48ce96a493d884c978b`; Juju hunter potion oldid `6258636`, 2012-09-17T16:04:30Z |

The OpenRS2 cache archives are:

- Revision 727, 2012-07-24, SHA-256 `ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8`.
- Revision 741, 2012-11-04, SHA-256 `61855e4c9f18e5ae25124277506c5b4d24317caf96f8e0a5cd1b06a037db7180`.
- Revision 742, 2012-11-07, SHA-256 `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`.

## Player-use behavior

Darkan `Potions.kt:522` registers `JUJU_HUNTER_POTION` as an ordinary potion enum row with no `canDrink` override. The inherited `canDrink` at lines 881-883 returns `true`; the shared drink path at lines 885-904 replaces the item with the next-lower dose, invokes the row effect, and sends the ordinary drink message. This row's effect only sends, "You decide that only plants are likely to enjoy the taste of this potion." It changes no stat. These lines come from supplying commit `afa87b9754de3bd9cf2fd5024ea903b00d99a798`.

The dated Juju hunter potion page, oldid `6258636` at 2012-09-17T16:04:30Z, says a drink attempt receives that flavour message and separately documents using the potion on a vine blossom. It does not say the attempted drink preserves the dose. Darkan therefore supplies the hidden server-side dose transition, while the rev-742 `Drink` option and dated message corroborate the action.

The period game's Habitat ingredient handling is separate from drinking. Darkan `FarmPatch.java:338-361`, supplying commit `4e46c05dbd88c44d2a25d48ce96a493d884c978b`, consumes a vial or flask dose on the Herblore Habitat flower patch and applies the ten-minute Juju hunter effect. This is source evidence only: this add-on ships no matching action, dose consumption, or attraction effect. `Potions.kt` does not own that source-game path.

## Registered placeholders

| ID | Live value | Why it remains unrecovered | What settles it |
| --- | --- | --- | --- |
| `hunter.herblore_habitat_success_curves` | `rate1=128`, `rate99=256` | The dated pages state the routes and rewards but no catch probability. | A period Marasamaw or tracker catch routine, or a qualified measured table. |
| `hunter.common_jadinko_seed_roll` | A `16/256` trigger and a uniform choice of five vine-herb seeds | Darkan reconstructs the hidden trigger and selector. The dated pages only state a chance. | A period Common jadinko drop routine or a qualified capture sample. |

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

Juju hunter potion is a manual consumable. The period game defines it as a Herblore Habitat flower-patch ingredient, but this add-on ships no mechanic that consumes it there or applies attraction. No earlier potion-family row represented a consumed dose whose only effect is a message, so the smallest extension uses the existing generic potion dose chain with empty `skills`, a `flavour_only` strategy label, and a family message override. It adds no new runtime branch.

## Reachability

Restoring the four dose-consume actions moves the current refusal baseline from `1,582 / 2,307 / 72 / 45 / 27 / 71 / 1,123` to `1,586 / 2,307 / 75 / 45 / 30 / 75 / 1,123` for actions / reachable items / orphan inputs / root orphans / cascade orphans / blocked actions / seed items. The graph still lacks the vine-herb farming chain needed to produce Erzille potion (unf).

## Verification

Focused potion, placeholder, registry, runtime, and Bob Barter checks pass.

The corrected merged tree passes the full plain lane:

```text
Ran 4181 tests in 243.061s
OK (skipped=502)
```

The offscreen Qt lane was deliberately skipped under the documentation-only lane exception because concurrent offscreen Qt runs have hung this repository. No Qt result is claimed for this tree.

The final reachability audit reports:

```text
1586 actions; 2307 reachable items; 75 orphan inputs; 75 blocked actions
```
