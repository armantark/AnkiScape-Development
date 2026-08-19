# Grimy herb family source audit — 2026-08-11

Status: **closed with one registered placeholder.**

## Scope

This slice closes the acquisition and processing chain for five vine herbs.
The herbs are Erzille, Argway, Ugune, Shengo, and Samaden.
Carrion jadinkos now supply all five seeds.
Each seed now produces its matching grimy herb.
Herblore cleaning and unfinished-potion rows now use the corrected levels.

All evidence is from before `2012-11-20T00:00:00Z`.

## Source pins

| Source | Exact pin | Values that this source supplies |
| --- | --- | --- |
| RuneScape Wiki | `Herblore Habitat` oldid `6513740`, `2012-10-31T21:20:32Z` | Farming levels, planting XP, harvest XP, protection payments, clean levels, clean XP, and the five herb families. |
| RuneScape Wiki | `Seeds` oldid `6565109`, `2012-11-17T05:58:56Z` | Seed quantity, crop identities, and the 80-minute Ugune total. |
| RuneScape Wiki | `Jadinkos` oldid `5917881`, `2012-07-10T13:09:23Z` | Jadinko levels, Hunter XP, primary vine drops, and the vine-herb seed family. |
| Darkan | Commit `7e7d67b481f1b94599de38a98c470419ab7c96b3`, `src/main/java/com/rs/game/content/skills/farming/ProduceType.java:103-107` | Seed IDs, grimy-herb IDs, four stages, Farming levels, XP, and save endpoints `67/80`. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/farming/PatchType.java:267-275,370-379` | The vine-herb patch uses four growth ticks per stage. The Farming dossier resolves this as 20 minutes per stage. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:458-473` | The uncomposted disease check uses `Utils.random(128) < 6`. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/hunter/BoxHunterType.java:79-97` | Jadinko NPC IDs, levels, XP, Marasamaw tool use, and success endpoints. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/hunter/BoxTrapType.java:30` | Marasamaw plant item ID `19965`. |
| Darkan | Same commit, `data/npcs/drops/hunter/hunter_jadinko_carrion.json` | One Pungent vine and one uniformly selected seed at `30/256`. |
| game-main | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore/HerbData.kt:149-187` | Grimy, clean, and unfinished item identities plus clean XP. |
| game-main | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore/mixing/CreateUnfinishedPotionAction.kt:14-62` | One clean herb and one Vial of water produce one unfinished potion. This action gives no XP. |
| game-main | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:17538-17556` | Exact grimy, clean, and unfinished item IDs. |

## Carrion jadinko acquisition

Carrion jadinko is the direct seed source for this family.
The row uses a reusable Marasamaw plant.
One successful catch always gives one Pungent vine.
The independent seed roll gives one seed at `30/256`.
The five seeds have equal weight in that roll.

| Value | Pinned result | Exact source |
| --- | --- | --- |
| Hunter level | `78` | `Jadinkos` oldid `5917881`; Darkan `BoxHunterType.java:89`. |
| Hunter XP | `505` | `Jadinkos` oldid `5917881`; Darkan `BoxHunterType.java:89`. |
| NPC ID | `13154` | Darkan `BoxHunterType.java:89`. |
| Tool | Marasamaw plant, item `19965` | Darkan `BoxTrapType.java:30`. |
| Primary output | Pungent vine, item `19974`, quantity `1` | Darkan `BoxHunterType.java:89`; `hunter_jadinko_carrion.json`. |
| Success endpoints | `rate1=15`, `rate99=130` | Darkan `BoxHunterType.java:89`. |
| Seed chance | `30/256` | Darkan `hunter_jadinko_carrion.json`. |
| Seed selection | One uniformly selected row | Darkan `hunter_jadinko_carrion.json` uses `dropOne: true`. |
| Seed IDs | Erzille `19897`; Ugune `19902`; Argway `19907`; Shengo `19912`; Samaden `19917` | Darkan `hunter_jadinko_carrion.json`; `ProduceType.java:103-107`. |

The slice also registers six adjacent period Jadinko rows.
These rows keep the Hunter family complete and explain the seven new cape roll paths.

| Jadinko | Level | XP | NPC ID | Vine item and ID | `rate1/rate99` | Exact Darkan source |
| --- | ---: | ---: | ---: | --- | --- | --- |
| Igneous | 74 | 465 | 13143 | Marble vine `19980` | `25/145` | `BoxHunterType.java:87`; `hunter_jadinko_igneous.json`. |
| Aquatic | 76 | 475 | 13142 | Aquatic vine `19976` | `15/135` | `BoxHunterType.java:85`; `hunter_jadinko_aquatic.json`. |
| Amphibious | 77 | 485 | 13130 | Oily vine `19972` | `15/130` | `BoxHunterType.java:81`; `hunter_jadinko_amphibious.json`. |
| Draconic | 80 | 525 | 13131 | Draconic vine `19973` | `15/130` | `BoxHunterType.java:83`; `hunter_jadinko_draconic.json`. |
| Saradomin | 81 | 600 | 13163 | Saradomin vine `19981` | `15/130` | `BoxHunterType.java:95`; `hunter_jadinko_saradomin.json`. |
| Zamorak | 81 | 600 | 13165 | Zamorak vine `19983` | `15/130` | `BoxHunterType.java:97`; `hunter_jadinko_zamorak.json`. |

`Jadinkos` oldid `5917881` supplies the player-visible level, XP, and vine-drop evidence for these rows.

## Vine-herb Farming rows

All five crops use one seed and four stages.
Each stage takes 20 minutes, for an 80-minute total.
Each crop uses save endpoints `67/80`.
The uncomposted disease selector uses `6/128` before the compost adjustment.
The starting-life count is the only unrecovered value.

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

## Registered placeholder

This slice registers one placeholder.
It registers no placeholder for growth stages, stage time, disease slots, or the Carrion seed roll.

| ID | Value in code | Why it stays unrecovered | What will settle it |
| --- | --- | --- | --- |
| `farming.vine_herb_base_lives` | Ordinary-herb fallback of `3` base lives | Darkan `ProduceType.java:103-107` gives save endpoints `67/80`, but it does not give starting lives. The period wiki gives no starting-life count. | A period vine-herb harvest routine or a qualified cutoff harvest sample. |

## Reachability result

The comparison uses this slice's merge-base, commit `0071218b`.
The audit command can exit `1` while orphan inputs remain.
The figures, not that exit code, define this gate.

| Record | Actions | Reachable items | Orphan inputs | Blocked actions |
| --- | ---: | ---: | ---: | ---: |
| Merge-base `0071218b` | 1,556 | 2,573 | 102 | 101 |
| Closed slice | 1,568 | 2,624 | 72 | 75 |
| Change | +12 | +51 | -30 | -26 |

The Carrion seed route closes the five seed roots.
The crop rows activate five grimy herbs, five clean herbs, and five unfinished potions.
## 2026-08-19 re-land verification

The re-land merged current main `d4c043218d5943f7878d36b556d785eeeefdeb36`
without changing the period pins above. Carrion's seed roll now uses main's
existing structured `secondary_outputs` pure-layer contract instead of keeping
the branch's parallel secondary-output schema. No source value changed.

The real kernel produced every chain outside the test runner. Each Carrion
catch supplied the selected seed and one Pungent vine; each seed planted in the
Habitat vine-herb patch, matured after 84 abstracted minutes, and harvested
three matching grimy herbs; cleaning and unfinished-potion mixing were enabled
at the corrected level and completed successfully.

| Record | Actions | Reachable items | Orphan inputs | Blocked actions |
| --- | ---: | ---: | ---: | ---: |
| Current main `d4c043218d5943f7878d36b556d785eeeefdeb36` | 1,571 | 2,266 | 84 | 87 |
| Re-land candidate | 1,583 | 2,333 | 50 | 53 |
| Change | +12 | +67 | -34 | -34 |

The five shipped-failure checks passed: period numbers retain their cited
sources; the chain ran through the real Hunter, Farming, and Herblore reducers;
no family row is inert in the reachability graph; no UI or panel rule was
introduced; and the only unrecovered family value still has both its
`PLACEHOLDER(farming.vine_herb_base_lives)` marker and register row.
