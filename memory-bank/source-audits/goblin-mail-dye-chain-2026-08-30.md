# Goblin mail and dye acquisition audit — 2026-08-30

## Scope and verdict

This slice closes the period-authentic material chain consumed by Goblin
Diplomacy. It models only the quest chain: three plain Goblin mails, Aggie's
red, yellow, and blue dye recipes, red-plus-yellow orange dye mixing, and the
orange and blue mail recolours.

**Verdict:** one zero-XP Utility gathering review searches the three documented
Goblin Village crates and grants three plain Goblin mails. Six zero-XP Utility
material-processing reviews make the three component dyes, mix orange dye, and
recolour two mails. The exact starting inputs are three Redberries, two Onions,
two Woad leaves, and 15 Coins. One plain mail remains for the brown-mail turn-in.
Every quantity and identity is period-settled, so this slice adds no placeholder.

## Baseline correction

The task premise's bounded search used `tools/repo_search.py ... --names`, which
searches file names rather than file contents. The reproduced main baseline
already registered all seven dye/mail items through existing quest and shop
catalogs, and `Goblin mail` was already reachable through
`combat:goblin_level_11`. The actual missing graph links were producers for Red,
Yellow, Orange, and Blue dye and for Orange and Blue goblin mail. The guaranteed
three-crate quest route was also absent.

The new crate action is retained even though the audit's chosen plain-mail route
remains the pre-existing combat route: the crate route is the period guide's
quantity-complete ordinary quest path and avoids depending on an unstated monster
drop probability.

## Pinned pre-cutoff wiki revisions

All six pages were fetched as literal wikitext with `curl` using
`?action=raw&oldid=<revision>`. Their revision timestamps were independently
read from the MediaWiki revisions API.

| Page | Oldid | UTC timestamp | Permanent URL |
| --- | ---: | --- | --- |
| Goblin Diplomacy | `6485448` | `2012-10-27T18:21:47Z` | <https://runescape.wiki/w/Goblin_Diplomacy?oldid=6485448> |
| Goblin mail | `6293293` | `2012-09-25T05:42:57Z` | <https://runescape.wiki/w/Goblin_mail?oldid=6293293> |
| Orange dye | `6169860` | `2012-08-31T12:56:06Z` | <https://runescape.wiki/w/Orange_dye?oldid=6169860> |
| Blue dye | `6536075` | `2012-11-05T18:18:10Z` | <https://runescape.wiki/w/Blue_dye?oldid=6536075> |
| Orange goblin mail | `6435504` | `2012-10-17T19:20:23Z` | <https://runescape.wiki/w/Orange_goblin_mail?oldid=6435504> |
| Blue goblin mail | `6435506` | `2012-10-17T19:21:33Z` | <https://runescape.wiki/w/Blue_goblin_mail?oldid=6435506> |

The non-beta Goblin Diplomacy revision is the controlling source. Its literal
wikitext states the complete requirement bundle:

```text
*3 suits of [[Goblin mail]] (can be obtained during quest)
*[[Blue dye]] (or 2 [[Woad leaf|Woad leaves]] and 5 [[coins]] to make)
*[[Orange dye]] (or 2 [[Onion]]s, 3 [[Redberries]], and 10 coins to make)
```

It gives the three crate locations:

```text
# Behind the generals' hut
# Next to the western hut
# Up a ladder near the entrance
```

It fixes Aggie's component recipes, the player-made orange dye, and the blue
dye service:

```text
Orange dye is made from combining red dye (3 [[redberries]] and 5 [[coins]]) with yellow dye (2 [[onions]] and 5 coins). If you do not already have the yellow and red dyes, take the supplies to [[Aggie]] the witch in [[Draynor village]], then mix the yellow and red to create orange.
```

```text
Likewise, if you don't already have the blue dye, take 2 [[woad leaf|woad leaves]] and 5 coins to Aggie to create the blue dye.
```

It also fixes the three final item states and turn-in order:

```text
Dye one goblin mail orange, one blue, and leave the last one unaltered.
```

```text
give the [[orange goblin mail]] ... Give them the [[Blue goblin mail]] ... Give them the plain brown Goblin mail.
```

