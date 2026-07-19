# Slayer Ganodermic-creatures Combat audit — 2026-07-19

Status: **source- and dependency-blocked; no Combat rows activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the Ganodermic runt and Ganodermic beast behind the settled
Duradel/Lapalok and Kuradal assignment family. It closes their visible period
identities, Slayer/Magic gates, LP, Slayer XP, Magic attacks, maxima, fungal
hazards, neem interaction, guaranteed drops, visible drop sets, and Polypore
context.

Neither target is runtime-certifiable. Both Darkan combat definitions are
explicitly named `nostats` and generate all five hidden combat levels as
non-real fallbacks. The runt has no Darkan ordinary-drop file. The beast's
complete 256-slot table conflicts with cutoff rune, flake, and noted-herb
quantities, while its shared neem handler does not preserve the cutoff attack
suppression. The canonical Neem-oil and Polypore-resource chains are also not
live in AnkiScape.

This pass therefore does **not** add either target to `COMBAT_ENEMY_DATA`.
Duradel/Lapalok remains hidden at **14/35**. `ganodermic_creatures` retains its
`combat_target` blocker and no denominator is changed.

## Settled target boundary

The owner-settled family explicitly contains
`("ganodermic_runt", "ganodermic_beast")`, requires Slayer 95 and Magic 60,
and declares `polypore_context`. Both identities remain exact selectable
targets; one is not a cosmetic or representative alias of the other.

Under Slayer Owner decision 20, either fully functional ordinary target could
satisfy the certification floor, while the other remains named implementation
debt. Neither currently qualifies because the missing combat levels and shared
resource/context substrate affect both.

## Period evidence

### Ganodermic beast

RuneScape Wiki `Ganodermic beast`, oldid `6530646`, timestamp
`2012-11-04T07:49:23Z`, literal wikitext establishes:

- level 280, 2,500 LP, Slayer 95, and 263 Slayer XP;
- Magic 60 to receive an assignment;
- passive, poison-immune Magic attacks, four-tick attack speed, a 264-LP
  maximum, and Magic weakness;
- bottom-floor Polypore context, with a level-73 Agility route to the adjacent
  floor;
- guaranteed Big bones and Neem drupe ×1–4;
- Blood runes ×8–12 and Death runes ×10–16;
- the complete named seed set;
- Ganodermic flakes ×1–270, noted Gorajian mushrooms ×12, noted Grimy
  ranarr ×2, noted Flax ×40, Sharks ×1–3, and Polypore spores ×1–1,252;
- Polypore stick, long/curved bones, spin ticket, court summons, effigy, and
  rare-drop-table access; and
- Duradel/Lapalok and Kuradal assignment membership.

Source:
<https://runescape.wiki/w/Ganodermic_beast?oldid=6530646>.

Cutoff `Talk:Ganodermic beast`, oldid `6097646`, timestamp
`2012-08-16T14:09:59Z`, discusses seed and rare-table classification but
provides no complete executable selector or hidden combat levels:
<https://runescape.wiki/w/Talk:Ganodermic_beast?oldid=6097646>.

### Ganodermic runt

RuneScape Wiki `Ganodermic runt`, oldid `6441961`, timestamp
`2012-10-19T13:32:47Z`, literal wikitext establishes:

- level 140, 1,250 LP, Slayer 95, and 125 Slayer XP;
- passive, poison-immune Magic attacks and a 139-LP maximum;
- 11–21 LP rapid infestation while the player is in melee range;
- neem temporarily preventing infestation;
- third/bottom-floor Polypore context;
- guaranteed Bones and Neem drupe ×1–3;
- Blood runes ×3 and Death runes ×5–6;
- two simultaneous seeds from the named seed set;
- noted Gorajian mushrooms ×5, Polypore spores ×1–625, noted Flax ×20, and
  Ganodermic flakes ×1–60; and
- spin-ticket and effigy channels.

Source:
<https://runescape.wiki/w/Ganodermic_runt?oldid=6441961>.

Cutoff `Talk:Ganodermic runt`, oldid `5371532`, timestamp
`2012-03-13T01:50:35Z`, supplies no missing combat levels or executable drop
weights:
<https://runescape.wiki/w/Talk:Ganodermic_runt?oldid=5371532>.

### Shared dungeon mechanic

RuneScape Wiki `Polypore Dungeon`, oldid `6578900`, timestamp
`2012-11-18T15:10:35Z`, independently establishes:

- Magic weakness and strong Melee/Ranged resistance;
- 11–21 LP Ganodermic-runt infestation;
- 12–27 LP Ganodermic-beast infestation;
- neem temporarily preventing movement/attacks and removing the relevant
  fungal hazard;
- the no-quest dungeon entrance, vine traversal, and 73-Agility shortcut; and
- the canonical Neem-drupe vine, Pestle-and-mortar, jug, and Neem-oil
  acquisition chain.

Source:
<https://runescape.wiki/w/Polypore_Dungeon?oldid=6578900>.

The no-position Combat contract already maps proximity into contextual combat
risk rather than tile micromanagement. It does not supply missing combat
levels, exact suppression duration, or loot weights.

## Cache evidence

Rev-742 contains attackable normal and neemed identities:

- NPCs `14696`/`14697`, level-280 Ganodermic beast; and
- NPCs `14698`/`14699`, level-140 Ganodermic runt.

