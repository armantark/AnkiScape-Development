# Dungeoneering mechanical-completion harvest

Date: `2026-07-28`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Scope: the owner-ratified Frozen solo starter expedition, plus the progression,
binding, Ring of Kinship, reward, door, and payout ladders that must be exact
from the first implementation. This audit supersedes the source-blocked notes in
`dungeoneering-starter-harvest-2026-07-20.md` where the later Darkan restoration
closed a rule, and preserves the block where it did not.

Status: **complete for mechanical completion with nine named placeholder
candidates.** No owner decision is open.

## Provenance keys

Darkan server root below is
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/`.
The Dungeoneering package is byte-unchanged between restoration commit
`e1cf61bf26ffdda8d1e08437af3c79c021f7c880` and the inspected `dev` tree.

| key | provenance | classification |
| --- | --- | --- |
| `R1` | `src/main/java/com/rs/game/content/skills/dungeoneering/DungeoneeringRules.java:7-90`, commit `e1cf61bf2` | **restored and source-qualified**: floor bands, level rule, fixed complexity penalties, prestige maximum, same-theme substitution shape, base-XP averaging; exact lower-floor search direction remains unresolved |
| `R2` | `src/main/java/com/rs/game/content/skills/dungeoneering/DungeonManager.java:1343-1377`, commit `e1cf61bf2` | **restored call sites**: fixed complexity, substitution/scoring, average, `floor(final XP / 10)` token award |
| `L1` | `src/main/java/com/rs/game/content/skills/dungeoneering/DungeonConstants.java:275-305`; `DungeonManager.java:1296-1420` | **legacy Darkan** completion coefficients and active-floor XP curve; not source-qualified by `e1cf61bf2` |
| `L2` | `src/main/java/com/rs/game/content/skills/dungeoneering/DungeonUtils.java:42-74`; `DungeonConstants.java:73-75` | **legacy Darkan** bind recognition and active-bind ladder |
| `L3` | `src/main/java/com/rs/game/content/skills/dungeoneering/KinshipPerk.java:19-39`; `DungManager.java:48` | **legacy Darkan**, independently matched to the period class/cost table |
| `L4` | `src/main/java/com/rs/game/content/skills/dungeoneering/DungeonConstants.java:79-96,166-275,444-590,659-850` | **legacy Darkan** room, skill-door, key, door-type, puzzle, and Frozen boss-room rosters |
| `L5` | `DungeonManager.java:250-252,949-1013,1062-1077`; `npcs/DungeonNPC.java:41-123`; `game/model/entity/npc/combat/NPCCombatDefinitions.java:289-306`; Frozen combatdefs under `data/npcs/combatdefs/uncategorized/` | **legacy Darkan** dynamic boss selection/stat model; internally contradictory and therefore placeholder-only |
| `L6` | `src/main/java/com/rs/game/content/skills/dungeoneering/DungeonRewards.java:86-123` | **legacy Darkan**, independently matched to the period reward catalog for every row it contains |
| `L7` | `src/main/java/com/rs/game/content/skills/dungeoneering/DungeonResourceShop.java:27-101` | **legacy Darkan** Smuggler shop routing and price arithmetic |
| `C1` | rev-727 and rev-742 cache enums `2987-2994` plus their item definitions; exact byte-for-byte decoded match on the inspected rows | period client stock identities, item values, and Dungeoneering price multipliers |
| `W1` | `Dungeoneering` oldid `6579699`, 2012-11-19T02:31:37Z | 60 floors, `2f-1`, sizes, binds/ammo, payout order, token ratio, death respawn |
| `W2` | `Dungeoneering floors` oldid `6542025`, 2012-11-08T00:49:39Z | six floor bands and level bands |
| `W3` | `Dungeoneering/Prestige` oldid `6516987`, 2012-11-01T21:57:13Z | `max(current, previous)`, same-theme replay, active/prestige average |
| `W4` | `Complexity` oldid `6555542`, 2012-11-14T19:37:17Z | C1-C6 feature groups, shop gates, skill-door gate, `50/45/40/35/30/0%` |
| `W5` | `Ring of kinship/Classes` oldid `6521933`, 2012-11-03T01:29:00Z | 12 classes and all ten token costs |
| `W6` | `Dungeoneering/Bosses` oldid `6398065`, 2012-10-14T01:46:52Z | Frozen boss roster and floor/level gates |
| `W7` | `Dungeoneering/Doors` oldid `6325508`, 2012-09-30T17:22:57Z | door semantics, feasible critical path, skill-door XP `required level × 5` |
| `W8` | `Daemonheim Rewards` oldid `6297239`, 2012-09-25T21:01:33Z | full reward catalog and token costs |
| `W9` | `Coal bag` oldid `6283103`, 2012-09-22T22:36:07Z | 4,000-token proof purchase, level gates, capacity and behavior |
| `W10` | `Dungeoneering/Fishing` oldid `5812989`, 2012-06-23T16:17:51Z; `Dungeoneering/Cooking` oldid `6457563`, 2012-10-23T01:30:20Z | Raw heim crab and Heim crab proof chain |
| `W11` | `Dungeoneering/Herblore` oldid `6555616`, 2012-11-14T20:45:41Z | Valerian/Weak ranged proof chain and C5 gate |
| `W12` | `Smuggler` oldid `6564954`, 2012-11-17T04:36:56Z | Smuggler role and in-floor closed economy |
| `W13` | `Pay-to-play Dungeoneering training` oldid `6552419`, 2012-11-13T18:52:00Z | death modifier bounded between 4% and 70%; at most 15 deaths count |
| `W14` | `Dungeoneering/Winterface` oldid `6542576`, 2012-11-08T05:06:24Z | completion modifiers add into one total modifier, then apply to base XP |
| `W15` | `Dungeoneering keys` oldid `5906279`, 2012-07-08T11:18:19Z | 63 obtainable keys; Gold shield key removed shortly after release |
| `W16` | `Dungeoneering/Puzzles` oldid `6565589`, 2012-11-17T08:34:30Z | period puzzle roster for the later full Frozen pass |

## What the Darkan restoration thread already source-qualified

Commit `e1cf61bf2` restored only the shared floor-progression seam. Its frozen
target contract at
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/dungeoneering-floor-tiers-target-contract.json:125-137`
qualifies exactly:

