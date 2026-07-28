# Mage Training Arena source-readiness harvest

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **the period room economy, complete reward catalog, caps,
restrictions, death consequence, and three observational room-throughput
ranges are pinned; the horizontal implementation remains `source_blocked` on
Enchantment throughput and related server cadence. No owner-design question is
open.**

Implementation update `2026-07-27`: the later breadth-phase placeholder
amendment supersedes that parking decision. Breadth one now ships the four core
room loops and representative shop rows, with Enchantment throughput, the
falling-bone roll, the two reward-rune selectors, the maze-length distribution,
and the Alchemist casts/free-cast averages registered in
`memory-bank/placeholder-values.md`. Ordinary timed dragonstone spawns remain the
explicit design-thread fork `3.12`; exhaustive reward rows remain the requested
later catalog pass.

## Authority and scope

The owner-settled behavior remains
`memory-bank/source-audits/mage-training-arena-loop-2026-07-18.md`. This pass
does not alter its four-wallet economy, goal router, natural switching
checkpoints, Arena-wide approach, Graveyard death boundary, or wand chain. It
asks only whether the smallest honest four-room implementation can now satisfy
that contract's source-calibrated cadence requirement.

## Primary period record

The literal historical wikitext of `Mage Training Arena`, oldid `6491109`,
timestamp `2012-10-28T20:51:43Z`, establishes the cutoff room and shop model:

<https://runescape.wiki/w/Mage_Training_Arena?oldid=6491109>

- level 7 Magic admits the first Enchantment spell and level 33 admits all four
  rooms; a Progress hat is required;
- clue scrolls, caskets, and familiars are excluded; coins cannot enter the
  Alchemist room, and bananas and peaches cannot enter the Graveyard;
- Telekinetic mazes use seven to ten Law runes, award two points each, and
  award eight extra points, ten Law runes, and 1,000 Magic XP after every five
  completed mazes;
- Alchemist values rotate roughly every forty seconds, casts yield 1-30 coins,
  the indicated item sometimes casts free, and every 100 deposited coins pays
  one point, 200 Magic XP, and ten banked coins;
- in the cutoff Enchantment room a correct shape pays one base point, every
  tenth correct shape pays a bonus equal to the enchantment level, Magic XP is
  75% of the ordinary spell value, and every twentieth orb pays three runes;
- six Dragonstones appear every five minutes, each paying twice the
  enchantment level, but the owner contract excludes world-hopping the spawn;
- Graveyard bones repeat four each of values one, two, three, and four;
  falling bones deal 20 life points; sixteen deposited fruit pay one point and
  one reward rune; Bones to Peaches costs two Nature runes and heals 80 life
  points versus a banana's 20; and death returns the player to the lobby and
  removes ten Graveyard points without equipment loss; and
- the point caps are 4,000 Telekinetic, 8,000 Alchemist, 16,000 Enchantment,
  and 4,000 Graveyard.

The primary page mentions the Graveyard reward-rune set. Its equal weighting
appears only inside an explicitly hypothetical cost calculation, so the
weights remain unproven.

## Complete cutoff reward catalog

The four numeric columns are Telekinetic / Alchemist / Enchantment /
Graveyard points:

| Reward | Cost |
|---|---:|
| Infinity gloves | `175 / 225 / 1,500 / 175` |
| Infinity hat | `350 / 400 / 3,000 / 350` |
| Infinity top | `400 / 450 / 4,000 / 400` |
| Infinity bottoms | `450 / 500 / 5,000 / 450` |
| Infinity boots | `120 / 120 / 1,200 / 120` |
| Battlestaff | `1 / 2 / 20 / 2` |
| Beginner wand | `30 / 30 / 300 / 30` |
| Apprentice wand | `60 / 60 / 600 / 60` plus Beginner wand |
| Teacher wand | `150 / 200 / 1,500 / 150` plus Apprentice wand |
| Master wand | `240 / 240 / 2,400 / 240` plus Teacher wand |
| Mage's book | `500 / 550 / 6,000 / 500` |
| Bones to Peaches | `200 / 300 / 2,000 / 200` |
| Mist, Dust, Mud, Smoke, Steam, or Lava rune | `1 / 1 / 15 / 1` |
| Cosmic rune | `0 / 0 / 5 / 0` |
| Chaos rune | `0 / 1 / 5 / 1` |
| Nature rune | `0 / 1 / 0 / 1` |
| Death rune | `2 / 1 / 20 / 1` |
| Law rune | `2 / 0 / 0 / 0` |
| Soul rune | `2 / 2 / 25 / 2` |
| Blood rune | `2 / 2 / 25 / 2` |

