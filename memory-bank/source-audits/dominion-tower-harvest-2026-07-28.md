# Dominion Tower implementation harvest

Date: `2026-07-28`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **complete for mechanical completion.** Everything the family needs is
pinned below. Twenty-four values the period had and the record does not state
are registered in `memory-bank/placeholder-values.md`.

## Why the tower needed a harvest at all

The Dominion Tower released `2011-11-01`, thirteen months inside the cutoff, so
it is comfortably in period. Darkan implements it, but its own file says what it
is: only endurance mode works, `openClimberMode` prints "Only endurance mode is
currently working", the boss list is annotated `// custom bosses` and contains
Jad and the King Black Dragon which the tower never offered, there are no
handicaps at all, and `getBossesTotalLevel` carries a `level = +` typo that
returns the last NPC's level instead of the sum. Darkan is therefore a shape
source here, never a roster source.

## Source ledger

| What | Where |
| --- | --- |
| Entry gates, five modes, eight boss classes with floor gates, the 22-row handicap wheel with per-round factor deltas, ten special matches, the achievement ladder | `Dominion Tower` oldid `6563470` (2012-11-16T06:18:29Z) |
| Mode factor multipliers (climber ×100, endurance ×10), `MAX_FACTOR = 10000000`, claim-resets-progress, the 110-combat check | Darkan `darkan-world-server/src/main/java/com/rs/game/content/minigames/domtower/DominionTower.java` |
| Per-NPC lifepoints, maximum hits and combat-stat blocks for roughly two thirds of the roster | Darkan `darkan-world-server/data/npcs/combatdefs/**.json` |
| NPC ids, client combat levels, and the ten attack/defence plus three strength bonus values for nearly every roster NPC | rev-727 cache dump `developer-information/npcListBonuses.txt` |
| Per-boss levels, lifepoints, maximum hits and attack styles | one pinned pre-cutoff revision per boss, cited on each NPC row in `data/dominion_tower_data.py` |
| Glove bonus blocks, level requirements and the exact six-boss unlock sets | `Goliath gloves` oldid `6581523`, `Spellcaster gloves` oldid `6290648`, `Swift gloves` oldid `6430300` |
| Reward-box contents and the 20-per-item cap | `Reward box` oldid `5277943` |
| Xp book skills and the level-75 gate | `Xp book` oldid `6461382` |
| Dreadnip level, maximum hit, duration, and the 450-kill-plus-spectate unlock giving 100 at a time | `Dreadnip` oldid `6513998` |
| Dominion sword, staff and crossbow: tower-only restriction, level requirements, degradation budgets, unlock conditions | oldids `6300686`, `6155092`, `6155090` |
| Dominion mine: 1,000 coins each, 400 kills plus every special match except Sunfreet, always 20% of maximum lifepoints | `Dominion mine` oldid `6534609` |
| Ascendancy mine: ten per claim, another 500 kills for more | `Ascendency mine` oldid `6092960` |
| Medallion +4 and Super medallion +8, three teleports a day | oldids `6081501`, `6134486` |
| Marker stages one to four at 100/200/300 kills and all achievements, boosting +4/+6/+8/+10 | `Dominion marker` oldid `6447188` |
| Twenty journal pages | `A journal page` oldid `6287858` |
| Scorpion meat heals 220, tower only | `Scorpion meat` oldid `5907745` |
| Two-dose tower potions | `Dom super restore` `5588114`, `Dom super prayer` `5588111`, `Dom super antipoison` `5588115`, `Dom saradomin brew` `5588118` |
| Bomb effects and the four-per-match cap; help horn's five charges | `Diminutive bomb` `6552690`, `Massive bomb` `5588105`, `Colossal bomb` `5992282`, `Help horn` `6082361` |

## What the sources settle exactly

- **Entry.** Combat level 110, and twenty of the thirty-eight listed quests.
  Darkan checks the same 110 through `getCombatLevelWithSummoning()`, so the two
  sources agree. Recipe for Disaster is one entry on the tower's list and ten
  subquests in AnkiScape's ledger, so it counts only when all ten are complete.
- **The roster is quest-gated.** "Only bosses of quests the player has completed
  will be available to fight in the tower." All thirty-seven of the remaining
  thirty-eight quests exist in `generated/quest_catalog_generated.py`, so the
  gate is real rather than decorative.
- **Eight classes of six.** Class A is floor 6+; every other class is floor 1+.
  The three glove sets turn out to partition classes A, B and C exactly, two
  encounters from each class per set, which is a strong cross-check that the
  class table and the three glove pages agree.
- **The handicap wheel.** Twenty-two handicaps, each with a signed per-round
  factor delta, listed in wheel order. A nudge lands on the handicap *before* the
  current one and wraps from the top to the bottom; the article gives two worked
  examples and both are asserted in the tests.
- **Two sentinels, not three.** The Goliath unlock list says "Two Dagannoth
  Sentinels" and the Dagannoth sentinel page's strategy text talks about "both"
  of them, so the climber arena holds two. The `Just Die Already` special holds
  six, which the tower page states separately.
- **The Dominion mine's price.** The tower page's "10,000 coins for 10 mines"
  and the mine page's "Each mine costs 1000 coins" are the same number stated
  two ways, not a conflict.

## Conflicts recorded rather than silently resolved

- **Agrith-Na-Na's combat level.** `Agrith-Na-Na` oldid `6303641` says 146; rev
  727 says 182 for the same NPC id 3493. The cache is the client's own
  definition, so it wins on identity, and the divergence is noted at the row.
- **Maximum hits.** Darkan and the wiki disagree by small amounts on several
  bosses (Dad 280 vs 275, The Draugen 70 vs 100, Jungle demon 320 vs 323). The
  pinned wiki revision is taken in each case, because Darkan's combat definitions
  are a reconstruction and the article is a period record.
- **Darkan stubs.** Eruni (5 lifepoints), Zenevivia (1), Dagannoth sentinel (2)
  and Decaying avatar (10) are placeholders in Darkan's own files, and the file
  names say so — `(nostats)`, `(noanims)`. The wiki figures are used. Where
  Darkan's *maximum hits* on those same stubs match the wiki exactly (Ayuni 253,
  Leeuni 272), that is recorded as corroboration.

## The one boss that cannot be reached

Tarn Razorlor and his terror dogs are gated on the Lair of Tarn Razorlor
miniquest, which is not one of the tower's thirty-eight and which AnkiScape's
quest ledger does not carry. The row ships with its authentic gate and lights up
by itself when miniquests land. It belongs to no reward set. Queued as design
thread 3.20.

## Translation decisions, disclosed

- **Two handicaps have no mechanical effect here and keep only their factor
  delta.** Random Freeze stops the player moving while still allowing attacks,
  and AnkiScape has no movement, so there is nothing to take away. This is
  recorded rather than faked.
- **The six reduced attack/defence handicaps** are stated only as "reduced". The
  attack half scales the player's damage; the defence half raises the arena's own
  maximum hits, which this family owns. One registered fraction covers both.
- **Reward boxes draw three common items only as a registered reconstruction.**
  Darkan's `giveRewards` routine performs three common draws, but Darkan is a
  shape source here and no period record states the roll count. The shipped count
  is registered as `dominion_tower.reward_box_rolls` rather than treated as exact.
- **Unsourced stat blocks use Temple Trekking's core-stat ratio.** Copying an
  NPC's combat level into all four combat stats gave the level-699 Nomad a
  defence of 699 and made him literally unbeatable, which is a placeholder
  disabling a mechanic. Seventy-two per cent of the level, capped at 99, is the
  ratio the Temple Trekking family already uses for the same problem.