- six floor bands covering floors 1-60;
- floor requirement `(floor × 2) - 1` and party floor ceiling;
- fixed complexity penalties `50/45/40/35/30/0%`;
- prestige `max(current progress, previous progress)`;
- same-theme substitution, preferring an incomplete lower floor before a higher one, and lower-floor scoring; the period pages do not settle whether multiple incomplete lower floors are searched lowest-first or nearest-first;
- `(active floor XP + prestige floor XP) / 2` before completion modifiers; and
- tokens `floor(final Dungeoneering XP / 10)`.

The same contract explicitly leaves the numeric active/prestige floor-XP
function and the room, level, guide, party-difficulty, death, and other
completion coefficients source-blocked. Therefore
`memory-bank/breadth-next-tranche.md:30` overstates the restoration when it says
`e1cf61bf2` supplies the floor-XP curve and death coefficient. It does not. The
legacy candidates are recorded below as placeholders, not historical facts.

## 1. All 60 floors and authentic size choices

Every floor uses requirement `2f-1`. Small and Medium are available to a solo
player; Large requires at least three players. The owner-ratified starter is a
**Small solo Frozen** floor even though Medium is an authentic solo choice.
Source on every row: `R1 + W1 + W2`.

| floor | theme | required Dungeoneering | authentic size choice |
| ---: | --- | ---: | --- |
| 1 | Frozen | 1 | Small or Medium solo; Large with 3+ players |
| 2 | Frozen | 3 | Small or Medium solo; Large with 3+ players |
| 3 | Frozen | 5 | Small or Medium solo; Large with 3+ players |
| 4 | Frozen | 7 | Small or Medium solo; Large with 3+ players |
| 5 | Frozen | 9 | Small or Medium solo; Large with 3+ players |
| 6 | Frozen | 11 | Small or Medium solo; Large with 3+ players |
| 7 | Frozen | 13 | Small or Medium solo; Large with 3+ players |
| 8 | Frozen | 15 | Small or Medium solo; Large with 3+ players |
| 9 | Frozen | 17 | Small or Medium solo; Large with 3+ players |
| 10 | Frozen | 19 | Small or Medium solo; Large with 3+ players |
| 11 | Frozen | 21 | Small or Medium solo; Large with 3+ players |
| 12 | Abandoned I | 23 | Small or Medium solo; Large with 3+ players |
| 13 | Abandoned I | 25 | Small or Medium solo; Large with 3+ players |
| 14 | Abandoned I | 27 | Small or Medium solo; Large with 3+ players |
| 15 | Abandoned I | 29 | Small or Medium solo; Large with 3+ players |
| 16 | Abandoned I | 31 | Small or Medium solo; Large with 3+ players |
| 17 | Abandoned I | 33 | Small or Medium solo; Large with 3+ players |
| 18 | Furnished | 35 | Small or Medium solo; Large with 3+ players |
| 19 | Furnished | 37 | Small or Medium solo; Large with 3+ players |
| 20 | Furnished | 39 | Small or Medium solo; Large with 3+ players |
| 21 | Furnished | 41 | Small or Medium solo; Large with 3+ players |
| 22 | Furnished | 43 | Small or Medium solo; Large with 3+ players |
| 23 | Furnished | 45 | Small or Medium solo; Large with 3+ players |
| 24 | Furnished | 47 | Small or Medium solo; Large with 3+ players |
| 25 | Furnished | 49 | Small or Medium solo; Large with 3+ players |
| 26 | Furnished | 51 | Small or Medium solo; Large with 3+ players |
| 27 | Furnished | 53 | Small or Medium solo; Large with 3+ players |
| 28 | Furnished | 55 | Small or Medium solo; Large with 3+ players |
| 29 | Furnished | 57 | Small or Medium solo; Large with 3+ players |
| 30 | Abandoned II | 59 | Small or Medium solo; Large with 3+ players |
| 31 | Abandoned II | 61 | Small or Medium solo; Large with 3+ players |
| 32 | Abandoned II | 63 | Small or Medium solo; Large with 3+ players |
| 33 | Abandoned II | 65 | Small or Medium solo; Large with 3+ players |
| 34 | Abandoned II | 67 | Small or Medium solo; Large with 3+ players |
| 35 | Abandoned II | 69 | Small or Medium solo; Large with 3+ players |
| 36 | Occult | 71 | Small or Medium solo; Large with 3+ players |
| 37 | Occult | 73 | Small or Medium solo; Large with 3+ players |
| 38 | Occult | 75 | Small or Medium solo; Large with 3+ players |
| 39 | Occult | 77 | Small or Medium solo; Large with 3+ players |
| 40 | Occult | 79 | Small or Medium solo; Large with 3+ players |
| 41 | Occult | 81 | Small or Medium solo; Large with 3+ players |
| 42 | Occult | 83 | Small or Medium solo; Large with 3+ players |
| 43 | Occult | 85 | Small or Medium solo; Large with 3+ players |
| 44 | Occult | 87 | Small or Medium solo; Large with 3+ players |
| 45 | Occult | 89 | Small or Medium solo; Large with 3+ players |
| 46 | Occult | 91 | Small or Medium solo; Large with 3+ players |
| 47 | Occult | 93 | Small or Medium solo; Large with 3+ players |
| 48 | Warped | 95 | Small or Medium solo; Large with 3+ players |
| 49 | Warped | 97 | Small or Medium solo; Large with 3+ players |
| 50 | Warped | 99 | Small or Medium solo; Large with 3+ players |
| 51 | Warped | 101 | Small or Medium solo; Large with 3+ players |
| 52 | Warped | 103 | Small or Medium solo; Large with 3+ players |
| 53 | Warped | 105 | Small or Medium solo; Large with 3+ players |
| 54 | Warped | 107 | Small or Medium solo; Large with 3+ players |
| 55 | Warped | 109 | Small or Medium solo; Large with 3+ players |
| 56 | Warped | 111 | Small or Medium solo; Large with 3+ players |
| 57 | Warped | 113 | Small or Medium solo; Large with 3+ players |
| 58 | Warped | 115 | Small or Medium solo; Large with 3+ players |
| 59 | Warped | 117 | Small or Medium solo; Large with 3+ players |
| 60 | Warped | 119 | Small or Medium solo; Large with 3+ players |