The item pages corroborate the transformations:

- Orange dye oldid `6169860`: orange dye is made by combining Red dye and
  Yellow dye; Aggie charges 5 Coins per component bottle.
- Blue dye oldid `6536075`: Aggie or Ali the Dyer makes Blue dye from two Woad
  leaves for 5 Coins.
- Orange goblin mail oldid `6435504`: use Orange dye on Goblin mail.
- Blue goblin mail oldid `6435506`: use Blue dye on Goblin mail.
- Goblin mail oldid `6293293`: Goblins may drop it, Goblin Village crates may
  contain it, and Goblin Diplomacy requires three.

Goblin mail and both coloured-mail pages begin with `{{beta}}`. They are not
used alone to close behavior. The non-beta quest revision, rev-742 client
identities, and two independent local implementations reconcile the claims.

## Rev-727 and rev-742 cache evidence

The exact item query was run against both dated cache builds:

```text
./tools/query_openrs2_cache.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache' --id 286 287 288 1763 1765 1767 1769 1793 1951 1957 995
./tools/query_openrs2_cache.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache' --id 286 287 288 1763 1765 1767 1769 1793 1951 1957 995
```

Both builds agree on names, IDs, stackability, and exchangeability:

| ID | Item | Stackable | Exchangeable |
| ---: | --- | --- | --- |
| 286 | Orange goblin mail | No | No |
| 287 | Blue goblin mail | No | No |
| 288 | Goblin mail | No | Yes |
| 1763 | Red dye | No | Yes |
| 1765 | Yellow dye | No | Yes |
| 1767 | Blue dye | No | Yes |
| 1769 | Orange dye | No | Yes |
| 1793 | Woad leaf | Yes | Yes |
| 1951 | Redberries | No | Yes |
| 1957 | Onion | No | Yes |
| 995 | Coins | Yes | No |

Between rev 727 and rev 742, all three mail models changed from `24514` to
`78507`, and the coloured recolour rows expanded. The encoded identity and
flags remained stable. This slice uses rev 742, the closest available pre-cutoff
cache, for the final item semantics and retains the existing October 17 source
sprites.

The closest-to-cutoff definition queries also returned:

```text
16559  Crate  [Search, null, null, null, null]
16560  Crate  [Search, null, null, null, null]
16561  Crate  [Search, null, null, null, null]
922    Aggie  [Talk-to, null, Make-dyes, null, null]
4493   General Bentnoze  [Talk-to, null, null, null, null]
4494   General Wartface  [Talk-to, null, null, null, null]
```

The cache proves three searchable crate identities and Aggie's Make-dyes
option. The wiki supplies the named locations. This audit does not invent a
one-to-one object-ID-to-location mapping.

## Local implementation corroboration

### 2011Scape (`/Users/ArmanTarkhanian1/Downloads/game-main`)

