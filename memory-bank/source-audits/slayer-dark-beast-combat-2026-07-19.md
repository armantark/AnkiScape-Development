# Slayer Dark beast Combat audit — 2026-07-19

Status: **source-, context-, and representation-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Dark beast required by the settled
Duradel/Lapalok and Kuradal pools. The cutoff record closes its level, LP,
Slayer level/XP, conditional Melee/Magic identity, attack interval, maxima,
weakness, guaranteed drop, locations, and visible loot contents. Darkan closes
real combat levels, cache defences, and respawn, but its combat row has a
zero maximum and its exact drop/charm reconstruction conflicts with the cutoff
record.

The current shared family schema also cannot preserve the two settled context
routes. Duradel/Lapalok's ordinary target requires the Temple-of-Light route;
Kuradal's Dungeon supplies a task-local variant that explicitly avoids that
quest route. A single global family feature would import one context into the
other.

This pass therefore does **not** add `dark_beast` to `COMBAT_ENEMY_DATA`.
Duradel/Lapalok remains hidden at **14/35**. `dark_beasts` retains its
`combat_target` blocker and no denominator is changed.

## Settled family and context boundary

The family registry names `("dark_beast", "revenant_dark_beast")`. The cutoff
article states that Revenant dark beasts may substitute on a Dark-beast task,
so both identities remain in the stable family ledger.

Slayer Owner decision 20 permits the ordinary level-182 Dark beast to certify
the family once one fully functional route is live. It does not flatten the
level-120 Revenant into that target. The Revenant remains separately named
implementation debt with its own Wilderness/context mechanics.

The owning pool audits distinguish:

- the Mourner Tunnels/Temple of Light route for Duradel/Lapalok; and
- Kuradal's task-only Dungeon route, which does not require Mourning's Ends
  Part II.

The existing `slayer_data.py` family-level
`readiness_features=("temple_of_light_context",)` cannot express that
master-specific split. The authoritative conflict and required schema repair
are already recorded in
`audits/slayer-kuradal-registry-schema-conflict-2026-07-19.md`. No new design
choice is introduced here.

## Period evidence

RuneScape Wiki `Dark beast`, oldid `6516256`, timestamp
`2012-11-01T16:36:24Z`, literal wikitext establishes:

- level 182, 2,200 LP, Slayer 90, and 225.4 Slayer XP;
- aggressive, poison-susceptible Melee and Magic attacks;
- six-tick attacks;
- a 174-LP Melee maximum and 80-LP Magic maximum;
- Slash/Stab weakness;
- conditional style behavior: a beast that initiates in melee range stays
  Melee, while a player-initiated or out-of-range encounter opens with Magic;
- Mourner Tunnels and Kuradal's Dungeon locations with their distinct access
  rules;
- guaranteed Big bones;
- the complete visible weapons, armour, runes, herbs, other, tertiary, and
  rare-table contents;
- Dark bow estimated at 1/486 from a cutoff Adventurer's Log sample;
- a stated 14% Blue-charm chance; and
- Ferocious ring as a Kuradal's-Dungeon-only drop.

Source:
<https://runescape.wiki/w/Dark_beast?oldid=6516256>.

Cutoff `Talk:Dark beast`, oldid `5485204`, timestamp
`2012-04-13T14:34:36Z`, discusses Blue-charms, clue/drop-table omissions,
Coins above 3,000, and rare-table reports. It supplies no executable ordinary
selector and does not reconcile the conflicts below:
<https://runescape.wiki/w/Talk:Dark_beast?oldid=5485204>.

The historical `Charm:Dark beast` transclusion no longer has a recoverable
pre-cutoff revision in the current Wiki API. The article's direct 14% Blue
statement survives independently.

The two context contracts remain pinned in:

- `source-audits/slayer-location-contexts-2026-07-15.md`;
- `source-audits/slayer-duradel-lapalok-pool-2026-07-17.md`; and
- `source-audits/slayer-kuradal-pool-2026-07-17.md`.

## Cache and executable combat evidence

Rev-742 and Darkan identify NPC `2783` as the attackable level-182 Dark beast.
Darkan's real-stat row and cache-derived defences provide:

| Field | Value |
|---|---:|
| LP | 2,200 |
| Attack | 140 |
| Strength | 160 |
| Defence | 120 |
| Magic | 160 |
| Ranged | 1 |
| Respawn | 59 ticks |
| Stab defence | 30 |
| Slash defence | 40 |
| Crush defence | 100 |
| Magic defence | 90 |
| Ranged defence | 100 |
| Attack bonuses | 0 |
| Strength bonuses | 0 |

Pinned Darkan paths and commits:

- ordinary combat row:
  `data/npcs/combatdefs/uncategorized/dark_beast.json`, commit
  `14e49a561bab1441384022421d10dc03a8d837f0`;
