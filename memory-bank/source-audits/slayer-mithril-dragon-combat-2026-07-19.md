# Slayer Mithril dragon Combat audit — 2026-07-19

Status: **source-blocked and representation-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Mithril dragon required by the settled
Duradel/Lapalok assignment registry. The identity, Ancient Cavern route,
Barbarian Training gate, level, period LP/Slayer XP, attack families, period
maxima, real combat levels, cache bonuses, respawn, guaranteed drops, named
drop set, charm quantity, and tertiary leads are recoverable. The complete
atomic target is not source-ready.

Three independent blockers remain:

1. Darkan conflicts with the cutoff record on LP and ranged/Magic maxima.
2. Darkan's ordinary selector omits or narrows multiple period-visible rows
   and quantities.
3. The settled fight is a source-visible Melee/Magic/Ranged/dragonfire
   rotation, while the current Combat enemy schema has one fixed ordinary
   attack style and one uniform dragonfire envelope.

This pass does **not** flatten the rotation into one style, extend the ordinary
metal-dragon abstraction without authority, or activate a partial target.
Duradel/Lapalok remains hidden at **14/35**. `mithril_dragons` retains its
`combat_target` blocker and no denominator changes.

## Settled target boundary

The newest registry binds `mithril_dragons` to exactly
`("mithril_dragon",)`, with `dragonfire` and `ancient_cavern_context` readiness
features. The owning pool audit requires the Ancient Cavern/Barbarian-training
route and metal-dragon/dragonfire behavior. These are implementation
requirements, not open design branches.

The current `COMBAT_ENEMY_DATA` schema supports:

- one `attack_style` for ordinary attacks;
- an optional player-class-dependent style override; and
- one independent `dragonfire` chance with a single unprotected and partial
  maximum.

It does not support a source-weighted random ordinary-style selector with
different Melee, Ranged, and Magic maxima, nor two dragonfire envelopes whose
protection maxima depend on the selected breath form. Implementing a fixed
style or copying the adjacent Iron/Steel selector would contradict the settled
Mithril-dragon fight.

## Period evidence

RuneScape Wiki `Mithril dragon`, oldid `6516855`, timestamp
`2012-11-01T21:14:21Z`, literal wikitext establishes:

- combat level 304, 2,540 LP, Slayer 1, and 273 Slayer XP;
- aggression and partial poison immunity, with Smoke spells as the stated
  exception;
- six-tick Melee, Magic, Ranged, and dragonfire attacks;
- maxima of 289 LP melee and 182 LP each for Magic and Ranged;
- guaranteed Dragon bones and Mithril bars ×3;
- Ancient Cavern access after starting the pyre-ship section of Barbarian
  Training;
- the complete named ordinary weapon, armour, rune, potion-mix, Coin, Shark,
  Ancient-page, hard-clue, elite-clue, Chewed-bones, Runite-bar, effigy,
  spin-ticket, Draconic-visage, and rare-drop-table families; and
- four charms per successful charm roll.

Source:
<https://runescape.wiki/w/Mithril_dragon?oldid=6516855>.

The page gives period-visible quantities including:

- Rune dart (p) ×14 and Rune javelin ×8;
- Runite bolts ×10–27, Rune knife ×8–18, and Rune arrows ×8–42;
- Blood runes ×27, Soul runes ×10, Law runes ×4 or ×45, and Death runes ×45
  or ×50;
- one of each two-dose Super attack, Super strength, Super defence, and Prayer
  mix;
- Coins ×283–8,441, Sharks ×1–6, and Runite bars ×2 or ×3;
- Adamant darts (p) ×20; and
- estimated Dragon-full-helm and Draconic-visage rates of 1/32,873 and
  1/9,819 from cutoff Adventurer's Log data.

Cutoff `Talk:Mithril dragon`, oldid `6359596`, timestamp
`2012-10-06T21:51:28Z`, supplies useful negative evidence:

- a 2,000-kill report says Runite bars were always dropped in groups of two,
  never one;
- the firebreath discussion confirms the long-ranged breath identity;
- the page rejects Dragon platelegs/plateskirt as ordinary Mithril-dragon
  drops;
- several discussions identify Rune spear and Dragon dagger rare-drop-table
  ambiguity; and
- a 400-kill log records observed Chewed bones, Rune battleaxes, Runite bars,
  Rune spears, Rune maces, and Rune full helms.

It does not supply a complete executable selector:
<https://runescape.wiki/w/Talk:Mithril_dragon?oldid=6359596>.

The article transcludes `Template:Charm:Mithril_dragon`, but no pre-cutoff
revision of that dependency was recovered by the pinned history tool. The
article closes quantity four, not exact charm-color rates.

## Cache and executable combat evidence

Rev-742 contains attackable level-304 NPC `5363` and a non-attackable temporary
level-57 identity `8424`. The latter is the Dragonkin-key animation form and is
not a second ordinary Combat target.

Darkan's cache-derived data gives NPC `5363` exact defences:

| Field | Value |
|---|---:|
| Stab defence | 50 |
| Slash defence | 100 |
| Crush defence | 70 |
| Magic defence | 30 |
| Ranged defence | 90 |
| Attack bonuses | 0 |
| Strength bonuses | 0 |

Pinned Darkan paths and commits:

- combat row:
  `data/npcs/combatdefs/uncategorized/mithril_dragon.json`, commit
  `14e49a561bab1441384022421d10dc03a8d837f0`;