This checkout is not a Git worktree (`fatal: not a git repository (or any of
the parent directories): .git`), so no commit can be pinned. It is used only as
independent reconstruction evidence.

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/draynor/aggie.plugin.kts:20-29`
  exposes Red, Blue, and Yellow dye options with the exact ingredients and
  5-Coin fee.
- The same file at `:177-203`, `:223-225`, and `:246-290` states and consumes
  three Redberries, two Onions, or two Woad leaves plus 5 Coins.
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/goblin/goblin_level_2.plugin.kts:24-55`
  includes one Goblin mail in the reconstructed Goblin drop table.
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:287-289`
  maps IDs 286, 287, and 288 to Orange, Blue, and plain Goblin mail.

The `40/1024` Goblin drop row is emulator reconstruction evidence, not a
period-settled rate. The guaranteed crate path closes this slice without using
that number.

### Darkan (`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`)

The read-only Darkan checkout was inspected at
`6277992980582f7b3da3a48e722e96cfa5b0a57d`.

- `src/main/java/com/rs/game/content/quests/goblindiplomacy/GoblinDiplomacy.java:41-56,146-195,223-242`
  records the exact requirement text, IDs, ordered turn-ins, three one-use
  crates, and both mail recolours. The path's latest restoration commit is
  `d04ec34c12309b732ad8e9159223c3ca273cde0b`; the relevant surviving bodies
  trace through `afd096b773265197c220b3ea512a0ebe653f8004`,
  `e81ed74d77a860d176fadf50a23b1bb5d27cec34`, and
  `37592c5e1a69c73c24f7588a8b40cf23617daaba`.
- `src/main/java/com/rs/game/content/items/Dye.kt:13-17,29-41` records IDs,
  component quantities, and Red-plus-Yellow mixing. The path's latest
  restoration commit is `5ba57196a06738f9c291cbd00c9bb1dec671e256`;
  the current rows trace through
  `99be3ad196fa5c5fb0a00b6b869756c17572e2cc` and
  `37592c5e1a69c73c24f7588a8b40cf23617daaba`.
- `src/main/java/com/rs/game/content/world/areas/draynor/npcs/Aggie.kt:28-76`
  consumes each ingredient set and 5 Coins. The path's latest restoration
  commit is `34c07714e641bebeb80429e214b6b6b93c559387`; the current service body
  traces through `b946d556cc9931d81af43dcd30f6c129172f6dc2` and
  `c2b2616e85c28744ad5ef5a4d50ec0f6ca0bbcd0`.

Darkan is reconstruction evidence and contains post-period restoration commits.
It corroborates but does not independently date the behavior; the pinned wiki
and dated cache close the visible contract.

## Product translation

- `gather_goblin_mail` is a zero-XP Utility gathering action with no material
  inputs and a batch size of three, matching the three named one-use crates.
- `aggie_make_red_dye` consumes three Redberries and 5 Coins.
- `aggie_make_yellow_dye` consumes two Onions and 5 Coins.
- `mix_orange_dye` consumes one Red dye and one Yellow dye.
- `aggie_make_blue_dye` consumes two Woad leaves and 5 Coins.
- `dye_goblin_mail_orange` and `dye_goblin_mail_blue` each consume one plain
  mail and one matching dye.
- All seven rows use the existing Utility selector, persisted
  `current_utility`, generic review runtime, save path, telemetry, and answer
  undo. No runtime or interface implementation was added.
- The quest consumes Orange mail, Blue mail, then the one remaining plain mail.

## Asset provenance

All required art already existed. The slice reuses it and locks its source
metadata in focused tests instead of downloading duplicates.

| Local asset | Source UTC timestamp | Source SHA-1 | Local dimensions | Local SHA-1 |
| --- | --- | --- | --- | --- |
| `constructionitems/red_dye.png` | `2009-09-06T16:24:59Z` | `d0dfdcc6cef46f838ad7888617e7f0dca31ff277` | 17×29 | `e555ac8209bb4e466355755e48b2fb113340a106` |
| `shopitems/yellow_dye.png` | `2009-09-06T16:28:45Z` | `4601a46ad231461e9341610ab95a3b654f037779` | 17×29 | `a862d70cbac1826572e48d739987ef453e44458c` |
| `shopitems/orange_dye.png` | `2009-09-06T16:29:57Z` | `22ccd860345dcaa457c5e52e0337e626edfebd37` | 17×29 | `55a93b2ee135fcce6ebfeb3c5caaa6d446525c9a` |
| `shopitems/blue_dye.png` | `2009-09-05T14:21:22Z` | `051d587e277c459a3a8ac95a3469fd2d651e25ff` | 17×29 | `101bc299a0bd442db485b20c33167e1e46c3b830` |
| `questitems/goblin_mail.png` | `2012-10-17T17:16:16Z` | `b1f24492992d7104e5489a09af2367588db0124e` | 29×26 | `2d9c3c238680d66456b27a8582a6b83f2476e36e` |
| `questitems/orange_goblin_mail.png` | `2012-10-17T17:17:46Z` | `598931ae7e87d67afec3b287364a4bf50df6aa78` | 29×26 | `b7bec228bbf0ccf68fe6310a4ddb4e3bbd999670` |
| `questitems/blue_goblin_mail.png` | `2012-10-17T17:27:06Z` | `046e2019f976fa46d3d190d31825e67b8ed979a5` | 29×26 | `5abf773605c39811bced25b4d0a4ec606a60a24d` |
| `farmingitems/woad_leaf.png` | `2011-12-05T06:56:45Z` | `95781fe175ede07ffadb808a58187fbde06ea131` | 30×26 | `330193b9eff0feaac23403ce953251e81ad89192` |
| `cookingitems/redberries.png` | `2011-11-27T15:58:21Z` | `284229e880a37512af504f0d76e06ff5cd509b6f` | 18×21 | `04ab9c5f09f4b8deb783b31c510a666ef9466ce9` |
| `cookingitems/onion.png` | `2010-06-10T12:00:13Z` | `e0b2bc51f25b7055258fd9f22552ba536137faa8` | 17×13 | `65ee6b93d0a3085fc66bf1bd2d8246085e813f26` |

The new Red dye target row deliberately uses the existing pre-cutoff RS3
`constructionitems/red_dye.png` asset. It does not change the pre-existing
Lletya shop row's OSRS-backed canonical item icon.

## Explicit abstractions, omissions, and placeholders

- Utility reviews abstract travel, coordinates, dialogue pacing, world-object
  depletion, and respawn time. One review is one source trip or one item
  processing step.
- The three crate locations are represented as one three-item trip. The source
  fixes the three locations and Darkan corroborates three one-use crates; no
  random selector is introduced.
- Ali the Dyer's alternative Blue dye route is period-attested but is outside
  the quest's ordinary Aggie chain and is not generalized here.
- Existing Goblin and Hobgoblin drop probabilities remain reconstruction data.
  This slice neither changes nor describes them as period-settled.
- No hidden value is needed by the implemented chain, so
  `memory-bank/placeholder-values.md` receives no row.

## Reachability result

| Pin | Before | After |
| --- | ---: | ---: |
| `action_count` | 1601 | 1608 |
| `reachable_item_count` | 2237 | 2243 |
| `orphan_input_count` | 190 | 190 |
| `root_orphan_count` | 39 | 39 |
| `cascade_orphan_count` | 151 | 151 |
| `unresolved_action_count` | 277 | 277 |
| `seed_item_count` | 1177 | 1177 |

Goblin Diplomacy no longer appears in `blocked_quest_stage_products`. The
completable-quest count rises from 43 to 44, and the startable-quest count rises
from 113 to 114. The Lost Tribe becomes startable but remains non-completable at
its own stage-2 generated sentinel, `Complete The Lost Tribe stage 2 objective`.

## Acceptance contract

- The three-crate action grants exactly three Goblin mails and no XP.
- Starting from three Redberries, two Onions, two Woad leaves, and 15 Coins,
  the seven-action chain leaves exactly one Orange mail, one Blue mail, and one
  plain mail, with no component dyes or payment remaining.
- Items 286, 287, 288, 1763, 1765, 1767, 1769, 1793, 1951, and 1957 retain the
  rev-742 identities and flags in the item registry.
- Every new target row uses existing sourced art and the existing target-row
  contract without interface code changes or visible truncation.
- Answer undo restores the exact pre-review inventory for every new action.
- Reachability resolves all four dyes and both coloured mails and clears Goblin
  Diplomacy without claiming The Lost Tribe is completable.

## Verification

Focused plain checks:

```text
Ran 6 tests in 6.624s
OK
```

Focused Qt checks:

```text
Ran 2 tests in 1.282s
OK
```

Full plain lane:

```text
Ran 4548 tests in 407.900s
OK (skipped=515)
```

Full offscreen Qt lane:

```text
Ran 4548 tests in 697.572s
OK (skipped=3)
```

Supporting audits:

```text
Audited 609 Markdown and 441 HTML files.
Documentation audit passed.
4513 tests across 221 files
hard issues: 0
structural clone candidates: 31 groups
```

The final reachability report retained the seven after-pins above, 145 blocked
quest-stage rows, no Goblin Diplomacy row, and the exact Lost Tribe stage-2
sentinel. It returned exit 1 because 190 unrelated orphan inputs remain. The
final guarded-worktree audit reported the layout safe.

Offscreen geometry checks showed horizontal-scroll maximum 0 at both the default
720×540 dialog and a 1080×560 laptop-height dialog. The captured Utility rows
showed all six processing labels without truncation.
