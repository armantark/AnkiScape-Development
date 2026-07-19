# Slayer Skeletal Wyvern Combat audit — 2026-07-19

Status: **source-blocked and dependency-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Skeletal Wyvern required by the settled
Duradel/Lapalok assignment registry. The identity, level, LP, Slayer gate/XP,
combat levels, cache bonuses, respawn, ordinary melee/ranged maxima, shield
family, visible breath envelopes, guaranteed drop, ordinary selector lead,
charms, clues, and visage lead are recoverable.

The complete target cannot activate because:

1. no period-lineage source recovered here supplies the ice-breath selection
   probability or freeze duration;
2. Darkan has no Skeletal-Wyvern attack handler and models only fixed melee;
3. the current Combat schema cannot select Melee, Ranged, and conditional
   ice-breath attacks with distinct maxima; and
4. none of the period-valid protective shields is live equippable equipment.

The generated Elemental Workshop I quest grants an `Elemental shield` item,
but `equipment_data.py` has no record for it. Mind, Body, Cosmic, Chaos, and
Dragonfire shields are also absent as live equipment. The only equipped
dragon shield is the Anti-dragon shield, which the cutoff article explicitly
rejects for Wyvern breath.

This is a settled-contract/code-reality conflict. The target remains absent
rather than becoming permanently locked or accepting the wrong shield.
Duradel/Lapalok remains hidden at **14/35**.

## Period evidence

RuneScape Wiki `Skeletal Wyvern`, oldid `6569736`, timestamp
`2012-11-17T23:35:19Z`, literal wikitext establishes:

- combat level 198, 2,000 LP, Slayer 72, and 210 Slayer XP;
- aggression, poison susceptibility, and a six-tick engine interval
  represented as speed `4` on the period Wiki scale;
- Melee, Ranged, and unique ice-breath attacks;
- a 139-LP Melee/Ranged maximum;
- a 150-LP breath maximum with a valid shield and `500+` without one;
- an ice-breath freeze which prevents fighting back;
- breath accuracy unaffected by armour, with higher Magic defence reducing
  its maximum slightly;
- required protection from Elemental, Mind, Body, Cosmic, Chaos, or Dragonfire
  shield, explicitly excluding Anti-dragon shield and Super antifire;
- guaranteed Wyvern bones;
- the complete named weapon/armour, rune, bolt, herb, seed, Coin, food,
  potion, hard-clue, crossbow, effigy, visage, and rare-drop-table sets.

Source:
<https://runescape.wiki/w/Skeletal_Wyvern?oldid=6569736>.

Cutoff `Talk:Skeletal Wyvern`, oldid `5516744`, timestamp
`2012-04-21T13:51:02Z`, corroborates:

- Elemental-shield use;
- ice-breath bypassing ordinary Ranged prayer at distance;
- historical long-distance breath behavior;
- the unreliable Salve/Dragon-Slayer classifications;
- a rebuilt charm log with more than 3,000 kills; and
- user reports of Toadflax and Irit seeds.

It does not provide a breath-selection probability, freeze duration, or
complete ordinary selector:
<https://runescape.wiki/w/Talk:Skeletal_Wyvern?oldid=5516744>.

The article transcludes `Template:Charm:Skeletal Wyvern`, but no pre-cutoff
revision of that dependency was recovered by the pinned history tool.

## Cache and Darkan evidence

Rev-742 contains four attackable level-198 identities, NPCs `3068`–`3071`.
All share a six-tick interval and these exact cache-derived defences:

| Field | Value |
|---|---:|
| Stab defence | 140 |
| Slash defence | 90 |
| Crush defence | 90 |
| Magic defence | 80 |
| Ranged defence | 140 |
| Attack bonuses | 0 |
| Strength bonuses | 0 |

Pinned Darkan paths and commits:

- combat row:
  `data/npcs/combatdefs/uncategorized/skeletal_wyvern.json`, commit
  `9376cbc21c31f30b9f4ae1712e7324dafe29387c`;
- cache-derived interval and bonuses:
  `developer-information/npcClientScriptData.txt:763-766` and
  `developer-information/npcListBonuses.txt:3070-3073`;