### Size geometry

| size | grid | maximum rooms | minimum party | source |
| --- | ---: | ---: | ---: | --- |
| Small | 4×4 | 16 | 1 | `L1` (`DungeonConstants.java:299-304`) + `W1` |
| Medium | 4×8 | 32 | 1 | `L1` + `W1` |
| Large | 8×8 | 64 | 3 | `L1` + `W1` |

The starter's eight-review Small-floor budget remains
`provisional/owner-approved-review-translation` from the closed design contract.
It is not a RuneScape room count and therefore is not a placeholder for a period
number.

## 2. Complexity 1-6

Each tier includes every feature of the previous tier. Slayer participates at
all complexities and is more common at C6. Source on every penalty and feature
row: `R1 + W4`; shop availability is also wired in legacy Darkan at
`DungeonResourceShop.java:28-55`.

| complexity | newly enabled content | Smuggler / rooms | XP penalty | completion multiplier |
| ---: | --- | --- | ---: | ---: |
| 1 | Attack, Constitution, Defence, Magic, Prayer, Ranged, Strength; starter weapons and armour supplied | shop closed; guide mode forced; no skill doors or challenge rooms | 50% | 0.50 |
| 2 | Cooking, Firemaking, Fishing, Woodcutting | minimal shop | 45% | 0.55 |
| 3 | Mining, Runecrafting, Smithing weapons | expanded shop | 40% | 0.60 |
| 4 | Farming textiles, Hunter, Smithing armour | expanded shop | 35% | 0.65 |
| 5 | Farming seeds, Herblore, Thieving, Construction, Summoning | full shop; skill doors and challenge rooms enabled | 30% | 0.70 |
| 6 | same skill set as C5; puzzles far more common | full shop | 0% | 1.00 |

The period table does not place Agility, Crafting, or Fletching in a separate
complexity unlock row. They remain real Daemonheim skills, and their skill-door
families appear only when skill doors become available at C5+.

## 3. Prestige, floor XP, completion modifiers, and tokens

### Period-closed payout order

Source: `R1 + R2 + W1 + W3`.

1. `prestige = max(current progress, previous progress)`.
2. A replayed floor ticks an incomplete lower floor in the same theme first,
   otherwise an incomplete higher floor. Scoring uses the lower of the completed
   and substituted floors. An exhausted theme gets prestige XP `0`. The source
   does not settle lowest-first versus nearest-lower-first when several lower
   floors are incomplete.
3. `base XP = (active-floor XP + prestige-floor XP) / 2`.
4. Penalties and bonuses add into one total modifier and operate on that base XP,
   not on active-floor XP alone (`W14`).
5. `tokens = floor(final Dungeoneering XP / 10)`.

The one-token-per-ten-XP rule is explicitly stated in `W1` and `W8` and is wired
at `DungeonManager.java:1374-1382`.

### Legacy Darkan candidate arithmetic — not period-qualified

The current server executes the following, all from `L1`:

