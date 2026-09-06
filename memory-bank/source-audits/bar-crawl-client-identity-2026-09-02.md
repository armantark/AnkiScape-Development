# RuneScape Bar Crawl: client-identity evidence

Date: 2026-09-02. Scope: read-only recovery of the RuneScape Bar Crawl client
identities from the local Darkan checkout, the local revision-727 OpenRS2 cache,
`/Users/ArmanTarkhanian1/Downloads/game-main`, and the remaining dated caches.
This record pins identities, names, interaction labels, source locations, and
source-side drink actions. It does not claim that a server-side effect or price
is a client-cache value.

## Provenance and archive set

The source implementation is the working-tree-identical-to-HEAD content in
`/Users/ArmanTarkhanian1/Documents/2012scape with bots`, current `HEAD`
`89f204233df16233a0eccb3c215811813e26aa24` (2026-09-02T09:42:46-07:00).
The checkout has unrelated dirty memory-bank material; the target Bar Crawl
sources, `BartenderUtils.kt`, and the NPC spawn dataset have no working-tree
diff. Their SHA-256 values are:

| Source file | SHA-256 |
| --- | --- |
| `darkan-world-server/src/main/java/com/rs/game/content/miniquests/bar_crawl/BarCrawl.kt` | `e6f576580316c0433d0c9e7ffc091bcc0c18c8f3b41644dd7a2755c0e4d05114` |
| `darkan-world-server/src/main/java/com/rs/game/content/utils/BartenderUtils.kt` | `f03b7901f5aa277979833ab7ecdc1e9e08878826087ff5ba0eceddabed68bf96` |
| `darkan-world-server/data/npcs/spawns/real_rs_spawns_unorganized.json` | `5db71ca982ca9c97fccddaf3655038aa1a37c9fbab90ad3ec218644b6b5252a1` |

The immutable local period-cache directories are under
`/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/`.
The SHA-256 values below are for each `cache/main_file_cache.dat2`:

| Build | Date | SHA-256 |
| ---: | --- | --- |
| 652 | 2011-06-08 | `5c920575cf646f05be00b12c3626c84f530682a0373c7452124c5c92a79bcab6` |
| 727 | 2012-07-24 | `2b8837d046688f566afca03f416e10607438842df43682f59ed1e01fa92418fc` |
| 728 | 2012-08-01 | `e0ec6a192c1e662243f1a6764a8b0476ff3ce64f031cf787482b1f09810d5376` |
| 729 | 2012-08-11 | `3e34fcf27c8cc8390a97c8acf095eabbc0cd1a158b593c1cbd8f3120d521bfe3` |
| 736 | 2012-10-09 | `a1e806aec4762b4fc00c80a625a7837d82aec4a027994730401c9eadacf87044` |
| 741 | 2012-11-04 | `a36b963a3a3202922b13d8b689da854d0c5c5681c432002499d94bceaa77315f` |
| 742 | 2012-11-07 | `8302e5d802add42424a2d68cec023948667d85c721fc39adf5ab9de0278c8d93` |

`/Users/ArmanTarkhanian1/Downloads/game-main` is not a Git repository. Its
relevant snapshot fingerprints are `data/cfg/items.yml` SHA-256
`4bc95333b282216b6d1a50dd60b4510aa0bbc837d5bc39b0d1b8e44d7390e4f0`,
`Items.kt` SHA-256
`77b817e72cbaf384178fcbeada61cddc5502129b5bb8b45ba3c34b39bf15847b`, and
`Npcs.kt` SHA-256
`d8870eb6ae2eca51986f4bb6b862661179925b70e1b3ced9af9d0db64d4fd554`.
Its relevant files have local mtime `2025-05-01T14:06:38-0700`; that is not an
upstream commit date.

## Search order, tools, and positive controls

The repository’s read-only decoders were used:

```sh
/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/query_openrs2_cache_definitions.sh <cache> npc|object <term|--id ...>
/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/query_openrs2_cache.sh <cache> <term|--id ...>
```

The definition decoder was positively controlled on revision 727 before any
negative name search:

