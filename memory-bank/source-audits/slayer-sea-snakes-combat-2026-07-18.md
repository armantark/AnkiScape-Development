# Slayer Sea snakes Combat closure

Date: 2026-07-18  
Status: **source closed and implemented, with labeled cadence and poison abstractions**

## Period authority

RuneScape Wiki `Sea Snake Hatchling`, oldid `6448392`, timestamp
`2012-10-21T07:02:07Z`, establishes the ordinary level-62 target:

- 500 LP, 50 Slayer XP, melee attacks, and a 69-LP maximum hit;
- no practical Slayer-level requirement;
- passive aggression, Vannaka assignment membership, and an initial 50-LP
  poison hit; and
- Royal Trouble dungeon access.

Pinned page:
<https://runescape.wiki/w/Sea_Snake_Hatchling?oldid=6448392>.

RuneScape Wiki `Sea Snake Young`, oldid `5936978`, timestamp
`2012-07-14T22:21:29Z`, establishes the ordinary level-90 target:

- 850 LP, Slayer 40, 85 Slayer XP, melee attacks, and an 84-LP maximum hit;
- passive aggression and Vannaka assignment membership; and
- an initial poison hit of 78 LP during Royal Trouble or 68 LP afterward.

Pinned page:
<https://runescape.wiki/w/Sea_Snake_Young?oldid=5936978>.

RuneScape Wiki `Miscellania and Etceteria dungeon`, oldid `6436494`,
timestamp `2012-10-18T09:21:04Z`, places both ordinary variants in the dungeon
and establishes Royal Trouble as the access route:
<https://runescape.wiki/w/Miscellania_and_Etceteria_dungeon?oldid=6436494>.

The cutoff Vannaka and cross-master evidence, including the accepted
30–60-task contract, is already reconciled in
`source-audits/slayer-vannaka-pool-2026-07-17.md`.

## Executable emulator authority

