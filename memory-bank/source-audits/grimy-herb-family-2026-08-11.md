# Grimy herb family source audit — 2026-08-11

Status: **source-audited; twelve rows are implemented, six have registered multi-secondary-table gaps, and one source-backed tracker route is queued.**

## Scope

This slice closes the acquisition and processing chain for five vine herbs.
The herbs are Erzille, Argway, Ugune, Shengo, and Samaden.
Common and Carrion jadinkos supply all five seeds. Draconic, Guthix, Saradomin,
Zamorak, Shadow, and Diseased supply the four seeds above Erzille at their exact
Darkan chances. Igneous and Cannibal supply Lergberry or Kalferberry seeds,
Aquatic supplies blossom seeds, and Amphibious supplies three fruit-tree seeds.

Darkan's source roster has thirteen Jadinko types. The branch registers twelve:
ten Marasamaw catches plus the Shadow and Diseased tracker routes. Camouflaged
is the third source-backed tracker, but it is not implemented in this slice and
is queued separately in `memory-bank/design-thread-queue.md` section 3.28.

Six registered rows — Common, Guthix, Saradomin, Zamorak, Shadow, and Diseased —
also have independent bush- and blossom-seed tables. The pure Hunter action can
execute only one secondary table per action, so all six exact omissions carry
adjacent `PLACEHOLDER(hunter.jadinko_multi_secondary_tables)` markers rather
than approximations. Each vine-herb seed produces its matching grimy herb.
Herblore cleaning and unfinished-potion rows use the corrected levels.

All evidence is from before `2012-11-20T00:00:00Z`.

## Source pins