- custom attack handler:
  `src/main/java/com/rs/game/content/world/npcs/MithrilDragonCombat.java`,
  commit `347552cad462e96670e3ff04228c0232881da9f5`;
- cache-derived bonuses:
  `developer-information/npcClientScriptData.txt:1294` and
  `developer-information/npcListBonuses.txt:5365`;
- ordinary drops:
  `data/npcs/drops/mithril_dragon.json`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- charm thresholds:
  `data/npcs/charmDrops.txt:122`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`; and
- clue rates:
  `src/main/java/com/rs/utils/NPCClueDrops.java:165,197`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

The combat JSON supplies Attack 268, Strength 268, Defence 268, Magic 168,
Ranged 168, aggression, and a 59-tick respawn. It conflicts with the period LP
at 2,550 instead of 2,540 and delegates attacks to a custom handler rather than
supplying a real maximum.

The handler chooses four equiprobable branches:

- adjacent melee, otherwise a 500-LP ranged breath;
- a 650-LP breath;
- 250-LP Ranged; or
- 250-LP Magic.

The Ranged and Magic maxima directly conflict with the period 182-LP rows.
The handler's breath protection ranges also vary by branch and distance.
Because AnkiScape has no position layer, the settled fight needs one explicit
source-backed no-position selector. The existing 1/2 adjacent Iron/Steel
abstraction proves neither this four-style selector nor which of Darkan's two
breath envelopes should survive.

## Executable drop evidence and conflicts

Darkan guarantees Dragon bones and Mithril bars ×3. Its 24 ordinary rows
occupy 127 of a declared 128 slots, leaving one implicit empty slot:

| Output | Slots |
|---|---:|
| Blood runes ×27 | 18 |
| Coins ×600 | 17 |
| Rune javelins ×8 | 14 |
| Rune battleaxe | 12 |
| Rune darts (p) ×14 | 7 |
| Coins ×876 | 7 |
| Runite bolts ×10–21 | 6 |
| Shark ×1 | 6 |
| Soul runes ×10 | 5 |
| Darkan gem table | 4 |
| Rune knives ×8 | 3 |
| Rune mace | 3 |
| Rune arrows ×8 | 3 |
| Chewed bones | 3 |
| Runite bars ×2 | 3 |
| Rune spear | 2 |
| Super attack mix (2) | 2 |
| Sharks ×6 | 2 |
| Super strength mix (2) | 2 |
| Prayer mix (2) | 2 |
| Super defence mix (2) | 2 |
| Rune full helm | 1 |
| Darkan standard rare table | 1 |
| Empty | 1 |

Independent Darkan rows add Draconic visage at 1/10,000 and Dragon full helm
at 1/32,768. `NPCClueDrops` adds hard clues at 1/128 and elite clues at 1/350.

The selector is not source-ready:

- Runite bolts ×10–21 narrows the cutoff ×10–27;
- Rune knives ×8 omit the cutoff ×9–18 outcomes;
- Rune arrows ×8 omit the cutoff ×9–42 outcomes;
- Adamant darts (p) ×20, Law runes, Death runes, Ancient pages, Rune
  longswords, Rune 2h swords, and several other period-visible rows are absent;
- the cutoff Coin range reaches ×8,441 while Darkan only emits ×600 or ×876;
  and
- Darkan's exact hard/elite rates are not closed by the article's rarity labels.

The Dragon-full-helm and visage rates are close to the cutoff estimates, but an
estimate cannot erase the selector's direct quantity omissions.

Darkan's charm thresholds are `19-49-19-4`, with quantity four. Lossless
enumeration of `CharmDrop.getCharmType()` produces a 1,212-slot lead: 75 Gold,
435 Green, 75 Crimson, 15 Blue, and 612 empty. The cutoff page corroborates
quantity four and charm content, but the missing historical template leaves
the exact color distribution emulator-only.

## Blocking findings

1. **Combat state conflicts.** Period 2,540 LP and 182 Ranged/Magic maxima
   conflict with Darkan's 2,550 LP and 250 maxima.
2. **The multi-style selector is source-blocked.** Only Darkan supplies exact
   1/4 branches, and its branch maxima conflict with the period record.
3. **The current enemy schema cannot represent the settled fight.** A fixed
   style plus one breath envelope would flatten source-visible behavior.
4. **The ordinary selector is incomplete and quantity-conflicting.** It cannot
   certify the cutoff item set.
5. **The Ancient Cavern gate has no live Combat-target predicate.** The family
   carries only a readiness label; Combat currently has no Barbarian-training
   completion field to enforce the settled route.

## Explicit omissions

- The Dragonkin-key level-57 animation form, Strange-key interaction, Fairy
  Ring/Ferocious Ring travel alternatives, cannon prohibition, surrounding
  Ancient Cavern enemies, pyre ships, Chewed-bones ritual, Dragon full helm
  acquisition downstream, and While Guthix Sleeps content are outside this
  ordinary target slice.
- No Mithril-dragon sprite or new drop icons were installed because the target
  is not runtime-certifiable.
- No Barbarian Training or quest file was edited.

## Required unblock

Activation requires all of the following without reopening design:

1. a period-lineage or independently corroborated no-position attack selector
   preserving Melee, Ranged, Magic, and dragonfire with period maxima;
2. an executable ordinary selector that retains every cutoff quantity;
3. a Combat-target gate for the settled Ancient Cavern/Barbarian-training
   route; and
4. a schema extension for weighted ordinary attack styles and the required
   dragonfire envelopes.

No owner-facing design question emerged. These are source and implementation
substrate blockers under the 2026-07-19 closed-design rule.
