# Slayer Kuradal assignment-pool audit — 2026-07-17

Status: **functional source contract provisionally closed; runtime hidden**.
Cutoff: `2012-11-20T00:00:00Z`.

## Finding

Kuradal's cutoff ordinary pool contains **36 families**. Darkan has 35
executable rows totaling 312 raw weight points. Its `VOLCANIC_CREATURES` row
is the ordinary 70–110 TzHaar assignment, not a second challenge-only family.
Darkan omits the period-proven Terror dogs family. Restoring Terror dogs at an
explicit 10-point common-master abstraction produces a provisional denominator
of **322**. These weights are implementation calibration, not recovered
RuneScape probabilities.

Kuradal requires Combat 110 and Slayer 75 and is reached through the Ancient
Cavern after the relevant Barbarian Training access. Her point schedule is
**18 / 90 / 270** after Smoking Kills.

## Evidence key

- **K** — RuneScape Wiki, `Kuradal`, oldid `6588106`, timestamp
  `2012-11-19T16:58:14Z`:
  <https://runescape.wiki/w/Kuradal?oldid=6588106>.
- **A** — RuneScape Wiki, `Slayer assignment`, oldid `6303852`, timestamp
  `2012-09-27T13:49:08Z`:
  <https://runescape.wiki/w/Slayer_assignment?oldid=6303852>.
- **D** — Darkan `Task.java`, `TaskMonster.java`, `Master.java` and
  `SlayerTaskManager.java`, pinned commit
  `c343a917712649675989315009ce250639e0850f`.
- **C** — RuneScape Wiki, `Slayer/Challenges`, oldid `6328439`, timestamp
  `2012-10-01T08:55:32Z`:
  <https://runescape.wiki/w/Slayer/Challenges?oldid=6328439>.
- **L** — `slayer-location-contexts-2026-07-15.md`, independently pinned from
  `Kuradal's Dungeon` oldid `6516655` and `Ferocious ring` oldid `6547685`.

## Reconciled ordinary pool

`Weight` is provisional hidden roll-table calibration. Counts are the observed
cutoff master-page values where they conflict with Darkan. Gates are authentic
player eligibility or unavoidable route requirements, not current AnkiScape
readiness.

