# Slayer Warped terrorbird Combat audit — 2026-07-19

Status: **authority-, source-, dependency-, and representation-blocked; no
Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Warped terrorbird required by the settled
Duradel/Lapalok registry. The cutoff record closes its ordinary level-81 and
quest level-143 identities, Slayer level, LP/XP, attack families, maxima,
Crystal-chime possession rule, morphology-specific weaknesses, ear-protection
effect, guaranteed drop, and visible loot contents.

Activation stops before code changes for four independent reasons:

1. the cutoff article requires only that The Path of Glouphrie be started
   before assignment, while current `required_quest_id` semantics require quest
   completion;
2. both Darkan combat rows are explicitly `nostats`;
3. Darkan fixes both forms to Melee and gives the level-143 form the
   level-81 maximum; and
4. its otherwise exact ordinary selector conflicts with most cutoff quantity
   ranges and omits visible rows.

The required Crystal chime is not a reachable inventory item in AnkiScape, and
the current fixed-style/fixed-defence enemy row cannot preserve the
Melee/Ranged double-hit and varying Stab/Slash/Crush morphology.

This pass therefore does **not** add `warped_terrorbird` to
`COMBAT_ENEMY_DATA`. Duradel/Lapalok remains hidden at **14/35**.

## Period evidence

RuneScape Wiki `Warped terrorbird`, oldid `6555103`, timestamp
`2012-11-14T10:32:24Z`, literal wikitext establishes:

- ordinary level 81 and quest level 143 forms;
- 1,549 LP, Slayer 56, and 154 Slayer XP;
- aggression, poison susceptibility, Melee and Ranged attacks;
- an approximately 140-LP ordinary maximum and a 210-LP quest-form maximum;
- guaranteed Bones;
- three visible morphologies, respectively weak to Stab, Slash, or Crush;
- a sound-based Ranged attack that hits twice;
- Earmuffs, Masked earmuffs, Slayer helmets, and Full slayer helmets reducing
  each Ranged hit's maximum to 20, for a protected two-hit maximum of 40;
- The Path of Glouphrie must be **started**, not necessarily completed, before
  the family may be assigned;
- the Crystal chime must be carried to kill the target; since the March 2010
  update the player no longer needs to use the chime on each bird;
- the Poison Waste Slayer Dungeon route; and
- the complete visible rune, armour, weapon, other, conditional, spin-ticket,
  and rare-drop-table contents.

Source:
<https://runescape.wiki/w/Warped_terrorbird?oldid=6555103>.

The page does not state an attack interval, the unprotected Ranged maximum, an
exact Melee/Ranged selector, or morphology probabilities. Those values remain
`source_blocked`.

Cutoff `Talk:Warped terrorbird`, oldid `4925276`, timestamp
`2011-11-09T19:29:07Z`, preserves unresolved reports about additional visual
combinations and Rune-kiteshield rarity. It supplies no executable combat or
drop selector:
<https://runescape.wiki/w/Talk:Warped_terrorbird?oldid=4925276>.

## Assignment-gate authority stop

The settled family row currently stores:

```python
SlayerFamily(
    "warped_terrorbirds",
    "Warped terrorbirds",
    ("warped_terrorbird",),
    required_slayer_level=56,
    required_quest_id="the_path_of_glouphrie",
    readiness_features=("crystal_chime",),
)
```

`slayer_logic.py:42-46,82-90` interprets every non-empty
`required_quest_id` as **quest completed** and renders a `Complete ...` lock.
That is stricter than the direct cutoff article's “at least started” rule.

The pool audit names a Path-of-Glouphrie gate without defining a stage
predicate. The closed-design instruction forbids this implementation pass from
silently choosing completion, any-start, Crystal-chime acquisition, or the
Poison-Waste stage as the canonical assignment predicate. The exact conflict
is separately recorded at
`audits/slayer-warped-terrorbird-gate-conflict-2026-07-19.md`.

## Cache and executable combat evidence

Rev-727/Darkan identify ordinary level-81 NPCs `6285`–`6292` and level-143
NPCs `6293`–`6295`. The client-script and bonus dumps preserve three repeated
defence shapes:

- Stab weak: `-50` Stab, `+50` Slash/Crush;
- Slash weak: `-50` Slash, `+50` Stab/Crush; and
- Crush weak: `-50` Crush, `+50` Stab/Slash.

Several forms also carry `+62` Ranged or Magic defence and `+62` melee
strength. Those exact form mappings are client evidence, but the cache does
not supply morphology selection probabilities or server combat levels.

Darkan's two combat files provide:

| Field | Ordinary, level 81 | Quest form, level 143 |
|---|---:|---:|
| LP | 1,549 | 1,549 |
| Maximum | 140 | **140 conflict** |
| Style | fixed Melee | fixed Melee |
| Respawn | 59 ticks | 59 ticks |
| Real combat levels | absent | absent |

Both files are named `nostats`; Darkan therefore generates equal, non-real
combat levels from combat level and LP. The generated values cannot be copied
into AnkiScape.

