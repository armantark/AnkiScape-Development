# Slayer Gorak Combat audit — 2026-07-19

Status: **assignment gate closed; source-, context-, and
representation-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the settled `goraks` family for Duradel/Lapalok. The family
contract already names two exact qualifying targets:

- `gorak_fairy_ring`, the level-145 Gorak-plane form; and
- `gorak_god_wars`, the level-149 Zamorak-aligned God Wars form.

The cutoff record closes both identities, their assignment count, the shared
Fairy Tale II completion gate, LP and maximum-hit pairs, typeless
prayer-ignoring melee, random stat drain, weakness, guaranteed drop, visible
loot contents, and distinct contexts. Darkan closes the level-145 real combat
levels, both forms' zero cache bonuses, the 59-tick respawn lead, and the
prayer-bypass shape.

Neither variant is runtime-certifiable. The level-149 Darkan row copies the
level-145 LP and maximum, the ordinary selector conflicts with the cutoff
contents and quantities, the source does not close the stat-drain magnitude or
attack cadence, and current Combat has no target-native landed-hit transaction
that both bypasses protection prayer and drains one random skill. The settled
player-selectable location contexts are also absent.

This pass therefore does **not** add either target to `COMBAT_ENEMY_DATA`.
Duradel/Lapalok remains hidden at **14/35**. The independently closed quest
gate is encoded on the family without pretending that it satisfies the Combat
or context blockers.

## Supersession note

This audit supersedes only the
`exact global quest predicate source_blocked` clause for Goraks in
`source-audits/slayer-duradel-lapalok-pool-2026-07-17.md`. It does not change
the settled family membership, two-context requirement, count, weight, or
readiness feature.

RuneScape Wiki `Gorak`, oldid `6518331`, states directly that Duradel and
Lapalok assign 40–80 Goraks and do not assign them until
`Fairy Tale Part II - Cure a Queen` is complete. The canonical AnkiScape quest
ID is `a_fairy_tale_ii_cure_a_queen`, so `slayer_data.py` now records that
family-level assignment gate.

## Period evidence

RuneScape Wiki `Gorak`, oldid `6518331`, timestamp
`2012-11-02T01:29:41Z`, literal wikitext establishes:

- level 145 and 149 identities with 1,120 and 1,280 LP;
- Slayer level 1, 112 Slayer XP in the shared infobox, and assignments of
  40–80 from Duradel/Lapalok after Fairy Tale II completion;
- aggression, poison susceptibility, typeless melee, Stab weakness, and
  140/165-LP maxima;
- attacks that ignore protection prayer;
- a drain of at least one point from a random skill on every damaging hit;
- the Gorak plane at fairy-ring code `DIR` and the God Wars Dungeon as distinct
  locations, with the God Wars form aligned to Zamorak;
- guaranteed Big bones, plus Long/Curved-bone tertiaries;
- the visible armour, weapons, herbs, other, clue, court-summons, spin-ticket,
  and rare-table contents;
- common Gorak claws, the Herblore input for Magic essence potions; and
- no Summoning charms.

Source:
<https://runescape.wiki/w/Gorak?oldid=6518331>.

The same revision contains an unresolved cadence conflict. Its structured
infobox says `attack speed = 6`, while the prose calls the attacks rapid and
approximately equal to a dagger's speed. No executable period dependency in
this pass reconciles those statements, so an exact attack interval is not
claimed.

Cutoff `Talk:Gorak`, oldid `5692087`, timestamp
`2012-06-01T10:55:22Z`, preserves player reports about:

- occasional missing Big bones near the crowded fairy ring, explicitly
  without statistical proof;
- Deflect Melee producing a message that it does not work on the Gorak plane;
- post-Ring-of-Wealth-update gem rarity;
- experience derived from the stated LP; and
- weakness-label disagreement.

It supplies no executable drop selector, stat-drain magnitude, or cadence
resolution. The article's newer guaranteed Big-bones row is independently
corroborated by Darkan and remains the stronger ordinary-drop finding:
<https://runescape.wiki/w/Talk:Gorak?oldid=5692087>.

## Cache and executable combat evidence

Rev-727/Darkan identify NPC `4418` as the attackable level-145 Gorak and NPC
`6218` as the level-149 God Wars form. Darkan's exact ordinary rows provide:

| Field | Gorak plane, 4418 | God Wars, 6218 |
|---|---:|---:|
| Level | 145 | 149 |
| LP | 1,120 | **1,120 conflict** |
| Maximum hit | 140 | **140 conflict** |
| Attack | 130 | 133 |
| Strength | 130 | 126 |
| Defence | 131 | 135 |
| Magic | 1 | 1 |
| Ranged | 1 | 1 |
| Respawn | 59 ticks | 59 ticks |
| Attack bonuses | 0 | 0 |
| Strength bonuses | 0 | 0 |
| All five defences | 0 | 0 |

The level-149 row directly conflicts with the cutoff 1,280 LP and 165-LP
maximum. Its real combat levels remain useful evidence, but its copied
level-145 LP/maximum cannot be adopted.

Darkan's shared `GorakCombat` handler rolls Melee damage and applies it as
`TRUE_DAMAGE`, preserving the source shape that protection prayer cannot
reduce a Gorak hit. It does not implement the mandatory random stat drain.

Pinned Darkan paths and commits:

- level-145 combat row:
  `data/npcs/combatdefs/uncategorized/gorak/gorak_(145).json:1-31`;