| Family | Weight | Count | Gate | Combat/context obligation | Provenance |
|---|---:|---:|---|---|---|
| Aberrant spectres | 10 | 140–250 | Slayer 60; Morytania route | Nose peg or accepted Slayer helmet; unprotected LP/stat drain | K/A/D |
| Abyssal demons | 12 | 150–250 | Slayer 85 | Mapless teleport interruption; Kuradal-Dungeon context controls Ferocious-ring drop | K/A/D/L |
| Aquanites | 10 | 120–240 | Slayer 78; 50-point assignment unlock | Prayer-negating special attack | K/A/D |
| Black demons | 10 | 190–250 | baseline | Ordinary family; named/boss variants remain explicit | K/A/D |
| Black dragons | 5 | 40–90 | baseline | Adult, baby and King Black Dragon membership; dragonfire where applicable | K/A/D |
| Bloodvelds | 10 | 180–250 | Slayer 50 | Ordinary and Mutated variants with route gates | K/A/D |
| Blue dragons | 7 | 120–200 | baseline | Adult and baby-blue identity; adult dragonfire | K/A/D/L |
| Dagannoths | 10 | 170–240 | baseline | Ordinary, fledgling, spawn, guardian and three Kings in their proper contexts | K/A/D |
| Dark beasts | 12 | 150–250 | Slayer 90 | Kuradal-Dungeon variant avoids importing an unrelated Temple-of-Light route gate | K/A/D/L |
| Desert strykewyrms | 9 | 90–160 | Slayer 77 | Assignment-only attackability, tunnelling and special attack | K/A/D |
| Dust devils | 10 | 150–250 | Slayer 65 | Face mask or accepted Slayer helmet; unprotected damage/stat drain | K/A/D |
| Fire giants | 10 | 170–250 | baseline | Ordinary family | K/A/D |
| Ganodermic creatures | 7 | 65–89 | Slayer 95; Magic 60 | Ganodermic runt and beast; Polypore context | K/A; cutoff count overrides D `70–90` |
| Gargoyles | 12 | 150–250 | Slayer 75 | Rock-hammer finisher; quick-finisher still requires the hammer | K/A/D/L |
| Greater demons | 11 | 150–250 | baseline | Ordinary family; named/boss variants excluded without explicit membership | K/A; cutoff count overrides D `150–258` |
| Grifolapines | 8 | 65–79 | Slayer 88; Magic 60 | Polypore context and neem-oil interaction | K/A; cutoff count overrides D `65–80` |
| Grifolaroos | 8 | 65–75 | Slayer 82; Magic 60 | Polypore context and neem-oil interaction | K/A; cutoff count overrides D `65–80` |
| Grotworms | 10 | 80–160 | baseline | Young, ordinary and Mature variants | K/A/D |
| Hellhounds | 10 | 130–230 | baseline | Ordinary family | K/A/D/L |
| Ice strykewyrms | 12 | 100–219 | Slayer 93; Tale of the Muspah; fire cape/TokHaar-Kal ownership or 2,000-point technique unlock | Assignment-only attackability, tunnelling and special attack | K/A; cutoff count overrides D `100–220` |
| Iron dragons | 9 | 40–117 | baseline | Metal-dragon and dragonfire behavior | K/A/L; cutoff count overrides D `40–120` |
| Jungle strykewyrms | 8 | 90–160 | Slayer 73 | Assignment-only attackability, tunnelling and poison | K/A; cutoff count overrides D `90–130` |
| Kalphites | 5 | 170–250 | baseline | Worker, soldier, guardian and Queen; larva excluded | K/A/D |
| Living rock creatures | 10 | 110–185 | Living Rock Caverns route | Protector, striker and patriarch boundary | K/A/D |
| Mithril dragons | 8 | 20–35 | Ancient Cavern/Barbarian Training route | Metal-dragon and dragonfire behavior | K/A/D |
| Mutated jadinkos | 8 | 160–220 | Slayer 80/86/91 by variant | Baby, guard and male variant identities | K/A/D |
| Nechryael | 10 | 140–220 | Slayer 80 | Up to two temporary Death spawns; spawns never grant family credit | K/A/D |
| Skeletal wyverns | 5 | 40–90 | Slayer 72 | Required elemental/mind/body/dragonfire-shield protection | K/A/D |
| Spiritual mages | 10 | 150–240 | Slayer 83; God Wars route | Four god variants with target-local alignment/aggression context | K/A/D |
| Steel dragons | 9 | 40–108 | baseline | Metal-dragon and dragonfire behavior | K/A/L; cutoff count overrides D `40–100` |
| Suqahs | 5 | 50–100 | Lunar Diplomacy/Lunar Isle route | Explicit Suqah family | K/A/D |
| Terror dogs | 10 | 60–70 | Slayer 40; Tarn's Lair route | Distinct from Dogs; target-local prayer-drain context | K/A; weight `abstraction/common-master-baseline`, absent from D |
| TzHaar | 7 | 70–110 | baseline | Ordinary surface TzHaar family; separate Fight-Cave challenge offer | K/A; D names the row `VOLCANIC_CREATURES` |
| Vyrewatch | 8 | 60–170 | Slayer 67; Branches of Darkmeyer | Restricted weapons; Vyrewatch/Vyrelady/Vyrelord/Juvinate boundary | K/A/D; K's displayed level `31` is stale |
| Warped tortoises | 8 | 150–240 | Slayer 56; Path of Glouphrie | Crystal-chime vulnerability | K/A/D |
| Waterfiends | 9 | 170–250 | route-specific access | Ordinary family in its proper contexts | K/A/D |

Darkan's 35 executable rows total 312. Mapping its 70–110
`VOLCANIC_CREATURES` row to the ordinary cutoff TzHaar row and adding the
omitted Terror dogs family at 10 yields `312 + 10 = 322`.

## Master access, points and reward gates

Kuradal oldid `6588106` directly supplies Combat 110, Slayer 75, Ancient Cavern
placement and the 18/90/270 point schedule. The required Ancient Cavern route
uses Barbarian Training; it is not a hidden Kuradal-only flag.

The steady-state 50-task point average is 28.8:

`(45 × 18 + 4 × 90 + 270) / 50 = 28.8`.

The first four tasks after starting or resetting the global point streak still
award zero, so this is a repeating-cycle average rather than a fresh-account
first-50 average.

Two assignment gates are master-specific:

- Aquanites require Slayer 78 and the 50-point `Allow Kuradal to assign
  aquanites` reward.
- Ice strykewyrms require Slayer 93, The Tale of the Muspah, and either
  ownership of a fire cape/TokHaar-Kal or the 2,000-point alternative
  technique unlock. The cape need not be equipped.

Darkan correctly applies the Aquanite unlock globally to its Kuradal row but
does not model the complete ice-strykewyrm ownership/quest alternative. Its
fresh previous-family field initializes to Abyssal demons and therefore
wrongly excludes that family from a first assignment.

## Kuradal's Dungeon and Ferocious ring

The already-pinned location contract in **L** remains authoritative:

- entry requires an active Kuradal assignment for a dungeon resident;
- only the assigned monster may be attacked, and only until completion;
- the period roster is Hellhounds, Greater demons, Blue dragons, Gargoyles,
  Abyssal demons, Dark beasts, Iron dragons and Steel dragons;
