# Slayer Suqah Combat audit — 2026-07-19

Status: **source-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Suqah required by the settled Duradel/Lapalok
assignment registry. The identity, Lunar Diplomacy gate, southern
Slayer-representative attack style, level, LP, Slayer XP, maximum hit, combat
levels, cache bonuses, attack speed, respawn, guaranteed drops, charms,
long/curved-bone tertiary, and hard-clue lead are recoverable. The ordinary
drop selector is not source-ready.

The cutoff page names Grimy guam and Grimy marrentill. Darkan's executable
129-way selector instead names Grimy ranarr and Grimy irit. The period page
does not supply numeric rates which could rebuild a selector around its own
contents. Under the source standard, the lower-tier executable table is a lead
rather than a fact when it conflicts with the pinned period record.

This pass therefore does **not** add `suqah` to `COMBAT_ENEMY_DATA`.
Duradel/Lapalok remains hidden at **14/35**. `suqahs` retains its
`combat_target` blocker and no denominator is changed.

## Settled target boundary

The newest owning registry binds the family to exactly `("suqah",)` behind
`lunar_diplomacy`; it does not declare separate northern and southern Combat
targets. The cutoff article supplies the corresponding ordinary
representative rule: southern Suqahs do not use Magic and are the more common
Slayer-task target.

Accordingly, the future single `suqah` row is the southern melee-only Slayer
representative. This does not flatten or reinterpret the separately attested
northern blue-shield forms, which may use Ice Barrage or Water Wave. It follows
the already-settled one-target registry and the period article's explicit
Slayer route. No new owner choice is introduced.

## Period evidence

RuneScape Wiki `Suqah`, oldid `6554227`, timestamp
`2012-11-14T02:56:50Z`, literal wikitext establishes:

- combat level 111, 1,050 LP, Slayer 1, and 107.6 Slayer XP;
- aggression, poison susceptibility, and a six-tick engine attack interval
  represented as speed `4` on the period Wiki scale;
- melee and Magic variants, with southern non-magic Suqahs identified as the
  common Slayer target;
- a 109-LP melee maximum for that representative;
- northern forms using weak Ice Barrage or Water Wave, including a
  100-LP landed Ice Barrage and approximately five seconds of movement freeze;
- Lunar Isle access after starting Lunar Diplomacy;
- guaranteed Big bones and Suqah hide;
- named Long bone, Curved bone, Suqah tooth, Grimy guam, Grimy marrentill,
  hard clue, anagogic-ort, Coin, spin-ticket, effigy, and rare-drop-table
  families.

Source:
<https://runescape.wiki/w/Suqah?oldid=6554227>.

The immediately preceding intact drop-table revision is oldid `6380099`,
timestamp `2012-10-10T17:26:02Z`. It independently contains the same Grimy
guam and Grimy marrentill rows. Oldid `6471540` temporarily replaced the drop
section with vandalism; the nearest cutoff revision restored the earlier
table rather than introducing the herb names:

- <https://runescape.wiki/w/Suqah?oldid=6380099>
- <https://runescape.wiki/w/Suqah?oldid=6471540>

Cutoff `Talk:Suqah`, oldid `5813428`, timestamp
`2012-06-23T18:55:12Z`, discusses weapon weakness, charm-log maintenance,
rare-drop-table access, and an unsupported effigy-rarity inference. It supplies
no ordinary-drop weights and does not reconcile the herb conflict:
<https://runescape.wiki/w/Talk:Suqah?oldid=5813428>.

The article transcludes `Template:Charm:Suqah`, but no pre-cutoff revision of
that dependency was recovered by the pinned history tool. The article proves
charm content, not Darkan's exact rates.

## Cache and executable combat evidence

Rev-742 contains seven attackable level-111 `Suqah` identities, NPCs
`4527`–`4533`, each with an `Attack` option. Darkan's cache-derived data gives
all seven the same six-tick interval and exact defences:

| Field | Value |
|---|---:|
| Stab defence | 50 |
| Slash defence | 70 |
| Crush defence | 70 |
| Magic defence | 90 |
| Ranged defence | 50 |
| Attack bonuses | 0 |
| Strength bonuses | 0 |

