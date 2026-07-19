# Slayer Warped-tortoise Combat audit — 2026-07-19

Status: **source-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Warped tortoise required by Chaeldar's settled
assignment registry. It closes the visible period identity, quest/Slayer gate,
combat style/cadence, invulnerability concept, crystal-chime window, named
drops, cache IDs, and Darkan execution boundary. It does **not** add
`warped_tortoise` to `COMBAT_ENEMY_DATA`.

Darkan explicitly marks the only combat definition `nostats`, supplies a
maximum which conflicts with the cutoff page, contains no executable
crystal-chime vulnerability handler, and reconstructs an ordinary selector
which omits or contradicts major period rows. The target is not
runtime-certifiable.

Chaeldar remains hidden at **25/34**. `warped_tortoises` retains its
`combat_target` blocker and the declared `crystal_chime` readiness feature
remains incomplete.

## Period evidence

RuneScape Wiki `Warped tortoise`, oldid `6547916`, timestamp
`2012-11-11T07:09:33Z`, literal wikitext establishes:

- level 96, 870 LP, Slayer 56, and 87 Slayer XP;
- completion of The Path of Glouphrie before assignment;
- passive six-tick melee with a 120-LP maximum;
- poison susceptibility;
- Crush, then Slash, then Ranged weakness;
- guaranteed Big bones;
- complete invulnerability until a Crystal chime is used;
- a 45-second vulnerable window after chiming;
- the named weapon/armour, ore, rune/talisman, shell, food, resource,
  Spin-ticket, effigy, and rare-drop-table sets; and
- assignment membership for Chaeldar, Sumona, and Kuradal.

Source:
<https://runescape.wiki/w/Warped_tortoise?oldid=6547916>.

Cutoff `Talk:Warped tortoise`, oldid `6043450`, timestamp
`2012-08-05T09:03:54Z`, corroborates:

- charm drops, including observed Gold, Green, Crimson, and Blue;
- Tortoise shells in batches of one to three;
- substantially more frequent shell drops than ordinary tortoises; and
- the unresolved player-facing Crush/Slash prose inconsistency.

It does not expose hidden combat levels, the exact charm selector, or ordinary
drop rates:
<https://runescape.wiki/w/Talk:Warped_tortoise?oldid=6043450>.

The settled no-wall-clock rule requires any future 45-second vulnerability
state to advance through review-driven Combat/cadence state and roll back with
review undo. This source pass does not choose or reopen its exact review
chunking.

## Cache and executable evidence

Rev-742 contains Warped tortoise NPCs 6296 and 6297. Darkan's cache-derived
bonus dump records zeroed attack, defence, and strength bonuses for both.
The client layer proves identities, not server levels or vulnerability logic.

Pinned Darkan paths and commits:

- incomplete combat row:
  `data/npcs/combatdefs/uncategorized/warped_tortoise (nostats).json`, commit
  `14e49a561bab1441384022421d10dc03a8d837f0`;
- ordinary drops:
  `data/npcs/drops/warped_tortoise.json`, commit
  `9fee66a1548441d2d954303348557aa18c1a0c7a`;
- charm thresholds:
  `data/npcs/charmDrops.txt:171`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`; and
- cache bonuses:
  `developer-information/npcListBonuses.txt:6298-6299`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`.

The Darkan combat row agrees on 870 LP, passive melee, and the visible
identity. It supplies a 106 maximum against the cutoff 120 and a four-tick
respawn, while omitting every combat level. Its `nostats` name causes
`NPCCombatDefinitions.getDefs()` to generate equal non-real levels. No
Warped-tortoise or item-11749 combat handler exists in the executable source;
the Crystal chime appears only in quest/item state. Darkan therefore does not
implement the target's defining vulnerability loop.

Darkan's main selector scales losslessly to 100,000 slots:

- four common rows at 21,028 slots each;
- ten uncommon rows at 1,401 slots each;
- two rare rows at 934 slots each; and
- 10 empty slots.

It is not source-ready:

- noted Mithril ore is ×1–3 against the cutoff ×3–9;
- Law runes are ×2–3 against ×3–6;
- Coins are ×33–49 against ×30–180;
- noted Coal is ×1–6 against ×6–16;
- Tangled toads' legs are ×1–16 against ×1–4; and
- Tortoise shells, Perfect shells, Rune warhammer, Tortoise-shell batches,
  and other named period rows are absent.

Guaranteed Big bones and the independent long/curved-bone table are useful
leads but cannot make the conflicting atomic drop transaction shippable.

Darkan charm thresholds `9-4-3-4` losslessly enumerate to a 303-slot lead:
19 Gold, 4 Green, 3 Crimson, 4 Blue, and 273 empty. The cutoff talk history
corroborates all four charm colors but not that distribution. Darkan has no
Warped-tortoise clue row, matching the cutoff article's omission.

## Blocking findings

1. **Combat levels are absent.** Darkan generates explicitly non-real levels.
2. **The maximum conflicts.** Darkan's 106 disagrees with the cutoff 120.
3. **The defining Crystal-chime handler is absent.** Item existence and quest
   reward text do not prove an executable 45-second vulnerability state.
4. **The ordinary selector conflicts and omits attested content.** Multiple
   quantities disagree and the shell/resource rows are incomplete.
5. **The canonical acquisition/use dependency is not live in AnkiScape.** The
   current quest gate does not itself create a carried Crystal chime item or
   atomic Combat action.

## Explicit omissions

- No sprite, Crystal-chime icon, shell/resource icons, target row, or runtime
  action was installed because the target is not source-certifiable.
- Warped terrorbirds, quest-stage boss encounters, Poison Waste travel,
  Regicide/Fur 'n' Seek conditional drops, cannon behavior, and ordinary
  tortoises are outside this family audit.
- The exact hidden levels, respawn, selector rates, and any chime-refresh
  behavior remain `source_blocked`.

## Required unblock

Activate Warped tortoises only after a period-lineage source closes the five
combat levels and 106/120 conflict, a reconciled selector preserves the cutoff
drop set, and the canonical quest reward plus non-consumed Crystal-chime
Combat action exist atomically. Copying Darkan's generated levels or
conflicting selector would violate the source standard.

No owner-facing design question emerged. These are source and dependency
blockers under the 2026-07-19 closed-design rule.