- cache-derived defences:
  `developer-information/npcClientScriptData.txt:722` and
  `developer-information/npcListBonuses.txt:2785`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- ordinary drops:
  `data/npcs/drops/dark_beast.json`, commit
  `9fee66a1548441d2d954303348557aa18c1a0c7a`;
- charm thresholds:
  `data/npcs/charmDrops.txt:46`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`;
- hard and elite clues:
  `src/main/java/com/rs/utils/NPCClueDrops.java:124,185`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

Darkan's combat row is not an executable damage authority: it fixes the target
to Melee and stores `maxHit: 0`, with no Dark-beast custom handler. The direct
cutoff 174/80 maxima and conditional style rule supersede that incomplete
emulator behavior.

## Executable selector conflict

Darkan has guaranteed Big bones, the shared long/curved-bone tertiary, a
127/128 ordinary selector, and an independent Dark bow at 1/512. The visible
ordinary selector includes:

- shared herb, rare-seed, standard rare, and gem-table rolls;
- Coins ×64/95/152/220;
- Death runes ×20, Chaos runes ×30, and Blood runes ×15;
- Black battleaxe, Sharks, noted Adamant bars, Adamant sq shield, Rune
  chainbody, Rune med helm, Rune full helm, Rune 2h sword, Rune battleaxe,
  noted Coal, and Runite ore.

It conflicts with the cutoff contents and quantities:

| Output | Cutoff | Darkan |
|---|---|---|
| Coins | 64, 95, 152, 220, 299, 3,000 | omits 299 and 3,000 |
| Death rune | 3–5 | 20 |
| Chaos rune | 10 | 30 |
| Blood rune | 7 | 15 |
| Herbs | each visible herb ×1–2 | one generic herb roll |
| Dark bow | estimated 1/486 | 1/512 |
| Black 2h sword / hatchet | visible | absent |
| Rune sq shield | visible | absent |
| Rune med helm | not visible | present |
| Attack potion / Death talisman | visible | absent |

The period page supplies rarity labels rather than the numeric rates needed to
rebuild the mutually exclusive selector. Emulator weights cannot be copied
onto a materially different item/quantity set.

Darkan's charm thresholds are `9-4-8-14`, quantity one. Lossless enumeration
of its inclusive threshold-and-shuffle algorithm yields a 1,212-slot lead:
37 Gold, 15 Green, 31 Crimson, 97 Blue, and 1,032 empty. That is approximately
8.0% Blue, directly conflicting with the cutoff page's 14% statement.

Darkan supplies hard clue 1/128 and elite clue 1/1,200. The cutoff article at
this revision does not list clue scrolls, while the talk page contains only an
unsourced omission complaint. Those tertiary rates remain emulator-only leads.

## Representation boundary

The period conditional attack rule is not equivalent to one fixed
`attack_style`. Current Combat supports one enemy style, plus a few
source-specific player-class mappings, but it has no encounter opener/range
state that can express an 80-LP Magic opener followed by 174-LP Melee once the
enemy closes.

The target also cannot honestly set `temple_of_light_context=True` as a bare
metadata flag. The settled route must be player-selectable and master-local,
and its eligibility/loot consequences must commit atomically. A truthy flag
would satisfy readiness without implementing those rules.

## Blocking findings

1. **The ordinary selector conflicts with the cutoff table.** Exact Darkan
   weights cannot be transferred to different contents and quantities.
2. **The charm rate conflicts directly.** Darkan's executable selector gives
   about 8% Blue while the cutoff article states 14%.
3. **The conditional dual-style fight is not representable.** Fixed Melee
   would discard the sourced Magic opener and its distinct maximum.
4. **The context gate is master-specific.** The current global family feature
   contradicts the settled Kuradal route and cannot certify an atomic context.

## Explicit omissions

- Revenant dark beast remains a separate future target; no Revenant stats,
  drops, Wilderness risk, or asset were folded into the ordinary row.
- Kuradal's Dungeon, Ferocious-ring drops/effects, and Ancient Cavern access
  remain owned by the existing context/schema blocker.
- Mourning's Ends quest-stage parity remains owned by the Darkan quest thread;
  no quest file was edited.
- No target sprite or drop icons were installed because the target is not
  runtime-certifiable.

## Required unblock

Activate the ordinary Dark beast only after:

1. a period-lineage or independently corroborated selector reconciles the
   cutoff contents and quantities;
2. charm probabilities reconcile the direct 14% Blue statement;
3. Combat can preserve the sourced Magic-opener/Melee-close transaction with
   separate maxima; and
4. the master-specific Temple/Kuradal context schema is repaired.

The level-182 identity, 2,200 LP, 225.4 Slayer XP, real combat levels, exact
cache defences, 59-tick respawn, guaranteed Big bones, and direct 174/80
period maxima can then be adopted without reopening design.

No owner-facing design question emerged. These are source and implementation
blockers under the 2026-07-19 closed-design rule.
