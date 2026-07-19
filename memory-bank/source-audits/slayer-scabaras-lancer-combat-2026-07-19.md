# Slayer Scabaras lancer Combat source audit — 2026-07-19

## Decision

Do not implement `scabaras_lancer` yet. The settled Slayer registry names it
as the Scabarites representative, and the cutoff record closes its ordinary
identity, LP, XP, style, speed, maximum, poison behavior, guaranteed drop, and
Sumona eligibility. Its executable combat levels are absent from every
available pre-EOC-lineage implementation layer, however. Those values are
content data, not hidden rolls, and cannot be inferred from combat level 112.

The `scabarites` family therefore remains `source_blocked` on its Combat
target. No owner design was reopened and no alternative representative was
substituted for the settled registry target.

## Period authority

RuneScape Wiki `Scabaras lancer`, oldid
[`6474953`](https://runescape.wiki/w/Scabaras_lancer?oldid=6474953),
timestamp `2012-10-26T12:43:02Z`, is inside the frozen cutoff. Literal
wikitext establishes:

- combat level 112, 900 LP, and 90 Slayer XP;
- aggressive melee combat and an approximately 130-LP maximum;
- non-poisonous attacks and susceptibility to player poison;
- guaranteed Bones;
- Sumona assignment and Scabarites-task qualification; and
- Dealing with Scabaras and the ordinary east-of-Sophanem/dungeon habitats.

RuneScape Wiki `Scabarites`, oldid
[`6062028`](https://runescape.wiki/w/Scabarites?oldid=6062028), timestamp
`2012-08-08T19:04:49Z`, independently lists Scabaras lancers among qualifying
Scabarites. It explicitly excludes Scabaras locusts, Scarab larvae, the High
Priest, and the Pit scabarite, while leaving the quest-only giant scarabs
unknown. This matches the owner-settled registry representative and exclusion
boundary.

## Cache and implementation evidence

The rev-742 cache contains NPC ID 6774 as `Scabaras lancer` with the `Attack`
option. The cache proves identity and interaction, not server combat stats.

Darkan commit `a802b254cd2bf90d08dda3d56638db2b09158c0b` provides
`data/npcs/combatdefs/uncategorized/scabaras_lancer (nostats).json`:

- 900 LP;
- 130 maximum;
- melee style;
- aggressive behavior; and
- 59-tick respawn.

The filename explicitly marks the row `nostats`, and the JSON contains no
`combatLevels` object. Darkan
`developer-information/npcListBonuses.txt:6776` supplies only the defensive
bonuses `30/30/0/0/0`; bonuses are not NPC Attack, Strength, Defence, Magic,
or Ranged levels.

The independent game-main repository contains Scabaras lancer spawn rows in
`spawns_13611.plugin.kts` and `spawns_13456.plugin.kts`, but no combat
definition or stat row. Darkan's `developer-information/beasts.txt` is an EOC
bestiary export whose level-77, 2,750-LP shape directly conflicts with the
cutoff level-112, 900-LP target and is excluded.

## Drops harvested but not activated

Darkan `data/npcs/drops/scabaras_lancer.json` supplies guaranteed Bones plus
denominator-bearing executable rows for Coins, key halves, Waterskin (4),
raw/cooked fish, Adamant arrows, Blood runes, Rune and Dragon equipment,
gems, Lava runes, Cactus seed, Desert goat horns, and other rare outputs.
`src/main/java/com/rs/utils/NPCClueDrops.java:167` supplies an independent
1/128 hard clue. The period page corroborates the major visible outputs.

These rows are preserved as implementation evidence but are not encoded into a
dead Combat target while the required combat levels remain unresolved.

## Source-blocked fields

- Attack level;
- Strength level;
- Defence level;
- Magic level; and
- Ranged level.

No available period page, Darkan executable record, rev-727/742 client
definition, or game-main combat definition states them. Estimating them from
combat level would invent non-roll content and violate
`pre-eoc-source-verification-standard.md`.

## Readiness and next evidence

Sumona remains hidden at 20/37. A source-ready implementation requires either:

1. a Darkan high-fidelity Scabaras lancer combat definition;
2. a period-lineage server/config source stating all five combat levels; or
3. another independently corroborated pre-EOC implementation row.

No owner-facing design gap emerged.