| component | legacy value |
| --- | --- |
| active/prestige floor curve | `0.16f³ + 0.28f² + 76.94f + 100`, then multiply by size scale and opened-room fraction, truncate to integer |
| floor-XP size scale | Small `1.0`, Medium `2.0`, Large `3.5` |
| opened-room fraction | opened rooms divided by `16/32/64` for Small/Medium/Large |
| completion size bonus | Small `0`, Medium `+0.0792`, Large `+0.1583` |
| bonus-room bonus | `+0.1267 × opened bonus rooms / non-critical rooms` |
| level modifier | guardian kill percentage `p` becomes `(20p - 1000) / 10000`, therefore `-10%` at `0%`, `0` at `50%`, `+10%` at `100%` |
| guide mode | `-0.05` |
| complexity | subtract the exact `0.50/0.45/0.40/0.35/0.30/0.00` |
| death | multiply the whole completion multiplier by `1 - 0.10 × min(deaths, 6)`; contradicted by the period 15-death cap and additive modifier rule |
| floor | clamp the combined multiplier to at least `0.10` |

Only the complexity row and the payout order are period-closed. The rest are
placeholder candidates below. The legacy party-difficulty matrix is not pinned
for the starter because party simulation is parked; it also contains a suspicious
`0.95` three-player cell at `DungeonConstants.java:283` and must not be copied.

## 4. Binding ladder and ammo/rune slot

Source on every row: `L2 + W1`. The legacy Darkan ladder matches the period
article exactly.

| Dungeoneering level | active bound items |
| ---: | ---: |
| 1 | 1 |
| 20 | 2 |
| 50 | 3 |
| 90 | 4 |
| 120 | 5 |

Additional exact rules:

- A player may collect up to **10** bound items and configure **3** loadouts,
  but only the level-gated number above is active on a floor (`W1`).
- One ammo/rune bind is separate and consumes no active-item slot. It may be one
  arrow stack, one rune stack, a magical blastbox, or a celestial surgebox
  (`DungeonUtils.java:42-51`; `DungeonConstants.java:73-75`; `W1`).
- The cap is **125** units, or **225** after `Salt in the Wound` (`W1`).
- Ammo replenishes to the bound quantity at each floor. Unbinding an ordinary
  item destroys it. Bound items cannot be traded, sold, or alchemised (`W1`).

## 5. Ring of Kinship classes and costs

The enum order, role grouping, and cost array are legacy Darkan but match the
period table exactly (`L3 + W5`). One class is active while worn.

| category | classes |
| --- | --- |
| Melee | Tank, Tactician, Berserker |
| Ranged | Sniper, Keen-eye, Desperado |
| Magic | Blazer, Blaster, Blitzer |
| Skiller | Medic, Gatherer, Artisan |

| target tier | token cost | cumulative cost | source |
| ---: | ---: | ---: | --- |
| 1 | 135 | 135 | `DungManager.java:48` + `W5` |
| 2 | 175 | 310 | `DungManager.java:48` + `W5` |
| 3 | 335 | 645 | `DungManager.java:48` + `W5` |
| 4 | 660 | 1,305 | `DungManager.java:48` + `W5` |
| 5 | 1,360 | 2,665 | `DungManager.java:48` + `W5` |
| 6 | 3,400 | 6,065 | `DungManager.java:48` + `W5` |
| 7 | 6,800 | 12,865 | `DungManager.java:48` + `W5` |
| 8 | 18,750 | 31,615 | `DungManager.java:48` + `W5` |
| 9 | 58,600 | 90,215 | `DungManager.java:48` + `W5` |
| 10 | 233,000 | 323,215 | `DungManager.java:48` + `W5` |

All twelve classes cost `3,878,580` tokens in total (`12 × 323,215`), matching
the period page's stated total. Exact class effects are outside this harvest:
the contract requires class choice and authentic tier metaprogression here, not
all twelve automation-effect curves.

## 6. Frozen room and boss roster

### Starter room families

The closed starter contract requires exactly six gameplay families. Darkan's
legacy room package supplies the period-shaped substrate; the AnkiScape review
budget remains the disclosed translation.

| starter family | pinned Darkan/period shape | source |
| --- | --- | --- |
| Start | four Frozen start layouts; Smuggler, supplies, return point | `DungeonConstants.java:444-450`; `W1`; `W12` |
| Guardian | one of 108 normal layouts with a guardian door; 13 Frozen guardian-monster families are cache-confirmed | `DungeonConstants.java:335-364,452-590`; `DoorType.GUARDIAN` at `:275`; rev-742; `W7` |
| Key | normal room with one of 64 shipped key/door definitions, of which 63 are drawable in period play | `DungeonConstants.java:166-275`; rev-742; `W1`; `W7`; `W15` |
| Skill | normal room with one of 15 period skill-door families at C5+; Darkan has Frozen object ids for nine and `-1` for six | `DungeonConstants.java:81-161`; `W4`; `W7` |
| Resource | normal room with Daemonheim gathering/crafting resources | `DungeonConstants.java:452-590`; proof chains in `W10/W11` |
| Boss | one of the six floor-gated Frozen bosses below | `DungeonConstants.java:825-850`; `W6` |

