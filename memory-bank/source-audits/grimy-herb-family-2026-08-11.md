# Grimy herb family source audit — 2026-08-11

Status: **closed with no registered placeholders.**

## Scope

This slice closes the acquisition and processing chain for five vine herbs.
The herbs are Erzille, Argway, Ugune, Shengo, and Samaden.
Common jadinkos supply all five seeds from Hunter level 70; Carrion jadinkos
also supply all five, while Draconic, Saradomin, and Zamorak jadinkos supply
the four seeds above Erzille at their exact Darkan chances.
Each seed produces its matching grimy herb.
Herblore cleaning and unfinished-potion rows use the corrected levels.

All evidence is from before `2012-11-20T00:00:00Z`.

## Source pins

| Source | Exact pin | Values that this source supplies |
| --- | --- | --- |
| RuneScape Wiki | `Herblore Habitat` oldid `6513740`, `2012-10-31T21:20:32Z` | Farming levels, planting XP, harvest XP, protection payments, clean levels, clean XP, and the five herb families. |
| RuneScape Wiki | `Seeds` oldid `6565109`, `2012-11-17T05:58:56Z` | Seed quantity, crop identities, and the 80-minute Ugune total. |
| RuneScape Wiki | `Jadinkos` oldid `5917881`, `2012-07-10T13:09:23Z` | Jadinko levels, Hunter XP, primary vine drops, and the vine-herb seed family. |
| Darkan | Commit `7e7d67b481f1b94599de38a98c470419ab7c96b3`, `src/main/java/com/rs/game/content/skills/farming/ProduceType.java:103-107` | Seed IDs, grimy-herb IDs, four stages, Farming levels, XP, and save endpoints `67/80`. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/farming/PatchType.java:267-275,370-379` | The vine-herb patch uses four growth ticks per stage. The Farming dossier resolves this as 20 minutes per stage. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:377-393` | `setInitialLives()` gives `VINE_HERB` exactly `3 + compostLevel` starting lives. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:458-473` | The uncomposted disease check uses `Utils.random(128) < 6`. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/hunter/BoxHunterType.java:79-97` | Jadinko NPC IDs, levels, XP, Marasamaw tool use, and success endpoints. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/hunter/BoxTrapType.java:30` | Marasamaw plant item ID `19965`. |
| Darkan | Same commit, `data/npcs/drops/hunter/hunter_jadinko_{common,carrion,draconic,saradomin,zamorak}.json` | Guaranteed vine outputs and the five source-specific vine-herb seed tables at `16/256`, `30/256`, `14/256`, `5/256`, and `5/256`. |
| RuneScape Wiki files | Cutoff revisions recorded in `assets_provenance.json` | Exact inventory sprites for Common, Aquatic, Draconic, Marble, Oily, Pungent, Saradomin, and Zamorak vines. |
| game-main | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore/HerbData.kt:149-187` | Grimy, clean, and unfinished item identities plus clean XP. |
| game-main | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore/mixing/CreateUnfinishedPotionAction.kt:14-62` | One clean herb and one Vial of water produce one unfinished potion. This action gives no XP. |
| game-main | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:17538-17556` | Exact grimy, clean, and unfinished item IDs. |

## Jadinko seed acquisition

Common jadinko is the earliest direct seed source for this family at Hunter 70.
The row uses a reusable Marasamaw plant, always gives one Common vine, and rolls
one of the five seeds with equal weight at `16/256`. Carrion supplies the same
five seeds at `30/256`. Draconic supplies Ugune, Argway, Shengo, or Samaden at
`14/256`; Saradomin and Zamorak each supply the same four at `5/256`.

The slice registers eight period Jadinko rows. Their source tables also provide
the exact primary vine outputs, and all eight outputs have cutoff-era inventory
sprites through the established Hunter asset path.

