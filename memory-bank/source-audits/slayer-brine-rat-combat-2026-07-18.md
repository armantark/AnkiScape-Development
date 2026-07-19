# Slayer Brine rat Combat closure

Date: 2026-07-18  
Status: **source closed and implemented with a conservative partial-quest gate**

## Period authority

RuneScape Wiki `Brine rat`, oldid `6555564`, timestamp
`2012-11-14T20:03:25Z`, establishes the ordinary level-70 target:

- 500 LP, Slayer 47, 50 Slayer XP, melee attacks, six-tick attack speed, and a
  93-LP maximum hit;
- passive aggression, no poison, and Vannaka, Chaeldar, and Sumona assignment
  membership;
- guaranteed Bones and Raw rat meat;
- access after partial completion of Olaf's Quest;
- a real Spade, not the toolbelt copy, to enter Brine Rat Cavern; and
- Brine sabre eligibility only after Olaf's Quest is complete.

Pinned page:
<https://runescape.wiki/w/Brine_rat?oldid=6555564>.

The cutoff Vannaka family weight/count contract is already reconciled in
`source-audits/slayer-vannaka-pool-2026-07-17.md`.

## Executable emulator authority

The following Darkan paths were read from
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`:

- `src/main/java/com/rs/game/content/skills/slayer/SlayerTaskManager.java:135-139`
  permits Brine-rat assignment at Olaf's Quest stage 40 or quest completion.
- `src/main/java/com/rs/game/content/skills/slayer/TaskMonster.java:100-108`
  records Slayer 47 and the Olaf's Quest dependency.
- `data/npcs/combatdefs/uncategorized/brine_rat.json:1-30` supplies 500 LP,
  93 maximum hit, passive melee, 59-tick respawn, and exact Attack 70,
  Strength 79, Defence 40, Magic 1, and Ranged 1.
- `developer-information/npcListBonuses.txt:3709` supplies zero attack,
  defence, and strength bonuses.
- `data/npcs/drops/brine_rat.json:1-282` supplies the two rate-zero guaranteed
  drops and all ordinary weighted rows.
- `src/main/java/com/rs/utils/drop/DropList.java:43-68` and `:98-147` establish
  one cumulative ordinary selector for sibling nonzero rows while emitting
  rate-zero rows separately.
- `data/npcs/charmDrops.txt:27` supplies `23-2-1-0` for
  Gold/Green/Crimson/Blue.
- `src/main/java/com/rs/tools/old/CharmDrop.java:54-75` rolls one inclusive
  integer from 0 through 100, admits every qualifying charm, and chooses
  uniformly among overlaps.
- `src/main/java/com/rs/utils/NPCClueDrops.java:78` supplies an independent
  1/128 medium-clue roll.
- `developer-information/itemList.txt:11039` supplies Brine sabre's Attack-40
  gate and cache combat values.

The higher-ranked local 2011Scape item authority at
`/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` item `11037`
supplies the one-handed weapon slot, four-tick attack speed, weapon type 6,
+7 stab, +47 slash, -2 crush, and +46 melee strength.

## Exact selectors

The ordinary table uses a common 512-slot denominator. Every Darkan `/128`
numerator is multiplied by four, the Brine sabre retains one `/512` slot, and
the unused mass is explicit:

| Output | Slots |
|---|---:|
| Coins ×1 | 84 |
| Death runes ×7 | 72 |
| Coins ×2 | 64 |
| Coins ×4 | 36 |
| Earth runes ×10 | 24 |
| Raw lobsters ×10 | 24 |
| Raw sharks ×3 | 24 |
| Earth runes ×36 | 16 |
| Water runes ×10 | 12 |
| Coins ×29 | 12 |
| Water talisman | 12 |
| Air runes ×18 | 8 |
| Earth runes ×18 | 8 |
| Water runes ×18 | 8 |
| Blood runes ×4 | 8 |
| Raw rat meat ×18 | 8 |
| Raw pike ×18 | 8 |
| Raw sharks ×8 | 8 |
| Raw swordfish ×9 | 8 |
| Raw shark | 4 |
| Brine sabre | 1 |
| Empty | 63 |

The charm algorithm is represented exactly over 606 slots. For rates
`23-2-1-0`, inclusive rolls 0 and 1 admit Gold, Green, and Crimson; roll 2
admits Gold and Green; rolls 3 through 23 admit Gold alone. Uniform
overlap selection therefore gives 133 Gold, 7 Green, 4 Crimson, and 462 empty
slots. The 1/128 medium clue remains a third independent selector.

## Access boundary

The real assignment/access permission is Olaf's Quest stage 40. The generated
quest surface currently exposes only completion as a stable semantic state.
Combat therefore records stage 40 in `partial_quest_access` metadata but
enforces the conservative completion gate today. It also requires one ordinary
Spade in the inventory/bank model and never consumes it. This is a bounded
location-access abstraction: it proves the player can enter the cavern without
adding a duplicate quest-stage interpretation.

Because the conservative gate already requires quest completion, every
currently playable Brine-rat kill is eligible for the Brine sabre row. If the
Darkan quest thread later exports stage-40 access, Combat must keep the sabre
suppressed until full quest completion. The handoff is
`codex-briefs/darkan-quest-handoff-brine-rat-2026-07-18.md`.

## Assets and item identity

- `combatenemies/brine_rat.png` is normalized from `Brine rat icon.png`
  revision `2010-06-01T15:33:31Z`, SHA-1
  `4d92645a407cfb9459d7ad16dec422c240228a10`.
- `combatitems/brine_sabre.png` is normalized from `Brine sabre.png` revision
  `2010-10-03T20:34:39Z`, SHA-1
  `d0c7bc96b7394c93bc7436bf38f737a3cfd7f0f2`.

Brine sabre keeps cache item ID 11037, non-stackable/tradeable inventory
shape, and generated source equipment. Its underwater-only Liquefy special is
not exposed because the current Combat action model has neither player-selected
weapon specials nor an underwater encounter. The ordinary weapon is complete;
the special remains a separate future Combat capability, not a hidden fake.

## Scope and design-gap record

No quest stage was implemented or edited. No owner-facing creative-direction
fork emerged. The remaining quest seam has one source-defined answer and is
owned by the Darkan parity thread.

## Workflow review attempt

Read-only Codex Workflows run
`7da08e25-506a-439a-86f5-656ac8ff416d` attempted one bounded Sol-high
source/implementation checker under runtime build
`0.1.0+codex.20260718175850`. It failed before session creation with
`provider emitted no startup event within 30s`: `session_id` remained null,
provider exit was `-15`, and telemetry remained at zero tokens and zero tools.
No reviewer claim was produced or used.

## Verification

Focused Combat, Slayer, registry, generated-equipment, metadata, and UI
coverage passes all 614 methods with 211 expected non-Qt skips. The focused
real offscreen Qt Combat-picker regression passes.

Full non-Qt discovery passes all 1,653 methods with 215 declared Qt-only
skips. Full real offscreen Qt discovery executes all 1,653 methods with zero
skips, failures, or errors. The docs audit passes 325 Markdown and 341 HTML
files; test quality reports zero hard issues; generated equipment is
reproducible; the readiness and reachability ledgers run; `git diff --check`
passes; and the worktree guard reports the canonical runtime layout safe.

Verification results are visualized in
`status-updates/slayer-brine-rat-results-2026-07-18.html`; the mobile copy is
<https://cf55icb0rmwe.postplan.dev>.