- level-149 combat row:
  `data/npcs/combatdefs/uncategorized/gorak/gorak_(149).json:1-31`;
- both combat rows: commit
  `14e49a561bab1441384022421d10dc03a8d837f0`;
- zero cache bonuses:
  `developer-information/npcListBonuses.txt:4420,6220`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- prayer-bypassing combat handler:
  `src/main/java/com/rs/game/content/world/npcs/GorakCombat.java:28-42`,
  commit `347552cad462e96670e3ff04228c0232881da9f5`;
- ordinary drops:
  `data/npcs/drops/gorak.json:1-311`, commit
  `9fee66a1548441d2d954303348557aa18c1a0c7a`; and
- hard clue:
  `src/main/java/com/rs/utils/NPCClueDrops.java`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

## Executable selector conflict

Darkan supplies guaranteed Big bones, the shared Long/Curved-bone table, and
an ordinary set whose probabilities sum to `99,519/100,000`, leaving
`481/100,000` empty:

- six common rows at `7,009/50,000`;
- fifteen uncommon rows at `467/50,000`; and
- three rare rows at `467/100,000`.

That selector cannot be transplanted:

| Output | Cutoff | Darkan |
|---|---|---|
| Coins | exactly 27, 97, 104, 132, or 286 | uniform quantity range 27–286 |
| Gorak claws | common | absent |
| Steel battleaxe | uncommon | absent |
| Rune helm | rare | absent |
| Bones | no ordinary row | present despite guaranteed Big bones |
| Rare-drop table | present | absent from the ordinary file |

The Darkan range admits 255 coin quantities the period table does not attest.
Its item `3192` is Iron halberd, not Gorak claws; canonical Gorak claws are
item `9016`. The missing claws also sever the already-live
`Gorak claws -> Gorak claw powder -> Magic essence` acquisition chain if the
selector were copied as-is.

The cutoff page supplies rarity labels rather than numeric weights. No
period-lineage selector found in this pass reconciles Darkan's contents, so
the ordinary drop transaction remains `source_blocked`. Long/Curved bones and
the hard-clue rate remain emulator leads rather than independently closed
numeric tertiaries.

## Representation and context boundary

Current Combat can apply a random-one stat drain inside missing-equipment and
Vampyre-bite special cases (`logic_pure.py:4057-4101,8127-8186`). It does not
expose the equivalent as a generic on-damaging-hit enemy rule.

Ordinary enemy damage is reduced by the matching protection prayer at
`a78963f9:logic_pure.py:8046-8076`. The bypass seam is currently tied to an
`unprotected_effect` produced by missing protective equipment, not to a
target-native attack property. Encoding Goraks through fake required equipment
would introduce a mechanic the source never had.

The exact drain magnitude is also not closed. “At least one” attests a floor,
not an always-one transformation. Selecting one as the permanent amount would
invent a non-probability value outside the provisional hidden-roll exception.

Finally, `readiness_features=("location_context",)` is only a ledger
obligation today. The player cannot select and atomically commit either:

- the Fairy-ring route, its quest/fairy-ring access, and the level-145 form; or
- the God Wars route, Zamorak alignment, and the level-149 form.

A truthy metadata flag would falsely certify a usable route without
implementing one.

## Blocking findings

1. **The level-149 emulator row conflicts with the cutoff.** It copies 1,120
   LP and a 140 maximum instead of the direct 1,280/165 pair.
2. **The ordinary selector conflicts with the cutoff table.** It omits Gorak
   claws and other rows, adds Bones, and turns five exact coin quantities into
   a continuous range.
3. **The exact attack interval and drain magnitude are not closed.** The
   cutoff cadence statements conflict, and “at least one” gives only a drain
   floor.
4. **The distinctive hit transaction is not representable.** Current Combat
   lacks a generic prayer-bypassing landed-hit random-stat drain.
5. **Neither settled location context is executable.** One metadata feature
   cannot substitute for a player-selectable route.

## Explicit omissions

- No Fairy Tale II quest stage or reward was edited; quest parity remains owned
  by the Darkan quest thread.
- No God Wars kill-count, god-item, aggression, or transport behavior was
  inferred into the target.
- No Gorak claws acquisition was added through a blocked drop selector.
- No Summoning charm table was added because the cutoff source explicitly says
  Goraks do not drop charms.
- No target asset was installed because neither target is
  runtime-certifiable.

## Required unblock

Activate a Gorak target only after:

1. a period-lineage selector reconciles the cutoff contents and quantities;
2. the attack interval and stat-drain magnitude are closed by evidence or an
   already-settled labeled abstraction;
3. Combat gains a target-native, undo-safe prayer-bypass and landed-hit random
   stat-drain transaction; and
4. its matching Fairy-ring or God Wars context is player-selectable and
   atomic.

Under Slayer Owner decision 20, one fully functional authentic gated route may
certify this player-gated family once the complete quest, context, distinctive
hit, and acquisition chain is live. The other settled variant remains named
implementation debt and cannot be flattened into the certifying target.

The shared Fairy Tale II completion gate, count 40–80, both exact identities,
period LP/maxima, real combat levels, zero cache bonuses, 59-tick respawn,
guaranteed Big bones, typeless prayer bypass, Stab weakness, and no-charm rule
can then be adopted without reopening design.

No owner-facing design question emerged. These are source and implementation
blockers under the 2026-07-19 closed-design rule.