| Jadinko | Level | XP | NPC ID | Vine item and ID | `rate1/rate99` | Vine-herb seed roll | Exact Darkan source |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| Common | 70 | 350 | 13119 | Common vine `19971` | `30/150` | All five, `16/256` | `BoxHunterType.java:93`; `hunter_jadinko_common.json`. |
| Igneous | 74 | 465 | 13143 | Marble vine `19980` | `25/145` | None | `BoxHunterType.java:87`; `hunter_jadinko_igneous.json`. |
| Aquatic | 76 | 475 | 13142 | Aquatic vine `19976` | `15/135` | None | `BoxHunterType.java:85`; `hunter_jadinko_aquatic.json`. |
| Amphibious | 77 | 485 | 13130 | Oily vine `19972` | `15/130` | None | `BoxHunterType.java:81`; `hunter_jadinko_amphibious.json`. |
| Carrion | 78 | 505 | 13154 | Pungent vine `19974` | `15/130` | All five, `30/256` | `BoxHunterType.java:89`; `hunter_jadinko_carrion.json`. |
| Draconic | 80 | 525 | 13131 | Draconic vine `19973` | `15/130` | Ugune through Samaden, `14/256` | `BoxHunterType.java:83`; `hunter_jadinko_draconic.json`. |
| Saradomin | 81 | 600 | 13163 | Saradomin vine `19981` | `15/130` | Ugune through Samaden, `5/256` | `BoxHunterType.java:95`; `hunter_jadinko_saradomin.json`. |
| Zamorak | 81 | 600 | 13165 | Zamorak vine `19983` | `15/130` | Ugune through Samaden, `5/256` | `BoxHunterType.java:97`; `hunter_jadinko_zamorak.json`. |

`Jadinkos` oldid `5917881` supplies the player-visible level, XP, and vine-drop
evidence. Each Darkan seed table uses `dropOne: true`; seed IDs are Erzille
`19897`, Ugune `19902`, Argway `19907`, Shengo `19912`, and Samaden `19917`.

## Vine-herb Farming rows

All five crops use one seed and four stages.
Each stage takes 20 minutes, for an 80-minute total.
Each crop uses save endpoints `67/80`.
The uncomposted disease selector uses `6/128` before the compost adjustment.
Darkan fixes the starting lives at `3 + compostLevel`, matching the existing `crop.base_lives + tier.extra_lives` model.

| Crop | Seed ID | Grimy herb ID | Farming level | Plant XP | Harvest XP | Protection payment | Exact source |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Erzille | 19897 | 19984 | 58 | 87.0 | 87.0 | 3 Green blossoms | `Herblore Habitat` oldid `6513740`; Darkan `ProduceType.java:103`. |
| Argway | 19907 | 19985 | 65 | 110.0 | 125.0 | 4 Red blossoms | `Herblore Habitat` oldid `6513740`; Darkan `ProduceType.java:104`. |
| Ugune | 19902 | 19986 | 70 | 135.0 | 152.0 | 3 Blue blossoms | `Herblore Habitat` oldid `6513740`; Darkan `ProduceType.java:105`. |
| Shengo | 19912 | 19987 | 76 | 140.5 | 160.0 | 5 Lergberries | `Herblore Habitat` oldid `6513740`; Darkan `ProduceType.java:106`. |
| Samaden | 19917 | 19988 | 80 | 170.0 | 190.0 | 5 Kalferberries | `Herblore Habitat` oldid `6513740`; Darkan `ProduceType.java:107`. |

## Herblore rows

Cleaning consumes one grimy herb and gives one clean herb.
The cleaning action gives the XP in this table.
The unfinished action consumes one clean herb and one Vial of water.
It gives one unfinished potion and zero XP.

