# Capes, Music Log and the Taskmaster presentation — 2026-07-27

Branch `diary/capes`, worktree `ankiscape_worktrees/diary-capes`. Both lanes
green: `python3 run_tests.py` runs 3,134 tests with 369 skips and no failures;
the offscreen Qt lane runs the same 3,134 with 1 skip and no failures. Baseline
before this work was 3,089 and 359.

This closes design-contract clauses D12, D13, D15, D16 and the outstanding half
of D8 from `achievement-diary-item-grants-design.md`.

## The source that made it cheap

Darkan at `c95aca409f397cab12c13b6d5269b73f6cd8abe9` carries the whole cape
system in one file, `com/rs/game/content/Skillcapes.kt`, and the whole period
song table in `data/music/songs.json`. Neither was looked at by the earlier
audits, which reasoned from the wiki.

| What | Where |
|---|---|
| 25 skillcapes: untrimmed, trimmed, hood and master item ids | `Skillcapes.kt:16-40` |
| 99,000-coin price, level-99 gate, cape-plus-hood grant | `Skillcapes.kt:42-61` |
| Trim rule — more than one 99 trims every owned cape | `Skills.java:132-138`, retro-sweep at `:140+`, called at `:864-866` |
| Master NPC per cape | `GenericSkillcapeOwnerD.java:30-58` plus seven per-master dialogue classes |
| Master NPC names | `developer-information/npcList.txt` (rev-727 definition dump) |
| Quest point cape: all quests, 99,000 coins, cape 9813 + hood 9814 | `WiseOldMan.kt:16-33`, equip guard `ItemConstants.java:376-380` |
| Max cape: all skills 99, 2,475,000 coins, cape 20767 + hood 20768 | `MaxD.java:47-75`, `Skills.isMaxed` at `:1156-1169` |
| Completionist cape item ids | `ItemConstants.java:412-414` |
| Veteran cape item ids 20763 and 24709 | `EmotesManager.java:579-595` |
| 1,056 period music tracks with their names and unlock hints | `data/music/songs.json` |
| "The Task at Hand", id 941, hint "by completing 350 Tasks." | `songs.json:8457-8464` |

Equipment bonuses come from the 2011Scape item config
(`game-main/data/cfg/items.yml`), which gives every skillcape defence 9 in each
style and prayer 4. Prices and prayer bonuses for the Max, Completionist and
Veteran capes are corroborated against the revisions the contract already pins.

Reproduce the music catalog with:

```
python3 tools/harvest_music_log.py
```

## What Darkan does not have, and what we did about it

- **No skillcape boost of any kind.** No operate handler, no equip handler, no
  code that raises a level while a cape is worn. D13's effective level 100 is
  the owner's design decision, not a period mechanic, and every period success
  table saturates at 99 anyway. Queued as **design fork 3.10** with the
  recommendation that is implemented: keep the rule, let the tables saturate,
  and let it bite by itself when a formula that does not cap at 99 ships.
- **No Completionist or Veteran vendor.** Their sellers and prices come from the
  pinned revisions: the Varrock Museum guard at 5,000,000 coins, and Hans at
  Lumbridge Castle at 50,000 and 100,000.
- **No music unlock hook.** Darkan unlocks tracks by map region, which AnkiScape
  cannot use because it has no map. A track is kept only when its own hint names
  something durable state can prove — a quest we ship, or the completed-task
  count. 191 of 1,056 tracks survive that rule.
- **No Taskmaster award.** The emote enum knows the 534-task threshold
  (`EmotesManager.java:100`) but nothing ever grants it. Our one-time
  presentation is the contract's translation, and it grants nothing.

## One effective level, not two

`familiar_effective_roll_level_pure` was already the invisible-boost seam for
success rolls. Rather than add a second one, `effective_roll_level_pure` in
`logic/cape_logic.py` composes the familiar boost and the skillcape, and every
roll site now calls it — the four gathering handlers, Firemaking, Cooking,
Smithing, Thieving and Agility. `agility_effective_level_pure` delegates to it
and no longer carries its own cape check.

Wiring Cooking exposed a real inconsistency that predated this work in shape:
the handler computed its reported success chance from one level and its actual
outcome from another. Both now take the roll level, so the number shown and the
number rolled against are the same number.

Crafting, Fletching, Herblore and Runecrafting are deliberately untouched: their
actions are deterministic or gated on level thresholds, and the contract is
explicit that a cape must not unlock a level-gated action.

## Latent rows, and why the log has a smaller denominator than its catalog

The Music Log ships 191 tracks and counts 190. "The Task at Hand" needs 350
completed tasks and the diary roster is 171 while three families' task tables
remain unharvested (fork 3.9). Rather than ship a row nothing can reach, the
track is labelled latent, excluded from the log's denominator, and activates by
itself when the roster is complete. Without that, the Completionist cape's music
requirement would be gated on content that does not exist.

Dungeoneering is treated the same way and for the same reason as the milestone
capes: it is in the source cape table and absent from the shipped one, derived
from `trainable_skill_definitions()`, so its cape and its 120 master cape appear
on the day the skill becomes trainable.

## Placeholders

One: `capes_of_distinction.prestige_defensive_block`. The 2011Scape config
carries `equipment: null` for the Max and Completionist capes and Darkan reads
its item definitions from the cache, so only the prayer bonus is recovered.

## Save version

`CURRENT_CONFIG_VERSION` is now 89. The migration seeds both new states by
running their own refresh rather than by inventing a starting point, so a player
who was already 99 in two skills keeps the correct first-99 keepsake and a
player who finished a quest years ago already owns its tracks.
