# Slayer Kurask Combat audit — 2026-07-19

Status: **source-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary level-106 Kurask required by Chaeldar's settled
assignment registry. The identity, complete combat levels, Slayer gate/XP,
melee behavior, restricted effective-damage routes, respawn, cache bonuses,
guaranteed Bones, charm lead, and hard-clue lead are source-ready. The
ordinary-drop selector is not.

Darkan's ordinary selector directly conflicts with several visible cutoff
quantities, most notably 20 noted Big bones against one or two ordinary Big
bones. Under the source standard, emulator values that conflict with the period
record are leads rather than facts. This pass therefore does **not** add
`kurask` to `COMBAT_ENEMY_DATA`, even though the existing Turoth restricted
weapon seam could represent its kill loop without new design.

Chaeldar remains hidden at **25/34**. `kurasks` retains its `combat_target`
blocker and no readiness denominator is changed.

## Period evidence

RuneScape Wiki `Kurask`, oldid `6581220`, timestamp
`2012-11-19T07:06:07Z`, literal wikitext establishes:

- level 106, 970 LP, Slayer 70, and 97 Slayer XP;
- aggressive six-tick melee with a 120-LP maximum;
- poison immunity;
- guaranteed Bones;
- assignment membership for Chaeldar and Sumona;
- ineffective player attacks unless they use a Leaf-bladed sword,
  Leaf-bladed spear, Magic Dart with Magic 50 and a Slayer's staff, Broad
  arrows, or Broad-tipped bolts;
- explicit ineffectiveness of dwarf multicannon damage;
- the complete named rune, broad-ammunition, weapon, armour, Herblore
  ingredient, herb, seed, food, resource, hard-clue, head, Spin-ticket,
  effigy, and rare-drop-table sets; and
- visible quantities including Coins ×22–748, noted Flax ×20–30, Bones ×1–2,
  Big bones ×1–2, Banana ×1–2, and Pineapple ×2–8, normally noted.

Source:
<https://runescape.wiki/w/Kurask?oldid=6581220>.

Cutoff `Talk:Kurask`, oldid `1093691`, timestamp
`2009-03-28T16:14:41Z`, contains only a rejected uncorroborated Amulet-of-glory
report and a cannon discussion consistent with the article's ineffective
damage. It supplies no hidden selector:
<https://runescape.wiki/w/Talk:Kurask?oldid=1093691>.

The ordinary level-106 representative follows the settled
one-representative-per-Slayer-family rule. The period article proves every
effective-damage route which the already-live Turoth lock represents.

## Cache and executable combat evidence

Rev-742 contains two ordinary level-106 Kurask identities, NPCs 1608 and 1609.
Darkan's cache-derived bonus dump gives both zero attack bonuses,
Slash/Crush defence `20/20`, zero Stab/Magic/Ranged defence, and zero strength
bonuses.

Pinned Darkan paths and commits:

- combat row:
  `data/npcs/combatdefs/uncategorized/kurask.json`, commit
  `14e49a561bab1441384022421d10dc03a8d837f0`;
- restricted-damage handler:
  `src/main/java/com/rs/game/content/items/CombatEnhancers.kt:135-155`,
  gate lineage introduced by commit
  `b79e684f651c57820fa8a8121e0257468930f8ad` and present through the current
  file revision;
- cache bonuses:
  `developer-information/npcListBonuses.txt:1610-1611`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- ordinary drops:
  `data/npcs/drops/kurask.json`, commit
  `9fee66a1548441d2d954303348557aa18c1a0c7a`;