The legacy package has 108 normal layouts, 10 implemented puzzle kinds expanded
across seven door configurations, and nine of those puzzle kinds available on
Frozen: Crystal puzzle, Toxin maze, Flip tiles, Fremennik camp, Fishing ferret,
Levers, Sliding statues, Unhappy ghost, and Return the flow
(`DungeonConstants.java:452-590,671-733,764-771`). Poltergeist is explicitly
excluded from Frozen; Flower roots, Coloured recess, and Sliding tiles are
disabled. The period Frozen-specific Icy Pressure Pad is present only as a TODO
comment at `DungeonConstants.java:780-783`. The full period Frozen puzzle roster
is deferred to `W16`; puzzle identity is content and must not be fabricated or
hidden behind a numeric placeholder. It is not needed by the starter's settled
six-family roster.

### Frozen boss gates

Boss names and gates are period-closed by `W6`; the room entries and NPC series
are legacy Darkan `L4/L5`.

| boss | Dungeoneering gate | eligible floors | Darkan NPC combat-level variants |
| --- | ---: | --- | --- |
| Gluttonous Behemoth | 1 | 1-11 | 5, 25, 41, 63, 91, 132, 170, 199, 238, 278, 299, 334, 362, 389, 437, 476, 518 |
| Astea Frostweb | 1 | 1-11 | 3, 5, 8, 16, 26, 43, 71, 97, 116, 134, 155, 189, 221, 253, 287, 331, 378, 435, 496 |
| Icy Bones | 1 | 1-11 | 5, 14, 23, 32, 41, 56, 71, 95, 124, 154, 188, 220, 258, 297, 340, 384, 429, 474 |
| Luminescent icefiend | 5 | 3-11 | 3, 7, 19, 40, 61, 77, 95, 124, 162, 197, 235, 274, 314, 362, 393, 423, 456 |
| Plane-freezer Lakhrahnaz | 11 | 6-11 | 7, 17, 25, 35, 57, 76, 104, 140, 174, 203, 233, 262, 293, 329, 362, 393, 424, 455, 491 |
| To'Kash the Bloodchiller | 17 | 9-11 | 8, 22, 49, 67, 104, 127, 159, 188, 216, 255, 292, 355, 408, 442, 477, 512 |

### Darkan combat-level/stat/LP conflicts

The NPC id blocks are confirmed by rev 742, but the cache tool does not expose
combat level. Darkan's dumped level ladders conflict with pinned boss pages above
the mid tiers for To'Kash and Luminescent icefiend, and Gluttonous Behemoth's
period wikitext records a rebalance. Plane-freezer Lakhrahnaz has a separate
Darkan defect: it has no dispatch branch at `DungeonManager.java:951-1013`, so
runtime always spawns fixed level-7 id 9929 instead of selecting from its
19-variant block.

Darkan also does not contain authentic fixed stat blocks for these bosses:

- every inspected Frozen combatdef is named `(nostats)` and carries the same
  placeholder `5,000` lifepoints and `50` maximum hit regardless of combat
  level;
- runtime ignores those two figures for the general boss model. It selects the
  variant closest to `1.5 × party average combat level`
  (`DungeonManager.java:250-252`), then `DungeonNPC.java:74-123` replaces
  lifepoints with `25 × combat level + 1`, maximum hit with `combat level`, and
  all five combat stats with the generated formula at
  `NPCCombatDefinitions.java:293-306`, clamped to `120` for bosses. The
  Luminescent Icefiend combat script is an exception that reads the placeholder
  maximum hit.

That makes the effective legacy lifepoint ranges:

| boss | legacy effective LP range | configured combatdef LP/max hit | source |
| --- | ---: | --- | --- |
| Gluttonous Behemoth | 126-12,951 | 5,000 / 50, no stats | `L5` |
| Astea Frostweb | 76-12,401 | 5,000 / 50, no stats | `L5` |
| Icy Bones | 126-11,851 | 5,000 / 50, no stats | `L5` |
| Luminescent icefiend | 76-11,401 | 5,000 / 50, no stats | `L5` |
| Plane-freezer Lakhrahnaz | 176-12,276 | 5,000 / 50, no stats | `L5` |
| To'Kash the Bloodchiller | 201-12,801 | 5,000 / 50, no stats | `L5` |

Neither side of that contradiction is safe to call period-accurate. The runtime
shape is the mechanical placeholder candidate below; the configured `5,000/50`
rows must not be copied as facts.

## 7. Door, key, and skill-door families

### Door types

Darkan's legacy enum has five procedural types: `NORMAL`, `GUARDIAN`, `SKILL`,
`CHALLENGE`, and `KEY` (`DungeonConstants.java:275`). Rev 742 separately names
Frozen object 50350 `Boss door [Enter]`, so Boss is a real client object family
even though Darkan models it as a boss-room property rather than a `DoorType`.
The period `W7` article groups these more coarsely into Basic doors (plain,
guardian, colour/shape key) and Skill doors; that is documentation taxonomy, not
evidence that the boss object was absent.

### Keys

The client ships **64** key/door definitions: eight colours crossed with eight
shapes (`DungeonConstants.java:166-230`; rev-742 objects 50208-50271 and items
18202-18329). Period play has **63 obtainable keys** because the Gold shield key
was removed shortly after release (`W15`). Ship all 64 definitions so old assets
and door identity remain stable, but never draw Gold shield as a key reward.

- Colours: Orange, Silver, Yellow, Green, Blue, Purple, Crimson, Gold.
- Shapes: Triangle, Diamond, Rectangle, Pentagon, Corner, Crescent, Wedge,
  Shield.
