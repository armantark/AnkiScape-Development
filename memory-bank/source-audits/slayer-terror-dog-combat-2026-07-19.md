# Slayer Terror dog Combat audit — 2026-07-19

Status: **source-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Terror-dog representative required by Sumona's
settled assignment registry. The family identity, two ordinary variants,
combat levels, Slayer gate/XP, route, prayer-drain context, melee behavior,
respawn, cache bonuses, guaranteed bones split, named drop set, and several
independent tertiary leads are source-ready. The ordinary-drop selector is not.

Darkan's executable selector includes Coins ×11, while the cutoff article
allows only Coins ×44–200 and ×440. The article's complete 329-revision
pre-cutoff history never records ×11, and the cutoff talk page does not repair
that conflict. Under the source standard, an emulator value which conflicts
with the literal period record remains a lead rather than a fact. This pass
therefore does **not** add `terror_dog` to `COMBAT_ENEMY_DATA` or implement the
otherwise-settled `prayer_drain_context`.

Sumona remains hidden at **20/37**. `terror_dogs` retains its
`combat_target` and `prayer_drain_context` blockers; no readiness denominator
is changed.

## Period evidence

RuneScape Wiki `Terror dog`, oldid `6547220`, timestamp
`2012-11-10T22:08:35Z`, literal wikitext establishes:

- ordinary levels 100 and 110 with 820/880 LP;
- Slayer 40 and 82/87 Slayer XP;
- aggressive six-tick melee, with approximate 110 and 150 maxima;
- Magic weakness for both and an additional Ranged weakness for level 110;
- Sumona and Kuradal assignment membership and explicit separation from the
  broad Dogs assignment;
- level-100 guaranteed Bones and level-110 guaranteed Big bones;
- Tarn's Lair draining one Prayer point every two game ticks;
- the complete named ordinary equipment, rune, herb, resource, hard-clue,
  bone-tertiary, spin, effigy, and rare-table outputs;
- Coins only in quantities 44–200 or 440; and
- Granite helm quantity one with an estimated 1/126 period Adventure-log
  observation.

Source:
<https://runescape.wiki/w/Terror_dog?oldid=6547220>.

Cutoff `Talk:Terror dog`, oldid `4742490`, timestamp
`2011-09-17T16:08:50Z`, independently distinguishes the guaranteed drops:
level 110 always drops Big bones while the lower variant drops Bones. Its
charm discussion contains only small player samples and rough Blue-charm
observations, not an executable distribution. Its herb report corroborates
the presence of herb drops. It contains no Coins ×11 report:
<https://runescape.wiki/w/Talk:Terror_dog?oldid=4742490>.

The article history was inspected through the MediaWiki revisions API from
oldid `6547220` back through the first 2007 revision, oldid `58533`: 329
revisions in total. The first quantity-bearing Coins row recorded `44-?`;
from oldid `2942043` (`2010-07-20T12:31:08Z`) onward it records `44-200`.
Oldid `5408495` (`2012-03-20T12:42:52Z`) still records `44-200`, and the
cutoff row adds 440. No pre-cutoff revision records 11.

RuneScape Wiki `Tarn's Lair`, oldid `6436502`, timestamp
`2012-10-18T09:21:30Z`, requires Haunted Mine and a Salve amulet to enter.
RuneScape Wiki `Haunted Mine`, oldid `6550244`, timestamp
`2012-11-12T21:25:02Z`, independently lists access to the Lair as a quest
reward. AnkiScape already has a stable Haunted Mine completion state, so the
route can use that conservative quest gate when the target becomes
source-ready. Quest stages remain owned by the Darkan quest program.

Sources:
<https://runescape.wiki/w/Lair_of_Tarn_Razorlor_(dungeon)?oldid=6436502> and
<https://runescape.wiki/w/Haunted_Mine?oldid=6550244>.

The settled one-representative-per-family certification pattern permits one
ordinary representative; it does not require both level variants. Darkan's
Slayer mapping and the stronger ordinary form both point to NPC 5417, so the
level-110 form is the source-ready representative once its selector is
reconciled. Dominion Tower and miniquest encounter variants do not count for
ordinary assignments.

## Cache and executable combat evidence

Rev-727 and independently dated rev-742 both contain attackable Terror dogs at
NPCs 5417, 5418, and 14431. IDs 5415 and 5416 are statues; 11365 and 14428
have no Attack option and are not ordinary certifying targets. Both caches
also contain wearable Granite helm item 10589.

Pinned Darkan paths and commits:

- level-100 combat row:
  `data/npcs/combatdefs/uncategorized/terror_dog/terror_dog_(100) (noanims).json`,
  commit `14e49a561bab1441384022421d10dc03a8d837f0`;
- level-110 combat row:
  `data/npcs/combatdefs/uncategorized/terror_dog/terror_dog_(110) (noanims).json`,
  commit `14e49a561bab1441384022421d10dc03a8d837f0`;
- cache bonuses:
  `developer-information/npcListBonuses.txt:5419-5420,14433`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- ordinary drops:
  `data/npcs/drops/terror_dog.json`, commit
  `9fee66a1548441d2d954303348557aa18c1a0c7a`;
