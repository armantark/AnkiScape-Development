# Phoenix Lair Breadth Implementation Source Audit

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **minimum mechanic-complete data slice pinned and implemented. Broader
guardian loot tables and hidden egg probability remain catalog-depth work.**

## Reused owner contract

The owner-settled review-native loop remains
`memory-bank/source-audits/phoenix-lair-loop-2026-07-18.md`: one persistent
aggregate guardian front, one pyre-preparation review, and one persistent
Phoenix encounter whose killing review completes the ritual atomically. This
audit supplies the smallest period-qualified data set needed to run that loop.

## Period activity and reward evidence

`Phoenix Lair`, oldid `6574295` (`2012-11-18T09:12:43Z`), establishes the
`In Pyre Need` and Slayer 51 gates; one completion per source day; five caverns
with one mandatory choke blocker and one twig each; knife, secateurs, and
tinderbox/toolbelt requirements; random Greater and Lesser Reborn variants;
non-respawning guardians; the preparation and Phoenix sequence; and the fixed
repeat reward of 7,500 Firemaking XP, 3,000 Fletching XP, 1,000 Crafting XP,
500 Slayer XP, and five Phoenix quills. The page also records the first-defeat
5,000 Slayer XP, possible egg reward, and level 72 Summoning hatch gate.

Source:

- <https://runescape.wiki/w/Phoenix_Lair?oldid=6574295>

`Phoenix`, oldid `6588809` (`2012-11-19T21:51:56Z`), pins level 235, 2,550 LP,
pure Magic attacks, approximate max hit 290, and the temporary Attack, Magic,
and Ranged dust drain. The page says the drained stats recover after a few
seconds but does not expose a stable attack frequency.

Source:

- <https://runescape.wiki/w/Phoenix?oldid=6588809>

## Minimum Reborn roster

The six period monster revisions provide the values used by the aggregate
front:

| Variant | oldid | Timestamp | Level | LP | Style | Approx. max hit |
|---|---:|---|---:|---:|---|---:|
| Lesser reborn warrior | `5882751` | `2012-07-04T17:40:12Z` | 100 | 960 | Melee | `source_blocked` |
| Greater reborn warrior | `5929109` | `2012-07-13T12:48:24Z` | 128 | 1,350 | Melee | 120 |
| Lesser reborn ranger | `6352235` | `2012-10-05T16:17:05Z` | 87 | 800 | Ranged | 110 |
| Greater reborn ranger | `6352812` | `2012-10-05T17:10:08Z` | 107 | 1,000 | Ranged | 130 |
| Lesser reborn mage | `6049792` | `2012-08-06T00:33:07Z` | 82 | 800 | Magic | 90 |
| Greater reborn mage | `6351801` | `2012-10-05T14:59:59Z` | 112 | 1,100 | Magic | 120 |

Sources:

- <https://runescape.wiki/w/Lesser_reborn_warrior?oldid=5882751>
- <https://runescape.wiki/w/Greater_reborn_warrior?oldid=5929109>
- <https://runescape.wiki/w/Lesser_reborn_ranger?oldid=6352235>
- <https://runescape.wiki/w/Greater_reborn_ranger?oldid=6352812>
- <https://runescape.wiki/w/Lesser_reborn_mage?oldid=6049792>
- <https://runescape.wiki/w/Greater_reborn_mage?oldid=6351801>

All six revisions list Ashes as the guaranteed drop. The breadth slice therefore
credits five Ashes when the five-blocker aggregate front is defeated. The
period pages contain larger drop catalogs with incomplete or qualitative
rarities; those tables are deferred rather than converted into invented rates.

## Cache identity and independent implementation convergence

OpenRS2 rev-742 cache definitions pin NPC IDs `8549` (Phoenix), `8557/8558`
(Lesser warrior), `8559/8560` (Greater warrior), `8561/8562` (Lesser ranger),
`8563/8564` (Greater ranger), `8565/8566` (Lesser mage), and `8567/8568`
(Greater mage). Item IDs are `14616` (Phoenix quill), `14629` (Phoenix egg),
and `14630` (Cracked phoenix egg). Cache evidence is used only for identity and
options.

Darkan commit `7907f0b5f` independently restores the Phoenix lifecycle and
fixed rewards; commit `ec85af3f2` binds its headless proof to controller-owned
actors. Relevant implementation paths are:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/dnds/phoenix/PhoenixLair.kt`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/dnds/phoenix/PhoenixLairState.kt`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/dnds/phoenix/PhoenixLairController.kt`

Darkan does not implement the egg reward and its guardian combat definitions
are incomplete, so neither is treated as proof of the hidden egg chance or a
full stat block.

## Declared bounded abstractions

The following are explicit AnkiScape abstractions, not historical claims:

1. Each run samples five blockers from the six period Reborn variants, one per
   mandatory cavern choke point, and combines their exact LP into one persistent
   front. The front rotates the sampled attack styles across reviews so the
   combat triangle remains mechanically present without simulating maps or
   background NPCs.
2. Full attack and defence stat blocks are absent from the period pages. The
   shared Combat reducer receives level-shaped values while period LP, style,
   and known approximate max hits remain exact. The Lesser warrior's unknown
   max hit uses a bounded 100-LP placeholder.
3. The Phoenix dust attack is represented every fifth Phoenix combat review;
   it halves current Attack, Magic, and Ranged, after which the ordinary
   review-driven Combat recovery dissipates the drain. No wall clock is stored.
4. The egg probability is `1/1000`. The period source proves only that the egg
   is possible and extremely rare; the numeric probability is therefore a
   labeled hidden-roll abstraction and remains source-blocked for parity.
5. One source day is the existing 240-answered-card AnkiScape world day.

## Egg choice and assets

`Phoenix egg`, oldid `4364298` (`2011-06-05T00:56:14Z`), pins Clap to the Cute
eggling and confirms the below-72 unhatched item. `Cracked phoenix egg`, oldid
`4362222` (`2011-06-04T23:46:16Z`), pins the Kick/Mean counterpart.

Sources:

- <https://runescape.wiki/w/Phoenix_egg?oldid=4364298>
- <https://runescape.wiki/w/Cracked_phoenix_egg?oldid=4362222>

The checked-in item sprites are fetched through
`tools/fetch_phoenix_lair_assets.py`; immutable fetch metadata and hashes live
in `assets_provenance.json`. The Phoenix quill is also the activity icon, matching
the existing reward-sprite convention. All three images pass the shared
transparent-padding normalizer in `tools/trim_icons.py`.

## Explicit omissions

- Exact full guardian stat blocks remain unavailable.
- Lesser reborn warrior max hit remains `source_blocked`.
- Non-Ashes guardian drop probabilities and quantities remain catalog depth.
- The historical Phoenix egg chance remains `source_blocked`; `1/1000` is the
  declared breadth abstraction.
- Exact source attack timing for the dust drain remains unavailable; the
  every-fifth-review cadence is review-native rather than historical timing.
