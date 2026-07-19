# Slayer Blue dragon family Combat source audit — 2026-07-18

## Decision

Implement the ordinary level-111 Blue dragon and the level-48 Baby blue
dragon together as Chaeldar's twenty-first executable family. Baby blue
dragons count toward a Blue dragon assignment in the cutoff game, so both
representatives belong in the target picker. The adult preserves dragonfire;
the baby is a melee-only substitute and must not inherit dragonfire.

This family slice does not add locations, dungeon access, quest routes, or
Daemonheim/Dungeoneering variants. No owner-facing design choice is required.

## Period authority

RuneScape Wiki `Blue dragon`, oldid `6506510`, timestamp
`2012-10-30T20:44:37Z`, is inside the frozen cutoff:
<https://runescape.wiki/w/Blue_dragon?oldid=6506510>.

The period revision establishes the ordinary adult's:

- combat level 111, 1,100 LP, and 107.6 Slayer XP;
- melee style, six-tick attack speed, and 110-LP melee maximum;
- close-range dragonfire with a 500-plus unprotected maximum;
- aggressive, non-poisonous attacks and susceptibility to player poison;
- guaranteed Blue dragonhide and Dragon bones;
- assignment by Chaeldar, Sumona, and Kuradal; and
- Baby blue dragon substitution on a Blue dragon Slayer task.

The infobox also contains a stale `slayer xp=105` field. The more specific
period `slayxp=107.6` field agrees with the page's 1,100-LP ordinary
representative and is used. Darkan's 1,050-HP/105-XP record is lower-ranked
executable corroboration, not authority to overwrite the frozen period row.

RuneScape Wiki `Baby blue dragon`, oldid `6516086`, timestamp
`2012-11-01T12:41:19Z`, establishes combat level 48, 510 LP, 50 Slayer XP,
six-tick melee, an approximately 60-LP maximum, no dragonfire, guaranteed
Baby dragon bones, and Blue-dragon-task substitution:
<https://runescape.wiki/w/Baby_blue_dragon?oldid=6516086>.

## Executable combat definitions

Darkan commit `d759fdd779ae38836900b0dea3c4357bc1a82458` provides
the adult executable record at
`data/npcs/combatdefs/uncategorized/blue_dragon.json:1-31`: Attack, Strength,
and Defence 95, Magic and Ranged 1, 110 maximum melee hit, and a 59-tick
respawn. Its `developer-information/npcListBonuses.txt:57` row supplies exact
stab/slash/crush/magic/ranged defences of 50/70/70/60/50.

The independently pinned game-main definition agrees at
`game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/dragons/blue_dragon_level_111.plugin.kts:75-108`.
The period 1,100 LP and 107.6 Slayer XP take precedence over the emulator's
1,050 HP and 105 XP.

Darkan
`data/npcs/combatdefs/uncategorized/baby_blue_dragon.json:1-30` supplies the
baby's Attack/Strength/Defence 40, Magic/Ranged 1, 60 maximum, melee style,
and 59-tick respawn. `developer-information/npcListBonuses.txt:54` supplies
exact defences of 30/50/50/40/30.

## Dragonfire

The adult reuses the already-live Green-dragon protection seam:

- no protection: 0–500 LP;
- one shield or ordinary antifire layer: 0–50 LP; and
- full protection: zero dragonfire damage.

The 1/4 dragonfire attack selector remains explicitly
`provisional/darkan`; the frozen page proves the attack and damage envelope
but not a period numeric selection rate. The baby has no `dragonfire`
definition, matching the period statement that it cannot breathe fire.

## Drops

Darkan `data/npcs/drops/blue_dragon.json:1-263` supplies guaranteed Blue
dragonhide and Dragon bones plus one complete 128-slot ordinary selector:

