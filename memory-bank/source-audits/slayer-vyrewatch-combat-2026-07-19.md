# Slayer Vyrewatch Combat audit — 2026-07-19

Status: **source-blocked; no Combat rows activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the cutoff Vyrewatch assignment family and the ordinary
level-110 Vyrewatch as the smallest current-period representative. It closes
the visible family membership, quest/Slayer gates, combat identities,
restricted weapons, corpse drop, named ordinary drops, cache identities, and
Darkan execution boundary. It does **not** add `vyrewatch` to
`COMBAT_ENEMY_DATA`.

There are two independent blockers:

1. the settled assignment is a broad family which accepts Vyrewatch,
   Vyreladies, Vyrelords, and Vampyre juvinates, while the executable stable
   registry declares only `("vyrewatch",)`; and
2. the level-110 Darkan row and ordinary selector conflict with cutoff values,
   including the maximum hit and Fire-rune quantity.

Chaeldar therefore remains hidden at **25/34**. `vyrewatch` retains its
`combat_target` blocker; no readiness denominator is changed.

## Period evidence

RuneScape Wiki `Vyrewatch`, oldid `6552643`, timestamp
`2012-11-13T22:48:45Z`, literal wikitext establishes:

- ordinary combat levels 110, 112, 120, 128, 130, and 140;
- corresponding LP `950 / 1220 / 1050 / 1400 / 1150 / 1250`;
- Slayer 67 to receive a task and completion of The Branches of Darkmeyer for
  the assignment route;
- Slayer XP `95 / 105 / 105 / 140 / 115 / 125`;
- aggressive five-tick melee unless disguised or protected by the completed
  quest context;
- displayed maxima `151 / ? / 162 / 114 / 171 / 170`;
- poison immunity for levels 110, 120, 130, and 140, but not 112 or 128;
- complete invulnerability to ordinary weapons, poison, recoil, and reflected
  curses, with damage allowed only from Ivandis flails and Blisterwood
  weapons;
- guaranteed Vyre corpse;
- Death runes ×1–25, Fire runes ×80, Blood runes ×10–15, ten noted-herb rows
  at ×4, Coins ×100–1,240, Splitbark helm/body, effigy, Spin ticket, and rare
  drop table; and
- task credit alternatives of Vyrelords, Vyreladies, and Vampyre juvinates.

Source:
<https://runescape.wiki/w/Vyrewatch?oldid=6552643>.

Cutoff `Talk:Vyrewatch`, oldid `6552649`, timestamp
`2012-11-13T22:54:26Z`, corroborates:

- silver plus unpredictability as the Ivandis-flail damage basis;
- the 2011 return of Vyrewatch assignments;
- location-dependent corpse-only drops for some variants;
- the different poison immunities of level-110/120/128/130/140 forms; and
- charm drops beginning in the period record by June 2012.

It does not close hidden combat levels, damage bonuses, drop rates, or the
complete stable variant ledger:
<https://runescape.wiki/w/Talk:Vyrewatch?oldid=6552649>.

## Cache and executable evidence

Rev-742 contains the many gender/location identities behind levels 110, 112,
120, 128, 130, and 140. Darkan's cache-derived bonus dump gives the ordinary
forms zero attack, defence, and strength bonuses; the client layer does not
prove their server combat levels or weapon multipliers.

Pinned Darkan paths and commits:

- ordinary combat rows:
  `data/npcs/combatdefs/uncategorized/vyrewatch/`, commit
  `14e49a561bab1441384022421d10dc03a8d837f0`;
- weapon restriction:
  `src/main/java/com/rs/game/content/items/CombatEnhancers.kt:157-169`,
  current file lineage through
  `5774ecb60bce9c1779f7097ce4696b4a84e762df`;
- ordinary drops:
  `data/npcs/drops/vyrewatch.json`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- charm thresholds:
  `data/npcs/charmDrops.txt:168`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`; and
- hard-clue lead:
  `src/main/java/com/rs/utils/NPCClueDrops.java:152`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

The level-110 Darkan row supplies 950 LP, Attack 110, Strength 96, Defence 85,
Magic 110, Ranged 110, aggressive melee, a 150 maximum, and a 59-tick
respawn. Its 150 maximum conflicts with the cutoff 151. The five hidden combat
levels have no independent period corroboration in this pass.

The weapon handler blocks non-Vyre equipment. It allows:

- Ivandis-flail/rod and related silver weapon IDs for melee;
- Blisterwood polearm/stake for melee or Ranged, with doubled accuracy/damage;
  and
- Blisterwood staff for Magic, with 1.5× accuracy/damage.

The cutoff page corroborates the weapon families and qualitative immunity, but
does not close those exact multipliers or the handler's broader item-ID set.
Current AnkiScape's Legacy of Seergaze definition does grant an `Ivandis flail`
and publishes it into the item manifest, but the generated item has no
`equipment_slot`, `equipment_data.py` has no combat equipment row for it, and
Combat has no Vyre-only damage path. The item is therefore obtainable but not
an executable allowed weapon. No live Blisterwood acquisition chain exists.

Darkan's ordinary file guarantees item 21608, Vyre corpse, then uses one
cumulative selector. It conflicts visibly with the cutoff record:

- Fire runes are ×35 instead of ×80;
- it includes noted Ranarr weed ×8, Splitbark legs, a Rune pickaxe, and a
  Torstol seed while omitting or changing several article rows; and
- the one shared name-based table cannot preserve the article's explicit
  corpse-only location variants.

Darkan charm thresholds `2-1-3-2` losslessly enumerate to a 606-slot lead:
5 Gold, 3 Green, 11 Crimson, 5 Blue, and 582 empty. The cutoff material
attests charms but not that selector. Darkan supplies a 1/128 hard clue while
the cutoff article does not name a clue row; no clue channel is inferred.

## Blocking findings

1. **The stable family ledger is incomplete.** One `vyrewatch` target cannot
   certify the source-attested Vyrelady/Vyrelord/Juvinate alternatives.
2. **The representative maximum conflicts.** Darkan gives 150 against the
   cutoff level-110 maximum of 151.
3. **The five hidden combat levels are uncorroborated.** Cache bonuses and
   displayed combat level do not prove them.
4. **The ordinary selector conflicts with period quantities and contexts.**
   Fire runes and location-specific corpse-only behavior are direct examples.
5. **The weapon dependency is only catalog-deep.** Legacy of Seergaze grants
   an Ivandis flail item, but it is not equipable or recognized by Combat;
   Blisterwood has no live acquisition route.

## Explicit omissions

- No Vyrewatch, Vyrelady, Vyrelord, or Juvinate sprite/item assets were
  installed because the family is not runtime-certifiable.
- Ivandis special attack, Guthix-balance use, corpse cremation, tithe/mines,
  Darkmeyer disguise, Temple Trekking, God Wars, and quest encounters are
  outside this ordinary Slayer-family audit.
- No stable variant set was invented. The authority mismatch is recorded in
  `../audits/slayer-vyrewatch-registry-conflict-2026-07-19.md`.

## Required unblock

Do not activate or certify the family until:

- the authoritative stable variant ledger is reconciled;
- period-lineage evidence closes a representative's hidden combat row and the
  150/151 conflict;
- its complete ordinary/location drop behavior is reconciled; and
- at least one canonical allowed weapon is both obtainable and executable in
  Combat.

No new design was invented. These are source, dependency, and authority
blockers under the 2026-07-19 closed-design rule.
