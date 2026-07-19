# Slayer Molanisk Combat closure

Date: 2026-07-18  
Status: **source-closed and implemented**

## Period contract

The primary cutoff page is RuneScape Wiki `Molanisk`, oldid `6565831`,
timestamp `2012-11-17T10:31:23Z`:
<https://runescape.wiki/w/Molanisk?oldid=6565831>.

It establishes the level-51 ordinary representative, 520 LP, Slayer 39,
52 Slayer XP, six-tick passive melee, approximate 53-LP maximum, guaranteed
Bones, and the period drop contents. It also states that the wall-bound monster
must be lured with a Slayer bell and that a light source should be brought.

RuneScape Wiki `Slayer bell`, oldid `6121349`, timestamp
`2012-08-21T00:06:34Z`, fixes the ordinary item and 150-coin Slayer-master
acquisition:
<https://runescape.wiki/w/Slayer_bell?oldid=6121349>.

RuneScape Wiki `Dorgesh-Kaan South Dungeon`, oldid `6393410`, timestamp
`2012-10-13T11:13:58Z`, establishes Death to the Dorgeshuun completion and a
lit light source as the route requirements:
<https://runescape.wiki/w/Dorgesh-Kaan_South_Dungeon?oldid=6393410>.

The existing quest catalog already implements Death to the Dorgeshuun, the
Slayer shops already sell item 10952, and the Firemaking graph already exposes
the reachable lit-source set. No quest, shop, or invented pseudo-item was
added.

## Review-native lure

One Combat encounter represents ringing the bell to pull one Molanisk from the
wall and fighting it. The bell remains in inventory and is not consumed. A
real lit source may be in inventory or equipped. The Combat picker says this
directly rather than exposing a redundant pre-fight button or using wall-clock
state.

This is a flattening of spatial interaction, not a probability abstraction:
the sourced item requirements and one-lure-per-monster meaning remain intact.

## Combat definition

Darkan
`data/npcs/combatdefs/uncategorized/molanisk.json:1-30` supplies:

- 520 LP;
- 40 Attack, 40 Strength, 50 Defence, 0 Magic, and 1 Ranged;
- 53 maximum hit;
- passive melee;
- 59-tick respawn.

Darkan `developer-information/npcListBonuses.txt:5753` supplies zero attack
bonuses, +45 stab defence, +45 slash defence, +35 crush defence, +30 Magic
defence, +55 Ranged defence, and zero strength bonuses.

## Executable drops

Darkan `data/npcs/drops/molanisk.json:1-283` contains one guaranteed Bones row
and 22 non-zero ordinary rows. Darkan
`src/main/java/com/rs/utils/drop/DropList.java:43-68,98-109` sorts those
non-zero rows into one mutually exclusive cumulative roll and appends the
remaining probability as empty.

The exact 100,000-slot ordinary selector is:

| Output | Slots |
|---|---:|
| Grimy guam | 16,791 |
| Grimy marrentill | 16,791 |
| Water rune | 16,791 |
| Earth rune | 16,791 |
| Swamp weed | 16,791 |
| Grimy tarromin | 1,749 |
| Grimy harralander | 1,749 |
| Grimy ranarr | 1,749 |
| Grimy dwarf weed | 1,749 |
| Coins | 1,749 |
| Mud rune | 1,749 |
| Grimy wergali | 1,749 |
| Wergali seed | 1,749 |
| Grimy irit | 207 |
| Grimy avantoe | 207 |
| Grimy kwuarm | 207 |
| Grimy cadantine | 207 |
| Nature rune | 207 |
| Cosmic rune | 207 |
| Grimy lantadyme | 207 |
| Mole claw | 207 |
| Death runes ×50 | 186 |
| Empty | 211 |

The 93/50,000 Death-rune row is represented exactly as 186/100,000. The period
page supplies rarity bands rather than numeric rates; the exact selector is
therefore labeled Darkan executable parity, not period-rate parity.

Darkan `src/main/java/com/rs/utils/NPCClueDrops.java:54` adds an independent
1/128 easy clue. There is no Molanisk row in Darkan `charmDrops.txt`, so no
charm selector is manufactured.

## Item identity and art

- Slayer bell item 10952 and its Slayer-master stock already existed.
- Swamp weed item 10978 and Mole claw item 7416 are non-stackable, tradeable
  material identities.
- `combatenemies/molanisk.png` is normalized from `Molanisk icon.png`, revision
  `2011-11-26T04:43:26Z`, SHA-1
  `5082e9110b3ca6166dc4f5c61c4faa7ede43fb68`.
- `combatitems/mole_claw.png` is normalized from `Mole claw.png`, revision
  `2011-11-26T04:43:46Z`, SHA-1
  `14d9188080da460e3e7cbcc8a9b83a1c53d4b613`.
- `combatitems/swamp_weed.png` is normalized from `Swamp weed.png`, revision
  `2008-10-20T16:36:49Z`, SHA-1
  `7050271dbe066d1a223b3decd347014827f40534`.

## Scope and design-gap record

No owner-facing design fork emerged. The existing quest, shop, light-source,
Combat, inventory, and Slayer-family contracts settle the implementation.

## Verification

Focused Combat, Slayer, registry, metadata, and UI coverage passes all 602
methods with 211 expected non-Qt skips. The focused real offscreen Qt
Combat-picker regression passes. Full discovery passes all 1,657 methods in
the non-Qt environment with 215 declared environment skips, and all 1,657
methods in the real offscreen Qt environment with zero skips. Documentation
passes across 326 Markdown and 342 HTML files. Test quality reports zero hard
issues across 73 files and four pre-existing advisory clone groups.

Compilation, JSON parsing, `git diff --check`, and the worktree-safety audit
pass. The readiness audit reports Turael/Spria 23/23, Mazchna/Achtryn 26/27
with only Mogres blocked, and Vannaka 33/35 with only Mogres and Turoth
blocked. The reachability audit ran over 1,253 actions and 1,849 reachable
items; its 293 orphan inputs and 320 blocked actions remain tracked project
debt rather than a falsely green closure gate.

Closure results are finalized in
`status-updates/slayer-molanisk-results-2026-07-18.html`; the mobile copy is
<https://2a1t6lht0q8n.postplan.dev>.