- ordinary drops:
  `data/npcs/drops/skeletal_wyvern.json`, commit
  `ede51d1a527980f5dd732e6266fec8f60c0c5225`;
- charm thresholds:
  `data/npcs/charmDrops.txt:147`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`; and
- elite clue:
  `src/main/java/com/rs/utils/NPCClueDrops.java:193`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

The combat row is real rather than `nostats`: Attack 125, Strength 116,
Defence 120, Magic 125, Ranged 120, 2,000 LP, 139 maximum, aggression, and a
59-tick respawn. It declares only melee. No matching Darkan custom handler
implements the period Ranged or ice-breath branches.

## Executable drop lead

Darkan guarantees Wyvern bones. Its ordinary rows occupy 124 of 128 slots,
leaving four empty. The direct item rows match many cutoff quantities exactly:

- Coins ×20–420;
- Bone bolts ×2–29, Mithril bolts ×8–39, Adamant bolts ×5–29, and Runite
  bolts ×5–25;
- Pure essence ×60, Air runes ×10–64, Water runes ×11–33, Chaos runes ×10,
  Law runes ×2–5, Blood runes ×2–11, Soul runes ×5–14, and Death runes ×1–5;
- Mithril sword, Black/Adamant hatchets, Snakeskin chaps, Lobsters ×3, Bass,
  Super attack (1), Defence potion (3), and Adamant c'bow (u).

The selector routes seven slots through Darkan's herb table, six through
common seeds, and six through rare seeds. Those nested tables require a
separate leaf-level comparison before runtime certification; the cutoff page
names eleven herbs and eighteen seed rows.

Independent Darkan rows add Dragon plateskirt, Dragon platelegs, and Granite
legs at 1/512 each and Draconic visage at 1/10,000. Only Granite legs and the
visage appear in the inspected cutoff article; the dragon leg/skirt rows need
independent period corroboration. The cutoff visage estimate is 1/12,686,
which does not close Darkan's exact 1/10,000 rate. Darkan adds an elite clue at
1/350, while the cutoff page names only a hard clue; the hard-clue rate is
absent from `NPCClueDrops`.

Darkan's charm thresholds are `7-3-55-1`, with quantity two. Lossless
enumeration produces a 1,212-slot lead: 38 Gold, 14 Green, 614 Crimson,
6 Blue, and 540 empty. The cutoff article and talk page corroborate
crimson-heavy two-charm behavior but not the exact distribution.

## Representation and dependency conflicts

The owning contract requires both `wyvern_breath` and
`protective_equipment`. Current code can enforce equipment or apply an
unprotected per-attack consequence, but it cannot:

- choose breath only on its sourced attack branch;
- alternate ordinary Melee and Ranged styles;
- assign 139 to ordinary attacks and separate 150/500+ breath envelopes;
- represent the freeze as review-driven skipped enemy attacks; or
- vary the breath envelope with Magic defence.

The equipment dependency is also non-executable:

- `quest_catalog_generated.py:6329` grants `Elemental shield`;
- `item_values_generated.py` knows that identity;
- `equipment_data.py` has no Elemental, Mind, Body, Cosmic, Chaos, or
  Dragonfire shield record; and
- the live Anti-dragon shield is explicitly invalid for this target.

This pass does not edit the quest-owned Elemental Workshop chain.

## Blocking findings

1. **Ice-breath probability and freeze duration are source-blocked.**
2. **Darkan omits the distinctive combat branches entirely.**
3. **The Combat enemy schema cannot represent the settled style/breath
   transaction without an implementation extension.**
4. **Every valid shield is non-equippable in the live registry.**
5. **The drop selector still needs nested herb/seed and tertiary
   reconciliation.**

## Required unblock

Activation requires:

1. an independently corroborated breath selector and review-driven freeze
   magnitude;
2. a multi-style/breath Combat schema extension that preserves the settled
   maxima;
3. at least one period-valid shield as real obtainable equipment, with the
   full valid-shield set retained as the contract requires; and
4. a leaf-level drop reconciliation including the missing hard clue and
   Darkan-only dragon leg/skirt rows.

No owner-facing design question emerged. These are source, substrate, and
quest/equipment dependency blockers under the 2026-07-19 closed-design rule.