- Marker object is `50208 + index`; Frozen door is `50353 + index`; the key item
  is `18202 + index × 2`. Rev 742 confirms each key name occupies two consecutive
  item ids, which explains the stride of two.
- Keys are party-shared after the April 2012 update (`W1`).

### Skill doors

All 15 legacy Darkan families correspond to period Daemonheim skill-door kinds.
They become available at C5+ and award `required level × 5` skill XP (`W4/W7`).
Darkan adds an unsourced `+10` and must not be followed. The Frozen object column
below is Darkan's theme array, not an independently proven period exclusion.

| door family | skill | Frozen object | source |
| --- | --- | ---: | --- |
| Runed door | Runecrafting | 50278 | `DungeonConstants.java:82` + rev-742 + `W7` |
| Barred door | Strength | 50272 | `:83` + rev-742 + `W7` |
| Pile of rocks | Mining | 50305 | `:84` + rev-742 + `W7` |
| Flammable debris | Firemaking | 50314 | `:85` + rev-742 + `W7` |
| Magical barrier | Magic | 50329 | `:86` + rev-742 + `W7` |
| Dark spirit | Prayer | 50332 | `:87` + rev-742 + `W7` |
| Wooden barricade | Woodcutting | 50317 | `:88` + rev-742 + `W7` |
| Broken key door | Smithing | 50308 | `:89` + rev-742 + `W7` |
| Broken pulley door | Crafting | 50299 | `:90` + rev-742 + `W7` |
| Locked door | Agility | — | `:91` + `W7`; Frozen exclusion source-blocked |
| Padlocked door | Thieving | — | `:92` + `W7`; Frozen exclusion source-blocked |
| Ramokee exile | Summoning | — | `:93` + `W7`; Frozen exclusion source-blocked |
| Liquid lock | Herblore | — | `:94` + `W7`; Frozen exclusion source-blocked |
| Vine-covered door | Farming | — | `:95` + `W7`; Frozen exclusion source-blocked |
| Collapsing doorframe | Construction | — | `:96` + `W7`; Frozen exclusion source-blocked |

The critical path is generated to be level-feasible; bonus doors may exceed the
player's level. The period record states that failure can deal
moderate-to-severe damage but does not state the failure probability or damage
magnitude. Legacy Darkan uses an 11% failure chance and `required level × 4`
true damage; those two numbers are the placeholder candidate below, not period
facts. The six Darkan-only Frozen exclusions are content gates, not numeric
placeholders: the starter may use the nine attested Frozen-object families while
the other six remain source-blocked.

## 8. Death penalty

The period rule is closed in shape and bounds: death respawns the player in the
start room, preserves the floor, increments the death count, and reduces the
end-of-floor payout (`W1`). The only period numeric statement says the penalty
lies between **4% and 70%**, and that at most **15 deaths** count (`W13`). The
15-death cap is also corroborated by `W1` and `W6` trivia. No period source gives
the per-death increments or the first-death value.

`W14` settles combination order: all completion modifiers add into one total
modifier, which is then applied to base XP. Death is therefore an additive
penalty term in the period completion modifier. Legacy Darkan instead applies
**10% per death**, caps at **six**, and multiplies it against the already-combined
modifier (`DungeonManager.java:1349-1351`). That is contradicted on both cap and
combination order and must not be used as the placeholder. The placeholder must
stay within the period 4%-70% / 15-death bounds until an exact curve is found.

## 9. Reward trader catalog and staging

Every cost below is period-pinned by `W8`; Darkan rows are independently matched
at `L6`. Rows absent from Darkan are still exact because the period catalog
states them directly. The Coal bag row is additionally pinned by `W9`.

Staging is settled: **Coal bag is the proof purchase. Every other row stays
hidden until its mechanic is fully functional.**