| Source | Exact pin | Values that this source supplies |
| --- | --- | --- |
| RuneScape Wiki | `Herblore Habitat` oldid `6513740`, `2012-10-31T21:20:32Z` | Farming levels, planting XP, harvest XP, protection payments, and the five herb families. |
| RuneScape Wiki | `Grimy erzille` oldid `6367356`, `2012-10-08T00:31:09Z` | Clean level 54 and 10.0 clean XP. |
| RuneScape Wiki | `Grimy argway` oldid `5288273`, `2012-02-25T16:58:12Z` | Clean level 57 and 11.6 clean XP. |
| RuneScape Wiki | `Grimy ugune` oldid `5307711`, `2012-03-01T16:32:35Z` | Clean level 56 and 11.5 clean XP. |
| RuneScape Wiki | `Grimy shengo` oldid `5288022`, `2012-02-25T14:17:38Z` | Clean level 58 and 11.7 clean XP. |
| RuneScape Wiki | `Grimy samaden` oldid `5285365`, `2012-02-24T17:32:22Z` | Clean level 59 and 11.7 clean XP. |
| RuneScape Wiki | `Seeds` oldid `6565109`, `2012-11-17T05:58:56Z` | Seed quantity, crop identities, and the 80-minute Ugune total. |
| RuneScape Wiki | `Jadinkos` oldid `5917881`, `2012-07-10T13:09:23Z` | Jadinko levels, Hunter XP, primary vine drops, and the vine-herb seed family. |
| Darkan | Commit `7e7d67b481f1b94599de38a98c470419ab7c96b3`, `src/main/java/com/rs/game/content/skills/farming/ProduceType.java:103-107` | Seed IDs, grimy-herb IDs, four stages, Farming levels, XP, and save endpoints `67/80`. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/farming/PatchType.java:267-275,370-379` | The vine-herb patch uses four growth ticks per stage. The Farming dossier resolves this as 20 minutes per stage. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:377-393` | `setInitialLives()` gives `VINE_HERB` exactly `3 + compostLevel` starting lives. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:458-473` | The generic Farming disease selector supplies the registered `farming.shared_disease_slots` placeholder; it does not settle a Habitat-specific period rate. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/skills/hunter/BoxHunterType.java:79-97` | Ten Marasamaw rows: NPC IDs, levels, XP, tool use, and success endpoints. |
| Darkan | Same commit, `src/main/java/com/rs/game/content/minigames/herblorehabitat/JadinkoType.kt:15-46` | The thirteen-row source roster and each row's Hunter level, guaranteed item, Juju requirement, Habitat feature, and produce setup. Camouflaged is level 79, gives item `19978`, requires Standing Stones and Lergberry, and requires an empty tree patch. |
| Darkan | Descendant commit `16b179acec2cd94ced1625741dc5a974010c21d2`, same `JadinkoType.kt:15-46` | Restored tracker XP values: Shadow `475.0`, Diseased `580.5`, and Camouflaged `600.0`. The earlier `7e7d67b` pin supplies the roster and setup but predates the `trackerXp` field. |
| Darkan | Commit `7e7d67b481f1b94599de38a98c470419ab7c96b3`, `src/main/java/com/rs/game/content/skills/hunter/BoxTrapType.java:30` | Marasamaw plant item ID `19965`. |
| Darkan | Same commit, `data/npcs/drops/hunter/hunter_jadinko_{common,shadow,igneous,cannibal,aquatic,amphibious,carrion,diseased,camouflaged,draconic,saradomin,guthix,zamorak}.json` and `data/npcs/drops/hunter/jadinko_sub/hh_{bush,blossom}_seed.json` | All thirteen guaranteed outputs; every vine-herb, bush, blossom, and fruit-tree secondary table; and every chance and item ID cited below. |
| RuneScape Wiki files | Cutoff revisions recorded in `assets_provenance.json` | Exact inventory sprites for all twelve implemented guaranteed outputs: Withered, Shadow, Marble, Aquatic, Oily, Pungent, Corrupt, Draconic, Saradomin, Guthix, and Zamorak vines, plus Plant teeth. |
| game-main | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore/HerbData.kt:149-187` | Grimy, clean, and unfinished item identities plus clean XP. |
| game-main | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore/mixing/CreateUnfinishedPotionAction.kt:14-62` | One clean herb and one Vial of water produce one unfinished potion. This action gives no XP. |
| game-main | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:17538-17556` | Exact grimy, clean, and unfinished item IDs. |

## Jadinko seed acquisition

Common jadinko is the earliest direct vine-herb seed source at Hunter 70. Its
live secondary table gives one of all five vine-herb seeds at `16/256`; Carrion
gives the same set at `30/256`. Draconic gives one of the four seeds above
Erzille at `14/256`; Guthix, Saradomin, Zamorak, Shadow, and Diseased each give
one of those four at `5/256`. Igneous gives one of the two vine-bush seeds at
`13/256`, Cannibal at `12/256`, Aquatic gives one of the three blossom seeds at
`12/256`, and Amphibious gives Apple, Banana, or Orange tree seed at `20/256`.

The source roster has thirteen rows. The table includes all thirteen so its
boundary follows `JadinkoType.kt`, not the branch: twelve rows have live routes,
and Camouflaged is explicitly marked absent. All twelve implemented primary
outputs have cutoff-era inventory sprites through the established Hunter asset
path.

| Jadinko | Route | Level | XP | NPC ID | Guaranteed item and ID | `rate1/rate99` | Implemented secondary roll | Other source tables not implemented | Pinned row sources |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| Common | Marasamaw | 70 | 350 | 13119 | Withered vine `19971` | `30/150` | All five vine-herb seeds, `16/256` | Bush seeds, `14/256`; blossom seeds, `17/256` | `BoxHunterType.java:79`; `hunter_jadinko_common.json`; `hh_bush_seed.json`; `hh_blossom_seed.json`. |
| Shadow | Tracker | 71 | 475 | — | Shadow vine `19977` | `128/256` placeholder | Four seeds above Erzille, `5/256` | Bush seeds, `8/256`; blossom seeds, `4/256` | `JadinkoType.kt:34`; `hunter_jadinko_shadow.json`; `hh_bush_seed.json`; `hh_blossom_seed.json`. |
| Igneous | Marasamaw | 74 | 465 | 13143 | Marble vine `19980` | `25/145` | Lergberry or Kalferberry seed, `13/256` | — | `BoxHunterType.java:87`; `hunter_jadinko_igneous.json`; `hh_bush_seed.json`. |
| Cannibal | Marasamaw | 75 | 475 | 13155 | Plant teeth `19975` | `20/140` | Lergberry or Kalferberry seed, `12/256` | — | `BoxHunterType.java:91`; `hunter_jadinko_cannibal.json`; `hh_bush_seed.json`. |
| Aquatic | Marasamaw | 76 | 475 | 13142 | Aquatic vine `19976` | `15/135` | Red, Blue, or Green blossom seed, `12/256` | — | `BoxHunterType.java:85`; `hunter_jadinko_aquatic.json`; `hh_blossom_seed.json`. |
| Amphibious | Marasamaw | 77 | 485 | 13130 | Oily vine `19972` | `15/130` | Apple, Banana, or Orange tree seed, `20/256` | — | `BoxHunterType.java:81`; `hunter_jadinko_amphibious.json`. |
| Carrion | Marasamaw | 78 | 505 | 13154 | Pungent vine `19974` | `15/130` | All five vine-herb seeds, `30/256` | — | `BoxHunterType.java:89`; `hunter_jadinko_carrion.json`. |
| Diseased | Tracker | 78 | 580.5 | — | Corrupt vine `19979` | `128/256` placeholder | Four seeds above Erzille, `5/256` | Bush seeds, `8/256`; blossom seeds, `4/256` | `JadinkoType.kt:40`; `hunter_jadinko_diseased.json`; `hh_bush_seed.json`; `hh_blossom_seed.json`. |
| Camouflaged | Tracker — not implemented | 79 | 600 | — | Camo vine `19978` | — | None; no live route | Bush seeds, `16/256`; four seeds above Erzille, `4/256`; blossom seeds, `4/256` | `JadinkoType.kt:41`; `hunter_jadinko_camouflaged.json`; `hh_bush_seed.json`; `hh_blossom_seed.json`. |
| Draconic | Marasamaw | 80 | 525 | 13131 | Draconic vine `19973` | `15/130` | Four seeds above Erzille, `14/256` | — | `BoxHunterType.java:83`; `hunter_jadinko_draconic.json`. |
| Saradomin | Marasamaw | 81 | 600 | 13163 | Saradomin vine `19981` | `15/130` | Four seeds above Erzille, `5/256` | Bush seeds, `6/256`; blossom seeds, `4/256` | `BoxHunterType.java:95`; `hunter_jadinko_saradomin.json`; `hh_bush_seed.json`; `hh_blossom_seed.json`. |
| Guthix | Marasamaw | 81 | 600 | 13164 | Guthix vine `19982` | `15/130` | Four seeds above Erzille, `5/256` | Bush seeds, `6/256`; blossom seeds, `4/256` | `BoxHunterType.java:93`; `hunter_jadinko_guthix.json`; `hh_bush_seed.json`; `hh_blossom_seed.json`. |
| Zamorak | Marasamaw | 81 | 600 | 13165 | Zamorak vine `19983` | `15/130` | Four seeds above Erzille, `5/256` | Bush seeds, `6/256`; blossom seeds, `4/256` | `BoxHunterType.java:97`; `hunter_jadinko_zamorak.json`; `hh_bush_seed.json`; `hh_blossom_seed.json`. |

### Guaranteed-vine item semantics

The seven rows below are enumerated from Darkan commit
`7e7d67b481f1b94599de38a98c470419ab7c96b3`,
`src/main/java/com/rs/game/content/minigames/herblorehabitat/JadinkoType.kt:35-45`,
and its matching Marasamaw routes in
`src/main/java/com/rs/game/content/skills/hunter/BoxHunterType.java:81-97`, not
from AnkiScape's item registry. Darkan's inherited
`ItemConstants.isTradeable()` rule at
`src/main/java/com/rs/game/player/content/ItemConstants.java:388-410` (core
rule commit `c6fbe036b1743f4dd6067ec178332c69c3708856`) and the later exception
set at `src/main/java/com/rs/game/content/ItemConstants.java:403-428` (commit
`14fb66f0db9d2ca8a63c6f0dec24fa1e709e290c`) treats stackable items as
tradeable only when `canExchange()` is true or their ID is in the explicit
exception set. None of these seven IDs appears there. The immutable
`/Users/ArmanTarkhanian1/Library/Caches/Codex/2012scape-openrs2/runescape-727-2012-07-24-openrs2-309-disk.zip`
archive has SHA-256
`ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8`; the
independent near-cutoff
`/Users/ArmanTarkhanian1/Library/Caches/Codex/2012scape-openrs2/runescape-742-2012-11-07-openrs2-544-disk.zip`
has SHA-256
`9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`. Both
decode every row below as `stackable=true, exchangeable=false`. Each pinned wiki
infobox independently says `tradeable = No` and describes an ingredient, bait,
or compost use, so their Hunter extra-item rows remain untradeable and retain
category `material`.

| Item | Dated cache definitions | Pinned pre-cutoff wiki evidence |
| --- | --- | --- |
| Aquatic vine `19976` | rev 727 and rev 742: `stackable=true`, `exchangeable=false` | [`Aquatic vine` oldid `5037449`](https://runescape.wiki/w/Aquatic_vine?oldid=5037449), `2011-12-10T01:37:34Z`, lines 1-20: `tradeable = No`; secondary ingredient for Juju fishing potion. |
| Draconic vine `19973` | rev 727 and rev 742: `stackable=true`, `exchangeable=false` | [`Draconic vine` oldid `5037535`](https://runescape.wiki/w/Draconic_vine?oldid=5037535), `2011-12-10T01:42:45Z`, lines 1-19: `tradeable = No`; secondary ingredient for Juju mining potion. |
| Marble vine `19980` | rev 727 and rev 742: `stackable=true`, `exchangeable=false` | [`Marble vine` oldid `5037668`](https://runescape.wiki/w/Marble_vine?oldid=5037668), `2011-12-10T01:49:47Z`, lines 1-20: `tradeable = No`; secondary ingredient for Juju farming potion. |
| Oily vine `19972` | rev 727 and rev 742: `stackable=true`, `exchangeable=false` | [`Oily vine` oldid `5037731`](https://runescape.wiki/w/Oily_vine?oldid=5037731), `2011-12-10T01:53:01Z`, lines 1-20: `tradeable = No`; combined with Clean samaden for Juju woodcutting potion. |
| Pungent vine `19974` | rev 727 and rev 742: `stackable=true`, `exchangeable=false` | [`Pungent vine` oldid `6016415`](https://runescape.wiki/w/Pungent_vine?oldid=6016415), `2012-07-30T21:11:06Z`, lines 1-20: `tradeable = No`; jadinko bait or supercompost material. |
| Saradomin vine `19981` | rev 727 and rev 742: `stackable=true`, `exchangeable=false` | [`Saradomin vine` oldid `5037805`](https://runescape.wiki/w/Saradomin_vine?oldid=5037805), `2011-12-10T01:56:35Z`, lines 1-20: `tradeable = No`; secondary ingredient for Saradomin's blessing. |
| Zamorak vine `19983` | rev 727 and rev 742: `stackable=true`, `exchangeable=false` | [`Zamorak vine` oldid `5970327`](https://runescape.wiki/w/Zamorak_vine?oldid=5970327), `2012-07-21T23:17:38Z`, lines 1-20: `tradeable = No`; secondary ingredient for Zamorak's favour. |

The 2011Scape snapshot conflicts: `data/cfg/items.yml:240819-240889` marks all
seven `tradeable: true`. That lower-tier value does not survive corroboration
against either dated cache or any of the seven pinned period wiki infoboxes, so
it is not used.

The twelve live rows are registered in `data/hunter_data.py`. The six known
multi-table omissions have adjacent markers at lines 402, 436, 772, 826, 989,
and 1021. The ten Marasamaw rows use the sourced `BoxHunterType` curves; only
the live Shadow and Diseased tracker rows remain on
`hunter.herblore_habitat_success_curves`. Camouflaged needs a third tracker
route with its own feature and produce gates, so it is a separate content slice,
not a seventh marker added to an absent action.

Every implemented secondary selector picks one item (`dropOne: true` in its
direct or referenced table). Vine-herb seed IDs are Erzille `19897`, Ugune
`19902`, Argway `19907`, Shengo `19912`, and Samaden `19917`. The shared bush
table contains Lergberry `19937` and Kalferberry `19942`; the shared blossom
table contains Red `19922`, Blue `19927`, and Green `19932`. Amphibious directly
lists Apple `5283`, Banana `5284`, and Orange `5285` tree seeds.

The omitted tables on Common, Guthix, Saradomin, Zamorak, Shadow, and Diseased
are independent of each row's live vine-herb table and can produce an additional
drop on the same action. Folding them into one chance or one weighted output
list would change those mechanics. The registered gap remains until Hunter
carries an ordered tuple of independently rolled secondary tables, as recorded
in `memory-bank/design-thread-queue.md` section 4.16. Camouflaged's whole route
remains separately queued in section 3.28.

## Vine-herb Farming rows

All five crops use one seed and four stages.
Each stage takes 20 minutes, for an 80-minute total.
Each crop uses save endpoints `67/80`.
Vine herbs use the registered `farming.shared_disease_slots` placeholder: Darkan's generic uncomposted `6/128` selector before the compost adjustment. A period Habitat routine remains unrecovered.
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
| Erzille | 19984 | 19989 | 19998 | 54 | 10.0 | `HerbData.kt:149-155`; `Grimy erzille` oldid `6367356`. |
| Argway | 19985 | 19990 | 20000 | 57 | 11.6 | `HerbData.kt:157-163`; corrected by `Grimy argway` oldid `5288273`. |
| Ugune | 19986 | 19991 | 19999 | 56 | 11.5 | `HerbData.kt:165-171`; corrected by `Grimy ugune` oldid `5307711`. |
| Shengo | 19987 | 19992 | 20001 | 58 | 11.7 | `HerbData.kt:173-179`; corrected by `Grimy shengo` oldid `5288022`. |
| Samaden | 19988 | 19993 | 20002 | 59 | 11.7 | `HerbData.kt:181-187`; corrected by `Grimy samaden` oldid `5285365`. |

## Corrected clean levels

The dated herb-page revisions supersede four stale game-main levels.
The unfinished-potion rows use the same corrected requirements.

| Herb | Old level | Correct level | Dated revision |
| --- | ---: | ---: | --- |
| Argway | 56 | 57 | `Grimy argway` oldid `5288273`, `2012-02-25T16:58:12Z`. |
| Ugune | 55 | 56 | `Grimy ugune` oldid `5307711`, `2012-03-01T16:32:35Z`. |
| Shengo | 57 | 58 | `Grimy shengo` oldid `5288022`, `2012-02-25T14:17:38Z`. |
| Samaden | 58 | 59 | `Grimy samaden` oldid `5285365`, `2012-02-24T17:32:22Z`. |

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

The re-land branch starts from merge-base
`d4c043218d5943f7878d36b556d785eeeefdeb36` and corrects the acquisition rows
against the pinned Darkan tables. Common
jadinko now opens all five seed roots at Hunter 70, and Carrion, Draconic,
Saradomin, and Zamorak retain their source-specific supplemental rolls through
main's structured `secondary_outputs` pure-layer contract.

The real kernel produced every chain outside the test runner. Each Common catch
supplied the selected seed and one Withered vine; each seed planted in the
Habitat vine-herb patch, matured after 84 abstracted minutes, and harvested
three matching grimy herbs; cleaning and unfinished-potion mixing were enabled
at the corrected level and completed successfully.

| Record | Actions | Reachable items | Orphan inputs | Blocked actions |
| --- | ---: | ---: | ---: | ---: |
| Re-land merge-base `d4c043218d5943f7878d36b556d785eeeefdeb36` | 1,571 | 2,266 | 84 | 87 |
| Re-land candidate | 1,584 | 2,334 | 50 | 53 |
| Change | +13 | +68 | -34 | -34 |

The five shipped-failure checks passed: period numbers retain their cited
sources; the chain ran through the real Hunter, Farming, and Herblore reducers;
no family row is inert in the reachability graph; no UI or panel rule was
introduced; and Darkan's `setInitialLives()` source retires the former base-lives
placeholder without changing the shipped value.