The following Darkan paths were read from
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`:

- `data/npcs/combatdefs/uncategorized/sea_snake_hatchling (nostats).json:1-22`
  confirms 500 LP, a 59-tick respawn, passive melee, and the absence of
  explicit combat stats. Its 60-LP maximum loses to the higher-ranked cutoff
  page's 69 LP.
- `src/main/java/com/rs/game/model/entity/npc/combat/NPCCombatDefinitions.java:138-151`
  and `:289-306` define the fallback-stat generator. Level 62 with 50
  old-scale hitpoints generates 84 Attack, Strength, Defence, Ranged, and
  Magic.
- `data/npcs/combatdefs/uncategorized/sea_snake_young.json:1-29` confirms 850
  LP, a 59-tick respawn, passive melee, and exact 90 Attack, 70 Strength, 70
  Defence, 1 Magic, and 1 Ranged. Its 80-LP maximum loses to the cutoff page's
  84 LP.
- `developer-information/npcListBonuses.txt:3941-3942` supplies zero attack,
  defence, and strength bonuses for both NPCs.
- `data/npcs/drops/sea_snake_hatchling.json:1-342` supplies guaranteed Bones,
  a 9/10 Casket roll, and 26 sibling 1/13,000 rare rows.
- `src/main/java/com/rs/utils/drop/DropList.java:43-68` and `:98-147` place
  sibling nonzero rows in one cumulative ordinary selector and emit rate-zero
  rows separately.
- `data/npcs/drops/sea_snake_young.json:1-244` supplies guaranteed Big bones
  and the complete 128-slot main table.
- `data/npcs/drops/tertiaries/long_curved_bone.json:1-30` supplies independent
  Long-bone 1/400 and Curved-bone 1/5,000 rolls.
- `src/main/java/com/rs/utils/NPCClueDrops.java:88-102` supplies an independent
  1/128 medium-clue roll for each variant.

Neither NPC has a Darkan charm row. No charm distribution is invented.

## Exact selectors

The hatchling keeps one ordinary selector plus an independent clue selector:

1. one exact 13,000-slot ordinary selector containing 11,700 Casket slots,
   one slot for each of Darkan's 26 sibling rare rows, and 1,274 empty slots;
   and
2. one medium-clue slot and 127 empty slots.

Darkan's `DropList` gives the 9/10 Casket row and all 26 rare entries adjacent
intervals in one cumulative selector. The AnkiScape representation is
therefore executable emulator parity rather than a compression abstraction:
one kill can emit a Casket or one rare row, never both, and every marginal
chance remains exact.

The young snake's main table is a complete 128-slot selector:

| Output | Slots |
|---|---:|
| Coins ×44 | 60 |
| Coins ×32 | 11 |
| Adamant dart tips ×2 | 10 |
| Coins ×24 | 9 |
| Coins ×23 | 7 |
| Fishing bait ×50 | 4 |
| Pearl bolt tips ×3 | 4 |
| Raw bass ×2 | 4 |
| Water orb | 3 |
| Water runes ×15 | 2 |
| Mist rune | 2 |
| Broad arrows ×4 | 2 |
| Raw lobster | 2 |
| Seaweed ×5 | 2 |
| Edible seaweed ×5 | 2 |
| Oyster pearls ×2 | 1 |
| Oyster pearls | 1 |
| Casket | 1 |
| Nested gem table | 1 |

The tertiary bone rows share a lossless 100,000-slot selector: 250 Long-bone
slots, 20 Curved-bone slots, and 99,730 empty slots. The independent 1/128
medium clue remains separate.

## Review-native mechanics and boundaries

AnkiScape's poison state uses integer old-scale damage and displays ten times
that value as LP. The hatchling's exact 50 LP is represented by 5. The
post-quest young-snake value of 68 LP is not exactly representable, so it uses
the nearest 70-LP value and labels that bounded abstraction. The mid-quest
78-LP branch is not selected because the current Combat access gate is quest
completion.

The six-tick attack cadence is corroborated by surviving later RuneScape and
OSRS data but is not claimed as an exact field recovered from these cutoff
pages. It is labeled as corroborated rather than period exact:
<https://runescape.wiki/w/Sea_Snake_Hatchling>,
<https://oldschool.runescape.wiki/w/Sea_Snake_Hatchling>, and
<https://oldschool.runescape.wiki/w/Sea_Snake_Young>.

The real dungeon permission arrives during Royal Trouble. The current shared
Combat gate only consumes stable quest-completion state, so this slice uses
the conservative `royal_trouble` completion gate. It does not duplicate or
guess Darkan's in-progress quest stages. A separate handoff asks that thread
to expose a stable dungeon-permission state; once present, Combat can accept
that state or quest completion without changing the enemy contract.

## Assets and item identity

- `combatenemies/sea_snake_hatchling.png` is normalized from
  `Sea Snake Hatchling.png` revision `2010-08-07T18:37:31Z`, SHA-1
  `a4658451176d5380e0fd66c5678cbe4ab9375e21`.
- `combatenemies/sea_snake_young.png` is normalized from
  `Sea Snake Young.png` revision `2012-03-09T03:02:36Z`, SHA-1
  `3db69fa99be068c4dfe65dbc27fb5851056ba242`.

Broad arrow item 4160 uses the existing canonical `Broad arrows` storage key,
Fletching registry identity, stackability, tradeability, category, and
cutoff-pinned local asset. This deliberately avoids recreating the retired
singular storage alias that config migration already normalizes to the plural.
Edible seaweed item 403 is newly registered with its cache identity,
stackability, tradeability, food category, and cutoff-pinned local asset:

- `fletcheditems/broad_arrows.png` is normalized from `Broad arrow 5.png`
  revision `2009-05-06T04:47:34Z`, SHA-1
  `d84493269782706946d31270455ea6e09075bba7`.
- `combatitems/edible_seaweed.png` comes from `Edible seaweed.png` revision
  `2011-04-26T00:12:28Z`, SHA-1
  `53a04f37cbc0ad58e285f5f784340e633e34e662`.

## Scope and design-gap record

No quest implementation was added. The Darkan handoff is
`codex-briefs/darkan-quest-handoff-sea-snakes-2026-07-18.md`.

No owner-facing creative-direction fork emerged. The cadence, poison
granularity, and conservative completion gate are visible implementation
abstractions with bounded consequences.

## Workflow review attempt

Read-only Codex Workflows run
`a3a1f312-6a00-4980-ab42-ebb860e65098` attempted one bounded Sol-high
implementation/source checker after runtime build
`0.1.0+codex.20260718175850` was installed. The worker failed before session
creation with `provider emitted no startup event within 30s`: `session_id` was
null, provider exit was `-15`, and telemetry remained at zero tokens and zero
tools. No review claim was produced or used, and the completed primary
investigation was not rerun through another agent.

## Verification

- Focused Combat/Slayer/registry/reachability/runtime/metadata/UI suite:
  **682 tests passed**, with 211 expected non-Qt skips.
- Targeted real offscreen Qt Combat picker: **1 test passed**.
- Full non-Qt discovery: **1,649 tests passed**, including 215 expected
  Qt-environment skips.
- Full real offscreen Qt discovery: **all 1,649 tests executed**, with zero
  skips, failures, or errors.
- Documentation, test-quality, generated-data, compilation, diff,
  Slayer-readiness, reachability-ledger, provenance, and worktree-safety gates
  pass. Test quality reports zero hard issues across 73 files. Reachability is
  an explicit debt ledger: 1,253 actions, 1,838 reachable items, and 297 known
  orphans.
- Results:
  `status-updates/slayer-sea-snakes-results-2026-07-18.html`; mobile copy:
  <https://i3lix9qo57d8.postplan.dev>.