| reward | token cost | Dungeoneering requirement | other stated requirement | stage/source |
| --- | ---: | ---: | --- | --- |
| Dungeoneering XP lamp | 1 | — | converts tokens to Dungeoneering XP at 1:1 | later; `W8` |
| Gem bag | 2,000 | 25 | — | later; `L6 + W8` |
| **Coal bag** | **4,000** | **35** | Mining 35; one owned; holds 27 Coal | **proof purchase; `L6 + W8 + W9`** |
| Arcane pulse necklace | 6,500 | 30 | — | later; `L6 + W8` |
| Twisted bird skull necklace | 8,500 | 30 | — | later; `L6 + W8` |
| Scroll of life | 10,000 | 25 | — | later; `L6 + W8` |
| Longbow sight | 10,000 | 45 | — | later; `L6 + W8` |
| Law staff | 10,000 | 45 | Magic 45 | later; `W8` |
| Nature staff | 12,500 | 53 | Magic 53 | later; `W8` |
| Arcane blast necklace | 15,500 | 50 | — | later; `L6 + W8` |
| Split dragontooth necklace | 17,000 | 60 | — | later; `L6 + W8` |
| Scroll of cleansing | 20,000 | 49 | — | later; `L6 + W8` |
| Scroll of efficiency | 20,000 | 55 | — | later; `L6 + W8` |
| Arcane stream necklace | 30,500 | 70 | — | later; `L6 + W8` |
| Bonecrusher | 34,000 | 21 | — | later; `L6 + W8` |
| Herbicide | 34,000 | 21 | — | later; `L6 + W8` |
| Demon horn necklace | 35,000 | 90 | — | later; `L6 + W8` |
| Amulet of zealots | 40,000 | 48 | — | later; `L6 + W8` |
| Gravite rapier | 40,000 | 45 | — | later; `L6 + W8` |
| Gravite longsword | 40,000 | 45 | — | later; `L6 + W8` |
| Gravite two-handed sword | 40,000 | 45 | — | later; `L6 + W8` |
| Gravite staff | 40,000 | 45 | — | later; `L6 + W8` |
| Gravite shortbow | 40,000 | 45 | — | later; `L6 + W8` |
| Magical blastbox | 40,000 | 30 | Magic 30, Runecrafting 30 | later; `W8` |
| Tome of frost | 43,000 | 48 | — | later; `L6 + W8` |
| Anti-poison totem | 44,000 | 60 | — | later; `L6 + W8` |
| Spirit cape | 45,000 | 50 | — | later; `L6 + W8` |
| Mercenary's gloves | 48,500 | 73 | — | later; `L6 + W8` |
| Ring of vigour | 50,000 | 62 | — | later; `L6 + W8` |
| Celestial surgebox | 65,000 | 70 | Magic 70, Runecrafting 70 | later; `W8` |
| Sneakerpeeper | 85,000 | 80 | — | later; `L6 + W8` |
| Scroll of renewal | 107,000 | 65 | — | later; `L6 + W8` |
| Scroll of rigour | 140,000 | 74 | — | later; `L6 + W8` |
| Scroll of augury | 153,000 | 77 | — | later; `L6 + W8` |
| Chaotic rapier | 200,000 | 80 | — | later; `L6 + W8` |
| Chaotic longsword | 200,000 | 80 | — | later; `L6 + W8` |
| Chaotic maul | 200,000 | 80 | — | later; `L6 + W8` |
| Chaotic staff | 200,000 | 80 | — | later; `L6 + W8` |
| Chaotic crossbow | 200,000 | 80 | — | later; `L6 + W8` |
| Chaotic kiteshield | 200,000 | 80 | — | later; `L6 + W8` |
| Eagle-eye kiteshield | 200,000 | 80 | — | later; `L6 + W8` |
| Farseer kiteshield | 200,000 | 80 | — | later; `L6 + W8` |

The Coal bag's 4,000-token cost is therefore verified twice and is not a
placeholder.

## 10. Smuggler shop and starter resource chains

### Shop gates and stock bands

Legacy Darkan selects paired cache enums by complexity at
`DungeonResourceShop.java:27-60`. A direct decode of rev 727 and the independent
near-cutoff rev 742 produced identical rows.

| complexity | item enums | rows | exact starter-relevant stock | source |
| ---: | --- | ---: | --- | --- |
| 1 | none | 0 | shop closed | `L7 + W4` |
| 2 | 2989 + 2990 | 4 | Raw heim crab 200 coins; Tangle gum branches 225; Feather 6; Antipoison 200 | `L7 + C1` |
| 3 | 2991 + 2992 | 19 | low ores, fish, branches, essence, basic weapons, arrows, bow string, feather, antipoison | `L7 + C1` |
| 4 | 2993 + 2994 | 26 | adds low textiles/hides and broader basic equipment | `L7 + C1` |
| 5-6 | 2987 + 2988 | 86 | full ten-tier ore/textile/hide/fish/branch rows, seeds, essence, five arrow tiers, four Herblore secondaries, basic equipment and supplies | `L7 + C1 + W4` |

Buy price is exactly
`item cache value × Dungeoneering shop multiplier`, truncated to an integer
(`DungeonResourceShop.java:56-78`; `C1`). For the quarantined proof chain, full
stock includes Valerian seed at **3,000** coins, Void dust at **1,000**, and a
Vial at **10** (`C1`, enums 2987-2988). The legacy 30% sell-back coefficient is
not independently period-qualified and remains a placeholder below. Keys,
bound items, rusty coins, Rings of Kinship, and gatestones cannot be sold
(`DungeonResourceShop.java:81-101`).

### Gathering proof chain: Raw heim crab -> Heim crab

| step | level | XP | result | minimum complexity | source |
| --- | ---: | ---: | --- | ---: | --- |
| Catch Raw heim crab | Fishing 1 | 9 | 1 Raw heim crab | 2 | `W10`; item 17797 in `C1` |
| Cook Heim crab | Cooking 1 | 22 | 1 Heim crab, heals 20 LP | 2 | `W10` |

This is the starter's one gathering/cooking chain. Nothing leaves the floor.

### Quarantined Herblore proof chain

Herblore requires C5+ and Druidic Ritual in the period (`W11`). The full
54-target quarantine remains owned by the Herblore family; the starter needs the
one independently reconciled chain below.

| step | level | XP | inputs | output | source |
| --- | ---: | ---: | --- | --- | --- |
| Clean valerian | Herblore 4 | 3.2 | Grimy valerian | Clean valerian | `W11` |
| Mix unfinished potion | Herblore 4 | 0 | Clean valerian + Vial of water | Valerian potion (unf) | `W11`; ingredient identity reconciled with game-main |
| Finish Weak ranged potion | Herblore 5 | 34 | Valerian potion (unf) + Void dust | Weak ranged potion | `W11`; Void dust item 17530 in `C1` |