- dwarf multicannons are forbidden;
- every dungeon resident can drop Ferocious rings, with exact denominators
  still `source_blocked`;
- the worn ring adds a fixed 40 life points to each successful dungeon hit,
  not 4% damage;
- below 10% but above zero life points, the ring destroys itself and safely
  ends the encounter; a hit reaching zero still kills;
- five teleport charges reach Kuradal and erase the abstract context trip
  cost; the fifth use destroys the ring; and
- Murky Matt combines partial charges as an instantaneous inventory operation.

Those rules make Kuradal's Dungeon a target-local Combat context. A generic
monster row must not expose its Ferocious-ring drop or bonuses outside that
context.

## Challenge boundary

Kuradal's optional challenge replaces an ordinary TzHaar assignment with one
complete Fight Cave run containing **280 kills**, including TzTok-Jad and two
waves of four Yt-HurKot healers. Only Fight Cave creatures count.

Cutoff oldids **K** and **C** establish:

- the offer may be declined immediately without penalty;
- an accepted challenge counts as one task and cannot be cancelled through the
  reward shop;
- ordinary completion points apply if Smoking Kills is complete, but there are
  no bonus challenge points;
- killing TzTok-Jad awards 25,000 bonus Slayer XP; and
- all 280 kills award 12,000 stated Slayer XP, for 37,000 total stated XP.

The dedicated challenge audit preserves the Fight Cave as a persistent Combat
instance, not 280 unrelated ordinary target selections. Leaving, death or
deliberate abandonment resets the run instance while the accepted challenge
remains active. The complete Fight Cave activity and wave roster do not yet
exist.

The exact offer probability and prerequisite remain `source_blocked`.
`Talk:Kuradal` oldid `6547230`, timestamp `2012-11-10T22:23:23Z`, reports an
offer on a player's first Kuradal task, contradicting any assertion that a
period minimum of several completed tasks is known:
<https://runescape.wiki/w/Talk%3AKuradal?oldid=6547230>.
The owner-authorized five-task/10% fallback remains labeled
implementation-only.

## Count and membership conflicts

The cutoff master page is a direct 36-row ledger. Its count values override
Darkan on nine rows:

- Ganodermic creatures `65–89`, not `70–90`;
- Greater demons `150–250`, not `150–258`;
- Grifolapines `65–79`, not `65–80`;
- Grifolaroos `65–75`, not `65–80`;
- Ice strykewyrms `100–219`, not `100–220`;
- Iron dragons `40–117`, not `40–120`;
- Jungle strykewyrms `90–160`, not `90–130`;
- Steel dragons `40–108`, not `40–100`; and
- Vyrewatch `60–170`, not `90–130`.

Darkan entirely omits Terror dogs. Its `VOLCANIC_CREATURES` name is retained
only as emulator evidence for the ordinary 70–110 TzHaar row; the 280-kill
Fight Cave challenge is a separate state machine, not a weighted second
family.

Kuradal oldid `6588106` displays Vyrewatch's required Slayer level as 31.
`Slayer assignment` oldid `6303852` and `Vyrewatch` oldid `6552643` instead
converge on Slayer 67, so 31 is rejected as a stale table typo.

Hidden weights, exact within-family combat-level selection, Ferocious-ring
drop denominators, the challenge offer roll and the exact generator formula
behind observed count envelopes remain `source_blocked`. Qualitative rarity
claims do not become weights.

Summoning and Dungeoneering creatures are outside this audit and remain
excluded from the ordinary pool.

## Current AnkiScape readiness and concrete repair

This audit does **not** authorize a partial live Kuradal role.

Black demon, Greater demon, Hellhound and the ordinary TzHaar family are
complete Combat candidates after the source XP repair below. Baby black dragon
cannot certify the full Black-dragon family. Abyssal demon lacks its mapless
teleport interruption and target-local Kuradal context. Nechryael has a
Death-spawn target but no summon hook. The other 29 families have no complete
certifying target. There is no stable Slayer family registry, assignment
generator, task-credit path, playable Ancient Cavern access chain, reward-gate
integration, Kuradal context or Fight Cave challenge, so end-to-end readiness
is **0/36**.

The safe independent data repair from this pass restores the cutoff
level-149 TzHaar-Ket's missing **136 Slayer XP** and cites Kuradal oldid
`6588106`. A focused regression first reproduced the absent field, then pinned
the repaired row.

No owner-level design question emerged. Remaining work is source/data and
implementation: build the stable family/variant registry; add the absent
targets and special mechanics; implement the two reward-gated assignment
paths, Ancient Cavern and Kuradal's Dungeon contexts; build the Fight Cave;
then certify the complete pool before exposing Kuradal.