Pinned Darkan paths and commits:

- combat row:
  `data/npcs/combatdefs/uncategorized/suqah.json`, commit
  `2a6bd7abcf8390ba9d595ecc834d181a93a5dcf4`;
- northern/southern handler:
  `src/main/java/com/rs/game/content/world/npcs/SuqahCombat.java`, commit
  `347552cad462e96670e3ff04228c0232881da9f5`;
- cache-derived interval and defences:
  `developer-information/npcClientScriptData.txt:1092-1098` and
  `developer-information/npcListBonuses.txt:4529-4535`;
- ordinary drops:
  `data/npcs/drops/suqah.json`, commit
  `9fee66a1548441d2d954303348557aa18c1a0c7a`;
- charm thresholds:
  `data/npcs/charmDrops.txt:153`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`; and
- hard clue:
  `src/main/java/com/rs/utils/NPCClueDrops.java:149`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

The combat JSON is a real-stat row: 1,050 LP, Attack 95, Strength 95, Defence
95, Magic 1, Ranged 1, aggressive melee, a 100-LP emulator maximum, and a
29-tick respawn. The period 109-LP maximum supersedes Darkan's conflicting
100-LP lead.

The custom handler identifies NPCs `4528`, `4529`, `4531`, and `4532` as
melee-only. Other variants choose Ice Barrage on one of four attack selections,
then independently hit 100 or zero with equal probability and apply a
five-second freeze. This corroborates the article's variant split. Those
northern mechanics are outside the registry's settled southern
Slayer-representative target and are not silently attached to it.

## Executable drop evidence and conflict

Darkan has two guaranteed rows, Big bones and Suqah hide, plus the shared
long/curved-bone tertiary. Its ordinary selector is exactly 129 slots:

| Output | Slots |
|---|---:|
| Suqah tooth ×1 | 69 |
| Grimy ranarr ×1 | 30 |
| Grimy irit ×1 | 25 |
| Darkan gem table | 5 |

This selector is executable but conflicts with the intact cutoff drop table,
which names Grimy guam and Grimy marrentill. The cutoff page supplies only
rarity labels, so there is no source-supported transformation from Darkan's
ranarr/irit weights into guam/marrentill weights. Swapping the item names while
keeping the emulator probabilities would invent non-roll content, which the
source standard forbids.

Darkan's charm thresholds are `14-8-6-7`. Lossless enumeration of
`CharmDrop.getCharmType()` produces a 1,212-slot lead: 103 Gold, 31 Green,
21 Crimson, 25 Blue, and 1,032 empty. Darkan independently supplies a hard
clue at 1/129. The cutoff article corroborates the charm colors and clue tier,
but the missing historical charm template and absence of a clue rate leave
those exact distributions as emulator leads.

## Blocking findings

1. **The ordinary selector conflicts with the period record.** Darkan's
   ranarr/irit contents cannot replace the cutoff guam/marrentill rows.
2. **The cutoff table has no executable rates.** Rarity labels do not determine
   a unique mutually exclusive selector.
3. **Charm and clue rates remain emulator leads.** Their content is attested,
   but their exact probabilities are not independently closed.

The southern combat row itself is not blocked; only the complete atomic
Combat-and-loot target is.

## Explicit omissions

- Northern blue-shield Magic variants, the caged Lady Zay form, Lunar
  Diplomacy quest encounters, cannon/location strategy, Tooth Fairy sale,
  Tooth creature use, Suqah-hide tanning, and Livid Farm distraction behavior
  are outside this ordinary Slayer-target slice.
- No Suqah sprite or drop icons were installed because the target is not
  runtime-certifiable.
- No quest file was edited; quest parity remains owned by the Darkan quest
  thread.

## Required unblock

Activate `suqah` only after a period-lineage or independently corroborated
executable ordinary selector reconciles the cutoff guam/marrentill contents
with numeric rates. The already-closed 95/95/95/1/1 combat row, cache bonuses,
29-tick respawn, guaranteed drops, 109-LP period maximum, and southern
melee-only representative can then be adopted without reopening design.

No owner-facing design question emerged. This is a source conflict under the
2026-07-19 closed-design rule, not a design gap.