| Output | Slots |
|---|---:|
| Coins ×44 | 29 |
| Coins ×132 | 25 |
| Darkan herb table | 15 |
| Coins ×200 | 10 |
| Water runes ×75 | 8 |
| Nature runes ×15 | 5 |
| Coins ×11 | 5 |
| Darkan gem table | 5 |
| Steel platelegs | 4 |
| Mithril hatchet | 3 |
| Mithril spear | 3 |
| Law runes ×3 | 3 |
| Adamantite ore | 3 |
| Bass | 3 |
| Adamant dagger | 2 |
| Adamant full helm | 1 |
| Mithril kiteshield | 1 |
| Rune dagger | 1 |
| Fire runes ×37 | 1 |
| Coins ×440 | 1 |

Darkan `data/npcs/charmDrops.txt:26` supplies thresholds `11-27-11-2`.
Lossless enumeration of Darkan's inclusive multi-threshold choice produces a
404-slot selector: 15 Gold, 79 Green, 15 Crimson, 3 Blue, and 292 empty.

`NPCClueDrops.java:115` supplies the independent 1/128 hard-clue roll.
`data/npcs/drops/tertiaries/blue_dragon_egg.json:1-19` supplies the independent
1/2,000 Blue dragon egg roll. The period page states that the egg is available
only at Summoning 99, so the drop table has a generic
`required_skill_levels=(("summoning", 99),)` gate. Gated tables are skipped
before their RNG draw when the requirement is unmet. This preserves both the
item's availability and the surrounding selector sequence. Hatching and
incubation remain in the separate Summoning system.

Darkan `data/npcs/drops/baby_blue_dragon.json:1-15` supplies only guaranteed
Baby dragon bones for the baby representative. Quest-only bones and later
loot are excluded.

## Assets

`combatenemies/blue_dragon.png` is pinned to the pre-cutoff
`File:Blue dragon.png` revision from `2011-02-01T13:53:37Z`, SHA-1
`bc969717f5dcf11dc91835bee02453482bc2a685`.

`combatenemies/baby_blue_dragon.png` is pinned to the pre-cutoff
`File:Baby blue dragon.png` revision from `2012-05-10T09:54:19Z`, SHA-1
`de87803872b56269ce0478098763c45601b00397`.

Both are fetched and normalized through the standard Combat-enemy asset
pipeline, with complete entries in `assets_provenance.json`.

## Readiness and scope

Registering both representatives advances Chaeldar from 20/34 to 21/34.
Thirteen families remain blocked, and Chaeldar remains hidden and
unrenormalized. The target does not manufacture Taverley, Heroes' Guild,
Ogre Enclave, resource-dungeon, Kuradal-dungeon, quest, or Daemonheim rules.

No owner-facing design gap emerged.

## Workflow and verification

Codex Workflows run `f75e6ec0-6998-4acd-9c03-665b4fb56fc2` launched two
bounded Sol-high read-only leaves using build
`0.1.0+codex.20260718224425`. Both created real provider sessions and emitted
tool activity, but neither produced a final result after roughly ten minutes.
One leaf stopped after yielding a long-running command cell; the other stopped
after completed repository inspection and encrypted reasoning. The primary
canceled both genuinely stuck leaves, independently reproduced every source
and repository claim above, and used no native-subagent fallback.

Focused Combat, Slayer, roster, and metadata coverage passes 350 tests. The
real offscreen Qt Combat picker passes. Full non-Qt discovery passes all 1,668
tests with 215 declared Qt-environment skips. Full real offscreen Qt discovery
executes all 1,668 tests with zero skips or failures in 540.174 seconds.

Test quality reports zero hard issues across 73 files and 1,668 methods; the
four structural-clone groups are the unchanged high-signal baseline.
Documentation passes across 338 Markdown and 347 HTML files. Compilation,
provenance JSON, diff hygiene, readiness, and worktree safety pass.
Reachability improves from 1,851 reachable items, 293 orphan inputs, and 320
unresolved actions to 1,861, 288, and 313 respectively; the combat drops close
existing item gaps without adding an action.

Results:
`status-updates/slayer-blue-dragon-family-results-2026-07-18.html`; mobile
copy: <https://ez10f8mr9lib.postplan.dev>.