- charm thresholds:
  `data/npcs/charmDrops.txt:154`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`;
- hard clue:
  `src/main/java/com/rs/utils/NPCClueDrops.java:150`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`; and
- selector/charm semantics:
  `src/main/java/com/rs/utils/drop/DropList.java:98-139` and
  `src/main/java/com/rs/tools/old/CharmDrop.java:54-75`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

The rows are marked `noanims`, not `nostats`, and provide real combat levels.
The level-110 representative has Attack 110, Strength 104, Defence 78,
Magic 1, Ranged 1, 880 LP, aggressive melee, and a 59-tick respawn. Its
cache-derived bonuses are zero except for 20 melee strength. Darkan's 110
maximum conflicts with the period level-110 approximate maximum of 150; the
period value is the higher-tier candidate.

## Prayer-drain context

The real environment rule is one Prayer point every two game ticks. The
settled Combat registry names this target-local requirement
`prayer_drain_context`, and live cadence already supplies review-driven ticks.
When the target becomes source-ready, this must be a persisted two-tick
residual inside the atomic Combat transaction, independent of whether a prayer
is selected. In AnkiScape's internal tenths-of-a-point scale, each completed
two-tick interval removes 10 units. It must never consult wall-clock time.

This is an implementation-ready seam, but it is not shipped by itself while no
certifying target can expose it.

## Executable drop evidence and conflict

Darkan models the long/curved-bone table and the two guaranteed bone rows as
separate zero-rate entries. The guaranteed pair is a collapsed multi-variant
file; the period record cleanly selects only Big bones for the level-110
representative.

The remaining non-zero rows form one 128-slot cumulative selector:

| Output | Slots |
|---|---:|
| Coins ×44 | 29 |
| Coins ×132 | 25 |
| Darkan herb subtable | 15 |
| Coins ×200 | 10 |
| Water runes ×75 | 8 |
| Nature runes ×15 | 5 |
| Coins ×11 | 5 |
| Darkan gem subtable | 5 |
| Steel platelegs | 4 |
| Mithril hatchet | 3 |
| Steel battleaxe | 3 |
| Law runes ×3 | 3 |
| Adamantite ore | 3 |
| Mithril spear | 2 |
| Bass | 2 |
| Adamant full helm | 1 |
| Granite helm | 1 |
| Mithril kiteshield | 1 |
| Rune dagger | 1 |
| Fire runes ×37 | 1 |
| Coins ×440 | 1 |
| Empty | 5 |

The selector is executable but not source-ready. Coins ×11 occupies five
slots and directly contradicts the period quantity set. Removing it would be
source cherry-picking and would change the executable selector; retaining it
would add period-disallowed content.

Darkan's charm thresholds are `10-7-8-3`. Lossless enumeration of its
inclusive multi-threshold choice produces a 606-slot lead: 29 Gold, 14 Green,
17 Crimson, 6 Blue, and 540 empty. The period article and talk page corroborate
all four charm identities but do not close that exact distribution. Darkan
also supplies an independent hard clue at 1/128 and the shared 1/400 Long-bone
and 1/5,000 Curved-bone table; the cutoff article corroborates those output
identities but not the latter exact rates.

## Granite helm

The period `Granite helm` page, oldid `5827068`, timestamp
`2012-06-25T19:49:23Z`, requires Strength 50 and Defence 50 and identifies
Terror dogs as its source. Cache item 10589 and game-main's item config agree
on its wearable identity, four-kilogram weight, tradeability, and equipment
bonuses. The item and its asset can be added mechanically with the target;
they are not registered as an unobtainable orphan during this blocked pass.

Source:
<https://runescape.wiki/w/Granite_helm?oldid=5827068>.

## Blocking findings

1. **The ordinary selector conflicts with the period record.** Coins ×11 is
   executable in Darkan but absent from every quantity-bearing pre-cutoff
   article revision; the cutoff row allows only 44–200 and 440.
2. **The exact charm distribution remains an emulator lead.** Period evidence
   proves charm outputs but not Darkan's 606-slot distribution.
3. **Several tertiary rates remain leads.** The hard clue and bone-tertiary
   identities are period-attested, but their exact emulator rates are not
   independently closed here.

The level-110 combat row, route gate, prayer-drain rule, and Granite-helm
equipment data themselves are not blocked.

## Explicit omissions

- No Dominion Tower or Tarn-miniquest encounter variant is registered.
- No quest stage or route system is edited.
- No target, Granite-helm item, sprite, or drop icon is installed while the
  target is not runtime-certifiable.
- No prayer-drain helper is added without an executable consumer.

## Required unblock

Activate the ordinary level-110 representative only after a period-lineage or
independently corroborated executable selector reconciles Coins ×11 with the
cutoff quantity set. The already-closed combat row, Haunted Mine gate,
two-tick Prayer residual, Granite helm, and level-110 Big-bones split can then
be adopted without reopening design.

No owner-facing design question emerged. This is a source conflict under the
2026-07-19 closed-design rule, not a design gap.

Codex Workflows run `1d40e55e-023b-4a05-af94-694587855167` was canceled after
the root independently proved the decisive selector conflict. The Sol-high
read-only leaf never established a session and produced zero tokens, tool
calls, or usable output.
