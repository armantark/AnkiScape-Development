# Slayer Green dragon Combat closure

Date: 2026-07-18  
Status: **implemented; no owner-facing design fork**

## Period identity

RuneScape Wiki `Green dragon`, oldid `6565810`, timestamp
`2012-11-17T10:25:21Z`, establishes the ordinary level-79 form at 750 LP,
75 Slayer XP, six-tick attacks, melee plus dragonfire, an 85-LP melee maximum,
500+ unprotected dragonfire, guaranteed Dragon bones and Green dragonhide,
Vannaka assignment membership, and the Wilderness/PKer context.

Source:
<https://runescape.wiki/w/Green_dragon?oldid=6565810>.

The ordinary Wilderness form is the representative. AnkiScape reuses the
owner-approved 1%/250-LP bounded Wilderness ambush and no-grave equipment-loss
rule already closed for Earth warriors. Exact live-player PKer frequency
remains `source_blocked`; it is not presented as an NPC statistic.

## Dragonfire

Pinned Darkan commit
`b50e8826d613b8caf0fb06f19a1a17f50b3b15d9` supplies the executable
dragonfire model:

- `LeatherDragonCombat.java:34-62` selects Green, Blue, Red, and Black dragons,
  requires adjacency, chooses melee on three of four attacks, and otherwise
  rolls flat dragonfire damage uniformly and inclusively from 0–500 LP,
  reduced to 0–50 LP at protection tier 1 and zero at tier 2.
- `PlayerCombat.kt:878-908` makes Super antifire tier 2 by itself. An
  anti-dragon-family shield, Protect/Deflect Magic without a shield, or
  regular Antifire is one layer. Regular Antifire plus a shield or magic
  prayer reaches tier 2. Shield plus prayer remains tier 1.
- `Potions.kt:306-309,434-435` gives both ordinary and super antifire vial and
  flask doses exactly six minutes. At 0.6 seconds per game tick, AnkiScape
  stores 600 review-driven ticks. The timer advances only with gameplay
  cadence and can expire and auto-refresh inside one long Combat review; no
  wall clock is used.

RuneScape Wiki `Dragonfire`, oldid `6534496`, timestamp
`2012-11-04T21:56:22Z`, corroborates close-range dragonfire, the ordinary
chromatic-dragon attack, protection layers, and the six-minute Antifire
duration. `Antifire`, oldid `6469134`, timestamp
`2012-10-25T04:50:15Z`, more directly corroborates regular Antifire plus a
shield or magic protection as complete and Super antifire as complete alone.

Sources:
<https://runescape.wiki/w/Dragonfire?oldid=6534496> and
<https://runescape.wiki/w/Antifire?oldid=6469134>.

The period prose is not fully internally consistent about every intermediate
damage sentence. Darkan's explicit tier function agrees with the Antifire
page's stacking structure, so that executable structure wins. Darkan chooses
dragonfire on 1/4 attacks while game-main
`DragonCombatScript.kt:68-72` chooses 1/10. No pinned period page gives an
exact frequency. The shipped 1/4 row is therefore labeled
`provisional/darkan`, not claimed as historically closed.

## Combat data and drops

The pinned local game-main
`green_dragon_level_79.plugin.kts` supplies:

- 750 LP; Attack, Strength, Defence, and Magic 68; Ranged 1;
- defensive bonuses 20 stab, 40 slash, 40 crush, 30 magic, and 20 ranged;
- 75 Slayer XP;
- guaranteed Dragon bones and Green dragonhide;
- its declared 1,024-way main table and independent 128-way hard-clue table.

The main source table is internally overbooked: its literal rows sum to 1,029
slots despite `total(1024)`. AnkiScape preserves the source rows and selector
total exactly rather than silently altering five odds. Under the cumulative
selector, the final five declared slots are unreachable. This is source
behavior, not a new probability abstraction.

The same plugin's speed 4 and respawn 30 conflict with the period page's speed
6 and Darkan's respawn 59. The higher-ranked period page supplies speed 6;
Darkan supplies respawn 59. Darkan's combat definition independently confirms
750 LP and the 85-LP melee maximum.

The cutoff page invokes a Green-dragon charm template, but the historical
template body is unavailable and neither pinned emulator provides a
Green-dragon charm distribution. Charm rates are `source_blocked`, so this
target does not fabricate them.

## Equipment and item flow

The existing Dragon Slayer quest awards Anti-dragon shield item 1540.
game-main `data/cfg/items.yml:19446-19474` makes it a shield with weight
5.4 kg and exact defences 7 stab, 9 slash, 8 crush, 2 magic, and 8 ranged.
The equipment generator now includes that quest reward as wearable equipment.

Herblore already creates Antifire and Super antifire. Their full vial and
six-dose flask families are now registered as drinkable consumables, preserve
the next-lower dose, and feed the Combat utility-potion loadout. Combat loads
one bottle for a dragon target, prefers Super antifire and the highest dose,
and drinks only when no antifire effect remains.

## UI and runtime mapping

- The target preview shows the current dragonfire state (`None`, `Partial`, or
  `Full`), current breath maximum, and the provisional one-in-four rate.
- The existing Wilderness confirmation includes the current protection state
  without adding a second modal. Transient potion duration is deliberately not
  part of the process-local risk fingerprint, so automatic drinking cannot
  invalidate confirmation every review.
- Runtime feedback reports breath count and LP lost. A dragonfire hit bypasses
  melee accuracy and ordinary melee-prayer reduction, then participates in the
  existing damage, food, reflection, death, undo, and Wilderness-ambush flow.
- Fatal Wilderness ambushes retain the already-settled no-grave behavior.

## Workflow and design-gap record

The bounded read-only Sol-high Codex Workflows run
`5429d102-4660-4810-bc65-6285f497d2a5` produced no review material and failed
before session creation with
`provider emitted no startup event within 30s`. This is the same known
zero-startup-event signature, not a new failure mode. Root independently
reproduced every source and owns implementation and verification.

No new creative-direction question emerged. The frequency conflict and missing
charm table are evidence-confidence issues handled by
`provisional/darkan` and `source_blocked`, respectively.

## Verification

- Focused cadence/Combat/runtime/metadata/equipment/registry/Slayer suite:
  **515 tests passed**.
- Complete non-Qt suite: **1,636 tests passed; 215 declared environment skips;
  zero failures or errors**.
- Targeted real offscreen Qt picker: **2 tests passed**.
- `tools/audit_slayer_readiness.py`: Vannaka is **28/35**, hidden, with seven
  exact Combat-target blockers.
- Documentation, test-quality, generated-equipment, asset-provenance, diff,
  and worktree-layout checks pass.
- Global item reachability retains the repository's known acquisition debt:
  1,251 actions, 1,835 reachable items, 297 orphan inputs, and 324 blocked
  actions. Antifire dose variants follow the same dose-transition reporting as
  existing potion families; no Green-dragon-specific regression appeared.

The self-contained closure report is
`memory-bank/status-updates/slayer-green-dragon-results-2026-07-18.html`
(<https://blwhzxpwaa52.postplan.dev>).
