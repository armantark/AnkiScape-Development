# Slayer Waterfiend Combat audit — 2026-07-19

Status: **source- and context-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits Waterfiends for the settled Duradel/Lapalok and Kuradal
assignment pools. The cutoff record closes the ordinary level-115 Waterfiend's
identity, LP, Slayer XP, dual Magic/magical-Ranged style, maximum hit, attack
interval, weakness, locations, guaranteed drop, and visible loot contents.
Darkan independently closes its real combat levels, cache defences, respawn,
dual-style selector, and an exact ordinary/charm/clue reconstruction.

The exact ordinary selector is not source-ready. Darkan contradicts the cutoff
table on Coins, Water-rune, Death-rune, Snape-grass, Seaweed, Water-orb, fish,
ore, and bar quantities. Its name-wide selector also includes a Ghorrock-only
Coal row without distinguishing the level-134 Ghorrock form from regular
level-115 Waterfiends.

This pass therefore does **not** add `waterfiend` to `COMBAT_ENEMY_DATA`.
Duradel/Lapalok remains hidden at **14/35**. `waterfiends` retains its
`combat_target` blocker and no denominator is changed.

## Settled variant boundary

The owner-settled family currently binds the live certifying floor to
`("waterfiend",)` and declares `location_context`. Slayer Owner decision 20
allows one fully functional ordinary variant to certify the family, but it
does not shrink the cutoff family definition. Other qualifying variants remain
named implementation debt until their own target, context, and mechanics are
runtime-ready.

The future `waterfiend` target is therefore the ordinary level-115 form found
in the Ancient Cavern and Chaos Tunnels. The level-134 Ghorrock form is a
separate qualifying variant because the cutoff article gives it a distinct
charm table and location-only drops. It may not be folded into the ordinary
target or silently share those outputs.

This is the owning contract's already-settled certification rule, not a new
representative choice or owner-facing design fork.

## Period evidence

RuneScape Wiki `Waterfiend`, oldid `6533288`, timestamp
`2012-11-04T15:58:28Z`, literal wikitext establishes:

- level 115 and 134 identities, 1,260 LP, Slayer 1, and 128 Slayer XP;
- aggressive, poison-immune Magic and magical-Ranged attacks;
- a six-tick engine interval and 119-LP maximum;
- Crush weakness;
- Ancient Cavern access through Barbarian Training's pyre-ship stage, plus
  Chaos Tunnels and Ghorrock locations;
- a guaranteed Water rune ×1;
- separate regular and Ghorrock charm templates;
- the complete visible rune, seed, weapon/armour, herb, ore/bar, fish, other,
  tertiary, and rare-table contents;
- Coal, Gold ore, Zamorak brew (1), Cannonballs, and Saradomin brew (1) as
  Ghorrock-only rows; and
- the ordinary quantity envelopes used in the conflict table below.

Source:
<https://runescape.wiki/w/Waterfiend?oldid=6533288>.

Cutoff `Talk:Waterfiend`, oldid `5778590`, timestamp
`2012-06-19T09:30:58Z`, independently records:

- both attacks rolling against Magic defence;
- the Ghorrock/Ice Plateau form's two-charm quantity, lower charm yield, and
  additional brew/cannonball drops;
- a 202-kill regular sample of 27 Gold, 7 Green, 158 Crimson, and 3 Blue
  charms, which is useful corroboration but not an exact distribution; and
- ordinary herb reports that do not supply executable selector weights.

Source:
<https://runescape.wiki/w/Talk:Waterfiend?oldid=5778590>.

The legacy `Charm:Waterfiend` dependencies no longer have recoverable
pre-cutoff revisions in the current Wiki API. The article and talk history
prove separate charm behavior and approximate composition, not exact rates.

## Cache and executable combat evidence

Rev-742 contains attackable Waterfiends at NPCs `5361`, `9054`, and
`9056`–`9059` at level 115, plus NPC `9077` at level 134. Darkan's real-stat
definitions give both forms:

| Field | Value |
|---|---:|
| LP | 1,260 |
| Attack | 0 |
| Strength | 0 |
| Defence | 128 |
| Magic | 105 |
| Ranged | 105 |
| Maximum hit | 119 |
| Respawn | 59 ticks |
| Stab defence | 100 |
| Slash defence | 100 |
| Crush defence | 10 |
| Magic defence | 100 |
| Ranged defence | 100 |
| Attack bonuses | 0 |
| Strength bonuses | 0 |

The custom handler for NPC `5361` chooses an inclusive three-way selector:
two Ranged branches and one Magic branch. All branches use the same 119-LP
envelope. This converges with the cutoff dual-style identity and maximum.

Pinned Darkan paths and commits:

