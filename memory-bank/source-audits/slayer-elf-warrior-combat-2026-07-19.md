# Slayer Elf warrior Combat source audit — 2026-07-19

## Decision

Implement both ordinary Elf warrior combat forms as one playable Slayer
family: level 90 ranged and level 108 melee. Both require completed Regicide,
retain distinct period combat identities, and share Darkan's generic ordinary,
charm, and hard-clue selectors.

AnkiScape has no location selector inside a Combat target. The shared drop
contract therefore combines Darkan's crystal-seed ordinary table with its
separate charm channel even though the period page says crystals belong to
Lletya and charms to the Elf Camp. This is an explicit no-position
location-flattening abstraction, not a claim that one 2012 spawn dropped both.
Lletya Thieving, Mourning's End quest stages, Prifddinas, and Dungeoneering
remain separate.

## Period authority

RuneScape Wiki `Elf warrior`, oldid `6547078`, timestamp
`2012-11-10T19:44:18Z`, is inside the frozen cutoff:
<https://runescape.wiki/w/Elf_warrior?oldid=6547078>.

Literal wikitext establishes:

- levels 90 ranged and 108 melee;
- 1,050/1,060 LP and 105/107.5 Slayer XP;
- six-tick attacks with 116/109 maximum hits;
- non-aggression, non-poisonous attacks, and poison susceptibility;
- guaranteed Bones and Chaeldar assignment;
- Lletya crystal drops versus Elf Camp charm drops; and
- Regicide-area access, with Lletya convenience requiring the later start of
  Mourning's End Part I rather than redefining the Slayer-family gate.

The already-settled Chaeldar pool uses completed Regicide, not Mourning's End
Part I, from RuneScape Wiki `Regicide`, oldid `6505748`; this Combat slice
reuses that exact quest ID and does not add quest stages.

The rev-742 cache dated `2012-11-07` independently contains attackable NPC IDs
1183/1184 and 2359–2362 named `Elf warrior`. ID 1201 is the separate Talk-to
record and is excluded.

## Executable combat definitions and conflict resolution

Darkan commit `d759fdd779ae38836900b0dea3c4357bc1a82458` supplies:

- `data/npcs/combatdefs/uncategorized/elf_warrior/elf_warrior_(90).json:1-32`:
  IDs 1183/2361/2362, 1,050 LP, Ranged 95, Strength 80, Attack/Defence 1,
  ranged style, non-aggression, 120 maximum, and 39-tick respawn;
- `data/npcs/combatdefs/uncategorized/elf_warrior/elf_warrior_(108).json:1-32`:
  IDs 1184/2359/2360, 1,050 LP, Attack/Defence 95, Strength 80, melee style,
  non-aggression, 120 maximum, and 39-tick respawn; and
- `developer-information/npcListBonuses.txt:1185-1186`: level-90
  Stab/Slash/Crush/Magic/Ranged defences 50/50/50/60/70, and level-108
  defences 50/70/70/60/50.

The period page directly states the player-visible LP and maximum hits, so it
wins the conflicts: level 90 uses 1,050/116 and level 108 uses 1,060/109.
Darkan supplies the hidden combat levels, numeric defences, and respawn.

## Drops

Darkan `data/npcs/drops/elf_warrior.json:1-235` supplies guaranteed Bones and
one 128-slot ordinary selector. `DropList.java:43-68` proves that the nonzero
sibling rows occupy one cumulative selector:

| Output | Slots |
|---|---:|
| Coins ×44 | 29 |
| Crystal teleport seed | 25 |
| Darkan herb table | 15 |
| Coins ×180 | 10 |
| Water runes ×70 | 8 |
| Nature runes ×12; Coins ×20; Darkan gem table | each 5 |
| Green d'hide body | 4 |
| Green d'hide chaps; Law runes ×2; Lobster; Shark | each 3 |
| Mithril spear; Fire runes ×37; Adamantite ore | each 2 |
| Mithril kiteshield; Adamant full helm; Rune dagger | each 1 |
| Empty | 1 |

The nonempty rows total 127 slots. The crystal seed is cache item 6103,
registered as unstackable and untradeable.

`data/npcs/charmDrops.txt:55` supplies thresholds `8-24-7-2`.
Lossless enumeration of the inclusive overlapping choice in
`src/main/java/com/rs/tools/old/CharmDrop.java:54-75` produces a 1,212-slot
selector: 35 Gold, 227 Green, 29 Crimson, 9 Blue, and 912 empty.

`src/main/java/com/rs/utils/NPCClueDrops.java:125` adds an independent 1/128
hard clue. The period page corroborates the clue tier. Its generic rare-drop
table transclusion has no executable rate in the pinned Darkan row, so that
roll remains `source_blocked`.

## Assets

The 2012 article names separate bow and spear renders, but those original file
pages did not survive the wiki migration. The current wiki retains explicit
2010 archive renders:

- `combatenemies/elf_warrior.png`: `File:Elf warrior (Iorwerth ranger)
  (2010).png`, source SHA-1
  `c262255a1f590f023bb06de2c2af7e087630ff52`, post-migration upload timestamp
  `2014-08-27T14:36:09Z`;
- `combatenemies/elf_warrior_level_108.png`: `File:Elf warrior (Iorwerth
  warrior) (2010).png`, source SHA-1
  `c84dbaae917ab317cf1834aa031073ef769d5ca8`, post-migration upload timestamp
  `2014-08-27T14:36:14Z`.

The provenance preserves those later upload dates instead of mislabeling them
as pre-cutoff revisions. The file names and the period article together attest
the archived 2010 visual identities. Both normalize through the standard
48-pixel Combat-enemy pipeline.

## Readiness and design-gap result

The two targets advance Chaeldar from 24/34 to 25/34 while the master remains
hidden and unrenormalized. Nine Combat families remain blocked: Fever
spiders, Fungal magi, Grifolapines, Grifolaroos, Jungle strykewyrms, Kurasks,
Trolls, Vyrewatch, and Warped tortoises.

No owner-facing design gap emerged. The location-flattening choice follows the
owner-approved no-map abstraction, and the quest gate was already settled.

## Workflow and verification

Codex Workflow `cafd0734-4254-4ab7-bbc1-1c1a5f953bd4` was bounded to two
read-only leaves, but shared global startup/concurrency pressure prevented
either leaf from creating a session. Its explicit ten-minute run deadline
expired with zero tokens and zero tool calls. No reviewer conclusion was
produced or used.

Root-focused Combat, Slayer, roster, and metadata coverage passes 361 tests.
The focused real offscreen Qt Combat picker passes after correctly supplying
the Regicide fixture state.

Full non-Qt discovery passes all 1,679 tests with 215 declared environment
skips. Full real offscreen Qt discovery passes all 1,679 tests with no skips,
failures, or errors. Test quality reports zero hard issues across 73 files and
1,679 methods. Documentation, compilation, provenance JSON, diff, readiness,
declared-baseline reachability, asset, and worktree-safety checks pass.
Reachability remains at 1,253 actions, 1,866 reachable items, 288 orphan
inputs, and 313 blocked actions.

Results: `../status-updates/slayer-elf-warrior-results-2026-07-19.html`;
mobile copy: <https://hp6p2ourxwdr.postplan.dev>.