- charm thresholds:
  `data/npcs/charmDrops.txt:114`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`; and
- hard clue:
  `src/main/java/com/rs/utils/NPCClueDrops.java:136`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

The combat JSON is a complete real-stat row: 970 LP, Attack 67, Strength 105,
Defence 105, Magic 1, Ranged 1, aggressive melee, a 120 maximum, and a 59-tick
respawn. Unlike the preceding blocked Chaeldar targets, it is not marked
`nostats` and does not invoke generated levels.

`CombatEnhancers.kt` applies the same effective-damage gate to Turoth and
Kurask:

- melee requires item 4158 or 13290, the Leaf-bladed spear or sword;
- Ranged requires compatible Broad arrows or Broad-tipped bolts; and
- Magic requires `MAGIC_DART`.

That handler, the cutoff article, and AnkiScape's live Turoth behavior agree.
The existing `restricted_weapon` schema is sufficient; no new mechanic or
owner decision is needed.

## Executable drop evidence and conflict

Darkan models guaranteed Bones and the long/curved-bone tertiary as
independent zero-rate-table entries. Its remaining entries form one cumulative
selector. The common denominator for the direct `n/124`, Leaf-bladed-sword
`1/384`, and Mystic-robe-top-light `1/512` rows is 47,616:

| Output | Slots |
|---|---:|
| Darkan herb subtable | 6,912 |
| Darkan rare-seed subtable | 5,760 |
| Darkan gem subtable | 2,304 |
| Coins ×22 | 6,144 |
| Nature runes ×10 | 3,456 |
| Nature runes ×15 | 2,688 |
| Limpwurt roots ×2 | 2,304 |
| Noted Flax ×25 | 2,304 |
| White berries ×1 | 2,304 |
| Coins ×500–748 | 1,920 |
| Noted Big bones ×20 | 1,920 |
| Nature runes ×30 | 1,536 |
| Pineapples ×2 | 1,536 |
| Bananas ×1–2 | 1,536 |
| Mithril kiteshield | 1,152 |
| Rune longsword | 1,152 |
| Adamant platebody | 1,152 |
| Mithril hatchet | 1,152 |
| Leaf-bladed sword | 124 |
| Mystic robe top (light) | 93 |
| Empty | 167 |

This selector is executable, but not source-ready:

- `Noted Big bones ×20` directly contradicts the cutoff `Big bones ×1–2`;
- unnoted `Pineapple ×2` does not preserve the cutoff `Pineapple ×2–8`,
  normally noted;
- the two Coin rows produce only 22 or 500–748 rather than the cutoff
  22–748 range; and
- the executable file omits several period-visible broad-ammunition and
  resource rows while routing substantial probability through generic nested
  tables.

The standard requires every period-proven output to survive exactly and says
an emulator implementation that conflicts with the period record is a lead,
not a fact. The root therefore did not cherry-pick the combat row while
inventing or pruning its loot transaction.

Darkan's charm thresholds are `9-27-6-1`. Lossless enumeration of
`CharmDrop.getCharmType()` produces a 1,212-slot lead: 44 Gold, 260 Green,
26 Crimson, 6 Blue, and 876 empty. The cutoff article corroborates charm drops
but not that distribution. Darkan supplies an independent hard clue at 1/128;
the cutoff article corroborates the tier but not the rate.

## Blocking findings

1. **The ordinary selector conflicts with the period record.** The noted
   Big-bones quantity is the clearest contradiction; Pineapple and Coin
   handling also fail to preserve visible cutoff quantities.
2. **The cutoff drop set is not represented completely.** Broad ammunition
   and several named resource rows cannot silently disappear behind generic
   nested tables.
3. **Charm and clue rates remain emulator leads.** Their content is attested,
   but no independent period value recovered here closes the exact rates.

The combat stats and effective-damage routes themselves are not blocked.

## Explicit omissions

- The one-off Kurask overlord, Kurask minions, Kurask head uses, Kurask pet,
  Desert/Fremennik dungeon routing, and other Slayer-master pools are outside
  this ordinary-family slice.
- No Kurask sprite or new drop icons were installed because the target is not
  runtime-certifiable.
- No restricted-weapon code was changed; Turoth already exercises the exact
  settled route.

## Required unblock

Activate the ordinary Kurask only after a period-lineage or independently
corroborated executable selector reconciles every visible quantity and retains
the period drop set. The already-closed 67/105/105/1/1 combat row and Turoth
restriction seam can then be adopted without reopening design.

No owner-facing design question emerged. This is a source conflict under the
2026-07-19 closed-design rule, not a design gap.