```sh
.../query_openrs2_cache_definitions.sh .../727-2012-07-24/cache npc 'Luminescent icefiend'
```

It returned all IDs `9912` through `9928`, each named `Luminescent icefiend`
and exposing `[null, Attack, null, null, null]`. The item decoder’s direct
positive control returned:

```text
455	Barcrawl card	[Read, null, null, null, drop]
```

Darkan’s Bar Crawl source is
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/miniquests/bar_crawl/BarCrawl.kt`.
It binds card `455`, guard `384`, and gates `2115`/`2116` at lines 20-38 and
lists the ten bars, prices, and drink labels at lines 133-151. Its bartender
handlers bind the listed NPC IDs to the source-side Bar Crawl action.

`game-main` was searched next. Its direct source-term command was:

```sh
rg -n -i --glob '!**/build/**' --glob '!**/.gradle/**' '(barcrawl|bar[ _-]crawl)' /Users/ArmanTarkhanian1/Downloads/game-main
```

The complete result was only the card’s item definition and generated constant:

```text
/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:3153:  name: "Barcrawl card"
/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:3154:  examine: "The official Alfred Grimhand bar crawl card."
/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:456:    const val BARCRAWL_CARD = 455
```

This negative implementation result has positive controls: the snapshot holds
913 Kotlin files, active quest implementations in
`game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/`, generated
entity catalogs, spawn scripts, and cache/map loaders. It contains no Bar Crawl
handler, dialogue, stage, object reference, or source-side bartender mapping.

Finally, exact-ID reads were compared across all seven dated caches. Builds
727, 728, 729, 736, 741, and 742 produce byte-identical English rows for the
target IDs. Build 652 has the same numeric identities but German-localized
names/options: e.g. item 455 is `Tavernenmarathonkarte` with `Lesen`, `Gate`
is `Tor` with `Öffnen`, and `Bartender` is `Barkeeper` with `Ansprechen`.

## Recovered client identities

### Card and completion-gate objects

| Identity | ID | Revision-727 and revision-742 definition |
| --- | ---: | --- |
| Barcrawl card | 455 | `Barcrawl card`; inventory option `Read`; model `2430`; non-stackable and non-exchangeable |
| Barbarian Outpost gate | 2115 | `Gate`; object option `Open` |
| Barbarian Outpost gate | 2116 | `Gate`; object option `Open` |

The server source’s `onObjectClick(2115, 2116)` gate binds the two client object
IDs to completed-Bar-Crawl access. No authoritative gate tile was recovered:
the Darkan object-spawn overlay is only 11 rows and has no 2115/2116 row. That
is not evidence that the client map lacks them.

### Ten bar actions, NPC identities, and locations

Coordinates are Darkan’s explicit NPC-spawn data. The cache confirms IDs and
native interaction labels, while the source handler ties each ID to exactly one
Bar Crawl entry. Every row below is stable in rev727 and rev742.

| Bar and source drink | Price | NPC ID(s), cache name, native option | Darkan source coordinate(s) |
| --- | ---: | --- | --- |
| Blue Moon Inn, Varrock — Uncle Humphrey’s Gutrot | 50 | 733, `Bartender`, `Talk-to` | (3226, 3399, 0) |
| Blurberry’s Bar, Tree Gnome Stronghold — Fire Toad Blast | 10 | 848, `Blurberry`, `Talk-to` | (2480, 3490, 1) |
| Dead Man’s Chest, Brimhaven — Supergrog | 15 | 735, `Bartender`, `Talk-to` | (2797, 3155, 0) |
| Dragon Inn, Yanille — Fire Brandy | 12 | 739, `Bartender`, `Talk-to` | (2556, 3078, 0) |
| Flying Horse Inn, Ardougne — Heart Stopper | 8 | 738, `Bartender`, `Talk-to` | (2574, 3319, 0) |
| Forester’s Arms, Seers’ Village — Liverbane Ale | 18 | 737, `Bartender`, `Talk-to` | (2690, 3493, 0) |
| Jolly Boar Inn, north-east of Varrock — Olde Suspiciouse | 10 | 731, `Bartender`, `Talk-to` | (3277, 3488, 0) |
| Karamja Spirits Bar, Musa Point — Ape Bite Liqueur | 7 | 568, `Zambo`, `Talk-to`, `Trade` | (2924, 3143, 0) |
| Rising Sun, Falador — Hand of Death Cocktail | 70 | 736 `Emily`, 3217 `Kaylee`, 3218 `Tina`; each `Talk-to` | (2954, 3373, 0); (2957, 3370, 0); (2956, 3373, 1) |
| Rusty Anchor, Port Sarim — Black Skull Ale | 8 | 734, `Bartender`, no native cache option | (3044, 3255, 0) |

The source handlers are respectively under
`darkan-world-server/src/main/java/com/rs/game/content/world/areas/{varrock,tree_gnome_stronghold,karamja,yanille,ardougne,falador,port_sarim,seers_village}/npcs/`.
For all handlers other than the Rising Sun’s three-ID binding, `onNpcClick` is
one ID: 731, 733, 734, 735, 737, 738, 739, 848, or 568. The Rising Sun handler
binds `onNpcClick(736, 3217, 3218)`.

`game-main` independently records the period bartender coordinates for 731,
733, 734, 735, 738, and 739. It differs from Darkan’s spawn source by one tile
for ID 734 `(3045, 3256, 0)` versus `(3044, 3255, 0)`, and by two x tiles for
ID 735 `(2795, 3155, 0)` versus `(2797, 3155, 0)`. This record preserves both
rather than choosing one. It has no registered spawn for 737, and associates
738 with both `(2574, 3319, 0)` and `(2691, 3492, 0)` without a Bar Crawl link.

### Drinks have no recovered inventory IDs

The explicit source action proves the distinction:
`BartenderUtils.kt:37-50` checks only the player’s coin balance, invokes the
bar effect/message, and does not add an `Item`. Each drink above is therefore a
named Bar Crawl action in this source, not evidence for a client item ID.

After the cache positive controls, the exact 10 source drink labels were
searched as item terms in rev727 and rev742:

```sh
.../query_openrs2_cache.sh .../727-2012-07-24/cache 'Uncle Humphrey' 'Fire Toad Blast' 'Supergrog' 'Fire Brandy' 'Heart Stopper' 'Liverbane Ale' 'Olde Suspiciouse' 'Ape Bite Liqueur' 'Hand of Death Cocktail' 'Black Skull Ale'
.../query_openrs2_cache.sh .../742-2012-11-07/cache 'Uncle Humphrey' 'Fire Toad Blast' 'Supergrog' 'Fire Brandy' 'Heart Stopper' 'Liverbane Ale' 'Olde Suspiciouse' 'Ape Bite Liqueur' 'Hand of Death Cocktail' 'Black Skull Ale'
```

Each completed with exit code `0` and `0` matched rows. This proves only that
those exact source labels are absent from the readable item definitions in
those two cache revisions; it does not prove that no differently named drink
item exists.

The same full-name scan against build 652 is inconclusive, not negative: the
Darkan core 2.0.5 item decoder reports `MISSING OPCODE 254 FOR ITEM 6` and exits
partial before a complete item scan. Exact `--id` definitions still decode in
that cache and establish localization only.

## Narrow result

The client identity is pinned as card 455, guard 384, gate objects 2115/2116,
and the 13 bartender NPC IDs above. The local client definitions expose only
native options, not Bar Crawl-specific action labels; Darkan’s source handlers
supply that semantic connection. All ten drinks and all ten prices are
recovered from the pinned Darkan source, but no drink inventory ID is recovered
or claimed. `game-main` corroborates card 455 and several bartender coordinates
but provides no Bar Crawl implementation.

## Tool notes

Two bounded-search pitfalls occurred and were contained without modifying a
source tree: a delegated search escaped its requested directory and was
terminated, and build 652’s newer-core full item scan failed on the exact error
above. A shell retry also initially used zsh’s read-only special parameter
`status`; the successful rerun used `rc`. These do not affect the positive
rev727/rev742 decoder results recorded here.