- level-115 and level-134 combat rows:
  `data/npcs/combatdefs/uncategorized/waterfiend/`, commit
  `ff86351405926e82d0ef2f3aabeb0545b15b3062`;
- dual-style handler:
  `src/main/java/com/rs/game/content/world/npcs/WaterfiendCombat.java`, commit
  `e1e71c9fb5979ba72bc66f4a251c725c8d0e1239`;
- cache-derived defences:
  `developer-information/npcClientScriptData.txt:1292,2399,2401-2404,2418`
  and
  `developer-information/npcListBonuses.txt:5363,9056,9058-9061,9079`,
  commit `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- ordinary drops:
  `data/npcs/drops/waterfiend.json`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- charm thresholds:
  `data/npcs/charmDrops.txt:172`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`; and
- hard clue:
  `src/main/java/com/rs/utils/NPCClueDrops.java:153`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

## Executable selector conflict

Darkan's ordinary selector totals exactly 128 slots and always gives Water
rune ×1 first. It is executable but incompatible with the cutoff table:

| Output | Cutoff quantity | Darkan quantity / slots |
|---|---:|---:|
| Coins | 97–692 | 1,200 / 15 |
| Water rune | 90 | 150 / 6 |
| Death rune | 9–19 | 23 / 5 |
| Mud rune | 3–9 | 2 / 8 |
| Snape grass | 20 noted | 40 / 4 and 6 / 2 |
| Seaweed | 10–29 noted | 25–75 / 2 |
| Water orb | 5–10 noted | 5–15 / 3 |
| Raw lobster | 5–12 | 4 / 3 |
| Raw swordfish | 5–7 | 2 / 3 |
| Raw shark | 3–6 | 2 / 3 |
| Mithril ore | 1–5 noted | 2–4 / 4 |
| Mithril bar | 2 | 10–15 / 1 |
| Steel bar | 3 noted | 6 / 2 |
| Coal | 1–6 noted, Ghorrock only | 3 / 2, name-wide |

The selector also collapses the cutoff paired-herb behavior into one generic
herb-table roll and omits many visible period rows. Because the period page
supplies rarity labels rather than numeric rates, the conflicting emulator
weights cannot be transplanted onto corrected contents.

Darkan's regular charm thresholds are `9-5-79-2` with quantity one. Lossless
enumeration of its inclusive threshold-and-shuffle algorithm yields a
1,212-slot lead: 45 Gold, 21 Green, 885 Crimson, 9 Blue, and 252 empty. This
is directionally compatible with the cutoff article's “around 75%” Crimson
statement and the talk sample, but those sources do not close the exact
distribution. Darkan independently supplies a hard clue at 1/128; the cutoff
article corroborates the tier but not the rate.

## Context representation boundary

The settled family explicitly requires `location_context`. The current Combat
target schema has no player-selectable Ancient Cavern/Chaos Tunnels/Ghorrock
context transaction. Merely setting a truthy `location_context` metadata flag
would satisfy the readiness checker without implementing the route choice,
variant-local charm/drop behavior, or atomic persistence required by the
contract. That would be false certification and is not done here.

## Blocking findings

1. **The exact ordinary selector contradicts the cutoff table.** Multiple
   quantities and contents are incompatible, including Coins ×1,200 versus
   the period 97–692 envelope.
2. **The emulator table leaks Ghorrock-only content.** A name-wide Coal row
   cannot distinguish the ordinary and level-134 location variant.
3. **Exact charm and clue rates remain emulator leads.** Their content and
   broad behavior are attested, but the transcluded historical rate tables did
   not survive.
4. **The required context transaction is absent.** A metadata-only readiness
   flag would not implement the settled route and variant boundary.

## Explicit omissions

- The level-134 Ghorrock target, its quantity-two charm table, and its
  location-only loot remain named implementation debt.
- Ghorrock Fortress quest-stage access remains owned by the Darkan quest
  parity thread; no quest file was edited.
- Cannon use, safespots, gear advice, familiars, and hourly charm strategy are
  not target mechanics.
- No target sprite or drop icons were installed because neither certifying
  target nor context is runtime-ready.

## Required unblock

Activate the ordinary `waterfiend` only after:

1. a period-lineage or independently corroborated executable selector
   reconciles the cutoff contents and quantities;
2. the regular charm selector receives a source-closed rate or a
   contract-authorized labeled fallback; and
3. the settled location-context transaction exists without admitting Ghorrock
   outputs to the ordinary target.

The level-115 combat row, exact cache defences, 59-tick respawn, 119-LP
maximum, guaranteed Water rune, and dual-style handler can then be adopted
without reopening design.

No owner-facing design question emerged. This is source and implementation
debt under the 2026-07-19 closed-design rule.