The recent Darkan Path-of-Glouphrie restoration makes ordinary warped
creatures invulnerable below Slayer 56 and automatically refreshes a
64-server-tick cleaned state on each incoming player hit when item `11749`
is carried. That corroborates the post-2010 possession-gate shape, but it does
not supply the missing combat levels, attack selector, morphology selector, or
ordinary drop reconciliation. The quest-owned restoration is not imported or
edited here.

Pinned Darkan paths and commits:

- level-81 row:
  `data/npcs/combatdefs/uncategorized/warped_terrorbird/`
  `warped_terrorbird_(81) (nostats) (noanims).json:1-38`;
- level-143 row:
  `data/npcs/combatdefs/uncategorized/warped_terrorbird/`
  `warped_terrorbird_(143) (nostats) (noanims).json:1-28`;
- both combat rows: commit
  `14e49a561bab1441384022421d10dc03a8d837f0`;
- ordinary drops:
  `data/npcs/drops/warped_terrorbird.json:1-319`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- cache morphology rows:
  `developer-information/npcClientScriptData.txt:1599-1609` and
  `developer-information/npcListBonuses.txt:6287-6297`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`; and
- possession-gate restoration:
  `src/main/java/com/rs/game/content/quests/pathofglouphrie/`
  `PathOfGlouphrie.kt:440-462,679-710`, commit
  `dc0a7aee079199aa634acf08041aaf894f837d67`.

## Executable selector conflict

Darkan's ordinary probabilities sum losslessly to `19,999/20,000`, leaving
one `1/20,000` empty outcome:

- thirteen common rows at `3,229/50,000`;
- eight uncommon rows at `1,749/100,000`;
- three rare rows at `621/100,000`; and
- Rune pickaxe at `93/50,000`.

The item identities mostly overlap the cutoff table, but the quantities do
not:

| Output | Cutoff | Darkan |
|---|---|---|
| Feather | 23–99 | 1–23 |
| Air rune | 24–60 | 1–24 |
| Earth rune | 12–36 | 1–12 |
| Death rune | 4–28 | 1–4 |
| Law / Soul rune | 1–10 | 1 |
| Coins | 15–370 | 1–15 |
| Swamp tar | 10–52 | 1–10 |
| Adamant bolts | 5–15 | 1–6 |
| Runite bolts | 3–12 | 1–3 |
| Each bolt-tip row | 16–24 | 1–16 |
| Chocolate bomb | 1–3 | 1 |
| Raw shark | 1–6 noted | 1 unnoted |

Darkan also adds a second Bones row and omits Tangled toads' legs, Sulphur,
Spin ticket, Anagogic ort, and the rare-drop table. Period rarity labels do not
supply numeric replacement weights. The emulator probabilities therefore
cannot be transplanted onto the materially different cutoff rows.

No executable charm selector or clue row was found for Warped terrorbirds.
The cutoff article also supplies no numeric charm or clue dependency, so this
pass does not invent one.

## Representation and dependency boundary

The complete ordinary fight requires one target-local state containing:

- a carried, non-consumed Crystal chime gate;
- one of three morphology-specific melee weaknesses;
- a Melee/Ranged attack selector;
- a two-hit Ranged attack;
- sound protection that caps each Ranged hit at 20; and
- ordinary protection-prayer behavior for each attack style.

Current Combat supports fixed enemy style and fixed defence bonuses. Its
protective-equipment seam models consequences from missing an item, but not a
sound-only two-hit branch alongside ordinary Melee. A generic level-81 fixed
Melee row would discard the settled distinctive loop and cannot certify the
family.

`Crystal chime` exists only in the generated value table. It is not a live
quest reward, inventory identity, target requirement, or picker-visible
dependency in AnkiScape. Quest parity remains owned by the Darkan quest thread.

## Blocking findings

1. **The assignment gate conflicts with current semantics.** Period “quest
   started” is not the implemented “quest completed” predicate.
2. **Both combat rows lack real levels.** Darkan explicitly generates them.
3. **The level-143 maximum conflicts.** Darkan stores 140 against the cutoff
   210.
4. **The distinctive attack/morphology loop is absent.** Fixed Melee and one
   defence row cannot represent the cutoff fight.
5. **The ordinary selector conflicts on quantities and contents.** Exact
   emulator weights cannot be transferred.
6. **The Crystal-chime acquisition/use dependency is not live.**

## Explicit omissions

- No Path-of-Glouphrie stage, reward, or quest encounter was edited.
- The three level-143 quest bosses were not folded into the ordinary Slayer
  target.
- No cannon, Poison-Waste travel, Spirit-tree, grapple, safespot, Guthan,
  familiar, or wall-clock behavior was introduced.
- No sprite or drop assets were installed because the target is not
  runtime-certifiable.

## Required unblock

Before activation:

1. a newer authority record must reconcile the started-versus-completed
   assignment predicate with the available quest-stage schema;
2. period-lineage evidence must close the five combat levels and reconcile the
   level-143 maximum;
3. a drop selector must preserve the cutoff quantities and contents;
4. Combat must implement the morphology, mixed-style, double-hit, and
   ear-protection transaction; and
5. the canonical Crystal chime must be obtainable and carried atomically.

No owner-facing creative-design question emerged. The gate is an
authority/schema conflict, and the remaining items are source, dependency, and
implementation blockers under the 2026-07-19 closed-design rule.