RuneHQ's guide was entered `2006-01-23` and records a last update of
`2012-07-01`. It independently corroborates the four-room structure, caps,
shop table, wand-upgrade requirement, death consequence, and item stats:

<https://www.runehq.com/minigame/mage-training-arena>

RuneHQ's Enchantment point-per-cast table conflicts with the primary cutoff
revision and therefore does not override it. Oldid `6491109` owns the cutoff
point rule.

## Throughput evidence

A dated player analysis published `2006-08-27` supplies observational rates:

<https://forum.tip.it/topic/61796-analysis-of-the-mage-training-arena/>

| Room | Period observational rate | Qualification |
|---|---:|---|
| Alchemist | about 120 points/hour and 60,000-75,000 Magic XP/hour | One player's efficient strategy; approximately three Nature runes per point. |
| Graveyard | 300-400 points/hour and 10,000-15,000 Magic XP/hour | Bones to Bananas plus carried food; the author says Bones to Peaches should be faster. |
| Telekinetic | about 100 points/hour and 15,000 Magic XP/hour | Approximately two Law runes per point. |
| Enchantment | `source_blocked` | The surviving rendered post truncates this section before a rate or complete calculation. |

These are legitimate pre-EOC observations, not exact server constants. They
can calibrate the contract's conservative route workload for three rooms, but
cannot manufacture a fourth rate.

## Implementation-source inspection

The search-order sources do not close the missing server behavior:

- Darkan's only Arena file,
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/minigames/mage_training_arena/MageTrainingArena.java`,
  contains ladder and room teleports only. It implements no room actions,
  hazards, point awards, or timers.
- game-main contains no Mage Training Arena runtime. Its ordinary Alchemy
  plugin at
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/alchemy/alchemy.plugin.kts`
  establishes a five-tick ordinary Alchemy timer, but that does not include
  cupboard selection, forty-second value rotation, deposit travel, or the
  Arena's free-cast opportunity.
- game-main's ordinary jewellery-enchantment plugin establishes spell outputs
  but no Arena collection, bonus-shape, deposit, or Dragonstone timing. It
  therefore cannot supply Arena throughput.
- rev-727 through rev-742 caches can establish item, object, and interface
  identities but cannot establish the missing server-side room rate.

## Source block and next replacement seam

The live cadence kernel uses a fixed `R = 1000` review baseline and requires an
integer or rational source rate for a rate-limited route. The settled Arena
contract explicitly rejects treating one review as one maze, one point, or an
arbitrary batch. Shipping the fourth room with a guessed hourly rate would be
an invented timer, which the source-verification standard does not permit.

The horizontal implementation is therefore parked as `source_blocked`, not
redesigned. The blocker can be replaced without changing product behavior when
one of these appears:

1. a dated official/fansite guide, calculator, video, or forum record with a
   reproducible cutoff Enchantment point or cast rate;
2. a Darkan or independent period-lineage Arena implementation with complete
   collection, casting, deposit, and spawn cadence, corroborated against the
   period point rules; or
3. an explicit future owner authorization for one global disclosed cadence
   abstraction under the source standard's estimation clause.

Graveyard falling-bone frequency and reward-rune weights remain later
source-depth blockers. They do not become permission to omit the hazard or
reward. Cache IDs and equipment stats remain a bounded harvest task after the
four-room cadence gate clears.

No owner-facing design gap surfaced in this pass. No product code or UI was
changed.