| Herb | Grimy ID | Clean ID | Unfinished ID | Clean level | Clean XP | Exact source |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Erzille | 19984 | 19989 | 19998 | 54 | 10.0 | `HerbData.kt:149-155`; `Herblore Habitat` oldid `6513740`. |
| Argway | 19985 | 19990 | 20000 | 57 | 11.6 | `HerbData.kt:157-163`; corrected by `Herblore Habitat` oldid `6513740`. |
| Ugune | 19986 | 19991 | 19999 | 56 | 11.5 | `HerbData.kt:165-171`; corrected by `Herblore Habitat` oldid `6513740`. |
| Shengo | 19987 | 19992 | 20001 | 58 | 11.7 | `HerbData.kt:173-179`; corrected by `Herblore Habitat` oldid `6513740`. |
| Samaden | 19988 | 19993 | 20002 | 59 | 11.7 | `HerbData.kt:181-187`; corrected by `Herblore Habitat` oldid `6513740`. |

## Corrected clean levels

The dated wiki revision supersedes four stale game-main levels.
The unfinished-potion rows use the same corrected requirements.

| Herb | Old level | Correct level | Dated revision |
| --- | ---: | ---: | --- |
| Argway | 56 | 57 | `Herblore Habitat` oldid `6513740`, `2012-10-31T21:20:32Z`. |
| Ugune | 55 | 56 | `Herblore Habitat` oldid `6513740`, `2012-10-31T21:20:32Z`. |
| Shengo | 57 | 58 | `Herblore Habitat` oldid `6513740`, `2012-10-31T21:20:32Z`. |
| Samaden | 58 | 59 | `Herblore Habitat` oldid `6513740`, `2012-10-31T21:20:32Z`. |

## Recovered base lives

No family placeholder remains. At the pinned Darkan commit,
`FarmPatch.setInitialLives()` groups `VINE_HERB` with allotment, herb, and hop
patches and sets `lives = 3 + compostLevel` at lines 377-393. AnkiScape stores
that exact rule as `crop.base_lives = 3` plus the compost tier's `extra_lives`.

## Reachability result

The comparison uses this slice's merge-base, commit `0071218b`.
The audit command can exit `1` while orphan inputs remain.
The figures, not that exit code, define this gate.

| Record | Actions | Reachable items | Orphan inputs | Blocked actions |
| --- | ---: | ---: | ---: | ---: |
| Merge-base `0071218b` | 1,556 | 2,573 | 102 | 101 |
| Closed slice | 1,568 | 2,624 | 72 | 75 |
| Change | +12 | +51 | -30 | -26 |

The level-70 Common jadinko route closes the five seed roots.
The crop rows activate five grimy herbs, five clean herbs, and five unfinished potions.
## 2026-08-19 re-land verification

The re-land merged current main `d4c043218d5943f7878d36b556d785eeeefdeb36`
while correcting the acquisition rows against the pinned Darkan tables. Common
jadinko now opens all five seed roots at Hunter 70, and Carrion, Draconic,
Saradomin, and Zamorak retain their source-specific supplemental rolls through
main's structured `secondary_outputs` pure-layer contract.

The real kernel produced every chain outside the test runner. Each Common catch
supplied the selected seed and one Common vine; each seed planted in the
Habitat vine-herb patch, matured after 84 abstracted minutes, and harvested
three matching grimy herbs; cleaning and unfinished-potion mixing were enabled
at the corrected level and completed successfully.

| Record | Actions | Reachable items | Orphan inputs | Blocked actions |
| --- | ---: | ---: | ---: | ---: |
| Current main `d4c043218d5943f7878d36b556d785eeeefdeb36` | 1,571 | 2,266 | 84 | 87 |
| Re-land candidate | 1,584 | 2,334 | 50 | 53 |
| Change | +13 | +68 | -34 | -34 |

The five shipped-failure checks passed: period numbers retain their cited
sources; the chain ran through the real Hunter, Farming, and Herblore reducers;
no family row is inert in the reachability graph; no UI or panel rule was
introduced; and Darkan's `setInitialLives()` source retires the former base-lives
placeholder without changing the shipped value.