The earlier Weak magic potion 21-versus-23 XP conflict is irrelevant to this
proof chain and remains outside the starter.

## Placeholder candidates

These are values the period game had but this harvest could not recover after
Darkan, all six local caches, game-main's bounded Dungeoneering search, and the
pinned period pages. The implementer should register these exact ids in
`memory-bank/placeholder-values.md` when code first uses them.

| proposed id | candidate value for mechanical completion | what it unblocks | what would settle it |
| --- | --- | --- | --- |
| `dungeoneering.floor_xp_curve` | legacy Darkan `truncate((0.16f³ + 0.28f² + 76.94f + 100) × size scale × opened/max rooms)`, size scales `1/2/3.5`, room maxima `16/32/64` | active and prestige floor-XP inputs | a period server routine, decoded completion script/table, or independently source-qualified restoration of `getFloorXP` |
| `dungeoneering.completion_modifiers` | legacy Darkan size bonus `0/0.0792/0.1583`, bonus-room cap `0.1267`, level modifier `-10%..+10%`, guide penalty `5%`, final multiplier floor `10%`; combine additively per `W14` | size, bonus-room, level-mod and guide rows on the completion screen | a period Winterface coefficient table or decoded server completion routine |
| `dungeoneering.death_xp_penalty_curve` | exact increments unknown; the placeholder must be an additive death term bounded by `4%-70%` across at most `15` counted deaths, never Darkan's multiplicative 10%-cap-6 rule | death-respawn payout reduction | a period server routine or decoded modifier table giving the first-death value and all increments |
| `dungeoneering.boss_combat_level_ladders` | the Darkan variant ladders printed in the boss table, explicitly provisional where To'Kash, Luminescent icefiend, and Gluttonous Behemoth conflict with period pages | tier selection for the six Frozen bosses | cache NPC combat-level decoding or a source-qualified restoration that reconciles the pinned boss revisions |
| `dungeoneering.boss_combat_definitions` | legacy dynamic fallback: LP `25 × combat level + 1`, max hit `combat level`, generated five-stat block clamped at 120; never the `(nostats)` 5,000/50 rows | lifepoints, maximum hit, Attack, Strength, Defence, Magic, and Ranged for all Frozen tiers | authentic per-tier combat definitions or a decoded period stat table |
| `dungeoneering.boss_level_scaling_formula` | legacy Darkan nearest tier to `1.5 × party average combat`; Lakhrahnaz's fixed-id defect must be bypassed | map player/party state to a boss tier | period server logic covering player level, complexity, and intended party size |
| `dungeoneering.skill_door_failure` | legacy Darkan 11% failure chance and `required level × 4` true damage, both explicitly provisional | failed skill-door outcomes | period server door handlers or a dated source stating probability and LP damage |
| `dungeoneering.floor_replay_substitution_direction` | restored Darkan lowest-unticked-lower-first; AnkiScape currently uses nearest-lower-first | deterministic replay credit when several lower floors are incomplete | a period server routine or dated worked example with multiple incomplete lower floors |
| `dungeoneering.smuggler_sellback_rate` | legacy Darkan `30%` of the cache-derived buy price | selling floor items back to the Smuggler | rev-742 CS2/server shop logic or a dated guide stating the sell-back fraction |

## Conflicts and defects the implementer must not silently inherit

- `e1cf61bf2` did **not** source-qualify the floor-XP curve or death coefficient;
  the restoration ledger says both remain blocked.
- Darkan's Frozen boss combatdefs all say `(nostats)` and carry identical
  `5,000/50` placeholders, while runtime replaces them with a different dynamic
  formula. Neither is historical proof. Several combat-level ladders also
  disagree with pinned boss pages, and Lakhrahnaz never enters the tier selector.
- Darkan's death rule is contradicted twice: period play counts up to 15 deaths,
  not six, and adds the death term into the total modifier rather than multiplying
  it against the other modifiers.
- The client contains 64 key assets, but period play has only 63 obtainable keys;
  Gold shield must remain defined but undrawable.
- Darkan adds `+10` to the sourced skill-door XP formula `required level × 5`.
  Do not copy the extra ten.
- Darkan and AnkiScape disagree on lowest-first versus nearest-lower-first replay
  substitution. The period prose does not arbitrate.
- Darkan's legacy three-player difficulty row contains `0.95` where the adjacent
  progression strongly suggests a decimal-place defect. Party simulation is
  parked, so the starter must not import it.
- Darkan lacks five period reward rows: Law staff, Nature staff, Magical
  blastbox, Celestial surgebox, and the one-token XP lamp. They are not
  placeholders because `W8` pins their identities and costs exactly.
- Darkan's Icy Pressure Pad is comment-only. The six-family starter does not need
  it, but a later full Frozen-puzzle pass must restore it instead of pretending
  the current puzzle enum is exhaustive.

## Owner decisions

None. The design is closed. The only unresolved work is source replacement for
the nine named placeholders above. The period record itself resolves Gold shield
as undrawable, death as additive with a 15-death cap, and skill-door XP as
`required level × 5`; none of those requires owner judgment.