Darkan's cache-derived data gives both forms Stab/Slash/Crush/Ranged defences
`60/70/50/0`. Magic defence changes from `-40` to `-65` between normal and
neemed forms. CS2 key 14 changes from `4` to `6`, consistent with a slowed
neemed form, but client configuration does not reveal the five server combat
levels or an exact suppression selector.

## Executable evidence and conflicts

Pinned Darkan paths and commits:

- `data/npcs/combatdefs/uncategorized/ganodermic_runt (nostats).json`, commit
  `e1e71c9fb5979ba72bc66f4a251c725c8d0e1239`;
- `data/npcs/combatdefs/uncategorized/ganodermic_beast (nostats).json`, same
  commit;
- `data/npcs/drops/ganodermic_beast.json`, commit
  `9fee66a1548441d2d954303348557aa18c1a0c7a`;
- `data/npcs/charmDrops.txt:64-65`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`;
- `src/main/java/com/rs/game/content/skills/slayer/npcs/PolyporeNPC.java`,
  commit `776f00faeb8ca4713a8b9ca8bf11ef0c0544db16`;
- `src/main/java/com/rs/game/model/entity/npc/combat/NPCCombatDefinitions.java`,
  commit `e1e71c9fb5979ba72bc66f4a251c725c8d0e1239`; and
- `src/main/java/com/rs/utils/NPCClueDrops.java:196`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`.

The two combat rows agree with the visible LP, maxima, Magic style, passivity,
and 59-tick respawn. They omit all combat levels. Darkan's fallback generates
equal levels from combat level/LP and explicitly marks them non-real; those
values are not period evidence and cannot be made provisional.

`PolyporeNPC` gives the runt 11–21 LP infestation, matching the cutoff. It gives
the beast 15–28 LP, conflicting with the cutoff dungeon's 12–27. Neem changes
the NPC form for 20 seconds, removes infestation, divides outgoing
Magic/Ranged damage by two, and reduces incoming Melee/Ranged damage before
neem. It does not stop attacks during the neemed form, contrary to the cutoff
dungeon description. The wall-clock duration is not adopted into gameplay.

### Beast drop selector

Darkan's Ganodermic-beast table has guaranteed Big bones and Neem drupes ×1–4,
then an exact 256-slot ordinary selector plus long/curved-bone tertiary. It
matches some cutoff rows, including noted Gorajian mushrooms ×12, Flax ×40,
Sharks ×1–3, and Polypore spores ×1–1,252, but conflicts materially:

| Output | Cutoff | Darkan |
|---|---|---|
| Ganodermic flake | 1–270 | 1–298 |
| Blood rune | 8–12 | 1–3 |
| Death rune | 10–16 | absent |
| Grimy ranarr | 2 noted | 2 unnoted |
| Gem table | not a visible ordinary row | 19/256 |

The 256-slot selector also contains an exact Polypore-stick 1/256 row, while
the cutoff page supplies only `Rare`. The lower-tier probability is a lead,
not a source-closed rate.

There is **no** `data/npcs/drops/ganodermic_runt.json` in the pinned Darkan
tree. The runt's visible period set therefore has no executable selector at
all.

### Charms and clues

Darkan's Ganodermic-beast thresholds `4-3-3-6` enumerate to a 1,212-slot lead:
18 Gold, 12 Green, 12 Crimson, 42 Blue, and 1,128 empty. Runt thresholds
`7-3-76-1` enumerate to 38 Gold, 14 Green, 866 Crimson, 6 Blue, and 288 empty.
The cutoff pages prove charm tables but do not expose the hidden numeric
distributions.

Darkan supplies an elite clue for the beast at 1/1,200, but the cutoff beast
page does not list a clue scroll. The runt has no Darkan clue row and no cutoff
clue row. No clue channel is inferred for either target.

## Blocking findings

1. **Both combat rows lack real levels.** Attack, Strength, Defence, Magic,
   and Ranged are explicitly generated non-real fallbacks.
2. **The runt has no executable ordinary selector.** Its complete visible set
   has no pinned numeric table.
3. **The beast selector conflicts.** Rune, flake, and noted-herb quantities do
   not reconcile with the cutoff page.
4. **The beast infestation conflicts.** Darkan's 15–28 LP does not match the
   cutoff 12–27.
5. **Neem suppression is incomplete.** Darkan removes infestation but keeps
   attacking; the cutoff mechanic temporarily suppresses attacks/movement.
6. **The resource/context substrate is absent.** Canonical Neem oil, Polypore
   resources, target forms, and the player-selectable dungeon context are not
   live AnkiScape actions/items.

## Explicit omissions

- No target sprites or Ganodermic-resource icons were installed because
  neither target is runtime-certifiable.
- Dungeoneering resource-room access is explicitly excluded; the ordinary
  Polypore context does not depend on Dungeoneering.
- Dungeon traversal, merchant storage, armour/staff crafting, and Agility
  shortcuts remain their owning contracts' implementation debt.
- Exact neem suppression duration, charm distributions, and hidden target
  selectors remain `source_blocked`.

## Required unblock

Do not activate either target until period-lineage evidence closes the five
combat levels, the runt receives an executable selector, the beast selector
and hazard are reconciled, and the canonical Neem-oil/context transaction
preserves the temporary target form and attack suppression atomically.

No owner-facing design question emerged. These are source and implementation
dependencies under the 2026-07-19 closed-design rule.
